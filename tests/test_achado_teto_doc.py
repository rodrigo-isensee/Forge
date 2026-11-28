"""ACHADO-TETO-DOC: o teto de 300 do achado. 0.44.2: o agente cita a regra do parecer; o teto é provado no forge-check
(tests/test_textos_034.py, ModelosDeParecer)."""
import re
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


# META85 (v0478 E35.1): texto que decide a volta → frase que prova a regra nele.
CARTAO = {
    "docs/regras/R-REVIEW.md": "a de review e QA vira cartão depois do merge; a de segurança é corrigida antes",
    "docs/regras/R-SEGURANCA.md": "O resto é recomendação, que volta e é corrigida antes do merge",
    "agents/tech-lead.md": "o `recomendado` vira cartão depois do merge",
    "agents/qa-engineer.md": "o `recomendado` vira cartão depois do merge",
    "agents/security-engineer.md": "o seu `recomendado` volta e é corrigido antes do merge",
    "skills/briefs-e-conferencia/SKILL.md": "o recomendado da segurança e o CI vermelho viram **um** brief de volta",
    "skills/briefs-e-conferencia/autor-ate-o-merge.md": "a de review e a de QA viram cartão depois do merge",
    "skills/trabalho-em-paralelo/SKILL.md": "`recomendado` de review e QA vira cartão: `R-REVIEW`",
    "templates/projeto/docs/reviews/_modelo.md": "não devolve e vira cartão depois do merge",
    "templates/projeto/docs/qa/_modelo.md": "não devolve e vira cartão depois do merge",
    "templates/projeto/docs/security/_modelo.md": "na segurança, volta ao autor e é corrigido antes do merge",
    "templates/projeto/docs/devops/_modelo.md": "não devolve e vira cartão depois do merge",
    "agents/devops-engineer.md": "o `recomendado` vira cartão depois do merge",
    "docs/security/_modelo.md": "na segurança, volta ao autor e é corrigido antes do merge",
}


class RecomendadoViraCartao(unittest.TestCase):
    """META85-RECOMENDADO-VIRA-CARTAO (v0478 E35.1, ordem do dono de 18/11 17:00): o achado `recomendado` de review e de QA
    não gera volta, vira cartão depois do merge; o `recomendado` da segurança continua corrigido antes, na volta. A regra mora
    em `docs/regras/R-REVIEW.md` e chega aos textos que decidem a volta: o Jarvis, os três portões, a skill do brief de volta e
    os modelos de parecer. Neutro: vale para todos os projetos (os modelos vão para cada um pelo `forge-init`)."""

    def test_cada_texto_que_decide_a_volta_traz_a_regra(self):
        self.assertGreaterEqual(len(CARTAO), 14)
        for rel, frase in CARTAO.items():
            with self.subTest(arquivo=rel):
                self.assertIn(frase, ler(rel))

    def test_o_passo_6_do_jarvis_separa_review_e_qa_da_seguranca(self):
        passo6 = next(l for l in ler("agents/jarvis.md").splitlines() if l.startswith("6. **QA**"))
        self.assertIn("recomendado de review e QA vira cartão, o de segurança volta", passo6)

    def test_o_brief_de_volta_inclui_so_o_recomendado_da_seguranca(self):
        volta = ler("skills/briefs-e-conferencia/autor-ate-o-merge.md")
        self.assertIn("Recomendação não entra, salvo a de segurança, que entra por `--incluir <parecer>:A<n>`", volta)

    def test_nenhum_texto_manda_corrigir_antes_o_recomendado_de_review_ou_qa(self):
        """A regra antiga ('achado `recomendado` incluso' na correção antes dos portões) gerava a volta que a META85 corta."""
        antigos = ("achado `recomendado` incluso", "o resto é `recomendado` e não devolve.", "O resto é recomendação e não devolve")
        arquivos = [*CARTAO, "agents/jarvis.md"]
        self.assertGreaterEqual(len(arquivos), 13)
        for rel in arquivos:
            for antigo in antigos:
                with self.subTest(arquivo=rel, antigo=antigo):
                    self.assertNotIn(antigo, ler(rel))
        for rel in ("agents/tech-lead.md", "agents/qa-engineer.md"):
            with self.subTest(arquivo=rel):
                self.assertIsNone(re.search(r"`recomendado`[^.;]*corrigid", ler(rel)))


if __name__ == "__main__":
    unittest.main()
