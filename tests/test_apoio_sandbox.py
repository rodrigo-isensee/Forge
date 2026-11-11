"""ENVIO-DO-SANDBOX, correção A (pedido v0457, E11): `tests/apoio_sandbox.py` pula só com a capacidade faltando de
fato e fora do CI; com CI definido, a falta reprova (no CI nada pula; `teto_pulados` não sobe). Casos C1 a C13 de
docs/security/ameacas/v0457-envio-sandbox.md (A2, A3, A4)."""
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

    def test_root_com_chown_em_einval_falta(self):
        motivo, chown = self.sem_excecao(self.chown, 0, OSError(errno.EINVAL, os.strerror(errno.EINVAL)))
        self.assertIn("EINVAL", motivo)
        self.assertIn(str(Path(chown.call_args.args[0]).parent), motivo)  # o motivo cita onde a sonda rodou
        self.assertEqual(chown.call_args.args[1:], (65534, 65534))

    def test_root_com_chown_que_funciona_nao_falta(self):
        self.assertIsNone(self.chown(0, None)[0])

    def test_quem_nao_e_root_nem_tenta_o_chown(self):
        motivo, chown = self.chown(1000, OSError(errno.EINVAL, "x"))
        self.assertIsNone(motivo)
        chown.assert_not_called()

    def test_outro_erro_do_chown_sobe_em_vez_de_virar_pulo(self):
        """A3/C7: só EINVAL é a falta do sandbox; EPERM (root sem CAP_CHOWN, outro caso), EACCES, ENOENT e EIO sobem."""
        for numero in (errno.EPERM, errno.EACCES, errno.ENOENT, errno.EIO):
            with self.subTest(errno.errorcode[numero]):
                with self.assertRaises(OSError) as erro:
                    self.chown(0, OSError(numero, os.strerror(numero)))
                self.assertEqual(erro.exception.errno, numero)

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


def ambiente_sem_ci(**extra):
    """`os.environ` sem os sinais de CI, mais `extra`, enquanto o contexto durar."""
    limpo = {k: v for k, v in os.environ.items() if k not in apoio_sandbox.SINAIS_DE_CI}
    return mock.patch.dict(os.environ, {**limpo, **extra}, clear=True)


class Exigir(unittest.TestCase):
    def setUp(self):
        apoio_sandbox.falta.cache_clear()
        self.addCleanup(apoio_sandbox.falta.cache_clear)
        for remendo in (mock.patch.dict(apoio_sandbox.SONDAS, {"x": lambda: MOTIVO, "ok": lambda: None}),
                        mock.patch.object(apoio_sandbox, "PODEM_PULAR", frozenset({"x.Y.test_z"})),
                        mock.patch.object(apoio_sandbox, "CI_NA_CARGA", frozenset())):
            remendo.start()
            self.addCleanup(remendo.stop)
        self.alvo = mock.Mock(spec=unittest.TestCase)
        self.alvo.id.return_value = "tests.x.Y.test_z"  # o prefixo `tests.` do modo `tests.<módulo>` não conta
        self.alvo.fail.side_effect = AssertionError
        self.alvo.skipTest.side_effect = unittest.SkipTest

    def exigir(self, capacidade, ambiente):
        erro = io.StringIO()
        antes = apoio_sandbox.pulados
        with redirect_stderr(erro), ambiente_sem_ci(**ambiente):
            try:
                apoio_sandbox.exigir(self.alvo, capacidade)
                resultado = "segue"
            except unittest.SkipTest:
                resultado = "pula"
            except AssertionError:
                resultado = "reprova"
        return resultado, apoio_sandbox.pulados - antes, erro.getvalue()

    def test_com_ci_definido_a_falta_reprova_e_nao_pula(self):
        """A2/C1 a C3: `CI` ou `GITHUB_ACTIONS` com qualquer valor não vazio é CI (`false` e `0` também)."""
        for ambiente in ({"CI": "true"}, {"GITHUB_ACTIONS": "true"}, {"CI": "false"}, {"CI": "0"}):
            with self.subTest(ambiente):
                resultado, contados, erro = self.exigir("x", ambiente)
                self.assertEqual((resultado, contados, erro), ("reprova", 0, ""))
                self.alvo.skipTest.assert_not_called()
                self.assertIn(MOTIVO, self.alvo.fail.call_args.args[0])

    def test_ci_da_carga_vale_mesmo_tirado_do_ambiente_depois(self):
        """A2: um teste que tira `CI` ou `GITHUB_ACTIONS` do `os.environ` (test_catraca.py) não faz o CI pular."""
        with mock.patch.object(apoio_sandbox, "CI_NA_CARGA", frozenset({"GITHUB_ACTIONS"})):
            self.assertEqual(self.exigir("x", {})[:2], ("reprova", 0))

    def test_teste_fora_da_lista_reprova_com_ou_sem_a_capacidade(self):
        """A4: a lista fechada vale em todo ambiente, antes da sonda."""
        self.alvo.id.return_value = "tests.x.Y.test_outro"
        for capacidade in ("ok", "x"):
            with self.subTest(capacidade):
                self.assertEqual(self.exigir(capacidade, {})[:2], ("reprova", 0))
                self.assertIn("PODEM_PULAR", self.alvo.fail.call_args.args[0])

    def test_chown_real_em_einval_reprova_com_ci_e_pula_sem(self):
        """C1 e C4 com a sonda de verdade (só o `os.chown` simulado)."""
        einval = OSError(errno.EINVAL, os.strerror(errno.EINVAL))
        with mock.patch.object(apoio_sandbox.os, "geteuid", return_value=0), \
                mock.patch.object(apoio_sandbox.os, "chown", side_effect=einval):
            self.assertEqual(self.exigir("chown", {"CI": "true"})[:2], ("reprova", 0))
            self.assertEqual(self.exigir("chown", {})[:2], ("pula", 1))
        self.assertIn("EINVAL", self.alvo.skipTest.call_args.args[0])

    def test_a_sonda_roda_antes_do_passo_e_nao_engole_o_erro_dele(self):
        """A3/C13: com a capacidade presente, o EINVAL do passo sob teste é erro do teste, não pulo."""
        ordem = []

        class Brinquedo(unittest.TestCase):
            def test_passo(self):
                apoio_sandbox.exigir(self, "sonda")
                ordem.append("passo")
                raise OSError(errno.EINVAL, "regressão do produto")

        caso = Brinquedo("test_passo")
        lista = frozenset({caso.id().removeprefix("tests.")})
        with mock.patch.dict(apoio_sandbox.SONDAS, {"sonda": lambda: ordem.append("sonda")}), \
                mock.patch.object(apoio_sandbox, "PODEM_PULAR", lista), ambiente_sem_ci():
            r = unittest.TestResult()
            caso.run(r)
        self.assertEqual((ordem, len(r.errors), len(r.failures), len(r.skipped)), (["sonda", "passo"], 1, 0, 0))

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
import os, sys, unittest
sys.path.insert(0, sys.argv[1])
import apoio_sandbox
apoio_sandbox.SONDAS["proc"] = lambda: "proc de mentira"
apoio_sandbox.PODEM_PULAR = frozenset({"__main__.T.test_precisa_do_proc"})
class T(unittest.TestCase):
    def test_precisa_do_proc(self):
        for nome in sys.argv[2:]:  # o teste tira o sinal do ambiente depois da carga
            os.environ.pop(nome)
        apoio_sandbox.exigir(self, "proc")
r = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
print(f"falhas={len(r.failures)} pulados={len(r.skipped)}")
"""


class NoProcessoReal(unittest.TestCase):
    """O `CI` lido é o do ambiente do processo (o padrão de `exigir`), num Python isolado e de ambiente limpo."""
    def rodar(self, *tirar, **extra):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", **extra}
        return subprocess.run([sys.executable, "-I", "-c", SCRIPT, str(AQUI), *tirar], env=env, capture_output=True,
                              text=True, timeout=60)

    def test_com_ci_definido_no_ambiente_reprova_sem_pular(self):
        for tirar, extra in (((), {"CI": "true"}), ((), {"GITHUB_ACTIONS": "true"}), (("CI",), {"CI": "true"})):
            with self.subTest(tirar=tirar, **extra):
                r = self.rodar(*tirar, **extra)
                self.assertIn("falhas=1 pulados=0", r.stdout, r.stderr)
                self.assertNotIn("sandbox: pulado", r.stderr)

    def test_sem_ci_no_ambiente_pula_e_conta(self):
        r = self.rodar()
        self.assertIn("falhas=0 pulados=1", r.stdout, r.stderr)
        self.assertIn("sandbox: pulado 1 · __main__.T.test_precisa_do_proc · proc: proc de mentira", r.stderr)


BRINQUEDO = """
from apoio_sandbox import exigir
from apoio_sandbox import exigir as pular  # acusa
import apoio_sandbox
class Listado(unittest.TestCase):
    def test_listado(self):
        if True:
            exigir(self, "proc")
    def test_fora(self):
        exigir(self, "proc")  # acusa
    def setUp(self):
        exigir(self, "proc")  # acusa
    @classmethod
    def setUpClass(cls):
        exigir(cls, "proc")  # acusa
    def test_no_try(self):
        try:
            exigir(self, "proc")  # acusa
        except Exception:
            pass
    def test_por_texto(self):
        getattr(apoio_sandbox, "exigir")(self, "proc")  # acusa
    def test_guardado(self):
        x = exigir  # acusa
    def test_outro_alvo(self):
        exigir(outro, "proc")  # acusa
    def test_valor(self):
        ok = exigir(self, "proc")  # acusa
def fabrica():
    class Aninhada(unittest.TestCase):
        def test_aninhado(self):
            exigir(self, "proc")  # acusa
@exigir  # acusa
class Decorada(unittest.TestCase):
    pass
class Mixin:
    def ajuda(self):
        exigir(self, "proc")  # acusa
def solta(self):
    apoio_sandbox.exigir(self, "proc")  # acusa
"""
LISTADOS = {f"brinquedo.Listado.{m}" for m in ("test_listado", "test_no_try", "test_por_texto", "test_guardado",
                                                "test_outro_alvo", "test_valor")} | {"brinquedo.Aninhada.test_aninhado"}


class ListaFechada(unittest.TestCase):
    """A4: só os testes de PODEM_PULAR chamam exigir; a lista não tem ID órfão (C10, C11)."""

    def test_brinquedo_acusa_cada_uso_fora_da_lista(self):
        queixas = apoio_sandbox.usos_fora_da_lista(BRINQUEDO, "brinquedo", LISTADOS)
        acusar = [n for n, linha in enumerate(BRINQUEDO.splitlines(), 1) if linha.endswith("# acusa")]
        self.assertGreaterEqual(len(acusar), 13)
        self.assertEqual(sorted(linha for linha, _ in queixas), acusar, queixas)

    def test_auxiliar_vale_so_com_todos_os_testes_que_o_chamam_na_lista(self):
        fonte = ("class C(unittest.TestCase):\n    def ajuda(self):\n        exigir(self, 'proc')\n"
                 "    def test_a(self):\n        self.ajuda()\n    def test_b(self):\n        self.ajuda()\n"
                 "    def test_c(self):\n        pass\n    def outra(self):\n        self.ajuda()\n")
        self.assertEqual(apoio_sandbox.usos_fora_da_lista(fonte, "m", {"m.C.test_a", "m.C.test_b"}), [])
        self.assertEqual([linha for linha, _ in apoio_sandbox.usos_fora_da_lista(fonte, "m", {"m.C.test_a"})], [3])

    def test_orfao_acusado(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "m.py").write_text(
                "class Base(unittest.TestCase):\n    def ajuda(self):\n        exigir(self, 'proc')\n"
                "class C(Base):\n    def test_a(self):\n        self.ajuda()\n    def test_b(self):\n        pass\n"
                "    def test_c(self):\n        self.outra()\n    def outra(self):\n        print()\n")
            lista = {"m.C.test_a", "m.C.test_b", "m.C.test_c", "m.C.test_sumiu", "m.X.test_a", "sumiu.C.test_a"}
            self.assertEqual(apoio_sandbox.orfaos(lista, Path(tmp)),
                             ["m.C.test_b", "m.C.test_c", "m.C.test_sumiu", "m.X.test_a", "sumiu.C.test_a"])

    def test_a_arvore_so_chama_exigir_nos_testes_da_lista(self):
        arquivos = [f for f in sorted(AQUI.rglob("*.py")) if f.name not in ("apoio_sandbox.py", Path(__file__).name)]
        self.assertGreater(len(arquivos), 50)  # a varredura achou a pasta de testes
        lista = apoio_sandbox.PODEM_PULAR
        queixas = [(f.relative_to(AQUI), linha, q) for f in arquivos
                   for linha, q in apoio_sandbox.usos_fora_da_lista(f.read_text(encoding="utf-8"), f.stem, lista)]
        self.assertEqual(queixas, [])

    def test_a_lista_tem_os_18_testes_e_nenhum_orfao(self):
        self.assertEqual(len(apoio_sandbox.PODEM_PULAR), 18)
        self.assertEqual(apoio_sandbox.orfaos(apoio_sandbox.PODEM_PULAR, AQUI), [])


if __name__ == "__main__":
    unittest.main()
