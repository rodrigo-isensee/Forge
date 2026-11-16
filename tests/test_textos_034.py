"""TEXTOS-034: regras da 0.34. 0.44.2: o teto de 300 do achado é provado no `forge-check` (o prefixo não conta); o resto, por
âncora e ID da regra (tests/apoio_regra_id.py), não pela frase."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import ids, ler, linha  # noqa: E402
from test_selo_e_entrega import fc  # noqa: E402


class PerguntaMaiorMenor(unittest.TestCase):
    def test_regra_e_skill_citam_a_regra_das_opcoes(self):
        self.assertIn("**as opções**", ler("docs/regras/R-DECISAO.md"))  # âncora protegida também por invariante
        self.assertIn("R-DECISAO", ids(ler("skills/modo-iniciante/SKILL.md")))


class ModelosDeParecer(unittest.TestCase):
    MODELOS = ("templates/projeto/docs/reviews/_modelo.md", "templates/projeto/docs/qa/_modelo.md",
               "templates/projeto/docs/security/_modelo.md", "docs/security/_modelo.md")

    def achado(self, texto):
        return f"## Achados\n- A1 (recomendado) {'x' * 60}.py:12 · {texto}\n"

    def test_teto_de_300_nao_conta_o_prefixo(self):
        _, erros, _ = fc.achados_do_parecer(self.achado("y" * fc.TETO_DO_ACHADO))
        self.assertEqual(erros, [], "o prefixo longo não entra na conta")
        _, erros, _ = fc.achados_do_parecer(self.achado("y" * (fc.TETO_DO_ACHADO + 1)))
        self.assertEqual(len(erros), 1)

    def test_modelos_citam_a_regra_do_parecer(self):
        self.assertEqual(len(self.MODELOS), 4)
        for rel in self.MODELOS:
            self.assertIn("R-REVIEW", ids(ler(rel)), rel)

    def test_modelo_de_seguranca_do_projeto_nao_fala_da_fabrica(self):
        self.assertNotIn("neutralidade", ler("templates/projeto/docs/security/_modelo.md"))


class InvarianteGatilho(unittest.TestCase):
    def test_modelo_de_pedido_nasce_com_a_etapa_de_seguranca(self):
        self.assertIn("R-SEGURANCA", ids(linha("templates/projeto/docs/pedidos/_modelo.md", "- E1.3 (security-engineer)")))


class PermissaoAgentesMd(unittest.TestCase):
    def test_skill_manda_avisar_antes_de_delegar_edicao_de_agents(self):
        self.assertIn("R-CONFORMIDADE", ids(linha("skills/trabalho-em-paralelo/SKILL.md", "- **Delegação que edita `agents/*.md`:**")))


class E8TextoAntigo(unittest.TestCase):
    """E8-TEXTO-ANTIGO (v047 E2.74): desde a E8 da 0.45.6 o `portoes` deixa desmarcada a regra "branch atualizada com a
    base"; a conferência do dono na ADR 0012 pede a regra desmarcada, não a trata como ligada."""
    def test_conferencia_da_0012_pede_a_regra_desmarcada(self):
        conf = linha("docs/adr/0012-main-por-merge-commit.md", "Conferência do dono antes da próxima release")
        self.assertIn("deixa desmarcada", conf)
        self.assertIn("docs/protecao-de-branch.md", conf)
        self.assertNotIn('a regra "branch atualizada com a base" do ruleset `portoes` são configuração', conf)


class CorrecaoAntesDosPortoes(unittest.TestCase):
    """CORRECAO-ANTES-DOS-PORTOES (v047 E2.74, retro da 0.47.0 C5): correção que muda arquivo da branch, achado
    `recomendado` incluso, entra antes dos portões; a regra fica na skill e o tech-lead aponta para ela."""
    ANCORA = "- **Correção antes dos portões:**"

    def test_skill_tem_a_regra_com_o_id(self):
        regra = linha("skills/trabalho-em-paralelo/SKILL.md", self.ANCORA)
        self.assertIn("R-REVIEW", ids(regra))
        self.assertIn("`recomendado`", regra)

    def test_tech_lead_aponta_para_a_skill(self):
        ponteiro = linha("agents/tech-lead.md", self.ANCORA)
        self.assertIn("trabalho-em-paralelo", ponteiro)
        self.assertIn("R-REVIEW", ids(ponteiro))


if __name__ == "__main__":
    unittest.main()
