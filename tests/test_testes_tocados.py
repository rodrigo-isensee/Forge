"""`bin/forge-testes` (TA-3): teste dirigido na iteração do autor; filtro do pre-push (EST-M8), nunca portão de CI."""
import ast
import importlib.machinery
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
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
            "bin/forge-changelog": ["test_changelog", "test_conferir_release", "test_forge"],
            "bin/forge-doutor": ["test_atualizar", "test_doutor", "test_forge"],
            "bin/forge-sugerir": ["test_forge", "test_sugerir"],
            "scripts/ci-local": ["test_ci_local", "test_forge", "test_testes_tocados"],
        }
        for caminho, esperado in casos.items():
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), ("dirigido", esperado))

    def test_forge_check_roda_os_modulos_dele(self):
        modo, modulos = self.plano("bin/forge-check")
        self.assertEqual(modo, "dirigido")
        self.assertEqual(len(modulos), 21)
        for modulo in ("test_erros_no_brief", "test_conferencia_base_dono", "test_anotar", "test_isencoes", "test_citacao", "test_medidas_m14b"):
            self.assertIn(modulo, modulos)

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

    # M8, opção C (critério de fim, item 3): módulo de teste no diff não tem regra e roda a suíte inteira.
    def test_modulo_de_teste_no_diff_cai_na_completa_com_o_motivo_sem_mapa(self):
        for caminho in ("tests/test_fechar.py",  # importado por 13 `test_fechar_*`
                        "tests/test_sugerir.py",  # que ninguém importa
                        "tests/test_modulo_novo_que_nao_existe.py",  # novo ou apagado: o arquivo não está lá
                        "tests/test_forge.py"):
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), ("completo", [f"{caminho} sem mapa"]))

    def test_codigo_sem_teste_segue_dirigido(self):
        self.assertEqual(self.plano("bin/forge-sugerir"), ("dirigido", ["test_forge", "test_sugerir"]))

    def test_modulo_de_teste_junto_de_outro_caminho_leva_tudo_a_completa(self):
        self.assertEqual(self.plano("bin/forge-sugerir", "tests/test_doutor.py"), ("completo", ["tests/test_doutor.py sem mapa"]))

    def test_o_mapa_nao_guarda_regra_nem_grafo_de_modulo_de_teste(self):
        self.assertFalse(hasattr(self.f, "IMPORTADO_POR"))
        self.assertFalse([p for p, _ in self.f.MAPA if re.fullmatch(p, "tests/test_sugerir.py")])

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
    """Cada arquivo do Forge que um tests/test_*.py lê ou executa tem de levar a esse módulo (o pre-push filtra por isto).

    Formas reconhecidas (ast, não regex): `RAIZ / "a" / "b"`, `RAIZ.joinpath(...)`, uma variável de módulo que guarda
    um caminho (`HOOKS = RAIZ / "hooks"` ou `...parent.parent / "hooks"`) usada como `HOOKS / "x.py"`, e `ler("...")`.
    Quando o módulo monta o caminho com uma variável (`RAIZ / rel`), todo literal do módulo que é um arquivo do
    Forge conta: falha fechada, o mapa tem de ser tão largo quanto o que o teste pode ler."""

    # Este próprio módulo só passa caminhos como texto para `planejar`: não os lê.
    SO_CITA = {"test_testes_tocados"}

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    @classmethod
    def partes(cls, no, vars_):
        """Caminho relativo à raiz (tupla) de uma expressão de caminho, ou None; "*" marca a parte dada por variável."""
        if isinstance(no, ast.Constant) and isinstance(no.value, str):
            return tuple(p for p in no.value.split("/") if p)
        if isinstance(no, ast.Name):
            return vars_.get(no.id)
        if isinstance(no, ast.BinOp) and isinstance(no.op, ast.Div):
            esq = cls.partes(no.left, vars_)
            if esq is None:
                return None
            direita = cls.partes(no.right, vars_) if isinstance(no.right, ast.Constant) else None
            return esq + (direita if direita is not None else ("*",))
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr == "joinpath":
            base = cls.partes(no.func.value, vars_)
            if base is None:
                return None
            for arg in no.args:
                p = cls.partes(arg, vars_) if isinstance(arg, ast.Constant) else None
                base = base + (p if p is not None else ("*",))
            return base
        if isinstance(no, ast.Attribute) and no.attr == "parent":  # Path(__file__).resolve().parent[.parent]
            dentro = no.value
            if isinstance(dentro, ast.Attribute) and dentro.attr == "parent":
                return () if ast.unparse(dentro.value) in ("Path(__file__).resolve()", "Path(__file__)") else None
            return ("tests",) if ast.unparse(dentro) in ("Path(__file__).resolve()", "Path(__file__)") else None
        return None

    @classmethod
    def variaveis(cls, arvore):
        """Variáveis de módulo que guardam um caminho fixo (tupla relativa à raiz)."""
        vars_ = {"RAIZ": ()}
        for no in arvore.body:
            if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
                p = cls.partes(no.value, vars_)
                if p is not None and "*" not in p:
                    vars_.setdefault(no.targets[0].id, p)
        return vars_

    def lidos(self, modulo):
        return self.lidos_do_texto(modulo, (RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))

    def lidos_do_texto(self, modulo, texto):
        arvore = ast.parse(texto)
        vars_ = self.variaveis(arvore)
        achados, dinamico = set(), False
        for no in ast.walk(arvore):
            candidato = None
            if isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id == "ler":
                if no.args and isinstance(no.args[0], ast.Constant) and isinstance(no.args[0].value, str):
                    candidato = tuple(p for p in no.args[0].value.split("/") if p)
            elif (isinstance(no, ast.BinOp) and isinstance(no.op, ast.Div)) or isinstance(no, ast.Call):
                candidato = self.partes(no, vars_)
            if candidato is None:
                continue
            if "*" in candidato:
                dinamico = True
                candidato = candidato[:candidato.index("*")]
            if candidato and (RAIZ / Path(*candidato)).is_file():
                achados.add("/".join(candidato))
        if dinamico and modulo not in self.SO_CITA:
            for no in ast.walk(arvore):
                if isinstance(no, ast.Constant) and isinstance(no.value, str) and "/" in no.value \
                        and "\n" not in no.value and (RAIZ / no.value).is_file():
                    achados.add(no.value)
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

    def test_a_conferencia_enxerga_as_formas_de_citar_um_caminho(self):  # LOTE-M8-PREPUSH (seg A1)
        fonte = (
            "from pathlib import Path\n"
            "RAIZ = Path(__file__).resolve().parent.parent\n"
            "HOOKS = Path(__file__).resolve().parent.parent / 'hooks'\n"
            "def ler(rel):\n    return (RAIZ / rel).read_text()\n"
            "a = HOOKS / 'agentes.py'\n"
            "b = ler('hooks/vigia.py')\n"
            "c = RAIZ.joinpath('bin', 'forge-changelog')\n"
            "def f(rel):\n    return RAIZ / rel\n"
            "d = ('docs/regras/R-BRIEF.md',)\n"
        )
        self.assertEqual(self.lidos_do_texto("test_x", fonte),
                         {"hooks/agentes.py", "hooks/vigia.py", "bin/forge-changelog", "docs/regras/R-BRIEF.md"})

    def test_a_familia_dos_testes_que_executam_hooks_e_bin_roda_no_envio_dirigido(self):  # LOTE-M8-PREPUSH (seg A1)
        for caminho, modulo in (("hooks/agentes.py", "test_agentes_hash_brief"), ("hooks/agentes.py", "test_agentes_clone"),
                                ("hooks/_comum.py", "test_agentes_hash_brief"), ("hooks/_comum.py", "test_agentes_clone"),
                                ("hooks/vigia.py", "test_textos_dono_f10"), ("bin/forge-changelog", "test_conferir_release"),
                                ("agents/jarvis.md", "test_clareza")):
            with self.subTest(caminho=caminho, modulo=modulo):
                self.assertIn(modulo, self.f.planejar([caminho], RAIZ)[1])

    def test_manifesto_do_plugin_de_dev_tem_regra_no_mapa_e_nao_cai_na_suite_completa(self):  # FORGE-TESTES-CAMINHOS
        modo, modulos = self.f.planejar(["dev/.claude-plugin/plugin.json"], RAIZ)
        self.assertEqual(modo, "dirigido")
        self.assertEqual(modulos, self.f.planejar([".claude-plugin/plugin.json"], RAIZ)[1])

    def test_conferir_reversao_tem_regra_no_mapa_e_nao_cai_na_suite_completa(self):  # REVERSAO-MAPA (A5)
        self.assertEqual(self.f.planejar(["scripts/conferir-reversao.py"], RAIZ),
                         ("dirigido", ["test_conferir_reversao", "test_forge", "test_testes_tocados"]))

    def test_forge_mutante_tem_regra_no_mapa_e_nao_cai_na_suite_completa(self):
        self.assertEqual(self.f.planejar(["bin/forge-mutante"], RAIZ), ("dirigido", ["test_forge", "test_forge_mutante"]))


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
        for modulo in ("test_outro", "test_forge"):
            (self.dir / "tests" / f"{modulo}.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n", encoding="utf-8")
        (self.dir / "bin").mkdir()
        (self.dir / "bin" / "forge-sugerir").write_text("x = 1\n", encoding="utf-8")  # o mapa leva a test_forge e test_sugerir
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "base")
        git(self.dir, "switch", "-q", "-c", "melhoria/x")

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(FERRAMENTA), "--base", "develop", *args], cwd=self.dir,
                              env=AMBIENTE, capture_output=True, text=True)

    def log(self):
        return (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8")

    def test_dirigido_roda_so_os_modulos_do_mapa_e_anota_o_log(self):
        (self.dir / "bin" / "forge-sugerir").write_text("x = 2\n", encoding="utf-8")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout)
        self.assertNotIn("test_outro", r.stdout)
        linha = self.log().strip().splitlines()[-1]
        for trecho in ("modo=dirigido", "modulos=test_forge,test_sugerir", "duracao=", "saida=0", "Z "):
            self.assertIn(trecho, linha)

    def test_arquivo_novo_nao_versionado_conta(self):
        (self.dir / "tests" / "test_novo.py").write_text("x = 1\n", encoding="utf-8")
        r = self.rodar("--listar")
        self.assertIn("suíte completa (tests/test_novo.py sem mapa)", r.stdout)  # o teste novo leva à completa

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
        (self.dir / "tests" / "test_forge_mutante.py").write_text("x = 1\n", encoding="utf-8")  # o mapa de bin/forge-mutante o cita
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "bin")
        git(self.dir, "switch", "-q", "-c", "melhoria/z")
        git(self.dir, "mv", "bin/forge-sugerir", "bin/forge-mutante")
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "melhoria/x", "--listar"], cwd=self.dir,
                           env=AMBIENTE, capture_output=True, text=True)
        self.assertIn("dirigido (test_forge, test_forge_mutante, test_sugerir)", r.stdout)  # test_sugerir vem do caminho antigo

    # FORGE-TESTES-CAMINHOS: classe "a ferramenta recusa a forma de chamada que os briefs mandam usar". Variantes:
    # caminho relativo, absoluto, com `..`, a partir de subpasta, vários, fora do repositório, junto de opção
    # incompatível e caminho começado por `-` (depois de `--`).
    def rodar_com(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(FERRAMENTA), *args], cwd=cwd or self.dir, env=AMBIENTE,
                              capture_output=True, text=True)

    def test_caminhos_dirigem_o_plano_sem_olhar_o_git(self):
        r = self.rodar_com("--listar", "bin/forge-sugerir", "bin/forge-sugerir")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout)
        self.assertFalse((self.dir / ".forge").exists())

    def test_caminho_sem_mapa_cai_na_completa_e_o_alterado_no_git_nao_conta(self):
        (self.dir / "tests" / "test_sugerir.py").write_text("x = 1\n", encoding="utf-8")  # alterado, mas não citado
        r = self.rodar_com("--listar", "novo.txt")
        self.assertIn("suíte completa (novo.txt sem mapa)", r.stdout)

    def test_caminho_absoluto_com_ponto_ponto_e_de_subpasta_valem(self):
        (self.dir / "sub").mkdir()
        absoluto = str(self.dir / "bin" / "forge-sugerir")
        for args, cwd in (((absoluto,), None), (("sub/../bin/forge-sugerir",), None),
                          (("../bin/forge-sugerir",), self.dir / "sub")):
            with self.subTest(args=args, cwd=cwd):
                r = self.rodar_com("--listar", *args, cwd=cwd)
                self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout, r.stdout + r.stderr)

    def test_caminho_fora_do_repositorio_e_recusado(self):
        r = self.rodar_com("--listar", "../fora.py")
        self.assertEqual(r.returncode, 2)
        self.assertIn("fora do repositório", r.stderr)
        self.assertNotIn("dirigido", r.stdout)

    def test_caminhos_nao_combinam_com_completa_nem_com_vermelho(self):
        for opcao in (("--completa",), ("--vermelho", "HEAD")):  # o `--vermelho` consome o argumento seguinte como base
            with self.subTest(opcao):
                r = self.rodar_com(*opcao, "tests/test_sugerir.py")
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("caminhos não combinam", r.stderr)

    def test_caminho_comecado_por_hifen_so_depois_de_dois_hifens(self):
        r = self.rodar_com("--listar", "--", "-x.py")
        self.assertIn("suíte completa (-x.py sem mapa)", r.stdout)

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


class MapaCobreImportacaoEVarredura(unittest.TestCase):
    """M8, opção C: o que um teste executa de outro teste ou varre de uma pasta não precisa de grafo no mapa, porque
    módulo de teste no diff roda a suíte inteira; estas conferências provam isso para as formas que o repositório usa
    (importação entre testes, estática e dinâmica; `glob`, `rglob` e `iterdir` sobre caminho conhecido)."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()
        cls.testes = sorted(p.stem for p in (RAIZ / "tests").glob("test_*.py"))

    def importados(self, texto):
        """(módulos de teste importados por nome, há importação dinâmica de nome montado). Qualquer nível do código."""
        achados, dinamico = set(), False
        for no in ast.walk(ast.parse(texto)):
            if isinstance(no, ast.Import):
                achados.update(a.name for a in no.names if re.fullmatch(r"test_[a-z0-9_]+", a.name))
            elif isinstance(no, ast.ImportFrom) and no.module and re.fullmatch(r"test_[a-z0-9_]+", no.module) and not no.level:
                achados.add(no.module)
            elif isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr == "import_module" \
                    and no.args:
                arg = no.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    achados.update(m for m in (arg.value.split(".")[-1],) if re.fullmatch(r"test_[a-z0-9_]+", m))
                else:
                    dinamico = True
        return achados, dinamico

    def varridos(self, texto):
        """Arquivos do Forge que um `glob`, `rglob` ou `iterdir` sobre caminho conhecido alcança, e a pasta varrida."""
        arvore = ast.parse(texto)
        vars_ = MapaCobreOQueOsTestesLeem.variaveis(arvore)
        achados, pastas = set(), set()
        for no in ast.walk(arvore):
            if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)
                    and no.func.attr in ("glob", "rglob", "iterdir")):
                continue
            base = MapaCobreOQueOsTestesLeem.partes(no.func.value, vars_)
            if base is None or "*" in base or not (RAIZ / Path(*base)).is_dir():
                continue
            pasta = RAIZ / Path(*base)
            padrao = no.args[0].value if no.args and isinstance(no.args[0], ast.Constant) else "*"
            casados = pasta.iterdir() if no.func.attr == "iterdir" else getattr(pasta, no.func.attr)(padrao)
            pastas.add("/".join(base))
            achados.update(c.relative_to(RAIZ).as_posix() for c in casados if c.is_file() and "__pycache__" not in c.parts)
        return achados, pastas

    def cobre(self, caminho, modulo):
        modo, planejados = self.f.planejar([caminho], RAIZ)
        return modo == "completo" or modulo in planejados

    def test_todo_teste_importado_por_outro_leva_quem_importa_a_suite_inteira(self):  # critério C.1
        arestas = 0
        for modulo in self.testes:
            importados, _ = self.importados((RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))
            for importado in sorted(importados & set(self.testes)):
                arestas += 1
                with self.subTest(modulo=modulo, importado=importado):
                    self.assertTrue(self.cobre(f"tests/{importado}.py", modulo))
                    self.assertEqual(self.f.planejar([f"tests/{importado}.py"], RAIZ)[0], "completo")
        self.assertGreaterEqual(arestas, 31)  # as 31 linhas de `import`/`from` entre testes na varredura da segurança

    def test_os_modulos_importados_por_outros_sao_os_conhecidos(self):  # critério C.1 (o conjunto não encolhe)
        importados = set()
        for modulo in self.testes:
            achados, _ = self.importados((RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))
            importados |= achados & set(self.testes)
        self.assertLessEqual({"test_fechar", "test_forge", "test_voltas", "test_volta_por_delta", "test_doutor",
                              "test_hooks", "test_atualizar"}, importados)

    def test_toda_varredura_de_pasta_conhecida_leva_o_modulo_a_suite_inteira_ou_ao_plano(self):  # critério C.2
        total, varrem_tests = 0, set()
        for modulo in self.testes:
            achados, pastas = self.varridos((RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))
            if "tests" in pastas:
                varrem_tests.add(modulo)
            for caminho in sorted(achados):
                total += 1
                with self.subTest(modulo=modulo, caminho=caminho):
                    self.assertTrue(self.cobre(caminho, modulo))
        self.assertGreaterEqual(total, 1000)
        # quem varre `tests/` cai quando um módulo de teste muda: todo módulo de teste dá a suíte inteira
        self.assertLessEqual({"test_ambiente_git", "test_testes_tocados", "test_forge"}, varrem_tests)
        for modulo in self.testes:
            with self.subTest(testes=modulo):
                self.assertEqual(self.f.planejar([f"tests/{modulo}.py"], RAIZ)[0], "completo")

    def test_a_conferencia_enxerga_importacao_e_varredura_na_fonte_sintetica(self):  # critério C.3
        fonte = (
            "import importlib\nfrom pathlib import Path\n"
            "import test_a\nimport test_b as y\n"
            "AQUI = Path(__file__).resolve().parent\n"
            "def f():\n    from test_c import coisa\n"
            "def g(n):\n    return importlib.import_module('tests.' + n)\n"
            "def h():\n    return importlib.import_module('tests.test_d')\n"
            "def i():\n    return list(AQUI.glob('test_*.py'))\n"
        )
        self.assertEqual(self.importados(fonte), ({"test_a", "test_b", "test_c", "test_d"}, True))
        self.assertEqual(self.importados("import os\n"), (set(), False))
        achados, pastas = self.varridos(fonte)
        self.assertEqual(pastas, {"tests"})
        self.assertIn("tests/test_forge.py", achados)
        achados, pastas = self.varridos("from pathlib import Path\nx = list(Path(d).iterdir())\n")
        self.assertEqual((achados, pastas), (set(), set()))


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


class ClassificacaoDoVermelho(unittest.TestCase):
    """A classe de cada teste vem do resultado por teste (falha × erro), nunca do código de saída do processo."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def classe(self, h, b, mudou=False, removidos=()):
        def entrada(res, tipo=None, nome=None):
            return {"id": "tests.m.T.t", "res": res, "tipo": tipo, "nome": nome}
        return self.f.classificar(entrada(*h), None if b is None else entrada(*b), mudou, set(removidos))

    def test_falha_por_asserção_na_base_e_prova(self):
        self.assertEqual(self.classe(("ok",), ("falha", "AssertionError")), "prova (asserção)")

    def test_api_ausente_e_prova(self):
        for tipo in ("AttributeError", "NameError", "ImportError"):
            with self.subTest(tipo):
                self.assertEqual(self.classe(("ok",), ("erro", tipo)), "prova (API ausente)")

    def test_modulo_que_a_diff_cria_e_api_ausente(self):
        self.assertEqual(self.classe(("ok",), ("erro", "ModuleNotFoundError", "pacote.apoio"), removidos=["apoio"]),
                         "prova (API ausente)")

    def test_erro_do_proprio_modulo_de_teste_e_sem_veredito_e_nunca_vermelho(self):  # CA-4
        for b in (("erro", "ModuleNotFoundError", "nao_existe"), ("erro", "SyntaxError"), ("erro", "ValueError")):
            with self.subTest(b):
                self.assertEqual(self.classe(("ok",), b, removidos=["apoio"]), "sem veredito")

    def test_passa_nos_dois_nao_prova(self):
        self.assertEqual(self.classe(("ok",), ("ok",)), "não prova (passa na base)")

    def test_cai_no_head_e_passa_na_base_e_regressao(self):
        self.assertEqual(self.classe(("falha", "AssertionError"), ("ok",)), "regressão")

    def test_divida_so_vale_com_modulo_sem_mudanca_e_falha_por_asserção_na_base(self):  # CA-6 e CA-7
        falha = ("falha", "AssertionError")
        self.assertEqual(self.classe(falha, falha, mudou=False), "dívida pré-existente")
        self.assertEqual(self.classe(falha, falha, mudou=True), self.f.ENTREGA)
        self.assertEqual(self.classe(falha, ("erro", "ImportError"), mudou=False), self.f.ENTREGA)
        self.assertEqual(self.classe(falha, None), self.f.ENTREGA)

    def test_sem_registro_na_base_e_sem_veredito(self):
        self.assertEqual(self.classe(("ok",), None), "sem veredito")

    def test_erro_de_setup_da_classe_na_base_vale_para_os_testes_da_classe(self):  # A3 do review
        erro = {"id": "setUpClass (tests.m.T)", "res": "erro", "tipo": "FileNotFoundError", "nome": "novo"}
        self.assertIs(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a"), erro)
        outra = {"id": "setUpClass (tests.m.U)", "res": "erro", "tipo": "ValueError", "nome": None}
        self.assertIsNone(self.f.da_base({outra["id"]: outra}, "tests.m.T.test_a"))

    def test_erro_de_setup_do_modulo_na_base_vale_para_os_testes_do_modulo(self):  # A3 do review
        erro = {"id": "setUpModule (tests.m)", "res": "erro", "tipo": "ImportError", "nome": None}
        self.assertIs(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a"), erro)

    def test_entrada_herdada_de_teste_que_ja_existia_na_base_vira_herdada_e_nao_prova(self):  # A1 do review e da segurança
        erro = {"id": "setUpModule (tests.m)", "res": "erro", "tipo": "ImportError", "nome": "novo"}
        b = self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a", {"T.test_a"})
        self.assertTrue(b["herdada"])
        self.assertEqual(self.classe(("ok",), (b["res"], b["tipo"], b["nome"]), removidos=["novo"]), "prova (API ausente)")
        self.assertEqual(self.f.classificar({"res": "ok"}, b, False, {"novo"}), "não prova (herdada da base)")
        self.assertIs(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_b", {"T.test_a"}), erro)

    def test_base_ilegivel_do_modulo_nao_da_prova_herdada(self):
        erro = {"id": "setUpModule (tests.m)", "res": "erro", "tipo": "ImportError", "nome": "novo"}
        self.assertTrue(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a", self.f.TodosExistiam())["herdada"])

    def test_a_entrada_do_proprio_teste_vence_a_do_setup(self):
        proprio = {"id": "tests.m.T.test_a", "res": "ok", "tipo": None, "nome": None}
        erro = {"id": "setUpClass (tests.m.T)", "res": "erro", "tipo": "ImportError", "nome": None}
        self.assertIs(self.f.da_base({proprio["id"]: proprio, erro["id"]: erro}, proprio["id"]), proprio)

    def test_arquivo_que_o_diff_cria_e_o_setup_nao_achou_na_base_e_api_ausente(self):  # A3 do review
        erro = ("erro", "FileNotFoundError", "novo.txt")
        self.assertEqual(self.classe(("ok",), erro, removidos=["novo"]), "prova (API ausente)")
        self.assertEqual(self.classe(("ok",), erro, removidos=["outro"]), "sem veredito")


class Vermelho(unittest.TestCase):
    """`--vermelho BASE` num repositório de brinquedo: duas cópias em $TMPDIR, a árvore real intacta."""

    LIB = "def dobro(x):\n    return x\n"
    BASE_TESTE = ("import unittest\nimport lib\n\n\nclass T(unittest.TestCase):\n"
                  "    def test_um(self):\n        self.assertEqual(lib.dobro(0), 0)\n")

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name) / "repo"
        self.tmp = Path(self._t.name) / "tmp"
        self.dir.mkdir()
        self.tmp.mkdir()
        git(self.dir, "init", "-q", "-b", "develop")
        self.gravar("lib.py", self.LIB)
        self.gravar("tests/test_lib.py", self.BASE_TESTE)
        self.gravar(".gitignore", ".forge\n")
        self.salvar("base")
        git(self.dir, "switch", "-q", "-c", "melhoria/x")

    def gravar(self, nome, texto):
        alvo = self.dir / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8")

    def salvar(self, mensagem):
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", mensagem)

    def metodo(self, nome, corpo):
        return f"\n    def {nome}(self):\n        {corpo}\n"

    def env(self, **extra):
        return {**AMBIENTE, "TMPDIR": str(self.tmp), **extra}

    def rodar(self, *args, **extra):
        return subprocess.run([sys.executable, str(FERRAMENTA), *args], cwd=self.dir, env=self.env(**extra),
                              capture_output=True, text=True)

    def vermelho(self, *args, **extra):
        return self.rodar("--vermelho", "develop", *args, **extra)

    def corrigir_lib(self):
        self.gravar("lib.py", "def dobro(x):\n    return x * 2\n")

    TRIVIAL = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"

    def com_modulos_do_mapa(self):
        """Commita (como base do vermelho) `bin/forge-sugerir`, que o mapa leva a test_forge e test_sugerir, e um
        módulo que o mapa não cita (test_outro)."""
        self.gravar("bin/forge-sugerir", "x = 1\n")
        for modulo in ("test_forge", "test_sugerir", "test_outro"):
            self.gravar(f"tests/{modulo}.py", self.TRIVIAL)
        self.salvar("apoio")

    def modulos_do_vermelho(self, r):
        linha = next(l for l in r.stdout.splitlines() if l.startswith("vermelho: base="))
        return linha.split("módulos=")[1].split(" ")[0].split(","), linha

    # M8, opção C (critério de fim, item 4): o `--vermelho` sem `--modulos` não manda módulo de teste ao `planejar`.
    def test_vermelho_usa_o_modulo_de_teste_do_diff_mais_o_plano_dos_outros_caminhos(self):
        self.com_modulos_do_mapa()
        self.gravar("bin/forge-sugerir", "x = 2\n")
        self.gravar("tests/test_sugerir.py", self.TRIVIAL + "# mudou\n")
        self.gravar("tests/test_outro.py", self.TRIVIAL + "# mudou\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, linha = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_outro", "test_sugerir"], r.stdout + r.stderr)
        self.assertNotIn("restrito", linha)

    def test_vermelho_so_com_modulo_de_teste_no_diff_roda_so_esse_modulo_e_nao_a_suite(self):
        self.com_modulos_do_mapa()
        self.gravar("tests/test_sugerir.py", self.TRIVIAL + "# mudou\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, linha = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_sugerir"], r.stdout + r.stderr)
        self.assertNotIn("restrito", linha)

    def test_vermelho_com_modulo_de_teste_apagado_no_diff_nao_o_roda(self):
        self.com_modulos_do_mapa()
        (self.dir / "tests" / "test_outro.py").unlink()
        self.gravar("bin/forge-sugerir", "x = 2\n")
        self.salvar("apaga")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, _ = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_sugerir"], r.stdout + r.stderr)
        self.assertNotIn("sem veredito", r.stdout)

    def test_vermelho_com_caminho_sem_mapa_junto_do_teste_roda_todos_os_modulos(self):
        self.com_modulos_do_mapa()
        self.gravar("lib.py", "def dobro(x):\n    return x * 2\n")
        self.gravar("tests/test_sugerir.py", self.TRIVIAL + "# mudou\n")
        self.salvar("muda")
        modulos, _ = self.modulos_do_vermelho(self.rodar("--vermelho", "HEAD~1"))
        self.assertEqual(modulos, ["test_forge", "test_lib", "test_outro", "test_sugerir"])

    def test_producao_mudada_e_teste_novo_que_a_cobre_e_prova_por_asserção(self):
        self.corrigir_lib()
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_dobro", "self.assertEqual(lib.dobro(2), 4)"))
        self.salvar("corrige")
        antes = git(self.dir, "status", "--porcelain")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("vermelho: base=", r.stdout)
        self.assertIn("revertidos à base: lib.py", r.stdout)
        self.assertIn("tests.test_lib.T.test_dobro · H=ok · B=falha · prova (asserção)", r.stdout)
        self.assertEqual(git(self.dir, "status", "--porcelain"), antes)
        self.assertEqual(list(self.tmp.iterdir()), [], "sobrou cópia em $TMPDIR")
        self.assertIn("modo=vermelho", (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8"))

    def test_teste_que_chama_funcao_que_a_base_nao_tem_e_prova_de_api_ausente(self):
        self.gravar("lib.py", self.LIB + "\n\ndef triplo(x):\n    return x * 3\n")
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_triplo", "self.assertEqual(lib.triplo(2), 6)"))
        self.salvar("triplo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("B=erro · prova (API ausente)", r.stdout)

    def test_arquivo_de_apoio_de_tests_e_producao_e_volta_a_base(self):  # CA-3
        self.gravar("tests/apoio.py", "VALOR = 1\n")
        self.gravar("tests/test_lib.py", "import os\n" + self.BASE_TESTE + self.metodo("test_apoio", "import sys; sys.path.insert(0, os.path.dirname(__file__)); import apoio; self.assertEqual(apoio.VALOR, 1)"))
        self.salvar("apoio")
        r = self.vermelho()
        self.assertIn("revertidos à base: tests/apoio.py", r.stdout)
        self.assertIn("mantidos no HEAD: tests/test_lib.py", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("prova (API ausente)", r.stdout)

    def test_setup_da_classe_que_carrega_o_arquivo_novo_prova_e_nao_vira_sem_veredito(self):  # A3 do review
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\nfrom pathlib import Path\n\n\nclass T(unittest.TestCase):\n"
                    "    @classmethod\n    def setUpClass(cls):\n        cls.texto = Path('novo.py').read_text()\n\n"
                    "    def test_um(self):\n        self.assertIn('VALOR', self.texto)\n\n"
                    "    def test_dois(self):\n        self.assertTrue(self.texto)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_novo.T.test_um · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertIn("tests.test_novo.T.test_dois · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertNotIn("sem veredito", r.stdout)

    def test_setup_do_modulo_que_importa_o_arquivo_novo_prova_e_nao_vira_sem_veredito(self):  # A3 do review
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\n\n\ndef setUpModule():\n    global novo\n    import novo\n\n\n"
                    "class T(unittest.TestCase):\n    def test_um(self):\n        self.assertEqual(novo.VALOR, 1)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_novo.T.test_um · H=ok · B=erro · prova (API ausente)", r.stdout)

    def test_modulo_que_importa_o_arquivo_novo_no_topo_prova_e_nao_vira_sem_veredito(self):  # R3 da segurança
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\n\nimport novo\n\n\nclass T(unittest.TestCase):\n"
                    "    def test_um(self):\n        self.assertEqual(novo.VALOR, 1)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_novo.T.test_um · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertNotIn("sem veredito", r.stdout)

    def modulo_existente_com_entrada_nova(self, antes, depois=""):
        """Entrega que cria `novo.py` e só acrescenta ao módulo que já existia na base uma entrada que o importa."""
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_lib.py", antes + self.BASE_TESTE + depois)
        self.salvar("so entrada")
        return self.vermelho()

    def confere_sem_prova_herdada(self, r):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tests.test_lib.T.test_um · H=ok · B=erro · não prova (herdada da base)", r.stdout)
        self.assertNotIn("prova (API ausente)", r.stdout)
        self.assertNotIn("sem veredito", r.stdout)

    def test_import_novo_no_topo_de_modulo_existente_sem_teste_novo_sai_1(self):  # A1 do review e da segurança
        self.confere_sem_prova_herdada(self.modulo_existente_com_entrada_nova("import novo  # noqa: F401\n"))

    def test_setup_da_classe_novo_em_modulo_existente_sem_teste_novo_sai_1(self):  # A1 do review e da segurança
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_lib.py", self.BASE_TESTE.replace(
            "    def test_um", "    @classmethod\n    def setUpClass(cls):\n        import novo  # noqa: F401\n\n    def test_um"))
        self.salvar("so setup")
        self.confere_sem_prova_herdada(self.vermelho())

    def test_setup_do_modulo_novo_em_modulo_existente_sem_teste_novo_sai_1(self):  # A1 do review e da segurança
        self.confere_sem_prova_herdada(self.modulo_existente_com_entrada_nova(
            "def setUpModule():\n    import novo  # noqa: F401\n\n\n"))

    def test_teste_novo_ao_lado_do_existente_prova_e_o_existente_continua_neutro(self):
        r = self.modulo_existente_com_entrada_nova(
            "import novo\n", self.metodo("test_novo", "self.assertEqual(novo.VALOR, 1)"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_lib.T.test_novo · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertIn("tests.test_lib.T.test_um · H=ok · B=erro · não prova (herdada da base)", r.stdout)

    def test_setup_da_classe_que_falha_por_outro_motivo_nao_vira_vermelho(self):  # a ampliação tem o alvo do diff
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\nfrom pathlib import Path\n\n\nclass T(unittest.TestCase):\n"
                    "    @classmethod\n    def setUpClass(cls):\n        cls.texto = Path('faltando.txt').read_text()\n\n"
                    "    def test_um(self):\n        self.assertTrue(True)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("prova (API ausente)", r.stdout)

    def test_teste_mudado_que_passa_na_base_nao_prova_e_sai_1(self):
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_novo", "self.assertTrue(True)"))
        self.salvar("so teste")
        r = self.vermelho("--modulos", "test_lib")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("não prova (passa na base)", r.stdout)
        self.assertIn("nenhum teste prova a mudança", r.stdout)
        self.assertIn("(restrito por --modulos)", r.stdout)

    def test_teste_sem_mudanca_que_cai_no_head_e_regressao(self):
        self.gravar("lib.py", "def dobro(x):\n    return 2\n")
        self.salvar("quebra")
        r = self.vermelho()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("H=falha · B=ok · regressão", r.stdout)

    def test_teste_sem_mudanca_que_ja_caia_na_base_e_divida_e_continua_bloqueando(self):  # CA-7
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_ruim", "self.assertEqual(lib.dobro(1), 5)"))
        self.salvar("divida")
        git(self.dir, "switch", "-q", "-c", "melhoria/y")
        self.gravar("lib.py", self.LIB + "\n\ndef outro():\n    return 0\n")
        self.salvar("outro")
        r = self.rodar("--vermelho", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("dívida pré-existente", r.stdout)
        self.assertIn("há teste que falha no HEAD", r.stdout)

    def test_teste_alterado_que_falha_na_base_e_no_head_nao_e_divida(self):  # CA-6
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_ruim", "self.fail('x')"))
        self.salvar("ruim")
        r = self.vermelho()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("regressão ou sem veredito", r.stdout)
        self.assertNotIn("dívida", r.stdout)

    def test_teste_que_estoura_o_prazo_e_sem_veredito_e_sai_2(self):  # CA-9
        self.corrigir_lib()
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_lento", "__import__('time').sleep(60)"))
        self.salvar("lento")
        r = self.vermelho("--prazo", "2")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("sem veredito", r.stdout)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_arvore_suja_sai_2_e_nao_cria_copia(self):  # CA-1
        self.corrigir_lib()
        r = self.vermelho()
        self.assertEqual(r.returncode, 2)
        self.assertIn("mudança não commitada", r.stderr)
        self.assertEqual((self.dir / "lib.py").read_text(encoding="utf-8"), "def dobro(x):\n    return x * 2\n")
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_base_invalida_sai_2_sem_criar_arquivo_nem_recuar(self):  # CA-8
        self.corrigir_lib()
        self.salvar("corrige")
        for args in (["--vermelho=--output=gravado.txt"], ["--base=--output=gravado.txt", "--vermelho"],
                     ["--vermelho", "nao-existe"]):
            with self.subTest(args):
                r = self.rodar(*args)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse((self.dir / "gravado.txt").exists())
                self.assertNotIn("suíte completa", r.stdout)

    def test_uso_invalido_sai_2(self):
        for args in (["--vermelho", "develop", "--completa"], ["--modulos", "test_lib"], ["--prazo", "5"],
                     ["--vermelho", "develop", "--modulos", "a;b"], ["--vermelho", "develop", "--prazo", "0"]):
            with self.subTest(args):
                self.assertEqual(self.rodar(*args).returncode, 2)

    def test_sinal_no_meio_da_rodada_deixa_a_arvore_intacta_e_apaga_as_copias(self):  # CA-2
        self.corrigir_lib()
        corpo = "open(os.environ['MARCA'], 'w').close(); __import__('time').sleep(60)"
        self.gravar("tests/test_lib.py", "import os\n" + self.BASE_TESTE + self.metodo("test_dorme", corpo))
        self.salvar("dorme")
        antes = git(self.dir, "status", "--porcelain")
        marca = Path(self._t.name) / "marca"
        processo = subprocess.Popen([sys.executable, str(FERRAMENTA), "--vermelho", "develop"], cwd=self.dir,
                                    env=self.env(MARCA=str(marca)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(processo.kill)
        for _ in range(300):
            if marca.exists():
                break
            time.sleep(0.1)
        self.assertTrue(marca.exists(), "o teste lento não começou")
        processo.terminate()
        processo.wait(timeout=60)
        self.assertEqual(git(self.dir, "status", "--porcelain"), antes)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_ambiente_da_copia_nao_herda_git_nem_forge(self):
        self.corrigir_lib()
        corpo = "self.assertEqual([k for k in os.environ if k.startswith(('GIT_DIR', 'GIT_WORK_TREE', 'FORGE_'))], [])"
        self.gravar("tests/test_lib.py", "import os\n" + self.BASE_TESTE + self.metodo("test_ambiente", corpo)
                    + self.metodo("test_dobro", "self.assertEqual(lib.dobro(2), 4)"))
        self.salvar("ambiente")
        r = self.vermelho(GIT_DIR=str(self.dir / ".git"), GIT_WORK_TREE=str(self.dir), FORGE_X="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("H=falha", r.stdout)
        self.assertNotIn("H=erro", r.stdout)


if __name__ == "__main__":
    unittest.main()
