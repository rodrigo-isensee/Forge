"""ACHADO-TETO-DOC: texto cobrado por teste."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(*partes):
    return RAIZ.joinpath(*partes).read_text(encoding="utf-8")


class AchadoTetoDoc(unittest.TestCase):
    def test_security_engineer_diz_o_teto_de_300_do_achado(self):
        self.assertIn("até 300 caracteres sem contar o prefixo", ler("agents", "security-engineer.md"))


if __name__ == "__main__":
    unittest.main()
