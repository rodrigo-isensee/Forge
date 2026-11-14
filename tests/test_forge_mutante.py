"""`bin/forge-mutante` (OK-14 e M-1): mutantes declarados do pedido; evidência do QA, não portão."""
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
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

    def test_erro_do_teste_declarado_mata_so_com_o_controle_verde(self):  # MUTANTE-ERRO-INVALIDO
        D, erro = ["tests.m.T.t"], [{"id": "tests.m.T.t", "res": "erro", "carga": False}]
        classe, motivo = self.f.veredito(D, erro, erro_mata=True)
        self.assertEqual((classe, motivo), ("morreu", self.f.MORREU_POR_ERRO))
        self.assertTrue(motivo.startswith("(erro)"))
        self.assertEqual(self.f.veredito(D, erro)[0], "inválido")  # o controle: erro sem o mutante não é verde

    def test_erro_que_nao_e_do_teste_declarado_segue_invalido(self):  # MUTANTE-ERRO-INVALIDO
        carga = [{"id": "tests.m", "res": "erro", "carga": True}]
        self.assertEqual(self.f.veredito(["tests.m"], carga, erro_mata=True)[0], "inválido")
        fixture = [{"id": "tests.m.T.t", "res": "ok"}, {"id": "setUpClass (tests.m.T)", "res": "erro"}]
        self.assertEqual(self.f.veredito(["tests.m.T.t"], fixture, erro_mata=True)[0], "inválido")
        faltou = [{"id": "tests.m.T.t", "res": "erro"}]
        self.assertEqual(self.f.veredito(["tests.m.T.t", "tests.m.T.u"], faltou, erro_mata=True)[0], "inválido")

    def test_falha_com_erro_e_morte_por_assercao(self):  # MUTANTE-ERRO-INVALIDO
        D = ["tests.m.T"]
        registro = [{"id": "tests.m.T.t", "res": "erro"}, {"id": "tests.m.T.u", "res": "falha"}]
        self.assertEqual(self.f.veredito(D, registro, erro_mata=True), ("morreu", ""))
        self.assertEqual(self.f.veredito(D, [{"id": "tests.m.T.t", "res": "ok"}], erro_mata=True), ("sobreviveu", ""))

    def test_registro_marca_o_erro_de_carga(self):  # MUTANTE-ERRO-INVALIDO
        class Falso:
            def __init__(self, ident):
                self.ident = ident

            def id(self):
                return self.ident

        registro = self.f.Registro()
        registro.addError(Falso("unittest.loader._FailedTest.tests.m"), None)
        registro.addError(Falso("tests.m.T.t"), None)
        self.assertEqual(registro.por_id["tests.m"], {"id": "tests.m", "res": "erro", "carga": True})
        self.assertEqual(registro.por_id["tests.m.T.t"], {"id": "tests.m.T.t", "res": "erro", "carga": False})


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


class Encerramento(unittest.TestCase):
    """L33: depois do sinal ou do erro de um processo, nenhum teste novo começa."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def test_rodar_depois_do_encerramento_nao_lanca_processo(self):
        self.addCleanup(self.f.ABORTAR.clear)
        self.f.ABORTAR.set()
        with mock.patch.object(self.f.subprocess, "Popen") as popen:
            self.assertIsNone(self.f.rodar(Path("."), ["tests.m.T.t"], "registro.jsonl", 5))
        popen.assert_not_called()


class ArvoreQueMuda(unittest.TestCase):
    """MUTANTE-ARVORE-MUDOU: a árvore se confere a cada mutante pronto; a primeira mudança para a rodada já."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def rodada(self, sujar_depois_de):
        """Dublês do `git status` e do `provar`: o mutante `sujar_depois_de` suja a árvore ao terminar; o M2 espera o
        sinal de parada (no máximo 5 s) e conta se o recebeu, se chegou a sair da fila; o M3 só anota que rodou."""
        estado, chamados, parada = {"status": ""}, [], []

        def git(*args, cwd=None):
            self.assertEqual(args, ("status", "--porcelain"))
            return estado["status"]

        def provar(m, *resto):
            chamados.append(m["id"])
            if m["id"] == "M2":
                parada.append(self.f.ABORTAR.wait(5))
                time.sleep(0.5)  # a parada cancela o M3 antes de ele sair da fila
            if m["id"] == sujar_depois_de:
                estado["status"] = " M lib.py\n?? novo.txt\n"
            return f"{m['id']} · morreu · lib.py:2", 0, True

        self.addCleanup(self.f.ABORTAR.clear)
        specs = [(b"{}", {"pedido": "x", "mutantes": [mutante("M1"), mutante("M2"), mutante("M3")]})]
        with mock.patch.object(self.f, "git", git), mock.patch.object(self.f, "provar", provar), \
                mock.patch.object(self.f, "anotar") as anotar, \
                mock.patch("sys.stdout", new_callable=io.StringIO) as saida, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as erro:
            codigo = self.f.principal(specs, "a" * 40, 5)
        return codigo, saida.getvalue(), erro.getvalue(), chamados, parada, anotar

    def test_a_primeira_mudanca_para_a_rodada_no_mutante_seguinte_e_diz_o_que_mudou(self):
        codigo, saida, erro, chamados, parada, anotar = self.rodada("M1")
        self.assertEqual(codigo, 2, saida + erro)
        self.assertIn("parei depois do mutante M1 (1 de 3 prontos)", erro)
        self.assertIn("   M lib.py\n  ?? novo.txt\n", erro)
        self.assertIn("a rodada recomeça do zero", erro)
        self.assertTrue(all(parada), "o M2 em curso não recebeu o sinal de parada")  # ou foi cancelado na fila
        self.assertNotIn("M3", chamados, "o mutante da fila rodou depois da mudança")
        self.assertNotIn("morreu", saida, "resultado de rodada com a árvore mudada saiu como prova")
        anotar.assert_not_called()

    def test_arvore_parada_roda_todos_e_nao_avisa(self):
        codigo, saida, erro, chamados, parada, anotar = self.rodada(None)
        self.assertEqual(codigo, 0, saida + erro)
        self.assertEqual(chamados, ["M1", "M2", "M3"])
        self.assertEqual(parada, [False])
        self.assertNotIn("árvore", erro)
        for ident in ("M1", "M2", "M3"):
            self.assertIn(f"{ident} · morreu", saida)


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
        self.assertNotIn("fora do commit", r.stdout)  # o teste está no commit e falha de verdade

    def test_controle_vermelho_por_teste_fora_do_commit_diz_qual_teste_falta_commitar(self):
        self.gravar("tests/test_lib.py", TESTE + "\n    def test_novo(self):\n        self.assertTrue(lib.limite(11))\n")
        self.gravar("tests/test_outro.py", TESTE)  # nem o módulo está no commit
        sha = git(self.dir, "rev-parse", "HEAD")[:12]
        for teste in ("tests.test_lib.T.test_novo", "tests.test_outro.T.test_borda"):
            with self.subTest(teste):
                r = self.rodar(self.spec(mutante(testes=["tests.test_lib.T.test_borda", teste])))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn(f"M1 · controle vermelho · lib.py · teste fora do commit {sha}: {teste} (commite o teste",
                              r.stdout)

    def test_log_que_nao_se_grava_vira_aviso_e_o_veredito_fica(self):  # candidata 8 da retro 0.45.6
        (self.dir / ".forge" / "run" / "testes.log").mkdir(parents=True)  # o root grava em arquivo só leitura; a pasta, não
        r = self.rodar(self.spec(mutante()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("M1 · morreu · lib.py:2", r.stdout)
        self.assertIn("forge-mutante: aviso: não gravei .forge/run/testes.log", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_mutante_que_leva_o_teste_a_erro_morre_por_erro_e_sai_0(self):  # MUTANTE-ERRO-INVALIDO
        r = self.rodar(self.spec(mutante(de="return 2", para="return None + 2")))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("M1 · morreu · lib.py:3 · (erro)", r.stdout)

    def test_teste_que_da_erro_tambem_sem_o_mutante_sai_2_e_nunca_morreu(self):  # MUTANTE-ERRO-INVALIDO
        self.gravar("tests/test_lib.py", TESTE + "\n    def test_quebrado(self):\n        raise KeyError('x')\n")
        self.salvar()
        r = self.rodar(self.spec(mutante(de="return 2", para="return None + 2",
                                         testes=["tests.test_lib.T.test_quebrado"])))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("controle vermelho", r.stdout)
        self.assertNotIn("morreu", r.stdout)

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

    # ---- L33 (M4): k processos, um clone cada ----
    def com_testes_de_pid(self, *nomes, corpo="__import__('time').sleep(60)"):
        """Acrescenta ao teste um método por nome: grava o pid e o cwd em `fora/` e roda `corpo`."""
        extra = "".join(f"\n    def {n}(self):\n        d = {str(self.fora)!r}\n        os = __import__('os')\n"
                        f"        open(d + '/pid-' + str(os.getpid()), 'w').write(os.getcwd())\n        {corpo}\n" for n in nomes)
        self.gravar("tests/test_lib.py", TESTE + extra)
        self.salvar()

    def test_k_processos_dao_o_mesmo_veredito_que_em_serie(self):  # L33, C-33a
        casos = {"1 sobrevive": [mutante("M1"), mutante("M2", para="x > 99"), mutante("M3", para="x > 9")],
                 "todos morrem": [mutante("M1"), mutante("M2", para="x > 99"), mutante("M3", para="x > 90")],
                 "um inválido": [mutante("M1"), mutante("M2", de="x > 11"), mutante("M3", para="x > 9")]}
        for nome, mutantes in casos.items():
            with self.subTest(nome):
                spec = self.spec(*mutantes)
                serie, paralelo = self.rodar(spec, "--processos", "1"), self.rodar(spec, "--processos", "3")
                self.assertEqual((paralelo.returncode, paralelo.stdout), (serie.returncode, serie.stdout), paralelo.stderr)
                self.assertEqual(serie.returncode, {"1 sobrevive": 1, "todos morrem": 0, "um inválido": 2}[nome], serie.stdout)
                self.assertEqual(list(self.tmp.iterdir()), [], "sobrou cópia em $TMPDIR")

    def test_cada_processo_roda_na_sua_copia(self):  # L33, T-33
        self.com_testes_de_pid("test_copia", corpo="pass")
        spec = self.spec(*[mutante(f"M{i}", para=f"x > 9{i}", testes=["tests.test_lib.T.test_copia"]) for i in range(1, 4)])
        r = self.rodar(spec, "--processos", "3")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)  # os três sobrevivem: o teste não olha a lib
        copias = {p.read_text(encoding="utf-8") for p in self.fora.glob("pid-*")}
        self.assertEqual(len(copias), 3, copias)  # o controle e cada mutante ficam na pasta de um mutante, três pastas
        self.assertTrue(all(str(self.tmp) in c for c in copias), copias)

    def test_processos_fora_da_faixa_sai_2(self):  # L33, C-33b
        for k in ("0", "5", "-1"):
            with self.subTest(k):
                r = self.rodar(self.spec(mutante()), "--processos", k)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("--processos vai de 1 a 4", r.stderr)

    def test_processo_que_cai_e_sem_veredito_nunca_morreu_e_os_outros_seguem(self):  # L33, T-33
        self.com_testes_de_pid("test_cai", corpo="__import__('os').kill(__import__('os').getpid(), 9)")
        spec = self.spec(mutante("M1"), mutante("M2", testes=["tests.test_lib.T.test_cai"]), mutante("M3", para="x > 90"))
        r = self.rodar(spec, "--processos", "3")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("M1 · morreu · lib.py:2", r.stdout)
        self.assertIn("M2 · sem veredito", r.stdout)
        self.assertNotIn("M2 · morreu", r.stdout)
        self.assertIn("M3 · morreu · lib.py:2", r.stdout)

    def test_sigterm_no_meio_mata_todos_os_processos_e_apaga_as_copias(self):  # L33, C-33a
        self.com_testes_de_pid("test_a", "test_b", "test_c")
        spec = self.spec(*[mutante(f"M{i}", testes=[f"tests.test_lib.T.test_{c}"]) for i, c in zip((1, 2, 3), "abc")])
        p = subprocess.Popen([sys.executable, str(FERRAMENTA), spec, "--processos", "3"], cwd=self.dir,
                             env={**AMBIENTE, "TMPDIR": str(self.tmp)}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            limite = time.monotonic() + 60
            while len(list(self.fora.glob("pid-*"))) < 3:
                self.assertLess(time.monotonic(), limite, "os três processos de teste não subiram")
                time.sleep(0.1)
            pids = [int(x.name[4:]) for x in self.fora.glob("pid-*")]
            p.send_signal(signal.SIGTERM)
            try:
                codigo = p.wait(timeout=20)  # os testes dormem 60 s: sair antes disso é o sinal que os matou
            except subprocess.TimeoutExpired:
                self.fail("o forge-mutante não saiu em 20 s depois do SIGTERM")
            self.assertEqual(codigo, 143)
        finally:
            if p.poll() is None:
                p.kill()
            p.communicate()
        self.assertEqual(list(self.tmp.iterdir()), [], "sobrou cópia em $TMPDIR")
        for pid in pids:
            for _ in range(50):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.1)
            else:
                self.fail(f"o processo de teste {pid} segue vivo")

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

    def test_bytecode_fora_da_copia_e_o_mutante_nao_le_o_do_controle(self):
        """O teste que mede CPU de um script grande não paga a compilação a cada subprocesso (controle vermelho do
        `test_doutor`): o bytecode vai para uma pasta fora da cópia, e a do mutante não é a do controle (a troca do
        mesmo tamanho no mesmo segundo leria o `.pyc` velho e o mutante sobreviveria)."""
        corpo = ("assert 'PYTHONDONTWRITEBYTECODE' not in os.environ\n"
                 "        prefixo = os.environ.get('PYTHONPYCACHEPREFIX', os.getcwd())\n"
                 "        self.assertFalse(os.path.realpath(prefixo).startswith(os.path.realpath(os.getcwd())))\n"
                 "        r = subprocess.run([sys.executable, '-c', 'import lib; assert lib.limite(11) == 2'])\n"
                 "        self.assertEqual(r.returncode, 0)")
        self.gravar("tests/test_lib.py", "import os, subprocess, sys\n" + TESTE
                    + f"\n    def test_filho(self):\n        {corpo}\n")
        self.salvar()
        r = self.rodar(self.spec(mutante(de="x > 10", para="x > 99", testes=["tests.test_lib.T.test_filho"])),
                       PYTHONDONTWRITEBYTECODE="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("M1 · morreu", r.stdout)

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

    # MUTANTE-CONDICAO-MOVIDA (v0457 E13.1): a condição que sai de um arquivo e entra coberta noutro é movida.
    MOVIDA = "def f(x, y):\n    if x > 100 and y:\n        return 1\n    return 0\n"

    def test_condicao_movida_coberta_noutro_arquivo_sai_movida_e_0_e_a_so_apagada_sai_1(self):
        self.salvar({"lib.py": "x = 1\n" + self.MOVIDA + "if z < 3:\n    pass\n"}, base=True)
        novo = self.MOVIDA.replace("x > 100 and y", "(x  >  100) and y")  # espaços e parênteses: o mesmo texto
        self.salvar({"lib.py": "x = 1\n", "mod.py": novo, **self.spec("(x  >  100) and y", "(x  >  101) and y",
                                                                       arquivo="mod.py")})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (1, [
            "apagada · lib.py:6(base) · z < 3", "movida · lib.py:3(base) · mod.py:2",
            "coberta · mod.py:2 · tests/mutantes/x.json:M1 · declarado, não provado"]), r.stderr)
        self.salvar({"lib.py": "x = 1\nif z < 3:\n    pass\n"})
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:3]), (0, [
            "movida · lib.py:3(base) · mod.py:2", "coberta · mod.py:2 · tests/mutantes/x.json:M1 · declarado, não provado"]))

    def test_movida_exige_coberta_e_uma_coberta_por_apagada(self):
        dupla = self.MOVIDA + self.MOVIDA.replace("def f", "def g")
        self.salvar({"lib.py": "x = 1\n" + dupla}, base=True)
        self.salvar({"lib.py": "x = 1\n", "mod.py": self.MOVIDA})  # sem mutante: segue apagada
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (1, [
            "apagada · lib.py:3(base) · x > 100 and y", "sem mutante · mod.py:2 · x > 100 and y"]))
        self.salvar(self.spec("if x > 100 and y:", "if x > 101 and y:", arquivo="mod.py"))  # 1 coberta, 2 apagadas
        r = self.cobertura()
        self.assertEqual((r.returncode, r.stdout.splitlines()[1]), (1, "apagada · lib.py:3(base) · x > 100 and y"))

    def test_movidas_consome_o_destino_e_nao_casa_texto_diferente(self):
        cob = ["coberta · b.py:2 · s:M1 · declarado, não provado"]
        apag = ["apagada · a.py:1(base) · p", "apagada · c.py:1(base) · p", "apagada · d.py:1(base) · q"]
        saida = self.f.movidas([(apag, {0: ("p", 1), 1: ("p", 1), 2: ("q", 1)}), (cob, {0: ("p", 1)})])
        self.assertEqual(saida[:3], ["movida · a.py:1(base) · b.py:2", "apagada · c.py:1(base) · p",
                                     "apagada · d.py:1(base) · q"])

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

    # E4-IL: isenta por linha (`linha_base`), só para a condição apagada; casa a linha que a saída imprime em `(base)`.
    REPETIDA = "x = 1\nif x > 100 and y:\n    x = 2\nif x > 100 and y:\n    x = 3\n"
    SEM_A_PRIMEIRA = "x = 1\nx = 2\nif x > 100 and y:\n    x = 3\n"
    POR_LINHA = {**ISENTA, "linha_base": 2}

    def por_linha(self, lista, base=REPETIDA, ponta=SEM_A_PRIMEIRA):
        """Cobertura da `ponta` sobre a `base` com as `isentas` da spec `i`, a partir do commit inicial."""
        git(self.dir, "reset", "-q", "--hard", git(self.dir, "rev-list", "--max-parents=0", "HEAD").strip())
        self.salvar({"lib.py": base}, base=True)
        self.salvar({"lib.py": ponta, **self.isentas(lista)})
        return self.cobertura()

    def test_isenta_por_linha_libera_a_apagada_de_texto_repetido(self):
        for antes in ("", 's = "ção"\n'):  # o texto não ASCII antes da condição desloca bytes e caracteres
            with self.subTest(antes):
                linha, base, ponta = 2 + bool(antes), antes + self.REPETIDA, antes + self.SEM_A_PRIMEIRA
                r = self.por_linha([{**self.POR_LINHA, "linha_base": linha}], base, ponta)
                self.assertEqual((r.returncode, r.stdout.splitlines()[1:]),
                                 (0, [f"isenta · lib.py:{linha}(base) · {self.MOTIVO}"]), r.stderr)
        self.assertEqual(self.por_linha([self.ISENTA]).returncode, 2, "a forma antiga não casa o texto repetido")
        nova = self.SEM_A_PRIMEIRA + "if w > 500 and v:\n    x = 4\n"
        r = self.por_linha([self.POR_LINHA, {**self.ISENTA, "trecho": "w > 500 and v"}], ponta=nova)
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:]), (0, [f"isenta · lib.py:5 · {self.MOTIVO}",
                         f"isenta · lib.py:2(base) · {self.MOTIVO}"]), r.stderr)

    def test_isenta_por_linha_que_nao_casa_a_linha_impressa_fica_solta(self):
        duas = "x = 1\nif x > 100 and y:\n    x = 2\nif z > 300 and w:\n    x = 3\n"
        casos = {"segunda ocorrência": ([{**self.POR_LINHA, "linha_base": 4}], {}),
                 "linha sem condição": ([{**self.POR_LINHA, "linha_base": 1}], {}),
                 "além do fim da base": ([{**self.POR_LINHA, "linha_base": 99}], {}),
                 "outro arquivo": ([{**self.POR_LINHA, "arquivo": "outro.py"}], {}),
                 "trecho fora do nó": ([{**self.POR_LINHA, "trecho": "x = 1\nif x > 100"}], {}),
                 "condição nova": ([{**self.POR_LINHA, "trecho": "z > 300 and w", "linha_base": 6}],
                                   {"ponta": self.REPETIDA + "if z > 300 and w:\n    x = 4\n"}),
                 "linha da outra apagada": ([{**self.POR_LINHA, "linha_base": 4}], {"base": duas, "ponta": "x = 1\nx = 2\nx = 3\n"}),
                 "ocorrência não impressa": ([{**self.POR_LINHA, "linha_base": 4}],
                                             {"ponta": "x = 1\nif x > 100 and y:\n    x = 2\nx = 3\n"}),
                 "isenta repetida": ([self.POR_LINHA, self.POR_LINHA], {}),
                 "base deslocada": ([self.POR_LINHA], {"base": "# novo\n" + self.REPETIDA, "ponta": "# novo\n" + self.SEM_A_PRIMEIRA})}
        for nome, (lista, arquivos) in casos.items():
            with self.subTest(nome):
                r = self.por_linha(lista, **arquivos)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn("isenta que não cruza condição listada", r.stderr)

    def test_isenta_por_linha_cobre_uma_condicao_so(self):  # C-4: duas condições externas na mesma linha da base
        base = "obj = 1\nif obj.ready > 100 and ok: y = 1 if obj.ready > 100 or z else 2\n"
        uma = {**self.POR_LINHA, "trecho": "obj.ready > 100"}
        r = self.por_linha([uma], base, "obj = 1\n")
        self.assertEqual((r.returncode, sorted(x.split(" · ")[0] for x in r.stdout.splitlines()[1:])), (1, ["apagada", "isenta"]))
        duas = [{**uma, "trecho": "obj.ready > 100 and ok"}, {**uma, "trecho": "obj.ready > 100 or z"}]
        self.assertEqual(self.por_linha(duas, base, "obj = 1\n").returncode, 0)

    def test_isenta_por_linha_nao_casa_texto_apagado_duas_vezes(self):  # C-4: A1 e sonda S1 da segurança g6
        ponta, usadas = "x = 1\nx = 2\nx = 3\n", set()
        saida = self.f.analisar("lib.py", [([2, 3, 4, 5], [2, 3])], self.REPETIDA, ponta, [], [self.POR_LINHA], usadas)
        self.assertEqual((saida, usadas), (["apagada · lib.py:2(base) · x > 100 and y"], set()))
        for lista in ([self.POR_LINHA], [self.POR_LINHA, {**self.POR_LINHA, "linha_base": 4}]):
            with self.subTest(len(lista)):
                self.assertNotEqual(self.por_linha(lista, ponta=ponta).returncode, 0)

    def test_isenta_por_linha_invalida_e_o_teto_conta_as_duas_formas(self):
        maximo = self.f.MAXIMO_DO_ARQUIVO
        ruins = [{**self.POR_LINHA, "linha_base": v} for v in ("2", True, False, 0, -1, maximo + 1, 2.0, None)]
        ruins += [{**self.POR_LINHA, "motivo": "m" * 19}, {**self.POR_LINHA, "trecho": "x > 100 an"},
                  {**self.POR_LINHA, "extra": "x"}, {k: v for k, v in self.POR_LINHA.items() if k != "trecho"}]
        for ruim in ruins:
            with self.subTest(ruim):
                self.assertRegex(" ".join(self.f.validar_isentas([ruim])), r"^isenta 1: .*linha_base")
        self.assertEqual(self.f.validar_isentas([{**self.POR_LINHA, "linha_base": maximo}, self.POR_LINHA, self.ISENTA]), [])
        r = self.por_linha([{**self.POR_LINHA, "linha_base": True}])
        self.assertEqual(r.returncode, 2)
        self.assertRegex(r.stderr, r"isenta 1: .*linha_base")
        self.salvar({**self.isentas([self.POR_LINHA] * 5), **self.isentas([self.ISENTA] * 4, "j")})
        r = self.cobertura()
        self.assertEqual(r.returncode, 2)
        self.assertIn("mais de 8 isentas somadas", r.stderr)



class Conferir(unittest.TestCase):
    """`--conferir --base` (E1.140 da v047): o `de` e a `linha_base` das specs do diff no lugar, sem rodar teste."""
    MOTIVO = "condição apagada de propósito no teste"

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        git(self.dir, "init", "-q", "-b", "develop")
        self.salvar({"lib.py": "x = 1\nif x > 100000:\n    x = 2\n"})
        self.base = git(self.dir, "rev-parse", "HEAD").strip()

    def salvar(self, arquivos):
        for nome, texto in arquivos.items():
            (self.dir / nome).parent.mkdir(parents=True, exist_ok=True)
            (self.dir / nome).write_text(texto, encoding="utf-8")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "c")

    def conferir(self, *args):
        return subprocess.run([sys.executable, "-I", str(FERRAMENTA), "--conferir", *args], cwd=self.dir, env=AMBIENTE,
                              capture_output=True, text=True)

    def spec(self, isentas=(), de="if x > 100000:"):
        dados = {"pedido": "x", "mutantes": [mutante(de=de, para="if x > 1000:")], "isentas": list(isentas)}
        return {"tests/mutantes/x.json": json.dumps(dados)}

    def test_de_no_lugar_sai_0_e_de_que_sumiu_depois_da_spec_sai_1_com_a_spec_e_o_trecho(self):
        self.salvar(self.spec())
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("conferidas: o trecho de cada spec do diff está no lugar", r.stdout)
        self.salvar({"lib.py": "x = 1\nif x > 100001:\n    x = 2\n"})  # a spec não muda; a linha vigiada, sim
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tests/mutantes/x.json: M1 · o trecho aparece 0 vezes em lib.py (precisa de uma) · 'if x > 100000:'",
                      r.stdout)

    def test_arquivo_vigiado_que_sumiu_sai_1_sem_cair(self):
        self.salvar({"tests/mutantes/x.json": json.dumps({"pedido": "x", "mutantes": [mutante(arquivo="sumiu.py")]})})
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("M1 · o trecho aparece 0 vezes em sumiu.py", r.stdout)

    def test_linha_base_que_bate_sai_0_e_a_deslocada_sai_1(self):
        isenta = {"arquivo": "lib.py", "trecho": "x > 100000", "motivo": self.MOTIVO, "linha_base": 2}
        self.salvar({"lib.py": "x = 1\nif x > 200:\n    x = 2\n", **self.spec([isenta], de="if x > 200:")})
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.salvar(self.spec([{**isenta, "linha_base": 3}], de="if x > 200:"))
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tests/mutantes/x.json: isenta 1 · linha_base 3 de lib.py sem condição com o trecho na base", r.stdout)

    def test_isenta_em_arquivo_sem_parse_nao_bate(self):
        isenta = {"arquivo": "run.sh", "trecho": "[ -f /etc/x ]", "motivo": self.MOTIVO, "linha_base": 1}
        self.salvar({"run.sh": "if [ -f /etc/x ]; then :; fi\n"})
        self.base = git(self.dir, "rev-parse", "HEAD").strip()
        self.salvar(self.spec([isenta]))
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("isenta 1 · linha_base 1 de run.sh", r.stdout)

    def test_sem_spec_no_diff_sai_0_e_spec_invalida_ou_base_ilegivel_saem_2(self):
        self.salvar({"lib.py": "x = 2\n"})
        self.assertEqual(self.conferir("--base", self.base).returncode, 0)
        self.salvar({"tests/mutantes/x.json": json.dumps({"pedido": "x", "mutantes": []})})
        r = self.conferir("--base", self.base)
        self.assertEqual(r.returncode, 2)
        self.assertIn("tests/mutantes/x.json: spec inválida", r.stderr)
        self.assertEqual(self.conferir("--base", "nao-existe").returncode, 2)

    def test_conferir_exige_base_e_recusa_spec_e_cobertura(self):
        for args in ((), ("--base", "HEAD", "spec.json"), ("--base", "HEAD", "--cobertura")):
            with self.subTest(args):
                r = self.conferir(*args)
                self.assertEqual(r.returncode, 2)
                self.assertIn("--conferir vem com --base", r.stderr)


PLACAR = RAIZ / "scripts" / "placar-mutacao.py"
# `forge-mutante` falso: anota a chamada, recusa sem `--` e pedido misto (como o de verdade) e imprime uma linha por classe.
FALSO = ("import json, sys\na = sys.argv[1:]\nopen('.git/chamadas', 'a').write(json.dumps(a) + '\\n')\n"
         "specs = [json.load(open(s)) for s in a[1:]] if a[:1] == ['--'] else []\n"
         "if len({s['pedido'] for s in specs}) != 1:\n    sys.exit(2)\n"
         "for n, c in enumerate([c for s in specs for c in s['classes']]):\n"
         "    print(f'equivalente: M{n} · razão' if c == 'equivalente' else f'M{n} · {c} · x.py:1')\n"
         "print('M99 · morreu')\n")


class PlacarDaRelease(unittest.TestCase):
    """M-5: o placar roda o `forge-mutante` uma vez por spec da amostra (fixa mais as novas desde a tag); não é portão."""

    def commit(self, arquivos):
        for nome, classes in arquivos.items():
            dados = FALSO if nome == "bin/forge-mutante" else json.dumps({"pedido": nome, "classes": classes})
            (self.dir / nome).parent.mkdir(parents=True, exist_ok=True)
            (self.dir / nome).write_text(dados, encoding="utf-8")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "c")

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.dir, self.m = Path(pasta.name), "tests/mutantes/"
        git(self.dir, "init", "-q")
        (self.dir / ".git" / "chamadas").touch()
        self.commit({"bin/forge-mutante": None, self.m + "antiga.json": ["morreu"]})
        git(self.dir, "tag", "v1")
        self.commit({self.m + "placar.json": ["morreu", "morreu"], self.m + "antiga.json": ["sobreviveu"],
                     self.m + "nova-a.json": ["morreu", "sobreviveu"],
                     self.m + "nova-b.json": ["equivalente", "inválido", "sem veredito"]})

    def placar(self, *args):
        r = subprocess.run([sys.executable, "-I", str(PLACAR), *args], cwd=self.dir, capture_output=True, text=True,
                           env={k: v for k, v in AMBIENTE.items() if k != "CI"})
        chamadas = (self.dir / ".git" / "chamadas").read_text(encoding="utf-8").splitlines()
        return r, [json.loads(c) for c in chamadas]

    def test_uma_rodada_por_spec_soma_as_classes_e_sai_0_com_sobrevivente(self):
        r, chamadas = self.placar("--desde", "v1", "--versao", "0.41.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        amostra = ["placar.json", "nova-a.json", "nova-b.json"]  # a antiga, só editada desde a tag, fica fora
        self.assertEqual(chamadas, [["--", self.m + s] for s in amostra])
        self.assertIn(f"spec: {self.m}nova-a.json rc=0 mortos=1 sobreviveu=1 ", r.stdout)
        self.assertEqual(r.stdout.splitlines()[-1],
                         "placar: 0.41.0 mortos=3 sobreviveu=1 equivalente=1 invalido=1 sem-veredito=1 specs=3")

    def test_nome_que_parece_opcao_e_link_simbolico_ficam_fora(self):
        os.symlink("nova-a.json", self.dir / self.m / "link.json")
        self.commit({self.m + "--executar.json": ["morreu"]})
        r, chamadas = self.placar("--desde", "v1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"recusada: '{self.m}--executar.json'\nrecusada: '{self.m}link.json'\n", r.stdout)
        self.assertEqual(len(chamadas), 3)
        self.assertTrue(r.stdout.endswith(" specs=3\n"))

    def test_a_nona_spec_nova_sai_fora_da_amostra(self):
        self.commit({f"{self.m}z{n}.json": ["morreu"] for n in range(1, 8)})
        r, chamadas = self.placar("--desde", "v1")
        self.assertEqual(r.stdout.splitlines()[0], f"fora da amostra: {self.m}z7.json")
        self.assertEqual(chamadas[-1], ["--", self.m + "z6.json"])
        self.assertEqual(len(chamadas), 9)

    def test_desde_que_nao_e_commit_sai_2_sem_rodar_nada(self):
        for desde in ("nao-existe", "--all", "-HEAD"):
            with self.subTest(desde):
                r, chamadas = self.placar(f"--desde={desde}")
                self.assertEqual((r.returncode, chamadas), (2, []))
                self.assertIn("não é commit", r.stderr)


class MedidaDaVagaPesada(unittest.TestCase):
    """MAQ-A7: a cópia do contexto no forge-mutante faz o mesmo que a do forge-testes."""
    setUp, gravar, salvar, spec, rodar = Execucao.setUp, Execucao.gravar, Execucao.salvar, Execucao.spec, Execucao.rodar

    def test_a_linha_modo_mutante_traz_entrada_validada_e_load1(self):
        self.assertEqual(self.rodar(self.spec(mutante()), FORGE_ENTRADA="push\n").returncode, 0)
        linha = (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(linha), 1)
        self.assertRegex(linha[0], r"^\S+Z modo=mutante modulos=- duracao=[0-9.]+s saida=0 entrada=\? load1=[0-9.]+ "
                                   r"nproc=\d+ outras=(\d+|\?)$")

    def test_outras_e_contexto_toleram_falha_de_leitura(self):
        f, proc = carregar(), self.dir / "proc"
        for pid, pai, linha in ((10, 5, b"bin/forge-mutante"), (5, 1, b"suite-paralela.py"), (40, 1, b"")):  # 40 sumiu
            (proc / str(pid)).mkdir(parents=True)
            (proc / str(pid) / "stat").write_text(f"{pid} (a b) S {pai} 0", encoding="utf-8")
            (proc / str(pid) / ("cmdline" if linha else "outro")).write_bytes(linha)
        (proc / "self").mkdir()
        self.assertEqual(f.outras(proc, eu=10), 0)  # nem a própria, nem o ancestral pesado
        self.assertEqual(f.outras(self.dir / "sem-proc", eu=10), "?")
        with mock.patch("os.getloadavg", side_effect=OSError):
            self.assertIn(" load1=? ", f.contexto())


class DiffDeTextoGrande(unittest.TestCase):
    """MUTANTE-ASSERTEQUAL-TEXTO (versao-071 E2): o `assertEqual` de sequência grande de textos dá veredito no prazo."""

    TESTE_GRANDE = ("import unittest\n\n\n"
                    "def linhas(fim):\n"
                    "    return tuple(f'{i:05d} ' + ''.join(chr(97 + (i * 7 + j * 13) % 26) for j in range(60)) + fim\n"
                    "                 for i in range(400))\n\n\n"
                    "class G(unittest.TestCase):\n"
                    "    def test_tuplas(self):\n"
                    "        self.assertEqual(linhas('a'), linhas('b'))\n\n"
                    "    def test_texto(self):\n"
                    "        self.assertEqual('\\n'.join(linhas('a')), '\\n'.join(linhas('b')))\n\n"
                    "    def test_igual(self):\n"
                    "        self.assertEqual(linhas('a'), linhas('a'))\n")

    def executar(self, *ids):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "test_grande.py").write_text(self.TESTE_GRANDE, encoding="utf-8")
            registro = Path(d, "registro.jsonl")
            try:  # sem a troca, o ndiff passa de 30 s: estourar é falha da asserção, não erro do teste
                r = subprocess.run([sys.executable, str(FERRAMENTA), "--executar", *ids, "--registro", str(registro)],
                                   cwd=d, capture_output=True, text=True, timeout=30)
            except subprocess.TimeoutExpired:
                self.fail("o executor passou de 30 s montando o diff da asserção")
            self.assertEqual(r.returncode, 0, r.stderr)
            return {e["id"]: e["res"] for e in map(json.loads, registro.read_text(encoding="utf-8").splitlines())}

    def test_assertequal_de_textos_grandes_falha_dentro_do_prazo(self):
        ids = ("test_grande.G.test_tuplas", "test_grande.G.test_texto", "test_grande.G.test_igual")
        self.assertEqual(self.executar(*ids), dict(zip(ids, ("falha", "falha", "ok"))))

    def test_o_diff_omitido_e_uma_linha_so(self):
        f = carregar()
        self.assertEqual(list(f.DiffOmitido.ndiff(["a"], ["b"])), [f.DiffOmitido.AVISO])
        self.assertEqual(list(f.DiffOmitido.ndiff([], [], linejunk=None)), [f.DiffOmitido.AVISO])


class MutacaoDirigida(unittest.TestCase):
    """v046 E7 (M-1): `SPEC --base SHA` roda só os mutantes cujo arquivo mudou no diff; o resto sai `fora do diff`."""
    gravar, salvar, spec, rodar = Execucao.gravar, Execucao.salvar, Execucao.spec, Execucao.rodar
    OUTRO = "def f(y):\n    if y > 5:\n        return 1\n    return 0\n"

    def setUp(self):
        Execucao.setUp(self)
        self.gravar("outro.py", self.OUTRO)
        self.salvar()
        self.base = git(self.dir, "rev-parse", "HEAD").strip()
        self.dois = (mutante(), mutante("M2", de="y > 5", para="y >= 50", arquivo="outro.py"))

    def test_so_o_mutante_do_arquivo_mudado_roda(self):
        self.gravar("lib.py", LIB + "# mudou\n")
        self.salvar()
        r = self.rodar(self.spec(*self.dois), "--base", self.base)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(f"base={self.base} mb={self.base}", r.stdout)
        self.assertIn("M1 · morreu · lib.py:2", r.stdout)
        self.assertIn("fora do diff: M2 · outro.py", r.stdout)
        self.assertNotIn("M2 · ", r.stdout.replace("fora do diff: M2 · ", ""))

    def test_nenhum_mutante_no_diff_sai_2_sem_rodar(self):
        self.gravar("outro.py", self.OUTRO + "# mudou\n")
        self.salvar()
        r = self.rodar(self.spec(mutante()), "--base", self.base)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("nenhum mutante da spec cai no diff", r.stderr)
        self.assertNotIn("morreu", r.stdout)

    def test_teste_enfraquecido_entre_base_e_rev_roda_o_mutante_e_sobrevive(self):  # sondas S1 e S2 da v046 E7
        self.gravar("tests/test_lib.py", TESTE.replace("lib.limite(11), 2", "lib.limite(11), lib.limite(11)"))
        self.gravar("outro.py", self.OUTRO + "# mudou\n")
        self.salvar()
        r = self.rodar(self.spec(*self.dois), "--base", self.base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("M1 · sobreviveu", r.stdout)
        self.assertNotIn("fora do diff: M1", r.stdout)

    def test_spec_mudada_entre_base_e_rev_roda_os_mutantes_dela(self):
        caminho = self.dir / "tests" / "mutantes" / "x.json"
        caminho.parent.mkdir(parents=True)
        caminho.write_text(json.dumps({"pedido": "x", "mutantes": [mutante()]}), encoding="utf-8")
        self.salvar()
        base = git(self.dir, "rev-parse", "HEAD").strip()
        caminho.write_text(json.dumps({"pedido": "x", "mutantes": [mutante(para="x >= 11")]}), encoding="utf-8")
        self.salvar()
        r = self.rodar(str(caminho), "--base", base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("M1 · sobreviveu", r.stdout)
        self.assertNotIn("fora do diff", r.stdout)

    def test_helper_de_tests_enfraquecido_poe_todos_os_mutantes_no_diff(self):  # sonda S2 da v046 E7.7 (A4)
        self.gravar("tests/apoio.py", "def igual(caso, a, b):\n    caso.assertEqual(a, b)\n")
        self.gravar("tests/test_lib.py", TESTE.replace("self.assertEqual(lib.limite(11), 2)",
                                                       "apoio.igual(self, lib.limite(11), 2)")
                    .replace("import lib\n", "import lib\nfrom tests import apoio\n"))
        self.salvar()
        base = git(self.dir, "rev-parse", "HEAD").strip()
        self.gravar("tests/apoio.py", "def igual(caso, a, b):\n    return None\n")
        self.gravar("outro.py", self.OUTRO + "# mudou\n")
        self.salvar()
        r = self.rodar(self.spec(*self.dois), "--base", base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("apoio de teste no diff: tests/apoio.py · todos os mutantes entram", r.stdout)
        self.assertIn("M1 · sobreviveu", r.stdout)
        self.assertNotIn("fora do diff", r.stdout)

    def test_teste_e_spec_de_outro_mutante_nao_poem_todos_no_diff(self):
        self.gravar("tests/test_outro.py", "import unittest\n")
        self.gravar("tests/mutantes/outra.json", "{}\n")
        self.gravar("lib.py", LIB + "# mudou\n")
        self.salvar()
        r = self.rodar(self.spec(*self.dois), "--base", self.base)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("fora do diff: M2 · outro.py", r.stdout)
        self.assertNotIn("apoio de teste", r.stdout)

    def test_modulos_do_teste_cobrem_o_arquivo_do_teste(self):
        self.assertIn("tests/test_lib.py", carregar().modulos_do_teste("tests.test_lib.T.test_borda"))

    def test_base_que_nao_e_commit_ou_sem_ancestral_sai_2(self):
        git(self.dir, "switch", "-q", "--orphan", "solta")
        self.gravar("solta.txt", "x\n")
        git(self.dir, "add", "solta.txt")
        git(self.dir, "commit", "-qm", "solta")
        solta = git(self.dir, "rev-parse", "HEAD").strip()
        git(self.dir, "switch", "-q", "-f", "develop")
        for base, texto in (("nao-existe", "--base ilegível"), (solta, "merge-base")):
            with self.subTest(base):
                r = self.rodar(self.spec(mutante()), "--base", base)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn(texto, r.stderr)
                self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
