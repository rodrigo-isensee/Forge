"""R-TETO: duas suítes do Forge não rodam ao mesmo tempo; o pre-push espera a vez por uma trava (flock).

Cada teste roda o hook de verdade, dentro de um repositório descartável com uma suíte mínima, para não
disparar a suíte do Forge de dentro dela. A trava vive em XDG_RUNTIME_DIR apontada para uma pasta temporária.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})

SUITE_RAPIDA = '''import unittest, pathlib
class T(unittest.TestCase):
    def test_roda(self):
        pathlib.Path("rodou").write_text("sim")
'''
SUITE_LENTA = '''import unittest, pathlib, time
class T(unittest.TestCase):
    def test_espera_liberar(self):
        pathlib.Path("iniciou").write_text("sim")
        for _ in range(300):
            if pathlib.Path("liberar").exists():
                return
            time.sleep(0.1)
        self.fail("ninguem liberou")
'''
SUITE_FALHA = '''import unittest
class T(unittest.TestCase):
    def test_falha(self):
        self.fail("de proposito")
'''
SEGURA_TRAVA = '''import fcntl, sys, time
f = open(sys.argv[1], "a")
fcntl.flock(f, fcntl.LOCK_EX)
print("pronto", flush=True)
time.sleep(600)
'''


class PrePushTrava(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        self.repo = base / "repo"
        (self.repo / "tests").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True, env=AMBIENTE)
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), FORGE_TRAVA_ESPERA="20")
        self.trava = self.run_dir / f"forge-suite-{os.getuid()}.lock"
        self.filhos = []
        self.addCleanup(self._mata_filhos)

    def _mata_filhos(self):
        for p in self.filhos:
            if p.poll() is None:
                p.kill()
            p.wait()
            for fluxo in (p.stdout, p.stderr):
                if fluxo:
                    fluxo.close()

    def suite(self, texto):
        (self.repo / "tests" / "test_x.py").write_text(texto)

    def hook(self, *args, **extra):
        env = dict(self.env, **extra)
        return subprocess.Popen(
            [str(HOOK), *args], cwd=self.repo, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def roda(self, *args, **extra):
        p = self.hook(*args, **extra)
        self.filhos.append(p)
        saida, erro = p.communicate(timeout=60)
        return p.returncode, saida, erro

    def espera_ate(self, condicao, limite=15):
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            if condicao():
                return True
            time.sleep(0.05)
        return False

    def segura_trava(self):
        """Um processo externo que segura a trava até ser morto; devolve o processo."""
        p = subprocess.Popen([sys.executable, "-I", "-c", SEGURA_TRAVA, str(self.trava)],
                             stdout=subprocess.PIPE, text=True)
        self.filhos.append(p)
        self.assertEqual(p.stdout.readline().strip(), "pronto")
        return p

    def test_suite_sem_concorrente_roda_e_devolve_o_codigo_da_suite(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, _ = self.roda()
        self.assertEqual(codigo, 0)
        self.assertTrue((self.repo / "rodou").exists())
        self.suite(SUITE_FALHA)
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("testes do Forge falharam", erro)

    def test_segunda_execucao_espera_a_vez(self):
        self.suite(SUITE_LENTA)
        primeira = self.hook()
        self.filhos.append(primeira)
        self.assertTrue(self.espera_ate((self.repo / "iniciou").exists), "a primeira suíte não começou")
        (self.repo / "iniciou").unlink()
        segunda = self.hook()
        self.filhos.append(segunda)
        # a segunda não pode ter começado a suíte enquanto a primeira segura a trava
        time.sleep(1.5)
        self.assertIsNone(segunda.poll(), "a segunda não esperou")
        self.assertFalse((self.repo / "iniciou").exists(), "a segunda rodou a suíte junto com a primeira")
        (self.repo / "liberar").write_text("")
        self.assertEqual(primeira.wait(timeout=60), 0)
        self.assertEqual(segunda.wait(timeout=60), 0)
        self.assertIn("esperando a vez", segunda.stderr.read())
        self.assertTrue((self.repo / "iniciou").exists(), "a segunda não rodou a suíte depois da vez")

    def test_status_acompanha_a_trava(self):
        self.suite(SUITE_LENTA)
        codigo, saida, _ = self.roda("--status")
        self.assertEqual((codigo, saida.strip()), (1, "nenhuma suíte do Forge rodando"))
        primeira = self.hook()
        self.filhos.append(primeira)
        self.assertTrue(self.espera_ate(lambda: self.roda("--status")[0] == 0), "o status não viu a suíte")
        _, saida, _ = self.roda("--status")
        self.assertIn("suíte do Forge rodando", saida)
        (self.repo / "liberar").write_text("")
        self.assertEqual(primeira.wait(timeout=60), 0)
        codigo, _, _ = self.roda("--status")
        self.assertEqual(codigo, 1)

    def test_trava_orfa_de_processo_morto_e_liberada(self):
        self.suite(SUITE_RAPIDA)
        dono = self.segura_trava()
        self.assertEqual(self.roda("--status")[0], 0)
        dono.send_signal(signal.SIGKILL)
        dono.wait()
        # o arquivo continua lá (com ou sem texto), mas ninguém o segura
        self.assertTrue(self.trava.exists())
        self.assertEqual(self.roda("--status")[0], 1)
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("esperando a vez", erro)
        self.assertTrue((self.repo / "rodou").exists())

    def test_limite_estourado_sai_com_erro_e_nao_roda_a_suite(self):
        self.suite(SUITE_RAPIDA)
        self.segura_trava()
        inicio = time.monotonic()
        codigo, _, erro = self.roda(FORGE_TRAVA_ESPERA="1")
        self.assertGreaterEqual(time.monotonic() - inicio, 0.9)
        self.assertEqual(codigo, 1)
        self.assertIn("esperando a vez", erro)
        self.assertIn("a vez não chegou", erro)
        self.assertFalse((self.repo / "rodou").exists(), "a suíte rodou sem ter a trava")

    def test_limite_invalido_e_recusado(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda(FORGE_TRAVA_ESPERA="logo")
        self.assertEqual(codigo, 1)
        self.assertIn("FORGE_TRAVA_ESPERA", erro)

    def test_trava_que_e_link_simbolico_e_recusada(self):
        self.suite(SUITE_RAPIDA)
        self.trava.symlink_to(self.run_dir / "alvo")
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("link simbólico", erro)
        self.assertFalse((self.run_dir / "alvo").exists())


if __name__ == "__main__":
    unittest.main()
