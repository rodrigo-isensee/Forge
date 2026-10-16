"""`bin/forge-testes` (TA-3): teste dirigido na iteração do autor; não é portão."""
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-testes"
AMBIENTE = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def carregar():
    carregador = importlib.machinery.SourceFileLoader("forge_testes", str(FERRAMENTA))
    spec = importlib.util.spec_from_loader("forge_testes", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=AMBIENTE, capture_output=True, text=True, check=True).stdout


class Mapa(unittest.TestCase):
    """O mapa de caminhos conhecidos e a falha fechada."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def plano(self, *caminhos):
        return self.f.planejar(list(caminhos), RAIZ)

    def test_caminhos_conhecidos_rodam_so_os_modulos_do_mapa(self):
        casos = {
            "bin/forge-changelog": ["test_changelog"],
            "bin/forge-doutor": ["test_doutor"],
            "bin/forge-sugerir": ["test_sugerir"],
            "scripts/ci-local": ["test_ci_local"],
        }
        for caminho, esperado in casos.items():
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), ("dirigido", esperado))

    def test_forge_check_roda_os_tres_modulos(self):
        self.assertEqual(self.plano("bin/forge-check"),
                         ("dirigido", ["test_forge", "test_portao_diff_proprio", "test_sobreposicao_quadro"]))

    def test_hooks_incluem_hooks_e_catraca(self):
        modo, modulos = self.plano("hooks/conformidade.py")
        self.assertEqual(modo, "dirigido")
        self.assertIn("test_hooks", modulos)
        self.assertIn("test_catraca", modulos)

    def test_conteudo_da_fabrica_roda_test_forge(self):
        for caminho in ("agents/jarvis.md", "skills/kanban-scrum/SKILL.md", "docs/economia-de-tokens.md",
                        "templates/projeto/CLAUDE.md", "stacks/x/pronto.md"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertIn("test_forge", modulos)

    def test_o_proprio_modulo_de_teste_roda_sozinho(self):
        self.assertEqual(self.plano("tests/test_sugerir.py"), ("dirigido", ["test_sugerir"]))

    def test_varios_caminhos_unem_os_modulos(self):
        self.assertEqual(self.plano("bin/forge-sugerir", "tests/test_doutor.py"),
                         ("dirigido", ["test_doutor", "test_sugerir"]))

    def test_caminho_sem_mapa_cai_na_completa(self):
        for caminho in ("coisa-nova/x.py", ".github/workflows/ci.yml", ".githooks/pre-push", "LICENSE",
                        "tests/catraca.py", "tests/fixtures/a.txt", "bin/forge-inexistente"):
            with self.subTest(caminho):
                self.assertEqual(self.plano("bin/forge-sugerir", caminho)[0], "completo")

    def test_config_e_o_proprio_mapa_caem_na_completa(self):
        for caminho in ("tests/config.json", "bin/forge-testes"):
            with self.subTest(caminho):
                self.assertEqual(self.plano("bin/forge-sugerir", caminho)[0], "completo")

    def test_modulo_mapeado_sem_arquivo_cai_na_completa(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "tests").mkdir()
            self.assertEqual(self.f.planejar(["bin/forge-sugerir"], Path(t))[0], "completo")

    def test_todo_modulo_do_mapa_existe(self):
        modulos = {m for _, destino in self.f.MAPA if destino for m in destino}
        self.assertGreaterEqual(len(modulos), 10)
        for m in sorted(modulos):
            with self.subTest(m):
                self.assertTrue((RAIZ / "tests" / f"{m}.py").is_file())


class Execucao(unittest.TestCase):
    """Roda o script de verdade num repositório de brinquedo."""

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        git(self.dir, "init", "-q", "-b", "develop")
        (self.dir / "tests").mkdir()
        (self.dir / "tests" / "test_sugerir.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n", encoding="utf-8")
        (self.dir / "tests" / "test_outro.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n", encoding="utf-8")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "base")
        git(self.dir, "switch", "-q", "-c", "melhoria/x")

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(FERRAMENTA), "--base", "develop", *args], cwd=self.dir,
                              env=AMBIENTE, capture_output=True, text=True)

    def log(self):
        return (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8")

    def test_dirigido_roda_so_o_modulo_tocado_e_anota_o_log(self):
        (self.dir / "tests" / "test_sugerir.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n# x\n", encoding="utf-8")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dirigido (test_sugerir)", r.stdout)
        linha = self.log().strip().splitlines()[-1]
        for trecho in ("modo=dirigido", "modulos=test_sugerir", "duracao=", "saida=0", "Z "):
            self.assertIn(trecho, linha)

    def test_arquivo_novo_nao_versionado_conta(self):
        (self.dir / "tests" / "test_novo.py").write_text("x = 1\n", encoding="utf-8")
        r = self.rodar("--listar")
        self.assertIn("dirigido (test_novo)", r.stdout)

    def test_sem_mapa_roda_a_completa_e_anota(self):
        (self.dir / "novo.txt").write_text("x\n", encoding="utf-8")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("suíte completa (novo.txt sem mapa)", r.stdout)
        self.assertIn("modo=completo", self.log())

    def test_completa_pedida_e_listar_nao_roda_nada(self):
        self.assertEqual(self.rodar("--listar", "--completa").returncode, 0)
        self.assertFalse((self.dir / ".forge").exists())
        self.assertEqual(self.rodar("--completa").returncode, 0)
        self.assertIn("modo=completo", self.log())

    def test_falha_de_teste_devolve_codigo_e_anota(self):
        (self.dir / "tests" / "test_sugerir.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ruim(self):\n        self.fail('x')\n",
            encoding="utf-8")
        r = self.rodar()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("saida=1", self.log())

    def test_base_ilegivel_cai_na_completa(self):
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "nao-existe"], cwd=self.dir, env=AMBIENTE,
                           capture_output=True, text=True)
        self.assertIn("suíte completa (não consegui ler o git", r.stdout)

    def test_nada_alterado_nao_roda(self):
        r = self.rodar()
        self.assertIn("nada alterado", r.stdout)
        self.assertFalse((self.dir / ".forge").exists())


class NaoEPortao(unittest.TestCase):
    """Decisão do dono: "A, desde que para main rode tudo." Nenhum portão chama o script."""

    def test_nenhum_portao_cita_o_script(self):
        alvos = [RAIZ / ".githooks", RAIZ / ".github", RAIZ / "hooks", RAIZ / "scripts" / "ci-local"]
        arquivos = []
        for alvo in alvos:
            arquivos += [alvo] if alvo.is_file() else [p for p in alvo.rglob("*") if p.is_file()]
        self.assertGreaterEqual(len(arquivos), 5)
        for arquivo in arquivos:
            with self.subTest(str(arquivo.relative_to(RAIZ))):
                self.assertNotIn("forge-testes", arquivo.read_text(encoding="utf-8", errors="replace"))

    def test_pre_push_roda_a_suite_inteira(self):
        self.assertIn("python3 -m unittest discover -s tests",
                      (RAIZ / ".githooks" / "pre-push").read_text(encoding="utf-8"))

    def test_regra_5_cita_o_script_e_a_decisao_do_dono(self):
        texto = (RAIZ / "docs" / "economia-de-tokens.md").read_text(encoding="utf-8")
        self.assertIn("bin/forge-testes", texto)
        self.assertIn("A, desde que para main rode tudo.", texto)

    def test_log_fica_fora_do_git(self):
        self.assertIn("/.forge", (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    unittest.main()
