"""E9.1 (v048, AFETADOS-CATRACA-E-CUSTO): o diff que toca hooks/, bin/ ou um arquivo protegido da catraca leva ao plano
dirigido do `bin/forge-testes` a catraca no modo do diff e o teste de custo (`test_hooks_volta_corpus`); o resto fica como
estava. O #957 nasceu vermelho na catraca e o #940 e o #944 no teste de custo, com os afetados verdes no computador."""
import importlib.machinery
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-testes"
AMBIENTE = sem_manutencao({**{k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON"))},
                           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
CATRACA_DE_BRINQUEDO = (
    'import sys\n'
    'PROTEGIDOS = (".githooks/", "scripts/protegido.py")\n'
    'open("catraca-rodou", "w").write(" ".join(sys.argv[1:]))\n'
    'sys.exit(int(open("catraca-saida").read()) if __import__("os").path.exists("catraca-saida") else 0)\n'
)
CUSTO_DE_BRINQUEDO = "import unittest\n\n\nclass C(unittest.TestCase):\n    def test_ok(self):\n        pass\n"


def carregar():
    carregador = importlib.machinery.SourceFileLoader("forge_testes_e91", str(FERRAMENTA))
    spec = importlib.util.spec_from_loader("forge_testes_e91", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


class Brinquedo(unittest.TestCase):
    """Raiz de brinquedo com a catraca (PROTEGIDOS própria) e o teste de custo."""

    def setUp(self):
        self.f = carregar()
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz, True)
        (self.raiz / "tests").mkdir()
        (self.raiz / "tests" / "catraca.py").write_text(CATRACA_DE_BRINQUEDO, encoding="utf-8")
        (self.raiz / "tests" / "test_hooks_volta_corpus.py").write_text(CUSTO_DE_BRINQUEDO, encoding="utf-8")

    def plano(self, *caminhos):
        return self.f.custo_e_catraca(list(caminhos), self.raiz)


class CustoECatraca(Brinquedo):
    def test_hooks_bin_e_protegidos_levam_a_catraca_e_o_custo(self):
        for caminho in ("hooks/a.py", "bin/forge-x", ".githooks/pre-push", "scripts/protegido.py"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.plano("docs/guia.md", caminho), (("test_hooks_volta_corpus",), True))

    def test_o_resto_fica_como_esta(self):
        for caminho in ("docs/guia.md", "scripts/protegido.pyx", "scripts/outro.py", "docs/hooks/x.md", "tests/bin/x"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.plano(caminho), ((), False))
        self.assertEqual(self.plano(), ((), False))

    def test_sem_a_catraca_nada_muda(self):
        (self.raiz / "tests" / "catraca.py").unlink()
        self.assertEqual(self.plano("bin/forge-x"), ((), False))

    def test_catraca_em_link_nao_conta(self):
        alvo = self.raiz / "fora.py"
        (self.raiz / "tests" / "catraca.py").rename(alvo)
        (self.raiz / "tests" / "catraca.py").symlink_to(alvo)
        self.assertEqual(self.plano("bin/forge-x"), ((), False))

    def test_sem_o_teste_de_custo_so_a_catraca(self):
        (self.raiz / "tests" / "test_hooks_volta_corpus.py").unlink()
        self.assertEqual(self.plano("hooks/a.py"), ((), True))

    def test_protegidos_ilegiveis_contam_como_tocados(self):  # falha fechada
        for texto in ("PROTEGIDOS = (", "PROTEGIDOS = ()\n", "PROTEGIDOS = ['.githooks/']\n", "PROTEGIDOS = (1,)\n",
                      "PROTEGIDOS = tuple()\n", "OUTRA = ('.githooks/',)\n"):
            with self.subTest(texto=texto):
                (self.raiz / "tests" / "catraca.py").write_text(texto, encoding="utf-8")
                self.assertEqual(self.plano("docs/guia.md"), (("test_hooks_volta_corpus",), True))


class ListaDaCatracaReal(unittest.TestCase):
    """A lista vem da PROTEGIDOS de tests/catraca.py, sem cópia: um protegido fora de hooks/ e bin/ a pede."""

    def test_le_a_protegidos_da_catraca_do_forge(self):
        f = carregar()
        protegidos = f.protegidos_da_catraca(RAIZ / "tests" / "catraca.py")
        self.assertIn("scripts/conferir-release.py", protegidos)
        self.assertIn(".github/workflows/", protegidos)
        self.assertEqual(f.custo_e_catraca(["scripts/conferir-release.py"], RAIZ), (("test_hooks_volta_corpus",), True))
        self.assertEqual(f.custo_e_catraca(["docs/guia.md"], RAIZ), ((), False))


class PeloComando(Brinquedo):
    """O comando inteiro, num repositório de brinquedo: o plano mostra a catraca e o custo, e a execução roda a catraca."""

    def setUp(self):
        super().setUp()
        (self.raiz / "bin").mkdir()
        for nome in ("forge-testes", "forge_apoio_testes.py"):
            shutil.copy2(RAIZ / "bin" / nome, self.raiz / "bin" / nome)
        subprocess.run(["git", "init", "-q"], cwd=self.raiz, env=AMBIENTE, check=True)

    def rodar(self, *args):
        return subprocess.run([sys.executable, "-I", "bin/forge-testes", *args], cwd=self.raiz, env=AMBIENTE,
                              capture_output=True, text=True, timeout=120)

    def test_listar_mostra_a_catraca_e_o_custo_para_bin(self):
        r = self.rodar("--afetados", "--listar", "bin/forge-testes")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("forge-testes: dirigido ("), r.stdout)
        self.assertIn("test_hooks_volta_corpus", r.stdout.splitlines()[0])
        self.assertIn("forge-testes: catraca no diff (tests/catraca.py --base origin/develop)", r.stdout)
        self.assertFalse((self.raiz / "catraca-rodou").exists())

    def test_listar_sem_hook_bin_nem_protegido_fica_como_esta(self):
        r = self.rodar("--afetados", "--listar", "docs/guia.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("catraca", r.stdout)
        self.assertNotIn("test_hooks_volta_corpus", r.stdout)

    def test_afetados_roda_a_catraca_no_modo_do_diff_e_devolve_a_saida_dela(self):
        (self.raiz / "catraca-saida").write_text("3", encoding="utf-8")
        r = self.rodar("--afetados", "--base", "origin/x", ".githooks/pre-push")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertEqual((self.raiz / "catraca-rodou").read_text(encoding="utf-8"), "--base origin/x")

    def test_catraca_verde_e_custo_verde_dao_zero(self):
        r = self.rodar("--afetados", "scripts/protegido.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.raiz / "catraca-rodou").exists())

    def test_sem_teste_afetado_a_catraca_roda_mesmo_assim(self):
        (self.raiz / "tests" / "test_hooks_volta_corpus.py").unlink()
        (self.raiz / "catraca-saida").write_text("4", encoding="utf-8")
        r = self.rodar("--afetados", ".githooks/pre-push")
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertNotIn("nada a rodar", r.stdout)
        self.assertTrue((self.raiz / "catraca-rodou").exists())

    def test_custo_vermelho_reprova_mesmo_com_a_catraca_verde(self):
        (self.raiz / "tests" / "test_hooks_volta_corpus.py").write_text(
            CUSTO_DE_BRINQUEDO.replace("pass", "self.fail('custo')"), encoding="utf-8")
        r = self.rodar("--afetados", "scripts/protegido.py")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.raiz / "catraca-rodou").exists())


if __name__ == "__main__":
    unittest.main()
