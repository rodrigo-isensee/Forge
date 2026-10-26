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

    def test_de_um_a_oito_mutantes(self):
        self.assertTrue(self.problemas())
        self.assertEqual(self.problemas(*[mutante(f"M{i}") for i in range(1, 9)]), [])
        self.assertTrue(self.problemas(*[mutante(f"M{i}") for i in range(1, 10)]))

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
        nove = {"pedido": "x", "mutantes": [mutante(f"B{i}") for i in range(1, 10)]}
        self.assertTrue(self.f.validar_specs([oito, nove]), "o teto de 8 continua por spec")

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

    def test_mais_de_oito_mutantes_sai_2(self):
        r = self.rodar(self.spec(*[mutante(f"M{i}") for i in range(1, 10)]))
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
        b = self.spec(*[mutante(f"B{i}") for i in range(1, 10)], nome="x-2.json")
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


if __name__ == "__main__":
    unittest.main()
