"""MODELOS-PARECER-AVISOS-2: texto cobrado por teste."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(*partes):
    return RAIZ.joinpath(*partes).read_text(encoding="utf-8")


class ModelosDeParecer(unittest.TestCase):
    MODELOS = ("templates/projeto/docs/reviews/_modelo.md", "templates/projeto/docs/qa/_modelo.md",
               "templates/projeto/docs/security/_modelo.md", "docs/security/_modelo.md")

    def test_teto_de_300_diz_que_o_prefixo_nao_conta(self):
        self.assertEqual(len(self.MODELOS), 4)
        for rel in self.MODELOS:
            self.assertIn("o prefixo `A<n> (...) <arquivo>:<linha>` não conta", ler(*rel.split("/")), rel)

    def test_modelo_de_seguranca_do_forge_avisa_da_neutralidade(self):
        self.assertIn("o parecer não cita nome de linguagem", ler("docs", "security", "_modelo.md"))
        self.assertNotIn("neutralidade", ler("templates", "projeto", "docs", "security", "_modelo.md"))


if __name__ == "__main__":
    unittest.main()
