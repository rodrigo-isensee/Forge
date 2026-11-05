"""PERMISSAO-AGENTES-MD: texto cobrado por teste."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(*partes):
    return RAIZ.joinpath(*partes).read_text(encoding="utf-8")


class PermissaoAgentesMd(unittest.TestCase):
    def test_skill_manda_avisar_antes_de_delegar_edicao_de_agents(self):
        texto = ler("skills", "trabalho-em-paralelo", "SKILL.md")
        self.assertIn("**Delegação que edita `agents/*.md`:**", texto)
        self.assertIn("Quando a regra de permissão para editar `agents/**` não estiver configurada", texto)
        self.assertIn("não contorna por script (`R-CONFORMIDADE`)", texto)


if __name__ == "__main__":
    unittest.main()
