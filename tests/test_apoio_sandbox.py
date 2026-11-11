"""ENVIO-DO-SANDBOX, correção A (pedido v0457, E11): `tests/apoio_sandbox.py` pula só com a capacidade faltando de
fato e fora do CI; com CI definido, a falta reprova (no CI nada pula; `teto_pulados` não sobe)."""
import errno
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))  # tests/ no caminho também no modo `tests.<módulo>`
import apoio_sandbox  # noqa: E402

MOTIVO = "falta de mentira para o teste"


class Sondas(unittest.TestCase):
    def sem_excecao(self, chamada, *args):
        """Exceção vira falha (não erro): o mutante que troca o pulo por exceção morre por asserção."""
        try:
            return chamada(*args)
        except Exception as erro:  # noqa: BLE001 - a falha diz qual exceção escapou
            self.fail(f"{type(erro).__name__} escapou: {erro}")

    def chown(self, euid, efeito):
        with mock.patch.object(apoio_sandbox.os, "geteuid", return_value=euid), \
                mock.patch.object(apoio_sandbox.os, "chown", side_effect=efeito) as chown:
            return apoio_sandbox.falta_chown(), chown

    def test_root_com_chown_em_einval_ou_eperm_falta(self):
        for numero in (errno.EINVAL, errno.EPERM):
            with self.subTest(errno.errorcode[numero]):
                motivo, chown = self.sem_excecao(self.chown, 0, OSError(numero, os.strerror(numero)))
                self.assertIn(errno.errorcode[numero], motivo)
                self.assertEqual(chown.call_args.args[1:], (65534, 65534))

    def test_root_com_chown_que_funciona_nao_falta(self):
        self.assertIsNone(self.chown(0, None)[0])

    def test_quem_nao_e_root_nem_tenta_o_chown(self):
        motivo, chown = self.chown(1000, OSError(errno.EINVAL, "x"))
        self.assertIsNone(motivo)
        chown.assert_not_called()

    def test_outro_erro_do_chown_sobe_em_vez_de_virar_pulo(self):
        with self.assertRaises(OSError) as erro:
            self.chown(0, OSError(errno.EIO, "disco"))
        self.assertEqual(erro.exception.errno, errno.EIO)

    def test_proc_do_proprio_namespace_nao_falta_e_o_de_outro_falta(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = Path(tmp)
            (proc / "self").symlink_to("123")
            self.assertIsNone(apoio_sandbox.falta_proc(proc, 123))
            self.assertIn("outro namespace de pid", str(apoio_sandbox.falta_proc(proc, 124)))

    def test_proc_sem_self_ou_com_self_que_nao_e_link_falta(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = Path(tmp)
            self.assertIn("sem ", str(self.sem_excecao(apoio_sandbox.falta_proc, proc, 1)))
            (proc / "self").write_text("1")  # readlink num arquivo comum: EINVAL, não FileNotFoundError
            self.assertIn("sem ", str(self.sem_excecao(apoio_sandbox.falta_proc, proc, 1)))


class Exigir(unittest.TestCase):
    def setUp(self):
        apoio_sandbox.falta.cache_clear()
        self.addCleanup(apoio_sandbox.falta.cache_clear)
        self.sondas = mock.patch.dict(apoio_sandbox.SONDAS, {"x": lambda: MOTIVO, "ok": lambda: None})
        self.sondas.start()
        self.addCleanup(self.sondas.stop)
        self.alvo = mock.Mock(spec=unittest.TestCase)
        self.alvo.id.return_value = "tests.x.Y.test_z"
        self.alvo.fail.side_effect = AssertionError
        self.alvo.skipTest.side_effect = unittest.SkipTest

    def exigir(self, capacidade, ambiente):
        erro = io.StringIO()
        antes = apoio_sandbox.pulados
        with redirect_stderr(erro):
            try:
                apoio_sandbox.exigir(self.alvo, capacidade, ambiente)
                resultado = "segue"
            except unittest.SkipTest:
                resultado = "pula"
            except AssertionError:
                resultado = "reprova"
        return resultado, apoio_sandbox.pulados - antes, erro.getvalue()

    def test_com_ci_definido_a_falta_reprova_e_nao_pula(self):
        resultado, contados, erro = self.exigir("x", {"CI": "true"})
        self.assertEqual((resultado, contados, erro), ("reprova", 0, ""))
        self.alvo.skipTest.assert_not_called()
        self.assertIn(MOTIVO, self.alvo.fail.call_args.args[0])

    def test_fora_do_ci_a_falta_pula_com_motivo_e_contagem(self):
        for ambiente in ({}, {"CI": ""}):
            with self.subTest(ambiente):
                n = apoio_sandbox.pulados + 1
                resultado, contados, erro = self.exigir("x", ambiente)
                self.assertEqual((resultado, contados), ("pula", 1))
                self.assertEqual(erro, f"sandbox: pulado {n} · tests.x.Y.test_z · x: {MOTIVO}\n")
                self.assertIn(MOTIVO, self.alvo.skipTest.call_args.args[0])

    def test_com_a_capacidade_segue_com_ou_sem_ci(self):
        for ambiente in ({}, {"CI": "true"}):
            with self.subTest(ambiente):
                self.assertEqual(self.exigir("ok", ambiente), ("segue", 0, ""))

    def test_capacidade_desconhecida_recusa(self):
        try:
            apoio_sandbox.falta("chwon")
        except Exception as erro:  # noqa: BLE001 - o tipo é o que se confere
            self.assertIsInstance(erro, ValueError)
        else:
            self.fail("capacidade desconhecida passou")

    def test_sonda_roda_uma_vez_por_processo(self):
        sonda = mock.Mock(return_value=None)
        with mock.patch.dict(apoio_sandbox.SONDAS, {"y": sonda}):
            apoio_sandbox.falta("y")
            apoio_sandbox.falta("y")
        sonda.assert_called_once_with()


SCRIPT = """
import sys, unittest
sys.path.insert(0, sys.argv[1])
import apoio_sandbox
apoio_sandbox.SONDAS["proc"] = lambda: "proc de mentira"
class T(unittest.TestCase):
    def test_precisa_do_proc(self):
        apoio_sandbox.exigir(self, "proc")
r = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
print(f"falhas={len(r.failures)} pulados={len(r.skipped)}")
"""


class NoProcessoReal(unittest.TestCase):
    """O `CI` lido é o do ambiente do processo (o padrão de `exigir`), num Python isolado e de ambiente limpo."""
    def rodar(self, **extra):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", **extra}
        return subprocess.run([sys.executable, "-I", "-c", SCRIPT, str(AQUI)], env=env, capture_output=True,
                              text=True, timeout=60)

    def test_com_ci_definido_no_ambiente_reprova_sem_pular(self):
        r = self.rodar(CI="true")
        self.assertIn("falhas=1 pulados=0", r.stdout, r.stderr)
        self.assertNotIn("sandbox: pulado", r.stderr)

    def test_sem_ci_no_ambiente_pula_e_conta(self):
        r = self.rodar()
        self.assertIn("falhas=0 pulados=1", r.stdout, r.stderr)
        self.assertIn("sandbox: pulado 1 · __main__.T.test_precisa_do_proc · proc: proc de mentira", r.stderr)


if __name__ == "__main__":
    unittest.main()
