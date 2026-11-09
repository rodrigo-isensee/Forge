"""D4 (F7): a revisão de UX só com interface, no Jarvis e em economia-de-tokens. 0.44.2: âncora e ID da regra (`R-REVIEW`),
não a frase (tests/apoio_regra_id.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import ids, linha  # noqa: E402


class F7UxSoComInterface(unittest.TestCase):
    def test_passo_de_ux_do_jarvis_cita_a_regra(self):
        self.assertIn("R-REVIEW", ids(linha("agents/jarvis.md", "7. **Revisão de UX**")))

    def test_economia_de_tokens_cita_a_mesma_regra(self):
        self.assertIn("R-REVIEW", ids(linha("docs/economia-de-tokens.md", "1. **Uma rodada por entrega.**")))


if __name__ == "__main__":
    unittest.main()
