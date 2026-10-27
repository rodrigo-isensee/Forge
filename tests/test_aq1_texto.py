"""AQ1-TEXTO: regras novas cobradas por texto (guardas do diff, QA como fonte de achados, brief seguinte)."""
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(*partes):
    return RAIZ.joinpath(*partes).read_text(encoding="utf-8")


class GuardasDoDiff(unittest.TestCase):
    def test_tech_lead_manda_um_mutante_por_linha_de_guarda(self):
        texto = ler("agents", "tech-lead.md")
        self.assertIn("**Guardas do diff (no Forge, `bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`):**", texto)
        self.assertIn("**um mutante por linha** em `tests/mutantes/<pedido>.json`", texto)
        self.assertIn("teste que lê o texto da fonte não conta", texto)
        self.assertIn("chama Python com `-I`", texto)
        self.assertIn("'Mutantes declarados'", texto)

    def test_a_secao_citada_existe_no_qa_testing(self):
        self.assertIn("## Mutantes declarados nos pedidos de controle", ler("skills", "qa-testing", "SKILL.md"))

    def test_skill_de_praticas_pede_mutante_e_ramo_de_falha_sem_caminho_do_forge(self):
        texto = ler("skills", "engineering-practices", "SKILL.md")
        linha = [l for l in texto.splitlines() if l.startswith("- Guarda nova ou mudada:")]
        self.assertEqual(len(linha), 1)
        self.assertIn("mutante declarado e teste do ramo de falha", linha[0])
        self.assertNotIn("bin/", linha[0])
        self.assertNotIn("hooks/", linha[0])


class AchadosDoQa(unittest.TestCase):
    def test_arquivo_aceita_qa_como_tipo_e_escritor(self):
        texto = ler("docs", "engineering", "achados-recorrentes.md")
        self.assertIn("`- AR-<n> · review|seguranca|qa · <classe>", texto)
        self.assertIn("o `tech-lead` (review), o `security-engineer` e o `qa-engineer`, no mesmo PR do parecer", texto)

    def test_qa_testing_manda_registrar_classe_reincidente(self):
        texto = ler("skills", "qa-testing", "SKILL.md")
        self.assertIn("Classe que já reprovou antes vira linha `AR-<n> · qa` em `docs/engineering/achados-recorrentes.md`.", texto)


if __name__ == "__main__":
    unittest.main()
