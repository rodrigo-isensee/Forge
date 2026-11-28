"""E3.43 (v0474, R-CUSTO): não reenviar branch nem repetir o CI sem motivo. Em projeto privado, cada push e cada `gh run rerun`
custa um run de CI (no projeto de origem, 163 rodadas de push contra 33 de PR num dia, e a cota grátis acabou).

Onde mora o texto: o detalhe na seção `## CI pago` de skills/trabalho-em-paralelo/ritmo-e-corte.md (diretriz 25: as skills do
Jarvis estão no teto de tests/fixtures/metricas-texto.json e trazem só o resumo e o ponteiro); nos agentes que enviam ou repetem o
CI (desenvolvimento e portões), uma linha com a âncora `**CI pago**`. O teste confere a âncora e as partes da regra, não a frase
inteira (padrão de tests/apoio_regra_id.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_regra_id import ids, ler  # noqa: E402

ANCORA = "**CI pago**"
# Linha dos agentes: o custo de cada envio, as condições do push e o rerun com motivo escrito.
PARTES = ("cada push", "`gh run rerun`", "junte os commits", "comando local verde", "motivo escrito", "falha de infraestrutura no log")
AGENTES = ("agents/tech-lead.md", "agents/devops-engineer.md", "agents/qa-engineer.md")
# Os agentes de desenvolvimento das stacks, por caminho: um glob em stacks/ tiraria o módulo do plano do forge-testes
# (test_testes_tocados, varredura de pasta).
STACKS = ("stacks/python/agents/python-backend.md", "stacks/node-react/agents/node-backend.md",
          "stacks/node-react/agents/react-frontend.md")
# O qa-engineer não cita o ID: citar carrega o texto do R-CUSTO (532 caracteres) e passa o teto de docs/regras/orcamento.json.
SEM_ID = {"agents/qa-engineer.md"}
DETALHE = "skills/trabalho-em-paralelo/ritmo-e-corte.md"
SKILL_ENVIO = "skills/trabalho-em-paralelo/SKILL.md"
SKILL_VOLTA = "skills/briefs-e-conferencia/SKILL.md"


def linhas_com(rel, trecho):
    return [l for l in ler(rel).splitlines() if trecho in l]


def linha_ci_pago(rel):
    achadas = linhas_com(rel, ANCORA)
    if len(achadas) != 1:
        raise AssertionError(f"{rel}: {len(achadas)} linhas com {ANCORA!r} (precisa de uma)")
    return achadas[0]


def secao(rel, titulo):
    """O texto da seção `## <titulo>...` até o próximo `## `."""
    texto = ler(rel)
    if f"\n## {titulo}" not in texto:
        raise AssertionError(f"{rel}: falta a seção '## {titulo}'")
    return texto.split(f"\n## {titulo}", 1)[1].split("\n## ", 1)[0]


class CiSemReenvio(unittest.TestCase):
    def test_stacks_listadas_sao_as_que_enviam(self):
        for rel in STACKS:
            with self.subTest(arquivo=rel):
                self.assertIn("Antes do push", ler(rel))

    def test_agentes_que_enviam_trazem_a_regra(self):
        for rel in AGENTES + STACKS:
            with self.subTest(arquivo=rel):
                linha = linha_ci_pago(rel)
                for parte in PARTES:
                    self.assertIn(parte, linha)
                if rel not in SEM_ID:
                    self.assertIn("R-CUSTO", ids(linha))

    def test_detalhe_no_ritmo_e_corte(self):
        texto = secao(DETALHE, "CI pago")
        self.assertIn("R-CUSTO", ids(texto))
        for parte in ("cada push", "`gh run rerun`", "Junte os commits", "comando local verde", "motivo escrito",
                      "falha de infraestrutura comprovada no log", "brief de volta"):
            with self.subTest(parte=parte):
                self.assertIn(parte, texto)

    def test_skill_de_envio_manda_ler_o_detalhe(self):
        linha = linha_ci_pago(SKILL_ENVIO)
        self.assertIn("`gh run rerun`", linha)
        self.assertIn("`ritmo-e-corte.md`", linha)
        self.assertIn("R-CUSTO", ids(linha))

    def test_ci_vermelho_vai_no_brief_de_volta_sem_rerun(self):
        paragrafo = [l for l in linhas_com(SKILL_VOLTA, "brief de volta") if "CI vermelho" in l]
        self.assertEqual(len(paragrafo), 1, "o CI vermelho saiu do parágrafo do brief de volta")
        self.assertIn("`gh run rerun`", paragrafo[0])
        self.assertIn("R-CUSTO", ids(paragrafo[0]))


if __name__ == "__main__":
    unittest.main()
