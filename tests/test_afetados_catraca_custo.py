"""E9.1 (v048, AFETADOS-CATRACA-E-CUSTO): o diff que toca hooks/, bin/ ou um arquivo protegido da catraca leva ao plano
dirigido do `bin/forge-testes` a catraca no modo do diff e o teste de custo (`test_hooks_volta_corpus`); o resto fica como
estava. O #957 nasceu vermelho na catraca e o #940 e o #944 no teste de custo, com os afetados verdes no computador.
E9.2 (ajuste do dono de 28/11 11:19): o plano do `--afetados` acima de LIMITE_LOCAL testes roda só a catraca, o teste de
custo e os testes do arquivo mudado, e diz quantos ficaram para o CI."""
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
        for caminho in ("hooks/a.py", "bin/forge-x", "scripts/outro.py", ".githooks/pre-push", "scripts/protegido.py"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.plano("docs/guia.md", caminho), (("test_hooks_volta_corpus",), True))

    def test_o_resto_fica_como_esta(self):
        for caminho in ("docs/guia.md", "lib/scripts/x.py", "docs/hooks/x.md", "tests/bin/x", "tests/scripts/x"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.plano(caminho), ((), False))
        self.assertEqual(self.plano(), ((), False))

    def test_sem_a_catraca_nada_muda(self):
        (self.raiz / "tests" / "catraca.py").unlink()
        self.assertEqual(self.plano("bin/forge-x"), ((), False))

    def test_catraca_em_link_pede_a_catraca_e_nao_e_rodavel(self):  # falha fechada (segurança c7df039 A1)
        alvo = self.raiz / "fora.py"
        (self.raiz / "tests" / "catraca.py").rename(alvo)
        (self.raiz / "tests" / "catraca.py").symlink_to(alvo)
        for caminhos in (("docs/guia.md",), ("bin/forge-x",), ()):
            with self.subTest(caminhos=caminhos):
                self.assertEqual(self.plano(*caminhos), (("test_hooks_volta_corpus",), True))
        self.assertFalse(self.f.catraca_rodavel(self.raiz))

    def test_catraca_apagada_no_diff_pede_a_catraca(self):  # falha fechada (segurança c7df039 A1)
        (self.raiz / "tests" / "catraca.py").unlink()
        self.assertEqual(self.plano("tests/catraca.py"), (("test_hooks_volta_corpus",), True))
        self.assertEqual(self.plano("docs/guia.md"), ((), False))  # o projeto sem catraca segue sem ela
        self.assertFalse(self.f.catraca_rodavel(self.raiz))

    def test_catraca_comum_e_rodavel(self):
        self.assertTrue(self.f.catraca_rodavel(self.raiz))

    def test_sem_o_teste_de_custo_so_a_catraca(self):
        (self.raiz / "tests" / "test_hooks_volta_corpus.py").unlink()
        self.assertEqual(self.plano("hooks/a.py"), ((), True))

    def test_protegidos_ilegiveis_contam_como_tocados(self):  # falha fechada
        for texto in ("PROTEGIDOS = (", "PROTEGIDOS = ()\n", "PROTEGIDOS = ['.githooks/']\n", "PROTEGIDOS = (1,)\n",
                      "PROTEGIDOS = tuple()\n", "OUTRA = ('.githooks/',)\n"):
            with self.subTest(texto=texto):
                (self.raiz / "tests" / "catraca.py").write_text(texto, encoding="utf-8")
                self.assertEqual(self.plano("docs/guia.md"), (("test_hooks_volta_corpus",), True))


def modulo_com(testes, cita=""):
    """Um módulo de teste com `testes` métodos test_*, um setUp e um auxiliar (que não contam) e o texto `cita`."""
    corpo = "".join(f"    def test_{i}(self):\n        pass\n\n" for i in range(testes))
    return (f"import unittest\n# {cita}\n\n\nclass T(unittest.TestCase):\n    def setUp(self):\n        pass\n\n"
            f"    def ajuda(self):\n        pass\n\n{corpo}")


class LimiteLocal(Brinquedo):
    """E9.2: a contagem do plano e os testes do arquivo mudado."""

    def test_conta_so_os_metodos_test_das_classes(self):
        (self.raiz / "tests" / "test_a.py").write_text(modulo_com(3) + "\n\ndef test_solto():\n    pass\n", encoding="utf-8")
        (self.raiz / "tests" / "test_ruim.py").write_text("def (", encoding="utf-8")
        self.assertEqual(self.f.contar_testes(["test_a", "test_ruim", "test_ausente", "test_hooks_volta_corpus"], self.raiz), 4)

    def test_testes_do_arquivo_mudado(self):
        for nome in ("test_protegido", "test_x", "test_forge", "test_novo"):
            (self.raiz / "tests" / f"{nome}.py").write_text(modulo_com(1), encoding="utf-8")
        caminhos = ["scripts/protegido.py", "bin/forge-x", "tests/test_novo.py", "lib/sem_teste.py", "docs/guia.md"]
        self.assertEqual(self.f.testes_do_arquivo(caminhos, self.raiz), {"test_protegido", "test_x", "test_novo"})
        self.assertEqual(self.f.testes_do_arquivo(["bin/forge-testes"], RAIZ), {"test_testes_tocados"})  # o MAPA, sem test_forge

    def test_o_limite_esta_num_lugar_so(self):
        self.assertEqual(self.f.LIMITE_LOCAL, 1000)


class ListaDaCatracaReal(unittest.TestCase):
    """A lista vem da PROTEGIDOS de tests/catraca.py, sem cópia: um protegido fora de hooks/ e bin/ a pede."""

    def test_le_a_protegidos_da_catraca_do_forge(self):
        f = carregar()
        protegidos = f.protegidos_da_catraca(RAIZ / "tests" / "catraca.py")
        self.assertIn("scripts/conferir-release.py", protegidos)
        self.assertIn(".github/workflows/", protegidos)
        self.assertEqual(f.custo_e_catraca(["scripts/conferir-release.py"], RAIZ), (("test_hooks_volta_corpus",), True))
        self.assertEqual(f.custo_e_catraca(["docs/guia.md"], RAIZ), ((), False))


class RecorteDoMutante(unittest.TestCase):
    """Review e QA c7df039 A1 (sonda S1): com a catraca no plano, o modulos_listados do forge-mutante, que lê o stdout
    inteiro do --listar, segue dando o recorte H5 do diff em bin/ (antes, conjunto vazio)."""

    def test_modulos_listados_de_bin_forge_mutante(self):
        carregador = importlib.machinery.SourceFileLoader("forge_mutante_e92", str(RAIZ / "bin" / "forge-mutante"))
        spec = importlib.util.spec_from_loader("forge_mutante_e92", carregador)
        mutante = importlib.util.module_from_spec(spec)
        carregador.exec_module(mutante)
        listados = mutante.modulos_listados(["bin/forge-mutante"])
        self.assertLessEqual({"test_forge_mutante", "test_hooks_volta_corpus", "test_pre_push_patch"}, listados)


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

    def plano_com(self, grandes):
        """Plano de `scripts/protegido.py`: o teste de custo (1), o test_protegido (1) e um test_grande que o cita."""
        (self.raiz / "tests" / "test_protegido.py").write_text(modulo_com(1), encoding="utf-8")
        (self.raiz / "tests" / "test_grande.py").write_text(modulo_com(grandes, "scripts/protegido.py"), encoding="utf-8")
        return self.rodar("--afetados", "--listar", "scripts/protegido.py")

    def test_no_limite_o_plano_fica_inteiro(self):  # 998 + 1 + 1 = 1000, não passa do limite
        r = self.plano_com(998)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0],
                         "forge-testes: dirigido (test_grande, test_hooks_volta_corpus, test_protegido). O CI do PR roda a suíte inteira.")
        self.assertNotIn("limite local", r.stderr)

    def test_acima_do_limite_so_catraca_custo_e_o_arquivo_e_diz_o_que_fica(self):  # 999 + 1 + 1 = 1001
        r = self.plano_com(999)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0],
                         "forge-testes: dirigido (test_hooks_volta_corpus, test_protegido). O CI do PR roda a suíte inteira.")
        self.assertIn("forge-testes: catraca no diff", r.stderr)
        self.assertIn("plano de 1001 testes passa do limite local de 1000", r.stderr)
        self.assertIn("999 testes ficam para o CI do PR", r.stderr)

    def test_o_limite_vale_so_para_os_afetados(self):
        (self.raiz / "tests" / "test_grande.py").write_text(modulo_com(1001, "x"), encoding="utf-8")
        r = self.rodar("--listar", "tests/test_grande.py")
        self.assertIn("test_grande", r.stdout)
        self.assertNotIn("limite local", r.stderr)

    def test_listar_mostra_a_catraca_e_o_custo_para_bin(self):
        r = self.rodar("--afetados", "--listar", "bin/forge-testes")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("forge-testes: dirigido ("), r.stdout)
        self.assertIn("test_hooks_volta_corpus", r.stdout.splitlines()[0])
        self.assertIn("forge-testes: catraca no diff (tests/catraca.py --base origin/develop)", r.stderr)
        self.assertEqual(len(r.stdout.splitlines()), 1, r.stdout)  # o plano numa linha só (review c7df039 A1)
        self.assertNotIn("não roda", r.stderr)
        self.assertFalse((self.raiz / "catraca-rodou").exists())

    def test_listar_sem_hook_bin_nem_protegido_fica_como_esta(self):
        r = self.rodar("--afetados", "--listar", "docs/guia.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("catraca", r.stdout + r.stderr)
        self.assertNotIn("test_hooks_volta_corpus", r.stdout)

    def test_catraca_em_link_reprova_sem_executar(self):  # falha fechada (segurança c7df039 A1)
        alvo = self.raiz / "fora.py"
        (self.raiz / "tests" / "catraca.py").rename(alvo)
        (self.raiz / "tests" / "catraca.py").symlink_to(alvo)
        r = self.rodar("--afetados", "docs/guia.md")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tests/catraca.py apagado ou trocado por link: a catraca não roda e o plano reprova", r.stderr)
        self.assertFalse((self.raiz / "catraca-rodou").exists())

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
