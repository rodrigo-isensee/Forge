"""Apoio dos testes da versão defasada (VD-1, VD-2, VD-3): ambiente, repositórios locais (bare + clones) e a origem falsa do Forge.

Os testes em si ficam nos módulos que o mapa de `bin/forge-testes` aciona para cada arquivo alterado: `test_forge` (forge-check) e
`test_doutor` (doutor, forge_versoes e jarvis-forge). Nunca a rede, nunca o repositório real."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
HOJE = "2026-10-20"
FRASE = "atrás do repositório; a conferência não vale; peça à pessoa:"
MARCADOR_D = "decisão D: não muda o veredito"  # só no Forge, e só no aviso da cópia vigente atrás (O1 = A, FORGE-CHECK-LOTE E1)
FRASE_NO_FORGE = f"atrás do repositório ({MARCADOR_D}); para atualizar:"


def ambiente(home):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="t",
               GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    env.pop("XDG_STATE_HOME", None)
    env.pop("XDG_DATA_HOME", None)
    env.pop("TMUX", None)
    return sem_manutencao(env)


def git(*args, cwd, home):
    r = subprocess.run(["git", "-C", str(cwd), *args], env=sem_manutencao(ambiente(home)), capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise AssertionError(f"git {' '.join(args)}: {r.stderr}")
    return r.stdout.strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="versao-defasada-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.env = ambiente(self.home)

    def g(self, *args, cwd):
        return git(*args, cwd=cwd, home=self.home)


class ForgeFalso(Base):
    """Uma origem com três versões do Forge na develop (0.20.0, 0.21.0, 0.22.0) e as cópias da ferramenta em cada ponto."""

    def setUp(self):
        super().setUp()
        self.origem = self.tmp / "origem.git"
        self.g("init", "-q", "--bare", "-b", "develop", str(self.origem), cwd=self.tmp)
        remoto_sem_manutencao(self.origem)
        self.semente = self.tmp / "semente"
        self.g("clone", "-q", str(self.origem), str(self.semente), cwd=self.tmp)
        self.v1 = self.publicar("0.20.0")
        self.antiga_sem_objeto = self.copia("antiga-sem-objeto")  # clonada antes de a develop andar: não conhece o commit novo
        self.v2 = self.publicar("0.21.0")
        self.repo = self.tmp / "repo"  # o repositório sob conferência: sabe até a v2
        self.g("clone", "-q", str(self.origem), str(self.repo), cwd=self.tmp)
        self.antiga_com_objeto = self.copia("antiga-com-objeto", ate=self.v1)  # tem o objeto, mas o HEAD está na v1
        self.igual = self.copia("igual")
        self.v3 = self.publicar("0.22.0")
        self.nova = self.copia("nova")

    def publicar(self, versao):
        (self.semente / ".claude-plugin").mkdir(exist_ok=True)
        (self.semente / ".claude-plugin/plugin.json").write_text(json.dumps({"name": "forge", "version": versao}), encoding="utf-8")
        (self.semente / "docs/pedidos").mkdir(parents=True, exist_ok=True)
        (self.semente / "docs/pedidos/p.md").write_text(f"# Pedido\n\n## Escopo\n- item · `confirmado`\n\nv{versao}\n", encoding="utf-8")
        self.g("add", "-A", cwd=self.semente)
        self.g("commit", "-q", "-m", f"feat: {versao}", cwd=self.semente)
        self.g("push", "-q", "origin", "develop", cwd=self.semente)
        return self.g("rev-parse", "HEAD", cwd=self.semente)

    def copia(self, nome, ate=None):
        """Uma cópia da ferramenta: um clone do Forge falso com o `bin/forge-check` de verdade dentro (não versionado)."""
        pasta = self.tmp / nome
        self.g("clone", "-q", str(self.origem), str(pasta), cwd=self.tmp)
        if ate:
            self.g("reset", "-q", "--hard", ate, cwd=pasta)
        (pasta / "bin").mkdir(exist_ok=True)
        shutil.copy(FORGE_CHECK, pasta / "bin" / "forge-check")
        return pasta

    def check(self, copia, *args, raiz=None):
        return subprocess.run([sys.executable, str(copia / "bin" / "forge-check"), *args, "--raiz", str(raiz or self.repo)],
                              env=self.env, capture_output=True, text=True, timeout=60)

    def comandos(self):
        """Os subcomandos que bloqueiam (`pr`, `delta`, `entrega`, `brief gerar` e `brief mensagem`), com argumentos mínimos (o bloqueio vem antes de qualquer leitura do pedido)."""
        return {"pr": ["pr", "p"], "delta": ["delta", self.v2],
                "entrega": ["entrega", "p", "--branch", "develop", "--base", "develop", "--base-sha", self.v2, "--etapa", "codigo"],
                "brief gerar": ["brief", "gerar", "--pedido", "p", "--destino", "forge:tech-lead"],
                "brief mensagem": ["brief", "mensagem", "--arquivo", "docs/briefs/p-tech-lead-1.md", "--pedido", "p",
                                   "--destino", "forge:tech-lead"]}
