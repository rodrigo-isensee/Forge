"""QA do L10 (E14 VOLTA-ETAPA-NOVA, T-3 e C-3): a prova de abertura vem só da forma e da ordem do `## Histórico` do pedido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_volta_por_delta import BriefDeVolta  # noqa: E402


class ProvaDaAbertura(BriefDeVolta):
    BRIEF = "- 2026-11-04 09:00: brief pedido-sintetico-dev-exemplo-1 delegado"

    def fora(self, *historico):
        self.pedido_e14(*historico)
        return self.gerar()[1].split("## Fora do escopo")[1].split("\n## ")[0]

    def test_so_o_brief_anterior_exato_marca_o_inicio_e_abertura_com_sufixo_nao_vale(self):  # C-3, T-3
        aberta = "- 2026-11-04 10:00: etapa E1.4b aberta"
        self.assertIn(self.LINHA_E14, self.fora(self.BRIEF, aberta))  # controle: a forma certa entra
        outro = self.BRIEF.replace("exemplo-1 ", "exemplo-10 ")  # outro brief, de número que começa igual
        self.assertNotIn(self.LINHA_E14, self.fora(outro, aberta))
        for ruim in ("- 2026-11-04 10:00: etapa E1.4b abertura prevista", "- 2026-11-04 10:00: etapa E1.4b abertas"):
            with self.subTest(ruim):
                self.assertNotIn(self.LINHA_E14, self.fora(self.BRIEF, ruim))


def load_tests(loader, tests, pattern):  # só a classe nova; a base é fixture, não suíte repetida
    return loader.loadTestsFromNames([f"{ProvaDaAbertura.__qualname__}.{n}" for n in dir(ProvaDaAbertura) if n.startswith("test_so_o_brief")], sys.modules[__name__])


if __name__ == "__main__":
    unittest.main()
