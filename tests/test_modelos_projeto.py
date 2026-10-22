"""Lote N-TPL-a: o passo a passo da proteção de branch (F8) e o modelo de dependabot.yml (M9) existem e dizem o que o modelo de ameaças exige."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE = "docs/protecao-de-branch.md"
MODELO = "templates/projeto/docs/engineering/protecao-de-branch.md"
# Controles do modelo de ameaças (F8, controles (a) a (g)): cada um tem de estar dito nos dois textos.
CONTROLES = {
    "ruleset sem desvio": "sem ator de bypass",
    "enforcement ativo": "Active",
    "fonte do check fixada": "GitHub Actions",
    "force push": "force push",
    "deleção": "deleção",
    "branch atualizada": "branch atualizada com a base",
    "conferência de leitura": "gh api repos/",
    "custo do repositório privado": "decisão do dono",
    "dono configura": "`R-CONFORMIDADE`",
    "sem filtro de caminho": "filtro de caminho",
    "sem aprovação humana obrigatória": "aprovação obrigatória de revisor",
}


def ler(caminho):
    return (RAIZ / caminho).read_text(encoding="utf-8")


class TestPassoAPassoDaProtecao(unittest.TestCase):
    def test_passo_a_passo_de_protecao_existe(self):
        for caminho in (FORGE, MODELO):
            self.assertTrue((RAIZ / caminho).is_file(), caminho)

    def test_passo_a_passo_traz_cada_controle_do_modelo_de_ameacas(self):
        for caminho in (FORGE, MODELO):
            texto = ler(caminho)
            for nome, trecho in CONTROLES.items():
                self.assertIn(trecho, texto, f"{caminho}: {nome}")

    def test_checks_citados_existem_nos_workflows(self):
        nomes = set()
        for wf in sorted((RAIZ / ".github/workflows").glob("*.yml")):
            nomes.update(re.findall(r"^\s+name:\s*([^\s#][^#\n]*?)\s*(?:#.*)?$", wf.read_text(encoding="utf-8"), re.M))
        citados = re.findall(r"^- Check exigido: `([^`]+)`", ler(FORGE), re.M)
        self.assertGreaterEqual(len(citados), 2)
        for check in citados:
            self.assertIn(check, nomes, check)

    def test_protecao_sem_bypass_nos_portoes(self):
        texto = ler(FORGE)
        portoes = texto.split("## Ruleset `portoes`", 1)[1].split("\n## ", 1)[0]
        self.assertIn("sem ator de bypass", portoes)
        self.assertNotRegex(portoes, r"(?i)bypass (para|do) (administrador|dono|bot)")

    def test_modelo_de_projeto_e_neutro_e_nao_manda_escrever_na_api(self):
        texto = ler(MODELO)
        self.assertNotRegex(texto, r"(?i)catraca")
        self.assertNotRegex(texto, r"(?i)bateria")
        for caminho in (FORGE, MODELO):
            self.assertNotRegex(ler(caminho), r"--method|-X (POST|PUT|PATCH|DELETE)|--input", caminho)

    def test_texto_diz_que_agente_nao_cola_token_nem_chama_api_de_escrita(self):
        for caminho in (FORGE, MODELO):
            texto = ler(caminho)
            self.assertIn("nenhum agente", texto, caminho)
            self.assertIn("token", texto, caminho)


if __name__ == "__main__":
    unittest.main()
