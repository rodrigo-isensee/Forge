"""ADOTAR-TESTE-VERMELHO-ALHEIO (E21.1, decisão do dono de 18/11): o teste vermelho de outro item que para um PR é
consertado pelo time, com duas condições, e o texto que o autor, o tech-lead e o QA leem as traz."""
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DETALHE = "skills/briefs-e-conferencia/teste-vermelho-alheio.md"
CONFIG = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))

# Condição 1: PR próprio, pequeno, prioridade máxima, parecer próprio do QA, nunca misturado ao PR parado, que espera só a correção.
CONDICAO_1 = [r"PR próprio e pequeno", r"prioridade máxima", r"parecer próprio do QA",
              r"Nunca se mistura ao PR parado", r"PR parado espera só a correção"]
# Condição 2: proibido apagar, pular ou afrouxar; teste errado pede a explicação do QA; os mutantes daquele trecho seguem morrendo.
CONDICAO_2 = [r"proibido apagar o teste, pulá-lo ou afrouxar o que ele confere", r"QA explica no parecer",
              r"mutantes daquele trecho continuam morrendo", r"sobrevivente bloqueia"]
# Onde o autor (autor-ate-o-merge, apontado pela SKILL.md da briefs-e-conferencia), o tech-lead (engineering-practices) e o QA
# (o agente) leem o apontamento.
APONTAM = ["skills/briefs-e-conferencia/autor-ate-o-merge.md", "skills/engineering-practices/SKILL.md", "agents/qa-engineer.md"]


def texto(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class DuasCondicoes(unittest.TestCase):
    def test_as_duas_condicoes_do_dono_estao_no_texto(self):
        corpo = texto(DETALHE)
        for padrao in CONDICAO_1 + CONDICAO_2:
            with self.subTest(trecho=padrao):
                self.assertRegex(corpo, padrao)

    def test_texto_lido_pelo_autor_tech_lead_e_qa_aponta_o_detalhe(self):
        for rel in APONTAM:
            with self.subTest(arquivo=rel):
                self.assertIn("teste-vermelho-alheio.md", texto(rel))

    def test_qa_nao_manda_mais_o_vermelho_para_cartao(self):
        linha = next(l for l in texto("skills/qa-testing/SKILL.md").splitlines() if "Dívida pré-existente" in l)
        self.assertNotIn("vira cartão", linha)
        self.assertIn("o time adota o conserto", linha)

    def test_invariantes_protegem_as_duas_condicoes(self):
        """Apagar uma condição do texto quebra o teste de invariantes, que tem regra e porque."""
        trechos = CONFIG["invariantes"].get(DETALHE, [])
        self.assertGreaterEqual(len(trechos), 8)
        corpo = texto(DETALHE)
        for padrao in CONDICAO_1 + CONDICAO_2:
            with self.subTest(trecho=padrao):
                cobertos = [t for t in trechos if re.search(t, corpo) and re.search(padrao, re.search(t, corpo).group(0))]
                self.assertTrue(cobertos, f"{padrao}: nenhum invariante cobre o trecho")
        self.assertEqual(CONFIG["invariantes_motivo"][DETALHE]["regra"], "R-QA")

    def test_invariante_reprova_o_texto_sem_a_condicao(self):
        """O ramo de falha: tirar a condição 2 do texto deixa algum invariante sem casar."""
        sem_condicao = re.sub(r"\*\*É proibido apagar.*?\n", "\n", texto(DETALHE))
        faltam = [t for t in CONFIG["invariantes"][DETALHE] if not re.search(t, sem_condicao, re.S)]
        self.assertTrue(faltam)


    def test_criterio_de_alheio_e_so_herdado_da_base(self):
        """A1 da segurança: o vermelho é alheio só se já cai na base; cair em código que o diff não toca não basta."""
        linha = next(l for l in texto(DETALHE).splitlines() if l.startswith("O PR de um item para"))
        self.assertIn("o teste já cai na base, sem o diff do item", linha)
        self.assertNotRegex(linha, r"ou cai em código que o diff não toca")


class FormasProibidasEPapeis(unittest.TestCase):
    """A2 da segurança: a lista das formas proibidas e as linhas do autor e do tech-lead também são invariantes."""
    TRECHOS = {
        "formas proibidas": r"sem `skip`, sem tirar asserção, sem trocar o valor esperado pelo obtido, sem tirá-lo da lista que roda",
        "autor": r"\*\*Autor:\*\*.*\n",
        "tech-lead": r"\*\*`tech-lead`:\*\*.*\n",
    }

    def test_cada_trecho_tirado_do_texto_reprova_um_invariante(self):
        corpo = texto(DETALHE)
        for nome, padrao in self.TRECHOS.items():
            with self.subTest(trecho=nome):
                self.assertRegex(corpo, padrao)
                sem = re.sub(padrao, "\n", corpo, count=1)
                faltam = [t for t in CONFIG["invariantes"][DETALHE] if not re.search(t, sem, re.S)]
                self.assertTrue(faltam, f"{nome}: tirar o trecho não quebra nenhum invariante")

    def test_texto_inteiro_casa_todos_os_invariantes(self):
        corpo = texto(DETALHE)
        self.assertEqual([t for t in CONFIG["invariantes"][DETALHE] if not re.search(t, corpo, re.S)], [])


if __name__ == "__main__":
    unittest.main()
