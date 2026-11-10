"""AQ1-TEXTO: guardas do diff, QA como fonte de achados e brief seguinte. 0.44.2: comportamento onde há (o formato que o
forge-check lê, o comando que existe) e, no resto, âncora e ID da regra, não a frase (tests/apoio_regra_id.py)."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import RAIZ, ids, ler, linha  # noqa: E402


class GuardasDoDiff(unittest.TestCase):
    def test_a_catraca_confere_as_guardas_e_o_tech_lead_cita_a_secao_do_qa(self):
        guardas = linha("agents/tech-lead.md", "**Guardas do diff")
        import catraca  # noqa: PLC0415 - quem confere as guardas é a catraca, não o texto
        self.assertTrue(callable(catraca.regra_guardas_dos_hooks))
        self.assertIn("tests/mutantes/", guardas)
        self.assertIn("Mutantes declarados", guardas, "a seção citada é a do qa-testing")

    def test_a_secao_citada_existe_no_qa_testing(self):
        self.assertIn("## Mutantes declarados nos pedidos de controle", ler("skills/qa-testing/SKILL.md").splitlines())

    def test_skill_de_praticas_pede_mutante_sem_caminho_do_forge(self):
        guarda = linha("skills/engineering-practices/SKILL.md", "- Guarda nova ou mudada:")
        self.assertNotIn("bin/", guarda)
        self.assertNotIn("hooks/", guarda)


class AchadosDoQa(unittest.TestCase):
    def test_o_qa_escreve_parecer_como_review_e_seguranca(self):
        sys.path.insert(0, str(RAIZ / "tests"))
        from test_selo_e_entrega import fc  # noqa: PLC0415
        self.assertIn("qa", fc.ETAPAS_DE_PARECER)  # o QA escreve parecer (e com ele os achados) como o review e a segurança
        self.assertIn("R-QA", ids(ler("skills/qa-testing/SKILL.md")))

    def test_arquivo_de_achados_cita_as_regras_dos_tres_escritores(self):
        self.assertLessEqual({"R-REVIEW", "R-SEGURANCA", "R-QA"}, ids(ler("docs/engineering/achados-recorrentes.md")))


class BriefSeguinte(unittest.TestCase):
    def test_o_comando_citado_pela_skill_existe(self):
        self.assertIn("forge-check brief selar", ler("skills/briefs-e-conferencia/SKILL.md"))
        r = subprocess.run([sys.executable, str(RAIZ / "bin" / "forge-check"), "brief", "selar", "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("R-BRIEF", ids(ler("skills/briefs-e-conferencia/SKILL.md")))


if __name__ == "__main__":
    unittest.main()
