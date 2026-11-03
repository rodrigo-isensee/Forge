"""L18 (M7): a `fila` mostra a ocupação da trava da suíte, só lendo (`.githooks/pre-push --status`); a leitura não toma a trava."""
import fcntl
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
KANBAN = "# Quadro\n\n## Pronto para fazer (WIP 5)\n\n## Pronto\n"

SEGURA_A_TRAVA = (
    "import fcntl, os, sys, time\n"
    "fd = os.open(sys.argv[1], os.O_RDWR)\n"
    "fcntl.flock(fd, fcntl.LOCK_EX)\n"
    "os.write(fd, ('pid %d\\n' % os.getpid()).encode())\n"
    "print('presa', flush=True)\n"
    "time.sleep(60)\n")


@unittest.skipUnless(shutil.which("flock"), "o pre-push usa o flock")
class OcupacaoDaTrava(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-ocupacao-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.raiz = self.tmp / "raiz"
        (self.raiz / ".githooks").mkdir(parents=True)
        shutil.copy(RAIZ / ".githooks" / "pre-push", self.raiz / ".githooks" / "pre-push")
        (self.raiz / "KANBAN.md").write_text(KANBAN, encoding="utf-8")
        self.home = self.tmp / "home"
        self.pasta = self.home / ".forge-contrib" / f"forge-{os.getuid()}"
        self.trava = self.pasta / f"forge-suite-{os.getuid()}.lock"
        self.pasta.mkdir(parents=True, mode=0o700)

    def fila(self):
        env = {k: v for k, v in os.environ.items() if k not in ("XDG_RUNTIME_DIR",)}
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.raiz), "fila"], capture_output=True, text=True, env=dict(env, HOME=str(self.home)))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout.splitlines()

    def segurar(self):
        self.trava.write_text("", encoding="utf-8")
        p = subprocess.Popen([sys.executable, "-c", SEGURA_A_TRAVA, str(self.trava)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.wait)
        self.addCleanup(p.terminate)
        self.assertEqual(p.stdout.readline().strip(), "presa")
        return p

    def test_trava_livre_fica_abaixo_do_limite_e_sem_aviso(self):
        linhas = self.fila()
        self.assertIn("fila: trava ocupacao=0.0 limite=0.6 (livre)", linhas)
        self.assertFalse([l for l in linhas if "acima de" in l], linhas)
        self.assertRegex(linhas[-1], r"^fila: \d+ podem começar")  # o resumo segue por último

    def test_trava_ocupada_sai_acima_do_limite_e_a_leitura_nao_a_toma_nem_a_apaga(self):
        p = self.segurar()
        linhas = self.fila()
        self.assertIn("fila: trava ocupacao=1.0 limite=0.6 (presa, 0 na fila)", linhas)
        self.assertTrue([l for l in linhas if "acima de 0.6" in l and "não despache" in l], linhas)
        self.assertIsNone(p.poll(), "a suíte presa continua presa")
        self.assertTrue(self.trava.is_file())
        with self.trava.open("rb") as f:  # a leitura não a tomou: quem a segura segue com ela
            with self.assertRaises(BlockingIOError):
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        p.terminate()
        p.wait()
        time.sleep(0.2)
        self.assertIn("fila: trava ocupacao=0.0 limite=0.6 (livre)", self.fila())

    def test_trava_como_link_recusa_sem_escrever_e_nao_vira_livre(self):
        alvo = self.tmp / "alvo.lock"
        alvo.write_text("intacto\n", encoding="utf-8")
        self.trava.symlink_to(alvo)
        linhas = self.fila()
        self.assertTrue([l for l in linhas if l.startswith("aviso: trava da suíte não verificável")], linhas)
        self.assertFalse([l for l in linhas if "ocupacao=0.0" in l], linhas)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "intacto\n")

    def test_sem_o_hook_a_fila_fica_como_estava(self):
        (self.raiz / ".githooks" / "pre-push").unlink()
        self.assertFalse([l for l in self.fila() if "trava" in l])


    def test_hook_alheio_sem_o_status_do_forge_nao_e_executado_nem_vira_trava_presa(self):  # L18, A2 do review
        marca = self.tmp / "executou"
        hook = self.raiz / ".githooks" / "pre-push"
        hook.write_text(f"#!/bin/sh\ntouch {marca}\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        linhas = self.fila()
        self.assertFalse(marca.exists(), "o hook de outro dono não roda")
        self.assertFalse([l for l in linhas if "presa" in l or "ocupacao=" in l], linhas)


if __name__ == "__main__":
    unittest.main()
