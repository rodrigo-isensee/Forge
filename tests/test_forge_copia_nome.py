"""bin/forge-copia, CLONE-NOME-UNICO: destino tomado nunca é reusado; a recusa diz a branch dele e sugere um nome único."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

BIN = Path(__file__).resolve().parent.parent / "bin" / "forge-copia"


class NomeUnico(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home = Path(t.name).resolve() / "home"
        self.pasta = self.home / ".forge-contrib"
        self.pasta.mkdir(parents=True)
        # ambiente limpo: nada herdado de quem roda a suíte além do PATH (AR-4)
        self.env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.home), "LANG": "C.UTF-8",
                                   "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
        self.origem = self.pasta / "origem"
        self.git(self.pasta, "init", "-q", "-b", "develop", str(self.origem))
        self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i")
        self.git(self.origem, "remote", "add", "origin", str(self.origem))
        self.git(self.origem, "update-ref", "refs/remotes/origin/develop", "HEAD")

    def git(self, cwd, *a):
        return subprocess.run(["git", *a], cwd=cwd, env=self.env, capture_output=True, text=True, check=True)

    def clone(self, destino, branch, *extra):
        return subprocess.run([sys.executable, "-I", str(BIN), "clone", str(destino), "--branch", branch,
                               "--origem", str(self.origem), *extra],
                              cwd=self.origem, env=self.env, capture_output=True, text=True)

    def branch_de(self, d):
        return self.git(d, "branch", "--show-current").stdout.strip()

    def test_nome_livre_cria(self):
        d = self.pasta / "v0480-x-tech-lead"
        r = self.clone(d, "melhoria/v0480-x", "--papel", "tech-lead")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/v0480-x")

    def test_nome_tomado_por_outra_branch_recusa_com_o_nome_sugerido(self):
        d = self.pasta / "c1"
        self.assertEqual(self.clone(d, "melhoria/a").returncode, 0)
        r = self.clone(d, "melhoria/b", "--papel", "qa-engineer")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("cópia da branch melhoria/a", r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'b-qa-engineer'}", r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/a")  # a cópia do outro agente não muda de branch

    def test_nome_sugerido_ja_tomado_ganha_sufixo_numerico(self):
        self.assertEqual(self.clone(self.pasta / "c1", "melhoria/a").returncode, 0)
        (self.pasta / "b-qa").mkdir()
        (self.pasta / "b-qa" / "x").write_text("x")
        (self.pasta / "b-qa-2").write_text("arquivo também toma o nome")
        r = self.clone(self.pasta / "c1", "melhoria/b", "--papel", "qa")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'b-qa-3'}", r.stderr)

    def test_sem_papel_sugere_a_branch_sem_prefixo(self):
        self.assertEqual(self.clone(self.pasta / "c1", "melhoria/a").returncode, 0)
        r = self.clone(self.pasta / "c1", "fix/sub/b")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'sub-b'}\n", r.stderr)

    def test_mesma_branch_em_uso_tambem_recusa(self):
        d = self.pasta / "c1"
        self.assertEqual(self.clone(d, "melhoria/a").returncode, 0)
        r = self.clone(d, "melhoria/a", "--papel", "qa")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'a-qa'}", r.stderr)

    def test_pasta_vazia_nao_esta_tomada(self):
        d = self.pasta / "vazia"
        d.mkdir()
        r = self.clone(d, "melhoria/a")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/a")

    def test_link_com_o_nome_sugerido_nao_e_oferecido(self):
        self.assertEqual(self.clone(self.pasta / "c1", "melhoria/a").returncode, 0)
        fora = self.home / "fora"
        fora.mkdir()
        (self.pasta / "b-qa").symlink_to(fora)  # link para pasta vazia fora da pasta de cópias
        r = self.clone(self.pasta / "c1", "melhoria/b", "--papel", "qa")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'b-qa-2'}", r.stderr)
        self.assertEqual(list(fora.iterdir()), [])

    def test_pasta_comum_dentro_de_repositorio_nao_diz_a_branch_do_repositorio(self):
        d = self.origem / "sub"
        d.mkdir()
        (d / "x").write_text("x")
        r = self.clone(d, "melhoria/b")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("cópia da branch", r.stderr)
        self.assertIn(f"use o nome único {self.origem / 'b'}", r.stderr)

    def test_papel_invalido_recusa_sem_criar(self):
        for papel in ("../x", "Tech", "-qa", "a/b"):
            with self.subTest(papel=papel):
                d = self.pasta / "c2"
                r = self.clone(d, "melhoria/a", f"--papel={papel}")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("papel inválido", r.stderr)
                self.assertFalse(d.exists())


if __name__ == "__main__":
    unittest.main()
