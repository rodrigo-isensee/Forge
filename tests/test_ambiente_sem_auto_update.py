import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class AmbienteSemAutoUpdate(unittest.TestCase):
    def test_orientacao_ao_dono_no_readme_e_no_modelo(self):
        for rel in ("README.md", "templates/projeto/CLAUDE.md"):
            with self.subTest(rel=rel):
                self.assertIn("desligue a atualização automática da extensão do Claude Code", ler(rel))

    def test_retomada_depois_de_reinicio_na_skill_do_jarvis(self):
        skill = ler("skills/trabalho-em-paralelo/SKILL.md")
        self.assertIn("relance cada agente do ponto em que parou, sem refazer o feito", skill)
        self.assertIn("briefs selados", skill)


if __name__ == "__main__":
    unittest.main()
