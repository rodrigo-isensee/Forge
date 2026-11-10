"""ACHADO-TETO-DOC: o teto de 300 do achado. 0.44.2: o agente cita a regra do parecer; o teto é provado no forge-check
(tests/test_textos_034.py, ModelosDeParecer)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import ids, ler  # noqa: E402


class AchadoTetoDoc(unittest.TestCase):
    def test_security_engineer_cita_a_regra_do_parecer(self):
        self.assertLessEqual({"R-REVIEW", "R-SEGURANCA"}, ids(ler("agents/security-engineer.md")))


if __name__ == "__main__":
    unittest.main()
