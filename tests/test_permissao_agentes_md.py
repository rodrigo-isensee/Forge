"""PERMISSAO-AGENTES-MD: a skill manda avisar antes de delegar edição de agents/*.md. 0.44.2: âncora e ID da regra."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import ids, linha  # noqa: E402


class PermissaoAgentesMd(unittest.TestCase):
    def test_skill_manda_avisar_antes_de_delegar_edicao_de_agents(self):
        self.assertIn("R-CONFORMIDADE", ids(linha("skills/trabalho-em-paralelo/SKILL.md", "- **Delegação que edita `agents/*.md`:**")))


if __name__ == "__main__":
    unittest.main()
