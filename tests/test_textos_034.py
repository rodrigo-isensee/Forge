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


if __name__ == "__main__":
    unittest.main()
