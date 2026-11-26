"""Oráculo do critério de parada do FORGE-SEMPRE-ATUAL (v047, E6.3, diretriz 30). Escrito pelo QA, antes do código.

O que este arquivo é: o contrato executável de `docs/arquitetura/forge-sempre-atual.md` (requisitos RD1 a RD11, D30b,
seções 2 a 5 e 8, "Critério de parada") e da ADR 0017. Cada teste responde a uma obrigação nomeada na primeira linha do
docstring (RD<n>, D30b, SEG-<n>, S<n>, seção do desenho). Sem rede, sem modelo, sem tocar o `~/.claude` real: tudo roda
num HOME temporário, com dublês de `claude`, `git` (só o `ls-remote` do catálogo), `tmux`, `gh`, `kill` e `pkill` no PATH.

Interface que o oráculo assume (o núcleo da E6.4 e as entradas da E6.5 a cumprem; mudar qualquer item volta ao QA):
  - `bin/forge-sempre-atual --gatilho atalho|poststart [--projeto <pasta>] [--orcamento <segundos>]` (padrão 60); roda como
    a pessoa no terminal (recusa dentro do Claude, D30b). Não lê entrada, não pergunta, nunca lê variável de ambiente que
    mude o que faz (SEG-2): os dublês entram só pelo PATH e pelo HOME.
  - Estado em `~/.claude/plugins/data/forge-forge/forge/sempre-atual/`: `registro.log` (TSV: carimbo, gatilho, escopo,
    projeto, antes, depois, resultado) e `estado.json` (`bom`, `fixacao`, `aviso`, `adiamentos`). Chave de `bom`:
    `<escopo>|<projectPath>` (`user|` no escopo do usuário). Resultados: `em_dia`, `atualizado`, `adiado:<motivo>`,
    `falhou:<etapa>[:resumo]` (etapas `prazo`, `sem-claude`, `branch-padrao`, `modelo`), `voltou`, `volta-falhou`.
  - Catálogo lido de `known_marketplaces.json` em `forge.source.ref`; escopos de `claude plugin list --json`; url do
    `repository` do plugin.json do installPath ativo do escopo do usuário; alvo = maior tag `vX.Y.Z` (`git ls-remote`).
  - Atalho: `<installPath>/scripts/jarvis` chama `<installPath>/bin/forge-sempre-atual --gatilho atalho --projeto "$PWD"`
    (pasta do próprio script, nunca por `sort -V`), ignora o código de saída e só então abre o `claude`.
  - Trampolins em `~/.local/bin` (`jarvis`, `jarvis-forge`, `forge`) executam o installPath ativo de `installed_plugins.json`.
  - Aviso pendente: `estado.json` -> `aviso.texto`; o doutor o mostra uma vez no Stop.
Não coberto aqui, por exigir clone vigente e rede de verdade: o `jarvis-forge` (volta da vigente, `ocupacao()` movida, forge-dev),
o `forge atualizar` sem `marketplace remove` (E6.5) e a reconciliação do catálogo na partida da sessão (sem prova sem modelo).
Limite conhecido: a ocupação (S2) olha o `/proc` inteiro; rodado dentro de uma sessão do Claude com agentes vigentes na
mesma raiz de um escopo de usuário, o escopo pode sair adiado. Por isso os testes de "atualiza" usam escopo de projeto.

Rodar uma classe: python3 -m unittest tests.test_oraculo_sempre_atual.Ocupacao
"""
import ast
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao  # noqa: E402
from sem_claude_ancestral import comando  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-sempre-atual"
MODULO = RAIZ / "bin" / "forge_sempre_atual.py"
URL = "https://example.test/forge.git"
GIT_REAL = shutil.which("git") or "/usr/bin/git"
UTILITARIOS = ("bash", "sh", "env", "sleep", "cat", "ls", "mkdir", "rm", "cp", "mv", "ln", "chmod", "date", "sed", "grep",
               "awk", "head", "tail", "sort", "find", "timeout", "readlink", "realpath", "dirname", "basename", "tr", "wc", "id",
               "stat", "install", "flock", "mktemp", "ps", "pgrep", "uname", "touch", "tee", "true", "false", "test", "printf", "xargs",
               "cut", "uniq", "diff", "cmp", "rmdir", "whoami", "hostname", "tty", "nproc")
CLAUDE_FALSO = r'''#!@PY@
import hashlib, json, os, shutil, sys, time
from pathlib import Path
FAKE, HOME = Path("@FAKE@"), Path("@HOME@")
PLUG = HOME / ".claude" / "plugins"
args = sys.argv[1:]
if args[:1] == ["--dormir"]:
    time.sleep(600)
    sys.exit(0)
def ctl():
    return json.loads((FAKE / "ctl.json").read_text())
def seq(texto):
    with open(FAKE / "seq.log", "a") as f:
        f.write(f"{time.monotonic_ns()} {texto}\n")
def selar(p):
    f = FAKE / "selos.json"
    s = json.loads(f.read_text()) if f.is_file() else {}
    s[str(p)] = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    f.write_text(json.dumps(s))
def gravar(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=2))
    selar(p)
def instalado():
    return json.loads((PLUG / "installed_plugins.json").read_text())
with open(FAKE / "claude.log", "a") as f:
    f.write(json.dumps({"args": args, "cwd": os.getcwd(), "gh_token": "GH_TOKEN" in os.environ}) + "\n")
if args[:1] != ["plugin"]:
    seq("claude-abriu")
    sys.exit(0)
c = ctl()
if args[:3] == ["plugin", "list", "--json"]:
    if c.get("list_falha"):
        print("erro interno do claude falso", file=sys.stderr)
        sys.exit(1)
    saida = []
    for e in instalado()["plugins"].get("forge@forge", []):
        item = {"id": "forge@forge", "version": e["version"], "scope": e["scope"], "enabled": True, "installPath": e["installPath"],
                "installedAt": e["installedAt"], "lastUpdated": e["lastUpdated"]}
        if e.get("projectPath"):
            item["projectPath"] = e["projectPath"]
        saida.append(item)
    print(json.dumps(saida, indent=2))
    sys.exit(0)
if args[:2] == ["plugin", "list"]:
    print("forge@forge")
    sys.exit(0)
if args[:3] == ["plugin", "marketplace", "add"]:
    if not c["rede"]:
        print("fatal: unable to access (sem rede)", file=sys.stderr)
        sys.exit(1)
    url, _, tag = args[3].partition("#")
    if c.get("add_falha_para") == tag:
        print("add recusado pelo claude falso", file=sys.stderr)
        sys.exit(1)
    if c.get("add_demora"):
        (FAKE / "add.pid").write_text(str(os.getpid()))
        time.sleep(c["add_demora"])
    if c.get("add_sem_efeito"):
        sys.exit(0)
    fonte = {"source": "git", "url": url, "ref": tag}
    gravar(PLUG / "known_marketplaces.json", {"forge": {"source": fonte, "installLocation": str(PLUG / "marketplaces" / "forge"),
                                                         "lastUpdated": "2026-11-15T12:00:00.000Z"}})
    gravar(HOME / ".claude" / "settings.json", {"extraKnownMarketplaces": {"forge": {"source": fonte}}})
    print("Successfully added marketplace: forge")
    sys.exit(0)
if args[:2] == ["plugin", "update"]:
    escopo = args[args.index("--scope") + 1]
    if not c["rede"]:
        print("network error", file=sys.stderr)
        sys.exit(1)
    ref = json.loads((PLUG / "known_marketplaces.json").read_text())["forge"]["source"].get("ref", "")
    versao = ref[1:] if ref.startswith("v") else ref
    inst = instalado()
    alvo = None
    for e in inst["plugins"].get("forge@forge", []):
        if e["scope"] != escopo:
            continue
        if escopo != "user" and os.path.realpath(e.get("projectPath", "")) != os.path.realpath(os.getcwd()):
            continue
        alvo = e
    if alvo is None or not versao:
        print("Plugin forge@forge is not installed at this scope", file=sys.stderr)
        sys.exit(1)
    dest = PLUG / "cache" / "forge" / "forge" / versao
    if not dest.exists():
        origem = FAKE / "publicadas" / versao
        if not origem.exists():
            print("versao nao publicada", file=sys.stderr)
            sys.exit(1)
        shutil.copytree(origem, dest)
    alvo["version"], alvo["installPath"], alvo["lastUpdated"] = versao, str(dest), "2026-11-15T13:00:00.000Z"
    gravar(PLUG / "installed_plugins.json", inst)
    print(f"Plugin forge updated to {versao} for scope {escopo}")
    sys.exit(0)
if args[:2] == ["plugin", "validate"]:
    alvo = Path(args[2])
    if not alvo.is_dir():
        print("File not found", file=sys.stderr)
        sys.exit(1)
    try:
        json.loads((alvo / ".claude-plugin" / "plugin.json").read_text())
    except (OSError, ValueError):
        print("Invalid JSON syntax", file=sys.stderr)
        sys.exit(1)
    if "--strict" in args and c.get("manifesto_com_aviso"):
        print("Validation failed (--strict treats warnings as errors)", file=sys.stderr)
        sys.exit(1)
    print("Validation passed")
    sys.exit(0)
if args[:3] == ["plugin", "marketplace", "remove"]:
    gravar(PLUG / "installed_plugins.json", {"version": 2, "plugins": {}})
    gravar(PLUG / "known_marketplaces.json", {})
    sys.exit(0)
sys.exit(0 if args[:3] == ["plugin", "marketplace", "update"] or args[:2] == ["plugin", "install"] else 2)
'''
GIT_FALSO = r'''#!@PY@
import json, os, sys
from pathlib import Path
FAKE = Path("@FAKE@")
argv = sys.argv[1:]
with open(FAKE / "git.log", "a") as f:
    f.write(json.dumps({"args": argv, "cwd": os.getcwd(), "gh_token": "GH_TOKEN" in os.environ}) + "\n")
if "push" in argv:
    print("git falso: envio recusado", file=sys.stderr)
    sys.exit(1)
if any("example.test" in a for a in argv):
    c = json.loads((FAKE / "ctl.json").read_text())
    if not c["rede"]:
        print("fatal: unable to access (sem rede)", file=sys.stderr)
        sys.exit(128)
    if "ls-remote" in argv and "--symref" in argv:
        print(f"ref: refs/heads/{c['branch_padrao']}\tHEAD\n{'a' * 40}\tHEAD")
        sys.exit(0)
    if "ls-remote" in argv:
        for tag in c["tags"]:
            print(f"{'b' * 40}\trefs/tags/{tag}")
        sys.exit(0)
    if "fetch" in argv:
        # a origem da tag: repositório bare local com a main e as tags publicadas (o protocolo https é só o nome dela)
        ori = str(FAKE / "origem.git")
        novo, pula = [], False
        for i, a in enumerate(argv):
            if pula:
                pula = False
            elif a == "-c" and argv[i + 1].startswith("protocol."):
                pula = True
            else:
                novo.append(ori if "example.test" in a else a)
        os.execv("@GIT@", ["@GIT@", "-c", "protocol.file.allow=always", *novo])
    print("git falso: so ls-remote do catalogo", file=sys.stderr)
    sys.exit(1)
os.execv("@GIT@", ["@GIT@", *argv])
'''
TMUX_FALSO = r'''#!@PY@
import json, os, subprocess, sys
from pathlib import Path
FAKE = Path("@FAKE@")
argv = sys.argv[1:]
with open(FAKE / "tmux.log", "a") as f:
    f.write(json.dumps({"args": argv, "cwd": os.getcwd()}) + "\n")
abertas = json.loads((FAKE / "ctl.json").read_text())["tmux"]
if argv[:1] == ["has-session"]:
    sys.exit(0 if argv[argv.index("-t") + 1] in abertas else 1)
if argv[:1] == ["new-session"]:
    nome = argv[argv.index("-s") + 1]
    if "-A" in argv and nome in abertas:
        sys.exit(0)  # já existe: só anexa
    pasta = argv[argv.index("-c") + 1] if "-c" in argv else os.getcwd()
    sys.exit(subprocess.run(["bash", "-c", argv[-1]], cwd=pasta, env={**os.environ, "TMUX": "/fake/tmux,1,0"}).returncode)
sys.exit(0)
'''
REGISTRADOR = r'''#!@PY@
import json, os, sys
with open("@FAKE@/@NOME@.log", "a") as f:
    f.write(json.dumps({"args": sys.argv[1:], "cwd": os.getcwd()}) + "\n")
if sys.argv[1:2] == ["--dormir"]:
    import time
    time.sleep(600)
sys.exit(0)
'''
STUB_DA_FERRAMENTA = r'''#!@PY@
import json, sys, time
with open("@FAKE@/ferramenta.log", "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
with open("@FAKE@/seq.log", "a") as f:
    f.write(f"{time.monotonic_ns()} ferramenta\n")
@COMPORTAMENTO@
'''


def ambiente_git():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="Oraculo", GIT_AUTHOR_EMAIL="o@exemplo.test", GIT_COMMITTER_NAME="Oraculo",
               GIT_COMMITTER_EMAIL="o@exemplo.test", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    return env


def git_real(*args, cwd, check=True):
    r = subprocess.run([GIT_REAL, *args], cwd=cwd, capture_output=True, text=True, env=ambiente_git(), timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {r.stderr}")
    return r.stdout.strip()


class Mundo(unittest.TestCase):
    """HOME temporário, dublês no PATH, catálogo fictício e projetos git locais. Nada sai da pasta temporária."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oraculo-sa-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home, self.fake, self.neutro = self.tmp / "home", self.tmp / "fake", self.tmp / "neutro"
        self.fbin, self.temp = self.fake / "bin", self.tmp / "t"
        self.proc = self.fake / "proc"  # os processos vivos do mundo do teste (a ferramenta lê daqui, não do /proc da máquina)
        for p in (self.home, self.fake, self.fbin, self.neutro, self.temp, self.fake / "publicadas", self.proc):
            p.mkdir(parents=True)
        self.plug = self.home / ".claude" / "plugins"
        self.cache = self.plug / "cache" / "forge" / "forge"
        self.estado_dir = self.plug / "data" / "forge-forge" / "forge" / "sempre-atual"
        self.ctl(rede=True, branch_padrao="main", tags=[], tmux=[])
        for nome, fonte in (("claude", CLAUDE_FALSO), ("git", GIT_FALSO), ("tmux", TMUX_FALSO)):
            self._script(self.fbin / nome, fonte)
        for nome in ("gh", "kill", "pkill", "killall", "shellcheck", "sudo", "forge-fechar"):
            self._script(self.fbin / nome, REGISTRADOR.replace("@NOME@", nome))
        os.symlink(sys.executable, self.fbin / "python3")
        for nome in UTILITARIOS:
            achado = shutil.which(nome)
            if achado and not (self.fbin / nome).exists():
                os.symlink(achado, self.fbin / nome)
        (self.home / ".gitconfig").write_text("[user]\n\tname = Oraculo\n\temail = o@exemplo.test\n[safe]\n\tdirectory = *\n")
        self.definir_ref("v0.0.0")
        self._gravar(self.plug / "installed_plugins.json", {"version": 2, "plugins": {}})
        self.origem = self.fake / "origem.git"
        self.origem_trab = self.fake / "origem-trab"
        git_real("init", "-q", "--bare", "-b", "main", str(self.origem), cwd=self.tmp)
        remoto_sem_manutencao(self.origem)
        git_real("init", "-q", "-b", "main", str(self.origem_trab), cwd=self.tmp)

    def outro(self):
        """Um mundo novo e vazio da mesma classe, para repetir o cenário em subTest sem herdar o estado do anterior."""
        m = type(self)(self._testMethodName)
        m.setUp()
        self.addCleanup(shutil.rmtree, m.tmp, ignore_errors=True)
        m._testMethodDoc = self._testMethodDoc
        return m

    # --- montagem ---------------------------------------------------------------------------------------------
    def _script(self, caminho, fonte):
        texto = fonte.replace("@PY@", sys.executable).replace("@FAKE@", str(self.fake)).replace("@HOME@", str(self.home))
        caminho.write_text(texto.replace("@GIT@", GIT_REAL), encoding="utf-8")
        caminho.chmod(0o755)

    def ctl(self, **mudancas):
        arq = self.fake / "ctl.json"
        atual = json.loads(arq.read_text()) if arq.is_file() else {}
        atual.update(mudancas)
        arq.write_text(json.dumps(atual))

    def _gravar(self, caminho, obj):
        """Grava como a CLI grava (e sela o conteúdo): a ferramenta nunca pode mudar estes arquivos."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        selos = self.fake / "selos.json"
        s = json.loads(selos.read_text()) if selos.is_file() else {}
        s[str(caminho)] = hashlib.sha256(caminho.read_bytes()).hexdigest()
        selos.write_text(json.dumps(s))

    def definir_ref(self, tag):
        fonte = {"source": "git", "url": URL, "ref": tag}
        self._gravar(self.plug / "known_marketplaces.json", {"forge": {"source": fonte, "installLocation": "x", "lastUpdated": "y"}})
        self._gravar(self.home / ".claude" / "settings.json", {"extraKnownMarketplaces": {"forge": {"source": fonte}}})

    def ref(self):
        return json.loads((self.plug / "known_marketplaces.json").read_text())["forge"]["source"].get("ref")

    def selos_alterados(self):
        """Arquivos da CLI cujo conteúdo difere do que a CLI (ou o preparo do teste) gravou por último."""
        selos = json.loads((self.fake / "selos.json").read_text())
        return [p for p, h in selos.items() if Path(p).is_file() and hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]

    def _construir(self, pasta, versao, py_quebrado=False, sh_quebrado=False, manifesto_ruim=False, doutor_problema=False,
                   upgrade_falha=False, repository=URL, isca=False):
        for sub in (".claude-plugin", "hooks", "bin", "scripts"):
            (pasta / sub).mkdir(parents=True, exist_ok=True)
        manifesto = "{ruim" if manifesto_ruim else json.dumps({"name": "forge", "version": versao, "repository": repository})
        (pasta / ".claude-plugin" / "plugin.json").write_text(manifesto, encoding="utf-8")
        (pasta / "hooks" / "ok.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (pasta / "bin" / "ok.py").write_text("X = 1\n", encoding="utf-8")
        if py_quebrado:
            (pasta / "hooks" / "quebrado.py").write_text("def (:\n", encoding="utf-8")
        log = f'echo "exec $0 $*" >> "{self.fake}/exec.log"'
        marca = f'echo "ISCA $0" >> "{self.fake}/exec.log"' if isca else log
        doutor = f"{marca}\n" + ('echo "- problema novo do oraculo"\nexit 1\n' if doutor_problema else "exit 0\n")
        upgrade = f"{marca}\n" + ("exit 1\n" if upgrade_falha else (
            f'cd "$1" || exit 1\ngit checkout -q -b forge/upgrade-{versao} || exit 1\nmkdir -p .forge\necho {versao} > .forge/versao\n'
            'git add -A\ngit commit -q -m "chore(forge): migracao"\n'))
        corpos = {"bin/forge-doutor": doutor, "bin/forge-upgrade": upgrade, "bin/forge": log + "\n",
                  "scripts/jarvis": log + "\n", "scripts/jarvis-forge": log + "\n", "scripts/preparar-estacao.sh": log + "\n"}
        for rel, corpo in corpos.items():
            arq = pasta / rel
            arq.write_text("#!/usr/bin/env bash\n" + corpo, encoding="utf-8")
            arq.chmod(0o755)
        if sh_quebrado:
            (pasta / "scripts" / "jarvis").write_text("#!/usr/bin/env bash\nif [ then\n", encoding="utf-8")

    def instalar(self, versao, escopo="user", projeto=None, **opcoes):
        """Versão instalada num escopo (e a pasta dela no cache)."""
        destino = self.cache / versao
        if not destino.exists():
            self._construir(destino, versao, **opcoes)
        arq = self.plug / "installed_plugins.json"
        dados = json.loads(arq.read_text())
        entrada = {"scope": escopo, "installPath": str(destino), "version": versao,
                   "installedAt": "2026-11-01T00:00:00.000Z", "lastUpdated": "2026-11-01T00:00:00.000Z"}
        if projeto:
            entrada["projectPath"] = str(projeto)
        dados["plugins"].setdefault("forge@forge", []).append(entrada)
        self._gravar(arq, dados)
        return destino

    def publicar(self, versao, **opcoes):
        """Versão publicada: tag vX.Y.Z no catálogo e a cópia que o `plugin update` traz para o cache."""
        self._construir(self.fake / "publicadas" / versao, versao, **opcoes)
        # a origem da tag: um commit na main do repositório bare local e a tag vX.Y.Z nele
        git_real("commit", "-q", "--allow-empty", "-m", f"release {versao}", cwd=self.origem_trab)
        git_real("tag", f"v{versao}", cwd=self.origem_trab)
        git_real("push", "-q", str(self.origem), "main", f"refs/tags/v{versao}", cwd=self.origem_trab)
        self.ctl(tags=[*json.loads((self.fake / "ctl.json").read_text())["tags"], f"v{versao}"])

    def projeto(self, nome, versao_modelo="0.45.2", isca=False):
        remoto = self.tmp / "remotos" / f"{nome}.git"
        remoto.parent.mkdir(exist_ok=True)
        git_real("init", "-q", "--bare", "-b", "main", str(remoto), cwd=self.tmp)
        remoto_sem_manutencao(remoto)  # o receive-pack local não herda GIT_CONFIG_* (ver ambiente_git.py)
        p = self.home / nome
        git_real("clone", "-q", str(remoto), str(p), cwd=self.tmp)
        (p / ".forge").mkdir()
        (p / ".forge" / "versao").write_text(versao_modelo + "\n")
        (p / ".gitignore").write_text(".forge/run/\n")
        (p / ".githooks").mkdir()
        (p / ".githooks" / "pre-push").write_text('#!/bin/sh\n[ "$1" = "--status" ] && exit 1\nexit 0\n')
        (p / ".githooks" / "pre-push").chmod(0o755)
        if isca:
            for rel in ("bin/forge-doutor", "bin/forge-upgrade", "scripts/preparar-estacao.sh", "scripts/jarvis", "bin/forge-sempre-atual"):
                (p / rel).parent.mkdir(exist_ok=True)
                (p / rel).write_text(f'#!/bin/sh\necho "ISCA work tree $0" >> "{self.fake}/exec.log"\nexit 0\n')
                (p / rel).chmod(0o755)
        git_real("add", "-A", cwd=p)
        git_real("commit", "-q", "-m", "inicio", cwd=p)
        git_real("push", "-q", "origin", "main", cwd=p)
        git_real("branch", "develop", cwd=p)
        git_real("push", "-q", "origin", "develop", cwd=p)
        return p

    def agentes(self, projeto, quantos):
        pasta = Path(projeto) / ".forge" / "run"
        pasta.mkdir(parents=True, exist_ok=True)
        registros = [{"id": "a" + f"{i:016x}", "desde": time.time()} for i in range(quantos)]
        (pasta / "agentes.json").write_text(json.dumps({"agentes": registros}))

    def semear_estado(self, **partes):
        self.estado_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        (self.estado_dir / "estado.json").write_text(json.dumps(partes))

    def bom(self, versao, escopo="user", projeto=""):
        return {f"{escopo}|{projeto}": {"versao": versao, "gitCommitSha": "0" * 40, "installPath": str(self.cache / versao),
                                        "data": "2026-11-01T00:00:00Z"}}

    def estado(self):
        arq = self.estado_dir / "estado.json"
        return json.loads(arq.read_text()) if arq.is_file() else {}

    def registro(self):
        arq = self.estado_dir / "registro.log"
        return [l.split("\t") for l in arq.read_text(encoding="utf-8").splitlines() if l.strip()] if arq.is_file() else []

    def resultados(self, escopo=None):
        return [c[6] for c in self.registro() if len(c) >= 7 and (escopo is None or c[2] == escopo)]

    def chamadas(self, arq="claude"):
        f = self.fake / f"{arq}.log"
        return [json.loads(l) for l in f.read_text().splitlines()] if f.is_file() else []

    def mutacoes(self):
        """Chamadas do `claude` que mudam catálogo ou instalação."""
        return [c for c in self.chamadas() if c["args"][:2] in (["plugin", "update"], ["plugin", "install"])
                or c["args"][:3] in (["plugin", "marketplace", "add"], ["plugin", "marketplace", "remove"],
                                     ["plugin", "marketplace", "update"])]

    def atualizacoes(self):
        return [c for c in self.chamadas() if c["args"][:2] == ["plugin", "update"]]

    def adds(self):
        return [c for c in self.chamadas() if c["args"][:3] == ["plugin", "marketplace", "add"]]

    def versoes(self):
        """{(escopo, projectPath): versão} lidas de installed_plugins.json."""
        dados = json.loads((self.plug / "installed_plugins.json").read_text())["plugins"].get("forge@forge", [])
        return {(e["scope"], e.get("projectPath", "")): e["version"] for e in dados}

    def execs(self):
        f = self.fake / "exec.log"
        return f.read_text().splitlines() if f.is_file() else []

    def upgrades(self):
        return [l for l in self.execs() if l.split()[1].endswith("/bin/forge-upgrade")]

    def eventos(self):
        f = self.fake / "seq.log"
        return [l.split()[1] for l in f.read_text().splitlines()] if f.is_file() else []

    def vivo(self, nome, cwd):
        """Processo vivo de nome `claude` ou `forge-fechar`, com a pasta dada (o que a ferramenta enxerga na árvore `self.proc`)."""
        p = subprocess.Popen([str(self.fbin / nome), "--dormir"], cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(lambda: (p.kill(), p.wait()))
        # O /proc da máquina não serve de fonte: no sandbox do Bash ele é de outro namespace de pid. O processo vivo (real, para
        # o teste provar que ninguém o derruba) entra na árvore do mundo do teste, que o lançador entrega à ferramenta.
        entrada = self.proc / str(p.pid)
        entrada.mkdir()
        (entrada / "comm").write_text(nome + "\n")
        (entrada / "cmdline").write_bytes(f"{nome}\0--dormir\0".encode())
        (entrada / "cwd").symlink_to(Path(cwd).resolve())
        return p

    def env(self, **extra):
        env = {"HOME": str(self.home), "PATH": str(self.fbin), "TMPDIR": str(self.temp), "LANG": "C.UTF-8"}
        env.update({k: v for k, v in ambiente_git().items() if k.startswith("GIT_")})
        env.update(extra)
        return env

    def exige(self):
        doc = (self._testMethodDoc or "").strip().splitlines()
        return doc[0] if doc else self._testMethodName

    def rodar(self, projeto=None, gatilho="atalho", orcamento=None, stdin=subprocess.DEVNULL, env=None, timeout=90, direto=False):
        """Roda a ferramenta como a pessoa no terminal. Falha dizendo o que falta se ela ainda não existe."""
        self.assertTrue(FERRAMENTA.is_file(), f"falta bin/forge-sempre-atual (E6.4); este oráculo exige: {self.exige()}")
        args = ["--gatilho", gatilho]
        if projeto:
            args += ["--projeto", str(projeto)]
        if orcamento is not None:
            args += ["--orcamento", str(orcamento)]
        cmd = [sys.executable, str(FERRAMENTA), *args] if direto else comando(FERRAMENTA, *args, ate=os.getpid(), proc=self.proc)
        try:
            return subprocess.run(cmd, cwd=projeto or self.neutro, env=env or self.env(), stdin=stdin, capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            self.fail(f"a ferramenta passou de {timeout} s e não terminou (RD5: nada para): {self.exige()}")

    def sem_traceback(self, r):
        self.assertNotIn("Traceback", r.stdout + r.stderr, "erro interno vazou como traceback; devia virar `falhou:<etapa>` no registro")
        self.assertLessEqual(len(r.stdout.strip().splitlines()), 1, f"no máximo uma linha no terminal: {r.stdout!r}")

    def cenario_atualiza(self, de="0.47.0", para="0.47.2"):
        """Projeto `p` com o plugin em `de` e `para` publicado: caso livre que deve atualizar. Devolve o projeto."""
        p = self.projeto("p")
        self.instalar(de, "project", p)
        self.publicar(de)
        self.publicar(para)
        self.definir_ref(f"v{de}")
        return p

    def atalho_instalado(self, comportamento="", ferramenta=True):
        """installPath ativo com o `scripts/jarvis` de verdade e um stub no lugar da ferramenta. Devolve (installPath, projeto)."""
        ativo = self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        shutil.copyfile(RAIZ / "scripts" / "jarvis", ativo / "scripts" / "jarvis")
        (ativo / "scripts" / "jarvis").chmod(0o755)
        (ativo / "bin" / "forge-doutor").write_text("#!/bin/sh\nexit 0\n")
        if ferramenta:
            self._script(ativo / "bin" / "forge-sempre-atual", STUB_DA_FERRAMENTA.replace("@COMPORTAMENTO@", comportamento))
        projeto = self.home / "proj"
        projeto.mkdir()
        return ativo, projeto

    def abrir_atalho(self, ativo, projeto, *args):
        return subprocess.run(["bash", str(ativo / "scripts" / "jarvis"), *args], cwd=projeto, env=self.env(),
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)

    def chamadas_do_stub(self):
        f = self.fake / "ferramenta.log"
        return [json.loads(l) for l in f.read_text().splitlines()] if f.is_file() else []


# ================================================================================================================
class Escopos(Mundo):
    def test_fixa_catalogo_na_maior_tag_e_atualiza_cada_escopo_livre(self):
        """RD2/RD3 · catálogo fixado na maior tag vX.Y.Z (comparação numérica) e um update por escopo que difere do alvo"""
        p1, p2, p3 = self.projeto("p1"), self.projeto("p2"), self.projeto("p3")
        self.instalar("0.9.0", "user")
        self.instalar("0.9.0", "project", p1)
        self.instalar("0.9.0", "local", p2)
        self.instalar("0.10.0", "project", p3)
        self.publicar("0.9.0")
        self.publicar("0.10.0")
        self.ctl(tags=["v0.9.0", "v0.10.0", "v9.9.9-rc1", "latest", "vfoo"])
        self.definir_ref("v0.9.0")
        r = self.rodar()
        self.assertEqual(self.ref(), "v0.10.0", f"alvo errado (0.10.0 é maior que 0.9.0; rc e nome solto não contam): {r.stderr}")
        self.assertEqual(set(self.versoes().values()), {"0.10.0"}, "todo escopo instalado devia estar na maior tag")
        self.assertEqual([c["args"] for c in self.adds()], [["plugin", "marketplace", "add", f"{URL}#v0.10.0", "--scope", "user"]])
        ups = {(c["args"][c["args"].index("--scope") + 1], os.path.realpath(c["cwd"])) for c in self.atualizacoes()}
        self.assertIn(("project", os.path.realpath(p1)), ups)
        self.assertIn(("local", os.path.realpath(p2)), ups)
        self.assertNotIn(("project", os.path.realpath(p3)), ups, "escopo já no alvo não leva update")
        ordem = [c["args"][1] for c in self.chamadas() if c["args"][:2] != ["plugin", "list"]]
        self.assertLess(ordem.index("marketplace"), ordem.index("update"), "o catálogo é fixado antes de qualquer update")

    def test_escopo_de_usuario_roda_em_pasta_neutra(self):
        """RD3 · add e update do escopo de usuário rodam em pasta neutra, fora de projeto e fora do work tree do Forge"""
        p = self.projeto("p")
        self.instalar("0.47.0", "user")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.rodar(projeto=p)
        chamadas = self.adds() + self.atualizacoes()
        self.assertTrue(chamadas, "nenhum add/update chamado")
        for c in chamadas:
            cwd = os.path.realpath(c["cwd"])
            self.assertFalse(cwd == os.path.realpath(p) or cwd.startswith(os.path.realpath(p) + os.sep), f"cwd dentro do projeto: {cwd}")
            self.assertFalse(cwd == str(RAIZ) or cwd.startswith(str(RAIZ) + os.sep), f"cwd no work tree do Forge: {cwd}")

    def test_projeto_ausente_e_pulado_e_registrado(self):
        """RD3 · escopo de projeto cuja pasta sumiu é pulado e registrado; os outros escopos seguem"""
        vivo = self.projeto("vivo")
        self.instalar("0.47.0", "project", vivo)
        self.instalar("0.47.0", "project", self.home / "sumiu")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.rodar()
        self.assertEqual(self.versoes()[("project", str(vivo))], "0.47.2")
        linhas = [c for c in self.registro() if len(c) >= 7 and "sumiu" in c[3]]
        self.assertTrue(linhas, "o projeto ausente não foi registrado")
        self.assertRegex(linhas[-1][6], r"^(pulado|falhou:|adiado:)", f"resultado do projeto ausente: {linhas[-1][6]}")

    def test_em_dia_nao_chama_nada_alem_da_leitura(self):
        """RD2 · fronteira: tudo no alvo e catálogo já fixado nele (caminho rápido): só `plugin list`, sem add nem update"""
        p = self.projeto("p")
        self.instalar("0.47.2", "project", p)
        self.publicar("0.47.2")
        self.definir_ref("v0.47.2")
        r = self.rodar(projeto=p)
        self.assertEqual(self.mutacoes(), [])
        self.assertEqual([c["args"][:2] for c in self.chamadas() if c["args"][:2] != ["plugin", "list"]], [],
                         "no caminho rápido o claude só lê a lista")
        self.assertIn("em_dia", self.resultados())
        self.sem_traceback(r)

    def test_branch_padrao_que_nao_e_main_nao_atualiza(self):
        """seção 2 · se `ls-remote --symref` não aponta refs/heads/main, nada é atualizado e o registro diz falhou:branch-padrao"""
        p = self.cenario_atualiza()
        self.ctl(branch_padrao="develop")
        r = self.rodar(projeto=p)
        self.assertEqual(self.atualizacoes(), [])
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertTrue(any(x.startswith("falhou:branch-padrao") for x in self.resultados()), self.resultados())
        self.sem_traceback(r)


class Abertura(Mundo):
    def test_sem_terminal_sem_pergunta_sem_ler_entrada(self):
        """RD1 · roda sem tty e com a entrada aberta e muda: não pergunta, não lê, não trava"""
        p = self.cenario_atualiza()
        self.assertTrue(FERRAMENTA.is_file(), f"falta bin/forge-sempre-atual (E6.4); este oráculo exige: {self.exige()}")
        cmd = comando(FERRAMENTA, "--gatilho", "atalho", "--projeto", p, ate=os.getpid(), proc=self.proc)
        proc = subprocess.Popen(cmd, cwd=p, env=self.env(),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.addCleanup(lambda: (proc.kill(), proc.wait()))
        try:
            saida, _ = proc.communicate(timeout=60)  # entrada nunca escrita nem fechada antes: quem ler trava
        except subprocess.TimeoutExpired:
            self.fail("a ferramenta ficou esperando entrada")
        self.assertNotIn("[s/N]", saida)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2", "atualiza sozinha, sem confirmação")

    def test_recusa_dentro_do_claude(self):
        """D30b · chamada de dentro do Claude é recusada (rc diferente de 0) sem tocar em nada"""
        p = self.cenario_atualiza()
        r = self.rodar(projeto=p, direto=True, env=self.env(CLAUDECODE="1", CLAUDE_CODE_ENTRYPOINT="cli"))
        self.assertNotEqual(r.returncode, 0, "devia recusar quando CLAUDECODE está no ambiente")
        self.assertEqual(self.mutacoes(), [])
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")

    def test_atalho_roda_a_ferramenta_uma_vez_antes_de_abrir_o_claude(self):
        """RD1 · o atalho chama a ferramenta do installPath com --gatilho atalho e --projeto, e só depois abre o claude"""
        ativo, projeto = self.atalho_instalado()
        self.abrir_atalho(ativo, projeto, "--sem-tmux")
        chamadas = self.chamadas_do_stub()
        self.assertEqual(len(chamadas), 1, f"a ferramenta devia rodar uma vez por abertura (rodou {len(chamadas)}: o atalho não a chama)")
        args = chamadas[0]
        self.assertEqual(args[args.index("--gatilho") + 1], "atalho")
        self.assertEqual(os.path.realpath(args[args.index("--projeto") + 1]), os.path.realpath(projeto))
        self.assertEqual(self.eventos(), ["ferramenta", "claude-abriu"], "primeiro atualiza, depois abre: a nova vale nesta abertura")

    def test_atalho_com_tmux_ja_aberto_so_reanexa(self):
        """RD4 · sessão tmux jarvis-<projeto> já aberta: o atalho reanexa e não chama a ferramenta nem abre outro claude"""
        ativo, projeto = self.atalho_instalado()
        self.abrir_atalho(ativo, projeto)
        self.assertEqual(len(self.chamadas_do_stub()), 1, "pré-condição: sem sessão aberta o atalho chama a ferramenta (não chama)")
        for arq in ("ferramenta.log", "seq.log"):
            (self.fake / arq).unlink()
        self.ctl(tmux=["jarvis-proj"])
        self.abrir_atalho(ativo, projeto)
        self.assertEqual(self.chamadas_do_stub(), [], "a ferramenta rodou com a sessão do Jarvis já aberta")
        self.assertEqual(self.eventos(), [], "não devia abrir um segundo claude")

    def test_atalho_sem_sessao_tmux_atualiza_uma_vez_so(self):
        """RD1 · sem sessão aberta o atalho cria a do tmux e a ferramenta roda exatamente uma vez no total"""
        ativo, projeto = self.atalho_instalado()
        self.abrir_atalho(ativo, projeto)
        self.assertEqual(len(self.chamadas_do_stub()), 1)
        self.assertEqual(self.eventos(), ["ferramenta", "claude-abriu"])


class Ocupacao(Mundo):
    def adiado(self, p, antes="0.47.0"):
        self.assertEqual(self.atualizacoes(), [], "atualizou com trabalho em curso")
        self.assertEqual(self.versoes()[("project", str(p))], antes)
        self.assertTrue(any(x.startswith("adiado:") for x in self.resultados()), f"o adiamento não foi registrado: {self.resultados()}")

    def test_tmux_aberto_so_reanexa(self):
        """RD4/S1 · sessão tmux do projeto aberta (nome com ponto vira sublinhado): nada é atualizado"""
        p = self.projeto("meu.proj")
        self.instalar("0.47.0", "project", p)
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.ctl(tmux=["jarvis-meu_proj"])
        self.rodar(projeto=p)
        self.assertEqual(self.atualizacoes(), [])
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")

    def test_agentes_vigentes_com_claude_vivo_adia(self):
        """RD4/S2+S3 · processo claude vivo no projeto e agente vigente no agentes.json: adia e registra"""
        p = self.cenario_atualiza()
        self.agentes(p, 2)
        self.vivo("claude", p)
        self.rodar(projeto=p)
        self.adiado(p)

    def test_registro_velho_sem_claude_vivo_nao_adia(self):
        """RD4 · agentes.json com registros dentro do prazo mas nenhum claude vivo: os agentes morreram, atualiza"""
        p = self.cenario_atualiza()
        self.agentes(p, 3)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")

    def test_claude_vivo_sem_trabalho_em_curso_nao_adia(self):
        """RD4 · fronteira: claude vivo, sem agente, trava, suíte nem integração, não é motivo para adiar"""
        p = self.cenario_atualiza()
        self.vivo("claude", p)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")

    def test_leitura_em_duvida_adia(self):
        """RD4/seção 3 · agentes.json ilegível com claude vivo conta como ocupado"""
        p = self.cenario_atualiza()
        (p / ".forge" / "run").mkdir(parents=True)
        (p / ".forge" / "run" / "agentes.json").write_text("{ nao e json")
        self.vivo("claude", p)
        self.rodar(projeto=p)
        self.adiado(p)

    def test_trava_pesado_viva_com_claude_vivo_adia(self):
        """RD4/S4 · trava pesado com dono vivo e claude vivo: adia"""
        p = self.cenario_atualiza()
        (p / ".forge" / "run").mkdir(parents=True)
        (p / ".forge" / "run" / "pesado.json").write_text(json.dumps({"desde": time.time(), "pid": os.getpid()}))
        self.vivo("claude", p)
        self.rodar(projeto=p)
        self.adiado(p)

    def test_suite_do_pre_push_rodando_com_claude_vivo_adia(self):
        """RD4/S5 · `.githooks/pre-push --status` com rc 0 (suíte rodando) e claude vivo: adia"""
        p = self.cenario_atualiza()
        # a trava que o pre-push da cópia instalada lê: <HOME>/.forge-contrib/forge-<uid>/forge-suite-<uid>.lock, presa por flock
        uid = os.getuid()
        pasta = self.home / ".forge-contrib" / f"forge-{uid}"
        pasta.mkdir(parents=True, mode=0o700)
        trava = open(pasta / f"forge-suite-{uid}.lock", "w")
        self.addCleanup(trava.close)
        fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.vivo("claude", p)
        self.rodar(projeto=p)
        self.adiado(p)

    def test_integracao_em_curso_adia_mesmo_sem_claude_vivo(self):
        """RD4/S6 · processo forge-fechar vivo com a pasta no projeto adia sozinho, sem precisar de claude"""
        p = self.cenario_atualiza()
        self.vivo("forge-fechar", p)
        self.rodar(projeto=p)
        self.adiado(p)

    def test_usuario_adiado_por_claude_vivo_em_outra_raiz_com_agentes(self):
        """RD4/seção 3 · escopo de usuário cobre toda raiz com claude vivo sem instalação própria: agente lá adia o usuário"""
        outra = self.projeto("outra")
        self.instalar("0.47.0", "user")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.agentes(outra, 1)
        self.vivo("claude", outra)
        self.rodar()
        self.assertEqual(self.atualizacoes(), [])
        self.assertEqual(self.versoes()[("user", "")], "0.47.0")
        self.assertTrue(any(x.startswith("adiado:") for x in self.resultados("user")), self.resultados())

    def test_adiamento_repetido_e_contado(self):
        """RD4/seção 3 · adiamentos seguidos ficam contados com a data do primeiro, para o aviso não ficar mudo"""
        p = self.cenario_atualiza()
        self.agentes(p, 1)
        self.vivo("claude", p)
        self.rodar(projeto=p)
        self.rodar(projeto=p)
        contagens = self.estado().get("adiamentos", {})
        self.assertTrue(any(v.get("n") == 2 and v.get("desde") for v in contagens.values()), f"adiamentos: {contagens}")


class Ancora(Mundo):
    def _forcar_checagem_e_modelo(self):
        p = self.projeto("p", isca=True)
        self.instalar("0.47.0", "project", p)
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.semear_estado(bom=self.bom("0.47.0", "project", str(p)))
        orfa = self.cache / "0.99.0"
        self._construir(orfa, "0.99.0", isca=True)
        (orfa / ".orphaned_at").write_text("1\n")
        self.rodar(projeto=p)
        return p

    def test_nunca_work_tree_nem_ref_local(self):
        """SEG-1/ancora · a checagem de início e o forge-upgrade vêm do installPath, nunca do work tree nem de ref local"""
        self._forcar_checagem_e_modelo()
        linhas = self.execs()
        self.assertFalse([l for l in linhas if "work tree" in l], f"executou código do work tree/ref local: {linhas}")
        self.assertTrue([l for l in linhas if f"{os.sep}0.47.2{os.sep}bin{os.sep}forge-doutor" in l],
                        f"a checagem de início devia rodar o doutor da versão nova: {linhas}")

    def test_pasta_orfa_mais_nova_do_cache_e_ignorada(self):
        """SEG-1/ancora · pasta órfã com versão maior no cache (0.99.0) nunca é executada; só o installPath ativo vale"""
        self._forcar_checagem_e_modelo()
        linhas = self.execs()
        self.assertTrue(linhas, "nada foi executado: a checagem de início não rodou")
        self.assertFalse([l for l in linhas if "0.99.0" in l or "ISCA" in l], f"executou a pasta órfã: {linhas}")
        for l in linhas:
            caminho = l.split()[1]
            self.assertTrue(caminho.startswith(str(self.cache) + os.sep), f"executou fora do cache do plugin: {caminho}")
            self.assertIn(Path(caminho).relative_to(self.cache).parts[0], ("0.47.0", "0.47.2"))

    def test_trampolim_segue_o_installpath_ativo_e_nao_o_maior_do_cache(self):
        """ancora/RD9 · o `forge` do terminal executa o installPath ativo, não a pasta de maior versão (órfã)"""
        ativo = self.instalar("0.47.1", "user")
        self._construir(self.cache / "0.99.0", "0.99.0", isca=True)
        subprocess.run(["bash", str(RAIZ / "scripts" / "instalar-atalho.sh")], env=self.env(), capture_output=True, timeout=60)
        r = subprocess.run([str(self.home / ".local" / "bin" / "forge"), "x"], env=self.env(), capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=30)
        linhas = self.execs()
        self.assertEqual([l.split()[1] for l in linhas], [str(ativo / "bin" / "forge")],
                         f"o trampolim devia executar só {ativo}/bin/forge; saída={r.stderr!r} execs={linhas}")

    def test_trampolim_sem_plugin_instalado_nao_cai_no_work_tree(self):
        """ancora · sem forge@forge instalado o trampolim diz o comando de instalação e sai; nunca roda o work tree"""
        subprocess.run(["bash", str(RAIZ / "scripts" / "instalar-atalho.sh")], env=self.env(), capture_output=True, timeout=60)
        atalho = self.home / ".local" / "bin" / "forge"
        self.assertTrue(atalho.is_file(), "o instalar-atalho.sh não criou o trampolim forge")
        r = subprocess.run([str(atalho), "--ajuda"], env=self.env(), capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           timeout=30)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("claude plugin install forge@forge", r.stderr + r.stdout)
        self.assertNotIn(str(RAIZ), atalho.read_text(), "o trampolim não pode apontar para o work tree")

    def test_claude_so_do_path_ou_de_local_bin(self):
        """SEG-6 · `claude` fora do PATH vale em ~/.local/bin; um `claude` em qualquer outro lugar é ignorado (falhou:sem-claude)"""
        p = self.cenario_atualiza()
        (self.fbin / "claude").unlink()
        for onde in (p / "claude", self.home / "bin" / "claude", self.neutro / "claude"):
            onde.parent.mkdir(exist_ok=True)
            self._script(onde, CLAUDE_FALSO)
        r = self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0", "usou um claude de lugar não previsto")
        self.assertTrue(any(x.startswith("falhou:sem-claude") for x in self.resultados()), self.resultados())
        self.sem_traceback(r)
        (self.home / ".local" / "bin").mkdir(parents=True)
        self._script(self.home / ".local" / "bin" / "claude", CLAUDE_FALSO)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2", "devia achar o claude em ~/.local/bin")

    def test_nao_repassa_gh_token(self):
        """SEG-3 · GH_TOKEN do ambiente não chega ao claude nem ao git"""
        p = self.cenario_atualiza()
        self.rodar(projeto=p, env=self.env(GH_TOKEN="segredo-do-oraculo"))
        usados = self.chamadas("claude") + self.chamadas("git")
        self.assertTrue(usados)
        self.assertFalse([c for c in usados if c["gh_token"]], "GH_TOKEN repassado a um subprocesso")

    def test_url_so_https_vinda_do_plugin_json_ativo(self):
        """SEG-5 · repository fora de https (http, file, com senha, opção) nunca chega ao `marketplace add`"""
        for ruim in ("http://example.test/forge.git", "file:///tmp/forge.git", "https://u:s@example.test/forge.git", "--upload-pack=x"):
            with self.subTest(repository=ruim):
                m = self.outro()
                p = m.projeto("p")
                m.instalar("0.47.0", "user", repository=ruim)
                m.instalar("0.47.0", "project", p, repository=ruim)
                m.publicar("0.47.2")
                m.ctl(tags=["v0.47.0", "v0.47.2"])
                m.definir_ref("v0.47.0")
                m.rodar(projeto=p)
                self.assertEqual(m.adds(), [], f"chamou add com url {ruim}")

    def test_estado_recusa_pasta_com_link_simbolico_e_fica_privado(self):
        """SEG-4 · pasta de dados que é link simbólico é recusada (nada gravado no destino); a normal é 0700"""
        p = self.cenario_atualiza()
        alvo = self.tmp / "alvo-do-link"
        alvo.mkdir()
        (self.plug / "data").mkdir(parents=True)
        os.symlink(alvo, self.plug / "data" / "forge-forge")
        r = self.rodar(projeto=p)
        self.assertEqual(list(alvo.rglob("*")), [], "gravou estado através de um link simbólico")
        self.assertNotIn("Traceback", r.stdout + r.stderr)
        os.unlink(self.plug / "data" / "forge-forge")
        self.rodar(projeto=p)
        modo = self.estado_dir.stat().st_mode & 0o777
        self.assertEqual(modo & 0o077, 0, f"pasta de estado com permissão {oct(modo)}; devia ser 0700")


class Volta(Mundo):
    def cenario_quebrado(self, escopos=("user",), **quebra):
        """0.47.1 instalada e boa, 0.47.2 publicada com defeito. Devolve o projeto."""
        p = self.projeto("p")
        bom = {}
        if "user" in escopos:
            self.instalar("0.47.1", "user")
            bom.update(self.bom("0.47.1"))
        if "project" in escopos:
            self.instalar("0.47.1", "project", p)
            bom.update(self.bom("0.47.1", "project", str(p)))
        self.publicar("0.47.1")
        self.publicar("0.47.2", **quebra)
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=bom)
        return p

    def volta_ok(self, r):
        self.assertEqual(set(self.versoes().values()), {"0.47.1"}, f"devia ter voltado à 0.47.1: {self.versoes()} {r.stderr}")
        self.assertEqual(self.ref(), "v0.47.1")
        self.assertIn("voltou", self.resultados())
        fix = self.estado().get("fixacao") or {}
        self.assertEqual((fix.get("motivo"), fix.get("de"), fix.get("para")), ("volta-automatica", "0.47.2", "0.47.1"))
        aviso = (self.estado().get("aviso") or {}).get("texto", "")
        self.assertTrue("0.47.2" in aviso and "0.47.1" in aviso, f"aviso pendente sem as duas versões: {aviso!r}")
        self.assertNotIn("claude plugin", aviso, "o aviso de volta bem-sucedida não pede ação nem traz comando (RD10)")
        self.assertNotIn("forge atualizar", aviso)
        self.sem_traceback(r)

    def test_checagem_quebrada_volta_a_ultima_boa(self):
        """RD6 · versão nova que quebra a checagem de início: volta à última boa, fixa, avisa, pelo add #v<boa> e update"""
        p = self.cenario_quebrado(py_quebrado=True)
        r = self.rodar(projeto=p)
        self.volta_ok(r)
        self.assertEqual([c["args"][3] for c in self.adds()], [f"{URL}#v0.47.2", f"{URL}#v0.47.1"],
                         "avanço e volta pelo mesmo mecanismo: add #tag sobre o existente")
        self.assertFalse([c for c in self.chamadas() if c["args"][:3] == ["plugin", "marketplace", "remove"]])

    def test_cada_item_da_checagem_de_inicio_reprova(self):
        """RD6/seção 4 · manifesto inválido, python que não compila, shell com erro de sintaxe e doutor com problema novo reprovam"""
        for quebra in ({"manifesto_ruim": True}, {"py_quebrado": True}, {"sh_quebrado": True}, {"doutor_problema": True}):
            with self.subTest(quebra=quebra):
                m = self.outro()
                p = m.cenario_quebrado(**quebra)
                r = m.rodar(projeto=p)
                self.assertEqual(set(m.versoes().values()), {"0.47.1"}, f"{quebra}: não voltou. {r.stderr}")
                self.assertIn("voltou", m.resultados())

    def test_volta_tambem_nos_escopos_de_projeto(self):
        """RD3/RD6 · a volta desce o escopo de projeto com cwd no projectPath, como desce o do usuário"""
        p = self.cenario_quebrado(escopos=("user", "project"), py_quebrado=True)
        r = self.rodar(projeto=p)
        self.volta_ok(r)
        desceu = [c for c in self.atualizacoes() if c["args"][c["args"].index("--scope") + 1] == "project"]
        self.assertTrue(desceu and all(os.path.realpath(c["cwd"]) == os.path.realpath(p) for c in desceu))

    def test_volta_que_falha_registra_e_da_o_comando(self):
        """RD6/seção 5.2 · se o add da volta falha: volta-falhou, fixação gravada e aviso com o comando exato (único caso)"""
        p = self.cenario_quebrado(py_quebrado=True)
        self.ctl(add_falha_para="v0.47.1")
        r = self.rodar(projeto=p)
        self.assertIn("volta-falhou", self.resultados())
        self.assertEqual((self.estado().get("fixacao") or {}).get("motivo"), "volta-automatica")
        aviso = (self.estado().get("aviso") or {}).get("texto", "")
        self.assertIn(f"claude plugin marketplace add {URL}#v0.47.1 --scope user", aviso)
        self.assertIn("claude plugin update forge@forge --scope user", aviso)
        self.sem_traceback(r)

    def test_igual_a_ultima_boa_nao_roda_a_checagem(self):
        """RD6/seção 2 · fronteira: instalada = última boa não confere de novo (nenhum doutor, nenhum validate)"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user", py_quebrado=True)
        self.publicar("0.47.1")
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=self.bom("0.47.1"))
        self.rodar(projeto=p)
        self.assertEqual(self.execs(), [])
        self.assertEqual([c for c in self.chamadas() if c["args"][:2] == ["plugin", "validate"]], [])
        self.assertNotIn("voltou", self.resultados())

    def test_sem_estado_confere_e_grava_a_instalada_como_boa(self):
        """RD6/seção 5.1 · sem estado.json a instalada passa pela checagem e, passando, vira a última boa"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        self.definir_ref("v0.47.1")
        self.rodar(projeto=p)
        self.assertEqual(self.estado().get("bom", {}).get("user|", {}).get("versao"), "0.47.1")

    def test_sem_estado_e_quebrada_registra_sem_ultima_boa_e_avisa(self):
        """RD6/seção 5.1 · sem última boa e checagem reprovada: não há volta; o registro diz sem-ultima-boa e fica o aviso"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user", py_quebrado=True)
        self.publicar("0.47.1")
        self.definir_ref("v0.47.1")
        r = self.rodar(projeto=p)
        self.assertTrue(any("sem-ultima-boa" in x for x in self.resultados()), self.resultados())
        self.assertEqual(self.adds(), [], "voltou para onde?")
        self.assertTrue((self.estado().get("aviso") or {}).get("texto"))
        self.sem_traceback(r)

    def test_aviso_do_validate_sem_strict_nao_reprova(self):
        """RD6/seção 4 · o validate roda sem --strict: manifesto só com aviso passa e a versão nova fica"""
        p = self.cenario_quebrado()
        self.ctl(manifesto_com_aviso=True)
        self.rodar(projeto=p)
        self.assertEqual(set(self.versoes().values()), {"0.47.2"})
        self.assertNotIn("voltou", self.resultados())
        validates = [c for c in self.chamadas() if c["args"][:2] == ["plugin", "validate"]]
        self.assertTrue(validates and all("--strict" not in c["args"] for c in validates), validates)

    def test_fixacao_automatica_segura_ate_sair_versao_maior(self):
        """RD6/seção 5.3 · depois da volta o alvo fica na boa; versão maior que a quebrada solta a fixação e atualiza"""
        p = self.cenario_quebrado(escopos=("project",), py_quebrado=True)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.1")
        antes = len(self.chamadas())
        self.rodar(projeto=p)
        novas = [c for c in self.chamadas()[antes:] if c["args"][:2] == ["plugin", "update"] or c["args"][:3] == ["plugin", "marketplace", "add"]]
        self.assertEqual([c for c in novas if "v0.47.2" in " ".join(c["args"])], [], "reaplicou a versão quebrada")
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.1")
        self.publicar("0.47.3")
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.3")
        self.assertFalse(self.estado().get("fixacao"), "a fixação devia sair quando sai versão maior que a quebrada")

    def test_fixacao_do_dono_e_respeitada(self):
        """RD1/seção 5.3 · fixação do dono segura o alvo mesmo com versão nova; registra adiado:fixado-pelo-dono"""
        p = self.cenario_atualiza()
        self.semear_estado(fixacao={"motivo": "dono", "de": "0.47.0", "para": "0.47.0", "desde": "2026-11-01"})
        self.rodar(projeto=p)
        self.assertEqual(self.atualizacoes(), [])
        self.assertTrue(any(x.startswith("adiado:fixado-pelo-dono") for x in self.resultados()), self.resultados())


class Catalogo(Mundo):
    def test_nunca_remove_nem_update_de_catalogo_nem_install(self):
        """U3/catalogo · nenhuma chamada a marketplace remove, marketplace update ou install; add sempre com #vX.Y.Z e --scope user"""
        p = self.cenario_atualiza()
        self.rodar(projeto=p)
        self.assertTrue(self.mutacoes(), "o cenário devia ter atualizado")
        for c in self.chamadas():
            a = c["args"]
            self.assertNotEqual(a[:3], ["plugin", "marketplace", "remove"], "marketplace remove desinstala os projetos (U3)")
            self.assertNotEqual(a[:3], ["plugin", "marketplace", "update"])
            self.assertNotEqual(a[:2], ["plugin", "install"])
            if a[:3] == ["plugin", "marketplace", "add"]:
                self.assertRegex(a[3], r"^https://.+#v\d+\.\d+\.\d+$")
                self.assertEqual(a[4:], ["--scope", "user"])

    def test_ferramenta_nao_grava_settings_nem_catalogo_nem_instalados(self):
        """SEG-5/catalogo · settings.json, known_marketplaces.json e installed_plugins.json só mudam pela CLI (conteúdo selado)"""
        p = self.cenario_atualiza()
        self.rodar(projeto=p)
        self.assertEqual(self.selos_alterados(), [], "a ferramenta gravou arquivo da CLI")
        self.ctl(rede=False)
        self.definir_ref("v0.47.0")
        self.rodar(projeto=p)
        self.assertEqual(self.selos_alterados(), [], "a ferramenta gravou arquivo da CLI no caminho de falha")

    def test_update_so_depois_de_o_ref_lido_ser_igual_ao_alvo(self):
        """catalogo/seção 11 · add que sai 0 sem mudar o ref (interrompido) não libera nenhum plugin update"""
        p = self.cenario_atualiza()
        self.ctl(add_sem_efeito=True)
        r = self.rodar(projeto=p)
        self.assertEqual(self.ref(), "v0.47.0")
        self.assertEqual(self.atualizacoes(), [], "atualizou com o catálogo fora do alvo")
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.sem_traceback(r)


class NuncaReabre(Mundo):
    def test_nao_mata_nao_manda_tecla_nao_recarrega_e_deixa_a_pasta_antiga(self):
        """RD11 · atualiza com sessão viva sem kill, sem tmux send-keys/kill-session, sem reload; processo e pasta antiga ficam"""
        p = self.cenario_atualiza()
        vivo = self.vivo("claude", p)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2", "o cenário devia ter atualizado (sessão sem trabalho em curso)")
        self.assertIsNone(vivo.poll(), "a sessão em curso foi derrubada")
        for dub in ("kill", "pkill", "killall"):
            self.assertEqual(self.chamadas(dub), [], f"chamou {dub}")
        for c in self.chamadas("tmux"):
            self.assertNotIn(c["args"][0], ("send-keys", "kill-session", "kill-server", "respawn-pane", "respawn-window"), c)
        self.assertFalse([c for c in self.chamadas() if "reload" in " ".join(c["args"])])
        self.assertTrue((self.cache / "0.47.0").is_dir(), "a pasta da versão anterior fica (14 dias) para quem a usa")

    def test_codigo_sem_chamada_de_encerramento_nem_tecla(self):
        """RD11 · leitura do código: sem send-keys, kill-session, reload-plugins nem os.kill com sinal"""
        arquivos = [a for a in (FERRAMENTA, MODULO) if a.is_file()]
        self.assertTrue(arquivos, "falta bin/forge-sempre-atual e bin/forge_sempre_atual.py (E6.4); este oráculo lê o código deles")
        for arq in arquivos:
            arvore = ast.parse(arq.read_text(encoding="utf-8"))
            docstrings = {id(n.body[0].value) for n in ast.walk(arvore)
                          if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and n.body
                          and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
            for no in ast.walk(arvore):
                if isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docstrings:
                    for proibido in ("send-keys", "kill-session", "kill-server", "reload-plugins"):
                        self.assertNotIn(proibido, no.value, f"{arq.name}:{no.lineno}")
                if (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr in ("kill", "killpg")
                        and isinstance(no.func.value, ast.Name) and no.func.value.id == "os"):
                    so_prova = no.func.attr == "kill" and len(no.args) == 2 and isinstance(no.args[1], ast.Constant) and no.args[1].value == 0
                    self.assertTrue(so_prova, f"{arq.name}:{no.lineno}: os.{no.func.attr} com sinal (a ferramenta não encerra processo de sessão)")


class SemEnvio(Mundo):
    def test_nenhum_push_nem_gh_nem_escrita_na_main_e_branch_so_local(self):
        """RD8 · cria a branch do modelo sem git push, sem gh, sem mexer em main/develop locais nem no remoto"""
        p = self.cenario_atualiza()
        remoto = self.tmp / "remotos" / "p.git"
        antes = git_real("for-each-ref", "--format=%(refname) %(objectname)", cwd=remoto)
        main, head = git_real("rev-parse", "main", cwd=p), git_real("rev-parse", "HEAD", cwd=p)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        self.assertFalse([c for c in self.chamadas("git") if "push" in c["args"]], "git push chamado")
        self.assertEqual(self.chamadas("gh"), [], "gh chamado")
        self.assertEqual(git_real("for-each-ref", "--format=%(refname) %(objectname)", cwd=remoto), antes, "o remoto mudou")
        self.assertEqual((git_real("rev-parse", "main", cwd=p), git_real("rev-parse", "HEAD", cwd=p)), (main, head))
        self.assertTrue(git_real("rev-parse", "--verify", "-q", "refs/heads/forge/upgrade-0.47.2", cwd=p, check=False),
                        "faltou a branch do modelo, local")


class Modelo(Mundo):
    def tem_branch(self, p, v="0.47.2"):
        return git_real("rev-parse", "--verify", "-q", f"refs/heads/forge/upgrade-{v}", cwd=p, check=False)

    def test_branch_criada_sem_envio_e_sem_tocar_a_copia(self):
        """RD7 · plugin acima do .forge/versao da origin/develop: branch forge/upgrade-<v> local por worktree temporária"""
        p = self.cenario_atualiza()
        head, status = git_real("rev-parse", "HEAD", cwd=p), git_real("status", "--porcelain", cwd=p)
        self.rodar(projeto=p)
        self.assertTrue(self.tem_branch(p), "branch do modelo não criada")
        self.assertEqual(git_real("show", "forge/upgrade-0.47.2:.forge/versao", cwd=p), "0.47.2")
        self.assertEqual((git_real("rev-parse", "HEAD", cwd=p), git_real("status", "--porcelain", cwd=p)), (head, status),
                         "a cópia de trabalho do projeto mudou")
        self.assertEqual(git_real("branch", "--show-current", cwd=p), "main")
        self.assertEqual(len(git_real("worktree", "list", cwd=p).splitlines()), 1, "sobrou worktree temporária")
        self.assertEqual(len(self.upgrades()), 1)

    def test_idempotente(self):
        """RD7 · segunda abertura com a branch já feita não recria nem roda o forge-upgrade de novo"""
        p = self.cenario_atualiza()
        self.rodar(projeto=p)
        sha = self.tem_branch(p)
        self.assertTrue(sha, "a primeira abertura devia criar a branch")
        self.rodar(projeto=p)
        self.assertEqual(self.tem_branch(p), sha)
        self.assertEqual(len(self.upgrades()), 1)

    def test_branch_ja_no_remoto_nao_recria(self):
        """RD7 · forge/upgrade-<v> já existe no remoto: nada a fazer (sem branch local nova, sem forge-upgrade)"""
        p = self.cenario_atualiza()
        git_real("push", "-q", "origin", "develop:refs/heads/forge/upgrade-0.47.2", cwd=p)
        self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2", "o cenário devia ter atualizado")
        self.assertEqual(self.tem_branch(p), "")
        self.assertEqual(self.upgrades(), [])

    def test_projeto_em_dia_com_o_modelo_nao_cria_branch(self):
        """RD7 · fronteira: versão do plugin <= .forge/versao da origin/develop não cria branch"""
        p = self.projeto("p", versao_modelo="0.47.2")
        self.instalar("0.47.2", "project", p)
        self.publicar("0.47.2")
        self.definir_ref("v0.47.2")
        self.rodar(projeto=p)
        self.assertEqual(self.resultados(), ["em_dia"], "o oráculo exige que a ferramenta tenha rodado e registrado")
        self.assertEqual(self.tem_branch(p), "")
        self.assertEqual(self.upgrades(), [])

    def test_falha_do_forge_upgrade_desfaz_a_worktree_e_registra(self):
        """RD7/seção 6 · forge-upgrade que falha: worktree desfeita, cópia intacta, registro falhou:modelo"""
        p = self.projeto("p")
        self.instalar("0.47.0", "project", p)
        self.publicar("0.47.0")
        self.publicar("0.47.2", upgrade_falha=True)
        self.definir_ref("v0.47.0")
        head = git_real("rev-parse", "HEAD", cwd=p)
        r = self.rodar(projeto=p)
        self.assertTrue(any(x.startswith("falhou:modelo") for x in self.resultados()), self.resultados())
        self.assertEqual(len(git_real("worktree", "list", cwd=p).splitlines()), 1)
        self.assertEqual((git_real("rev-parse", "HEAD", cwd=p), git_real("status", "--porcelain", cwd=p)), (head, ""))
        self.sem_traceback(r)


class Falha(Mundo):
    def test_sem_rede_segue_e_registra(self):
        """RD5 · sem rede: nada muda, uma linha no terminal, registro falhou:<etapa>, sem traceback"""
        p = self.cenario_atualiza()
        self.ctl(rede=False)
        r = self.rodar(projeto=p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertTrue(any(x.startswith("falhou:") for x in self.resultados()), self.resultados())
        self.sem_traceback(r)

    def test_prazo_estourado_mata_o_filho_e_segue(self):
        """RD5 · add que demora além do orçamento é morto, registra falhou:prazo e não libera update"""
        p = self.cenario_atualiza()
        self.ctl(add_demora=40)
        inicio = time.monotonic()
        r = self.rodar(projeto=p, orcamento=3, timeout=30)
        self.assertLess(time.monotonic() - inicio, 25, "a ferramenta não respeitou o orçamento")
        pid = int((self.fake / "add.pid").read_text())
        for _ in range(50):
            try:
                os.kill(pid, 0)
                time.sleep(0.1)
            except ProcessLookupError:
                break
        else:
            os.kill(pid, signal.SIGKILL)
            self.fail("o claude que passou do prazo ficou vivo")
        self.assertTrue(any(x.startswith("falhou:prazo") for x in self.resultados()), self.resultados())
        self.assertEqual(self.atualizacoes(), [])
        self.sem_traceback(r)

    def test_leitura_da_lista_que_falha_registra_e_nao_cai(self):
        """RD5 · erro interno do claude ao listar: registra falhou:<etapa> e termina limpo, sem traceback"""
        p = self.cenario_atualiza()
        self.ctl(list_falha=True)
        r = self.rodar(projeto=p)
        self.assertTrue(any(x.startswith("falhou:") for x in self.resultados()), self.resultados())
        self.sem_traceback(r)

    def test_sem_claude_registra_falhou_sem_claude(self):
        """RD5/SEG-6 · sem claude no PATH nem em ~/.local/bin: falhou:sem-claude"""
        p = self.cenario_atualiza()
        (self.fbin / "claude").unlink()
        r = self.rodar(projeto=p)
        self.assertTrue(any(x.startswith("falhou:sem-claude") for x in self.resultados()), self.resultados())
        self.sem_traceback(r)

    def test_atalho_abre_mesmo_com_ferramenta_quebrada(self):
        """RD5 · o atalho abre o claude seja qual for o fim da ferramenta (erro, traceback, morta por sinal, ausente)"""
        for nome, comportamento, existe in (("rc 1", "sys.exit(1)", True), ("traceback", "raise RuntimeError('quebrei')", True),
                                            ("sinal", "import os, signal\nos.kill(os.getpid(), signal.SIGKILL)", True),
                                            ("ausente", "", False)):
            with self.subTest(ferramenta=nome):
                m = self.outro()
                ativo, projeto = m.atalho_instalado(comportamento, existe)
                r = m.abrir_atalho(ativo, projeto, "--sem-tmux")
                if existe:
                    self.assertEqual(len(m.chamadas_do_stub()), 1, f"o atalho não chamou a ferramenta ({nome})")
                self.assertIn("claude-abriu", m.eventos(), f"o atalho não abriu o claude depois de: {nome}; stderr={r.stderr!r}")


class Avisos(Mundo):
    def _doutor(self, evento, projeto):
        entrada = {"hook_event_name": evento, "session_id": "s1", "cwd": str(projeto)}
        env = {**self.env(), "FORGE_VERIFICAR_VERSAO": "0", "PATH": os.environ["PATH"]}
        return subprocess.run([sys.executable, str(RAIZ / "hooks" / "doutor.py")], input=json.dumps(entrada), env=env, cwd=projeto,
                              capture_output=True, text=True, timeout=30)

    def _projeto_do_doutor(self):
        p = self.projeto("p")
        git_real("config", "core.hooksPath", ".githooks", cwd=p)
        return p

    def test_versao_nova_sem_comando(self):
        """RD10 · o aviso de versão nova diz que entra na próxima abertura e não pede ação nem manda comando"""
        sys.path.insert(0, str(RAIZ / "bin"))
        self.addCleanup(sys.path.remove, str(RAIZ / "bin"))
        import forge_versoes
        for superficie in ("projeto", "forge"):
            texto = forge_versoes.texto_de_versao_nova("0.47.1", "0.47.2", superficie)
            self.assertIn("próxima abertura", texto, f"[{superficie}] o aviso ainda não diz que a atualização é automática: {texto!r}")
            for proibido in ("rode", "forge atualizar", "--atualizar-vigente", "jarvis-forge"):
                self.assertNotIn(proibido, texto, f"[{superficie}] o aviso ainda pede ação do dono")

    def test_aviso_pendente_da_volta_sai_uma_vez_no_stop(self):
        """RD6 · o doutor mostra o aviso pendente de uma volta uma vez, só no Stop, e não repete"""
        p = self._projeto_do_doutor()
        texto = "A 0.47.2 falhou na checagem de início (hooks); o Forge voltou à 0.47.1 e fica nela até sair versão maior. Nada a fazer."
        self.semear_estado(aviso={"texto": texto, "avisado": False})
        r = self._doutor("SessionStart", p)
        self.assertNotIn("voltou à 0.47.1", r.stdout, "o aviso só sai no Stop")
        r = self._doutor("Stop", p)
        self.assertIn("voltou à 0.47.1", r.stdout, f"o doutor não mostrou o aviso pendente: {r.stdout!r} {r.stderr!r}")
        r = self._doutor("Stop", p)
        self.assertNotIn("voltou à 0.47.1", r.stdout, "o aviso repetiu")

    def test_adiamento_repetido_nao_fica_mudo(self):
        """RD4/seção 3 · adiamentos seguidos viram aviso 'adiado N vezes desde <data> (trabalho em curso)' no Stop"""
        p = self._projeto_do_doutor()
        self.semear_estado(adiamentos={"project": {"n": 3, "desde": "2026-11-14"}})
        r = self._doutor("Stop", p)
        self.assertRegex(r.stdout, r"adiado 3 vezes desde 2026-11-14", f"saída do doutor: {r.stdout!r} {r.stderr!r}")


class Atalho(Mundo):
    def test_recriacao_refaz_jarvis(self):
        """RD9 · HOME sem ~/.local/bin e com ~/.claude: o preparo essencial do postStart refaz os atalhos como trampolins"""
        ativo = self.instalar("0.47.1", "user")
        shutil.rmtree(ativo / "scripts")
        shutil.copytree(RAIZ / "scripts", ativo / "scripts")
        self._script(ativo / "bin" / "forge-sempre-atual", STUB_DA_FERRAMENTA.replace("@COMPORTAMENTO@", ""))
        self.assertFalse((self.home / ".local" / "bin").exists())
        env = self.env(FORGE_PREPARO_ESSENCIAL="1", FORGE_PERSISTENTE=str(self.tmp / "persistente"))
        subprocess.run(["bash", str(ativo / "scripts" / "preparar-estacao.sh"), "--container"], env=env, cwd=self.neutro,
                       stdin=subprocess.DEVNULL, capture_output=True, timeout=120)
        for nome in ("jarvis", "jarvis-forge", "forge"):
            self.assertTrue(os.access(self.home / ".local" / "bin" / nome, os.X_OK), f"o postStart não refez ~/.local/bin/{nome}")
        self.assertTrue(any(a[a.index("--gatilho") + 1] == "poststart" for a in self.chamadas_do_stub() if "--gatilho" in a),
                        f"o postStart não chamou a ferramenta com --gatilho poststart: {self.chamadas_do_stub()}")
        marca = ativo / "scripts" / "jarvis"
        marca.write_text(f'#!/usr/bin/env bash\necho "jarvis-ativo $0" >> "{self.fake}/exec.log"\n')
        subprocess.run([str(self.home / ".local" / "bin" / "jarvis")], env=self.env(), cwd=self.neutro, stdin=subprocess.DEVNULL,
                       capture_output=True, timeout=30)
        self.assertEqual([l.split()[1] for l in self.execs()], [str(marca)], "o trampolim jarvis não executa o installPath ativo")
        self.assertIn(".local/bin", (self.home / ".bashrc").read_text(), "a linha de PATH no .bashrc também some na recriação")


class Guarda(unittest.TestCase):
    def test_todo_requisito_do_dono_e_toda_classe_do_criterio_tem_oraculo(self):
        """guarda · RD1 a RD11, D30b e cada classe do critério de parada aparecem em algum oráculo; a suíte não esvazia"""
        modulo = sys.modules[__name__]
        suite = unittest.defaultTestLoader.loadTestsFromModule(modulo)
        casos = [t for grupo in suite for t in grupo if not isinstance(t, Guarda)]
        self.assertGreaterEqual(len(casos), 50, "o oráculo tem menos testes do que na entrega (E6.3)")
        docs = " ".join(type(t).__dict__[t._testMethodName].__doc__ or "" for t in casos)
        for n in range(1, 12):
            self.assertRegex(docs, rf"RD{n}(?!\d)", f"nenhum oráculo cita RD{n}")
        self.assertIn("D30b", docs)
        for classe in ("Ocupacao", "Ancora", "Volta", "Catalogo", "NuncaReabre", "SemEnvio", "Falha"):
            testes = unittest.defaultTestLoader.loadTestsFromTestCase(getattr(modulo, classe)).countTestCases()
            self.assertGreater(testes, 0, f"classe {classe} sem teste")


if __name__ == "__main__":
    unittest.main()
