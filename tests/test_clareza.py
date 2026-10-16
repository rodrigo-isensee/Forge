"""Pacote 1 de clareza: o texto novo existe nos arquivos que o carregam (marcas, recibo, formato de pergunta, ordem ampla, tags)."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCAS = ["confirmado", "delegado", "suposição", "técnico", "no-protótipo"]
TAGS = ["PERGUNTA:", "NAO-ENTENDI:", "ESCOPO+:", "ESCOPO-:", "DEVOLVIDA:"]


def ler(caminho):
    return (RAIZ / caminho).read_text(encoding="utf-8")


class TestClareza(unittest.TestCase):
    def test_modelo_de_pedido_tem_marcas_clareza_e_tags(self):
        t = ler("templates/projeto/docs/pedidos/_modelo.md")
        for item in MARCAS + TAGS + ["**Clareza:**"]:
            self.assertIn(item, t)

    def test_modo_iniciante_tem_formato_fixo_de_pergunta(self):
        t = ler("skills/modo-iniciante/SKILL.md")
        secao = t.split("## Como perguntar", 1)[1].split("\n## ", 1)[0]
        for trecho in ["Afrouxa o processo?", "custo de eficiência", "Faltam N perguntas.", "decidam vocês", "Exemplo", "Recomendação"]:
            self.assertIn(trecho, secao)

    def test_regra_decisao_delegado_e_ordem_ampla_so_por_acrescimo(self):
        t = ler("docs/regras/R-DECISAO.md")
        for trecho in ["viram item `delegado`", "nunca são delegáveis assim", "Ordem ampla não confirma", "`confirmado` ou `delegado`"]:
            self.assertIn(trecho, t)
        self.assertIn("Teste de bloqueante", t)  # trecho existente continua

    def test_jarvis_manda_marcar_dar_recibo_gravar_tags_e_citar_formato(self):
        t = ler("agents/jarvis.md")
        for trecho in ["Recibo antes de acionar o time", "frase literal entre aspas", "Como perguntar", "Ordem ampla não confirma"] + TAGS:
            self.assertIn(trecho, t)

    def test_agile_coach_mede_pelas_tags(self):
        t = ler("agents/agile-coach.md")
        self.assertGreaterEqual(len(re.findall(r"`(?:PERGUNTA|NAO-ENTENDI|ESCOPO\+|ESCOPO-|DEVOLVIDA):`", t)), 5)
        self.assertIn("Medição de clareza, por pedido", t)


if __name__ == "__main__":
    unittest.main()
