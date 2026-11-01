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
              `conformidade` pede confirmação, `permissionDecision: ask` no stdout, código 0), stderr (trecho), stderr_sem ([trechos] que a recusa não pode ter), estado {arquivo: {contem: [...], ausente: [...]}}, sem_arquivo [...],
              sem_run (true: .forge/run/ não foi criado), erros_log (trecho)
              sem_caminho ([caminho]: não existem; {tmp} vale)
"""
import concurrent.futures
import contextlib
import errno
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


def _cpu_dos_filhos():
    """Segundos de CPU (usuário + sistema) dos filhos já encerrados; None onde não há `resource`."""
    try:
        import resource
    except ImportError:
        return None
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


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
    """O que o `segmento` relê de um comando simples: a palavra com substituição entre aspas e o `bash -c`/`eval`, em cada
    leitura possível do lançador (`separar_lancadores`: a recusa é a união delas, RET-LEITURA-HOOK-G)."""
    _, conformidade, _ = modulos_dos_hooks()
    while palavras and palavras[0] in conformidade.CORPO_DE_LACO:
        palavras = palavras[1:]
    atribuicoes = palavras[:len(palavras) - len(conformidade.sem_atribuicoes(palavras))]
    try:
        possiveis = conformidade.separar_lancadores(palavras)
    except ValueError:
        return []  # texto dividido com aspas abertas, ou palavras demais fora da tabela: o hook só dá o R-CONTRIB para o Forge
    lidos = []
    for palavras, lancadas in possiveis:
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
def nucleos_do_processo():
    """Os núcleos do processo, pela afinidade (respeita cpuset) com recuo para `os.cpu_count()`; `None` se não der.
    Não lê `FORGE_NPROC`: essa variável é dos fixtures e não dimensiona o portão (N-CI, C-1)."""
    try:
        return len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
    except OSError:
        return None


def trabalhadores_do_pool(nucleos):
    """As threads dos pools de testes: cada uma espera um subprocesso (não usa CPU), então o número acompanha os
    núcleos, entre 2 e 4 (`R-TETO`); `None`, zero, negativo ou valor inválido dão 2 (N-CI, C-1)."""
    if not isinstance(nucleos, int) or isinstance(nucleos, bool) or nucleos < 1:
        return 2
    return min(4, max(2, nucleos))


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
        # O fixture com `executaveis` grava e dá `chmod` num programa que o hook roda: ele é montado antes do pool, na
        # thread principal, porque o executável gravado enquanto outra thread faz `fork` sai com `ETXTBSY` (o mesmo
        # defeito do T9b, bug `lote-leitura-hook-1`).
        montados = {}
        for nome, f in em_paralelo:
            if f.dados.get("executaveis"):
                tmp = self._pasta_temporaria()
                montados[nome] = (tmp, f.montar(tmp, outro.pid))
        trabalhadores = trabalhadores_do_pool(nucleos_do_processo())
        with concurrent.futures.ThreadPoolExecutor(max_workers=trabalhadores) as pool:
            futuros = []
            for nome, f in em_paralelo:
                tmp, montado = montados.get(nome, (self._pasta_temporaria(), None))
                futuros.append((nome, pool.submit(self.executar_fixture, f, tmp, outro.pid, montado)))
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

    def executar_fixture(self, f, tmp, outro_pid, montado=None):
        """Monta (ou recebe montado: (raiz, entrada) de `Fixture.montar`) e roda o fixture, conferindo o esperado."""
        raiz, entrada = montado or f.montar(tmp, outro_pid)
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
            for trecho in esperado.get("stderr_sem", []):
                self.assertNotIn(trecho, linha)
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

    def test_apoio_pathlib_312_faz_o_caminho_longo_demais_levantar(self):
        """Pré-condição dos testes de falha fechada: com `tests/apoio_pathlib_312` no PYTHONPATH, `Path.exists` levanta o
        ENAMETOOLONG em toda versão do Python (a 3.14 o engole). Sem isso, os testes de erro interno do hook falhariam
        com `esperado 2, veio 0` e sem pista; aqui a falha aponta o apoio (HOOKS-FALHA-FECHADA-SANDBOX)."""
        codigo = ("import pathlib\n"
                  "try:\n    pathlib.Path('/' + 'a' * 300).exists()\n"
                  "except OSError as erro:\n    print(erro.errno)\n"
                  "else:\n    print('engoliu')\n")
        env = ambiente_limpo()
        env["PYTHONPATH"] = str(PATHLIB_312)
        r = subprocess.run([sys.executable, "-c", codigo], env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.stdout.strip(), str(errno.ENAMETOOLONG), r.stderr)

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

    def test_marca_do_heredoc_e_palavra_comum_entre_espacos(self):  # heredoc-rapido, passo 2, C-2
        """Na linha que o `tirar_heredocs` lê para achar os donos, cada operador vira a marca dele cercada de espaço,
        uma palavra comum (sem `=`, sem dígito ou `-` no começo, fora de `COMPOSTOS`), e só elas casam com `MARCAS`."""
        _comum, _, _ = modulos_dos_hooks()
        linha = "cat<<'A'|bash\na\nA\nx=$(cat <<B\nb\nB\n)"
        with mock.patch.object(_comum, "leituras", wraps=_comum.leituras) as lidas:
            _comum.tirar_heredocs(linha)
        marcada = lidas.call_args_list[0].args[0]
        for operador in (3, linha.index("<<B")):
            with self.subTest(operador=operador):
                self.assertIn(f" {_comum.marca(operador)} ", marcada)
                self.assertRegex(_comum.marca(operador), r"^[A-Za-z_][A-Za-z0-9_]*$")
                self.assertNotIn(_comum.marca(operador), _comum.COMPOSTOS)
        self.assertEqual(len(_comum.MARCAS.findall(marcada)), 2)

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
        corpos = "".join(f"x\nE{i}\n" for i in range(n))
        # C-7 do heredoc-rapido, passo 2: também o heredoc numa substituição (6004 palavras: recusa pelo teto, depois
        # de ler a linha marcada) e o `|`
        for forma, texto, recusa in (("um por linha", "".join(f"cat > f{i} <<'EOF'\nx\nEOF\n" for i in range(n)), None),
                                     ("&&", " && ".join(f"cat > f{i} <<'E{i}'" for i in range(n)) + "\n" + corpos, None),
                                     ("x=$(", "".join(f"x=$(cat <<'E'\nx\nE\n)\n" for i in range(n)),
                                      "R-CONFORMIDADE: chamada com ação crítica e 6004 palavras"),
                                     ("|", " | ".join(f"cat <<'E{i}'" for i in range(n)) + "\n" + corpos, None)):
            with self.subTest(forma=forma):
                caso = json.loads(json.dumps(dados))
                caso["entrada"]["tool_input"]["command"] = texto + "git push origin main"
                caso["esperado"]["stderr"] = recusa or caso["esperado"]["stderr"]
                tmp = self._pasta_temporaria()
                arquivo = tmp / "conformidade" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(caso), encoding="utf-8")
                fixture = Fixture(arquivo)
                montado = fixture.montar(tmp, os.getpid())  # a montagem (git init, commit...) fica fora da janela medida
                cpu_antes = _cpu_dos_filhos()
                inicio = time.monotonic()
                self.executar_fixture(fixture, tmp, os.getpid(), montado=montado)
                parede = time.monotonic() - inicio
                cpu = None if cpu_antes is None else _cpu_dos_filhos() - cpu_antes
                self.assertLess(parede, limite / 2, "a decisão sai bem antes do Claude Code matar o hook")
                if cpu is not None:  # sem `resource` (Windows) só vale a parede
                    self.assertLess(cpu, limite / 2, "o custo de CPU do hook (filhos) fica no mesmo teto, sem depender da carga")

    def test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao(self):  # HEREDOC-RAPIDO, E1.1 (desenho, seção c)
        """Os N destinos de uma decisão (uma `Guarda`) leem o manifesto e resolvem a raiz e o home uma vez; outra
        decisão (outra `Guarda`) calcula de novo, sem cache entre elas."""
        _, conformidade, _ = modulos_dos_hooks()
        hook = mock.Mock(raiz=RAIZ)
        manifestos, homes = [], []
        def manifesto(raiz):
            manifestos.append(raiz)
            return True
        def home():
            homes.append(1)
            return Path(os.path.expanduser("~"))
        with mock.patch.object(conformidade, "tem_manifesto_do_forge", manifesto), \
                mock.patch.object(conformidade.Path, "home", staticmethod(home)):
            for _ in range(4):
                guarda = conformidade.Guarda(hook, conformidade.politica(), "dev")
                for i in range(50):
                    guarda.caminho_barrado(RAIZ / f"f{i}")
        self.assertEqual((len(manifestos), len(homes)), (4, 4), "uma leitura e um home por Guarda, não por destino")
        self.assertEqual({str(m) for m in manifestos}, {str(RAIZ)})

    def corpus_de_recusas(self):
        """As linhas das fixtures de recusa de Bash (código 2) dos hooks que leem a linha, menos as que o bash não aceita
        (`bash -n`: a variante cairia dentro de uma aspa aberta) e as recusas por erro interno (`erros_log`)."""
        if not _CORPUS:
            todas = [f for f in self.fixtures if f.hook in ("conformidade", "parecer", "pesado")
                     and f.dados["esperado"].get("codigo") == 2 and f.dados["entrada"].get("tool_name") == "Bash"
                     and f.caminho.stem != FIXTURE_DE_ORCAMENTO]  # a linha adversária de tempo recusa pelo teto, não pelo corpus
            fora = [f.caminho.stem for f in todas if "erros_log" in f.dados["esperado"]
                    or not bash_aceita(f.dados["entrada"]["tool_input"]["command"])]
            # 10: as duas sondas de extglob do PN7-DOLAR-INTERROG; o `bash -n` não roda o `shopt -s extglob` da 1ª linha
            self.assertLessEqual(len(fora), 10, fora)
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

    def test_t6_a_leitura_ve_a_acao_sem_marcador_com_cada_variante(self):  # FURO-HOOK-A, A1 TESTE-MATRIZ-CRITICO
        """T6, pelo hook real: a ação sem marcador `CRITICO` (que a rede da ADR 0011 não recusa) com cada variante que o
        bash ignora sai 2 sem o motivo da rede ("o hook não modela", `nao_modelada`): a recusa vem da leitura, que viu a ação
        ou a deu por ilegível. O `parecer` entra com o merge reprovado, que a rede dele também cobriria. Nenhum caso sai da
        matriz: uma lista de pendentes afrouxaria o controle e precisa do dono."""
        _comum, conformidade, _ = modulos_dos_hooks()
        self.assertLessEqual(set(MECANISMOS_DO_COMENTARIO.values()), set(VARIANTES_QUE_O_BASH_IGNORA))
        por_comando = {f.dados["entrada"]["tool_input"].get("command"): f for f in self.fixtures
                       if f"{f.hook}/{f.caminho.stem}" in FAMILIAS_DE_RECUSA}
        sem_marcador = [a for a, hook in ACOES_DO_CORPUS.items() if hook == "conformidade" and not conformidade.CRITICO.search(a)]
        self.assertGreaterEqual(len(sem_marcador), 2, sem_marcador)
        merge = "gh pr merge feature/x --repo rodrigo-isensee/Forge --merge"
        acoes = [(a, por_comando[a]) for a in sem_marcador + [merge]]
        casos = []
        for acao, modelo in acoes:
            for i, (prefixo, sufixo) in enumerate(VARIANTES_QUE_O_BASH_IGNORA):
                f = Fixture(modelo.caminho)
                f.dados["entrada"]["tool_input"]["command"] = prefixo + acao + sufixo
                rede = "com ação crítica: o hook não modela" if modelo.hook == "conformidade" else "o hook não modela"
                f.dados["esperado"] = {"codigo": 2, "stderr": "R-", "stderr_sem": [rede]}  # `R-` vale: ilegível também recusa
                casos.append((f"{modelo.hook}/{modelo.caminho.stem} + variante {i}", f))
        self.assertEqual(self.executar_em_lote(casos), len(acoes) * len(VARIANTES_QUE_O_BASH_IGNORA))

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

    def test_fixtures_do_lote_furo_hook_a(self):  # FURO-HOOK-A: só as fixtures do lote (a descrição abre com o nome), para a mutação
        lote = [(f"{f.hook}/{f.caminho.stem}", f) for f in self.fixtures if f.dados.get("descricao", "").startswith("FURO-HOOK-A")]
        self.assertGreaterEqual(len(lote), 8, "as fixtures do lote")
        self.assertEqual(self.executar_em_lote(lote), len(lote))

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


class CodigoDeSaida(unittest.TestCase):  # PN7-DOLAR-INTERROG (ADR 0011, emenda H1-1)
    """O `$?` é construção modelada só entre aspas duplas: `$?` × posição na palavra × aspas × lugar × `IFS` posto de
    qualquer jeito. Entre aspas duplas passa sempre; fora de aspas, o `$?` é recusado, como todo outro `$`, nos lugares
    da propriedade, que o hook lê por terem marcador crítico; sem marcador crítico o hook lê como na base."""
    TOKENS = ("$?", "${?}", "$#", "$@", "$1", "$x", "$'r'", '$"r"', "$$?", "$?$x")
    POSICOES = ("{}", "rc={}", "a{}b", "{}x")
    ASPAS = {"fora": "{}", "duplas": '"{}"', "simples": "'{}'"}
    IFS = ("", "IFS=0; ", 'export I"FS"=0; ', "declare I'FS'=0; ", "export I\\FS=0; ", "printf -v IF\\S %s 0; ",
           'read -r I""FS < f; ', ". ./ifs.sh; ", "declare $(printf I)FS=0; ")
    LUGARES = ("echo {}", "printf %s {}", "echo {}; git push origin melhoria/x", "git push origin {}",
               "{} push origin main", "echo {} | sh", "echo {} > f", "printf -v {} x", "printf {} x", "x={}",
               "echo $(git push origin {})", "git push origin {}; echo ok", "git push origin $(true) echo {}",
               "git push origin $((0)) echo {}", "git push origin @(x)echo {}", "git push origin >& echo {}",
               "git push origin 2>& echo {}", "git push origin <& echo {}", "git push origin >| echo {}")

    def test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs(self):
        _comum, _, parecer = modulos_dos_hooks()
        vistos = 0
        for token, posicao, (aspas, molde), ifs, lugar in itertools.product(
                self.TOKENS, self.POSICOES, self.ASPAS.items(), self.IFS, self.LUGARES):
            if aspas == "simples" and "'" in token:
                continue  # `$'r'` não se escreve entre aspas simples
            comando = lugar.format(molde.format(posicao.format(token)))
            passa = aspas == "simples" or token == "$?" and aspas == "duplas"
            with self.subTest(comando=comando, ifs=ifs):
                vistos += 1
                linha = f"{ifs}git commit -F - <<'EOF'\nx\nEOF\n{comando}"
                self.assertEqual(_comum.construcao_nao_modelada(linha) is None, passa, linha)
                resto = f"{ifs}git commit -F - {_comum.OPERADOR_K}\n{comando}"
                da_gramatica = not any(s in resto for s in ("\\", "<", ">", "|", "("))
                self.assertEqual(isinstance(_comum.simples_da_gramatica(resto), list), passa and da_gramatica, resto)
                self.assertFalse(parecer.heredocs_simples(f"cat <<'EOF'\nx\nEOF\n{ifs}{comando}"))
        self.assertGreaterEqual(vistos, 5000)

    def test_codigo_fora_de_aspas_recusa_em_todo_lugar(self):
        """Fora de aspas o `$?` recusa também como argumento de `echo` (DECISÃO DO DONO 2026-10-30, "A"): a fronteira do
        comando simples não é plana no bash (`$(…)`, extglob `@(x)`, `>&`), e só as aspas duplas impedem a divisão. Vale
        no domínio de `construcao_nao_modelada`, que o hook só roda com marcador crítico; sem ele lê como na base."""
        _comum, _, _ = modulos_dos_hooks()
        for antes in ("", "git push origin x; ", "git push origin $(true) ", "shopt -s extglob nullglob\ngit push @(x)",
                      "git push origin >& ", "git push origin >| ", "IFS=0; git push origin <& "):
            for depois, passa in (("echo rc=$?", False), ('echo "rc=$?"', True), ("echo rc=\"$?\"", True)):
                with self.subTest(linha=antes + depois):
                    self.assertEqual(_comum.construcao_nao_modelada(antes + depois) is None, passa)
        k3 = f"git commit -m {_comum.PALAVRA_K3}\necho "
        self.assertIsInstance(_comum.simples_da_gramatica(k3 + '"rc=$?"'), list)
        self.assertIsInstance(_comum.simples_da_gramatica("git commit -m x\necho rc=$?"), str)
        self.assertIsInstance(_comum.simples_da_gramatica('git commit -m x\necho "$$?"'), str)

    def test_ifs_com_digito_divide_o_codigo_fora_de_aspas(self):
        """O motivo de valer só entre aspas: no bash, `x$?main` vira duas palavras com `IFS=1` e uma só entre aspas."""
        saida = subprocess.run(["bash", "-c", "IFS=1; false; printf '<%s>' x$?main; false; printf '<%s>' \"x$?main\""],
                               capture_output=True, text=True, check=False).stdout
        self.assertEqual(saida, "<x><main><x1main>")


class PoolDosFixtures(unittest.TestCase):
    """O pool de threads dos fixtures e do corpus: uma fonte só (N-CI, C-1), por subprocesso (espera, não CPU)."""

    def test_pool_por_nucleos_e_limites(self):  # AB-8
        for nucleos, esperado in ((1, 2), (2, 2), (4, 4), (16, 4), (None, 2), (0, 2), (-3, 2), ("x", 2)):
            with self.subTest(nucleos=nucleos):
                self.assertEqual(trabalhadores_do_pool(nucleos), esperado)

    def test_pool_le_a_afinidade_e_ignora_o_forge_nproc(self):  # AB-8
        with mock.patch.dict(os.environ, {"FORGE_NPROC": "64"}):
            with mock.patch.object(os, "sched_getaffinity", create=True, return_value={0, 1}), \
                    mock.patch.object(os, "cpu_count", return_value=16):
                self.assertEqual(trabalhadores_do_pool(nucleos_do_processo()), 2)
            with mock.patch.object(os, "sched_getaffinity", create=True, return_value={0, 1, 2, 3, 4, 5}):
                self.assertEqual(trabalhadores_do_pool(nucleos_do_processo()), 4)
            with mock.patch.object(os, "sched_getaffinity", create=True, side_effect=OSError), \
                    mock.patch.object(os, "cpu_count", return_value=8):
                self.assertEqual(trabalhadores_do_pool(nucleos_do_processo()), 2)  # sem leitura, o piso

    def test_pool_uma_fonte_so(self):  # C-1: nenhum módulo de teste refaz a conta `cpu_count // 2` do pool
        copias = []
        for arquivo in sorted(Path(__file__).resolve().parent.glob("*.py")):
            for n, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"cpu_count\(\) or 2\) // 2", linha):
                    copias.append(f"{arquivo.name}:{n}")
        self.assertEqual([c.split(":")[0] for c in copias], ["apoio_volta_unica.py"], copias)  # só o limite de CPU (C-3)


if __name__ == "__main__":
    unittest.main()
