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
        # (10 + 2 + 400) * 2 (antes) + (20 + 2 + 400) * 2 (depois)
        self.assertIn("1 casos válidos, 4 chamadas, custo estimado 1668 tokens", saida)
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


if __name__ == "__main__":
    unittest.main()
