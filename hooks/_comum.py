"""Forge: base comum dos hooks do plugin (ADR 0003).

Silenciosos (sem saída quando tudo está certo), determinísticos (só estado em disco e git local),
só agem em projeto com `.forge/versao` e liberam em erro interno (registrado em `.forge/run/erros.log`).
Exceção (ADR 0009, seção 7): `parecer` e `conformidade` falham fechado, de forma seletiva: em erro interno
bloqueiam só se a entrada crua tiver um marcador crítico. Só biblioteca padrão; nada vindo da entrada é executado.
"""
import functools
import importlib.machinery
import importlib.util
import json
import os
import re
import shlex
import sys
import time
from contextlib import contextmanager
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LIMITE_MENSAGEM = 200
LIMITE_LOG = 256 * 1024
# Usados só se o modelo do projeto (templates/projeto/.forge/config.json) não puder ser lido.
RESERVA = {"teto_agentes": 3, "pesados": []}  # a lista padrão vem da stack (forge-init)
INTEGRACAO = {"main", "master", "develop", "homolog"}
SEPARADORES = set("();|&\n")
REDIRECIONAMENTO = set("<>")


def raiz_do_projeto(inicio):
    """Raiz da cópia de trabalho que contém `inicio`, se for projeto do Forge (tem `.forge/versao`); senão None.
    Só consulta o disco: nada de git no caminho comum."""
    inicio = Path(inicio)
    for d in (inicio, *inicio.parents):
        if (d / ".git").exists():
            return d if (d / ".forge" / "versao").is_file() else None
    return None


def e_projeto(raiz):
    """A raiz (ou a cópia de trabalho que a contém) tem `.forge/versao`: é projeto, e nunca o Forge (R-CONTRIB)."""
    raiz = Path(raiz)
    return (raiz / ".forge" / "versao").is_file() or raiz_do_projeto(raiz) is not None


def tem_manifesto_do_forge(raiz):
    """A raiz tem `.claude-plugin/plugin.json` de nome `forge`. Sozinho não prova nada (o projeto pode escrever o
    arquivo): serve para PROTEGER mais (caminhos `so_forge`, alvo do Forge), nunca para dar poder."""
    try:
        dados = json.loads((Path(raiz) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        return isinstance(dados, dict) and dados.get("name") == "forge"
    except (OSError, ValueError):
        return False


def e_clone_do_forge(raiz):
    """A raiz é um clone do próprio Forge: tem o manifesto do Forge e não é projeto (sem `.forge/versao`). O projeto
    vem antes do Forge, então escrever o manifesto num projeto não o torna o Forge (R-CONTRIB)."""
    return raiz is not None and not e_projeto(raiz) and tem_manifesto_do_forge(raiz)


def raiz_declarada():
    """`CLAUDE_PROJECT_DIR`: a raiz da sessão, que o Claude Code define no processo do hook (também para os
    subagentes). O Bash roda em outro processo: `export` ou `VAR=...` na linha de comando não a mudam."""
    raiz = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(raiz) if raiz and Path(raiz).is_absolute() else None


def contrib():
    """`~/.forge-contrib`, onde o projeto trabalha o Forge (clone e worktrees)."""
    return Path(os.path.realpath(Path.home() / ".forge-contrib"))


def em_contrib(pasta):
    alvo = Path(os.path.realpath(pasta))
    return contrib() in (alvo, *alvo.parents)


def sessao_vigiada(hook):
    """Os hooks que falham fechado agem nesta sessão? A mesma decisão de `identificar_sessao` (conformidade), pela
    raiz da sessão e não pela pasta corrente: raiz em projeto, em qualquer pasta; raiz no Forge, só dentro de um
    projeto; sem raiz, num projeto ou em `~/.forge-contrib`. Se nem isso der para decidir, vigia (falha fechado)."""
    try:
        cwd, raiz = hook.cwd(), raiz_declarada()
        if raiz is not None and e_projeto(raiz):
            return True
        if raiz_do_projeto(cwd) is not None:
            return True
        return not e_clone_do_forge(raiz) and em_contrib(cwd)
    except Exception:  # noqa: BLE001 - na dúvida, a ação crítica fica barrada (ADR 0009, seção 7)
        return True


def git(raiz, *args):
    """O git do forge-check (sem GIT_* herdadas, com limite de tempo): uma função só para hooks e validador."""
    return forge_check().git(raiz, *args)


def segmentos(comando):
    """Divide a linha do shell em comandos simples (listas de palavras), sem executar nada.
    Aspas desbalanceadas levantam ValueError (o próprio shell vai recusar o comando)."""
    lex = shlex.shlex(comando, posix=True, punctuation_chars="();<>|&\n")
    lex.whitespace, lex.whitespace_split = " \t\r", True
    atual, pular = [], False
    for tok in lex:
        if tok and set(tok) <= SEPARADORES:
            yield atual
            atual = []
        elif tok and set(tok) <= REDIRECIONAMENTO:
            pular = True
        elif pular:
            pular = False
        else:
            atual.append(tok)
    yield atual


def comandos(comando):
    """Como `segmentos`, mas devolve (palavras, destinos) por comando simples: `destinos` são os alvos dos
    redirecionamentos de saída (`>`, `>>`, `&>`, `>|`, `2>`); `>&1` e `>&-` não são arquivos."""
    lex = shlex.shlex(comando, posix=True, punctuation_chars="();<>|&\n")
    lex.whitespace, lex.whitespace_split = " \t\r", True
    atual, destinos, modo = [], [], None  # modo: None | "saida" | "entrada"
    for tok in lex:
        if tok and set(tok) <= SEPARADORES:
            yield atual, destinos
            atual, destinos, modo = [], [], None
        elif tok and set(tok) <= REDIRECIONAMENTO | set("|&") and set(tok) & REDIRECIONAMENTO:
            modo = "saida" if ">" in tok else "entrada"
        elif modo:
            if modo == "saida" and not re.fullmatch(r"\d+|-", tok):
                destinos.append(tok)
            modo = None
        else:
            atual.append(tok)
    yield atual, destinos


def sem_atribuicoes(palavras):
    """Tira as atribuições de variáveis do início de um comando simples (`A=1 B=2 git ...`)."""
    i = 0
    while i < len(palavras) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", palavras[i]):
        i += 1
    return palavras[i:]


@functools.lru_cache(maxsize=1)
def forge_check():
    """Carrega bin/forge-check como módulo, para reaproveitar a validação (ADR 0004) sem duplicá-la."""
    caminho = str(PLUGIN / "bin" / "forge-check")
    carregador = importlib.machinery.SourceFileLoader("forge_check", caminho)
    spec = importlib.util.spec_from_loader("forge_check", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


def ler_json(caminho, padrao):
    if not caminho.exists():
        return padrao
    return json.loads(caminho.read_text(encoding="utf-8"))


def gravar_json(caminho, dados):
    tmp = caminho.with_name(caminho.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, caminho)


def mensagem(rid, texto):
    """Uma linha com o ID da regra, até LIMITE_MENSAGEM caracteres."""
    linha = " ".join(f"{rid}: {texto}".split())
    return linha if len(linha) <= LIMITE_MENSAGEM else linha[: LIMITE_MENSAGEM - 1] + "…"


def bloquear(rid, texto):
    """Saída 2: o Claude Code bloqueia a ferramenta (PreToolUse) ou mostra o motivo (PostToolUse)."""
    print(mensagem(rid, texto), file=sys.stderr)
    sys.exit(2)


def separar_regra(violacao, padrao):
    """'arquivo: campo: problema (R-X)' -> ('R-X', 'arquivo: campo: problema')."""
    m = re.search(r"\s*\((R-[A-Z][A-Z0-9-]*|ADR-\d+)\)$", violacao)
    return (m.group(1), violacao[: m.start()]) if m else (padrao, violacao)


def nome_da_branch(ref):
    """'origin/feature/x' ou 'refs/heads/feature/x' -> 'feature/x'."""
    for prefixo in ("refs/heads/", "refs/remotes/", "origin/", "upstream/"):
        if ref.startswith(prefixo):
            ref = ref[len(prefixo):]
            if prefixo == "refs/remotes/" and "/" in ref:
                ref = ref.split("/", 1)[1]
    return ref


class Hook:
    def __init__(self, nome):
        self.nome = nome
        self.entrada = {}
        self.raiz = None
        self._config = None
        self._run = None

    # Entrada -------------------------------------------------------------------------------
    def campo(self, *chaves):
        valor = self.entrada
        for c in chaves:
            valor = valor.get(c) if isinstance(valor, dict) else None
        return valor

    def cwd(self):
        cwd = self.entrada.get("cwd")
        return Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()

    # Projeto e configuração ------------------------------------------------------------------
    def projeto(self, inicio):
        """Raiz do projeto do Forge que contém `inicio`, ou None (projeto alheio ou hook desligado na config)."""
        self.raiz, self._config, self._run = raiz_do_projeto(inicio), None, None
        if self.raiz is None or self.nome in self.config()["hooks_desligados"]:
            return None
        return self.raiz

    def config(self):
        """Limites do projeto (`.forge/config.json`); o que faltar vem do modelo do Forge."""
        if self._config is not None:
            return self._config
        try:
            base = json.loads((PLUGIN / "templates/projeto/.forge/config.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            base = RESERVA
        projeto = ler_json(self.raiz / ".forge" / "config.json", {})
        if not isinstance(projeto, dict):
            raise ValueError(".forge/config.json não é um objeto JSON")

        def valor(chave, valido, padrao):
            for fonte in (projeto, base):
                if chave in fonte and valido(fonte[chave]):
                    return fonte[chave]
            return padrao

        def inteiro(v):
            return isinstance(v, int) and not isinstance(v, bool) and v >= 1

        def numero(v):
            return isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0

        def lista(v):
            return isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v)

        self._config = {
            "teto_agentes": valor("teto_agentes", inteiro, None),  # None: teto adaptativo (R-TETO)
            "teto_maximo": valor("teto_maximo", inteiro, None),
            "pesados": valor("pesados", lista, RESERVA["pesados"]),
            "expiracao_horas": valor("expiracao_horas", numero, 2),
            "hooks_desligados": valor("hooks_desligados", lista, []),
        }
        return self._config

    def expira_s(self):
        return self.config()["expiracao_horas"] * 3600

    # Estado em .forge/run/ da cópia principal ------------------------------------------------
    def run(self):
        """`.forge/run/` da cópia de trabalho principal (as worktrees somam no mesmo estado)."""
        if self._run is None:
            principal = self.raiz
            cod, comum = git(self.raiz, "rev-parse", "--git-common-dir")
            if not cod and comum:
                comum = (self.raiz / comum).resolve()
                if comum.name == ".git":
                    principal = comum.parent
            run = principal / ".forge" / "run"
            run.mkdir(parents=True, exist_ok=True)
            ignorar = run / ".gitignore"
            if not ignorar.exists():
                ignorar.write_text("*\n", encoding="utf-8")
            self._run = run
        return self._run

    @contextmanager
    def trava(self):
        """Exclusão mútua entre hooks simultâneos (sessões e worktrees) ao ler e gravar o estado."""
        with open(self.run() / ".trava", "a", encoding="utf-8") as f:
            try:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX)
            except ImportError:  # sem fcntl (Windows nativo): segue sem trava
                pass
            yield

    def registrar_erro(self, erro):
        """Falha interna não bloqueia (ADR 0003, item 4): registra numa linha e libera."""
        try:
            raiz = self.raiz or raiz_do_projeto(self.cwd())
            if raiz is None:
                return
            self.raiz = raiz
            try:
                pasta = self._run or self.run()
            except Exception:  # noqa: BLE001 - sem git: grava ao lado do projeto
                pasta = raiz / ".forge" / "run"
                pasta.mkdir(parents=True, exist_ok=True)
            log = pasta / "erros.log"
            if log.exists() and log.stat().st_size > LIMITE_LOG:
                os.replace(log, pasta / "erros.log.1")
            linha = " ".join(f"{type(erro).__name__}: {erro}".split())[:300]
            with open(log, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {self.nome} {linha}\n")
        except Exception:  # noqa: BLE001 - registrar o erro nunca pode bloquear a ferramenta
            pass


def texto_da_acao(hook, bruto):
    """O que a ação tem de crítico: o comando do Bash e o caminho do arquivo, nunca o conteúdo gravado (`content`,
    `new_string`...). Se o JSON não abriu, só resta a entrada crua."""
    entrada = hook.campo("tool_input")
    if not hook.entrada:
        return bruto
    if not isinstance(entrada, dict):
        return ""
    return "\n".join(v for k in ("command", "file_path", "notebook_path") if isinstance(v := entrada.get(k), str))


def falhar_fechado(hook, critico, bruto):
    """ADR 0009, seção 7: em erro interno, bloqueia só se o comando ou o caminho da ação tem marcador crítico e o
    a sessão é vigiada (`sessao_vigiada`: pela raiz da sessão, não pela pasta corrente), e nunca depois da
    ferramenta, quando já não há o que impedir."""
    if (critico is None or hook.entrada.get("hook_event_name") == "PostToolUse"
            or not critico.search(texto_da_acao(hook, bruto)) or not sessao_vigiada(hook)):
        return
    bloquear("R-CONFORMIDADE", f"erro interno do hook {hook.nome} diante de uma ação crítica; ele não pôde "
                               "decidir. Corrigir: veja .forge/run/erros.log e leve ao usuário (R-DECISAO)")


def executar(nome, funcao, critico=None):
    """Lê o JSON do stdin, chama `funcao(hook)` e sai com 0; `bloquear` sai com 2. `critico` (regex) liga a falha
    fechada seletiva; `FORGE_GUARDA_ABERTA=1` no ambiente do processo (só o dono) abre a guarda desses hooks."""
    hook = Hook(nome)
    bruto = sys.stdin.read()
    if critico is not None and os.environ.get("FORGE_GUARDA_ABERTA") == "1":
        sys.exit(0)
    try:
        entrada = json.loads(bruto or "{}")
        if isinstance(entrada, dict):
            hook.entrada = entrada
            funcao(hook)
    except Exception as erro:  # noqa: BLE001 - ADR 0003: erro interno libera e fica no erros.log
        hook.registrar_erro(erro)
        falhar_fechado(hook, critico, bruto)
    sys.exit(0)
