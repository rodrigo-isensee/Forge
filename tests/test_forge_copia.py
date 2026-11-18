"""bin/forge-copia: a cópia de trabalho só nasce dentro de ~/.forge-contrib; fora dela, recusa."""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

BIN = Path(__file__).resolve().parent.parent / "bin" / "forge-copia"


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home = Path(t.name).resolve() / "home"
        self.pasta = self.home / ".forge-contrib"
        self.pasta.mkdir(parents=True)
        self.fora = Path(t.name).resolve() / "fora"
        self.fora.mkdir()
        self.env = sem_manutencao({**os.environ, "HOME": str(self.home), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
        self.origem = self.pasta / "origem"
        self.git(self.pasta, "init", "-q", "-b", "develop", str(self.origem))
        self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i")
        self.git(self.origem, "remote", "add", "origin", str(self.origem))  # sem remoto, o git nem tentaria rastrear
        self.git(self.origem, "update-ref", "refs/remotes/origin/develop", "HEAD")

    def git(self, cwd, *a):
        return subprocess.run(["git", *a], cwd=cwd, env=self.env, capture_output=True, text=True, check=True)

    def copia(self, *a, cwd=None):
        return subprocess.run(["python3", "-I", str(BIN), *a], cwd=cwd or self.origem, env=self.env, capture_output=True, text=True)

    def branch_de(self, d):
        return self.git(d, "branch", "--show-current").stdout.strip()


class Cria(Base):
    def test_clone_dentro_cria_branch_a_partir_da_base_sem_rastreio(self):
        d = self.pasta / "c1"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/x")
        self.assertEqual(self.git(d, "rev-parse", "HEAD").stdout, self.git(d, "rev-parse", "origin/develop").stdout)
        cfg = subprocess.run(["git", "config", "--get", "branch.melhoria/x.remote"], cwd=d, env=self.env, capture_output=True)
        self.assertNotEqual(cfg.returncode, 0)  # --no-track: sem upstream

    def test_clone_com_base_que_nao_existe_falha_com_1(self):
        r = self.copia("clone", str(self.pasta / "c3"), "--branch", "melhoria/x", "--origem", str(self.origem), "--base", "origin/nada")
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_worktree_dentro_cria_a_branch(self):
        d = self.pasta / "wt" / "w1"
        r = self.copia("worktree", str(d), "--branch", "melhoria/w", "--base", "origin/develop")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/w")
        cfg = subprocess.run(["git", "config", "--get", "branch.melhoria/w.remote"], cwd=d, env=self.env, capture_output=True)
        self.assertNotEqual(cfg.returncode, 0)  # --no-track: sem upstream


class Recusa(Base):
    def recusado(self, destino, *extra):
        r = self.copia("worktree", str(destino), "--branch", "melhoria/z", "--base", "origin/develop", *extra)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("recusado", r.stderr)
        return r

    def test_fora_da_pasta(self):
        self.recusado(self.fora / "w")
        self.assertFalse((self.fora / "w").exists())

    def test_com_ponto_ponto_mesmo_voltando_para_dentro(self):
        self.recusado(f"{self.pasta}/x/../y")

    def test_por_link_simbolico(self):
        (self.pasta / "atalho").symlink_to(self.fora)
        self.recusado(self.pasta / "atalho" / "w")
        self.assertFalse((self.fora / "w").exists())

    def test_a_propria_pasta_liberada(self):
        self.recusado(self.pasta)

    def test_prefixo_parecido_nao_vale(self):
        irmao = self.home / ".forge-contrib-outro"
        irmao.mkdir()
        self.recusado(irmao / "w")

    def test_a_pasta_liberada_vazia_tambem_e_recusada(self):
        vazia = self.home / ".forge-contrib"
        for item in list(vazia.iterdir()):
            item.rename(self.fora / item.name)
        r = self.copia("worktree", str(vazia), "--branch", "melhoria/z", cwd=self.fora / "origem")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("própria pasta", r.stderr)

    def test_destino_ocupado(self):
        (self.pasta / "ocupado").mkdir()
        (self.pasta / "ocupado" / "a").write_text("x")
        self.recusado(self.pasta / "ocupado")

    def test_branch_ou_base_com_cara_de_opcao(self):
        r = self.copia("worktree", str(self.pasta / "w"), "--branch=--detach", "--base", "origin/develop")
        self.assertEqual(r.returncode, 2, r.stderr)
        r = self.copia("worktree", str(self.pasta / "w"), "--branch", "melhoria/q", "--base=--orphan")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_clone_sem_origem(self):
        r = self.copia("clone", str(self.pasta / "c"), "--branch", "melhoria/q")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_origem_com_cara_de_opcao(self):
        r = self.copia("clone", str(self.pasta / "c"), "--branch", "melhoria/q", "--origem=--upload-pack=x")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_nome_de_branch_invalido(self):
        r = self.copia("worktree", str(self.pasta / "w"), "--branch", "a..b")
        self.assertEqual(r.returncode, 2, r.stderr)


def disco(usado, livre):
    return shutil._ntuple_diskusage(usado + livre, usado, livre)


class Disco(unittest.TestCase):
    """MP6: disco falso (shutil.disk_usage trocado no processo), sem encher disco de verdade; o git do clone também é falso."""

    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home = Path(t.name).resolve()
        (self.home / ".forge-contrib").mkdir()
        self.mod = SourceFileLoader("forge_copia_teste", str(BIN)).load_module()
        self.gits = []
        for alvo in (mock.patch.dict(os.environ, {"HOME": str(self.home)}),
                     mock.patch.object(self.mod, "git", lambda *a, cwd=None: self.gits.append(a) or 0)):
            alvo.start()
            self.addCleanup(alvo.stop)

    def copiar(self, uso):
        erro = io.StringIO()
        with mock.patch("shutil.disk_usage", **uso), redirect_stderr(erro):
            rc = self.mod.main(["clone", str(self.home / ".forge-contrib" / "c"), "--branch", "melhoria/q", "--origem", "o"])
        return rc, erro.getvalue()

    def test_acima_do_limiar_recusa_e_manda_limpar_sem_chamar_o_git(self):
        rc, erro = self.copiar({"return_value": disco(91, 9)})
        self.assertEqual((rc, self.gits), (2, []), erro)
        self.assertIn("91% de uso, acima de 90%", erro)
        self.assertIn("--limpar", erro)

    def test_no_limiar_cria(self):
        rc, erro = self.copiar({"return_value": disco(90, 10)})
        self.assertEqual(rc, 0, erro)
        self.assertEqual(self.gits[0][0], "clone")

    def test_disco_ilegivel_recusa(self):
        rc, erro = self.copiar({"side_effect": OSError("sem statvfs")})
        self.assertEqual((rc, self.gits), (2, []), erro)
        self.assertIn("não consegui medir o disco", erro)

    def test_disco_sem_espaco_ocupavel_conta_como_cheio(self):
        rc, erro = self.copiar({"return_value": disco(0, 0)})
        self.assertEqual((rc, self.gits), (2, []), erro)

    def test_destino_novo_mede_o_pai_que_existe(self):
        medidos = []
        rc, erro = self.copiar({"side_effect": lambda p: medidos.append(p) or disco(1, 99)})
        self.assertEqual((rc, medidos), (0, [str(self.home / ".forge-contrib")]), erro)

    def test_o_limiar_mora_so_no_forge_disco(self):
        self.assertEqual(self.mod.LIMIAR_DISCO, 90)
        for nome in ("forge-copia", "forge-placar"):
            self.assertNotRegex((BIN.parent / nome).read_text(), r"\b90\s*%|>\s*90\b")


if __name__ == "__main__":
    unittest.main()
