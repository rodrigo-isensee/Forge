"""S4 (0.44.2): `forge-check meta --armar|--desarmar|--estado` grava o objetivo onde o hook de Stop (hooks/meta.py) o lê
(fixtures em tests/hooks/meta)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")


class Meta(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-meta-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(self.tmp)], check=True)
        (self.tmp / ".forge").mkdir()

    def rodar(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "meta", *args], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout

    def test_armar_grava_no_run_do_hook_e_desarmar_tira(self):
        rc, out = self.rodar("--armar", "p1", "--checagem", "python3 -m unittest tests.x", "--checagem", "true")
        self.assertEqual(rc, 0, out)
        meta = json.loads((self.tmp / ".forge" / "run" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["pedido"], meta["armado"], meta["checagens"]), ("p1", True, [["python3", "-m", "unittest", "tests.x"], ["true"]]))
        self.assertIn("armado=True", self.rodar("--estado")[1])
        self.assertEqual(self.rodar("--desarmar")[0], 0)
        self.assertEqual(self.rodar("--estado")[0], 1)

    def test_sem_checagem_ou_pedido_invalido_recusa(self):
        self.assertEqual(self.rodar("--armar", "p1")[0], 2)
        self.assertEqual(self.rodar("--armar", "../x", "--checagem", "true")[0], 2)
        self.assertEqual(self.rodar("--armar", "p1", "--checagem", "'aberta")[0], 2)
        self.assertFalse((self.tmp / ".forge" / "run" / "meta.json").exists())


if __name__ == "__main__":
    unittest.main()
