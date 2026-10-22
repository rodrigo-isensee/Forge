"""D4 (F7): texto de revisão de UX no Jarvis e em economia-de-tokens. Texto curto e estável, não invariante."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class F7UxSoComInterface(unittest.TestCase):
    """F7 (variante B): diff sem interface não tem revisão de UX."""

    def test_passo_de_ux_do_jarvis_tem_a_condicao(self):
        passo = next(l for l in ler("agents/jarvis.md").splitlines() if l.startswith("7. **Revisão de UX**"))
        self.assertIn("só quando a entrega muda interface", passo)
        self.assertIn("diff sem interface não tem revisão de UX", passo)

    def test_economia_de_tokens_tem_a_mesma_condicao(self):
        regra = next(l for l in ler("docs/economia-de-tokens.md").splitlines() if l.startswith("1. **Uma rodada por entrega.**"))
        self.assertIn("só quando a entrega muda interface", regra)
        self.assertIn("diff sem interface não tem revisão de UX", regra)


if __name__ == "__main__":
    unittest.main()
