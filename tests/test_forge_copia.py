"""bin/forge-copia: a cópia de trabalho só nasce dentro de ~/.forge-contrib; fora dela, recusa."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


class Instalar(Base):
    """--instalar com stack falsa (pacote em raiz temporária, sem rede): roda o comando declarado dentro da cópia."""

    def pacote(self, spec, detecta_em=None):
        raiz = self.fora / "raiz"
        (raiz / "bin").mkdir(parents=True)
        (raiz / "bin" / "forge-copia").write_text(BIN.read_text())
        (raiz / "stacks" / "falsa").mkdir(parents=True)
        (raiz / "stacks" / "falsa" / "instalar.json").write_text(spec if isinstance(spec, str) else json.dumps(spec))
        self.bin = raiz / "bin" / "forge-copia"
        if detecta_em:
            (self.origem / detecta_em).write_text("x")
            self.git(self.origem, "add", detecta_em)
            self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "d")
            self.git(self.origem, "update-ref", "refs/remotes/origin/develop", "HEAD")

    def roda(self, destino, *extra):
        return subprocess.run(["python3", "-I", str(self.bin), "clone", str(destino), "--branch", "melhoria/i", "--origem", str(self.origem), *extra],
                              cwd=self.origem, env=self.env, capture_output=True, text=True)

    def test_roda_o_comando_declarado_dentro_da_copia(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "pwd > instalado.txt"]]}, "marca.txt")
        d = self.pasta / "i1"
        r = self.roda(d, "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(Path((d / "instalado.txt").read_text().strip()).resolve(), d.resolve())

    def test_worktree_tambem_instala(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        d = self.pasta / "wt" / "i8"
        r = subprocess.run(["python3", "-I", str(self.bin), "worktree", str(d), "--branch", "melhoria/i8", "--instalar"],
                           cwd=self.origem, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((d / "instalado.txt").exists())

    def test_sem_a_opcao_nao_instala(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        self.assertEqual(self.roda(self.pasta / "i2").returncode, 0)
        self.assertFalse((self.pasta / "i2" / "instalado.txt").exists())

    def test_stack_nao_detectada_avisa_e_sai_0(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]})
        r = self.roda(self.pasta / "i3", "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhuma stack detectada", r.stderr)
        self.assertFalse((self.pasta / "i3" / "instalado.txt").exists())

    def test_comando_que_falha_sai_1_e_diz_qual(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "exit 3"]]}, "marca.txt")
        r = self.roda(self.pasta / "i4", "--instalar")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("rc=3", r.stderr)

    def test_comando_ausente_sai_1_com_mensagem(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["gerenciador-que-nao-existe", "install"]]}, "marca.txt")
        r = self.roda(self.pasta / "i5", "--instalar")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("indisponível", r.stderr)

    def test_falha_interrompe_os_comandos_seguintes(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "exit 1"], ["sh", "-c", "touch depois.txt"]]}, "marca.txt")
        self.roda(self.pasta / "i6", "--instalar")
        self.assertFalse((self.pasta / "i6" / "depois.txt").exists())

    def test_spec_invalida_sai_1(self):
        for spec in ("nao e json", {"detecta": ["marca.txt"], "comandos": ["sh -c touch x"]}, {"comandos": []}):
            self.pacote(spec, "marca.txt")
            r = self.roda(self.pasta / "i7", "--instalar")
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("inválido", r.stderr)
            shutil.rmtree(self.pasta / "i7", ignore_errors=True)
            shutil.rmtree(self.fora / "raiz")

    def test_nao_afrouxa_a_recusa_de_pasta(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        r = self.roda(self.fora / "c", "--instalar")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertFalse((self.fora / "c").exists())

    def test_pacotes_reais_declaram_instalar_valido(self):
        for stack in (BIN.parent.parent / "stacks").iterdir():
            spec = json.loads((stack / "instalar.json").read_text())
            self.assertTrue(spec["detecta"] and spec["comandos"], stack.name)
            self.assertTrue(all(isinstance(c, list) and c for c in spec["comandos"]), stack.name)


if __name__ == "__main__":
    unittest.main()
