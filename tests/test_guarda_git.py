"""A guarda do `.git/config` comum (tests/guarda_git.py) enxerga uma mudança de identidade."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import guarda_git  # noqa: E402
from test_forge import git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


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

    def test_ignora_branch_e_acusa_o_resto(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            git("init", "-q", "-b", "develop", cwd=tmp)
            caminho = guarda_git.config_comum(tmp)
            git("config", "user.email", "a@b.c", cwd=tmp)
            antes = guarda_git.ler(caminho)
            git("config", "branch.x.remote", "origin", cwd=tmp)
            git("config", "branch.x.merge", "refs/heads/x", cwd=tmp)
            self.assertEqual(guarda_git.diferenca(antes, guarda_git.ler(caminho)), "")
            git("config", "branch.x.remote", "outro", cwd=tmp)
            self.assertEqual(guarda_git.diferenca(antes, guarda_git.ler(caminho)), "")
            for chave in ("user.name", "core.hooksPath", "commit.gpgsign", "include.path", "alias.l",
                          "remote.origin.url", "novo.chave"):
                with self.subTest(chave=chave):
                    antes_chave = guarda_git.ler(caminho)
                    git("config", chave, "v", cwd=tmp)
                    self.assertNotEqual(guarda_git.diferenca(antes_chave, guarda_git.ler(caminho)), "")

    def test_secao_seguinte_a_branch_continua_vigiada(self):
        antes = '[branch "x"]\n\tremote = origin\n[user]\n\tname = a\n'
        depois = '[branch "x"]\n\tremote = o2\n[user]\n\tname = b\n'
        self.assertIn("+\tname = b", guarda_git.diferenca(antes, depois))

    def test_fora_de_repositorio_nao_quebra(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(guarda_git.config_comum(Path(tmp)))
            self.assertIsNone(guarda_git.ler(None))


if __name__ == "__main__":
    unittest.main()
