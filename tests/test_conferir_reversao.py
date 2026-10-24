"""`scripts/conferir-reversao.py` (M10): aviso por commit, sem escrever no repositório real."""
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "conferir-reversao.py"
AMBIENTE = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                           "GIT_COMMITTER_EMAIL": "t@t"})
TESTE_BASE = "import unittest\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.assertTrue(True)\n"
# O teste lê `dado.txt`: reverter o commit que o criou faz a suíte falhar.
TESTE_LE = ("import unittest\nfrom pathlib import Path\nclass T(unittest.TestCase):\n"
            "    def test_dado(self):\n        self.assertTrue(Path('dado.txt').is_file())\n")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=AMBIENTE, check=True).stdout.strip()


def impressao(raiz):
    """Hash de tudo sob `raiz` (conteúdo e caminhos), para provar que nada foi escrito."""
    h = hashlib.sha256()
    for p in sorted(Path(raiz).rglob("*")):
        h.update(str(p.relative_to(raiz)).encode())
        if p.is_file() and not p.is_symlink():
            h.update(p.read_bytes())
    return h.hexdigest()


class ConferirReversao(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        (self.repo / "tests").mkdir(parents=True)
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "tests" / "test_a.py").write_text(TESTE_BASE)
        self.commitar("base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "switch", "-q", "-c", "feat")

    def commitar(self, msg):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", msg)
        return git(self.repo, "rev-parse", "--short=7", "HEAD")

    def rodar(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd or self.repo, capture_output=True,
                              text=True, env=AMBIENTE)

    def test_commit_que_se_reverte(self):
        (self.repo / "extra.txt").write_text("x\n")
        sha = self.commitar("add extra")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), f"{sha} reverte")

    def test_commit_que_nao_se_reverte(self):
        (self.repo / "dado.txt").write_text("d\n")
        (self.repo / "tests" / "test_a.py").write_text(TESTE_LE)
        ruim = self.commitar("dado e teste que o le")
        (self.repo / "tests" / "test_a.py").write_text(TESTE_LE + "# depois\n")
        conflita = self.commitar("mexe no teste")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)  # aviso, não portão
        linhas = r.stdout.strip().splitlines()
        self.assertEqual(len(linhas), 2)
        self.assertTrue(linhas[0].startswith(f"{ruim} nao-reverte: "), linhas[0])
        self.assertTrue(linhas[1].startswith(f"{conflita} "), linhas[1])

    def test_conflito_ao_reverter_avisa(self):
        (self.repo / "tests" / "test_a.py").write_text(TESTE_BASE + "# um\n")
        primeiro = self.commitar("um")
        (self.repo / "tests" / "test_a.py").write_text(TESTE_BASE + "# um\n# dois\n")
        self.commitar("dois")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"{primeiro} nao-reverte: conflito", r.stdout)

    def test_nao_escreve_no_original(self):
        (self.repo / "extra.txt").write_text("x\n")
        self.commitar("add extra")
        (self.repo / "dado.txt").write_text("d\n")
        (self.repo / "tests" / "test_a.py").write_text(TESTE_LE)
        self.commitar("dado")
        antes = impressao(self.repo)
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(impressao(self.repo), antes)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_erro_de_uso_e_repositorio_invalido_saem_com_2(self):
        self.assertEqual(self.rodar().returncode, 2)
        self.assertEqual(self.rodar(self.base, "nao-existe").returncode, 2)
        with tempfile.TemporaryDirectory() as fora:
            self.assertEqual(self.rodar("a", "b", cwd=fora).returncode, 2)


if __name__ == "__main__":
    unittest.main()
