"""N-JAR-A (0.37 E5): D2, D3, Q1 e Q2 do dono nas skills do Jarvis; o núcleo cita a skill sem passar do teto de linhas.
0.44.2: IDs das regras que mandam em cada skill, não as frases (tests/apoio_regra_id.py)."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import RAIZ, ids, ler  # noqa: E402

TETO = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))["limite_linhas"]["agente"]
REGRAS = {"skills/trabalho-em-paralelo/SKILL.md": {"R-FLUXO", "R-TETO", "R-WIP"},
          "skills/falar-com-o-dono/SKILL.md": {"R-DECISAO", "R-CUSTO"}}


class TextoDoNJarA(unittest.TestCase):
    def test_as_skills_citam_as_regras_das_decisoes(self):
        self.assertEqual(len(REGRAS), 2)
        for rel, esperadas in REGRAS.items():
            with self.subTest(arquivo=rel):
                self.assertLessEqual(esperadas, ids(ler(rel)))

    def test_o_jarvis_cita_a_skill_e_nao_passa_do_teto(self):
        jarvis = ler("agents/jarvis.md")
        self.assertIn("skills/trabalho-em-paralelo/SKILL.md", jarvis)
        self.assertLessEqual(len(jarvis.splitlines()), TETO)


if __name__ == "__main__":
    unittest.main()
