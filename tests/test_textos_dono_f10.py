"""D4 (F10): pedido, lista ou decisão do dono gravados no mesmo turno; o vigia avisa a lista não gravada. 0.44.2: o aviso do
vigia é provado pelos fixtures (comportamento) e o texto, por âncora e ID da regra (tests/apoio_regra_id.py)."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import RAIZ, ids, ler  # noqa: E402


class F10PedidoListaOuDecisao(unittest.TestCase):
    def test_regra_e_jarvis_cobrem_a_decisao_gravada(self):
        self.assertIn("**Decisão só vale gravada:**", ler("docs/regras/R-DECISAO.md"))
        self.assertIn("R-DECISAO", ids(ler("agents/jarvis.md")))

    def test_sem_citacao_de_diario_inexistente(self):
        for rel in ("docs/regras/R-DECISAO.md", "agents/jarvis.md"):
            with self.subTest(arquivo=rel):
                self.assertNotIn("diário de retomada", ler(rel), "citação sem arquivo nem modelo no Forge")
                self.assertNotIn("ou no diário", ler(rel))

    def test_vigia_avisa_a_lista_nao_gravada_nos_fixtures(self):
        fixture = json.loads((RAIZ / "tests" / "hooks" / "vigia" / "entrada-sem-registro-avisa.json").read_text(encoding="utf-8"))
        self.assertIn("docs/pedidos/", fixture["esperado"]["saida"])  # o test_hooks roda o vigia e confere esta saída
        self.assertEqual(fixture["entrada"]["hook_event_name"], "Stop")


if __name__ == "__main__":
    unittest.main()
