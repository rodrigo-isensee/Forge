"""Forge: base comum dos hooks do plugin (ADR 0003).

Silenciosos (sem saída quando tudo está certo), determinísticos (só estado em disco e git local),
só agem em projeto com `.forge/versao` e liberam em erro interno (registrado em `.forge/run/erros.log`).
Só biblioteca padrão; nada vindo da entrada é executado.
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LIMITE_MENSAGEM = 200
LIMITE_LOG = 256 * 1024
# Usados só se o modelo do projeto (templates/projeto/.forge/config.json) não puder ser lido.
RESERVA = {"teto_agentes": 3, "pesados": ["playwright", "docker compose up"]}
INTEGRACAO = {"main", "master", "develop", "homolog"}


def raiz_do_projeto(inicio):
    """Raiz da cópia de trabalho que contém `inicio`, se for projeto do Forge (tem `.forge/versao`); senão None.
    Só consulta o disco: nada de git no caminho comum."""
    inicio = Path(inicio)
    for d in (inicio, *inicio.parents):
        if (d / ".git").exists():
            return d if (d / ".forge" / "versao").is_file() else None
    return None


def git(raiz, *args):
    """Roda git na raiz sem as variáveis GIT_* herdadas. Devolve (código, stdout sem espaços nas pontas)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, env=env, timeout=5)
    return r.returncode, r.stdout.strip()


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
            "teto_agentes": valor("teto_agentes", inteiro, RESERVA["teto_agentes"]),
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


def executar(nome, funcao):
    """Lê o JSON do stdin, chama `funcao(hook)` e sai com 0; `bloquear` sai com 2."""
    hook = Hook(nome)
    try:
        entrada = json.loads(sys.stdin.read() or "{}")
        if isinstance(entrada, dict):
            hook.entrada = entrada
            funcao(hook)
    except Exception as erro:  # noqa: BLE001 - ADR 0003: erro interno libera e fica no erros.log
        hook.registrar_erro(erro)
    sys.exit(0)
