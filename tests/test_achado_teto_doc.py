"""ACHADO-TETO-DOC: o teto de 300 do achado. 0.44.2: o agente cita a regra do parecer; o teto é provado no forge-check
(tests/test_textos_034.py, ModelosDeParecer)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import ids, ler  # noqa: E402


class AchadoTetoDoc(unittest.TestCase):
    def test_security_engineer_cita_a_regra_do_parecer(self):
        self.assertLessEqual({"R-REVIEW", "R-SEGURANCA"}, ids(ler("agents/security-engineer.md")))


class ParecerCurto(unittest.TestCase):
    """v047 E2.276 (TEMPO-A, A10): mitigação pelo ID, gatilhos em uma linha e volta sem recopiar a rodada anterior."""

    ARQUIVOS = ("agents/security-engineer.md", "docs/security/_modelo.md", "templates/projeto/docs/security/_modelo.md")
    FRASES = ("citada pelo ID dela (ex.: `M1.1`)", "sem recopiar o texto", "não recopie a rodada anterior (ela fica no git)",
              "`Gatilhos: ")

    def test_agente_e_modelos_trazem_as_tres_regras_do_parecer_curto(self):
        for caminho in self.ARQUIVOS:
            texto = ler(caminho)
            for frase in self.FRASES:
                with self.subTest(arquivo=caminho, frase=frase):
                    self.assertIn(frase, texto)

    def test_os_dois_modelos_seguem_iguais(self):
        self.assertEqual(ler("docs/security/_modelo.md"), ler("templates/projeto/docs/security/_modelo.md"))

    def test_gatilhos_do_modelo_em_uma_linha(self):
        for caminho in self.ARQUIVOS[1:]:
            secao = ler(caminho).split("## Gatilhos\n", 1)[1].split("\n\n", 1)[0]
            with self.subTest(arquivo=caminho):
                self.assertEqual(secao.count("\n"), 0)
                self.assertIn("`Gatilhos: ", secao)


if __name__ == "__main__":
    unittest.main()
