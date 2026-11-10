"""0.44.2: três skills curtas sem agente novo (produto-criterios, observabilidade-incidentes, explicar-para-o-leigo): cabeçalho
válido, teto de tamanho e a citação onde o Jarvis, o devops-engineer e o modo-iniciante as usam."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CITADA_EM = {"produto-criterios": "agents/jarvis.md", "observabilidade-incidentes": "agents/devops-engineer.md",
             "explicar-para-o-leigo": "skills/modo-iniciante/SKILL.md"}
TETO_CARACTERES = 2500


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class SkillsDaV0442(unittest.TestCase):
    def test_cabecalho_com_nome_e_descricao_de_uso(self):
        for nome in CITADA_EM:
            with self.subTest(skill=nome):
                texto = ler(f"skills/{nome}/SKILL.md")
                self.assertRegex(texto, rf"\A---\nname: {nome}\ndescription: [^\n]*[Uu]se [^\n]+\n---\n\n# ")

    def test_curta_e_com_passos(self):
        for nome in CITADA_EM:
            with self.subTest(skill=nome):
                texto = ler(f"skills/{nome}/SKILL.md")
                self.assertLess(len(texto), TETO_CARACTERES)
                self.assertGreaterEqual(len(re.findall(r"(?m)^(?:\d+\.|-) ", texto)), 4)

    def test_citada_onde_e_usada(self):
        for nome, onde in CITADA_EM.items():
            with self.subTest(skill=nome):
                self.assertIn(f"`{nome}`", ler(onde))

    def test_sem_agente_novo(self):
        for nome in CITADA_EM:
            self.assertFalse((RAIZ / "agents" / f"{nome}.md").exists())


if __name__ == "__main__":
    unittest.main()
