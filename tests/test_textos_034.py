"""TEXTOS-034: regras de texto dos agentes, skills e modelos da 0.34, cobradas pelo texto."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(*partes):
    return RAIZ.joinpath(*partes).read_text(encoding="utf-8")


class PerguntaMaiorMenor(unittest.TestCase):
    def test_regra_e_skill_pedem_dizer_se_o_custo_fica_maior_ou_menor(self):
        self.assertIn("se esse custo fica maior ou menor que o das outras opções", ler("docs", "regras", "R-DECISAO.md"))
        skill = ler("skills", "modo-iniciante", "SKILL.md")
        self.assertIn("se o custo da opção fica **maior ou menor** que o das outras", skill)
        self.assertIn("Em custo, a mais cara.", skill)


class ModelosDeParecer(unittest.TestCase):
    MODELOS = ("templates/projeto/docs/reviews/_modelo.md", "templates/projeto/docs/qa/_modelo.md",
               "templates/projeto/docs/security/_modelo.md", "docs/security/_modelo.md")

    def test_teto_de_300_diz_que_o_prefixo_nao_conta(self):
        self.assertEqual(len(self.MODELOS), 4)
        for rel in self.MODELOS:
            self.assertIn("o prefixo `A<n> (...) <arquivo>:<linha>` não conta", ler(*rel.split("/")), rel)

    def test_modelo_de_seguranca_do_forge_avisa_da_neutralidade(self):
        self.assertIn("o parecer não cita nome de linguagem", ler("docs", "security", "_modelo.md"))
        self.assertNotIn("neutralidade", ler("templates", "projeto", "docs", "security", "_modelo.md"))


if __name__ == "__main__":
    unittest.main()
