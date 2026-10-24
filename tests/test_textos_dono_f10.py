"""D4 (F10): pedido, lista ou decisão do dono em R-DECISAO e no Jarvis, e a checagem do vigia. Texto curto e estável, não invariante."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class F10PedidoListaOuDecisao(unittest.TestCase):
    """F10 (variante A): pedido, lista ou decisão do dono gravados no mesmo turno; o vigia avisa a lista não gravada."""

    def test_regra_e_jarvis_cobrem_pedido_lista_ou_decisao(self):
        for rel in ("docs/regras/R-DECISAO.md", "agents/jarvis.md"):
            with self.subTest(arquivo=rel):
                texto = " ".join(ler(rel).split()).lower()
                self.assertTrue("pedido, lista ou decisão do dono" in texto, "falta 'pedido, lista ou decisão do dono'")
                self.assertTrue("scratchpad" in texto, "falta a regra do scratchpad")

    def test_sem_citacao_de_diario_inexistente(self):
        for rel in ("docs/regras/R-DECISAO.md", "agents/jarvis.md"):
            with self.subTest(arquivo=rel):
                self.assertNotIn("diário de retomada", ler(rel), "citação sem arquivo nem modelo no Forge")
                self.assertNotIn("ou no diário", ler(rel))

    def test_vigia_declara_a_checagem_e_so_avisa_o_dono(self):
        fonte = ler("hooks/vigia.py")
        self.assertTrue("entrada-sem-registro" in fonte, "vigia sem a checagem entrada-sem-registro")
        self.assertTrue("a lista do turno não foi gravada em docs/pedidos/" in fonte, "vigia sem o texto fixo do aviso")


if __name__ == "__main__":
    unittest.main()
