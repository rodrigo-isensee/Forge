"""Bancada de instrução (S7, 0.45.3): validação dos casos, estimativa e a rodada com um executor falso; nunca chama o modelo."""
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("bancada", RAIZ / "tests" / "bancada" / "bancada.py")
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)


def falso(saida, rc=0, chamadas=None):
    def executar(cmd, **_kw):
        if chamadas is not None:
            chamadas.append(cmd)
        return subprocess.CompletedProcess(cmd, rc, stdout=saida, stderr="")
    return executar


class ParecidoComObjeto:
    """Tem `get` e itera como um dict, mas não é dict: a validação recusa pelo tipo, não por quebrar."""

    def __iter__(self):
        return iter(["id", "entrada"])

    def get(self, _campo, padrao=None):
        return "x"


def proibido(*_a, **_kw):
    raise AssertionError("a bancada chamou o modelo sem --executar")


class Bancada(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        self.antes, self.depois, self.casos = d / "antes.md", d / "depois.md", d / "casos.json"
        self.antes.write_text("a" * 40, encoding="utf-8")
        self.depois.write_text("d" * 80, encoding="utf-8")
        self.casos.write_text(json.dumps([{"id": "c1", "entrada": "x" * 8, "espera": "Recomendo"}]), encoding="utf-8")

    def rodar(self, *extra, executar=proibido):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = b.principal(["--antes", str(self.antes), "--depois", str(self.depois), "--casos", str(self.casos), *extra],
                             executar)
        return rc, out.getvalue()

    def test_casos_gravados_do_repositorio_sao_validos(self):
        self.assertEqual(b.validar_casos(json.loads(b.CASOS.read_text(encoding="utf-8"))), [])

    def test_validacao_recusa_forma_errada(self):
        self.assertTrue(b.validar_casos([]))
        self.assertTrue(b.validar_casos([{"id": "a"}]))
        self.assertTrue(b.validar_casos([{"id": "a", "entrada": "x", "extra": 1}]))
        self.assertTrue(b.validar_casos([{"id": "a", "entrada": "x"}, {"id": "a", "entrada": "y"}]))
        self.assertTrue(b.validar_casos([{"id": "a", "entrada": "x", "espera": 3}]))
        self.assertTrue(b.validar_casos([{"id": "a", "entrada": "   "}]))
        self.assertEqual(b.validar_casos([ParecidoComObjeto()]), ["caso 1: não é objeto"])

    def test_sem_executar_so_estima_e_nao_chama_o_modelo(self):
        rc, saida = self.rodar("--rodadas", "2")
        self.assertEqual(rc, 0)
        # a instrução estimada leva a nota fixa SEM_FERRAMENTAS (0.45.4): (40 + 2 + len(nota)) caracteres
        nota = len(b.SEM_FERRAMENTAS) + 2
        esperado = 2 * (-(-(40 + nota) // 4) + 2 + 400) + 2 * (-(-(80 + nota) // 4) + 2 + 400)
        self.assertIn(f"1 casos válidos, 4 chamadas, custo estimado {esperado} tokens", saida)
        self.assertIn("simulação", saida)

    def test_caso_invalido_da_rc_1_sem_chamar(self):
        self.casos.write_text("[{}]", encoding="utf-8")
        self.assertEqual(self.rodar()[0], 1)

    def test_id_repetido_da_rc_1_sem_chamar(self):
        self.casos.write_text(json.dumps([{"id": "a", "entrada": "x"}, {"id": "a", "entrada": "y"}]), encoding="utf-8")
        self.assertEqual(self.rodar()[0], 1)

    def test_executar_mede_tokens_tempo_e_espera(self):
        chamadas = []
        resposta = json.dumps({"result": "Recomendo A", "usage": {"input_tokens": 10, "output_tokens": 5,
                                                                  "cache_read_input_tokens": 3,
                                                                  "web_search_requests": 7, "outros_tokens": 2.5}})
        rc, saida = self.rodar("--executar", executar=falso(resposta, chamadas=chamadas))
        self.assertEqual(rc, 0)
        self.assertIn("antes c1 rodada=1 tokens=18", saida)
        self.assertIn("ok=True", saida)
        self.assertIn("media depois: tokens=18", saida)
        self.assertEqual(len(chamadas), 2)
        self.assertEqual(chamadas[0][:2], ["claude", "-p"])
        self.assertIn("--tools", chamadas[0])

    def test_chamada_que_falha_da_rc_1(self):
        self.assertEqual(self.rodar("--executar", executar=falso("", rc=1))[0], 1)
        self.assertEqual(self.rodar("--executar", executar=falso(json.dumps({"is_error": True})))[0], 1)
        valida = json.dumps({"result": "Recomendo", "usage": {"input_tokens": 1}})
        self.assertEqual(self.rodar("--executar", executar=falso(valida, rc=1))[0], 1)

    def test_rodadas_fora_do_limite_e_erro_de_uso(self):
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stderr(io.StringIO()):
            self.rodar("--rodadas", "0")
        self.assertEqual(e.exception.code, 2)
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stderr(io.StringIO()):
            self.rodar("--rodadas", str(b.RODADAS_MAX + 1))
        self.assertEqual(e.exception.code, 2)

    def test_script_direto_roda_a_simulacao(self):
        # sem --executar: só valida e estima, nunca chama o modelo
        r = subprocess.run([sys.executable, str(RAIZ / "tests" / "bancada" / "bancada.py"), "--antes", str(self.antes),
                            "--depois", str(self.depois), "--casos", str(self.casos)],
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0)
        self.assertIn("simulação", r.stdout)


def respostas(*textos, chamadas=None):
    """Executor falso que devolve os textos em ordem (um por chamada), com 10 tokens cada."""
    fila = list(textos)

    def executar(cmd, **_kw):
        if chamadas is not None:
            chamadas.append(cmd)
        saida = json.dumps({"result": fila.pop(0), "usage": {"input_tokens": 10}})
        return subprocess.CompletedProcess(cmd, 0, stdout=saida, stderr="")
    return executar


class BancadaGravaEValida(unittest.TestCase):
    """0.45.4: `--saida` grava as respostas; a nota fixa sem ferramentas e o `--contexto`; a rodada `invalida` (chamada de
    ferramenta falsa) sai das médias; `espera` com alternativas, sem maiúsculas nem acentos. Nunca chama o modelo."""

    rodar = Bancada.rodar

    def setUp(self):
        Bancada.setUp(self)
        self.casos.write_text(json.dumps([{"id": "c1", "entrada": "x" * 8, "espera": "recomend"}]), encoding="utf-8")

    def test_saida_grava_entrada_resposta_tokens_segundos_e_ok_por_versao_caso_e_rodada(self):
        arq = Path(self.tmp.name) / "respostas.json"
        rc, saida = self.rodar("--executar", "--rodadas", "2", "--saida", str(arq),
                               executar=respostas("Minha recomendação é A", "sem nada", "Recomendo B", "RECOMENDO C"))
        self.assertEqual(rc, 0)
        self.assertIn(f"respostas gravadas em {arq}", saida)
        dados = json.loads(arq.read_text(encoding="utf-8"))
        self.assertEqual(dados["sem_ferramentas"], b.SEM_FERRAMENTAS)
        self.assertEqual([(r["versao"], r["caso"], r["rodada"], r["resposta"], r["ok"]) for r in dados["rodadas"]],
                         [("antes", "c1", 1, "Minha recomendação é A", True), ("antes", "c1", 2, "sem nada", False),
                          ("depois", "c1", 1, "Recomendo B", True), ("depois", "c1", 2, "RECOMENDO C", True)])
        primeira = dados["rodadas"][0]
        self.assertEqual((primeira["entrada"], primeira["tokens"], primeira["invalida"], primeira["falhou"]),
                         ("x" * 8, 10, False, False))
        self.assertIsInstance(primeira["segundos"], float)
        self.assertIn("media antes: tokens=10", saida)
        self.assertIn("ok=1/2", saida)
        self.assertEqual(dados["resumo"]["antes"], {"rodadas": 2, "invalidas": 0, "ok": 1, "com_espera": 2, "tokens": 10,
                                                    "segundos": dados["resumo"]["antes"].get("segundos")})

    def test_saida_registra_a_chamada_que_falhou_e_da_rc_1(self):
        arq = Path(self.tmp.name) / "respostas.json"
        rc, _ = self.rodar("--executar", "--saida", str(arq), executar=falso("", rc=1))
        self.assertEqual(rc, 1)
        dados = json.loads(arq.read_text(encoding="utf-8"))
        self.assertEqual([(r["versao"], r["falhou"], "resposta" in r) for r in dados["rodadas"]],
                         [("antes", True, False), ("depois", True, False)])
        self.assertEqual(dados["resumo"]["antes"], {"rodadas": 0, "invalidas": 0, "ok": 0, "com_espera": 0})

    def test_saida_que_nao_grava_da_rc_1(self):
        arq = Path(self.tmp.name) / "nao-existe" / "respostas.json"
        rc, saida = self.rodar("--executar", "--saida", str(arq), executar=respostas("Recomendo", "Recomendo"))
        self.assertEqual(rc, 1)
        self.assertNotIn("respostas gravadas", saida)

    def test_saida_nao_gravavel_recusa_antes_da_primeira_chamada(self):
        chamadas = []
        arq = Path(self.tmp.name) / "nao-existe" / "respostas.json"
        rc, saida = self.rodar("--executar", "--saida", str(arq), executar=falso("Recomendo", chamadas=chamadas))
        self.assertEqual(rc, 1)
        self.assertEqual(chamadas, [])
        self.assertNotIn("antes c1", saida)

    def test_saida_gravavel_nao_deixa_arquivo_antes_da_rodada(self):
        arq = Path(self.tmp.name) / "r.json"
        self.assertIsNone(b.saida_gravavel(arq))
        self.assertFalse(arq.exists())

    def test_saida_sem_executar_e_erro_de_uso(self):
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stderr(io.StringIO()):
            self.rodar("--saida", str(Path(self.tmp.name) / "r.json"))
        self.assertEqual(e.exception.code, 2)
        self.assertFalse((Path(self.tmp.name) / "r.json").exists())

    def test_nota_sem_ferramentas_igual_nas_duas_versoes_e_contexto_opcional(self):
        chamadas = []
        self.rodar("--executar", executar=respostas("Recomendo", "Recomendo", chamadas=chamadas))
        instrucoes = [c[c.index("--append-system-prompt") + 1] for c in chamadas]
        self.assertEqual(instrucoes, ["a" * 40 + "\n\n" + b.SEM_FERRAMENTAS, "d" * 80 + "\n\n" + b.SEM_FERRAMENTAS])
        contexto = Path(self.tmp.name) / "contexto.md"
        contexto.write_text("  Projeto de teste.\n", encoding="utf-8")
        chamadas.clear()
        self.rodar("--executar", "--contexto", str(contexto), executar=respostas("Recomendo", "Recomendo", chamadas=chamadas))
        for c in chamadas:
            self.assertTrue(c[c.index("--append-system-prompt") + 1].endswith(
                b.SEM_FERRAMENTAS + "\n\nContexto do projeto:\nProjeto de teste."))

    def test_contexto_longo_da_rc_1_sem_chamar(self):
        contexto = Path(self.tmp.name) / "contexto.md"
        contexto.write_text("c" * (b.CONTEXTO_MAX + 1), encoding="utf-8")
        self.assertEqual(self.rodar("--executar", "--contexto", str(contexto))[0], 1)
        contexto.write_text("c" * b.CONTEXTO_MAX, encoding="utf-8")
        self.assertEqual(self.rodar("--contexto", str(contexto))[0], 0)

    def test_chamada_de_ferramenta_falsa_e_invalida_e_sai_das_medias(self):
        falsas = ['<invoke name="Bash"><parameter name="command">ls</parameter></invoke>',
                  'Vou ver: {"name": "Bash", "input": {"command": "ls"}}', '{"name":"Bash"}']
        for falsa in falsas:
            with self.subTest(falsa=falsa):
                self.assertTrue(b.FERRAMENTA_FALSA.search(falsa))
        self.assertFalse(b.FERRAMENTA_FALSA.search("Recomendo rodar o Bash e invocar a suíte."))
        arq = Path(self.tmp.name) / "respostas.json"
        rc, saida = self.rodar("--executar", "--rodadas", "2", "--saida", str(arq),
                               executar=respostas(falsas[0], "Recomendo", falsas[1], falsas[2]))
        self.assertEqual(rc, 0)
        self.assertIn("media antes: tokens=10 segundos=", saida)
        self.assertIn("rodadas=1 invalidas=1 ok=1/1", saida)
        self.assertIn("media depois: rodadas=0 invalidas=2 ok=0/0", saida)
        self.assertIn("antes c1 rodada=1 tokens=10", saida)
        self.assertIn("invalida (chamada de ferramenta falsa)", saida.splitlines()[1])
        self.assertNotIn("invalida", saida.splitlines()[2])
        dados = json.loads(arq.read_text(encoding="utf-8"))
        self.assertEqual([r["invalida"] for r in dados["rodadas"]], [True, False, True, True])
        self.assertEqual(dados["resumo"]["depois"], {"rodadas": 0, "invalidas": 2, "ok": 0, "com_espera": 0})

    def test_espera_com_alternativas_sem_maiusculas_nem_acentos(self):
        self.assertTrue(b.atende("recomend", "Minha recomendação é esperar"))
        self.assertTrue(b.atende("Recomendação", "minha RECOMENDACAO"))
        self.assertTrue(b.atende("sugiro|recomend", "Recomendo A"))
        self.assertTrue(b.atende("sugiro | recomend", "eu sugiro"))
        self.assertFalse(b.atende("sugiro|recomend", "Faça A"))
        self.assertEqual(b.validar_casos([{"id": "a", "entrada": "x", "espera": "a|b"}]), [])
        for ruim in ("a||b", "|", " | a", ""):
            with self.subTest(espera=ruim):
                self.assertTrue(b.validar_casos([{"id": "a", "entrada": "x", "espera": ruim}]))


if __name__ == "__main__":
    unittest.main()
