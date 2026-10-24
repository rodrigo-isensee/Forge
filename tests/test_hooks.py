"""Testes dos hooks do plugin (ADR 0003): cada fixture em tests/hooks/<hook>/<caso>.json roda o script do hook
com a entrada no stdin, num projeto git temporário, e confere o código de saída, o stderr e o estado.

Formato do fixture:
  descricao   texto livre
  forge       false para projeto sem .forge/versao (padrão: true)
  arquivos    {caminho: texto ou lista de linhas} gravados antes do commit inicial (branch develop)
  config      objeto gravado em .forge/config.json; `config_bruta` grava o texto como está
  executaveis [caminho] relativos à raiz que ganham permissão de execução (ex.: um `gh` falso, sem rede, no PATH do `env`)
  links       {caminho: alvo} links simbólicos criados depois dos arquivos ({raiz} e {tmp} valem no alvo)
  env         variáveis de ambiente do processo do hook ({tmp} vale; ex.: FORGE_GUARDA_ABERTA, HOME)
  git         passos depois do commit inicial: {"branch": b} | {"checkout": b} | {"worktree": pasta, "branch": b} (com "solto": true, HEAD solto)
              | {"ref": "refs/remotes/origin/b"} (aponta para o HEAD) | {"config": {chave: valor}} (git config local)
              | {"arquivos": {...}, "commit": msg}  ({HEAD} no texto vira o hash do commit atual)
  repos       {pasta relativa a {tmp}: {"arquivos": {...}, "branch": b, "remotos": {nome: url}}} outros repositórios git
              (ex.: um clone do Forge em {tmp}/home/Forge), com um commit inicial
  proc        /proc simulado do hook `agentes`: {"loadavg": texto, "mem_gb": disponível, "mem_total_gb": total (16),
              "nproc": núcleos (8)} ou {"ausente": true} (padrão: sem leitura, ou seja, o padrão 3)
  estado      {arquivo: objeto ou texto} gravados em .forge/run/ antes de rodar
  entrada     JSON do hook ({raiz} e {tmp} viram caminhos; "{agora-N}" e os PIDs viram números: "{pid_vivo}" é a
              sessão que chama o hook, "{pid_outro}" outra sessão viva, "{pid_morto}" uma encerrada; "{pid_ns}" é o namespace de PID
              do teste, como o `agentes` o grava, ou texto vazio sem /proc)
  passos      antes da `entrada`, em ordem: {"entrada": {...}} roda o hook (código 0; no SessionStart, stdout vazio); {"gravar": {caminho: texto}} e
              {"anexar": {caminho: texto}} mexem em arquivos ({tmp} e {raiz} valem; relativo = da raiz do projeto)
              Também em passos: {"remover": [caminho]} apaga arquivos (como um `git rm` que o hook não viu) e
              {"git": [argumentos]} roda o git no projeto (como um comando que o hook não viu, ex.: sparse-checkout)
              Em caminhos e textos, {marca} e {marca_wt} valem pela marca da sessão (`.git/forge/projeto-<hash da raiz>`) do
              projeto e da worktree `{tmp}/wt`
  esperado    codigo, saida (trecho do systemMessage; só o `vigia` escreve no stdout), pergunta (trecho do motivo: só o
              `conformidade` pede confirmação, `permissionDecision: ask` no stdout, código 0), stderr (trecho), estado {arquivo: {contem: [...], ausente: [...]}}, sem_arquivo [...],
              sem_run (true: .forge/run/ não foi criado), erros_log (trecho)
              sem_caminho ([caminho]: não existem; {tmp} vale)
"""
import collections
import concurrent.futures
import contextlib
import functools
import hashlib
import io
import itertools
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo, git, minimo  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

HOOKS = RAIZ / "hooks"
FIXTURES = Path(__file__).resolve().parent / "hooks"
# Erro de caminho igual em toda versão do Python (a 3.14 engole o OSError de Path.exists): ver o módulo da pasta.
PATHLIB_312 = Path(__file__).resolve().parent / "apoio_pathlib_312"
PESADOS_DA_STACK = json.loads((RAIZ / "stacks/node-react/pesados.json").read_text(encoding="utf-8"))


def pid_morto():
    p = subprocess.Popen([sys.executable, "-c", ""])
    p.wait()
    return p.pid


def namespace_de_pid():
    try:
        return os.readlink("/proc/self/ns/pid")
    except OSError:
        return ""


def substituir(valor, mapa, agora):
    if isinstance(valor, dict):
        return {substituir(k, mapa, agora): substituir(v, mapa, agora) for k, v in valor.items()}
    if isinstance(valor, list):
        return [substituir(v, mapa, agora) for v in valor]
    if isinstance(valor, str):
        m = re.fullmatch(r"\{agora-(\d+)\}", valor)
        if m:
            return agora - int(m.group(1))
        if valor in ("{pid_vivo}", "{pid_outro}", "{pid_morto}"):
            return mapa[valor]
        for chave, texto in mapa.items():
            if isinstance(texto, str):
                valor = valor.replace(chave, texto)
    return valor


def texto(conteudo):
    return "\n".join(conteudo) + "\n" if isinstance(conteudo, list) else conteudo


def conferir_passo(entrada, r):
    """Saída dos `passos`: sempre código 0; no SessionStart o stdout vira contexto do modelo, então tem de ser vazio."""
    assert r.returncode == 0, f"passo {entrada.get('hook_event_name')} saiu com {r.returncode}: {r.stderr}"
    if entrada.get("hook_event_name") == "SessionStart":
        assert r.stdout == "", f"SessionStart não escreve no stdout (ADR 0003, item 1): {r.stdout!r}"


# HOOK-COMENTARIO-SHLEX (ADR 0013): o que o bash ignora (ou roda à toa) antes ou depois de uma linha. Cada variante põe
# um `#` num contexto em que uma leitura errada do comentário esconderia o resto, ou deixa a linha ilegível para o hook.
# O bash roda a linha depois de cada uma (o T5 confere): o `$[1 #x]` é erro de aritmética, que encerra o `bash -c`, e
# por isso fica depois de `true ||`, que o bash lê e não avalia.
PREFIXOS_QUE_O_BASH_IGNORA = ("echo `echo a #b`; ", "echo ${x:- #b}; ", "x=abc; echo ${x/ #y/z}; ", "true || echo $[1 #x]; ",
                              "(true)#'\n", "(( 1 )) # it's\n", "true #'\n", "echo $'it\\'s'; ", "[[ a =~ ( #b) ]]; ",
                              "[[ a == @(a| #b) ]]; ", "echo a\\ #b; ")
SUFIXOS_QUE_O_BASH_IGNORA = ("; (true)#x", "\n# it's", "; echo $'it\\'s'", "; (true)#'", " # it's ((")
# Em par: a aspa de um comentário dentro de crase (que o bash fecha na crase) casaria com a do outro lado da linha.
PARES_QUE_O_BASH_IGNORA = (("x=`#'`; ", " # '"), ('x=`#"`; ', ' # "'), ("echo `# it's`; ", "; echo `# it's`"),
                           ("echo `true # it's`;\n", "\necho `true # it's`"),
                           # CRASE-ASPA-HOOK: a aspa sem par no corpo da crase (que o bash fecha na crase) casaria com a
                           # do outro corpo, e o comando do meio viraria texto entre aspas
                           ("x=`'`; ", "; y=`'`"), ('x=`"`; ', '; y=`"`'), ("x=`$'`; ", "; y=`$'`"),
                           ('echo "`\'`"; ', '; echo "`\'`"'), ("x=`'`; ", "; y=`'`\n`"),  # e uma crase sem par adiante
                           # CRASE-SESSAO-PROJETO: a ação dentro da crase, também entre aspas duplas e com texto em volta
                           *(CRASE_EM_VOLTA := (("echo `", "`"), ('echo "`', '`"'), ("x=`", "`"), ('echo "x `', '` y"'),
                                                ('x="`', '`"'))),
                           # N1: a substituição entre aspas numa atribuição; N2: `$(…)` entre aspas duplas (parecer)
                           *(SUBSTITUICAO_ENTRE_ASPAS := (
                               ('x="$(', ')"'), ("x='a'\"$(", ')"'), ('x="$(', ')" true'),
                               ('echo "$(', ')"'), ('echo "a $(', ') b"'), ('echo "$(true; ', ')"'))),
                           # HEREDOC-FURO-HOOK: um `<<` que o bash não lê como heredoc (H1-H8) tomava a ação por corpo;
                           # H9: o corpo de heredoc sem aspas no delimitador expande `$(…)` e crase
                           *(HEREDOC_FALSO := (("echo '<<X'\n", "\nX"), ('echo "<<X"\n', "\nX"), ("echo \\<<X\n", "\nX"),
                                               ("ls # <<X\n", "\nX"), ("x=$(date) # <<X\n", "\nX"), ("x=`# <<X`\n", "\nX"),
                                               ("echo 'a\n<<X'\n", "\nX"), ("echo $((1<<X))\n", "\nX"),
                                               ("cat <<EOF\n$(", ")\nEOF"), ("cat <<EOF\n`", "`\nEOF"),
                                               # o corpo já tirado não volta a ser tirado na palavra relida
                                               ("x=\"$(cat <<'X'\nX\n", "\n)\""))))
VARIANTES_QUE_O_BASH_IGNORA = (tuple((p, "") for p in PREFIXOS_QUE_O_BASH_IGNORA)
                               + tuple(("", s) for s in SUFIXOS_QUE_O_BASH_IGNORA) + PARES_QUE_O_BASH_IGNORA)
# T2: uma variante por mecanismo, aplicada a uma fixture de cada família de recusa (o motivo vai ao lado).
MECANISMOS_DO_COMENTARIO = {"${": ("echo ${x:- #b}; ", ""), "crase": ("echo `echo a #b`; ", ""), "$[": ("true || echo $[1 #x]; ", ""),
                            "(true)#'": ("", "; (true)#'"), " # it's ((": ("", " # it's (("),
                            "$'": ("", "; echo $'it\\'s'"), "⏎# it's": ("", "\n# it's"),
                            "crase em par": PARES_QUE_O_BASH_IGNORA[0], "crase em par, aspas duplas": PARES_QUE_O_BASH_IGNORA[1],
                            "aspa na crase": PARES_QUE_O_BASH_IGNORA[4], "dentro de crase": CRASE_EM_VOLTA[0],
                            "crase entre aspas com texto": CRASE_EM_VOLTA[3], "atribuição com $( entre aspas":
                            SUBSTITUICAO_ENTRE_ASPAS[0], "$( entre aspas": SUBSTITUICAO_ENTRE_ASPAS[3],
                            "heredoc entre aspas": HEREDOC_FALSO[0], "heredoc em comentário": HEREDOC_FALSO[3]}
FAMILIAS_DE_RECUSA = {
    "conformidade/trava-repo-delete-bloqueia": "gh repo delete",
    "conformidade/trava-push-main-bloqueia": "push na main (R-MAIN)",
    "conformidade/flag-push-no-verify-bloqueia": "--no-verify (R-VERIFY)",
    "conformidade/trava-rm-pasta-githooks-bloqueia": "caminho protegido fora de .claude/",
    "conformidade/trava-forge-sugerir-fila-bloqueia": "forge sugerir",
    "conformidade/trava-claude-plugin-install-bloqueia": "claude plugin install",
    "conformidade/flag-config-hookspath-bloqueia": "git config",
    "parecer/forge-clone-pr-merge-reprovado-bloqueia": "merge com parecer reprovado (R-REVIEW)",
    "parecer/forge-clone-pr-create-sem-parecer-bloqueia": "PR sem parecer (R-REVIEW)",
    "pesado/outra-ativa-bloqueia": "tarefa pesada de outra sessão (R-TETO)",
}
# Tabela 2.4 da ADR 0013: no `pesado`, a trava de recurso fica aberta quando nenhuma das duas leituras fecha (como na
# develop); o `$'…'` sem `#` não tem leitura antiga, e na crase em par a antiga (a da develop) tira o comando com o
# comentário que começa na crase.
FORA_DO_T2 = {("pesado/outra-ativa-bloqueia", "$'"), ("pesado/outra-ativa-bloqueia", "crase em par"),
              ("pesado/outra-ativa-bloqueia", "crase em par, aspas duplas"),
              # CRASE-ASPA-HOOK: a linha com corpo de crase que não se lê é ilegível, e o `pesado` libera a ilegível
              ("pesado/outra-ativa-bloqueia", "aspa na crase"),
              # O `pesado` não lê o corpo da crase nem a substituição entre aspas (ADR 0013)
              ("pesado/outra-ativa-bloqueia", "dentro de crase"), ("pesado/outra-ativa-bloqueia", "crase entre aspas com texto"),
              ("pesado/outra-ativa-bloqueia", "atribuição com $( entre aspas"), ("pesado/outra-ativa-bloqueia", "$( entre aspas")}
# FICHAS-CORPUS-BASH (T5): a ação de cada família de recusa, numa linha só, e o hook cuja leitura a confere (o
# `conformidade` lê todas). Guarda do corpus (`PROIBIDO_NO_ORACULO`): nenhuma palavra começa por `/` (`core.hooksPath h`
# no lugar de `/tmp/h`).
ACOES_DO_CORPUS = {
    "gh repo delete dono/proj --yes": "conformidade",
    "git push origin main": "conformidade",
    "git push --no-verify origin feature/x": "conformidade",
    "rm -rf .githooks": "conformidade",
    "forge sugerir --fila": "conformidade",
    "claude plugin install forge@forge": "conformidade",
    "git config core.hooksPath h": "conformidade",
    "gh pr merge feature/x --repo rodrigo-isensee/Forge --merge": "parecer",
    "gh pr create --base develop --title t --body x": "parecer",
    "docker compose up -d": "pesado",
}
# O oráculo roda o bash de verdade (modelo de ameaças do lote, seção 4): com `PATH` numa pasta que não existe, todo
# comando externo cai em `command_not_found_handle`, que registra o comando expandido no stderr (o stdout é capturado
# por `$(…)` e pelo corpo de heredoc). O `-r` recusa nome de comando com `/` (mesmo montado), redirecionamento de saída,
# `exec`, `enable` e mudar `PATH`; o que ele não barra (`kill`, `trap`, `ulimit`, segundo plano...) a guarda recusa no
# texto, antes de rodar.
PROLOGO_DO_ORACULO = "command_not_found_handle() { printf 'RODOU %s\\n' \"$*\" >&2; }\n"
PROIBIDO_NO_ORACULO = re.compile(
    r"(?:^|[\s;&|()`'\"=<>{}$])\.{0,2}/"  # palavra que começa por / ou ./ (programa por caminho, /dev/tcp, /dev/udp)
    r"|(?:^|[\s;&|()`'\"{}])(?:kill|trap|ulimit|umask|disown|exec|eval|source|enable|hash|command|builtin|\.)"
    r"(?=[\s;&|()`'\"]|$)"
    r"|>|(?<!&)&(?!&)")  # redirecionamento de saída (`>`, `2>`, `&>`) e comando em segundo plano


class Ilegivel(Exception):
    """A composição de teste não lê a linha: o hook a recusa por isso (fora do papel só de leitura)."""


def modulos_dos_hooks():
    if str(HOOKS) not in sys.path:
        sys.path.insert(0, str(HOOKS))
    import _comum
    import conformidade
    import parecer
    return _comum, conformidade, parecer


def ler_como_o_conformidade(linha, nivel=0, so_substituicoes=False, todas=True):
    """Composição de teste (desenho do lote, 3.3), sem função nova no hook: o caminho de leitura do `Guarda.bash` e do
    `segmento`, que devolve (palavras, destinos) de cada comando que o hook confere ou levanta `Ilegivel`. `todas`:
    False lê só a leitura fiel do nível de fora (a base do T1)."""
    _comum, conformidade, _ = modulos_dos_hooks()
    if nivel > conformidade.PROFUNDIDADE:
        return []  # o hook só dá o R-CONTRIB da linha aninhada que aponta para o Forge, e não lê mais nada
    try:
        linha, corpos = _comum.tirar_heredocs(linha)
    except ValueError:
        raise Ilegivel(linha) from None
    linha = re.sub(r"\$\(\s*pwd(\s+-[LP])?\s*\)", "$PWD", linha)
    lidas = _comum.leituras(linha)
    if lidas.ilegivel:
        raise Ilegivel(linha)
    lidos = []
    for partes in lidas.partes if todas or nivel else lidas.partes[:1]:
        for palavras, destinos, sub in partes:
            if so_substituicoes and not sub:
                continue
            lidos.append((palavras, destinos))
            lidos += ler_dentro_do_comando(palavras, nivel)
    for corpo in _comum.conteudos_de_crase(linha, so_os_fechados=True):  # CRASE-SESSAO-PROJETO
        lidos += ler_como_o_conformidade(corpo, nivel + 1)
    for dono, corpo in corpos:
        if re.search(r"\b(bash|sh|zsh|dash)\b", dono):
            lidos += ler_como_o_conformidade(corpo, nivel + 1)
    return lidos


def ler_dentro_do_comando(palavras, nivel):
    """O que o `segmento` relê de um comando simples: a palavra com substituição entre aspas e o `bash -c`/`eval`."""
    _, conformidade, _ = modulos_dos_hooks()
    while palavras and palavras[0] in conformidade.CORPO_DE_LACO:
        palavras = palavras[1:]
    atribuicoes = palavras[:len(palavras) - len(conformidade.sem_atribuicoes(palavras))]
    try:
        palavras, lancadas = conformidade.separar_lancadores(palavras)
    except ValueError:
        return []  # `env -S` com aspas abertas: o hook só dá o R-CONTRIB para o Forge
    lidos = []
    for p in atribuicoes + lancadas + palavras:  # N1: a atribuição também
        if "`" in p:
            lidos += ler_como_o_conformidade(p, nivel + 1)
        elif "$(" in p.replace(conformidade.OPACO["$"], ""):
            lidos += ler_como_o_conformidade(p, nivel + 1, so_substituicoes=True)
    prog = Path(palavras[0].lstrip("`")).name if palavras else ""
    internos = []
    if prog in conformidade.SHELLS:
        internos = [palavras[i + 2] for i, a in enumerate(palavras[1:-1]) if re.fullmatch(r"-[a-z]*c[a-z]*", a)]
    elif prog == "eval":
        internos = [" ".join(palavras[1:])]
    for interno in internos:
        lidos += ler_como_o_conformidade(interno, nivel + 1)
        if "\\`" in interno:
            lidos += ler_como_o_conformidade(interno.replace("\\`", "`"), nivel + 1)
    return lidos


def ler_como_o_parecer(linha, nivel=0, so_substituicoes=False):
    """Composição de teste do `parecer.conferir_linha`: os comandos de cada leitura da linha e, recursivamente, os do
    corpo de cada crase (P4) e das palavras com `$(…)` entre aspas (N2), ou `Ilegivel`."""
    _comum, _, _ = modulos_dos_hooks()
    lidas = _comum.leituras(linha)
    if lidas.ilegivel or nivel > _comum.PROFUNDIDADE:
        raise Ilegivel(linha)
    lidos = [(palavras, destinos) for leitura in lidas.partes for palavras, destinos, sub in leitura
             if sub or not so_substituicoes]
    for corpo in _comum.conteudos_de_crase(linha, so_os_fechados=True):
        lidos += ler_como_o_parecer(corpo, nivel + 1)
    for p in [p for leitura in lidas.partes for palavras, _, _ in leitura for p in palavras]:
        if "$(" in p.replace(_comum.OPACO["$"], ""):
            lidos += ler_como_o_parecer(p, nivel + 1, so_substituicoes=True)
    return lidos


COMPOSICOES = {"conformidade": ler_como_o_conformidade, "parecer": ler_como_o_parecer}


def le_a_acao(composicao, variante, acao):
    """Afirmação 2 do T5: a composição dá ilegível (o hook recusa) ou tem um comando que começa pelas palavras da ação."""
    try:
        lidos = composicao(variante)
    except Ilegivel:
        return True
    return any(palavras[:len(acao)] == acao for palavras, _ in lidos)


@functools.lru_cache(maxsize=1)
def bash_do_oraculo():
    """(caminho absoluto do bash, None) ou (None, motivo): o oráculo precisa do bash 4 ou mais novo
    (`command_not_found_handle`) e do modo restrito (`-r`)."""
    caminho = shutil.which("bash")
    if not caminho:
        return None, "sem bash no PATH"
    caminho = os.path.realpath(caminho)
    r = subprocess.run([caminho, "--norc", "--noprofile", "-r", "-c",
                        'echo "${BASH_VERSINFO[0]}"; shopt -q restricted_shell && echo restrito'],
                       capture_output=True, text=True, env={}, stdin=subprocess.DEVNULL, timeout=5)
    linhas = r.stdout.split()
    if not linhas or not linhas[0].isdigit() or int(linhas[0]) < 4:
        return None, f"bash {linhas[:1]} anterior ao 4"
    if "restrito" not in linhas:
        return None, "bash sem o modo restrito (-r)"
    return caminho, None


def rodado_pelo_bash(bash, variante):
    """O que o bash executa da variante, pelo oráculo: os comandos externos, cada um como `nome args` já expandidos.
    `HOME` e a pasta de trabalho numa pasta temporária nova, ambiente só com `PATH` e `HOME`, stdin vazio, prazo de
    5 s e o grupo de processos inteiro morto ao terminar."""
    with tempfile.TemporaryDirectory(prefix="forge-oraculo-") as tmp:
        env = {"PATH": str(Path(tmp) / "inexistente"), "HOME": tmp}
        p = subprocess.Popen([bash, "--norc", "--noprofile", "-r", "-c", PROLOGO_DO_ORACULO + variante], cwd=tmp,
                             env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
        try:
            _, erro = p.communicate(timeout=5)
        finally:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(p.pid, signal.SIGKILL)
            p.wait()
    return [linha[len("RODOU "):] for linha in erro.splitlines() if linha.startswith("RODOU ")]


# T3: modelos `<construção> #x⏎echo R`. Fora de G, nenhum `#` pode abrir comentário; em G, todo `#` marcado tem de ser
# comentário também para o bash.
MODELOS_FORA_DE_G = (
    "((#x)); echo R", "(( 1 #x )); echo R", "for ((i=0; i<1 #x; i++)); do :; done; echo R", "echo $(( 1 #x )); echo R",
    "echo $[1 #x]; echo R", "echo ${x:- #x}; echo R", "x=abc; echo ${x/ #y/z}; echo R", "echo `echo a #x`; echo R",
    "[[ a =~ ( #x) ]]; echo R", "[[ a =~ (a|#x) ]]; echo R", "[[ a == @(a| #x) ]]; echo R", "echo $(echo a)#x; echo R",
    "echo $(echo a) #x\necho R", "(true)#x\necho R", "(true) #x\necho R", "echo <(true) #x\necho R",
    "case a in a) #x\necho R;; esac", "a=( #x\n1 ); echo R", "f() #x\n{ echo R; }", "echo $'a' #x\necho R",
    "echo $\"a\" #x\necho R", "echo \"$(echo a)\" #x\necho R", "cat <<< a #x\necho R", "echo >#x\necho R",
    "echo a\\\n#x; echo R", "echo \"a\nb\" `true` #x\necho R", "echo a\r #x\necho R", "x=1 =~ #x\necho R",
)
MODELOS_EM_G = (
    "ls #x\necho R", "ls;#x\necho R", "ls&&#x\necho R", "ls|#x\necho R", "ls &#x\necho R", "{ ls; } #x\necho R",
    "[[ a == a ]] #x\necho R", "[[ a == a #x\n]] && echo R", "echo \"a $b\" #x\necho R", "echo 'a(b' #x\necho R",
    "echo a\\(b #x\necho R", "echo $# #x\necho R", "echo $@ $1 $? #x\necho R", "coproc true #x\necho R",
    "echo >&2 #x\necho R", "! true #x\necho R", "x=1 #x\necho R", "echo {a,b} #x\necho R", "echo a#b #x\necho R",
    "for i in 1; do echo R; done #x\necho R", "if true; then echo R; fi #x\necho R", "case a in #x\na) echo R;; esac",
    "echo ~ #x\necho R", "time ls #x\necho R", "echo a\\ b #x\necho R", "ls # um\nls # dois\necho R",
    "echo \"it's\" #x\necho R", "git log -1 # don't\necho R",
)
_CORPUS = []
FIXTURE_DE_ORCAMENTO = "crase-aninhada-em-60-pastas-no-verify-bloqueia"  # só o teste de orçamento de tempo a usa


def bash_aceita(linha):
    """`bash -n`: o bash lê a linha sem erro de sintaxe (nada é executado)."""
    return subprocess.run(["bash", "-n", "-c", linha], capture_output=True).returncode == 0


class Fixture:
    def __init__(self, caminho, dados=None):
        self.caminho = caminho
        self.dados = json.loads(caminho.read_text(encoding="utf-8")) if dados is None else dados
        self.hook = caminho.parent.name

    def montar(self, tmp, outro):
        raiz = tmp / "proj"
        raiz.mkdir()
        d = self.dados
        mapa = {"{tmp}": str(tmp), "{raiz}": str(raiz), "{pid_vivo}": os.getpid(), "{pid_outro}": outro,
                "{pid_morto}": pid_morto(), "{pid_ns}": namespace_de_pid()}
        for chave, pasta in (("{marca}", raiz), ("{marca_wt}", tmp / "wt")):  # a marca da sessão: uma por raiz
            mapa[chave] = f".git/forge/projeto-{hashlib.sha256(os.path.realpath(pasta).encode()).hexdigest()[:16]}"
        git("init", "-q", "-b", "develop", cwd=raiz)
        git("config", "user.email", "t@example.com", cwd=raiz)
        git("config", "user.name", "Teste", cwd=raiz)
        arquivos = dict(d.get("arquivos", {}))
        arquivos.setdefault("README.md", "projeto\n")
        if d.get("forge", True):
            arquivos[".forge/versao"] = "0.5.0\n"
        arquivos[".forge/config.json"] = json.dumps({"pesados": PESADOS_DA_STACK})  # como o forge-init grava
        if "config" in d:
            arquivos[".forge/config.json"] = json.dumps(d["config"])
        if "config_bruta" in d:
            arquivos[".forge/config.json"] = d["config_bruta"]
        arquivos[".gitignore"] = ".forge/run/\n"
        self.gravar(raiz, arquivos, mapa)
        for rel in d.get("executaveis", []):
            (raiz / rel).chmod(0o755)
        for rel, alvo in d.get("links", {}).items():
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (raiz / rel).symlink_to(substituir(alvo, mapa, 0))
        git("add", "-A", cwd=raiz)
        git("commit", "-q", "-m", "base", cwd=raiz)
        for passo in d.get("git", []):
            if "worktree" in passo:
                if passo.get("solto"):  # HEAD solto, sem branch (cópia de review)
                    git("worktree", "add", "-q", "--detach", str(tmp / passo["worktree"]), cwd=raiz)
                else:
                    git("worktree", "add", "-q", "-b", passo["branch"], str(tmp / passo["worktree"]), cwd=raiz)
            elif "branch" in passo:
                git("switch", "-q", "-c", passo["branch"], cwd=raiz)
            elif "checkout" in passo:
                git("switch", "-q", passo["checkout"], cwd=raiz)
            elif "config" in passo:
                for chave, valor in passo["config"].items():
                    git("config", chave, valor, cwd=raiz)
            elif "ref" in passo:  # ex.: refs/remotes/origin/x apontando para o HEAD, como depois de um fetch
                git("update-ref", passo["ref"], "HEAD", cwd=raiz)
            if "arquivos" in passo:
                mapa["{HEAD}"] = git("rev-parse", "HEAD", cwd=raiz).stdout.strip()
                self.gravar(raiz, passo["arquivos"], mapa)
            if "commit" in passo:
                git("add", "-A", cwd=raiz)
                git("commit", "-q", "-m", passo["commit"], cwd=raiz)
        for pasta, conf in d.get("repos", {}).items():
            self.repositorio(tmp / pasta, conf, mapa)
        agora = time.time()
        if d.get("estado"):
            run = raiz / ".forge" / "run"
            run.mkdir(parents=True, exist_ok=True)
            for nome, conteudo in d["estado"].items():
                conteudo = substituir(conteudo, mapa, agora)
                (run / nome).write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo),
                                        encoding="utf-8")
        self.passos = d.get("passos", [])
        self.mapa, self.agora = mapa, agora
        entrada = substituir(d["entrada"], mapa, agora)
        entrada.setdefault("cwd", str(raiz))
        return raiz, entrada

    def executar_passos(self, raiz, rodar_hook):
        """Roda os `passos` (ver o cabeçalho) antes da entrada principal."""
        for passo in self.passos:
            if "entrada" in passo:
                entrada = substituir(passo["entrada"], self.mapa, self.agora)
                entrada.setdefault("cwd", str(raiz))
                conferir_passo(entrada, rodar_hook(entrada))
            for caminho in passo.get("remover", []):
                (raiz / substituir(caminho, self.mapa, 0)).unlink()
            if "git" in passo:
                git(*substituir(passo["git"], self.mapa, 0), cwd=raiz)
            for modo, chave in (("w", "gravar"), ("a", "anexar")):
                for caminho, conteudo in passo.get(chave, {}).items():
                    alvo = raiz / substituir(caminho, self.mapa, 0)
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    with open(alvo, modo, encoding="utf-8") as f:
                        f.write(substituir(texto(conteudo), self.mapa, 0))

    def repositorio(self, pasta, conf, mapa):
        """Outro repositório git do fixture (`repos`): arquivos, um commit e os remotos."""
        pasta.mkdir(parents=True)
        git("init", "-q", "-b", conf.get("branch", "develop"), cwd=pasta)
        git("config", "user.email", "t@example.com", cwd=pasta)
        git("config", "user.name", "Teste", cwd=pasta)
        self.gravar(pasta, {"README.md": "repo\n", **conf.get("arquivos", {})}, mapa)
        git("add", "-A", cwd=pasta)
        git("commit", "-q", "-m", "base", cwd=pasta)
        for nome, url in conf.get("remotos", {}).items():
            git("remote", "add", nome, url, cwd=pasta)

    @staticmethod
    def gravar(raiz, arquivos, mapa):
        for rel, conteudo in arquivos.items():
            p = raiz / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(substituir(texto(conteudo), mapa, 0), encoding="utf-8")


def montar_proc(tmp, proc):
    """/proc simulado em tmp/proc (FORGE_PROC); `{"ausente": true}` aponta para uma pasta sem os arquivos."""
    pasta = tmp / "proc"
    pasta.mkdir()
    proc = proc or {"ausente": True}
    if not proc.get("ausente"):
        (pasta / "loadavg").write_text(proc["loadavg"] + "\n", encoding="utf-8")
        kb = int(proc["mem_gb"] * 1024 * 1024)
        total = int(proc.get("mem_total_gb", 16) * 1024 * 1024)
        (pasta / "meminfo").write_text(f"MemTotal:       {total} kB\nMemFree:  1 kB\nMemAvailable:   {kb} kB\n",
                                       encoding="utf-8")
    return pasta


PRAZO_DO_CLAUDE_CODE_S = 10  # `timeout` de hooks/hooks.json: o Claude Code o trata como liberado


def rodar(hook, entrada, cwd, proc=None, extra=None, prazo=120, como_o_claude_code=False, producao=False, lento=False):
    """`como_o_claude_code`: o hook que passa de `PRAZO_DO_CLAUDE_CODE_S` é morto e a ação é liberada (código 0), como
    o Claude Code faz, e o vigia de prazo é o de produção; sem isso, o teste espera `prazo` s (largo, para a máquina
    carregada). `producao`: só o vigia de produção. `lento`: o passo lento injetado (`lancador`)."""
    env = ambiente_limpo()
    env.pop("FORGE_GUARDA_ABERTA", None)
    env.pop("FORGE_CARGA_LIVRE", None)
    env.update(extra or {})
    if proc is not None:
        env["FORGE_PROC"] = str(proc)
    comando = lancador(hook, producao or como_o_claude_code, lento)
    try:
        return subprocess.run(comando, input=json.dumps(entrada), cwd=cwd, env=env, capture_output=True,
                              text=True, timeout=PRAZO_DO_CLAUDE_CODE_S if como_o_claude_code else prazo)
    except subprocess.TimeoutExpired:
        if not como_o_claude_code:
            raise
        return subprocess.CompletedProcess(comando, 0, "", "")


# O git dos hooks tem 5 s (o hook inteiro tem 10 s em hooks.json); com os processos da suíte em paralelo a máquina
# carregada passa disso e o teste falharia sem o hook ter erro algum. Os testes rodam o hook pelo mesmo script, só com
# o prazo do git largo: o prazo de produção segue em bin/forge-check e é conferido à parte (test_timeout_de_rede...).
# O vigia de prazo (3 s, `_comum.PRAZO_DA_DECISAO_S`) segue o mesmo caminho: largo nos testes, de produção só onde o
# teste mede o prazo (`producao=True`). `lento` injeta num passo da decisão um `sleep` de 60 s, uma vez só (monkeypatch
# do processo do teste, sem tocar os hooks): o segundo `Hook.campo`, o primeiro que o hook lê depois do marcador.
PRAZO_GIT_NOS_TESTES = 120
PRAZO_DA_DECISAO_NOS_TESTES = 120
LANCADOR = """
import runpy, sys, time
sys.path.insert(0, sys.argv[1])
import _comum
_comum.forge_check().GIT_TIMEOUT_S = int(sys.argv[3])
if sys.argv[4] != "producao":
    _comum.PRAZO_DA_DECISAO_S = float(sys.argv[4])
if sys.argv[5] == "lento":
    campo, chamadas = _comum.Hook.campo, []
    def lento(self, *chaves):
        chamadas.append(1)
        if len(chamadas) == 2:  # a 1.a leitura é a do marcador; a 2.a é a 1.a do hook, depois dele
            time.sleep(60)
        return campo(self, *chaves)
    _comum.Hook.campo = lento
sys.argv = [sys.argv[2]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def lancador(hook, producao=False, lento=False):
    """Comando que roda hooks/<hook>.py como o Claude Code o roda, com o prazo do git largo para os testes."""
    return [sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / f"{hook}.py"), str(PRAZO_GIT_NOS_TESTES),
            "producao" if producao else str(PRAZO_DA_DECISAO_NOS_TESTES), "lento" if lento else ""]


class Hooks(unittest.TestCase):
    def setUp(self):
        self.fixtures = minimo([Fixture(p) for p in sorted(FIXTURES.glob("*/*.json"))], 460, "fixtures em tests/hooks/")

    def test_fixtures(self):
        self.assertTrue(self.fixtures, "nenhum fixture em tests/hooks/")
        casos = [(f"{f.hook}/{f.caminho.stem}", f) for f in self.fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(self.fixtures), "todo fixture é verificado")

    def executar_em_lote(self, casos):
        """Roda os casos (nome, Fixture) como subTest, em paralelo, menos os que dependem de PID ou da trava do `pesado`
        (um de cada vez, depois). Devolve quantos foram verificados."""
        outro = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])  # outra sessão viva
        self.addCleanup(outro.wait)
        self.addCleanup(outro.kill)
        em_serie = [c for c in casos if self.depende_de_pid_ou_trava(c[1])]
        em_paralelo = [c for c in casos if c not in em_serie]
        verificados = 0
        # Montar e rodar é espera de subprocesso (não segura o GIL); cada fixture tem a sua pasta temporária.
        # As falhas voltam como objeto e viram subTest na thread principal, com o mesmo nome de caso.
        trabalhadores = max(1, min(4, (os.cpu_count() or 2) // 2))
        with concurrent.futures.ThreadPoolExecutor(max_workers=trabalhadores) as pool:
            futuros = [(nome, pool.submit(self.executar_fixture, f, self._pasta_temporaria(), outro.pid))
                       for nome, f in em_paralelo]
            for nome, futuro in futuros:
                with self.subTest(fixture=nome):
                    verificados += 1
                    erro = futuro.exception()
                    if erro is not None:
                        raise erro
        for nome, f in em_serie:  # PID e trava global do `pesado`: um de cada vez, depois do paralelo
            with self.subTest(fixture=nome):
                verificados += 1
                self.executar_fixture(f, self._pasta_temporaria(), outro.pid)
        return verificados

    def _pasta_temporaria(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        return tmp

    @staticmethod
    def depende_de_pid_ou_trava(f):
        return f.hook == "pesado" or "{pid_" in json.dumps(f.dados)

    def executar_fixture(self, f, tmp, outro_pid):
        raiz, entrada = f.montar(tmp, outro_pid)
        proc = montar_proc(tmp, f.dados.get("proc"))
        extra = {k: v.replace("{tmp}", str(tmp)) for k, v in f.dados.get("env", {}).items()}
        extra["FORGE_NPROC"] = str((f.dados.get("proc") or {}).get("nproc", 8))
        if f.dados.get("pathlib_312"):  # a fixture provoca erro interno por Path.exists (tests/apoio_pathlib_312)
            extra["PYTHONPATH"] = str(PATHLIB_312)
        f.executar_passos(raiz, lambda e: rodar(f.hook, e, raiz, proc, extra))
        r = rodar(f.hook, entrada, raiz, proc, extra)
        esperado = f.dados["esperado"]
        if "saida" in esperado:  # só o vigia: aviso ao usuário, nunca contexto para o modelo
            self.assertEqual(f.hook, "vigia")
            self.assertNotEqual(entrada.get("hook_event_name"), "SessionStart", "SessionStart é silencioso")
            saida = json.loads(r.stdout)
            self.assertEqual(list(saida), ["systemMessage"])
            self.assertNotIn("\n", saida["systemMessage"], "uma linha só")
            self.assertRegex(saida["systemMessage"], r"^Forge: \d+ (violação\(ões\)|aviso\(s\)|mudança\(s\))(, \d+ \S+)* — ")
            self.assertIn(esperado["saida"], saida["systemMessage"])
        elif "pergunta" in esperado:  # só o conformidade: pede a confirmação da pessoa, com a consequência
            self.assertEqual(f.hook, "conformidade")
            saida = json.loads(r.stdout)["hookSpecificOutput"]
            self.assertEqual((saida["hookEventName"], saida["permissionDecision"]), ("PreToolUse", "ask"))
            self.assertNotIn("\n", saida["permissionDecisionReason"], "uma linha só")
            self.assertIn(esperado["pergunta"], saida["permissionDecisionReason"])
        else:
            self.assertEqual(r.stdout, "", "hook nunca escreve no stdout (ADR 0003: silencioso)")
        self.assertEqual(r.returncode, esperado["codigo"], r.stderr)
        if esperado["codigo"] == 0:
            self.assertEqual(r.stderr, "", "sem violação, sem saída")
        else:
            linha = r.stderr.rstrip("\n")
            self.assertNotIn("\n", linha, "uma linha só")
            self.assertLessEqual(len(linha), 200)
            self.assertRegex(linha, r"^R-[A-Z]+: ")
            self.assertIn(esperado["stderr"], linha)
        run = raiz / ".forge" / "run"
        if esperado.get("sem_run"):
            self.assertFalse(run.exists(), ".forge/run/ não deveria ser criado")
        for nome, conf in esperado.get("estado", {}).items():
            conteudo = (run / nome).read_text(encoding="utf-8")
            for trecho in conf.get("contem", []):
                self.assertIn(trecho, conteudo)
            for trecho in conf.get("ausente", []):
                self.assertNotIn(trecho, conteudo)
        for caminho in esperado.get("sem_caminho", []):
            self.assertFalse(Path(substituir(caminho, f.mapa, 0)).exists(), f"{caminho} não deveria existir")
        for nome in esperado.get("sem_arquivo", []):
            self.assertFalse((run / nome).exists(), f"{nome} deveria ter sido removido")
        if "erros_log" in esperado:
            self.assertIn(esperado["erros_log"], (run / "erros.log").read_text(encoding="utf-8"))
        elif (run / "erros.log").exists():  # só o aviso do FORGE_NPROC/FORGE_PROC (que os testes fixam) é esperado
            outras = [l for l in (run / "erros.log").read_text(encoding="utf-8").splitlines() if " Aviso: FORGE_" not in l]
            self.assertEqual(outras, [], "erro interno inesperado")
        if run.exists() and not f.dados.get("estado"):  # o hook criou .forge/run/
            self.assertEqual((run / ".gitignore").read_text(encoding="utf-8"), "*\n")


    def test_projeto_com_copia_atrasada_barra_o_pr_de_ponta_a_ponta(self):
        """Num projeto, com o cache do doutor dizendo `defasado` para esta versão do plugin, `gh pr create` sai com código 2 e uma
        linha com `R-CONFORMIDADE`, mesmo com review e QA aprovados; sem o atraso, o mesmo caso libera em silêncio."""
        versao = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        base = json.loads((FIXTURES / "parecer/pr-com-pareceres-aprovados.json").read_text(encoding="utf-8"))
        for atrasada, esperado in ((True, {"codigo": 2, "stderr": "R-CONFORMIDADE: forge-check"}), (False, {"codigo": 0})):
            with self.subTest(atrasada=atrasada):
                tmp = self._pasta_temporaria()
                cache = {"data": time.strftime("%Y-%m-%d"), "defasado": atrasada, "atual": versao, "ultima": "999.0.0"}
                dados = {**base, "estado": {"versao-nova": cache}, "esperado": esperado}
                arquivo = tmp / "parecer" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(dados), encoding="utf-8")
                self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    def test_vigia_com_git_lento_nao_falha_por_carga(self):
        """O git lento (carga da máquina com a suíte em processos) não derruba o vigia: o primeiro `git` do PATH demora 6 s, mais que
        os 5 s de produção, e o fixture `settings-local-nao-conta` segue verde; com o prazo de produção ele falharia."""
        base = json.loads((FIXTURES / "vigia/settings-local-nao-conta.json").read_text(encoding="utf-8"))
        real = shutil.which("git")
        for prazo, passa in ((120, True), (5, False)):
            with self.subTest(prazo=prazo), mock.patch(f"{__name__}.PRAZO_GIT_NOS_TESTES", prazo):
                tmp = self._pasta_temporaria()
                (tmp / "lento").mkdir()
                atalho = tmp / "lento" / "git"
                atalho.write_text(f'#!/bin/sh\n[ -e "{tmp}/lento/ja" ] || {{ : > "{tmp}/lento/ja"; sleep 6; }}\nexec "{real}" "$@"\n', encoding="utf-8")
                atalho.chmod(0o755)
                dados = {**base, "env": {"PATH": f"{tmp / 'lento'}{os.pathsep}{os.environ['PATH']}"}}
                arquivo = tmp / "vigia" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(dados), encoding="utf-8")
                if passa:
                    self.executar_fixture(Fixture(arquivo), tmp, os.getpid())
                else:
                    with self.assertRaises(AssertionError):
                        self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    def test_git_rm_com_pathspec_magico_bloqueia(self):
        """As formas do pathspec do git (`:(literal)`, `:(glob)`, `:(icase)`, `:/`, curinga e `-r :/`) valem pelo que o git
        resolve, como `:(top)` (fixture `git-rm-pathspec-magica-bloqueia`); pathspec que não alcança caminho em vigor passa."""
        formas = {"git rm ':(literal).forge/versao'": 2, "git rm ':(glob)**/versao'": 2, "git rm ':(icase).FORGE/VERSAO'": 2,
                  "git rm ':/.forge/versao'": 2, "git rm '*versao'": 2, "git rm -r ':/'": 2, "git rm -r '*'": 2,
                  "git checkout HEAD -- ':(top).forge/versao'": 2, "git restore -s HEAD ':(glob)**/versao'": 2,
                  "git rm ':(top)src/app.js'": 0, "git rm 'src/*.js'": 0, "git checkout -- .": 0, "git restore .": 0}
        for comando, codigo in formas.items():
            with self.subTest(comando=comando):
                tmp = self._pasta_temporaria()
                dados = {"arquivos": {"src/app.js": "v1\n", ".githooks/pre-push": "#!/bin/sh\n"},
                         "env": {"CLAUDE_PROJECT_DIR": "{tmp}/proj"},
                         "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": "forge:dev",
                                     "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
                         "esperado": {"codigo": codigo, "stderr": "R-CONFORMIDADE"}}
                arquivo = tmp / "conformidade" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(dados), encoding="utf-8")
                self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    def test_pathspecs_por_variavel_de_ambiente_valem_como_as_opcoes(self):
        """`GIT_*_PATHSPECS` (atribuição na linha, `env`, `export`) ligam o modo de pathspec como as opções `--*-pathspecs`
        (fixture `git-rm-env-icase-pathspecs-bloqueia`); falso explícito e pathspec que não alcança caminho em vigor passam."""
        formas = {"GIT_ICASE_PATHSPECS=1 git rm .FORGE/VERSAO": 2, "env GIT_ICASE_PATHSPECS=1 git rm -q .FORGE/VERSAO": 2,
                  "export GIT_ICASE_PATHSPECS=1; git rm .FORGE/VERSAO": 2,
                  "GIT_ICASE_PATHSPECS=1 git checkout HEAD -- .FORGE/VERSAO": 2,
                  "GIT_GLOB_PATHSPECS=1 git rm '**/versao'": 2, "GIT_ICASE_PATHSPECS=0 git rm .FORGE/VERSAO": 0,
                  "GIT_ICASE_PATHSPECS=1 git rm src/app.js": 0}
        for comando, codigo in formas.items():
            with self.subTest(comando=comando):
                tmp = self._pasta_temporaria()
                dados = {"arquivos": {"src/app.js": "v1\n", ".githooks/pre-push": "#!/bin/sh\n"},
                         "env": {"CLAUDE_PROJECT_DIR": "{tmp}/proj"},
                         "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": "forge:dev",
                                     "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
                         "esperado": {"codigo": codigo, "stderr": "R-CONFORMIDADE"}}
                arquivo = tmp / "conformidade" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(dados), encoding="utf-8")
                self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    # R-CONTRIB: o rótulo afrouxa-regra só do dono (fixtures `rotulo-so-dono-*`); aqui, as formas da volta 1 -----------
    @staticmethod
    def dados_da_sessao_do_forge(comando, gh, codigo):
        """Sessão do Forge (a raiz é um clone do Forge, sem `.forge/versao`) com um `gh` falso no PATH, sem rede."""
        esperado = {"codigo": codigo}
        if codigo:
            esperado["stderr"] = "R-CONTRIB: "
        return {"arquivos": {"src/app.js": "v1\n", "bin/gh": gh, ".claude-plugin/plugin.json": "{\"name\": \"forge\"}"},
                "executaveis": ["bin/gh"], "forge": False,
                "env": {"HOME": "{tmp}/home", "CLAUDE_PROJECT_DIR": "{tmp}/proj", "PATH": "{tmp}/proj/bin:/usr/bin:/bin"},
                "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "hook_event_name": "PreToolUse",
                            "tool_use_id": "toolu_9"},
                "esperado": esperado}

    def rodar_dados(self, dados):
        tmp = self._pasta_temporaria()
        arquivo = tmp / "conformidade" / "caso.json"
        arquivo.parent.mkdir()
        arquivo.write_text(json.dumps(dados), encoding="utf-8")
        self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    def test_fixtures_da_sessao_do_forge_que_citam_o_rotulo_usam_o_gh_falso(self):
        """Nenhum resultado depende da credencial da máquina: toda fixture da sessão do Forge (`forge: false` com o
        `plugin.json` do Forge na raiz) que cita o rótulo traz o `gh` falso executável e o põe à frente no PATH."""
        achadas = []
        for f in self.fixtures:
            d = f.dados
            if d.get("forge") is not False or ".claude-plugin/plugin.json" not in d.get("arquivos", {}):
                continue
            if "afrouxa-regra" not in json.dumps(d.get("entrada", {})):
                continue
            achadas.append(f.caminho.name)
            with self.subTest(fixture=f.caminho.name):
                self.assertIn("bin/gh", d.get("arquivos", {}))
                self.assertIn("bin/gh", d.get("executaveis", []))
                self.assertTrue(d.get("env", {}).get("PATH", "").startswith("{tmp}/proj/bin:"))
        self.assertGreaterEqual(len(achadas), 10, "fixtures da sessão do Forge com o rótulo")

    def test_rotulo_so_dono_formas_alternativas(self):
        """Volta 1 (segurança A2, A3, A4 e R2): GraphQL por caminho ou URL, REST com `?…` ou `#…`, crase (fora de aspas
        simples) e criar ou renomear rótulo com o nome barram outra conta; a conta do dono passa; o resto não muda."""
        mutacao = "mutation { addLabelsToLabelable(input:{labelableId:\\\"X\\\", labelIds:[\\\"Y\\\"]}) { clientMutationId } }"
        barram = [
            f"gh api /graphql -f query=\"{mutacao}\"",
            f"gh api https://api.github.com/graphql -f query=\"{mutacao}\"",
            f"gh api https://ghe.exemplo/api/graphql -f query=\"{mutacao}\"",
            f"gh api 'graphql?x=1' -f query=\"{mutacao}\"",
            "gh api 'repos/o/r/issues/70/labels?x=1' -f 'labels[]=afrouxa-regra'",
            "gh api 'repos/o/r/issues/70/labels#x' -f 'labels[]=afrouxa-regra'",
            "gh api 'https://api.github.com/repos/o/r/issues/70/labels/' -f 'labels[]=afrouxa-regra'",
            "echo `gh pr edit 70 --add-label afrouxa-regra`",
            "x=`gh pr edit 70 --add-label afrouxa-regra`",
            "echo \"a `gh issue edit 70 --add-label afrouxa-regra` b\"",
            "bash -c 'echo `gh pr edit 70 --add-label afrouxa-regra`'",
            "echo `gh pr edit 70 --add-label afrouxa-regra",  # crase sem par: não se analisa e cita o rótulo
            "gh label create afrouxa-regra",
            "gh label edit tmp --name afrouxa-regra",
            "gh label edit afrouxa-regra --name tmp",
            "gh api -X PATCH repos/o/r/labels/afrouxa-regra -f new_name=tmp",
            "gh api repos/o/r/labels/tmp -X PATCH -f new_name=afrouxa-regra",
            "gh api repos/o/r/labels -f name=afrouxa-regra",
            "gh api graphql -f query='mutation { updateLabel(input:{id:\"L\", name:\"x\"}) { clientMutationId } }'",
            "gh api /graphql -f query='mutation { createLabel(input:{repositoryId:\"R\", name:\"x\"}) { clientMutationId } }'",
        ]
        passam = ["echo 'a `gh pr edit 70 --add-label afrouxa-regra` b'", "gh issue comment 70 --body 'cite `afrouxa-regra`'",
                  "gh label create bug", "gh label edit bug --name defeito", "gh pr edit 70 --add-label bug",
                  "gh api /graphql -f query='query { viewer { login } }'", "gh api 'repos/o/r/issues/70/labels?x=1' -f 'labels[]=bug'",
                  "echo `date`"]
        casos = [(c, "#!/bin/sh\necho outra-pessoa\n", 2) for c in barram]
        casos += [(c, "#!/bin/sh\necho outra-pessoa\n", 0) for c in passam]
        casos += [(c, "#!/bin/sh\necho Rodrigo-Isensee\n", 0) for c in barram[:9] + barram[12:15]]
        for comando, gh, codigo in minimo(casos, 40, "casos de rótulo"):
            with self.subTest(comando=comando, gh=gh.split()[-1], codigo=codigo):
                self.rodar_dados(self.dados_da_sessao_do_forge(comando, gh, codigo))

    def test_rotulo_so_dono_volta_2_crase_escapada_comentario_clone_e_remocao(self):
        """Volta 2 (segurança B1, review 1 a 3): a crase escapada em `bash -c`/`sh -c`/`eval`, a aspa simples de um comentário
        antes da crase, `gh label clone` e `--remove-label afrouxa-regra` exigem o dono; a conta do dono passa; o resto não muda."""
        rotulo = "gh pr edit 70 --add-label afrouxa-regra"
        barram = [
            f'bash -c "echo \\`{rotulo}\\`"',
            f'sh -c "x=\\`{rotulo}\\`"',
            f'eval "echo \\`{rotulo}\\`"',
            f"echo hi # don't\nx=`{rotulo}`",
            f"echo hi # don't\necho \"`{rotulo}`\"",
            "gh label clone o/outro",
            "gh label clone o/outro --force",
            "gh pr edit 70 --remove-label afrouxa-regra",
            "gh issue edit 70 --remove-label=afrouxa-regra",
            "gh pr edit 70 --remove-label bug,afrouxa-regra",
            "gh api -X DELETE repos/o/r/issues/70/labels/afrouxa-regra",
        ]
        passam = [f'bash -c "echo \\`date\\`"', f'echo "\\`{rotulo}\\`"', f"echo hi # don't\nx=`date`",
                  "echo a # `" + rotulo + "`", "gh pr edit 70 --remove-label bug", "gh label list"]
        casos = [(c, "#!/bin/sh\necho outra-pessoa\n", 2) for c in barram]
        casos += [(c, "#!/bin/sh\necho outra-pessoa\n", 0) for c in passam]
        casos += [(c, "#!/bin/sh\necho Rodrigo-Isensee\n", 0) for c in barram]
        for comando, gh, codigo in minimo(casos, 20, "casos de rótulo da volta 2"):
            with self.subTest(comando=comando, gh=gh.split()[-1], codigo=codigo):
                self.rodar_dados(self.dados_da_sessao_do_forge(comando, gh, codigo))

    def test_rotulo_so_dono_volta_2_sessao_de_projeto(self):
        """Segurança R5: as formas da crase escapada e do comentário também são barradas na sessão de projeto (R-CONTRIB),
        quando apontam para o Forge; a mesma linha sem apontar para o Forge passa."""
        alvo = "gh pr edit https://github.com/rodrigo-isensee/Forge/pull/70 --add-label afrouxa-regra"
        casos = [
            (f'bash -c "echo \\`{alvo}\\`"', 2), (f'sh -c "x=\\`{alvo}\\`"', 2), (f'eval "echo \\`{alvo}\\`"', 2),
            (f"echo hi # don't\nx=`{alvo}`", 2), (f"echo hi # don't\necho \"`{alvo}`\"", 2),
            ('bash -c "echo \\`date\\`"', 0), ("echo hi # don't\nx=`date`", 0),
        ]
        for comando, codigo in minimo(casos, 6, "casos de projeto da volta 2"):
            with self.subTest(comando=comando):
                esperado = {"codigo": codigo}
                if codigo:  # barra por R-CONTRIB (alvo no Forge) ou R-CONFORMIDADE (crase com ação crítica, não modelada)
                    esperado["stderr"] = "R-CON"
                self.rodar_dados({"arquivos": {"src/app.js": "v1\n"}, "env": {"HOME": "{tmp}/home", "CLAUDE_PROJECT_DIR": "{tmp}/proj"},
                                  "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "hook_event_name": "PreToolUse",
                                              "tool_use_id": "toolu_9"}, "esperado": esperado})

    def test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook(self):
        """Segurança A1: `gh` que não responde (com um filho segurando a saída) barra dentro do timeout do hook."""
        limite = min(h["timeout"] for g in json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
                     for h in g["hooks"] if h["args"][0].endswith("/conformidade.py"))
        inicio = time.monotonic()
        self.rodar_dados(self.dados_da_sessao_do_forge("gh pr edit 70 --add-label afrouxa-regra",
                                                       "#!/bin/sh\nsleep 30\necho outra-pessoa\n", 2))
        self.assertLess(time.monotonic() - inicio, limite - 1, "a decisão sai antes do Claude Code matar o hook")

    def test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento(self):
        """Segurança A1 do LOTE-LEITURA-HOOK: 60 `cd` e 60 crases aninhadas terminando em push com --no-verify refaziam a
        conferência 37 630 vezes (10,9 s, acima do timeout do hooks.json, e o Claude Code libera o comando que o hook não
        decidiu a tempo). O `conformidade` recusa (saída 2) em uma fração do prazo."""
        limite = min(h["timeout"] for g in json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
                     for h in g["hooks"] if h["args"][0].endswith("/conformidade.py"))
        dados = json.loads((FIXTURES / "conformidade" / f"{FIXTURE_DE_ORCAMENTO}.json")
                           .read_text(encoding="utf-8"))
        comando = dados["entrada"]["tool_input"]["command"]
        self.assertGreaterEqual(comando.count("cd d"), 60, "a linha adversária tem as 60 pastas")
        self.assertGreaterEqual(comando.count("`echo"), 60, "a linha adversária tem as 60 crases aninhadas")
        self.assertTrue(comando.endswith("--no-verify origin feature/x`"), "e termina na ação que a base recusava")
        inicio = time.monotonic()
        self.rodar_dados(dados)
        self.assertLess(time.monotonic() - inicio, limite / 2, "a decisão sai bem antes do Claude Code matar o hook")
        # A1 do review: o custo de cada conferência cresce com o corpo; 20 `cd` e 19 crases distintas de 5 a 20 KB
        # (a de 8 KB tem 152 KB e passava de 14 s com o teto só por contagem). A base recusava pela rede da ADR 0011.
        for pastas, crases, kb in ((20, 19, 5), (20, 19, 8), (15, 25, 20)):
            corpo = " ".join(f"`echo \\`echo \\\\\\`ls\\\\\\`\\` c{i} {'a' * kb * 1024}`" for i in range(crases))
            linha = " && ".join(f"cd d{i}" for i in range(pastas)) + f" && {corpo} `git push --no-verify origin feature/x`"
            with self.subTest(pastas=pastas, crases=crases, kb=kb):
                self.assertGreater(len(linha), crases * kb * 1024)
                grande = json.loads(json.dumps(dados))
                grande["entrada"]["tool_input"]["command"] = linha
                inicio = time.monotonic()
                self.rodar_dados(grande)
                self.assertLess(time.monotonic() - inicio, limite / 2, "a linha grande também sai antes do prazo")
        # Recomendação do review (volta 3): uma conferência só de 290 mil caracteres levava 4,2 s, perto do timeout com a
        # máquina carregada; o teto de caracteres fica em cerca de 150 mil, e a linha logo acima dele recusa por ele.
        _, conformidade, _ = modulos_dos_hooks()
        self.assertLessEqual(conformidade.TETO_DE_CARACTERES, 150_000)
        grande = json.loads(json.dumps(dados))
        grande["entrada"]["tool_input"]["command"] = ("echo " + "a" * conformidade.TETO_DE_CARACTERES
                                                      + " && git push --no-verify origin feature/x")
        grande["esperado"] = {"codigo": 2, "stderr": "linha longa demais"}
        inicio = time.monotonic()
        self.rodar_dados(grande)
        self.assertLess(time.monotonic() - inicio, limite / 2, "a recusa pelo teto sai antes do prazo")

    def test_timeout_de_rede_dos_hooks_abaixo_do_hooks_json(self):
        """Segurança A1: todo subprocesso de rede dos hooks (`gh`, `curl`, `git fetch`...) tem limite de tempo menor que o
        menor timeout do hooks.json; senão o Claude Code mata o hook e o comando segue (falha aberta)."""
        import ast
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        limite = min(h["timeout"] for grupos in d["hooks"].values() for g in grupos for h in g["hooks"])
        rede, git_rede = {"gh", "curl", "wget", "ssh"}, {"fetch", "pull", "push", "ls-remote", "clone"}
        achados = []
        for arquivo in minimo(sorted(HOOKS.glob("*.py")), 5, "scripts de hook"):
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
            constantes = {alvo.id: no.value.value for no in arvore.body if isinstance(no, ast.Assign)
                          and isinstance(no.value, ast.Constant) for alvo in no.targets if isinstance(alvo, ast.Name)}
            for funcao in (n for n in ast.walk(arvore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
                listas = [n for n in ast.walk(funcao) if isinstance(n, ast.List) and n.elts
                          and isinstance(n.elts[0], ast.Constant)]
                de_rede = [n for n in listas if n.elts[0].value in rede or n.elts[0].value == "git" and any(
                    isinstance(e, ast.Constant) and e.value in git_rede for e in n.elts[1:])]
                if not de_rede:
                    continue
                prazos = [k.value for n in ast.walk(funcao) if isinstance(n, ast.Call) for k in n.keywords if k.arg == "timeout"]
                with self.subTest(arquivo=arquivo.name, funcao=funcao.name):
                    achados.append(funcao.name)
                    self.assertTrue(prazos, "subprocesso de rede sem timeout")
                    for prazo in prazos:
                        valor = prazo.value if isinstance(prazo, ast.Constant) else constantes.get(getattr(prazo, "id", None))
                        self.assertIsInstance(valor, (int, float), f"timeout não resolvido: {ast.dump(prazo)}")
                        self.assertLess(valor, limite, f"timeout {valor} s não fica abaixo dos {limite} s do hooks.json")
        minimo(achados, 1, "subprocessos de rede nos hooks")

    def test_rotulo_so_dono_erro_inesperado_falha_fechado(self):
        """Revisão (4) e segurança R3: erro do analisador que não é ValueError barra na sessão do Forge quando a linha
        cita o rótulo (mesmo com a conta do dono: o hook não pôde decidir); a linha que não cita segue a regra geral."""
        for comando, codigo in {"gh pr edit 70 --add-label afrouxa-regra": 2, "gh pr edit 70 --add-label bug": 0,
                                "gh api graphql -f query='mutation { addLabelsToLabelable(input:{}) { x } }'": 2}.items():
            with self.subTest(comando=comando):
                tmp = self._pasta_temporaria()
                f = Fixture.__new__(Fixture)
                f.caminho, f.hook = tmp / "conformidade" / "caso.json", "conformidade"
                f.dados = self.dados_da_sessao_do_forge(comando, "#!/bin/sh\necho Rodrigo-Isensee\n", codigo)
                raiz, entrada = f.montar(tmp, os.getpid())
                envoltorio = tmp / "envoltorio.py"
                envoltorio.write_text(
                    f"import sys\nsys.path.insert(0, {str(HOOKS)!r})\nimport conformidade\n"
                    "def quebra(*a, **k):\n    raise RuntimeError('quebra de teste')\n"
                    "conformidade.conteudos_de_crase = quebra\n"
                    "conformidade.executar('conformidade', conformidade.principal, conformidade.CRITICO)\n", encoding="utf-8")
                env = ambiente_limpo()
                env.pop("FORGE_GUARDA_ABERTA", None)
                env.update({k: v.replace("{tmp}", str(tmp)) for k, v in f.dados["env"].items()})
                r = subprocess.run([sys.executable, str(envoltorio)], input=json.dumps(entrada), cwd=raiz, env=env,
                                   capture_output=True, text=True, timeout=30)
                self.assertEqual(r.returncode, codigo, r.stderr)
                if codigo:
                    self.assertIn("R-CONTRIB: erro interno ao conferir o rótulo afrouxa-regra", r.stderr)

    def test_contrib_graphql_por_caminho_na_sessao_de_projeto(self):
        """Segurança R4: na sessão de projeto, `/graphql` e a URL completa do GraphQL valem como `graphql` (R-CONTRIB)."""
        consulta = "mutation { closePullRequest(input:{pullRequestId:\"X\"}) { clientMutationId } }"
        casos = {f"gh api /graphql -f query='{consulta}'": 2, f"gh api https://api.github.com/graphql -f query='{consulta}'": 2,
                 "gh api /graphql -f query='mutation { addLabelsToLabelable(input:{labelableId:\"X\"}) { x } }'": 2,
                 "gh api 'graphql?a=1' -f query='mutation { updatePullRequest(input:{}) { x } }'": 2,
                 "gh api /graphql -f query='query { viewer { login } }'": 0}
        for comando, codigo in casos.items():
            with self.subTest(comando=comando):
                esperado = {"codigo": codigo, **({"stderr": "R-CONTRIB: gh api"} if codigo else {})}
                self.rodar_dados({"arquivos": {"src/app.js": "v1\n"}, "env": {"HOME": "{tmp}/home"},
                                  "entrada": {"tool_name": "Bash", "tool_input": {"command": comando},
                                              "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
                                  "esperado": esperado})

    def test_marca_de_projeto_por_raiz_e_nunca_apagada(self):
        """A chave da marca é a raiz da cópia de trabalho: a worktree irmã tem marca própria e não herda a do clone; o
        `SessionStart` só grava, nunca apaga."""
        import _comum
        tmp = self._pasta_temporaria()
        clone, wt = tmp / "clone", tmp / "wt"
        clone.mkdir()
        git("init", "-q", "-b", "develop", cwd=clone)
        git("config", "user.email", "t@example.com", cwd=clone)
        git("config", "user.name", "Teste", cwd=clone)
        (clone / ".forge").mkdir()
        (clone / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("add", "-A", cwd=clone)
        git("commit", "-q", "-m", "base", cwd=clone)
        git("worktree", "add", "-q", "-b", "melhoria/w", str(wt), cwd=clone)
        self.assertNotEqual(_comum.marca_de_projeto(clone), _comum.marca_de_projeto(wt))
        self.assertEqual(_comum.marca_de_projeto(clone).parent, _comum.marca_de_projeto(wt).parent)
        _comum.marcar_projeto(clone)
        (wt / ".forge" / "versao").unlink()
        self.assertTrue(_comum.projeto_marcado(clone))
        self.assertFalse(_comum.projeto_marcado(wt), "a worktree irmã não herda a marca do clone")
        self.assertIsNone(_comum.raiz_do_projeto(wt))
        _comum.marcar_projeto(wt)  # sem `.forge/versao`: não grava e, sobretudo, não apaga a marca do clone
        self.assertTrue(_comum.marca_de_projeto(clone).is_file())

    def test_cada_hook_tem_caso_que_passa_e_que_bloqueia(self):
        scripts = {p.stem for p in minimo(HOOKS.glob("*.py"), 5, "scripts de hook") if not p.name.startswith("_")}
        self.assertEqual({f.hook for f in self.fixtures}, scripts)
        for hook in scripts:
            codigos = {f.dados["esperado"]["codigo"] for f in self.fixtures if f.hook == hook}
            nomes = {f.caminho.stem for f in self.fixtures if f.hook == hook}
            with self.subTest(hook=hook):
                self.assertEqual(codigos, {0} if hook in ("vigia", "doutor") else {0, 2})  # o vigia e o doutor avisam, nunca bloqueiam
                self.assertIn("sem-forge-versao", nomes)
                self.assertIn("erro-interno", nomes)

    def test_hooks_json(self):
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        self.assertNotIn("UserPromptSubmit", d["hooks"], "hook não injeta contexto")
        self.assertNotIn("additionalContext", (HOOKS / "vigia.py").read_text(encoding="utf-8").replace(
            "nunca `additionalContext`", ""), "o vigia só avisa o usuário (systemMessage)")
        for evento in ("SessionStart", "Stop"):  # SessionStart: o stdout vira contexto do modelo (ADR 0003, item 1)
            comandos = {h["args"][0].rsplit("/", 1)[-1] for g in d["hooks"].get(evento, []) for h in g["hooks"]}
            self.assertLessEqual(comandos, {"vigia.py", "doutor.py"}, f"só o vigia e o doutor (sem stdout no SessionStart) ficam em {evento}")
        usados = set()
        for evento, grupos in d["hooks"].items():
            for g in grupos:
                for h in g["hooks"]:
                    with self.subTest(evento=evento, matcher=g.get("matcher")):
                        self.assertEqual(h["command"], "python3", "forma exec, sem shell")
                        self.assertEqual(h.get("timeout"), 10, "sem timeout, o padrão do Claude Code é 600 s")
                        self.assertEqual(len(h["args"]), 1)
                        rel = h["args"][0].replace("${CLAUDE_PLUGIN_ROOT}/", "")
                        self.assertTrue((RAIZ / rel).is_file(), rel)
                        usados.add(Path(rel).stem)
        minimo(usados, 5, "hooks registrados em hooks.json")
        self.assertEqual(usados, {f.hook for f in self.fixtures})
        matchers = {g.get("matcher") for g in d["hooks"]["PreToolUse"]}
        self.assertIn("Agent|Task", matchers)

    def test_medicao_do_proc_real_nao_quebra(self):
        sys.path.insert(0, str(HOOKS))
        import agentes
        carga, memoria, total = agentes.medir()
        self.assertTrue(carga is None or carga >= 0)
        self.assertTrue(memoria is None or memoria > 0)
        self.assertTrue(total is None or total >= (memoria or 0))
        self.assertEqual(agentes.medir(Path("/nao/existe")), (None, None, None))
        self.assertTrue((agentes.nucleos() or 1) >= 1)

    def test_faixas_do_teto_segue_o_hardware(self):
        """R-TETO: bloqueia com load >= 0,8 x nproc ou MemAvailable <= max(1 GB, 15% do total); o teto é nproc."""
        sys.path.insert(0, str(HOOKS))
        import agentes
        casos = [  # (load, disponível, total, nproc, carga alta)
            (3, 6, 8, 16, False), (12.7, 6, 8, 16, False), (12.8, 6, 8, 16, True),
            (6.39, 8, 16, 8, False), (6.4, 8, 16, 8, True), (0.1, 2.5, 16, 8, False), (0.1, 2.4, 16, 8, True),
            (0.1, 1.1, 4, 8, False), (0.1, 1.0, 4, 8, True), (0.8, 8, 16, 1, True), (0.7, 8, 16, 1, False)]
        for carga, memoria, total, nproc, alta in casos:
            with self.subTest(carga=carga, memoria=memoria, total=total, nproc=nproc):
                self.assertEqual(agentes.carga_alta(carga, memoria, total, nproc), alta)
                self.assertEqual(agentes.teto_adaptativo(carga, memoria, total, nproc), nproc)
        for faltando in range(4):  # sem uma das medidas: nunca é carga alta e o teto cai no padrão 3
            medidas = [1.0, 6.0, 16.0, 8]
            medidas[faltando] = None
            self.assertFalse(agentes.carga_alta(*medidas))
            self.assertEqual(agentes.teto_adaptativo(*medidas), 3)

    def test_teto_sem_leitura_nunca_passa_de_nproc(self):  # A3
        sys.path.insert(0, str(HOOKS))
        import agentes
        for nproc, esperado in ((1, 1), (2, 2), (3, 3), (8, 3), (None, 3)):
            with self.subTest(nproc=nproc):
                self.assertEqual(agentes.teto_adaptativo(None, None, None, nproc), esperado)

    def test_teto_maximo_vale_igual_sobre_o_fixo_e_o_adaptativo(self):  # A2
        sys.path.insert(0, str(HOOKS))
        import agentes
        pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, pasta, True)
        (pasta / "loadavg").write_text("0.1\n", encoding="utf-8")
        (pasta / "meminfo").write_text("MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"FORGE_NPROC": "16"}):
            self.assertEqual(agentes.calcular_teto({"teto_agentes": 8, "teto_maximo": 5}, pasta)[0], 5)
            self.assertEqual(agentes.calcular_teto({"teto_agentes": 4, "teto_maximo": 5}, pasta)[0], 4)
            self.assertEqual(agentes.calcular_teto({"teto_maximo": 5}, pasta)[0], 5)
            self.assertEqual(agentes.calcular_teto({}, pasta)[0], 16)

    def test_nucleos_respeita_a_afinidade(self):  # A4
        sys.path.insert(0, str(HOOKS))
        import agentes
        env = {k: v for k, v in os.environ.items() if k != "FORGE_NPROC"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(os, "sched_getaffinity", create=True, return_value={0, 1}), \
                    mock.patch.object(os, "cpu_count", return_value=16):
                self.assertEqual(agentes.nucleos(), 2)
            with mock.patch.object(os, "sched_getaffinity", create=True, side_effect=OSError), \
                    mock.patch.object(os, "cpu_count", return_value=16):
                self.assertIsNone(agentes.nucleos())
            with mock.patch.object(os, "cpu_count", return_value=4):
                saved = getattr(os, "sched_getaffinity", None)
                if saved is not None:
                    del os.sched_getaffinity
                try:
                    self.assertEqual(agentes.nucleos(), 4)
                finally:
                    if saved is not None:
                        os.sched_getaffinity = saved

    def test_registro_de_agente_solta_so_com_prova_de_sessao_morta(self):
        """F1 (C1-1, C1-2, C1-4): `sessao_morta` só diz True com pid válido, mesmo namespace e processo inexistente;
        `vigentes` nunca levanta por causa de um registro; a casca ou o pid morto não entram no registro."""
        sys.path.insert(0, str(HOOKS))
        import agentes
        agora, ns, morto = time.time(), agentes.namespace_de_pid(), pid_morto()
        self.assertIsNotNone(ns, "o teste precisa de /proc/self/ns/pid")
        base = {"id": "a1", "desde": agora - 60}
        self.assertTrue(agentes.sessao_morta({**base, "pid": morto, "pidns": ns}))
        self.assertFalse(agentes.sessao_morta({**base, "pid": os.getpid(), "pidns": ns}))
        for pid in ("123", True, 0, -1, 1.5, None, 2 ** 63, agentes.pid_max() + 1):
            self.assertFalse(agentes.sessao_morta({**base, "pid": pid, "pidns": ns}), repr(pid))
        self.assertFalse(agentes.sessao_morta({**base, "pid": morto}))
        self.assertFalse(agentes.sessao_morta({**base, "pid": morto, "pidns": "pid:[0]"}))
        registros = [None, "x", 7, {"desde": "ontem"}, {**base, "pid": 2 ** 70, "pidns": ns}, {**base, "pid": morto, "pidns": ns}]
        with mock.patch.object(agentes.os, "kill", side_effect=PermissionError):  # sem permissão: não é prova de morte
            self.assertEqual(agentes.vigentes(registros, agora, 7200), registros[4:])
        with mock.patch.object(agentes, "sessao_morta", side_effect=RuntimeError):  # erro por registro mantém o registro
            self.assertEqual(agentes.vigentes(registros, agora, 7200), registros[4:])
        self.assertEqual(agentes.vigentes(registros, agora, 7200), registros[4:5])
        hook = mock.Mock()
        hook.campo.return_value = "s1"
        with mock.patch.object(agentes, "pid_da_sessao", return_value=os.getpid()):
            self.assertEqual(agentes.da_sessao(hook), {"pid": os.getpid(), "pidns": ns, "sessao": "s1"})
        with mock.patch.object(agentes, "pid_da_sessao", return_value=morto):  # pid que já morreu
            self.assertEqual(agentes.da_sessao(hook), {})
        with mock.patch.object(agentes, "pid_da_sessao", return_value=os.getpid()), \
                mock.patch.object(agentes, "CASCAS", {Path(f"/proc/{os.getpid()}/comm").read_text(encoding="utf-8").strip()}):
            self.assertEqual(agentes.da_sessao(hook), {})  # casca: o intermediário some depois do hook
        hook.campo.return_value = None  # sem session_id
        with mock.patch.object(agentes, "pid_da_sessao", return_value=os.getpid()):
            self.assertEqual(agentes.da_sessao(hook), {})

    def test_variaveis_de_substituicao_ficam_no_erros_log(self):  # R1
        raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, raiz, True)
        git("init", "-q", cwd=raiz)
        (raiz / ".forge").mkdir()
        (raiz / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        proc = montar_proc(raiz, {"loadavg": "0.1 0.1 0.1", "mem_gb": 8})
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(raiz),
                   "tool_input": {"subagent_type": "x", "description": "d"}}
        r = rodar("agentes", entrada, raiz, proc, {"FORGE_NPROC": "8"})
        self.assertEqual(r.returncode, 0, r.stderr)
        logs = list(raiz.glob("**/erros.log"))
        self.assertEqual(len(logs), 1, "um erros.log")
        texto = logs[0].read_text(encoding="utf-8")
        self.assertIn("agentes Aviso: FORGE_NPROC=8", texto)
        self.assertIn("agentes Aviso: FORGE_PROC=", texto)

    def test_raiz_de_estado_no_clone_do_forge(self):
        """Anti-alucinação, fatia 3: a raiz do clone do Forge (cópia principal e worktree) é achada; o projeto vem antes
        do manifesto e pasta sem manifesto não é clone."""
        sys.path.insert(0, str(HOOKS))
        import _comum
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        clone, wt, projeto, alheio = tmp / "Forge", tmp / "wt" / "aa", tmp / "proj", tmp / "alheio"
        for pasta in (clone, projeto, alheio):
            (pasta / "docs").mkdir(parents=True)
            git("init", "-q", "-b", "develop", cwd=pasta)
            git("config", "user.email", "t@example.com", cwd=pasta)
            git("config", "user.name", "Teste", cwd=pasta)
        for pasta in (clone, projeto):
            (pasta / ".claude-plugin").mkdir()
            (pasta / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
        (projeto / ".forge").mkdir()
        (projeto / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("add", "-A", cwd=clone)
        git("commit", "-q", "-m", "base", cwd=clone)
        git("worktree", "add", "-q", "-b", "melhoria/x", str(wt), cwd=clone)
        self.assertEqual(_comum.raiz_de_estado(clone / "docs"), clone)
        self.assertEqual(_comum.raiz_de_estado(wt / "docs"), wt)
        self.assertEqual(_comum.raiz_de_estado(projeto / "docs"), projeto)
        self.assertIsNone(_comum.raiz_de_estado(alheio / "docs"))
        self.assertIsNone(_comum.raiz_de_estado(tmp))
        hook = _comum.Hook("parecer")
        hook.entrada = {"cwd": str(wt), "tool_input": {"command": "gh pr ready"}}
        self.assertIsNone(hook.projeto(wt))  # sem o pedido, o hook segue só nos projetos
        self.assertEqual(hook.projeto(wt, clone_do_forge=True), wt)
        self.assertEqual(hook.copia_principal().resolve(), clone.resolve())  # o estado vai para a cópia principal
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
            self.assertFalse(_comum.sessao_vigiada(hook))  # pasta corrente no clone, fora de ~/.forge-contrib
            self.assertTrue(_comum.sessao_vigiada(hook, clone_do_forge=True))
            hook.entrada["cwd"] = str(tmp)
            os.environ["CLAUDE_PROJECT_DIR"] = str(clone)  # sessão do dono em ~/Forge, pasta corrente fora dela
            self.assertTrue(_comum.sessao_vigiada(hook, clone_do_forge=True))
            erro = io.StringIO()
            with self.assertRaises(SystemExit) as saida, contextlib.redirect_stderr(erro):
                _comum.falhar_fechado(hook, re.compile(r"\bpr\b.*\bready\b"), "", clone_do_forge=True)
            self.assertEqual(saida.exception.code, 2)
            self.assertIn("erro interno do hook parecer", erro.getvalue())

    def test_suite_do_forge_e_pesada(self):
        # TA-2: no clone do Forge a suíte completa é pesada; em projeto, só o que a config lista.
        sys.path.insert(0, str(HOOKS))
        import _comum
        import pesado
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        clone, projeto = tmp / "Forge", tmp / "proj"
        for pasta in (clone, projeto):
            (pasta / ".claude-plugin").mkdir(parents=True)
            (pasta / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
            git("init", "-q", "-b", "develop", cwd=pasta)
        (projeto / ".forge").mkdir()
        (projeto / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        suite = "python3 -m unittest discover -s tests -q"
        hook = _comum.Hook("pesado")
        raiz = hook.projeto(clone, clone_do_forge=True)
        self.assertEqual(raiz, clone)
        self.assertTrue(pesado.pesado(suite, pesado.pesados_da_raiz(hook, raiz)))
        self.assertTrue(pesado.pesado("cd tests && PYTHONPATH=. python -m unittest discover", pesado.pesados_da_raiz(hook, raiz)))
        self.assertFalse(pesado.pesado("python3 -m unittest tests.test_forge", pesado.pesados_da_raiz(hook, raiz)))
        self.assertFalse(pesado.pesado("echo python3 -m unittest discover", pesado.pesados_da_raiz(hook, raiz)))
        # D4: a suíte dividida em processos (o que o pre-push e o CI chamam) também é a suíte inteira
        for comando in ("python3 scripts/suite-paralela.py", "python scripts/suite-paralela.py",
                        "scripts/suite-paralela.py", "./scripts/suite-paralela.py",
                        "FORGE_SUITE_PROCS=2 python3 scripts/suite-paralela.py 2>&1 | tail -1",
                        ".githooks/pre-push --suite"):
            with self.subTest(comando=comando):
                self.assertTrue(pesado.pesado(comando, pesado.pesados_da_raiz(hook, raiz)))
        self.assertFalse(pesado.pesado("cat scripts/suite-paralela.py", pesado.pesados_da_raiz(hook, raiz)))
        hook = _comum.Hook("pesado")
        raiz = hook.projeto(projeto, clone_do_forge=True)
        self.assertEqual(raiz, projeto)
        self.assertFalse(pesado.pesado(suite, pesado.pesados_da_raiz(hook, raiz)))  # projeto: só o que a config lista
        self.assertFalse(pesado.pesado("python3 scripts/suite-paralela.py", pesado.pesados_da_raiz(hook, raiz)))

    def test_entrada_invalida_libera(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for hook in ("agentes", "conformidade", "parecer", "pesado", "quadro", "vigia"):
            for entrada in ("", "não é json", "[1, 2]"):
                with self.subTest(hook=hook, entrada=entrada):
                    r = subprocess.run([sys.executable, str(HOOKS / f"{hook}.py")], input=entrada, cwd=tmp,
                                       env=ambiente_limpo(), capture_output=True, text=True, timeout=30)
                    self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_politica_de_conformidade_malformada_bloqueia(self):
        """Entrada de `caminhos` sem chave ou com tipo errado: falha fechado (saída 2), não libera com KeyError."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        malformadas = {"sem motivo": {"caminho": ".github/", "quem": []},
                       "branch não texto": {"caminho": ".github/", "quem": [], "motivo": "m", "branch": 7},
                       "quem não lista": {"caminho": ".github/", "quem": "jarvis", "motivo": "m"},
                       "so_forge não booleano": {"caminho": ".github/", "quem": [], "motivo": "m", "so_forge": "s"},
                       "entrada não objeto": "docs/"}
        for nome, entrada in malformadas.items():
            with self.subTest(nome):
                tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                shutil.copytree(HOOKS, tmp / "plugin" / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
                politica = dict(base, caminhos=[entrada, *base["caminhos"]])
                (tmp / "plugin" / "hooks" / "conformidade.json").write_text(json.dumps(politica), encoding="utf-8")
                raiz = tmp / "proj"
                (raiz / ".forge").mkdir(parents=True)
                (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
                git("init", "-q", "-b", "develop", cwd=raiz)
                entrada_hook = {"tool_name": "Write", "tool_input": {"file_path": str(raiz / ".github/workflows/ci.yml")},
                                "agent_type": "forge:dev", "hook_event_name": "PreToolUse", "cwd": str(raiz)}
                env = ambiente_limpo()
                env.pop("FORGE_GUARDA_ABERTA", None)
                r = subprocess.run([sys.executable, str(tmp / "plugin" / "hooks" / "conformidade.py")],
                                   input=json.dumps(entrada_hook), cwd=raiz, env=env, capture_output=True, text=True,
                                   timeout=30)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("política de conformidade inválida", r.stderr)

    def test_aq_grava_so_nas_duas_pastas_do_clone_de_contribuicao(self):
        """FC-AQ-HOOK (ADR 0009, seção 6): o aq escreve em `~/.forge-contrib/docs/propostas/` e `.../arquitetura/` e em mais
        nenhuma pasta do clone; travessia (`..`) e link simbólico para fora são recusados."""
        casos = {
            "propostas": ("~/.forge-contrib/docs/propostas/x.md", 0, None, {}),
            "arquitetura": ("~/.forge-contrib/docs/arquitetura/x.md", 0, None, {}),
            "pedidos": ("~/.forge-contrib/docs/pedidos/x.md", 2, "R-", {}),
            "quadro": ("~/.forge-contrib/KANBAN.md", 2, "o papel aq escreve só em", {}),
            "outra pasta de docs": ("~/.forge-contrib/docs/reviews/x.md", 2, "o papel aq escreve só em", {}),
            "fora do clone": ("~/outra/docs/propostas/x.md", 2, "o papel aq escreve só em", {}),
            "travessia": ("~/.forge-contrib/docs/propostas/../pedidos/x.md", 2, "R-", {}),
            "link para fora": ("~/.forge-contrib/docs/propostas/x.md", 2, "o papel aq escreve só em",
                               {"links": {"../home/.forge-contrib/docs/propostas": "{tmp}/fora"}}),
            # Regressões da recomendação do parecer de segurança (docs/security/fc-aq-hook.md): a comparação é sensível à caixa,
            # `~/.forge-contrib` apontando para fora do home some da forma `home` e `.git/` dentro da pasta liberada é protegido.
            "maiúsculas no caminho": ("~/.forge-contrib/docs/Propostas/x.md", 2, "o papel aq escreve só em", {}),
            "maiúsculas na raiz do clone": ("~/.Forge-Contrib/docs/propostas/x.md", 2, "o papel aq escreve só em", {}),
            "clone como link para fora do home": ("~/.forge-contrib/docs/propostas/x.md", 2, "o papel aq escreve só em",
                                                  {"links": {"../home/.forge-contrib": "{tmp}/fora"}}),
            ".git aninhado em propostas": ("~/.forge-contrib/docs/propostas/e/.git/config", 2, ".git", {}),
        }
        for nome, (caminho, codigo, trecho, extra) in casos.items():
            with self.subTest(nome):
                esperado = {"codigo": codigo}
                if trecho:
                    esperado["stderr"] = trecho
                self.rodar_dados({"arquivos": {"src/app.js": "v1\n"}, "env": {"HOME": "{tmp}/home"}, **extra,
                                  "entrada": {"tool_name": "Write", "tool_input": {"file_path": caminho.replace("~", "{tmp}/home")},
                                              "agent_type": "forge-dev:aq", "hook_event_name": "PreToolUse",
                                              "tool_use_id": "toolu_9"}, "esperado": esperado})

    def test_escrita_permitida_malformada_bloqueia(self):
        """ADR 0009, seção 6.6: `escrita_permitida` com forma errada (ou lista vazia) falha fechado, não libera."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        for nome, valor in {"não objeto": ["docs/"], "papel sem lista": {"aq": "docs/propostas/"},
                            "lista vazia": {"aq": []}, "item não texto": {"aq": [7]}}.items():
            with self.subTest(nome):
                r = self.rodar_com_politica(dict(base, escrita_permitida=valor), "ls", "forge-dev:aq")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("política de conformidade inválida", r.stderr)

    def test_erro_interno_com_lista_de_permissao_falha_fechado(self):
        """ADR 0009, seções 6.6 e 7: erro interno na decisão do papel com `escrita_permitida` barra (o caminho não
        tem marcador crítico, e sem isso o hook liberaria). Outro papel segue a regra geral (libera)."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        raiz = tmp / "proj"
        (raiz / ".forge").mkdir(parents=True)
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=raiz)
        ilegivel = raiz / "docs" / "propostas" / "ilegivel"  # `exists()` em pasta sem permissão levanta PermissionError
        (ilegivel / "sub").mkdir(parents=True)
        ilegivel.chmod(0)
        self.addCleanup(ilegivel.chmod, 0o755)
        if os.access(ilegivel / "sub", os.X_OK):
            self.skipTest("o processo ignora permissões de pasta (root)")
        env = ambiente_limpo()
        env.pop("FORGE_GUARDA_ABERTA", None)
        env["PYTHONPATH"] = str(PATHLIB_312)  # o PermissionError de exists() em toda versão do Python (a 3.14 o engole)
        for papel, esperado in {"forge-dev:aq": 2, "forge:dev": 0}.items():
            with self.subTest(papel):
                entrada = {"tool_name": "Write", "tool_input": {"file_path": str(ilegivel / "sub" / "x.md")},
                           "agent_type": papel, "hook_event_name": "PreToolUse", "cwd": str(raiz)}
                r = subprocess.run([sys.executable, str(HOOKS / "conformidade.py")], input=json.dumps(entrada), cwd=raiz,
                                   env=env, capture_output=True, text=True, timeout=30)
                self.assertEqual(r.returncode, esperado, r.stderr)
                if esperado:
                    self.assertIn("erro interno do hook conformidade para o papel aq", r.stderr)

    def rodar_com_politica(self, politica, comando, agent_type):
        """Roda o hook sobre uma cópia do plugin com a política dada; devolve o processo."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(HOOKS, tmp / "plugin" / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        (tmp / "plugin" / "hooks" / "conformidade.json").write_text(json.dumps(politica), encoding="utf-8")
        raiz = tmp / "proj"
        (raiz / ".forge").mkdir(parents=True)
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=raiz)
        entrada_hook = {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": agent_type,
                        "hook_event_name": "PreToolUse", "cwd": str(raiz)}
        env = ambiente_limpo()
        env.pop("FORGE_GUARDA_ABERTA", None)
        return subprocess.run([sys.executable, str(tmp / "plugin" / "hooks" / "conformidade.py")],
                              input=json.dumps(entrada_hook), cwd=raiz, env=env, capture_output=True, text=True,
                              timeout=30)

    def test_politica_com_chave_de_topo_malformada_bloqueia(self):
        """Qualquer chave de topo ausente ou com tipo errado: falha fechado (saída 2), nunca libera."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        sem = lambda chave: {k: v for k, v in base.items() if k != chave}
        npm_sem_congelados = {"npm": {"adicionam": ["install"]}}
        malformadas = {
            "papeis em lista": dict(base, papeis=["forge:qa-engineer"]),
            "papeis sem lista de tipos": dict(base, papeis={"qa": "forge:qa-engineer"}),
            "papeis ausente": sem("papeis"),
            "sem_agent_type não texto": dict(base, sem_agent_type=None),
            "sem_agent_type ausente": sem("sem_agent_type"),
            "papel_padrao não texto": dict(base, papel_padrao=3),
            "papel_padrao ausente": sem("papel_padrao"),
            "acoes em lista": dict(base, acoes=["dev"]),
            "acoes com valor não lista": dict(base, acoes={"instalar_pacote": "dev"}),
            "acoes ausente": sem("acoes"),
            "acoes sem ação conhecida": dict(base, acoes={}),
            "pacotes ausente": sem("pacotes"),
            "pacotes em lista": dict(base, pacotes=["npm"]),
            "pacotes: npm sem congelados": dict(base, pacotes=npm_sem_congelados),
            "pacotes: adicionam não lista": dict(base, pacotes={"npm": {"adicionam": "install", "congelados": []}}),
            "pacotes: flags_congeladas não lista": dict(
                base, pacotes={"npm": {"adicionam": [], "congelados": [], "flags_congeladas": None}}),
            "pacotes: so_arquivo não lista": dict(
                base, pacotes={"npm": {"adicionam": [], "congelados": [], "so_arquivo": "-r"}}),
            "flags_congeladas null": dict(base, flags_congeladas=None),
            "flags_congeladas ausente": sem("flags_congeladas"),
            "caminhos ausente": sem("caminhos"),
            "so_leitura em lista": dict(base, so_leitura=["conferente"]),
            "so_leitura sem comandos": dict(base, so_leitura={"papeis": ["conferente"], "saidas": []}),
            "so_leitura: saidas não lista": dict(base, so_leitura=dict(base["so_leitura"], saidas="/dev/null")),
        }
        for nome, politica in malformadas.items():
            with self.subTest(nome):
                r = self.rodar_com_politica(politica, "echo oi", "forge:dev")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("política de conformidade inválida", r.stderr)

    def test_qa_nao_instala_pacote_com_pacotes_malformado(self):
        """O furo do review: com `pacotes` malformado o `qa` rodava `npm install x`; agora o hook bloqueia."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        politica = dict(base, pacotes={"npm": {"adicionam": ["install"]}})
        r = self.rodar_com_politica(politica, "npm install x", "forge:qa-engineer")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("política de conformidade inválida", r.stderr)

    def test_politica_vigente_passa_na_validacao(self):
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        r = self.rodar_com_politica(base, "echo oi", "forge:dev")
        self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_varredura_do_vigia_nao_desce_em_pastas_ignoradas(self):
        sys.path.insert(0, str(HOOKS))
        import vigia
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        raiz = tmp / "proj"
        (raiz / ".git").mkdir(parents=True)
        (raiz / ".forge").mkdir()
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        (raiz / ".claude").mkdir()
        (raiz / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
        (raiz / ".gitignore").write_text(".forge/run/\n.claude/worktrees/\n", encoding="utf-8")
        for i in range(60):  # 6000 arquivos numa worktree do Claude Code, com node_modules
            pasta = raiz / ".claude" / "worktrees" / f"w{i % 3}" / "node_modules" / f"p{i}"
            pasta.mkdir(parents=True)
            for j in range(100):
                (pasta / f"f{j}.js").write_text("x", encoding="utf-8")
        visitadas = []
        original = os.walk

        def espiao(*a, **k):
            for pasta, dirs, nomes in original(*a, **k):
                visitadas.append(pasta)
                yield pasta, dirs, nomes
        vigia.os.walk = espiao
        try:
            self.assertEqual(sorted(vigia.hashes(raiz)), [".claude/settings.json", ".forge/versao"])
        finally:
            vigia.os.walk = original
        self.assertLess(len(visitadas), 10, "não desce em .claude/worktrees")
        git("init", "-q", "-b", "develop", cwd=raiz)
        git("-c", "user.email=t@example.com", "-c", "user.name=T", "add", "-A", cwd=raiz)
        git("-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-q", "-m", "base", cwd=raiz)
        entrada = {"cwd": str(raiz), "session_id": "s"}
        rodar("vigia", {**entrada, "hook_event_name": "SessionStart", "source": "startup"}, raiz)
        tempos = []
        for _ in range(3):
            t0 = time.perf_counter()
            r = rodar("vigia", {**entrada, "hook_event_name": "Stop"}, raiz)
            tempos.append(time.perf_counter() - t0)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        self.assertLess(sorted(tempos)[1], 1.0, "mediana do Stop com 6000 arquivos em worktrees")

    def test_vigia_estado_e_leitura_do_git_status(self):
        sys.path.insert(0, str(HOOKS))
        import vigia
        self.assertEqual(vigia.caminho_da_linha("R  .githooks/a -> .githooks/b"), ".githooks/b")
        self.assertEqual(vigia.caminho_da_linha('?? ".claude/novo arquivo.md"'), ".claude/novo arquivo.md")
        self.assertEqual(vigia.caminho_da_linha(" M .githooks/pre-push"), ".githooks/pre-push")
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        log = tmp / "violacoes.jsonl"
        log.write_text("x" * (vigia.LIMITE_LOG + 1), encoding="utf-8")
        vigia.rotacionar(log)
        self.assertFalse(log.exists())
        self.assertTrue((tmp / "violacoes.jsonl.1").exists())
        (tmp / "t.jsonl").write_text("", encoding="utf-8")
        agora = time.time()
        estado = {"raizes": {str(tmp): {}, "/nao/existe": {}}, "git": {"/nao/existe": ["x"]},
                  "transcricoes": {str(tmp / "t.jsonl"): 0, "/nao/existe.jsonl": 0},
                  "bloqueios": [{"em": agora}, {"em": agora - 10_000}]}
        vigia.podar(estado, agora, 7200)
        self.assertEqual(list(estado["raizes"]), [str(tmp)])
        self.assertEqual(estado["git"], {})
        self.assertEqual(list(estado["transcricoes"]), [str(tmp / "t.jsonl")])
        self.assertEqual(len(estado["bloqueios"]), 1)

    def test_vv2_politica_libera_so_entrega_e_delta_e_protege_pedidos(self):  # VV-2, A1 e B2
        politica = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        comandos = politica["so_leitura"]["comandos"]
        self.assertIn("forge-check entrega", comandos)
        self.assertIn("forge-check delta", comandos)
        self.assertEqual([c for c in comandos if c.startswith("forge-check")],
                         ["forge-check pr", "forge-check docs", "forge-check brief", "forge-check entrega", "forge-check delta"])
        protegidos = {e["caminho"]: e["quem"] for e in politica["caminhos"]}
        for caminho in ("docs/pedidos/", "~/.forge-contrib/docs/pedidos/", "docs/briefs/", "~/.forge-contrib/docs/briefs/"):
            self.assertEqual(protegidos[caminho], ["jarvis"], caminho)

    def test_cerquilha_so_abre_comentario_no_inicio_de_palavra(self):  # HOOK-COMENTARIO-SHLEX
        """Como no bash: `#` colado a uma palavra é parte dela e não esconde o resto da linha; no início de palavra
        (depois de espaço, `;`, `&`, `|` ou quebra de linha), o comentário vai até a quebra de linha, que segue
        separando comandos. Na dúvida (`(`, `)`, redirecionamento, `\r`), a linha é lida por inteiro."""
        sys.path.insert(0, str(HOOKS))
        import _comum

        def palavras(linha):
            return [p for p, _, _ in _comum.comandos(linha) if p]

        casos = {
            "echo a#; git push --force origin main": [["echo", "a#"], ["git", "push", "--force", "origin", "main"]],
            "cat a#&&git push origin main": [["cat", "a#"], ["git", "push", "origin", "main"]],
            "grep x f#; forge sugerir --fila": [["grep", "x", "f#"], ["forge", "sugerir", "--fila"]],
            "ls # nota; git push --force": [["ls"]],
            "ls;#nota; git push": [["ls"]],
            "ls&&#x|y": [["ls"]],
            "# só comentário": [],
            "ls # nota\ngit push --force origin main": [["ls"], ["git", "push", "--force", "origin", "main"]],
            "git commit -m x # don't": [["git", "commit", "-m", "x"]],
            "echo a\\ #b; git push": [["echo", "a #b"], ["git", "push"]],
            "echo \"#\"x; git push": [["echo", "#x"], ["git", "push"]],
            "echo $#; git push": [["echo", "$#"], ["git", "push"]],
            "echo $(echo a)#b; git push": [["echo", "a"], ["echo", "$(…)#b"], ["git", "push"]],
            "echo >#x; git push": [["echo"], ["git", "push"]],
            "echo a\r#b; git push": [["echo", "a", "#b"], ["git", "push"]],
            "((#x)); git push --force origin main": [["#x"], ["git", "push", "--force", "origin", "main"]],
            "[[ a =~ (#b) ]]; git push": [["[[", "a", "=~"], ["#b"], ["]]"], ["git", "push"]],
            "echo $((#x)); git push": [["#x"], ["echo", "$(…)"], ["git", "push"]],
            # Volta 5 (ADR 0013): `${`, crase e `$[` encerram a prova do comentário; o espaço escapado não abre palavra.
            "echo ${x:- #b}; gh repo delete d/p": [["echo", "${x:-", "#b}"], ["gh", "repo", "delete", "d/p"]],
            "echo `echo a #b`; gh repo delete d/p": [["echo", "`echo", "a", "#b`"], ["gh", "repo", "delete", "d/p"]],
            "echo $[1 #x]; gh repo delete d/p": [["echo", "$[1", "#x]"], ["gh", "repo", "delete", "d/p"]],
            "a\\ #b; git push origin main": [["a #b"], ["git", "push", "origin", "main"]],
            "ls # it's ((": [["ls"]],
        }
        for linha, esperado in casos.items():
            with self.subTest(linha=linha):
                self.assertEqual(palavras(linha), esperado)

    def test_cerquilha_nao_abre_comentario_com_aritmetica_ou_regex(self):  # HOOK-COMENTARIO-SHLEX, volta 2
        """Dentro de `((…))` e na regex do `=~` o bash não abre comentário nem no início de palavra: com `((` ou `=~` na
        linha, `fichas` lê o `#` como palavra e a guarda de construção não modelada não para nele; o `#` colado a `)`
        também não para a guarda. Na dúvida, a linha é lida por inteiro."""
        sys.path.insert(0, str(HOOKS))
        import _comum

        for linha in ("((1 #x)); git push --force origin main", "(( 1 #x )); git push --no-verify origin feature/x",
                      "for ((i=0; i<1 #x; i++)); do :; done; git push", "[[ a =~ ( #b) ]]; git push",
                      "[[ a =~ (a|#b) ]]; git push", "echo $(( 1 #x )); git push"):
            with self.subTest(linha=linha):
                self.assertIn(["git", "push"], [p[:2] for p, _, _ in _comum.comandos(linha)])
        for linha in ("echo $(echo a)#b; echo ${X}", "((1 #x)); echo ${X}", "[[ a =~ ( #b) ]]; echo $X",
                      "a\\ #b; git push origin ${B:-main}", "echo $[1 #x]; echo ${X}", "echo `a #b`; echo $X"):
            with self.subTest(linha=linha):
                self.assertIsNotNone(_comum.construcao_nao_modelada(linha))
        # Sem `((` nem `=~`, o comentário de verdade segue valendo.
        self.assertEqual([p for p, _, _ in _comum.comandos("ls # nota $X; git push") if p], [["ls"]])
        self.assertIsNone(_comum.construcao_nao_modelada("ls # nota $X"))

    def test_leituras_piso_da_develop_e_linha_ambigua(self):  # HOOK-COMENTARIO-SHLEX, volta 5 (ADR 0013)
        """I2: com `#` na linha e a leitura antiga (a da develop) diferente, as duas voltam, e a antiga junta o que a
        develop juntava. Comentário que o hook não prova, com aspa ou `\\` que passaria para outra linha: ilegível."""
        sys.path.insert(0, str(HOOKS))
        import _comum

        lidas = _comum.leituras("gh repo # x\ndelete dono/proj --yes")
        self.assertFalse(lidas.ilegivel)
        self.assertEqual([[p for p, _, _ in parte if p] for parte in lidas.partes],
                         [[["gh", "repo"], ["delete", "dono/proj", "--yes"]], [["gh", "repo", "delete", "dono/proj", "--yes"]]])
        self.assertEqual(len(_comum.leituras("ls # nota").partes), 1, "leituras iguais não se repetem")
        self.assertEqual(len(_comum.leituras("git push origin main").partes), 1, "sem #, só a fiel")
        for linha in ("echo ${x} # a\\\ngh repo delete d/p --yes", "echo ${x:- #b} # \"\ngh repo delete d/p\n# \"",
                      "x=$(date) # it's\nls", "gh pr merge x; (true)#'",
                      # volta 6: dentro de crase o comentário acaba na crase, e a aspa dele casaria com outra adiante
                      "x=`#'`; gh repo delete dono/proj --yes # '", "echo `# it's`; gh pr merge x --merge; echo `# it's`",
                      "echo `true # it's`; gh pr merge x --merge; echo `true # it's`",
                      # CRASE-ASPA-HOOK: o corpo da crase com aspa sem par, também com uma crase sem par adiante
                      "x=`'`; gh repo delete d/p --yes; y=`'`", 'x=`"`; gh repo delete d/p --yes; y=`"`',
                      "x=`$'`; gh repo delete d/p --yes; y=`$'`", "x=`'`; gh pr merge x; y=`'`\n`",
                      "echo `echo \\`'\\``; gh pr merge x", "x=`date # it's`"):
            with self.subTest(linha=linha):
                self.assertTrue(_comum.leituras(linha).ilegivel)
        for linha in ("x=`date` # nota", "echo `echo a #b`; ls", "echo `# nota`; ls # fim", "x=`date`", 'echo "`it`"',
                      'git commit -m "fix: `a.py` e `b.py`"', "echo `date +%s`", "`echo", "+%s`"):
            with self.subTest(linha=linha):
                self.assertFalse(_comum.leituras(linha).ilegivel, "crase com comentário sem aspa: lida inteira")
        lidas = _comum.leituras("docker compose up; (true)#'")
        self.assertTrue(lidas.ilegivel)
        self.assertIn(["docker", "compose", "up"], [p for p, _, _ in lidas.partes[0]], "a antiga fecha e fica")

    def test_heredocs_operador_provado(self):  # HEREDOC-FURO-HOOK
        """O `tirar_heredocs` só separa o corpo de um `<<` que a varredura prova ser operador; o `<<` em dúvida com linha
        depois e o corpo que o bash expande (H9) levantam ValueError. Cada linha: o texto e os corpos separados, ou
        None (ilegível)."""
        _comum, _, _ = modulos_dos_hooks()
        L = "gh repo delete d/p --yes"
        casos = {
            f"echo '<<X'\n{L}\nX": [],  # H1
            f"x=$(date) # <<X\n{L}\nX": None,  # H2: `#` que G não prova
            f"x=`# <<X`\n{L}\nX": None,  # H3: dentro de crase
            f'echo "<<X"\n{L}\nX': [],  # H4
            f"echo \\<<X\n{L}\nX": [],  # H5
            f"ls # <<X\n{L}\nX": [],  # H6: comentário provado
            f"echo 'a\n<<X'\n{L}\nX": [],  # H7
            f"echo $((1<<X))\n{L}\nX": None,  # H8
            f"echo ${{x:-<<X}}\n{L}\nX": None,
            f"x=$(case a in a) cat <<X;; esac)\n{L}\nX": None,
            f"cat <<EOF\n$({L})\nEOF": None,  # H9
            f"cat <<EOF\n`{L}`\nEOF": None,  # H9c
            f"cat <<'EOF'\n$({L})\nEOF": ["$(" + L + ")"],  # controle negativo: o bash não roda o corpo literal
            f"cat <<EOF\n\\$(x)\nEOF": ["\\$(x)"],
            "git commit -F - <<'EOF'\nit's\nEOF": ["it's"],
            "gh pr create --body \"$(cat <<'EOF'\na \"b\"\nEOF\n)\"": ['a "b"'],
            "cat <<-'E'\n\tx\n\tE\nls": ["\tx"],
            "cat <<'A' <<'B'\na\nA\nb\nB\nls": ["a", "b"],
            "bash <<'X'\ngit push origin main\nX": ["git push origin main"],
            "cat <<\"E\"OF\nx\nEOF\nls": ["x"],  # delimitador parcialmente entre aspas
            "cat <<E\\OF\nx\nEOF\nls": ["x"],
            "cat <<<x\nls": [],
            "echo $((1<<2))": [],  # dúvida sem linha depois: nada a esconder
            "cat <<'X'\nsem fim": ["sem fim"],
            f"cat <<EOF\n\\\\$({L})\nEOF": None,  # R1: `\\\\$(` é uma barra e um `$(` vivo
            f"cat <<EOF\n$\\\n({L})\nEOF": None,  # R1: `$\\` + quebra junta as linhas
            f"cat <<EOF\n\\\\`{L}`\nEOF": None,  # R1: a crase depois de uma barra escapada
            "cat <<EOF\n\\\\\\$(x)\nEOF": ["\\\\\\$(x)"],  # três barras: uma barra e `\\$` escapado
            f"cat <<X\n X\ncat <<Y\nX\n{L}\nY": [" X\ncat <<Y"],  # R2: ` X` não fecha; o `<<Y` é corpo
            f"cat <<X\nX \ncat <<Y\nX\n{L}\nY": ["X \ncat <<Y"],
            f"cat <<-X\n  X\ncat <<Y\nX\n{L}\nY": ["  X\ncat <<Y"],  # `<<-` só tira tab
            "cat <<-X\n\tcorpo\n\tX\nls": ["\tcorpo"],
            f"cat <<X\na\\\nX\ncat <<Y\nX\n{L}\nY": ["a\\\nX\ncat <<Y"],  # A2: `a\\` + `X` é `aX`, não fecha
            "cat <<X\n\\\nX\nls": [""],  # `\\` + `X` é `X`, e fecha
            "cat <<X\na\\\\\nX\nls": ["a\\\\"],  # `a\\\\`: barra escapada, sem continuação
            "cat <<'X'\na\\\nX\nls": ["a\\"],  # delimitador entre aspas: o bash não junta
            "cat <<-X\n\ta\\\n\tX\nX\nls": ["\ta\\\n\tX"],  # com `<<-`, a linha juntada mantém a tab
        }
        for linha, esperado in casos.items():
            with self.subTest(linha=linha):
                if esperado is None:
                    with self.assertRaises(ValueError):
                        _comum.tirar_heredocs(linha)
                    continue
                resto, corpos = _comum.tirar_heredocs(linha)
                self.assertEqual([corpo for _, corpo in corpos], esperado)
                self.assertNotIn("<<'", resto, "o operador sai com o corpo")
        resto, [(dono, corpo)] = _comum.tirar_heredocs("bash <<'X'\ngit push origin main\nX\nls")
        self.assertEqual((resto.split(), corpo), (["bash", "ls"], "git push origin main"))
        # M2 da volta única: o dono soma os programas do texto fora da lista dos outros (o `ls` da linha seguinte)
        self.assertEqual(set(dono.split()), {"bash", "ls"})

    def test_corpo_de_heredoc_so_lido_pela_lista_positiva(self):  # LOTE-LEITURA-HOOK, A1 de segurança
        """O corpo só fica fora da conferência quando todo comando da linha do dono é um leitor; qualquer outro dono
        (shell, `source`, `.`, `eval`, laço, lançador, alias de `git -c`) faz dele comando."""
        _comum, _, _ = modulos_dos_hooks()
        lidos = ("cat <<'EOF'", "x=$(cat <<'EOF'", "gh pr create --draft --body \"$(cat <<'EOF'",
                 "gh pr create --draft --body-file - <<'EOF'", "git commit -F - <<'EOF'", "git -C d commit -F - <<EOF",
                 "cat <<'EOF' > x 2>&1", "cat <<EOF | tee x", "gh issue create -F - <<EOF")
        executados = ("bash <<'EOF'", "source /dev/stdin <<'EOF'", ". /dev/stdin <<'EOF'", "ksh <<'EOF'",
                      "eval \"$(cat <<'EOF'", "cat <<'EOF' | sh", "done <<'EOF'", "sudo tee x <<'EOF'",
                      "git -c alias.x=!sh x <<'EOF'", "gh x <<'EOF'", "/bin/cat <<'EOF'", "xargs -0 <<'EOF'",
                      "python3 - <<'EOF'", "sort -S 1k --compress-program=sh <<'EOF'",
                      # M4 da volta única: a atribuição antes do dono muda o programa ou o que ele roda
                      "GH_REPO=a/b gh issue create -F - <<EOF", "PATH=/tmp/x cat <<'EOF'")
        for dono in lidos:
            with self.subTest(dono=dono):
                self.assertTrue(_comum.corpo_so_lido(dono))
        for dono in minimo(executados, 10, "donos que rodam o corpo"):
            with self.subTest(dono=dono):
                self.assertFalse(_comum.corpo_so_lido(dono))
        self.assertTrue(_comum.corpo_so_lido("python3 - <<'EOF'", lambda p: p == "python3"), "o `tambem` de quem chama")
        # A1 de segurança, volta 3: o dono é o comando lógico do operador (`comando_logico`), não só a linha física
        # dele; quem roda o corpo pode vir antes, por barra, ou depois do fim, por pipe ou barra.
        L = "gh pr merge feature/x --merge"
        noutra_linha = {f"cat <<'EOF' |\n{L}\nEOF\nbash": "bash", f"bash \\\n<<'EOF'\n{L}\nEOF": "bash",
                        f"while read -r l; do eval \"$l\"; done \\\n<<'EOF'\n{L}\nEOF": "eval",
                        f"cat <<'EOF' | \\\nbash\n{L}\nEOF": "bash", f"cat <<'EOF' &&\n{L}\nEOF\nbash": "bash",
                        f"eval \"$(\ncat <<'EOF'\n{L}\nEOF\n)\"": "eval", f"eval $(echo; cat <<'EOF'\n{L}\nEOF\n)": "eval",
                        f"( source /dev/stdin ) <<'EOF'\n{L}\nEOF": "source", f"cat <<'EOF' | {{ read; bash; }}\n{L}\nEOF": "bash",
                        f"cat > x.sh <<'EOF' && bash x.sh\n{L}\nEOF": "bash",  # como na develop: `bash` no comando lógico
                        f"read -r x <<'EOF' && eval \"$x\"\n{L}\nEOF": "eval",
                        # A1 de segurança, volta 4: outro comando da lista fora da lista positiva roda o arquivo gravado
                        f"cat > x.sh <<'EOF' && chmod +x x.sh && ./x.sh\n{L}\nEOF": "./x.sh",
                        f"cat > x.sh <<'EOF'; ./x.sh\n{L}\nEOF": "./x.sh", f"cat > x.sh <<'EOF' || ./x.sh\n{L}\nEOF": "./x.sh",
                        f"cat > Makefile <<'EOF' && make\n{L}\nEOF": "make", f"cat > x.sh <<'EOF' &&\n{L}\nEOF\n./x.sh": "./x.sh",
                        f"cat > x.sh <<'EOF' && git -c alias.x='!sh x.sh' x\n{L}\nEOF": "git",
                        # A2 de segurança, volta 4: a linha que fecha a substituição aberta no operador é o mesmo comando
                        f"x=$(cat <<'EOF'\n{L}\nEOF\n); eval \"$x\"": "eval", f"x=$(cat <<'EOF'\n{L}\nEOF\n) && $x": "$x",
                        f"x=$(cat <<'EOF' # )\n{L}\nEOF\n); eval \"$x\"": "eval",
                        f"x=$(cat <<'EOF'; : \")\"\n{L}\nEOF\n); eval \"$x\"": "eval",
                        # A1 de segurança, volta 5: opção fora da lista fechada, abreviada, global, ou
                        # atribuição antes, no comando ou num `export` de outro comando do texto
                        f"x=$(cat <<'EOF'\n{L}\nEOF\n) && git push --receive-pack=\"$x\" . HEAD": "git",
                        f"cat > x.sh <<'EOF' && git push --rec='sh x.sh' . HEAD\n{L}\nEOF": "git",
                        f"cat > x.sh <<'EOF' && git --config-env=core.sshCommand=X push ssh://h/r\n{L}\nEOF": "git",
                        f"cat > .gitconfig <<'EOF' && HOME=. git status\n{L}\nEOF": "git",
                        f"cat > x.sh <<'EOF' && GIT_SSH=sh git push ssh://x.sh/r HEAD\n{L}\nEOF": "git",
                        f"export GIT_SSH=sh\ncat > x.sh <<'EOF' && git push ssh://x.sh/r HEAD\n{L}\nEOF": "git",
                        # A2 do review, volta 5: a linha grava arquivo e o git roda ganchos, filtros e configuração
                        f"cat > .husky/pre-push <<'EOF' && git push origin feature/x\n{L}\nEOF": "git",
                        f"cat > .husky/pre-commit <<'EOF' && git commit -m x\n{L}\nEOF": "git",
                        f"cat >> .husky/pre-commit <<'EOF' && git add -A\n{L}\nEOF": "git",
                        f"tee .husky/pre-push <<'EOF' && git push origin feature/x\n{L}\nEOF": "git",
                        f"git apply <<'EOF' && git commit -m x\n{L}\nEOF": "git",
                        f"( cat > .husky/pre-commit <<'EOF' ) && git commit -m x\n{L}\nEOF": "git",
                        # M2 da volta única: o programa de outra linha do texto pode rodar o arquivo gravado
                        f"cat > f <<'EOF'\n{L}\nEOF\nbash f": "bash", f"cat <<'EOF'\n{L}\nEOF\nbash": "bash",
                        f"cat <<'EOF' \\\\\n{L}\nEOF\nsh": "sh",
                        # M5 da volta única: `echo` redefinido no texto não é o builtin da lista dos outros
                        f"echo() {{ ./x.sh; }}\ncat > x.sh <<'EOF'\n{L}\nEOF\necho": "./x.sh",
                        f"alias echo=./x.sh\ncat > x.sh <<'EOF'\n{L}\nEOF\necho": "alias"}
        for linha in minimo(list(noutra_linha), 38, "formas em que o corpo vai a quem o roda"):
            programa = noutra_linha[linha]
            with self.subTest(linha=linha):
                [(dono, corpo)] = _comum.tirar_heredocs(linha)[1]
                self.assertEqual(corpo, L)
                self.assertIn(programa, dono)
                self.assertFalse(_comum.corpo_so_lido(dono))
        separados = (f"git add x && git commit -m \"$(cat <<'EOF'\n{L} it's\nEOF\n)\" && git push origin feature/x",
                     f"git add -A && git commit -m \"$(cat <<'EOF'\n{L}\nEOF\n)\" && git push -u origin feature/x",
                     f"cd sub && cat > n.md <<'EOF'\n{L}\nEOF", f"mkdir -p d && cd d && x=$(cat <<'EOF'\n{L}\nEOF\n)",
                     f"cat <<'EOF' 2>/dev/null && git push -u origin feature/x\n{L}\nEOF",
                     f"cat <<'EOF' 2>&1 && git status --short\n{L}\nEOF",
                     f"git commit -m \"$(cat <<'EOF'\n{L}\nEOF\n)\" && echo feito", f"true && cat <<'EOF'\n{L}\nEOF")
        for linha in separados:  # outro comando da lista não lê o corpo (A1 do review: o comum dos projetos)
            with self.subTest(linha=linha):
                self.assertTrue(_comum.corpo_so_lido(_comum.tirar_heredocs(linha)[1][0][0]))

    def test_comando_logico_le_os_limites_uma_vez_por_texto(self):  # LOTE-LEITURA-HOOK, A1 do review, volta 5
        """O `comando_logico` de cada um dos 2000 heredocs de um texto sai em tempo linear: os limites dos comandos
        lógicos são lidos uma vez por texto, e não do começo a cada operador (26,9 s com 3000 heredocs no conformidade,
        acima do timeout de 10 s em que o Claude Code libera a linha)."""
        _comum, _, _ = modulos_dos_hooks()
        linhas = [f"cat > f{i} <<'EOF'" for i in range(2000)]
        texto = "\n".join(linhas)
        posicoes = [texto.index(linha) for linha in linhas]
        inicio = time.perf_counter()
        logicos = [_comum.comando_logico(texto, p) for p in posicoes]
        self.assertLess(time.perf_counter() - inicio, 1.0, "2000 comandos lógicos do mesmo texto")
        self.assertEqual(logicos, linhas)
        self.assertEqual(_comum.comando_logico("a &&\nb\nc", 5), "a &&\nb")

    def test_tirar_heredocs_em_tempo_linear(self):  # LOTE-LEITURA-HOOK, A1 do review, volta 5
        """Com 2000 heredocs, um por linha, num pipeline, ligados por `&&` ou na mesma linha, `tirar_heredocs` e a
        conferência de cada dono (`corpo_so_lido`) saem dentro do orçamento de 3 s do `conformidade`: o dono de cada
        heredoc sai de índices das leituras (`pipeline_do_operador`) e de limites dos comandos lógicos lidos uma vez por
        texto, e heredocs do mesmo dono o dividem (antes, 12,4 s um por linha e 30 s no pipeline e com `&&`)."""
        _comum, _, _ = modulos_dos_hooks()
        n = 2000
        formas = {"um por linha": "".join(f"cat > f{i} <<'EOF'\nx\nEOF\n" for i in range(n)),
                  "pipeline": "".join(f"cat <<'E{i}' |\nx\nE{i}\n" for i in range(n)) + "cat\n",
                  "&&": " && ".join(f"cat > f{i} <<'E{i}'" for i in range(n)) + "\n" + "".join(f"x\nE{i}\n" for i in range(n)),
                  "mesma linha": "cat " + " ".join(f"<<'E{i}'" for i in range(n)) + "\n" + "".join(f"x\nE{i}\n" for i in range(n))}
        for forma, texto in formas.items():
            with self.subTest(forma=forma):
                inicio = time.perf_counter()
                resto, corpos = _comum.tirar_heredocs(texto + "git push origin main")
                lidos = [_comum.corpo_so_lido(dono) for dono, _ in corpos]
                self.assertLess(time.perf_counter() - inicio, 3.0, f"{n} heredocs")
                self.assertEqual(len(corpos), n)
                self.assertTrue(resto.endswith("git push origin main"))
                # M2 da volta única: com o texto gravando (`cat > f`), o `git` do texto faz de todo corpo comando
                self.assertEqual(set(lidos), {forma in ("pipeline", "mesma linha")})

    def test_muitos_heredocs_recusam_dentro_do_orcamento(self):  # LOTE-LEITURA-HOOK, A1 do review, volta 5
        """Pelo hook real: 3000 heredocs com `git push origin main` no fim recusam (R-MAIN) bem antes do timeout do
        `hooks.json` (26,9 s antes, e o Claude Code libera o comando que o hook não decidiu a tempo)."""
        limite = min(h["timeout"] for g in json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
                     for h in g["hooks"] if h["args"][0].endswith("/conformidade.py"))
        dados = json.loads((FIXTURES / "conformidade" / "heredoc-outro-comando-make-push-main-bloqueia.json")
                           .read_text(encoding="utf-8"))
        n = 3000
        for forma, texto in (("um por linha", "".join(f"cat > f{i} <<'EOF'\nx\nEOF\n" for i in range(n))),
                             ("&&", " && ".join(f"cat > f{i} <<'E{i}'" for i in range(n)) + "\n"
                              + "".join(f"x\nE{i}\n" for i in range(n)))):
            with self.subTest(forma=forma):
                caso = json.loads(json.dumps(dados))
                caso["entrada"]["tool_input"]["command"] = texto + "git push origin main"
                inicio = time.monotonic()
                self.rodar_dados(caso)
                self.assertLess(time.monotonic() - inicio, limite / 2, "a decisão sai bem antes do Claude Code matar o hook")

    def corpus_de_recusas(self):
        """As linhas das fixtures de recusa de Bash (código 2) dos hooks que leem a linha, menos as que o bash não aceita
        (`bash -n`: a variante cairia dentro de uma aspa aberta) e as recusas por erro interno (`erros_log`)."""
        if not _CORPUS:
            todas = [f for f in self.fixtures if f.hook in ("conformidade", "parecer", "pesado")
                     and f.dados["esperado"].get("codigo") == 2 and f.dados["entrada"].get("tool_name") == "Bash"
                     and f.caminho.stem != FIXTURE_DE_ORCAMENTO]  # a linha adversária de tempo recusa pelo teto, não pelo corpus
            fora = [f.caminho.stem for f in todas if "erros_log" in f.dados["esperado"]
                    or not bash_aceita(f.dados["entrada"]["tool_input"]["command"])]
            self.assertLessEqual(len(fora), 8, fora)
            _CORPUS.extend(f.dados["entrada"]["tool_input"]["command"] for f in todas if f.caminho.stem not in fora)
        return minimo(_CORPUS, 500, "linhas de recusa de Bash")

    def test_t1_variantes_que_o_bash_ignora_nao_tiram_comando_da_leitura(self):  # HOOK-COMENTARIO-SHLEX, ADR 0013
        """T1, inclusão no leitor: com qualquer variante que o bash ignora, todo comando da leitura fiel da linha continua
        lido (as palavras dele no começo de um comando da variante, os destinos entre os dela), ou a variante é ilegível
        (e quem confere recusa). Pela composição de teste do `conformidade` (heredoc, palavras relidas, `bash -c`), sem
        subprocesso."""
        _comum, _, _ = modulos_dos_hooks()

        def lidos(linha, todas=True):
            try:
                return ler_como_o_conformidade(linha, todas=todas)
            except Ilegivel:
                return None

        lidas = 0
        for linha in self.corpus_de_recusas():
            base = lidos(linha, todas=False) or []
            for prefixo, sufixo in VARIANTES_QUE_O_BASH_IGNORA:
                if '$(' in prefixo and '"' in prefixo and ('"' in linha or _comum.CASE.search(linha)):
                    # O hook relê a palavra que o `shlex` já tirou das aspas: a aspa dupla da linha fecha a de fora, e o
                    # `)` de um padrão de `case` fecha o `$(` (achado do lote, cartão próprio; o T5 cobre as ações)
                    continue
                if "`" in linha and (prefixo, sufixo) in CRASE_EM_VOLTA:
                    continue  # crase não se aninha sem `\``: em volta de outra, a variante muda o que o bash roda
                variante = prefixo + linha + sufixo
                outra = lidos(variante)
                lidas += 1
                if outra is None:
                    continue
                for palavras, destinos in base:
                    achou = any(p[:len(palavras)] == palavras and set(destinos) <= set(d) for p, d in outra)
                    if not achou:
                        self.fail(f"{variante!r}: some {palavras} {destinos}")
        self.assertGreaterEqual(lidas, 500 * len(VARIANTES_QUE_O_BASH_IGNORA))

    def test_t2_cada_familia_de_recusa_recusa_com_cada_mecanismo(self):  # HOOK-COMENTARIO-SHLEX, ADR 0013
        """T2, ligação leitor → recusa, pelo hook real: uma fixture por família de recusa, com uma variante por mecanismo
        do comentário, sai 2 (qualquer recusa `R-`)."""
        casos = []
        for nome, motivo in FAMILIAS_DE_RECUSA.items():
            caminho = FIXTURES / f"{nome}.json"
            self.assertTrue(caminho.is_file(), f"{nome} ({motivo})")
            for mecanismo, (prefixo, sufixo) in MECANISMOS_DO_COMENTARIO.items():
                if (nome, mecanismo) in FORA_DO_T2:
                    continue
                f = Fixture(caminho)
                self.assertEqual(f.dados["esperado"]["codigo"], 2, nome)
                f.dados["entrada"]["tool_input"]["command"] = prefixo + f.dados["entrada"]["tool_input"]["command"] + sufixo
                f.dados["esperado"] = {"codigo": 2, "stderr": "R-"}
                casos.append((f"{nome} + {mecanismo}", f))
        self.assertEqual(len(casos), len(FAMILIAS_DE_RECUSA) * len(MECANISMOS_DO_COMENTARIO) - len(FORA_DO_T2))
        self.assertEqual(self.executar_em_lote(casos), len(casos))

    def test_t3_todo_comentario_marcado_e_comentario_para_o_bash(self):  # HOOK-COMENTARIO-SHLEX, ADR 0013
        """T3, oráculo do bash para a gramática G: em cada posição que `comentarios` marca, troca o texto do comentário
        por aspas e crase sem par; se o bash não lesse ali um comentário, a linha deixaria de ser aceita (`bash -n`).
        Fora de G (modelos com a construção antes do `#`), nada é marcado; os modelos de G marcam ao menos um `#`."""
        sys.path.insert(0, str(HOOKS))
        import _comum

        carga = "'\"`"
        conferidas = 0
        recusados = [m for m in MODELOS_FORA_DE_G + MODELOS_EM_G if not bash_aceita(m)]
        self.assertLessEqual(len(recusados), 4, recusados)
        for modelo in MODELOS_FORA_DE_G:
            with self.subTest(fora_de_g=modelo):
                self.assertEqual(_comum.comentarios(modelo), frozenset())
        for modelo in MODELOS_EM_G:
            with self.subTest(em_g=modelo):
                self.assertTrue(_comum.comentarios(modelo), "o comentário de verdade continua comentário")
        for linha in tuple(self.corpus_de_recusas()) + MODELOS_EM_G:
            if linha in recusados:
                continue
            for p in sorted(_comum.comentarios(linha)):
                fim = linha.find("\n", p)
                trocada = linha[:p + 1] + carga + (linha[fim:] if fim >= 0 else "")
                conferidas += 1
                with self.subTest(linha=linha, posicao=p):
                    self.assertTrue(bash_aceita(trocada), f"o bash não lê comentário em {p}: {trocada!r}")
        self.assertGreaterEqual(conferidas, len(MODELOS_EM_G))

    def test_t4_nenhum_hook_le_a_linha_fora_de_leituras(self):  # HOOK-COMENTARIO-SHLEX, ADR 0013
        """T4, estrutural: os hooks leem a linha só por `leituras` (`_comum.py`); `comandos` só é chamada por ela e
        `fichas`, só por `comandos`. `segmentos`, que lia por fora, não existe mais."""
        import ast
        permitidas = {"comandos": {"leituras"}, "fichas": {"comandos"}, "segmentos": set()}
        arquivos = minimo(sorted(HOOKS.glob("*.py")), 8, "scripts de hook")
        achadas = []
        for arquivo in arquivos:
            for topo in ast.parse(arquivo.read_text(encoding="utf-8")).body:
                dono = topo.name if isinstance(topo, (ast.FunctionDef, ast.ClassDef)) else "<módulo>"
                for no in ast.walk(topo):
                    nome = (no.id if isinstance(no, ast.Name) else no.attr if isinstance(no, ast.Attribute)
                            else no.name if isinstance(no, ast.alias) else None)
                    if nome in permitidas:
                        achadas.append((arquivo.name, dono, nome))
                        with self.subTest(arquivo=arquivo.name, dono=dono, nome=nome):
                            self.assertTrue(arquivo.name == "_comum.py" and dono in permitidas[nome],
                                            f"{arquivo.name}: {dono} usa {nome}")
        # O alvo do teste de ausência ainda existe: as duas chamadas permitidas estão lá.
        self.assertIn(("_comum.py", "leituras", "comandos"), achadas)
        self.assertIn(("_comum.py", "comandos", "fichas"), achadas)

    def test_t5_guarda_do_corpus_do_oraculo(self):  # FICHAS-CORPUS-BASH (modelo de ameaças do lote, 4.2 e 4.3)
        """Antes do T5: nenhuma ação nem variante tem o que o oráculo não pode rodar, e a guarda pega cada forma proibida."""
        proibidas = ("kill -9 -1", "trap 'x' EXIT", "ulimit -n 1", "umask 0", "ls; disown", "exec ls", "eval ls",
                     "source x", ". x", "enable -n echo", "hash -p x ls", "command -p ls", "builtin cd", "/bin/true",
                     "./x", "x=/bin/true; $x", "cat </dev/tcp/h/80", "echo a > f", "ls 2>e", "ls &>e", "sleep 1 &",
                     "echo `kill 1`", "(exec ls)")
        for linha in proibidas:
            with self.subTest(proibida=linha):
                self.assertTrue(PROIBIDO_NO_ORACULO.search(linha), linha)
        for linha in ("rm -rf .githooks", "gh pr merge a --repo dono/proj", "true && ls || ls", "echo a.b"):
            with self.subTest(permitida=linha):
                self.assertIsNone(PROIBIDO_NO_ORACULO.search(linha))
        for acao in ACOES_DO_CORPUS:
            for prefixo, sufixo in VARIANTES_QUE_O_BASH_IGNORA:
                with self.subTest(variante=prefixo + acao + sufixo):
                    self.assertIsNone(PROIBIDO_NO_ORACULO.search(prefixo + acao + sufixo))
        # ADR 0013: o que prova início de palavra está contido no que gera dúvida (a "constante única" do cartão)
        _comum, _, _ = modulos_dos_hooks()
        self.assertLessEqual(_comum.SEPARADORES_DE_G, _comum.ANTES_DE_CANDIDATO)

    def test_t5_o_que_o_bash_roda_esta_no_que_o_hook_le(self):  # FICHAS-CORPUS-BASH
        """T5, oráculo do bash: para cada ação do corpus e cada variante, (1) o bash roda a ação, com todas as palavras
        (senão a variante está errada); (2) a composição de teste do `conformidade`, e a do `parecer` para as ações
        dele, dá ilegível ou lê a ação. É a leitura que conta, não a saída do hook: a recusa pela rede da ADR 0011
        (`construcao_nao_modelada`, só com marcador crítico) não prova que a ação foi lida. O `pesado` não lê a crase
        (ADR 0013, tabela 2.4) e fica de fora da afirmação 2."""
        bash, motivo = bash_do_oraculo()
        if bash is None:
            if os.environ.get("CI"):
                self.fail(f"o CI tem bash 5: {motivo}")
            self.skipTest(motivo)
        # Controles do oráculo: registra o comando externo, também dentro de `$(…)`, e não o corpo literal de heredoc.
        self.assertEqual(rodado_pelo_bash(bash, "x=$(gh a 'b c')"), ["gh a b c"])
        self.assertEqual(rodado_pelo_bash(bash, "cat <<'EOF'\n$(gh a)\nEOF"), ["cat"])
        casos = [(acao, prefixo + acao + sufixo) for acao in ACOES_DO_CORPUS
                 for prefixo, sufixo in VARIANTES_QUE_O_BASH_IGNORA]
        for _, variante in casos:
            self.assertIsNone(PROIBIDO_NO_ORACULO.search(variante), variante)
        inicio = time.monotonic()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            rodados = list(pool.map(lambda caso: rodado_pelo_bash(bash, caso[1]), casos))
        duracao = time.monotonic() - inicio
        for (acao, variante), rodou in zip(casos, rodados):
            palavras = shlex.split(acao)
            with self.subTest(variante=variante):
                self.assertIn(" ".join(palavras), rodou, "o bash não roda a ação: a variante não serve ao corpus")
                hooks = ["conformidade"] + ([ACOES_DO_CORPUS[acao]] if ACOES_DO_CORPUS[acao] == "parecer" else [])
                for hook in hooks:
                    self.assertTrue(le_a_acao(COMPOSICOES[hook], variante, palavras),
                                    f"o bash roda {acao!r} e a leitura do {hook} não a vê")
        self.assertGreaterEqual(len(casos), len(ACOES_DO_CORPUS) * len(VARIANTES_QUE_O_BASH_IGNORA))
        self.assertLess(duracao, 60, f"oráculo lento: {duracao:.1f} s para {len(casos)} execuções")



# LOTE-LEITURA-HOOK, volta única (docs/propostas/lote-leitura-hook-volta-unica.md, seções 3 a 5): o corpus das classes
# R, N, S, H, V, L e F nos dois hooks, o oráculo das redireções (T6) e o enumerador de programas (T7). A marca `fecha`
# de um caso é a regra (M1 a M5) em cujo commit ele passa a dar o resultado esperado: até lá o teste exige o resultado
# errado (o vermelho continua provado) e falha se a marca sobra. A classe X do desenho fica fora (cartão N-HOOK1).
CORPUS_VOLTA_UNICA = Path(__file__).resolve().parent / "fixtures" / "heredoc-volta-unica.json"
REGRAS_DA_VOLTA_UNICA = frozenset({"M1", "M2", "M3", "M4", "M5", "D", "A", "B", "B2", "C", "T"})  # D, A, B e B2: as opções (RET-LEITURA-HOOK-D, -A, -B, -C); C e T: a opção C e o bloco T da revalidação 10 (RET-LEITURA-HOOK-E)
EXIGE_NENHUMA_MARCA = True  # passo (7) do desenho e opções D, A, B e B2: todas as regras entraram, nenhuma marca `fecha` sobra
# A marca `nao_promete` (o cartão): a forma está na linha "Não promete" da frase de parada (RET-LEITURA-HOOK-CAMINHO4); a
# célula é o código de hoje, para o conserto futuro aparecer como mudança de teste, e o T9b registra que o bash a roda.
CARTOES_DO_NAO_PROMETE = frozenset({"N-HOOK1", "R5A-COPROC", "A6"})
NAO_PROMETE = "não promete"
MINIMO_POR_CLASSE = {"R": 32, "N": 12, "S": 34, "H": 8, "V": 13, "L": 12, "F": 12}
IDS_DA_VOLTA_UNICA = ("R8", "R9", "R18", "R19a", "R19b", "R19c", "R19d", "R19e", "R20a", "R20b", "R20c", "S5", "S15",
                      "S17a", "S17b", "S17c", "S17d", "S17e", "S17f", "S18a", "S18b", "S18c", "F7a", "F7b", "F8a", "F8b",
                      # opção A (RET-LEITURA-HOOK-A): as sondas da revalidação 7 e os falsos positivos medidos
                      "G1", "G2", "G3", "G3c", "G3d", "G4", "G5", "G6", "G7", "G8", "GL1", "GL2", "GL3", "GL4", "GL5",
                      "GL6", "B1", "B2", "BL1", "HC1", "HC2", "HC3", "HC4", "HC5", "FD9", "FD9b", "FD10", "FD10b", "FD11",
                      "FD11b",
                      # opção B (RET-LEITURA-HOOK-B): as sondas da revalidação 8 e os falsos positivos FD12 e FD13
                      "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "QC1", "QC2", "BL2", "FD12", "FD12b", "FD13a", "FD13b", "FD13c",
                      "FD13d", "FD13e", "QP1",
                      # opção B da revalidação 9 (RET-LEITURA-HOOK-C): as sondas CO, AN, NR, VA, o FD14 e o "não promete"
                      "CO1", "CO2", "CO3", "AN1", "AN2", "AN3", "AN4", "AN5", "NR1", "NR2", "NR3", "VA1", "FD14a",
                      "FD14b", "FD14c", "FD14d", "CO4", "CO5", "CN1", "CN2", "CN3", "VA2", "PE1", "ST1", "ST2", "ST3",
                      # opção C e bloco T da revalidação 10 (RET-LEITURA-HOOK-E): `\x{…}`, `$"…"`, 20 mil palavras e o FD15
                      "AN34", "AN34b", "AN34c", "AN34d", "AN34e", "AN34f", "AN34g", "AN35a", "AN35b", "AN35c", "AN35d",
                      "OT1", "OT2", "FD15a", "FD15b", "FD15c", "FD15d", "FD15e", "FD15f", "FD15g", "FD15h", "FD15i",
                      # A1 da segurança na revalidação 11 (RET-LEITURA-HOOK-E): o lançador que divide texto (`env -S`)
                      *(f"ES{k}" for k in range(1, 18)), "FD16a", "FD16b", "FD16c", "FD16d")


def corpus_da_volta_unica():
    """O corpus, com `{REPETE:<texto>:<n>}` no `comando` trocado pelo texto repetido n vezes (a sonda de 20 mil
    palavras não cabe escrita no JSON)."""
    texto = re.sub(r"\{REPETE:([^:}]+):(\d+)\}", lambda m: m.group(1) * int(m.group(2)),
                   CORPUS_VOLTA_UNICA.read_text(encoding="utf-8"))
    return json.loads(texto)


class CorpusHeredocVoltaUnica(unittest.TestCase):
    """Os casos de `tests/fixtures/heredoc-volta-unica.json`, cada um no modelo de fixture do hook (`modelos`), com
    `{CORPO}` trocado pela linha crítica dele (`corpos`). Em cada caso, o código esperado por hook (`null`: a célula não
    roda) e a marca `fecha`: a regra, ou `{hook: regra}` quando o outro hook já dá o esperado (pelo item 2 da ADR 0011,
    por exemplo). `passos` são chamadas anteriores do Bash, a última é a principal."""
    executar_em_lote = Hooks.executar_em_lote
    _pasta_temporaria = Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(Hooks.depende_de_pid_ou_trava)

    def conferir_marca(self, fecha, passou, saida):
        """Sem marca, o caso tem de passar; com marca, tem de falhar (a regra da marca ainda não entrou)."""
        if fecha:
            self.assertIn(fecha, REGRAS_DA_VOLTA_UNICA)
            self.assertFalse(passou, f"marca sobrando: o caso já passa; tire a marca {fecha} neste commit ({saida})")
        else:
            self.assertTrue(passou, saida)

    def executar_fixture(self, f, tmp, outro_pid):
        raiz, entrada = f.montar(tmp, outro_pid)
        proc = montar_proc(tmp, None)
        extra = {"FORGE_NPROC": "8"}
        f.executar_passos(raiz, lambda e: rodar(f.hook, e, raiz, proc, extra))
        r = rodar(f.hook, entrada, raiz, proc, extra, como_o_claude_code=bool(f.dados.get("prazo_de_producao")))
        codigo = f.dados["esperado"]["codigo"]
        if codigo == 0:
            passou = r.returncode == 0 and r.stderr == ""
        else:
            passou = r.returncode == codigo and re.match(r"^R-[A-Z]+: ", r.stderr) is not None
        self.conferir_marca(f.dados.get("fecha"), passou, f"código {r.returncode}: {r.stderr.strip()}")

    def fixtures_do_corpus(self):
        dados = corpus_da_volta_unica()
        fixtures = []
        for caso in dados["casos"]:
            for hook, modelo in dados["modelos"].items():
                if caso[hook] is None:
                    continue
                caminho = FIXTURES / hook / f"{modelo}.json"
                base = json.loads(caminho.read_text(encoding="utf-8"))
                comandos = [c.replace("{CORPO}", dados["corpos"][hook]) for c in caso.get("passos", [caso.get("comando")])]

                def entrada(comando):
                    e = json.loads(json.dumps(base["entrada"]))
                    e["tool_input"]["command"] = comando
                    return e

                base["passos"] = [{"entrada": entrada(c)} for c in comandos[:-1]]
                base["entrada"] = entrada(comandos[-1])
                base["esperado"] = {"codigo": caso[hook]}
                if caso.get("prazo_de_producao"):  # a decisão tem de vir antes do timeout do Claude Code (bloco T)
                    base["prazo_de_producao"] = True
                fecha = caso.get("fecha")  # a regra, ou {hook: regra} quando só um dos hooks ainda falha
                fecha = fecha.get(hook) if isinstance(fecha, dict) else fecha
                if fecha:
                    base["fecha"] = fecha
                fixtures.append((f"{hook}/{caso['id']}", Fixture(caminho, base)))
        return fixtures

    def test_corpus_nos_dois_hooks(self):
        inicio = time.monotonic()
        casos = self.fixtures_do_corpus()
        self.assertEqual(self.executar_em_lote(casos), len(casos))
        self.assertLess(time.monotonic() - inicio, 60, "o corpus roda em paralelo, como os fixtures")

    def test_oraculo_das_redirecoes(self):  # T6
        """Para cada redireção das classes R e N e cada prefixo (P0 a P4), o bash roda `<P>cat <redireção> <<'EOF'⏎x⏎EOF`
        numa pasta vazia; se ele criou ou mudou um arquivo ali, `grava_arquivo` dá verdadeiro, e para a classe N, com
        todo prefixo, falso. Só roda `cat` e `echo`, sem rede (R-CUSTO)."""
        bash = shutil.which("bash")
        versao = None
        if bash:
            r = subprocess.run([bash, "--noprofile", "--norc", "-c", 'echo "${BASH_VERSINFO[0]}"'], capture_output=True,
                               text=True, env={"PATH": "/usr/bin:/bin"}, stdin=subprocess.DEVNULL, timeout=5)
            versao = r.stdout.strip()
        if not bash or not (versao or "").isdigit() or int(versao) < 4:
            self.skipTest(f"bash ausente ou anterior ao 4 (BASH_VERSINFO={versao}): {{fd}}> e &>> não existem")
        _comum, _, _ = modulos_dos_hooks()
        oraculo = corpus_da_volta_unica()["oraculo"]
        for redirecao in oraculo["redirecoes"]:
            for nome, prefixo in oraculo["prefixos"].items():
                texto = f"{prefixo}cat {redirecao['op']} <<'EOF'\nx\nEOF"
                with self.subTest(texto=texto), tempfile.TemporaryDirectory(prefix="forge-redirecao-") as tmp:
                    subprocess.run([bash, "--noprofile", "--norc", "-c", texto], cwd=tmp, env={"PATH": "/usr/bin:/bin"},
                                   stdin=subprocess.DEVNULL, capture_output=True, timeout=5)
                    gravou = any(Path(tmp).iterdir())
                    resto, _ = _comum.tirar_heredocs(texto)
                    grava = _comum.grava_arquivo(resto)
                    passou = (grava or not gravou) and (redirecao["classe"] != "N" or not grava)
                    self.conferir_marca(redirecao.get("fecha", {}).get(nome), passou,
                                        f"bash gravou: {gravou}; grava_arquivo: {grava}")
        self.assertGreaterEqual(len(oraculo["redirecoes"]), 28)

    def test_enumerador_nao_engole_programa(self):  # T7
        """A redireção completa (operador e alvo colado) não consome a palavra seguinte, nem depois de atribuição ou de
        `!`; o operador que pede alvo separado consome só o alvo."""
        _comum, _, _ = modulos_dos_hooks()
        enumerador = corpus_da_volta_unica()["enumerador"]
        casos = [(item, forma, f"{forma}{item['op']} ./x.sh", "./x.sh", None)
                 for item in enumerador["completos"] for forma in enumerador["formas"]]
        casos += [(item, "", f"{item['op']} alvo ./x.sh", "./x.sh", "alvo") for item in enumerador["pedem_alvo"]]
        for item, forma, texto, programa, alvo in casos:
            with self.subTest(texto=texto):
                programas = [p for p, _, _ in _comum.programas_e_atribuicoes(texto)]
                passou = programa in programas and alvo not in programas
                self.conferir_marca(item.get("fecha", {}).get(forma), passou, f"programas: {programas}")
        self.assertGreaterEqual(len(casos), 70)

    # T8 e T9 (opções D e A): as zonas do texto saem de uma varredura própria, sem `_comum.heredocs` nem o leitor do hook.
    K3_DO_TESTE = re.compile(r"\"\$\(cat[ \t]+<<'(\w+)'\n(.*?\n)?\1\n\)\"", re.S)
    LINHAS_QUE_FECHAM = ("{X})", "{X} )", "{X} x)", "{X};)", "{X}foo")  # o bash 5.3 fecha as quatro primeiras em `$(`
    TROCAS_DE_PALAVRA = ("-c", "--config-env=core.fsmonitor=X", "--exec-path=/tmp/x", "sh")

    @classmethod
    def heredocs_do_teste(cls, texto):
        """Os heredocs `<<'X'` de um caso L, sem o hook: (início do operador, fim do operador, início do corpo, depois da
        linha do delimitador, delimitador). Os casos L têm um heredoc por linha e o corpo acaba na linha igual a X."""
        achados = []
        for m in re.finditer(r"<<'(\w+)'", texto):
            corpo = texto.index("\n", m.end()) + 1
            fim = re.compile(rf"^{m[1]}(?:\n|$)", re.M).search(texto, corpo)
            achados.append((m.start(), m.end(), corpo, fim.start(), min(fim.end(), len(texto)), m[1]))
        assert len(achados) == texto.count("<<"), texto
        return achados

    @classmethod
    def zonas_do_teste(cls, texto):
        """A zona de cada ponto de inserção (0 a len): corpo, k (recusa sempre), simples, duplas ou fora."""
        zona = [None] * (len(texto) + 1)
        for operador, fim_do_operador, corpo, _, fim, _ in cls.heredocs_do_teste(texto):
            for i in range(operador + 1, fim_do_operador):
                zona[i] = "k"
            for i in range(corpo, fim + 1):
                zona[i] = "corpo"
        for m in cls.K3_DO_TESTE.finditer(texto):
            for i in range(m.start() + 1, m.end()):
                zona[i] = zona[i] or "k"
        estado = "fora"
        for i, c in enumerate(texto):
            zona[i] = zona[i] or estado
            if zona[i] in ("corpo", "k"):
                continue
            if c == "'" and estado != "duplas":
                estado = "fora" if estado == "simples" else "simples"
            elif c == '"' and estado != "simples":
                estado = "fora" if estado == "duplas" else "duplas"
        zona[len(texto)] = zona[len(texto)] or estado
        return zona

    def casos_aceitos(self, corpos=None):
        """(id, hook, texto) de cada caso L com heredoc que a gramática aceita, com o corpo de cada hook (`corpos`, ou os
        do corpus)."""
        _comum, _, _ = modulos_dos_hooks()
        dados = corpus_da_volta_unica()
        aceitos = []
        for caso in dados["casos"]:
            if caso["classe"] != "L" or "comando" not in caso:
                continue
            for hook, corpo in (corpos or dados["corpos"]).items():
                texto = caso["comando"].replace("{CORPO}", corpo)
                if caso[hook] == 0 and isinstance(_comum.gramatica_com_heredoc(texto), _comum.Gramatica):
                    aceitos.append((caso["id"], hook, texto))
        return aceitos

    # T8 por nível (seção 3 da proposta caminho-rev8): o texto do nível 1 dentro de cada reavaliação que o hook segue,
    # escrito para o nível 0, e o `<<` dele em cada forma que o nível 0 apaga até `<<` (`HEREDOC_DO_TESTE`). Só o T8 a usa:
    # no T9b e na propriedade da opção B, G1 (`textos_de_g1`) a substitui (RET-LEITURA-HOOK-C).
    NIVEIS = (("eval '{}'", "simples"), ('eval "{}"', "duplas"), ("eval {}", "sem aspas"), ("bash -c '{}'", "simples"),
              ('sh -c "{}"', "duplas"), ("env X=1 bash -c '{}'", "simples"), ("command eval '{}'", "simples"))
    FORMAS_DO_HEREDOC = ("<<", "<''<", '<""<', "\\<\\<", "<\\\n<", "<'\\''<", "<$(:)<")
    HEREDOC_DO_TESTE = re.compile(r"<(?:['\"\\]|\\\n|\$\([^()]*\))*<")  # o que o bash pode juntar em `<<` num nível de cima

    @staticmethod
    def para_o_nivel_0(texto, aspas):
        """O texto que o nível 0 entrega ao `eval`/`bash -c` como `texto`: entre aspas simples, duplas ou sem aspas (cada
        sinal com `\\`, a quebra de linha entre aspas duplas, como no Q4)."""
        if aspas == "simples":
            return texto.replace("'", "'\\''")
        if aspas == "duplas":
            return re.sub(r'([\\"$`])', r"\\\1", texto)
        return "".join(c if re.fullmatch(r"[\w./:=@,+%^-]", c) else '"\n"' if c == "\n" else "\\" + c for c in texto)

    @classmethod
    def mutacoes_de_nivel(cls, texto):
        """(rótulo, texto do nível 0) do caso dentro de cada reavaliação de `NIVEIS`, com o `<<` em cada forma de
        `FORMAS_DO_HEREDOC` (sem aspas, só a forma `\\<\\<` da própria escrita)."""
        saida = []
        for nivel, aspas in cls.NIVEIS:
            escrito = cls.para_o_nivel_0(texto, aspas)
            formas = ("\\<\\<",) if aspas == "sem aspas" else cls.FORMAS_DO_HEREDOC
            for forma in formas:
                na_forma = escrito if aspas == "sem aspas" else escrito.replace("<<", forma)
                saida.append((f"{nivel.format('…')} {forma!r}", nivel.format(na_forma)))
        return saida

    def mutacoes_de_palavra(self):
        """T8 por palavra: (rótulo, texto com a palavra simples, texto com a mesma palavra entre aspas). Cada palavra
        fora de aspas, de corpo e das formas K, e cada troca de `TROCAS_DE_PALAVRA` no lugar dela, em `'…'`, `"…"` e
        partida (`-'c'`): o bash entrega ao programa a mesma palavra."""
        saida = []
        for id, hook, texto in self.casos_aceitos():
            zona = self.zonas_do_teste(texto)
            for m in re.finditer(r"[\w./:=@,+%~^-]+", texto):
                antes, depois = texto[m.start() - 1:m.start()], texto[m.end():m.end() + 1]
                if any(zona[i] != "fora" for i in range(m.start(), m.end() + 1)) or antes not in ("", " ", "\n", ";", "&") \
                        or depois not in ("", " ", "\n", ";", "&"):
                    continue
                for troca in (m[0],) + self.TROCAS_DE_PALAVRA:
                    simples = texto[:m.start()] + troca + texto[m.end():]
                    for aspas in (f"'{troca}'", f'"{troca}"', f"{troca[0]}'{troca[1:]}'" if len(troca) > 1 else None):
                        if aspas:
                            saida.append((f"{id}/{hook}: {m[0]!r} -> {aspas!r}", simples,
                                          texto[:m.start()] + aspas + texto[m.end():]))
        return saida

    def test_t8_mutacao_da_gramatica_da_opcao_d(self):  # T8 (RET-LEITURA-HOOK-D e -A)
        """A classe "leitor" acaba quando a gramática decide pelo texto que o bash roda. Para cada caso L que ela aceita
        (com o corpo de cada hook): (1) cada caractere fora do alfabeto e cada abridor (`$(`, `$((`, `<(`, `>(`, crase,
        `${`, `$'`, `$"`) inserido em cada posição recusa, salvo dentro de aspas simples, dentro de aspas duplas se a
        inserção não tem `$`, crase, `\\` nem `!`, e no corpo; dentro da palavra `"$(cat <<'X'…X⏎)"` e do operador,
        qualquer inserção recusa. (2) Por palavra: a palavra entre aspas só passa se ela passa sem as aspas (opção A,
        item 1; o contrário é só recusa a mais, como `'cat' > arq` na K1, lida crua). (3) Por nível: o caso dentro de cada
        reavaliação de `NIVEIS`, com o `<<` em cada forma de `FORMAS_DO_HEREDOC`, recusa (item 2 e opção A da
        revalidação 8). (4) Por corpo:
        uma linha `X)`, `X )`, `X x)`, `X;)` ou `Xfoo` no corpo recusa (item 3). As zonas vêm de uma varredura própria."""
        _comum, _, _ = modulos_dos_hooks()
        inseridos = list("#{}<>()*?[]!|$`\\") + ["$(", "$((", "<(", ">(", "${", "$'", '$"']
        contagem = collections.Counter()
        usados = set()
        for id, hook, texto in self.casos_aceitos():
            usados.add(id)
            zona = self.zonas_do_teste(texto)
            for i in range(len(texto) + 1):
                if zona[i] in ("corpo", "simples"):
                    continue
                for inserido in inseridos:
                    if zona[i] == "duplas" and not set(inserido) & _comum.DUPLAS_RECUSA:
                        continue
                    mutada = texto[:i] + inserido + texto[i:]
                    if mutada.replace("cat >>", "cat >") == texto.replace("cat >>", "cat >") and mutada != texto:
                        continue  # `cat >` mais `>` é a forma K1 com `>>`, também aceita
                    if not self.HEREDOC_DO_TESTE.search(mutada):
                        continue  # o sinal partiu o `<<` (`<#<`): sem `<<` que o bash forme a gramática não vale (opção A)
                    contagem["caractere"] += 1
                    self.assertIsNotNone(_comum.fora_da_gramatica_com_heredoc(mutada),
                                         f"{id}/{hook}: passou com {inserido!r} em {i}: {mutada!r}")
            for rotulo, envolto in self.mutacoes_de_nivel(texto):
                contagem["nivel"] += 1
                self.assertIsNotNone(_comum.fora_da_gramatica_com_heredoc(envolto),
                                     f"{id}/{hook} em {rotulo}: passou {envolto!r}")
            for _, _, corpo, fim_do_corpo, _, delimitador in self.heredocs_do_teste(texto):
                pontos = [corpo] + [k + 1 for k in range(corpo, fim_do_corpo) if texto[k] == "\n"]
                for ponto in dict.fromkeys(pontos):
                    for linha in self.LINHAS_QUE_FECHAM:
                        mutada = texto[:ponto] + linha.format(X=delimitador) + "\n" + texto[ponto:]
                        contagem["corpo"] += 1
                        self.assertIsNotNone(_comum.fora_da_gramatica_com_heredoc(mutada),
                                             f"{id}/{hook}: passou com {linha!r} no corpo: {mutada!r}")
        for rotulo, simples, entre_aspas in self.mutacoes_de_palavra():
            contagem["palavra"] += 1
            if _comum.fora_da_gramatica_com_heredoc(entre_aspas) is None:  # a K1 é lida crua: `'cat' > a` só recusa
                self.assertIsNone(_comum.fora_da_gramatica_com_heredoc(simples),
                                  f"{rotulo}: passou entre aspas e recusa sem elas: {entre_aspas!r}")
        self.assertLessEqual({"L1", "L2", "L3", "L11", "K1a", "K1b", "K2", "K3a", "K3b"}, usados)
        self.assertGreaterEqual(contagem["caractere"], 1000)
        self.assertGreaterEqual(contagem["palavra"], 500)
        self.assertGreaterEqual(contagem["nivel"], 43 * len(usados))
        self.assertGreaterEqual(contagem["corpo"], 5 * len(usados))

    REGISTRADOR = """#!{bash}
e=
while IFS= read -r l; do e+="$l"$'\\n'; done
e+="$l"
{{ printf '%s\\037' "${{0##*/}}" "$@"; printf '\\035%s\\036' "$e"; }} >> "$REG"
[[ ${{0##*/}} == cat ]] && printf '%s' "$e"
exit 0
"""
    EMBUTIDOS = frozenset({"cd", "echo", "true"})  # da lista da gramática, o bash os roda sem processo

    @classmethod
    def esperado_no_bash(cls, lida, pasta):
        """A sequência (programa, argumentos, entrada) que o bash tem de rodar para o que a gramática aceitou: os comandos
        simples sem aspas, na ordem, cada `"$(cat <<'X'…)"` antes do comando dele (um `cat` com o corpo na entrada, e o
        corpo sem as quebras do fim no lugar da palavra), o corpo de `-F - <<'X'` na entrada do `git`, e o `cat` da K1.
        Os embutidos não abrem processo; as pastas de `cd` são criadas em `pasta`. None se um `cd` sai da pasta ou leva
        opção (o bash para a lista no `cd` que falha)."""
        _comum, _, _ = modulos_dos_hooks()
        if lida.k1:
            return [("cat", [], lida.corpos[0])]
        eventos, corpos, atual = [], iter(lida.corpos), Path(pasta)
        for palavras in lida.comandos:
            argumentos, entrada = [], ""
            for palavra in palavras:
                if palavra == _comum.OPERADOR_K:
                    entrada = next(corpos)
                elif palavra == _comum.PALAVRA_K3:
                    corpo = next(corpos)
                    eventos.append(("cat", [], corpo))
                    argumentos.append(corpo.rstrip("\n"))
                else:
                    argumentos.append(palavra)
            if argumentos[0] == "cd":
                if len(argumentos) != 2 or argumentos[1].startswith(("/", "-")) or ".." in argumentos[1].split("/"):
                    return None
                atual = atual / argumentos[1]
                atual.mkdir(parents=True, exist_ok=True)
            if argumentos[0] not in cls.EMBUTIDOS:
                eventos.append((argumentos[0], argumentos[1:], entrada))
        return eventos

    def test_t9_oraculo_de_bash(self):  # T9 (RET-LEITURA-HOOK-A, seção 3 da proposta caminho-rev7)
        """O que a gramática libera com o marcador crítico e `<<` roda no bash exatamente o que ela listou. Para cada
        texto do corpus e das mutações de palavra do T8 que a gramática aceita, o bash roda o texto como `env -i bash
        --noprofile --norc -c` (o ambiente só com `PATH` e `REG`), numa pasta de `$TMPDIR`, com o `PATH` só com
        registradores (um script do próprio bash por nome que aparece no texto: grava o argv e a entrada em `REG`, sem
        rede); a sequência gravada tem de ser a de `esperado_no_bash`, e nenhum programa pode faltar ao `PATH`. Só
        roda o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        _comum, conformidade, parecer = modulos_dos_hooks()
        dados = corpus_da_volta_unica()
        textos = {}
        for caso in dados["casos"]:
            for hook, corpo in dados["corpos"].items():
                if "comando" in caso:
                    textos.setdefault(caso["comando"].replace("{CORPO}", corpo), f"{caso['id']}/{hook}")
        for rotulo, simples, entre_aspas in self.mutacoes_de_palavra():
            textos.setdefault(simples, rotulo)
            textos.setdefault(entre_aspas, rotulo)
        rodados, ids = 0, set()
        with tempfile.TemporaryDirectory(prefix="forge-t9-") as tmp:
            for n, (texto, rotulo) in enumerate(textos.items()):
                if not (conformidade.CRITICO.search(texto) or parecer.CRITICO.search(texto)):
                    continue
                lida = _comum.gramatica_com_heredoc(texto)
                if not isinstance(lida, _comum.Gramatica):
                    continue
                base = Path(tmp) / str(n)
                registradores, pasta, registro = base / "bin", base / "pasta", base / "registro"
                registradores.mkdir(parents=True)
                pasta.mkdir()
                esperado = self.esperado_no_bash(lida, pasta)
                if esperado is None:
                    continue
                for nome in set(re.findall(r"[A-Za-z_][\w.+-]*", texto)) | {"cat", "git", "gh", "mkdir", "sh"}:
                    arquivo = registradores / nome
                    arquivo.write_text(self.REGISTRADOR.format(bash=bash), encoding="utf-8")
                    arquivo.chmod(0o755)
                r = subprocess.run([bash, "--noprofile", "--norc", "-c", texto], cwd=pasta, stdin=subprocess.DEVNULL,
                                   env={"PATH": str(registradores), "REG": str(registro)}, capture_output=True,
                                   text=True, timeout=10)
                gravado = registro.read_text(encoding="utf-8") if registro.exists() else ""
                rodou = []
                for item in gravado.split("\036")[:-1]:
                    argv, entrada = item.split("\035", 1)
                    argv = argv.split("\037")[:-1]
                    rodou.append((argv[0], argv[1:], entrada))
                with self.subTest(rotulo=rotulo):
                    self.assertNotIn("command not found", r.stderr, f"{texto!r}: o bash rodou um programa fora do PATH")
                    self.assertEqual(rodou, esperado, f"{texto!r}: o bash rodou outra coisa ({r.stderr.strip()})")
                rodados += 1
                ids.add(rotulo.split("/")[0].split(":")[0])
        self.assertLessEqual({"K1a", "K1b", "K2", "K3a", "K3b", "L1", "L3"}, ids)
        self.assertGreaterEqual(rodados, 200)

    # T9b (seção 3 da proposta caminho-rev8): o oráculo do gatilho. O T9 só roda o que a gramática aceitou; aqui entra o
    # que o hook libera, com a linha sentinela no `{CORPO}`.
    SENTINELAS = {"conformidade": "git push origin SENTINELA:main", "parecer": "gh pr merge SENTINELA --merge"}
    SHELLS_DO_T9B = ("bash", "sh", "dash", "zsh", "ksh", "rbash")  # no `PATH` do T9b, o próprio bash: a reavaliação roda
    # Os prefixos que só repassam o comando, no T9b, sem o programa real (R3 da segurança, revalidação 9): o resto roda.
    REPASSADORES_DO_T9B = {
        "sudo": 'while [[ $1 == -* ]]; do shift; done\nexec "$@"\n',
        "nohup": 'exec "$@"\n',
        "nice": '[[ $1 == -n ]] && shift 2\nexec "$@"\n',
        "timeout": 'shift\nexec "$@"\n',
        "flock": 'while [[ $1 == -* ]]; do shift; done\nshift\nexec "$@"\n',
        "find": ('while [[ $# -gt 0 && $1 != -exec ]]; do shift; done\nshift\na=()\n'
                 'while [[ $# -gt 0 && $1 != ";" ]]; do a+=("${1//\\{\\}/.}"); shift; done\nexec "${a[@]}"\n'),
    }
    DECISOES = {}  # (hook, texto) -> código, de `decisoes_dos_hooks`

    def modelos_montados(self):
        """{hook: (raiz, entrada, proc)}: um repositório por hook, no modelo do corpus, montado uma vez."""
        montados = {}
        for hook, modelo in corpus_da_volta_unica()["modelos"].items():
            caminho = FIXTURES / hook / f"{modelo}.json"
            base = json.loads(caminho.read_text(encoding="utf-8"))
            base["passos"] = []
            tmp = self._pasta_temporaria()
            raiz, entrada = Fixture(caminho, base).montar(tmp, os.getpid())
            montados[hook] = (raiz, entrada, montar_proc(tmp, None))
        return montados

    def decidir_com_prazo(self, montados, hook, texto, **como):
        """(código, stderr, segundos) do hook real sobre `texto`, no modelo do corpus, com o vigia de produção."""
        raiz, entrada, proc = montados[hook]
        entrada = json.loads(json.dumps(entrada))
        entrada["tool_input"]["command"] = texto
        inicio = time.monotonic()
        r = rodar(hook, entrada, raiz, proc, {"FORGE_NPROC": "8"}, producao=True, **como)
        return r.returncode, r.stderr, time.monotonic() - inicio

    def decisoes_dos_hooks(self, pedidos):
        """{(hook, texto): código} de cada hook, no modelo do corpus (um repositório por hook, montado uma vez), em
        paralelo. O hook cujo marcador (`CRITICO`) o texto não tem não roda: ele libera sem ler (0). Os códigos ficam
        em `DECISOES`, da classe: o T9b e a propriedade da opção B leem os mesmos textos."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        montados = self.modelos_montados()

        def decidir(pedido):
            hook, texto = pedido
            if not criticos[hook].search(texto):
                return 0
            raiz, entrada, proc = montados[hook]
            entrada = json.loads(json.dumps(entrada))
            entrada["tool_input"]["command"] = texto
            # a sonda de tempo (texto de dezenas de KB) vale como o Claude Code a trata: passou de 10 s, liberou
            return rodar(hook, entrada, raiz, proc, {"FORGE_NPROC": "8"},
                         como_o_claude_code=len(texto) > 50_000).returncode

        faltam = [pedido for pedido in dict.fromkeys(pedidos) if pedido not in self.DECISOES]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(4, (os.cpu_count() or 2) // 2))) as pool:
            self.DECISOES.update(zip(faltam, pool.map(decidir, faltam)))
        return {pedido: self.DECISOES[pedido] for pedido in pedidos}

    def rodar_no_bash_do_t9b(self, bash, texto, base):
        """Roda o texto como no T9 (`env -i bash --noprofile --norc -c`, `HOME` e a pasta em `base`, no `$TMPDIR`, sem
        rede), com registradores no `PATH` e em `base/x0` (o `PATH` que o Z1 monta: `PATH=<base>/x$(( cat ))`), onde o
        `cat` roda a entrada como o bash (o B1 da revalidação 7). Os shells são o próprio bash. Devolve os (programa,
        argumentos) gravados. Nenhum programa real além do bash (R-CUSTO)."""
        registradores, pasta, registro, casa = base / "bin", base / "pasta", base / "registro", base / "casa"
        z1 = base / "x0"
        for d in (registradores, pasta, casa, z1):
            d.mkdir(parents=True)
        # os shells e os repassadores entram sempre: a grafia do nome (`b''ash`, `$'\x62'ash`) não o mostra no texto
        nomes = set(re.findall(r"[A-Za-z_][\w.+-]*", texto)) | {"cat", "git", "gh", "mkdir", "env"}
        for nome in nomes | set(self.SHELLS_DO_T9B) | set(self.REPASSADORES_DO_T9B):
            for d in (registradores, z1):
                arquivo = d / nome
                if nome in self.SHELLS_DO_T9B:
                    arquivo.write_text(f'#!{bash}\nexec {bash} --noprofile --norc "$@"\n', encoding="utf-8")
                elif nome in self.REPASSADORES_DO_T9B:
                    arquivo.write_text(f"#!{bash}\n{self.REPASSADORES_DO_T9B[nome]}", encoding="utf-8")
                elif nome == "env":  # o `env X=1 prog`, sem o programa real
                    arquivo.write_text(f'#!{bash}\nwhile [[ $1 == *=* ]]; do export "$1"; shift; done\nexec "$@"\n',
                                       encoding="utf-8")
                elif nome == "cat" and d == z1:
                    arquivo.write_text(f"#!{bash}\nexec {bash} --noprofile --norc -s\n", encoding="utf-8")
                else:
                    arquivo.write_text(self.REGISTRADOR.format(bash=bash), encoding="utf-8")
                arquivo.chmod(0o755)
        subprocess.run([bash, "--noprofile", "--norc", "-c", texto], cwd=pasta, stdin=subprocess.DEVNULL,
                       env={"PATH": str(registradores), "REG": str(registro), "HOME": str(casa)}, capture_output=True,
                       text=True, timeout=10)
        gravado = registro.read_text(encoding="utf-8") if registro.exists() else ""
        rodou = []
        for item in gravado.split("\036")[:-1]:
            argv = item.split("\035", 1)[0].split("\037")[:-1]
            rodou.append((argv[0], argv[1:]))
        return rodou

    def textos_do_t9b(self, base):
        """(rótulo, hook, texto, pasta, marca) dos textos do corpus com `{CORPO}` (a sentinela do hook no lugar, e
        `/tmp/x` do Z1 numa pasta de `base`) e dos textos de G1 com a sentinela (`textos_de_g1`, RET-LEITURA-HOOK-C: G1
        substitui as mutações de `NIVEIS`)."""
        dados = corpus_da_volta_unica()
        textos = []
        for caso in dados["casos"]:
            if "{CORPO}" not in caso.get("comando", ""):
                continue
            for hook, sentinela in self.SENTINELAS.items():
                if caso[hook] is None:
                    continue
                pasta = base / f"{caso['id']}-{hook}"
                marca = caso.get("fecha")
                marca = marca.get(hook) if isinstance(marca, dict) else marca
                marca = NAO_PROMETE if caso.get("nao_promete") else marca
                texto = caso["comando"].replace("{CORPO}", sentinela).replace("/tmp/x", f"{pasta}/x")
                textos.append((f"{caso['id']}/{hook}", hook, texto, pasta, marca))
        for k, (rotulo, hook, texto, _) in enumerate(self.textos_de_g1(self.SENTINELAS)):
            textos.append((rotulo, hook, texto, base / f"g1-{k}", None))
        return textos

    def test_t9b_oraculo_do_gatilho(self):  # T9b (RET-LEITURA-HOOK-B, seção 3 da proposta caminho-rev8)
        """O que o hook libera com o marcador crítico, o bash não roda escondido. Para cada texto de `textos_do_t9b` que
        o hook dono da sentinela libera (código 0), o bash roda o texto (`rodar_no_bash_do_t9b`), e nenhum registrador
        pode gravar a linha sentinela: o hook liberou, e o bash rodou a linha que ele não viu. Com a marca `fecha`, o
        caso ainda tem de mostrar a sentinela rodada (o vermelho continua provado). Só roda o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria()
        textos = self.textos_do_t9b(base)
        decisoes = self.decisoes_dos_hooks([(hook, texto) for _, hook, texto, _, _ in textos])
        ids = set()
        for rotulo, hook, texto, pasta, marca in textos:
            if decisoes[(hook, texto)] != 0:
                if marca and marca != NAO_PROMETE:
                    with self.subTest(rotulo=rotulo):
                        self.conferir_marca(marca, True, f"o {hook} já recusa {texto!r}")
                continue
            sentinela = shlex.split(self.SENTINELAS[hook])
            rodou = self.rodar_no_bash_do_t9b(bash, texto, pasta)
            if marca == NAO_PROMETE:  # o código de hoje: o hook libera e o bash roda a sentinela (cartão, não bloqueia)
                with self.subTest(rotulo=rotulo):
                    self.assertIn((sentinela[0], sentinela[1:]), rodou, f"{rotulo}: o bash não roda a sentinela")
                continue
            with self.subTest(rotulo=rotulo):
                self.conferir_marca(marca, (sentinela[0], sentinela[1:]) not in rodou,
                                    f"o {hook} libera {texto!r} e o bash roda {' '.join(sentinela)}: {rodou}")
            ids.add(rotulo.split("/")[0])
        self.assertLessEqual({"K1a", "K1b"}, ids, "o T9b roda no bash o que o hook libera")
        self.assertGreaterEqual(len(textos), 500)

    # G1, o gerador da classe "nível" (proposta caminho-rev9, 3B): o texto com uma reavaliação pelo shell, por produto
    # de prefixos × grafias (`GRAFIAS`, no nome e na opção) × reavaliadores × corpos. A verdade vem da construção: o
    # teste pôs a reavaliação ali, e `test_g1_esta_na_classe` prova no bash (hooks desligados) que ela roda o corpo.
    # Prefixo: (nome, molde com `{R}` no lugar da reavaliação, nativo, para quem). Nativo: o bash o executa sozinho
    # (palavra reservada, builtin), e o texto entra na prova de G1. Para quem: "eval", "shell" ou None (os dois); o que
    # só repassa a um programa (`env`, `sudo`, `find -exec`) não roda o builtin `eval`. O `xprefixo` (programa
    # desconhecido) só prova a regra do hook: no T9b, é um registrador (S6 da proposta).
    PREFIXOS_DE_G1 = (
        ("nenhum", "{R}", True, None),
        ("coproc", "coproc {R}", True, None),
        ("coproc NOME {", "coproc x { {R}; }", True, None),
        ("time", "time {R}", True, None),
        ("time -p", "time -p {R}", True, None),
        ("!", "! {R}", True, None),
        ("if", "if {R}; then :; fi", True, None),
        ("{", "{ {R}; }", True, None),
        ("$(…)", "x=$({R})", True, None),
        ("pipeline", "true | {R}", True, None),
        ("command", "command {R}", True, None),
        ("builtin", "builtin {R}", True, "eval"),
        ("exec", "exec {R}", True, "shell"),
        ("env X=1", "env X=1 {R}", False, "shell"),
        ("sudo", "sudo {R}", False, "shell"),
        ("flock f", "flock f {R}", False, "shell"),
        ("find -exec", "find . -maxdepth 0 -exec {R} \\;", False, "shell"),
        ("xprefixo", "xprefixo {R}", False, None),
    )
    GRAFIAS_DE_G1 = ("direta", "simples", "duplas", "barra", "ansi", "hexa", "ansi no meio", "vazio no meio")
    REAVALIADORES_DE_G1 = (("eval", None), ("bash", "-c"), ("sh", "-c"), ("zsh", "-c"), ("dash", "-c"), ("ksh", "-c"),
                           ("rbash", "-c"), ("bash", "-ec"), ("bash", "-lc"))
    LINHAS_DIRETAS = {"conformidade": "git push origin feature/x",
                      "parecer": "gh pr create --draft --base develop --title t --body x"}

    @classmethod
    def textos_de_g1(cls, corpos_por_hook, so_nativos=False):
        """(rótulo, hook, texto, nativo) de G1 com o corpo de cada hook (`corpos_por_hook`: hook -> linha), entre aspas
        simples como argumento da reavaliação. A grafia vale para o nome e para a opção do shell."""
        saida = []
        for prefixo, molde, nativo, para in cls.PREFIXOS_DE_G1:
            if so_nativos and not nativo:
                continue
            for grafia in cls.GRAFIAS_DE_G1:
                escrever = cls.GRAFIAS[grafia]
                for nome, opcao in cls.REAVALIADORES_DE_G1:
                    if para and para != ("eval" if opcao is None else "shell"):
                        continue
                    reavaliador = escrever(nome) + (f" {escrever(opcao)}" if opcao else "")
                    for hook, corpo in corpos_por_hook.items():
                        texto = molde.replace("{R}", f"{reavaliador} '{corpo}'")
                        rotulo = f"G1 {prefixo} / {grafia} / {nome}{' ' + opcao if opcao else ''} / {hook}"
                        saida.append((rotulo, hook, texto, nativo))
        return saida

    def test_g1_esta_na_classe(self):  # item 3 do critério de fim da opção B (proposta caminho-rev9): o oráculo do oráculo
        """Com os hooks desligados, o bash roda a sentinela em cada texto de G1 de prefixo nativo: G1 só tem reavaliação
        de verdade, e um gerador que não a produz fica vermelho. Roda como o T9b (`rodar_no_bash_do_t9b`: `env -i`,
        `HOME` no `$TMPDIR`, sem rede, os shells são o próprio bash); só o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria()
        textos = self.textos_de_g1(self.SENTINELAS, so_nativos=True)

        def rodar(item):
            k, (_, _, texto, _) = item
            return self.rodar_no_bash_do_t9b(bash, texto, base / f"g1-{k}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(4, (os.cpu_count() or 2) // 2))) as pool:
            rodados = list(pool.map(rodar, enumerate(textos)))
        for (rotulo, hook, texto, _), rodou in zip(textos, rodados):
            sentinela = shlex.split(self.SENTINELAS[hook])
            with self.subTest(rotulo=rotulo):
                self.assertIn((sentinela[0], sentinela[1:]), rodou, f"o bash não roda a sentinela em {texto!r}")
        self.assertGreaterEqual(len(textos), 1500)

    # Propriedade da opção B ((5) da seção 4B da proposta caminho-rev8, item 2 do critério da caminho-rev9), sem bash:
    # com o marcador crítico e uma reavaliação pelo shell, o hook recusa. No corpus, a reavaliação é reconhecida por uma
    # leitura própria do teste (`REAVALIACAO_DO_TESTE`); em G1, pela construção.
    REAVALIACAO_DO_TESTE = re.compile(r"(?<![\w.-])(?:eval|(?:bash|sh|zsh|dash|ksh)(?:\s+-\w+)*?\s+-[A-Za-z]*c[A-Za-z]*)(?=\s)")

    def test_propriedade_da_reavaliacao_com_marcador(self):  # (5) da opção B, sobre G1 (RET-LEITURA-HOOK-B e -C)
        """Para todo texto de G1 (com a linha crítica direta e com a sentinela de cada hook), cada hook cujo marcador
        crítico (`CRITICO`) o texto tem roda e dá 2. No corpus, o caso com marcador e reavaliação
        (`REAVALIACAO_DO_TESTE`, fora das formas "não promete") tem a célula 2 (o `test_corpus_nos_dois_hooks` prova o
        código)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        dados = corpus_da_volta_unica()
        no_corpus = 0
        for caso in dados["casos"]:
            for hook, critico in criticos.items():
                texto = caso.get("comando", "").replace("{CORPO}", dados["corpos"][hook])
                if caso[hook] is not None and not caso.get("nao_promete") and critico.search(texto) \
                        and self.REAVALIACAO_DO_TESTE.search(texto):
                    no_corpus += 1
                    with self.subTest(caso=f"{caso['id']}/{hook}"):
                        self.assertEqual(caso[hook], 2, f"reavaliação com marcador e célula {caso[hook]}: {texto!r}")
        textos = self.textos_de_g1(self.LINHAS_DIRETAS) + self.textos_de_g1(self.SENTINELAS)
        pedidos = [(hook, texto) for _, _, texto, _ in textos for hook, critico in criticos.items()
                   if critico.search(texto)]
        decisoes = self.decisoes_dos_hooks(pedidos)
        for rotulo, dono, texto, _ in textos:
            self.assertRegex(texto, criticos[dono], "o corpo de G1 tem o marcador do hook dele")
            for hook, critico in criticos.items():
                if critico.search(texto):
                    with self.subTest(rotulo=rotulo, hook=hook):
                        self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        self.assertGreaterEqual(no_corpus, 25)
        self.assertGreaterEqual(len(textos), 4000)

    # Propriedade da opção C (item 1 do critério de fim, proposta caminho-rev10, 3C): o `$'` e o `$"` entram em cada
    # posição da palavra do reavaliador e da opção de G1, com cada escape do alfabeto inteiro (`\` e cada caractere de
    # 0x20 a 0x7E, a quebra de linha e o `\x{…}` do bash 5.3, com e sem a chave de fecho). A verdade vem da construção:
    # a palavra gerada tem `$'` ou `$"` fora de aspas, e o teste não depende do que o bash faz com o escape.
    ESCAPES_DO_ALFABETO = tuple("\\" + chr(c) for c in range(0x20, 0x7F)) + (
        "\\\n", "\\x{65}", "\\x{0000065}", "\\x{65", "\\x{}", "\\x{zz}", "\\u{65}", "\\U", "\\c", "\\c\\'")
    FORMAS_ANSI = (("$'", "'"), ('$"', '"'))
    PREFIXOS_DO_ALFABETO = ("nenhum", "coproc", "env X=1", "$(…)", "pipeline")

    @classmethod
    def textos_do_alfabeto(cls, corpos_por_hook, escapes=None, prefixos=None, reavaliadores=None):
        """(rótulo, hook, texto) de G1 com o `$'` ou o `$"` e um escape em cada posição do nome do reavaliador e da opção."""
        saida = []
        escapes = cls.ESCAPES_DO_ALFABETO if escapes is None else escapes
        for prefixo, molde, _, para in cls.PREFIXOS_DE_G1:
            if prefixo not in (prefixos or cls.PREFIXOS_DO_ALFABETO):
                continue
            for nome, opcao in (reavaliadores or cls.REAVALIADORES_DE_G1):
                if para and para != ("eval" if opcao is None else "shell"):
                    continue
                for onde, palavra in (("nome", nome), ("opção", opcao)):
                    if palavra is None:
                        continue
                    for posicao in range(len(palavra) + 1):
                        for (abre, fecha), escape in itertools.product(cls.FORMAS_ANSI, escapes):
                            nova = palavra[:posicao] + abre + escape + fecha + palavra[posicao:]
                            reavaliador = (nova if onde == "nome" else nome) + (f" {nova if onde == 'opção' else opcao}" if opcao else "")
                            for hook, corpo in corpos_por_hook.items():
                                rotulo = f"alfabeto {prefixo} / {nome} {opcao or ''} / {onde}@{posicao} / {abre}{escape}{fecha} / {hook}"
                                saida.append((rotulo, hook, molde.replace("{R}", f"{reavaliador} '{corpo}'")))
        return saida

    def test_propriedade_do_alfabeto_de_escapes_com_marcador(self):  # item 1 do critério de fim da opção C
        """Com o marcador crítico, toda palavra com `$'` ou `$"` fora de aspas recusa, qualquer que seja o escape. Todo
        texto gerado (`textos_do_alfabeto`) é reconhecido por `reavaliacao`, o reconhecedor que os dois hooks usam, e
        uma amostra dos escapes, em cada posição, dá 2 nos DOIS hooks reais: a propriedade separa os hooks (a mutação que
        tira a recusa de um só deixa essa parte vermelha)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        todos = self.textos_do_alfabeto(self.LINHAS_DIRETAS)
        self.assertGreaterEqual(len(todos), 40_000)
        for rotulo, hook, texto in todos:
            self.assertRegex(texto, criticos[hook], "o texto tem o marcador do hook dele")
            if _comum.reavaliacao(texto) is None:
                self.fail(f"o reconhecedor libera {rotulo}: {texto!r}")
        amostra = self.ESCAPES_DO_ALFABETO[::9] + ("\\x{65}", "\\x{0000065}", "\\x{65", "\\'", '\\"', "\\$")
        reais = self.textos_do_alfabeto(self.LINHAS_DIRETAS, amostra, ("nenhum",), (("bash", "-c"), ("eval", None)))
        decisoes = self.decisoes_dos_hooks([(hook, texto) for _, hook, texto in reais])
        for rotulo, hook, texto in reais:
            with self.subTest(rotulo=rotulo):
                self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        self.assertGreaterEqual(len(reais), 800)

    def conferir_os_pares_contra_o_bash(self):  # item 2 do critério de fim da opção C
        """Parte de `test_reducao_da_palavra_como_o_bash`. Para toda `\\` seguida de cada caractere de 0x20 a 0x7E e da quebra de linha, e depois de cada sufixo (nada, `{`,
        `}`, dígito octal, dígito hexadecimal, `'`, fim), fora de aspas e entre aspas duplas: a `reduzida` dá o mesmo que o
        `printf '%s'` do bash, ou `None` (expansão ou aspas sem par). Nunca um literal diferente, nunca um literal onde
        o bash recusa a palavra. Cobre o alfabeto inteiro, e não uma tabela. Só o bash (R-CUSTO)."""
        _comum, _, _ = modulos_dos_hooks()
        bash = shutil.which("bash")
        casa = self._pasta_temporaria()
        casos = []
        for c in [chr(x) for x in range(0x20, 0x7F)] + ["\n"]:
            for sufixo in ("b", "{b", "}b", "7b", "fb", "'b", ""):
                miolo = f"a\\{c}{sufixo}"
                casos += [("fora", miolo), ("duplas", f'"{miolo}"')]

        def do_bash(caso):
            return subprocess.run([bash, "--noprofile", "--norc", "-c", f"printf '%s' {caso[1]}"], cwd=casa,
                                  env={"HOME": str(casa), "LC_ALL": "C.UTF-8"}, capture_output=True, timeout=30)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(8, (os.cpu_count() or 2)))) as pool:
            do_bash_de = list(pool.map(do_bash, casos))
        for (contexto, cru), r in zip(casos, do_bash_de):
            valor = _comum.reduzida(cru)
            com_expansao = any(ch in cru for ch in "$`*?[{~")
            with self.subTest(contexto=contexto, cru=cru):
                self.assertIsNot(valor, _comum.INDECIDIVEL, "a barra e um caractere não formam `$'` nem `$\"`")
                if valor is None:
                    self.assertTrue(com_expansao or r.returncode != 0, f"None sem expansão nem erro do bash: {cru!r}")
                else:
                    self.assertEqual(r.returncode, 0, f"o bash recusa {cru!r} e o hook o reduz a {valor!r}")
                    self.assertEqual(r.stdout.decode("utf-8", "surrogateescape"), valor)
        self.assertGreaterEqual(len(casos), 1300)

    # As grafias de G1 (proposta caminho-rev9, 3B): a mesma palavra escrita pelos mecanismos de aspas do bash, que a
    # entrega igual ao programa. O teste de diferença (`test_reducao_da_palavra_como_o_bash`) prova cada uma no bash.
    GRAFIAS = {
        "direta": lambda w: w,
        "simples": lambda w: f"'{w}'",
        "duplas": lambda w: f'"{w}"',
        "barra": lambda w: "\\" + w,
        "ansi": lambda w: f"$'{w}'",
        "hexa": lambda w: f"$'\\x{ord(w[0]):02x}'{w[1:]}",
        "ansi no meio": lambda w: f"{w[0]}$'{w[1:]}'",
        "vazio no meio": lambda w: f"{w[0]}''{w[1:]}",
        "locale": lambda w: f'$"{w}"',
        "octal": lambda w: f"$'\\{ord(w[0]):03o}'{w[1:]}",
        "unicode": lambda w: f"$'\\u{ord(w[0]):04x}'{w[1:]}",
    }
    PALAVRAS_DE_G1 = ("eval", "bash", "sh", "zsh", "dash", "ksh", "rbash", "-c", "-ec", "-lc")
    # As bordas da remoção de aspas do POSIX que G1 não gera (a redução não tem tabela de escapes: o `$'…'` e o `$"…"` são
    # INDECIDIVEL, sem ler o escape). Cada uma entra na comparação com o bash.
    BORDAS_DA_REDUCAO = ('"a\\b"', '"a\\$b"', '"a\\`b"', '"a\\"b"', '"a\\\nb"', "e\\\nval", "\\e\\v\\a\\l", "é'v'al",
                         "'$'", "a''b", '""', "\\\\", '"\\\\"', "'\\'", '"\\\nx"')
    # Com `$'` ou `$"` fora de aspas, em qualquer posição e com qualquer escape (o bash 5.3 lê `\x{65}`, o 5.2 não): o
    # hook não lê o escape e não decide.
    INDECIDIVEIS = ("$'eval'", "e$'val'", "$'\\x{65}'val", "$'\\x{0000065}'val", "$'\\x{65'val", "$'ev\\0al'x", "$'\\545val'",
                    "$'\\cA'", "$'\\c\\''", "$'\\u'", "$'\\U00110000'", "$'a\\'b'", "$'ev", "$\"eval\"", "e$\"val\"",
                    "$\"e\\$\"", "$\"ev", "$x$'a'", "$(x)$'a'", "${x}$\"a\"", "`x`$'a'", "\"$(x)\"$'y'", "\"`x`\"$'y'")
    NAO_SE_REDUZEM = ("$x", "${x}", "$(echo eval)", "`echo eval`", "e*", "ev?l", "[e]val", "{e,}val", "~", "\"$x\"",
                      '"a`b`"', "'ev", '"ev', "$((1))", "e$x", "\"$'a'\"", "\"$\\\"\"x", "x\"$(y)\"z", "\"${x}\"")

    def test_reducao_da_palavra_como_o_bash(self):  # item 4 do critério de fim da opção B (proposta caminho-rev9)
        """A redução do hook (`_comum.reduzida`) é a do bash: para cada grafia de G1 de cada palavra de G1 que não usa
        `$'` nem `$"`, e para as bordas, a palavra reduzida é igual à que o `printf '%s'` do bash imprime (`env -i`,
        `HOME` no `$TMPDIR`, sem rede; só o bash, R-CUSTO). A palavra com expansão não se reduz (None: fica no N-HOOK1),
        e a com `$'` ou `$"` fora de aspas é INDECIDIVEL (opção C da revalidação 10). Por último, o teste exaustivo por par
        (`conferir_os_pares_contra_o_bash`)."""
        _comum, _, _ = modulos_dos_hooks()
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash ausente")
        todas = [grafia(w) for w in self.PALAVRAS_DE_G1 for grafia in self.GRAFIAS.values()]
        crus = [cru for cru in todas if "$'" not in cru and '$"' not in cru] + list(self.BORDAS_DA_REDUCAO)
        script = "".join(f"printf '%s\\036' {cru}\n" for cru in crus)
        casa = self._pasta_temporaria()
        saida = subprocess.run([bash, "--noprofile", "--norc", "-c", script], env={"HOME": str(casa), "LC_ALL": "C.UTF-8"},
                               cwd=casa, capture_output=True, timeout=30)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        do_bash = saida.stdout.decode("utf-8", "surrogateescape").split("\036")[:-1]
        self.assertEqual(len(do_bash), len(crus))
        for cru, valor in zip(crus, do_bash):
            with self.subTest(cru=cru):
                self.assertEqual(_comum.reduzida(cru), valor)
        for w in self.PALAVRAS_DE_G1:
            for nome, grafia in self.GRAFIAS.items():
                cru = grafia(w)
                if "$'" in cru or '$"' in cru:
                    self.assertIs(_comum.reduzida(cru), _comum.INDECIDIVEL, f"{nome} de {w}")
                else:
                    self.assertEqual(_comum.reduzida(cru), w, f"{nome} de {w}")
        for cru in self.INDECIDIVEIS:
            with self.subTest(indecidivel=cru):
                self.assertIs(_comum.reduzida(cru), _comum.INDECIDIVEL)
        for cru in self.NAO_SE_REDUZEM:
            with self.subTest(cru=cru):
                self.assertIsNone(_comum.reduzida(cru))
        self.assertGreaterEqual(len(crus), 60)
        self.conferir_os_pares_contra_o_bash()

    # Bloco T da revalidação 10 (proposta caminho-rev10, seção 2): o orçamento de tempo. Os tipos de palavra que mais
    # custam (a unidade, quantas palavras ela tem e a forma de 2 a 3 caracteres, para o teto de caracteres), e o
    # tamanho: 1 mil palavras, o teto de palavras, o teto + 1 e o teto de caracteres com as palavras curtas.
    TIPOS_DO_ORCAMENTO = {
        "nome de shell": ("bash ", 1, "sh "),
        "env": ("env ", 1, "env "),
        "env -S": ("env -S 'x' ", 3, "env -S x "),
        "$'…' longo": ("$'" + "a" * 40 + "' ", 1, "$'a' "),
        "-c": ("-c ", 1, "-c "),
        "inerte": ("x ", 1, "x "),
    }

    def test_t_orcamento_por_numero_de_palavras(self):  # item 1 do critério de fim do bloco T (proposta caminho-rev10)
        """Para cada tipo de palavra de `TIPOS_DO_ORCAMENTO` e cada tamanho, os dois hooks reais, com o vigia de
        produção, recusam a chamada com o marcador (código 2, com a regra) em menos de 3 s, e não deixam o timeout de
        10 s do Claude Code liberá-la. O texto é `: <palavras>; <linha crítica direta>`."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        montados = self.modelos_montados()
        corpos = corpus_da_volta_unica()["corpos"]
        tamanhos = {"1 mil": 1000, "o teto": _comum.TETO_DE_PALAVRAS, "o teto + 1": _comum.TETO_DE_PALAVRAS + 1,
                    "o teto de caracteres": None}
        pior = 0.0
        for tipo, (unidade, por_unidade, curta) in self.TIPOS_DO_ORCAMENTO.items():
            for nome, n in tamanhos.items():
                if n is None:
                    palavras = f": {curta * ((_comum.TETO_DE_CARACTERES_DA_CHAMADA - 200) // len(curta))}"
                else:
                    palavras = f": {unidade * (n // por_unidade)}"
                for hook in ("conformidade", "parecer"):
                    texto = f"{palavras}; {corpos[hook]}"
                    with self.subTest(tipo=tipo, tamanho=nome, hook=hook):
                        codigo, erro, segundos = self.decidir_com_prazo(montados, hook, texto)
                        pior = max(pior, segundos)
                        self.assertEqual(codigo, 2, f"{codigo}: {erro.strip()}")
                        self.assertRegex(erro, r"^R-[A-Z]+: ")
                        self.assertLess(segundos, 3.0, f"{len(texto)} caracteres")
                        if n != 1000:  # `:`, o corpo e as palavras passam de 5 mil: quem recusa é o teto, não a regra do corpo
                            self.assertRegex(erro, "o teto é|linha longa demais")  # o 2.o: o teto antigo do conformidade
        print(f"\n[T] pior tempo de decisão: {pior:.2f} s", file=sys.stderr)

    @staticmethod
    @contextlib.contextmanager
    def limite_de_tempo(segundos):
        """Falha o teste (AssertionError) se o bloco passa de `segundos` s: o alarme interrompe a conta lenta."""
        def estourar(signo, quadro):
            raise AssertionError(f"passou de {segundos} s")
        anterior = signal.signal(signal.SIGALRM, estourar)
        signal.setitimer(signal.ITIMER_REAL, segundos)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, anterior)

    def test_t_reconhecedor_da_reavaliacao_e_linear(self):  # item 2 do critério de fim do bloco T
        """`reavaliacao_das_palavras` e `separar_lancadores` sozinhas, com 50 mil palavras, rodam em menos de 1 s (a
        versão quadrática levava 8,3 s com 10 mil): o limite não oscila com a máquina."""
        _comum, _, _ = modulos_dos_hooks()
        casos = {"shell": ["bash"] * 50_000, "shell com opção": ["bash"] * 49_999 + ["-c"], "env": ["env"] * 50_000,
                 "env -S": ["env", "-S", "x"] * 16_000, "não se reduz": [None] * 50_000, "inerte": ["x"] * 50_000}
        for nome, palavras in casos.items():
            with self.subTest(nome=nome), self.limite_de_tempo(5):
                inicio = time.perf_counter()
                _comum.reavaliacao_das_palavras(palavras)
                _comum.separar_lancadores([p or "" for p in palavras])
                self.assertLess(time.perf_counter() - inicio, 1.0)

    def test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem(self):  # item 3 do critério de fim do bloco T
        """Um passo lento injetado (`lancador(lento=True)`: o 2.o `Hook.campo`, depois do marcador, dorme 60 s) faz os dois hooks
        recusarem a chamada com o marcador antes de 10 s, com a regra do hook (R-CONFORMIDADE, R-REVIEW), e liberarem a
        sem marcador. Sem o passo lento, a mesma chamada com marcador passa: o que recusa é o vigia, e é por construção,
        para qualquer passo lento, e não só para os que o teste 1 gera."""
        montados = self.modelos_montados()
        linhas = {"conformidade": ("git push origin feature/x", "R-CONFORMIDADE"),
                  "parecer": ("gh pr create --draft --base develop --title x --body y", "R-REVIEW")}
        for hook, (critica, regra) in linhas.items():
            with self.subTest(hook=hook, caso="sem passo lento"):
                self.assertEqual(self.decidir_com_prazo(montados, hook, critica)[0], 0)
            with self.subTest(hook=hook, caso="com marcador"):
                codigo, erro, segundos = self.decidir_com_prazo(montados, hook, critica, lento=True)
                self.assertEqual(codigo, 2, erro)
                self.assertRegex(erro, f"^{regra}: ")
                self.assertGreater(segundos, 2.5, "o vigia vence aos 3 s")
                self.assertLess(segundos, PRAZO_DO_CLAUDE_CODE_S)
            with self.subTest(hook=hook, caso="sem marcador"):
                codigo, erro, segundos = self.decidir_com_prazo(montados, hook, "echo oi", lento=True)
                self.assertEqual((codigo, erro), (0, ""))
                self.assertLess(segundos, PRAZO_DO_CLAUDE_CODE_S)

    def test_t_vigia_cobre_a_busca_do_proprio_marcador(self):
        """O marcador é um regex com `.*`, e o texto de propósito o faz levar mais de 10 s (`pr pr … api`). O vigia o
        interrompe, e o marcador desconhecido vale como marcado: recusa, em vez de o timeout liberar a chamada."""
        montados = self.modelos_montados()
        textos = {"parecer": "pr " * 20_000 + "api", "conformidade": "git " * 20_000 + "--no-verify"}
        for hook, texto in textos.items():
            with self.subTest(hook=hook):
                codigo, erro, segundos = self.decidir_com_prazo(montados, hook, texto)
                self.assertEqual(codigo, 2, erro)
                self.assertLess(segundos, PRAZO_DO_CLAUDE_CODE_S)

    def test_corpus_cobre_as_classes(self):
        dados = corpus_da_volta_unica()
        casos = dados["casos"]
        ids = [c["id"] for c in casos]
        self.assertEqual(len(ids), len(set(ids)), "ID repetido no corpus")
        for classe, minimo in MINIMO_POR_CLASSE.items():
            self.assertGreaterEqual(sum(c["classe"] == classe for c in casos), minimo, f"classe {classe}")
        self.assertLessEqual({c["classe"] for c in casos}, set(MINIMO_POR_CLASSE), "a classe X não entra no corpus")
        for id in IDS_DA_VOLTA_UNICA:
            self.assertIn(id, ids)
        marcas = [m for c in casos for m in (c["fecha"].values() if isinstance(c.get("fecha"), dict)
                                             else [c["fecha"]] if "fecha" in c else [])]
        for secao in (dados["oraculo"]["redirecoes"], dados["enumerador"]["completos"], dados["enumerador"]["pedem_alvo"]):
            marcas += [m for item in secao for m in item.get("fecha", {}).values()]
        self.assertLessEqual(set(marcas), REGRAS_DA_VOLTA_UNICA)
        if EXIGE_NENHUMA_MARCA:
            self.assertEqual(marcas, [], "o passo (7) não aceita marca `fecha`")
        for caso in casos:
            self.assertTrue(caso["conformidade"] is not None or caso["parecer"] is not None, caso["id"])
            self.assertEqual(sum(chave in caso for chave in ("comando", "passos")), 1, caso["id"])
            if "nao_promete" in caso:
                self.assertIn(caso["nao_promete"], CARTOES_DO_NAO_PROMETE, caso["id"])
                self.assertNotIn("fecha", caso, f"{caso['id']}: não promete e fecha ao mesmo tempo")


if __name__ == "__main__":
    unittest.main()
