"""A guarda do `.git/config` comum (tests/guarda_git.py) enxerga uma mudança de identidade."""
import tempfile
import unittest
from pathlib import Path

import guarda_git
from test_forge import git
from guarda_git import setUpModule, tearDownModule  # noqa: F401


class GuardaGit(unittest.TestCase):
    def test_config_igual_nao_acusa(self):
        self.assertEqual(guarda_git.diferenca("[core]\n", "[core]\n"), "")

    def test_detecta_identidade_gravada_no_config_comum(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            git("init", "-q", "-b", "develop", cwd=tmp)
            caminho = guarda_git.config_comum(tmp)
            self.assertEqual(caminho, (tmp / ".git" / "config").resolve())
            antes = guarda_git.ler(caminho)
            git("config", "user.name", "t", cwd=tmp)
            mudou = guarda_git.diferenca(antes, guarda_git.ler(caminho))
            self.assertIn("+\tname = t", mudou)

    def test_fora_de_repositorio_nao_quebra(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(guarda_git.config_comum(Path(tmp)))
            self.assertIsNone(guarda_git.ler(None))


if __name__ == "__main__":
    unittest.main()
