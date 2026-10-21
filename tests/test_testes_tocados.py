"""`bin/forge-testes` (TA-3): teste dirigido na iteração do autor; não é portão."""
import importlib.machinery
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-testes"
AMBIENTE = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                           "GIT_COMMITTER_EMAIL": "t@t"})


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
            "bin/forge-changelog": ["test_changelog", "test_forge"],
            "bin/forge-doutor": ["test_atualizar", "test_doutor", "test_forge"],
            "bin/forge-sugerir": ["test_forge", "test_sugerir"],
            "scripts/ci-local": ["test_ci_local", "test_forge", "test_testes_tocados"],
        }
        for caminho, esperado in casos.items():
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), ("dirigido", esperado))

    def test_forge_check_roda_os_treze_modulos(self):
        modo, modulos = self.plano("bin/forge-check")
        self.assertEqual(modo, "dirigido")
        self.assertEqual(len(modulos), 13)
        self.assertIn("test_erros_no_brief", modulos)

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

    def test_caminhos_do_forge_publicado_incluem_test_atualizar(self):
        for caminho in ("migrations/0.7.0/migrar", "templates/projeto/CLAUDE.md", ".claude-plugin/plugin.json",
                        "bin/forge-doutor", "bin/forge", "hooks/doutor.py", "bin/forge-upgrade"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertIn("test_atualizar", modulos)

    def test_stacks_incluem_test_hooks(self):
        modo, modulos = self.plano("stacks/node-react/pesados.json")
        self.assertEqual(modo, "dirigido")
        self.assertIn("test_hooks", modulos)

    def test_modulo_importado_roda_quem_importa(self):
        modo, modulos = self.plano("tests/test_forge.py")
        self.assertEqual(modo, "dirigido")
        self.assertEqual(modulos, ["test_forge", "test_guarda_git", "test_hooks"])

    def test_o_proprio_modulo_de_teste_roda_sozinho(self):
        self.assertEqual(self.plano("tests/test_sugerir.py"), ("dirigido", ["test_sugerir"]))

    def test_varios_caminhos_unem_os_modulos(self):
        self.assertEqual(self.plano("bin/forge-sugerir", "tests/test_doutor.py"),
                         ("dirigido", ["test_doutor", "test_forge", "test_sugerir"]))

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


class MapaCobreOQueOsTestesLeem(unittest.TestCase):
    """Cada `RAIZ / "..."` de um tests/test_*.py que aponta para um arquivo do Forge tem de levar a esse módulo."""

    CAMINHO = re.compile(r'RAIZ\s*/\s*"([^"]+)"((?:\s*/\s*"[^"]+")*)')
    # Testes que só montam o próprio projeto de brinquedo e não dependem do conteúdo do Forge ficam de fora
    # por não citarem RAIZ; os módulos abaixo citam e são conferidos.

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def lidos(self, modulo):
        texto = (RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8")
        achados = set()
        for inicio, resto in self.CAMINHO.findall(texto):
            partes = [inicio] + re.findall(r'"([^"]+)"', resto)
            caminho = "/".join(partes)
            if (RAIZ / caminho).is_file():
                achados.add(caminho)
        return achados

    def test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo(self):
        modulos = sorted(p.stem for p in (RAIZ / "tests").glob("test_*.py"))
        total = 0
        for modulo in modulos:
            for caminho in sorted(self.lidos(modulo)):
                total += 1
                with self.subTest(modulo=modulo, caminho=caminho):
                    modo, planejados = self.f.planejar([caminho], RAIZ)
                    self.assertTrue(modo == "completo" or modulo in planejados, f"{caminho} -> {planejados}")
        self.assertGreaterEqual(total, 40)


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

    def test_arquivo_protegido_renomeado_cai_na_completa(self):
        (self.dir / "tests" / "config.json").write_text("{}\n", encoding="utf-8")
        (self.dir / "docs").mkdir()
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "config")
        git(self.dir, "switch", "-q", "-c", "melhoria/y")
        git(self.dir, "mv", "tests/config.json", "docs/config.json")
        git(self.dir, "commit", "-qm", "move")
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "melhoria/x", "--listar"], cwd=self.dir,
                           env=AMBIENTE, capture_output=True, text=True)
        self.assertIn("suíte completa (tests/config.json altera o mapa ou a configuração)", r.stdout)

    def test_arquivo_mapeado_renomeado_inclui_os_modulos_do_caminho_antigo(self):
        (self.dir / "bin").mkdir()
        (self.dir / "bin" / "forge-sugerir").write_text("x = 1\n", encoding="utf-8")
        (self.dir / "tests" / "test_forge.py").write_text("x = 1\n", encoding="utf-8")  # o mapa também o cita
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "bin")
        git(self.dir, "switch", "-q", "-c", "melhoria/z")
        git(self.dir, "mv", "bin/forge-sugerir", "tests/test_novo.py")
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "melhoria/x", "--listar"], cwd=self.dir,
                           env=AMBIENTE, capture_output=True, text=True)
        self.assertIn("dirigido (test_forge, test_novo, test_sugerir)", r.stdout)

    def test_nada_alterado_nao_roda(self):
        r = self.rodar()
        self.assertIn("nada alterado", r.stdout)
        self.assertFalse((self.dir / ".forge").exists())


class NaoEPortao(unittest.TestCase):
    """Decisão do dono: "A, desde que para main rode tudo." Nenhum portão chama o script."""

    def test_nenhum_portao_cita_o_script(self):
        alvos = [RAIZ / ".githooks", RAIZ / ".github", RAIZ / "hooks", RAIZ / "scripts" / "ci-local",
                 RAIZ / "bin" / "forge-check"]
        arquivos = []
        for alvo in alvos:
            # __pycache__ fica de fora: o .pyc guarda o caminho da worktree, que pode se chamar forge-testes-*
            arquivos += [alvo] if alvo.is_file() else [p for p in alvo.rglob("*")
                                                       if p.is_file() and "__pycache__" not in p.parts]
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


class MapaDoForgeCheck(unittest.TestCase):
    """O mapa de `bin/forge-check` lista todo módulo que importa ou executa o script (FORGE-TESTES-MAPA)."""

    CITA = re.compile(r'bin/forge-check|"bin"\s*[,/]\s*"forge-check"|joinpath\("bin",\s*"forge-check"\)')
    IMPORTA = re.compile(r"^\s*(?:from|import)\s+(test_[a-z0-9_]+)\b", re.M)

    def modulos_que_usam(self):
        textos = {p.stem: p.read_text(encoding="utf-8") for p in (RAIZ / "tests").glob("test_*.py")}
        usam = {m for m, t in textos.items() if self.CITA.search(t)}
        usam.discard("test_doutor")  # só grava um `bin/forge-check` falso na semente; não executa o real
        usam.add("test_catraca")  # carrega o script por `catraca.forge_check()`, sem citar o caminho
        mudou = True
        while mudou:  # quem importa um módulo que usa o script também o executa
            mudou = False
            for m, t in textos.items():
                if m not in usam and usam & set(self.IMPORTA.findall(t)):
                    usam.add(m)
                    mudou = True
        return usam

    def test_mapa_lista_todo_modulo_que_usa_o_forge_check(self):
        usam = self.modulos_que_usam()
        self.assertGreaterEqual(len(usam), 8)
        listados = set(carregar().FORGE_CHECK)
        self.assertEqual(sorted(usam - listados), [], "faltam no mapa FORGE_CHECK")
        self.assertEqual(sorted(listados - usam), [], "sobram no mapa FORGE_CHECK")

    def test_erros_no_brief_roda_quando_so_o_forge_check_muda(self):
        modo, modulos = carregar().planejar(["bin/forge-check"], RAIZ)
        self.assertEqual(modo, "dirigido")
        self.assertIn("test_erros_no_brief", modulos)


if __name__ == "__main__":
    unittest.main()
