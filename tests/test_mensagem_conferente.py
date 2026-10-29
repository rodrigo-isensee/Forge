"""T6 (T6T3-MENSAGEM, E1): a etapa da mensagem ao conferente vem da linha `Etapa:` do brief. Raiz sintética do `Cenario`; biblioteca padrão, sem rede."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ARQ, Cenario  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

BASE_SHA = "c" * 40
CABECALHO = f"Etapa: codigo   Cobre: E1.1\nBranch: melhoria/x   Base: develop   Base-sha: {BASE_SHA}\n"


class MensagemPelaEtapaDoBrief(Cenario):
    def setUp(self):
        super().setUp()
        self.completo = self.completo.replace("Agente destino: forge:dev-exemplo\n", "Agente destino: forge:dev-exemplo\n" + CABECALHO, 1)
        self.gravar(ARQ, self.completo)

    def test_a_etapa_sai_da_linha_etapa_do_brief(self):
        rc, saida = self.mensagem(etapa=None)
        self.assertEqual(rc, 0, saida)
        self.assertIn("Etapa: codigo", saida.decode().splitlines()[1])
        self.assertEqual(self.mensagem(etapa="codigo")[0], 0)

    def test_etapa_diferente_da_do_brief_e_recusada_com_a_etapa_certa(self):
        rc, saida = self.mensagem(etapa="pr")
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), "brief mensagem: --etapa difere da `Etapa:` do brief; a etapa do brief é codigo")


if __name__ == "__main__":
    unittest.main()
