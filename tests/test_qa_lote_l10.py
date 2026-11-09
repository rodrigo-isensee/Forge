"""QA do L10 (E14 VOLTA-ETAPA-NOVA), revisto na 0.43.1 (C2): o Fora do escopo da volta sai do `## Etapas` do pedido; a prova de abertura
no `## Histórico` deixou de ser condição (o E14 só acrescentava ao Fora copiado do brief anterior, que não é mais copiado)."""
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

    def test_so_o_brief_anterior_exato_marca_o_inicio_e_abertura_com_sufixo_nao_vale(self):  # nome mantido (load_tests); 0.43.1: sem prova
        aberta = "- 2026-11-04 10:00: etapa E1.4b aberta"
        outro = self.BRIEF.replace("exemplo-1 ", "exemplo-10 ")
        for historico in ((self.BRIEF, aberta), (outro, aberta), (self.BRIEF, "- 2026-11-04 10:00: etapa E1.4b aberta-nao"), ()):
            with self.subTest(historico=historico):  # a etapa do pedido entra no Fora com ou sem a linha de abertura, uma vez só
                fora = self.fora(*historico)
                self.assertEqual(fora.count(self.LINHA_E14), 1, fora)

def load_tests(loader, tests, pattern):  # só a classe nova; a base é fixture, não suíte repetida
    return loader.loadTestsFromNames([f"{ProvaDaAbertura.__qualname__}.{n}" for n in dir(ProvaDaAbertura) if n.startswith("test_so_o_brief")], sys.modules[__name__])


if __name__ == "__main__":
    unittest.main()
