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
    "branch atualizada (a decisão dita; no modelo, desmarcada desde a E8 da 0.45.6)": "Require branches to be up to date before merging",
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

    def test_modelo_deixa_branch_atualizada_desmarcada_com_o_motivo(self):  # E8 (0.45.6): a base entra uma vez, no fim
        passo = next(l for l in ler(MODELO).splitlines() if "Require branches to be up to date before merging" in l)
        self.assertIn("Deixe **Require branches to be up to date before merging** desmarcado", passo)
        self.assertIn("CI contra a base real", passo)

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



SKILL_CHECAGEM = "skills/checagem-do-brief/SKILL.md"
LISTA_LOCAL = "docs/engineering/brief-checklist.md"
# Itens da SK-1 (brief-do-forge), fechada pela B3: ficam na lista do Forge e nunca na skill neutra.
ITENS_DO_FORGE = ("STATUS-HOOK-DEVELOP", "BRIEF-DIFF-COMMIT", "ROTEIRO-SIMULACAO-MERGE", "RETOMADA-MERGE-BRANCH",
                  "WORKFLOW-SCOPE", "INVARIANTE-GATILHO", "HOOK-STDERR-ADR", "GH-LOG-CACHE", "ROTEIRO-DA-RELEASE")
SO_DO_FORGE = ITENS_DO_FORGE + ("catraca", "PROTEGIDOS", "~/Forge", "afrouxa-regra")


class ChecagemDoBrief(unittest.TestCase):
    """B3 (CHECAGEM-DO-BRIEF, versao-038 E2): skill neutra com a lista local opcional do projeto."""

    def test_skill_existe_com_o_nome(self):
        self.assertRegex(ler(SKILL_CHECAGEM), r"\A---\nname: checagem-do-brief\n")

    def test_skill_cita_a_lista_local(self):
        self.assertIn(f"Se existir `{LISTA_LOCAL}` no projeto, confira cada item cujo `quando:` casa com o tipo do brief", ler(SKILL_CHECAGEM))

    def test_lista_local_so_acrescenta(self):
        for caminho in (SKILL_CHECAGEM, "templates/projeto/" + LISTA_LOCAL, LISTA_LOCAL):
            self.assertIn("nunca dispensa portão, review, QA, segurança nem rótulo do dono", ler(caminho), caminho)
        self.assertIn("vira pergunta ao dono (`R-DECISAO`)", ler(SKILL_CHECAGEM))

    def test_modelo_do_projeto_existe_e_e_neutro(self):
        texto = ler("templates/projeto/" + LISTA_LOCAL)
        self.assertIn("(quando: <tipo de brief>)", texto)
        for termo in SO_DO_FORGE:
            self.assertNotIn(termo, texto, termo)

    def test_skill_neutra_sem_item_do_forge(self):
        texto = ler(SKILL_CHECAGEM)
        for termo in SO_DO_FORGE:
            self.assertNotIn(termo, texto, termo)

    def test_lista_do_forge_traz_os_itens_da_sk1(self):
        linhas = [l for l in ler(LISTA_LOCAL).splitlines() if l.startswith("- [ ] ")]
        for item in ITENS_DO_FORGE:
            self.assertEqual(sum(l.endswith(f" · {item}") for l in linhas), 1, item)

    def test_briefs_e_conferencia_manda_ler_a_skill(self):
        self.assertIn("Leia a skill `checagem-do-brief` para o que a ferramenta não sabe",
                      ler("skills/briefs-e-conferencia/SKILL.md"))


if __name__ == "__main__":
    unittest.main()


PRATICAS = "templates/projeto/docs/engineering/praticas.md"
# Os 4 trechos de `invariantes` (tests/config.json) do modelo praticas.md seguem depois da meta (E3a, M-4).
INVARIANTES_PRATICAS = ("## Regras e quem as decide", "**ferramenta**", "**leitura**",
                        "pendência a registrar, não revisão manual")


class MetaDeMutacao(unittest.TestCase):
    """M-4 (versao-041 E3a): o modelo de práticas traz a meta de mutação que o pronto.md da stack cita."""

    def setUp(self):
        self.texto = ler(PRATICAS)
        achado = re.search(r"^## Meta de mutação\n(.*?)(?=^## |\Z)", self.texto, re.S | re.M)
        self.secao = achado.group(1) if achado else ""

    def test_linha_da_tabela_decidida_pelo_comando_de_mutacao(self):
        self.assertIn("| Pontuação de mutação no código alterado ≥ meta | `<comando de mutação do pronto.md>` |",
                      self.texto)

    def test_secao_da_meta_com_valor_e_regras(self):
        self.assertTrue(self.secao.strip(), "falta a seção '## Meta de mutação'")
        for trecho in ("<pontuação da primeira rodada>", "só sobe", "decisão do dono", "Entrega sem código"):
            self.assertIn(trecho, self.secao, trecho)

    def test_invariantes_do_modelo_seguem(self):
        for trecho in INVARIANTES_PRATICAS:
            self.assertIn(trecho, self.texto, trecho)
