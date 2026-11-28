"""v047 E2.318 (FILA-13 T-5): o fim do pedido com a retrospectiva gravada é marco da regra 9 de docs/economia-de-tokens.md,
com a medida por pedido e o critério de volta. Âncora da regra e o trecho do marco, não a frase (tests/apoio_regra_id.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import linha  # noqa: E402

ANCORA = "9. **Conversa principal curta**"


class FimDoPedidoEMarco(unittest.TestCase):
    def setUp(self):
        self.regra = linha("docs/economia-de-tokens.md", ANCORA)

    def test_fim_do_pedido_com_retrospectiva_e_marco(self):
        self.assertIn("fim do pedido com a retrospectiva gravada", self.regra)

    def test_medida_por_pedido(self):
        self.assertIn("forge-check transcricao custo --pedido", self.regra)

    def test_criterio_de_volta_do_marco(self):
        volta = self.regra.split("**Volta atrás:**", 1)[1]
        self.assertIn("fim do pedido", volta)


if __name__ == "__main__":
    unittest.main()
