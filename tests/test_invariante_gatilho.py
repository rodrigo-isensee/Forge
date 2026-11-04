"""INVARIANTE-GATILHO: texto cobrado por teste."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(*partes):
    return RAIZ.joinpath(*partes).read_text(encoding="utf-8")


class InvarianteGatilho(unittest.TestCase):
    def test_modelo_de_pedido_nasce_com_a_etapa_de_seguranca_para_invariante_novo(self):
        texto = ler("templates", "projeto", "docs", "pedidos", "_modelo.md")
        linha = [l for l in texto.splitlines() if l.startswith("- E1.3 (security-engineer)")]
        self.assertEqual(len(linha), 1)
        self.assertIn("no Forge, inclusive quando prevê invariante novo ou alterado em `tests/config.json`", linha[0])


if __name__ == "__main__":
    unittest.main()
