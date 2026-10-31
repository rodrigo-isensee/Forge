"""`bin/forge-mutante` (OK-14 e M-1): mutantes declarados do pedido; evidência do QA, não portão."""
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-mutante"
AMBIENTE = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                           "GIT_COMMITTER_EMAIL": "t@t"})
LIB = "def limite(x):\n    if x > 10:\n        return 2\n    return 0\n"
TESTE = ("import unittest\nimport lib\n\n\nclass T(unittest.TestCase):\n"
         "    def test_borda(self):\n        self.assertEqual(lib.limite(11), 2)\n\n"
         "    def test_baixo(self):\n        self.assertEqual(lib.limite(0), 0)\n")


def carregar():
    carregador = importlib.machinery.SourceFileLoader("forge_mutante", str(FERRAMENTA))
    spec = importlib.util.spec_from_loader("forge_mutante", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=AMBIENTE, capture_output=True, text=True, check=True).stdout


def mutante(ident="M1", de="x > 10", para="x >= 100", testes=("tests.test_lib.T.test_borda",), arquivo="lib.py"):
    return {"id": ident, "guarda": "limite", "arquivo": arquivo, "de": de, "para": para, "testes": list(testes)}


class Veredito(unittest.TestCase):
    """O veredito sai do resultado por teste, nunca do código de saída do processo (V10)."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def test_falha_por_asserção_mata_e_tudo_verde_sobrevive(self):
        D = ["tests.m.T.t"]
        self.assertEqual(self.f.veredito(D, [{"id": "tests.m.T.t", "res": "falha"}])[0], "morreu")
        self.assertEqual(self.f.veredito(D, [{"id": "tests.m.T.t", "res": "ok"}])[0], "sobreviveu")

    def test_erro_de_carga_e_teste_que_nao_rodou_sao_invalidos_e_nunca_morreu(self):  # CA-10 e CA-11
        D = ["tests.m.T.t"]
        self.assertEqual(self.f.veredito(D, [{"id": "tests.m", "res": "erro"}])[0], "inválido")
        self.assertEqual(self.f.veredito(D, [])[0], "inválido")
        self.assertEqual(self.f.veredito(D, [{"id": "tests.m.T.outro", "res": "falha"}])[0], "inválido")
        self.assertEqual(self.f.veredito(D, [{"id": "tests.m.T.t", "res": "pulado"}])[0], "inválido")

    def test_id_de_classe_ou_modulo_cobre_os_testes_dele(self):
        self.assertEqual(self.f.veredito(["tests.m"], [{"id": "tests.m.T.t", "res": "falha"}])[0], "morreu")
        self.assertEqual(self.f.veredito(["tests.m.T"], [{"id": "tests.m.TT.t", "res": "falha"}])[0], "inválido")


class ValidacaoDaSpec(unittest.TestCase):
    """A spec fecha na dúvida: o que não é o objeto esperado, ou aponta para fora, é inválido."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def problemas(self, *mutantes, **extra):
        return self.f.validar_spec({"pedido": "x", "mutantes": list(mutantes), **extra})

    def test_spec_valida(self):
        self.assertEqual(self.problemas(mutante()), [])

    def test_o_que_nao_e_o_objeto_esperado_e_invalido(self):
        for spec in ([], "x", None, {"pedido": "x"}, {"mutantes": []}, {"pedido": "x", "mutantes": [], "extra": 1},
                     {"pedido": 1, "mutantes": [mutante()]}):
            with self.subTest(spec):
                self.assertTrue(self.f.validar_spec(spec))

    def test_de_um_a_dezesseis_mutantes(self):  # VEL-P1P10: o teto por spec sobe de 8 para 16
        self.assertTrue(self.problemas())
        self.assertEqual(self.problemas(*[mutante(f"M{i}") for i in range(1, 17)]), [])
        self.assertTrue(self.problemas(*[mutante(f"M{i}") for i in range(1, 18)]))

    def equivalente(self, justificativa="o ramo morto nunca roda neste commit", ident="E1"):
        m = {k: v for k, v in mutante(ident, de="return 0", para="return 1").items() if k != "testes"}
        return {**m, "equivalente": justificativa}

    def test_equivalente_declarado_com_justificativa_e_valido_sem_testes(self):  # VEL-P1P10
        self.assertEqual(self.problemas(self.equivalente()), [])
        self.assertEqual(self.problemas(mutante(), self.equivalente()), [])

    def test_equivalente_sem_justificativa_ou_com_testes_mal_formados_e_invalido(self):  # COBERTURA-EQUIVALENTE
        for justificativa in ("", "curta demais", " " * 30, None, 7):
            with self.subTest(repr(justificativa)):
                self.assertTrue(self.problemas(self.equivalente(justificativa)))
        self.assertEqual(self.problemas({**self.equivalente(), "testes": ["tests.test_lib.T.test_borda"]}), [])
        for testes in ([], ["lib"], "tests.test_lib"):
            with self.subTest(testes):
                self.assertTrue(self.problemas({**self.equivalente(), "testes": testes}))
        semchave = self.equivalente()
        del semchave["equivalente"]
        self.assertTrue(self.problemas(semchave))

    def test_arquivo_fora_do_padrao_e_invalido(self):  # CA-13
        for arquivo in ("/etc/x", "../fora.py", "a/../../b.py", "./lib.py", "a//b.py", "-lib.py", "a b.py", "a;b",
                        "lib.py\n", "", "tests/test_lib.py", "tests/config.json", "tests/fixtures/a.json"):
            with self.subTest(arquivo):
                self.assertTrue(self.problemas(mutante(arquivo=arquivo)))
        self.assertEqual(self.problemas(mutante(arquivo="bin/ferramenta"), mutante("M2", arquivo="tests/catraca.py")), [])

    def test_id_de_teste_fora_do_padrao_e_invalido(self):  # CA-16
        for teste in ("tests.test_lib.T.test-x", "tests.test lib", "tests.t;rm", "tests.$(x)", "bin.x", "tests..x",
                      "tests.x.", "../tests.x", "tests.x\n"):
            with self.subTest(teste):
                self.assertTrue(self.problemas(mutante(testes=[teste])))
        self.assertTrue(self.problemas(mutante(testes=[])))

    def test_id_de_teste_com_identificador_python_nao_ascii_e_valido(self):  # MUTANTE-ID-ASCII
        for teste in ("tests.test_lib.Vermelho.test_produção_mudada_e_prova_por_asserção", "tests.teste_ção",
                      "tests.test_lib.Ação"):
            with self.subTest(teste):
                self.assertEqual(self.problemas(mutante(testes=[teste])), [])
        for teste in ("tests.ç-x", "tests.x.1a", "tests.x.ç ç", "tests.x\u00a0y", "tests", "testes.x", "tests.x․y"):
            with self.subTest(teste):
                self.assertTrue(self.problemas(mutante(testes=[teste])))

    def test_id_de_teste_que_nao_e_texto_ou_nao_normalizado_e_invalido(self):  # QA A2, A3 e review A2 do lote
        for teste in (1, None, ["tests.x"], {"a": 1}):
            with self.subTest(repr(teste)):
                try:  # a guarda some: AttributeError vira falha de asserção, que o leitor de veredito conta como morreu
                    valido = self.f.id_de_teste_valido(teste)
                except AttributeError as erro:
                    self.fail(f"id que não é texto quebrou em vez de ser recusado: {erro}")
                self.assertFalse(valido)
                self.assertTrue(self.problemas(mutante(testes=[teste])))
        for teste in ("tests.c\u0327", "tests.x.\uff21b", "outro.x", "x.tests.y"):  # fora da NFKC e raiz que não é tests
            with self.subTest(teste):
                self.assertFalse(self.f.id_de_teste_valido(teste))

    def test_troca_vazia_igual_ou_enorme_e_invalida(self):  # CA-14
        self.assertTrue(self.problemas(mutante(de="")))
        self.assertTrue(self.problemas(mutante(de="a", para="a")))
        self.assertTrue(self.problemas(mutante(de="a" * 4001)))

    def test_id_repetido_ou_fora_do_padrao_e_invalido(self):
        self.assertTrue(self.problemas(mutante("M1"), mutante("M1")))
        self.assertTrue(self.problemas(mutante("M 1")))

    def test_executor_sem_leitor_e_invalido(self):  # CA-22
        self.assertTrue(self.problemas(mutante(), executor="outro"))
        self.assertEqual(self.problemas(mutante(), executor="unittest"), [])

    def test_varias_specs_do_pedido_passam_de_oito_sem_subir_o_teto_por_spec(self):  # MUTANTE-TETO
        oito = {"pedido": "x", "mutantes": [mutante(f"A{i}") for i in range(1, 9)]}
        mais = {"pedido": "x", "mutantes": [mutante(f"B{i}") for i in range(1, 7)]}
        self.assertEqual(self.f.validar_specs([oito, mais]), [])
        dezessete = {"pedido": "x", "mutantes": [mutante(f"B{i}") for i in range(1, 18)]}
        self.assertTrue(self.f.validar_specs([oito, dezessete]), "o teto de 16 continua por spec")

    def test_varias_specs_com_pedido_diferente_ou_id_repetido_sao_invalidas(self):  # MUTANTE-TETO
        a = {"pedido": "x", "mutantes": [mutante("M1")]}
        self.assertTrue(self.f.validar_specs([a, {"pedido": "y", "mutantes": [mutante("M2")]}]))
        self.assertTrue(self.f.validar_specs([a, {"pedido": "x", "mutantes": [mutante("M1")]}]))
        self.assertTrue(self.f.validar_specs([]))


class Execucao(unittest.TestCase):
    """Roda o script de verdade num repositório de brinquedo, com a spec fora dele."""

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        base = Path(self._t.name)
        self.dir, self.tmp, self.fora = base / "repo", base / "tmp", base / "fora"
        for pasta in (self.dir, self.tmp, self.fora):
            pasta.mkdir()
        git(self.dir, "init", "-q", "-b", "develop")
        self.gravar("lib.py", LIB)
        self.gravar("tests/test_lib.py", TESTE)
        self.gravar(".gitignore", ".forge\n")
        self.salvar()

    def gravar(self, nome, texto):
        alvo = self.dir / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8")

    def salvar(self):
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "c")

    def spec(self, *mutantes, nome="spec.json", **extra):
        caminho = Path(self._t.name) / nome
        caminho.write_text(json.dumps({"pedido": "x", "mutantes": list(mutantes), **extra}), encoding="utf-8")
        return str(caminho)

    def rodar(self, spec, *args, **env):
        return subprocess.run([sys.executable, str(FERRAMENTA), spec, *args], cwd=self.dir,
                              env={**AMBIENTE, "TMPDIR": str(self.tmp), **env}, capture_output=True, text=True)

    def test_mutante_que_o_teste_derruba_morre_e_sai_0(self):
        spec = self.spec(mutante())
        antes = git(self.dir, "status", "--porcelain")
        r = self.rodar(spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("M1 · morreu · lib.py:2", r.stdout)
        self.assertIn(hashlib.sha256(Path(spec).read_bytes()).hexdigest(), r.stdout)
        self.assertIn("rev=" + git(self.dir, "rev-parse", "HEAD")[:12], r.stdout)
        self.assertEqual(git(self.dir, "status", "--porcelain"), antes)  # CA-18
        self.assertEqual((self.dir / "lib.py").read_text(encoding="utf-8"), LIB)
        self.assertEqual(list(self.tmp.iterdir()), [], "sobrou cópia em $TMPDIR")

    def test_dois_mortos_e_um_sobrevivente_saem_1_com_uma_linha_por_mutante(self):  # CA-17
        spec = self.spec(mutante("M1"), mutante("M2", para="x > 99"), mutante("M3", para="x > 9"))
        r = self.rodar(spec)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        for linha in ("M1 · morreu · lib.py:2", "M2 · morreu · lib.py:2", "M3 · sobreviveu · lib.py:2"):
            self.assertIn(linha, r.stdout)  # a troca de um não vaza para a cópia do seguinte

    def test_de_com_zero_ou_duas_ocorrencias_sai_2(self):  # CA-14
        for de in ("x > 11", "return"):
            with self.subTest(de):
                r = self.rodar(self.spec(mutante(de=de, para="y")))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("inválido", r.stdout)

    def test_controle_vermelho_sai_2(self):  # CA-12
        self.gravar("tests/test_lib.py", TESTE + "\n    def test_ruim(self):\n        self.fail('x')\n")
        self.salvar()
        r = self.rodar(self.spec(mutante(testes=["tests.test_lib.T.test_borda", "tests.test_lib.T.test_ruim"])))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("controle vermelho", r.stdout)

    def test_teste_inexistente_sai_2_e_nunca_morreu(self):  # CA-11
        r = self.rodar(self.spec(mutante(testes=["tests.test_lib.T.test_nao_existe"])))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertNotIn("morreu", r.stdout)

    def test_troca_que_quebra_a_sintaxe_sai_2_e_nao_conta_como_morreu(self):  # CA-10
        r = self.rodar(self.spec(mutante(de="return 2", para="return (")))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("sintaxe", r.stdout)
        self.assertNotIn("morreu", r.stdout)

    def test_arquivo_invalido_sai_2_sem_executar_nada(self):  # CA-13
        for arquivo in ("../fora.py", "/etc/passwd", "tests/test_lib.py"):
            with self.subTest(arquivo):
                r = self.rodar(self.spec(mutante(arquivo=arquivo, de="x", para="y")))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("nada foi executado", r.stderr)

    def test_link_simbolico_para_fora_sai_2_e_o_alvo_fica_intacto(self):  # CA-13
        alvo = self.fora / "alvo.py"
        alvo.write_text("x = 1\n", encoding="utf-8")
        hash_antes = hashlib.sha256(alvo.read_bytes()).hexdigest()
        (self.dir / "link.py").symlink_to(alvo)
        (self.dir / "pasta").symlink_to(self.fora)
        self.salvar()
        for arquivo in ("link.py", "pasta/alvo.py"):
            with self.subTest(arquivo):
                r = self.rodar(self.spec(mutante(arquivo=arquivo, de="x = 1", para="x = 2")))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("link simbólico", r.stdout)
                self.assertEqual(hashlib.sha256(alvo.read_bytes()).hexdigest(), hash_antes)

    def equivalente(self, **troca):
        return {"id": "E1", "guarda": "limite", "arquivo": "lib.py", "de": "return 0", "para": "return 1",
                "equivalente": "o retorno padrão não muda o resultado observável", **troca}

    def test_equivalente_declarado_nao_roda_nao_da_rc_1_e_sai_na_linha_propria(self):  # VEL-P1P10
        r = self.rodar(self.spec(mutante(), self.equivalente()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("equivalente: E1 · o retorno padrão não muda o resultado observável\n", r.stdout)
        self.assertNotIn("E1 · sobreviveu", r.stdout)

    def test_equivalente_com_o_trecho_ausente_ou_repetido_sai_2(self):  # VEL-P1P10
        for de in ("return 9", "return"):
            with self.subTest(de):
                r = self.rodar(self.spec(self.equivalente(de=de)))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("E1 · inválido", r.stdout)

    def test_spec_so_de_equivalentes_sem_testes_nao_sai_0(self):  # COBERTURA-EQUIVALENTE (b)
        r = self.rodar(self.spec(self.equivalente()))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("nenhum teste rodou", r.stderr)

    def test_equivalente_com_testes_roda_e_o_que_eles_matam_e_invalido(self):  # COBERTURA-EQUIVALENTE (c)
        r = self.rodar(self.spec(mutante(), self.equivalente(testes=["tests.test_lib.T.test_baixo"])))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("E1 · inválido · lib.py:4 · declarado equivalente, mas os testes listados o matam", r.stdout)
        r = self.rodar(self.spec(self.equivalente(testes=["tests.test_lib.T.test_borda"])))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("E1 · equivalente · lib.py:4\n", r.stdout)

    def test_equivalente_sem_justificativa_barra_a_spec_antes_de_rodar(self):  # VEL-P1P10
        r = self.rodar(self.spec(mutante(), self.equivalente(equivalente="curta")))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nada foi executado", r.stderr)

    def test_mais_de_dezesseis_mutantes_sai_2(self):
        r = self.rodar(self.spec(*[mutante(f"M{i}") for i in range(1, 18)]))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nada foi executado", r.stderr)

    def test_duas_specs_do_mesmo_pedido_rodam_juntas_com_o_hash_de_cada_uma(self):  # MUTANTE-TETO
        a = self.spec(mutante("M1"), nome="x-1.json")
        b = self.spec(mutante("M2", para="x > 9"), nome="x-2.json")
        r = self.rodar(a, b)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("M1 · morreu · lib.py:2", r.stdout)
        self.assertIn("M2 · sobreviveu · lib.py:2", r.stdout)
        for caminho in (a, b):
            self.assertIn("spec=" + hashlib.sha256(Path(caminho).read_bytes()).hexdigest(), r.stdout)

    def test_segunda_spec_invalida_barra_tudo_antes_de_rodar(self):  # MUTANTE-TETO
        a = self.spec(mutante("M1"), nome="x-1.json")
        b = self.spec(*[mutante(f"B{i}") for i in range(1, 18)], nome="x-2.json")
        r = self.rodar(a, b)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("nada foi executado", r.stderr)
        self.assertNotIn("morreu", r.stdout)

    def test_teste_com_nome_nao_ascii_roda_e_mata(self):  # MUTANTE-ID-ASCII
        self.gravar("tests/test_lib.py", TESTE + "\n    def test_borda_ação(self):\n        self.assertEqual(lib.limite(11), 2)\n")
        self.salvar()
        r = self.rodar(self.spec(mutante(testes=["tests.test_lib.T.test_borda_ação"])))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("M1 · morreu · lib.py:2", r.stdout)

    def test_modulo_com_metacaractere_sai_2_e_nada_roda(self):  # CA-16
        marca = self.fora / "marca"
        for teste in (f"tests.x;touch {marca}", f"tests.$(touch {marca})", "tests.x y"):
            with self.subTest(teste):
                r = self.rodar(self.spec(mutante(testes=[teste])))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse(marca.exists())

    def test_teste_que_estoura_o_prazo_sai_2_sem_veredito(self):  # CA-9
        self.gravar("tests/test_lib.py", TESTE + "\n    def test_lento(self):\n        __import__('time').sleep(60)\n")
        self.salvar()
        r = self.rodar(self.spec(mutante(testes=["tests.test_lib.T.test_lento"])), "--prazo", "2")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("sem veredito", r.stdout)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_ambiente_da_copia_nao_herda_git_nem_forge(self):
        corpo = "self.assertEqual([k for k in os.environ if k.startswith(('GIT_DIR', 'GIT_WORK_TREE', 'FORGE_'))], [])"
        self.gravar("tests/test_lib.py", "import os\n" + TESTE + f"\n    def test_ambiente(self):\n        {corpo}\n")
        self.salvar()
        r = self.rodar(self.spec(mutante(testes=["tests.test_lib.T.test_borda", "tests.test_lib.T.test_ambiente"])),
                       GIT_DIR=str(self.dir / ".git"), GIT_WORK_TREE=str(self.dir), FORGE_X="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_spec_ilegivel_ou_grande_demais_sai_2(self):
        caminho = Path(self._t.name) / "ruim.json"
        for conteudo in ("{", "[]", "x" * 70000):
            with self.subTest(len(conteudo)):
                caminho.write_text(conteudo, encoding="utf-8")
                self.assertEqual(self.rodar(str(caminho)).returncode, 2)
        self.assertEqual(self.rodar(str(self.fora / "nao-existe.json")).returncode, 2)

    def test_sem_leitor_de_veredito_sai_2(self):  # CA-22
        r = self.rodar(self.spec(mutante(), executor="outro"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("sem leitor de veredito", r.stderr)

    def test_sem_executor_e_sem_testes_unittest_sai_2_em_qualquer_spec_do_conjunto(self):  # QA A1 do lote
        git(self.dir, "rm", "-q", "tests/test_lib.py")
        self.salvar()
        sem = self.spec(mutante("M1"), nome="x-1.json")
        com = self.spec(mutante("M2"), nome="x-2.json", executor="unittest")
        for specs in ((sem,), (com, sem), (sem, com)):
            with self.subTest(len(specs)):
                r = self.rodar(*specs)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("sem leitor de veredito", r.stderr)

    def test_spec_com_testes_que_nao_sao_texto_sai_2_como_spec_invalida(self):  # QA A2 do lote
        r = self.rodar(self.spec(mutante(testes=[1])))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("nada foi executado", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_rev_invalido_sai_2_sem_criar_arquivo(self):
        r = self.rodar(self.spec(mutante()), "--rev=--output=gravado.txt")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertFalse((self.dir / "gravado.txt").exists())


class TextoQueMandaUsarAFerramenta(unittest.TestCase):
    """O que a skill e o agente mandam rodar é o contrato da ferramenta (SPEC, não o nome do pedido) e a conferência da V14 (a)."""

    @classmethod
    def setUpClass(cls):
        cls.textos = {c: (RAIZ / c).read_text(encoding="utf-8") for c in ("skills/qa-testing/SKILL.md", "agents/qa-engineer.md")}

    def test_manda_passar_o_caminho_da_spec_e_nunca_o_nome_do_pedido(self):  # A2 do review
        for caminho, texto in self.textos.items():
            with self.subTest(caminho):
                self.assertIn("bin/forge-mutante tests/mutantes/<pedido>.json", texto)
                self.assertNotIn("forge-mutante <pedido>", texto)

    def test_exige_um_mutante_por_linha_de_guarda_mudada_e_manda_conferir(self):  # A1 da segurança, V14 (a)
        for caminho, texto in self.textos.items():
            with self.subTest(caminho):
                self.assertRegex(texto, r"(um mutante|\*\*um) por linha de guarda mudada")
                self.assertIn("linha de guarda", texto)
                self.assertRegex(texto, r"sem mutante é achado")

    def test_a_linha_do_item_65_nao_cola_na_do_item_34_no_agente(self):  # A1 do review
        linhas = self.textos["agents/qa-engineer.md"].splitlines()
        vermelho = [i for i, l in enumerate(linhas) if "forge-testes --vermelho" in l]
        mutante_ = [i for i, l in enumerate(linhas) if "bin/forge-mutante" in l]
        passo5 = next(i for i, l in enumerate(linhas) if l.startswith("5. Para cada defeito"))
        self.assertEqual(len(mutante_), 1, "a linha do forge-mutante falta ou se repete")
        mutante_ = mutante_[0]
        if vermelho:  # sem a linha do `--vermelho` (item 34 revertido), não há com o que colar
            self.assertGreater(mutante_ - vermelho[0], 1)
        self.assertEqual(mutante_, passo5 - 1, "a linha do forge-mutante vem depois do fim do passo 4")


class Cobertura(unittest.TestCase):
    """`--cobertura --base`: a condição Python mudada no diff sem mutante declarado (GUARDA-SEM-MUTANTE)."""
    COND = "x = 1\nif x > 100:\n    x = 2\n"

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        git(self.dir, "init", "-q", "-b", "develop")
        self.salvar({"lib.py": "x = 1\n"}, base=True)

    def cabeca(self):
        return git(self.dir, "rev-parse", "HEAD").strip()

    def salvar(self, arquivos, base=False):
        for nome, texto in arquivos.items():
            alvo = self.dir / nome
            alvo.parent.mkdir(parents=True, exist_ok=True)
            if texto is None:
                alvo.unlink()
            else:
                alvo.write_bytes(texto if isinstance(texto, bytes) else texto.encode("utf-8"))
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "c")
        if base:
            self.base = self.cabeca()

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(FERRAMENTA), *args], cwd=self.dir, env=AMBIENTE,
                              capture_output=True, text=True)

    def cobertura(self, *args):
        return self.rodar("--cobertura", "--base", self.base, *args)

    def spec(self, de, para, nome="x", arquivo="lib.py"):
        mutantes = [mutante(de=de, para=para, arquivo=arquivo)]
        return {f"tests/mutantes/{nome}.json": json.dumps({"pedido": "x", "mutantes": mutantes})}

    def test_condicao_nova_sem_mutante_sai_1_e_com_mutante_declarado_sai_0(self):
        self.salvar({"lib.py": self.COND, **self.spec("if x > 100:", "if x > 1000:", arquivo="outro.py")})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[0]), (1, f"base={self.base} mb={self.base} rev={self.cabeca()}"))
        self.assertIn("sem mutante · lib.py:2 · x > 100", r.stdout)
        self.salvar(self.spec("if x > 100:", "if x > 1000:"))
        r = self.cobertura()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("coberta · lib.py:2 · tests/mutantes/x.json:M1 · declarado, não provado", r.stdout)

    def test_condicao_coberta_so_por_equivalente_sai_em_linha_propria_e_1(self):  # COBERTURA-EQUIVALENTE (a)
        equivalente = {k: v for k, v in mutante("E1", de="if x > 100:", para="if x > 1000:").items() if k != "testes"}
        equivalente["equivalente"] = "o limite maior não muda nada observável aqui"
        spec = {"tests/mutantes/x.json": json.dumps({"pedido": "x", "mutantes": [equivalente]})}
        self.salvar({"lib.py": self.COND, **spec})
        r = self.cobertura()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("só equivalente · lib.py:2 · tests/mutantes/x.json:E1 · não provado", r.stdout)
        self.assertNotIn("coberta", r.stdout)
        comum = mutante(de="if x > 100:", para="if x > 1000:")
        self.salvar({"tests/mutantes/x.json": json.dumps({"pedido": "x", "mutantes": [equivalente, comum]})})
        r = self.cobertura()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("coberta · lib.py:2 · tests/mutantes/x.json:M1 · declarado, não provado", r.stdout)

    def test_linha_mudada_sozinha_conta(self):  # o hunk `@@ -1,0 +2 @@` não traz a contagem
        self.salvar({"lib.py": "x = 1\nif x > 100: x = 2\n"})
        self.assertEqual(self.cobertura().returncode, 1)

    def test_reformatar_nao_conta_e_copiar_ou_apagar_conta(self):  # multiconjunto
        self.salvar({"lib.py": self.COND}, base=True)
        self.salvar({"lib.py": "x = 1\nif (x  >  100):\n    x = 2\n"})
        r = self.cobertura()
        self.assertEqual((r.returncode, len(r.stdout.splitlines())), (0, 1), r.stdout)
        self.salvar({"lib.py": self.COND + "if x > 100:\n    x = 3\n"})
        r = self.cobertura()
        self.assertEqual(r.returncode, 1)
        self.assertIn("sem mutante · lib.py:4", r.stdout)
        self.assertNotIn("lib.py:2", r.stdout)
        self.salvar({"lib.py": "x = 1\n"})
        r = self.cobertura()
        self.assertEqual(r.returncode, 1)
        self.assertIn("apagada · lib.py:2(base) · x > 100", r.stdout)

    def test_arquivo_python_removido_sai_como_apagada_e_o_que_nao_e_python_nao_coberto(self):  # A2 do review
        self.salvar({"lib.py": self.COND, "Makefile": "all:\n\ttrue\n",
                     "bin/run": "#!/bin/sh\nif [ -f x ]; then :; fi\n",
                     "bin/py": "#!/usr/bin/env python3\nif y:\n    pass\n"}, base=True)
        self.salvar({"lib.py": None, "Makefile": None, "bin/run": None, "bin/py": None})
        r = self.cobertura()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("apagada · lib.py:2(base) · x > 100", r.stdout)
        self.assertIn("não coberto: Makefile", r.stdout)
        self.assertIn("não coberto: bin/run", r.stdout)
        self.assertIn("apagada · bin/py:2(base) · y", r.stdout)  # removido sem extensão: o tipo vem da base
        self.salvar({"tests/test_a.py": "if 1 > 0:\n    pass\n"}, base=True)
        self.salvar({"tests/test_a.py": None})
        self.assertEqual(self.cobertura().returncode, 0)

    def test_condicao_editada_e_coberta_pela_nova_e_so_a_tirada_sem_troca_e_apagada(self):  # A2 do QA
        self.salvar({"lib.py": "if y:\n    pass\n" + self.COND}, base=True)
        self.salvar({"lib.py": "if y:\n    pass\nx = 1\nif x >= 100:\n    x = 2\n", **self.spec("if x >= 100:", "if x > 9:")})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (0, ["coberta · lib.py:4 · tests/mutantes/x.json:M1 · "
                         "declarado, não provado"]))
        self.salvar({"lib.py": "x = 1\nif x >= 100:\n    x = 2\n"})
        self.assertEqual(self.cobertura().stdout.splitlines()[2:], ["apagada · lib.py:1(base) · y"])

    def test_binario_e_fora_do_utf8_so_param_no_python_e_o_cr_solto_e_2(self):  # A1 do review, A2 da segurança
        for nome, dados, rc in (("tests/fixtures/a.txt", b"caf\xe9", 0), ("logo.png", b"\x89PNG\0\xff", 0),
                                ("c.py", b"x = '\xe9'\n", 2), ("d.py", b"x = 1\rif y:\n    pass\n", 2),
                                ("e.py", b"x = 1\r\nif y:\r\n    pass\r\n", 1)):
            with self.subTest(nome):
                self.salvar({nome: dados})
                r = self.cobertura()
                git(self.dir, "reset", "-q", "--hard", self.base)
                self.assertEqual(r.returncode, rc, r.stdout + r.stderr)
                self.assertIn(f"{nome}: " if rc == 2 else "e.py:2" if rc else "", r.stderr + r.stdout)

    def test_atributo_do_git_nao_esconde_o_hunk(self):  # A1 da segurança
        git(self.dir, "config", "diff.t.textconv", "true")
        git(self.dir, "config", "diff.b.binary", "true")
        for atributo in ("-diff", "binary", "diff=t", "diff=b"):
            with self.subTest(atributo):
                self.salvar({".gitattributes": f"lib.py {atributo}\n", "lib.py": "x = 1\n"}, base=True)
                self.salvar({"lib.py": self.COND})
                self.assertIn("sem mutante · lib.py:2", self.cobertura().stdout)

    def test_condicao_apagada_e_outra_nova_sem_relacao_no_mesmo_hunk_sai_apagada_e_a_editada_nao(self):  # A5 da segurança
        self.salvar({"lib.py": "x = 1\nif aaa > 100:\n    x = 2\nif b > 1:\n    x = 3\n"}, base=True)
        self.salvar({"lib.py": "x = 1\nif bbb == 777:\n    x = 2\nif b > 2:\n    x = 3\n",
                     **self.spec("if bbb == 777:", "if bbb == 778:")})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (1, [
            "coberta · lib.py:2 · tests/mutantes/x.json:M1 · declarado, não provado", "sem mutante · lib.py:4 · b > 2",
            "apagada · lib.py:2(base) · aaa > 100"]))

    def test_condicao_so_reformatada_no_hunk_nao_toma_o_lugar_da_editada(self):
        self.salvar({"lib.py": "a = 1\nif (p): a = 2\nif aaa > 1: a = 3\n"}, base=True)
        self.salvar({"lib.py": "a = 1\nif p: a = 2\nif aaa > 2: a = 3\n", **self.spec("if aaa > 2:", "if aaa > 3:")})
        r = self.cobertura()
        self.assertEqual((r.returncode, len(r.stdout.splitlines())), (0, 2), r.stdout)

    def test_arquivo_de_shell_sai_nao_coberto_uma_vez_sem_olhar_a_linha(self):
        casos = {"run.sh": "#!/bin/sh\nif [ -f /etc/x ]; then exit 1; fi\n",
                 ".githooks/pre-x": "#!/bin/sh\nif [ -f /etc/x ]; then exit 1; fi\nif [ -n a ]; then :; fi\n",
                 "bin/run": "#!/usr/bin/env bash\ncat <<EOF\nit's\n  EOF\nit's\nEOF\nif [ -f /etc/x ]; then exit 1; fi\n",
                 "sonda.sh": "#!/bin/sh\nbash -c 'echo a\n'\nif [ -f /etc/x ]; then exit 1; fi\nx=$[1]; cat <<\"$f\"\n"}
        for nome, texto in casos.items():
            with self.subTest(nome):
                self.salvar({nome: texto})
                r = self.cobertura()
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(r.stdout.splitlines()[1:], [f"não coberto: {nome}"])
                self.salvar({nome: None})

    def test_isenta_para_arquivo_de_shell_e_solta_e_sai_2(self):
        self.salvar({"run.sh": "#!/bin/sh\nif [ -f /etc/x ]; then exit 1; fi\n",
                     **self.isentas([{"arquivo": "run.sh", "trecho": "[ -f /etc/x ]", "motivo": self.MOTIVO}])})
        r = self.cobertura()
        self.assertEqual(r.returncode, 2)
        self.assertIn("isenta que não cruza", r.stderr)

    MOTIVO = "mensagem de erro sem efeito"
    ISENTA = {"arquivo": "lib.py", "trecho": "x > 100 and y", "motivo": MOTIVO}
    COND2 = "x = 1\nif x > 100 and y:\n    x = 2\n"

    def isentas(self, lista, nome="i", mutantes=None):
        mutantes = mutantes or [mutante(de="if x > 100:", para="if x > 1000:", arquivo="outro.py")]
        return {f"tests/mutantes/{nome}.json": json.dumps({"pedido": "x", "mutantes": mutantes, "isentas": lista})}

    def test_isenta_libera_a_condicao_sem_mutante_e_a_apagada_e_impressa(self):
        self.salvar({"lib.py": self.COND2, **self.isentas([self.ISENTA])})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (0, [f"isenta · lib.py:2 · {self.MOTIVO}"]), r.stderr)
        git(self.dir, "reset", "-q", "--hard", self.base)
        self.salvar({"lib.py": self.COND2}, base=True)
        self.salvar({"lib.py": "x = 1\n", **self.isentas([self.ISENTA])})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (0, [f"isenta · lib.py:2(base) · {self.MOTIVO}"]), r.stderr)

    def test_isenta_que_nao_cruza_condicao_listada_ou_nao_casa_uma_vez_e_2(self):
        casos = {"coberta por mutante": ({"lib.py": self.COND2, "tests/mutantes/i.json": json.dumps({"pedido": "x", "mutantes": [
                     mutante(de="if x > 100 and y:", para="if x > 100 or y:")], "isentas": [self.ISENTA]})}),
                 "trecho duas vezes": {"lib.py": self.COND2 + self.COND2, **self.isentas([self.ISENTA])},
                 "trecho fora do nó": {"lib.py": self.COND2, **self.isentas([{**self.ISENTA, "trecho": "x = 1\nif x > 100"}])},
                 "outro arquivo": {"lib.py": self.COND2, **self.isentas([{**self.ISENTA, "arquivo": "outro.py"}])},
                 "trecho além do nó": {"lib.py": self.COND2, **self.isentas([{**self.ISENTA, "trecho": "x > 100 and y:\n    x = 2"}])},
                 "trecho que não existe": {"lib.py": self.COND2, **self.isentas([{**self.ISENTA, "trecho": "x > 100 and z"}])}}
        for nome, arquivos in casos.items():
            with self.subTest(nome):
                self.salvar(arquivos)
                r = self.cobertura()
                git(self.dir, "reset", "-q", "--hard", self.base)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn("isenta que não cruza condição listada", r.stderr)

    def test_isenta_invalida_e_mais_de_oito_somadas_sao_2(self):
        ruins = [{**self.ISENTA, "trecho": "x > 100"}, {**self.ISENTA, "motivo": "n/a"}, {**self.ISENTA, "arquivo": "tests/test_a.py"},
                 {**self.ISENTA, "extra": "x"}, {**self.ISENTA, "motivo": 20}, "x"]
        for ruim in ruins:
            with self.subTest(ruim):
                self.salvar({"lib.py": self.COND2, **self.isentas([ruim])})
                r = self.cobertura()
                git(self.dir, "reset", "-q", "--hard", self.base)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn("isenta 1: arquivo, trecho", r.stderr)
        self.salvar({"lib.py": self.COND2, **self.isentas([self.ISENTA] * 5), **self.isentas([self.ISENTA] * 4, "j")})
        r = self.cobertura()
        self.assertEqual(r.returncode, 2)
        self.assertIn("mais de 8 isentas somadas", r.stderr)
        self.salvar(self.isentas([self.ISENTA] * 9))
        self.assertIn("isentas é uma lista de até 8", self.cobertura().stderr)

    def test_tetos_do_diff_e_das_condicoes_dizem_qual_e_sao_2(self):
        self.salvar({"lib.py": self.COND2})
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.dir)
        with mock.patch.object(self.f, "MAXIMO_DO_DIFF", 10), self.assertRaisesRegex(ValueError, "o diff passa de 10 bytes"):
            self.f.mudancas(self.base, self.cabeca())
        com_duas = "if a:\n    pass\nif b:\n    pass\n"
        with mock.patch.object(self.f, "MAXIMO_DE_CONDICOES", 1):
            with self.assertRaisesRegex(ValueError, "lib.py: mais de 1 condições"):
                self.f.analisar("lib.py", [], "", com_duas, [], [], set())
            self.assertEqual(len(self.f.analisar("lib.py", [], "", "if a:\n    pass\n", [], [], set())), 0)
        self.assertEqual(len(self.f.analisar("lib.py", [], "", com_duas, [], [], set())), 0)

    def test_spec_acima_do_teto_de_64_kib_e_entrada_invalida(self):
        spec = {"pedido": "x", "mutantes": [mutante(de="if x > 100:", para="if x > 1000:")], "pad": "a" * 70000}
        self.salvar({"lib.py": self.COND, "tests/mutantes/x.json": json.dumps(spec)})
        r = self.cobertura()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("com mais de 65536 bytes", r.stderr)

    def test_cada_tipo_de_condicao_conta_pelo_no_mais_externo(self):
        casos = {"if a > 1:\n    pass\nelif b:\n    pass\n": ["a > 1", "b"], "while x < 3:\n    pass\n": ["x < 3"],
                 "y = 1 if c else 2\n": ["c"], "z = [i for i in r if i % 2]\n": ["i % 2"], "assert a == b\n": ["a == b"],
                 "match x:\n    case 1 if x > 5:\n        pass\n": ["x > 5"], "def f():\n    return a > b\n": ["a > b"],
                 "k = not p\n": ["not p"], "if a and b > 1:\n    pass\n": ["a and b > 1"], "k = -p + 1\n": []}
        for texto, esperado in casos.items():
            with self.subTest(texto):
                self.assertEqual([c[0] for c in self.f.condicoes(texto)], esperado)

    def casa(self, de, para, texto, arquivo="lib.py"):
        ini, fim = self.f.condicoes(texto)[0][3:]
        return self.f.casa(mutante(de=de, para=para, arquivo=arquivo), "lib.py", texto, ini, fim)

    def test_casamento_pelo_intervalo_do_no_e_as_travas_do_de(self):
        texto = "k = 1\nif x > 1000:\n    pass\n"
        self.assertTrue(self.casa("\nif x > 1000:", "\nif x > 2000:", texto))
        self.assertFalse(self.casa("\nif x > 100", "\nif x > 200", texto), "o de tem 7 caracteres não brancos")
        self.assertFalse(self.casa("k = 1\nif x > 1000", "k = 2\nif x > 1000", texto), "a troca fica antes do nó")
        self.assertFalse(self.casa("if x > 1000:\n    pass", "if x > 1000:\n    fail", texto), "a troca fica depois do nó")
        self.assertFalse(self.casa("if x > 1000:", "if x > 2000:", texto, arquivo="outro.py"))
        repetido = "if x > 1000:\n    pass  # if x > 1000:\n"
        self.assertFalse(self.casa("if x > 1000:", "if x > 2000:", repetido), "o de aparece duas vezes")
        self.assertTrue(self.casa("t = x > 1000", "t = x > 2000", 's = "éé"; t = x > 1000\n'), "deslocamento em bytes")

    def test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam(self):
        """MUTANTE-CASA-ESPACO: o prefixo comum engole o espaço junto da condição e o sufixo comum começa nele."""
        self.assertTrue(self.casa("x if f() else y", "x if f() and False else y", "k = x if f() else y\n"), "ternário")
        texto = "k = any(p and q(l) for l in r)\n"
        self.assertTrue(self.casa("p and q(l) for l in", "p and q(l) and False for l in", texto), "fim do nó")
        self.assertFalse(self.casa("else yyyy", "else yyyyy", "k = 1 if a > b else yyyy\n"), "desliza fora do nó")
        try:
            removido = self.casa("k = q if aa e", "k = q if e", "k = q if aa else aa\n")
        except SyntaxError as erro:
            self.fail(f"remove mais que o nó: o casa aplicou a troca fora do nó ({erro})")
        self.assertFalse(removido, "remove mais que o nó")

    def test_troca_que_nao_muda_o_ast_e_mutante_de_fachada(self):
        with self.assertRaises(ValueError):
            self.casa("\nif x > 1000:", "\nif (x > 1000):", "k = 1\nif x > 1000:\n    pass\n")

    def test_so_a_spec_que_o_diff_adiciona_ou_edita_cobre_e_a_removida_ou_editada_e_listada(self):
        self.salvar(self.spec("if x > 100:", "if x > 1000:"), base=True)
        self.salvar({"lib.py": self.COND})
        self.assertEqual(self.cobertura().returncode, 1, "a spec que já estava na base não cobre")
        self.salvar(self.spec("if x > 100:", "if x > 2000:"))
        r = self.cobertura()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("spec editada · tests/mutantes/x.json", r.stdout)
        self.salvar({"tests/mutantes/x.json": None})
        r = self.cobertura()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("spec removida · tests/mutantes/x.json", r.stdout)
        self.salvar({"tests/mutantes/y.json": json.dumps({"pedido": "x", "mutantes": []})})
        r = self.cobertura()
        self.assertEqual(r.returncode, 2)
        self.assertIn("spec inválida", r.stderr)

    def test_base_que_nao_resolve_e_diff_vazio_sao_2_e_a_arvore_suja_so_avisa(self):
        self.salvar({"lib.py": self.COND})
        for args in (("--base", "nao-existe"), ("--base", self.base, "--rev=-x")):
            r = self.rodar("--cobertura", *args)
            self.assertEqual(r.returncode, 2)
            self.assertIn("precisam resolver", r.stderr)
        r = self.rodar("--cobertura", "--base", "HEAD")
        self.assertEqual(r.returncode, 2)
        self.assertIn("diff é vazio", r.stderr)
        (self.dir / "lib.py").write_text("x = 1\nwhile y:\n    pass\n", encoding="utf-8")
        r = self.cobertura()
        self.assertEqual(r.returncode, 1)
        self.assertIn("x > 100", r.stdout)
        self.assertNotIn("while", r.stdout)
        self.assertIn("árvore de trabalho suja", r.stderr)

    def test_nao_coberto_aparece_e_teste_doc_e_arquivo_removido_ficam_fora(self):
        self.salvar({"run.sh": "#!/bin/sh\nif [ -f x ]; then :; fi\n", ".github/workflows/ci.yml": "on: push\n",
                     "tools/notas": "python = 1\nif x:\n    pass\n", "tools/ferramenta": "#!/usr/bin/env python3\nif y:\n    pass\n",
                     "docs/a.md": "# t\n", "changelog.d/x.md": "t\n", "tests/test_x.py": "if x:\n    pass\n",
                     "novo.py": "if z:\n    pass\n"})
        self.salvar({"lib.py": None})
        r = self.cobertura()
        self.assertEqual(r.stdout.splitlines()[1:], ["não coberto: .github/workflows/ci.yml", "sem mutante · novo.py:1 · z",
                         "não coberto: run.sh", "sem mutante · tools/ferramenta:2 · y", "não coberto: tools/notas"])
        self.assertEqual(r.returncode, 1)

    def test_limites_e_nomes_de_arquivo_hostis(self):
        for nome, texto in {"a.py": "if :\n", "b.py": "x = 1\n" * 200000}.items():
            with self.subTest(nome):
                self.salvar({nome: texto})
                self.assertEqual(self.cobertura().returncode, 2)
                git(self.dir, "reset", "-q", "--hard", self.base)
        self.salvar({f"f{i}.txt": "" for i in range(300)})
        self.assertEqual(self.cobertura().returncode, 0)
        self.salvar({"mais.txt": ""})
        self.assertEqual(self.cobertura().returncode, 2)
        git(self.dir, "reset", "-q", "--hard", self.base)
        self.salvar({"-x.py": "if y:\n    pass\n", "a b.py": "if z:\n    pass\n"})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (1, ["sem mutante · -x.py:1 · y", "sem mutante · a b.py:1 · z"]))
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.dir)
        with self.assertRaises(ValueError):
            self.f.ler_no_commit(self.base, "nao_existe.py")

    def test_cobertura_e_base_vem_juntos_e_sem_spec(self):
        for args in (("--cobertura",), ("--base", self.base), ("--cobertura", "--base", self.base, "spec.json")):
            with self.subTest(args):
                r = self.rodar(*args)
                self.assertEqual(r.returncode, 2)
                self.assertIn("vêm juntos", r.stderr)


if __name__ == "__main__":
    unittest.main()
