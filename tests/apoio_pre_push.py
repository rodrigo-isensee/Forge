"""Apoio dos testes do pre-push sem fila (PREPUSH-TAGS, PREPUSH-SEM-CODIGO): um repositório descartável com a trava da
bateria presa por fora; quem entra na fila é barrado em 2 s, quem não entra não espera."""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})
ZERO = "0" * 40
OUTRA = "import unittest, pathlib\nclass O(unittest.TestCase):\n    def test_a(self):\n        pathlib.Path('rodou-outra').write_text('s')\n"


class Repo(unittest.TestCase):
    ARQUIVOS = {}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir, self.repo = Path(tmp.name), Path(tmp.name) / "repo"
        (self.dir / "run").mkdir()
        self.git("init", "-q", "-b", "melhoria/x", str(self.repo))
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.dir / "run"), HOME=str(self.dir / "home"), FORGE_TRAVA_ESPERA="2")
        self.base = self.commit(**{".gitignore": "rodou-*\n__pycache__/\n", "tests/test_a.py": OUTRA, "src/app.py": "x\n",
                                   "docs/guia.md": "g\n", **self.ARQUIVOS})
        for ref in ("develop", "melhoria/x"):
            self.git("update-ref", f"refs/remotes/origin/{ref}", self.base)
        trava = self.dir / "run" / f"forge-suite-{os.getuid()}.lock"
        trava.touch()
        segurador = subprocess.Popen(["flock", str(trava), "sleep", "120"])
        self.addCleanup(segurador.wait)
        self.addCleanup(segurador.terminate)
        while subprocess.run(["flock", "-n", str(trava), "true"]).returncode == 0:
            time.sleep(0.05)

    def git(self, *args):
        r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.repo if self.repo.exists() else None,
                           env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, **arquivos):
        for nome, texto in arquivos.items():
            (self.repo / nome).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / nome).write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")
        return self.git("rev-parse", "HEAD")

    def envia(self, *linhas, remoto="origin"):
        for p in self.repo.glob("rodou-*"):
            p.unlink()
        r = subprocess.run([str(HOOK), remoto, "u"], cwd=self.repo, env=self.env, input="".join(linhas),
                           capture_output=True, text=True, timeout=120)
        return r.returncode, {p.name for p in self.repo.glob("rodou-*")}, r.stderr

    def assert_fila(self, resultado):
        """O caminho de sempre: entra na fila da bateria e, com a trava presa, é barrado sem rodar."""
        rc, marcas, erro = resultado
        self.assertEqual((rc, marcas), (1, set()), erro)
        self.assertIn("a vez não chegou", erro)
