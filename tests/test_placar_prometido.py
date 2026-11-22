"""`forge-placar propostas` (MEDIR-DE-NOVO-O-PROMETIDO): a proposta com `prometido: <N>%` na Métrica mostra o ganho medido
depois de entrar ao lado do prometido, e `sem medida` quando não há. Fixtures sintéticas numa raiz temporária, sem rede."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLACAR = Path(__file__).resolve().parent.parent / "bin" / "forge-placar"
CAB_CONF = ("| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota | classe | autor |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n")
CAB_MELHORIAS = ("| ID | Hipótese | Mudança | Métrica | Critério de reversão | Início | Revisão | Resultado |\n"
                 "|---|---|---|---|---|---|---|---|\n")
PROPOSTA = ("| M-1 | o prevoo corta forma | código: trava no forge-check | taxa_forma prometido: -20% | sobe 2 semanas "
            "| 2026-11-08 | 2026-11-20 | |\n")


def vereditos(dia, aprovados, forma):
    """`aprovados` briefs aprovados (delegações) e `forma` reprovações de forma num dia."""
    linha = "| {} 10:00 | p | p-x-1 | brief | 1 | {} | s | nota | {} | jarvis |\n"
    return linha.format(dia, "aprovado", "—") * aprovados + linha.format(dia, "reprovado", "forma") * forma


class Prometido(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-prometido-"))
        self.addCleanup(shutil.rmtree, self.raiz, ignore_errors=True)

    def gravar(self, rel, texto):
        arq = self.raiz / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def rodar(self, *linhas, hoje="2026-11-15", conf=((10, 5), (10, 2)), extra=()):
        """Antes do Início (11-05) e depois dele (11-10): taxa_forma de 50% para 20% com o padrão, queda de 60%."""
        self.gravar("docs/kanban/melhorias.md", "# Experimentos\n\n" + CAB_MELHORIAS + "".join(linhas))
        if conf:
            self.gravar("docs/kanban/conferencias.md", CAB_CONF + vereditos("2026-11-05", *conf[0]) + vereditos("2026-11-10", *conf[1]))
        ambiente = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.raiz / "home")}
        r = subprocess.run([sys.executable, "-I", str(PLACAR), "propostas", "--hoje", hoje, "--raiz", str(self.raiz), *extra],
                           capture_output=True, text=True, env=ambiente, timeout=60)
        return r.returncode, r.stdout, r.stderr

    def test_real_medido_ao_lado_do_prometido(self):
        rc, saida, erro = self.rodar(PROPOSTA)
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("prometido: M-1 taxa_forma · prometido -20% · real -60%\n", saida)

    def test_json_traz_o_prometido_e_o_real(self):
        rc, saida, erro = self.rodar(PROPOSTA, extra=("--json",))
        self.assertEqual(rc, 0, erro)
        self.assertEqual(json.loads(saida)["prometidos"], [{"id": "M-1", "metrica": "taxa_forma", "prometido": -20.0, "real": -60}])

    def test_janela_de_depois_aberta_sai_sem_medida(self):
        rc, saida, _ = self.rodar(PROPOSTA, hoje="2026-11-14")
        self.assertEqual(rc, 0, saida)
        self.assertIn("prometido: M-1 taxa_forma · prometido -20% · real sem medida\n", saida)

    def test_janela_que_fecha_no_dia_mede(self):
        self.assertIn("real -60%", self.rodar(PROPOSTA, hoje="2026-11-15")[1])

    def test_sem_fonte_sai_sem_medida(self):
        self.assertIn("real sem medida", self.rodar(PROPOSTA, conf=None)[1])

    def test_base_zero_sai_sem_medida(self):
        self.assertIn("real sem medida", self.rodar(PROPOSTA, conf=((10, 0), (10, 2)))[1])

    def test_metrica_fora_do_placar_nao_quebra_e_sai_sem_medida(self):
        rc, saida, erro = self.rodar(PROPOSTA.replace("taxa_forma prometido", "qualidade prometido"))
        self.assertEqual(rc, 1, saida + erro)
        self.assertIn("prometido: M-1 qualidade · prometido -20% · real sem medida\n", saida)
        self.assertNotIn("Traceback", erro)

    def test_prometido_sem_numero_e_falta(self):
        rc, saida, _ = self.rodar(PROPOSTA.replace("prometido: -20%", "prometido: muito"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("falta: M-1: prometido tem de ser um número em %", saida)
        self.assertNotIn("prometido: M-1", saida)

    def test_prometido_com_digitos_demais_e_falta_e_o_json_segue_estrito(self):
        """Centenas de dígitos virariam float inf e o --json sairia Infinity (achado A1 da segurança)."""
        rc, saida, erro = self.rodar(PROPOSTA.replace("prometido: -20%", "prometido: " + "9" * 400 + "%"), extra=("--json",))
        self.assertEqual(rc, 1, saida + erro)
        dados = json.loads(saida, parse_constant=lambda c: self.fail(f"--json com {c}"))
        self.assertEqual(dados["prometidos"], [])
        self.assertTrue(any(f.startswith("M-1: prometido tem de ser um número em %") for f in dados["faltas"]), dados)

    def test_prometido_de_seis_digitos_ainda_vale(self):
        rc, saida, _ = self.rodar(PROPOSTA.replace("prometido: -20%", "prometido: -999999%"))
        self.assertEqual(rc, 0, saida)
        self.assertIn("prometido: M-1 taxa_forma · prometido -999999% · real -60%\n", saida)

    def test_proposta_sem_prometido_nao_ganha_a_linha(self):
        rc, saida, _ = self.rodar(PROPOSTA.replace(" prometido: -20%", ""), extra=("--json",))
        self.assertEqual(rc, 0, saida)
        self.assertEqual(json.loads(saida)["prometidos"], [])

    def test_so_a_janela_de_antes_sem_medida_sai_sem_medida(self):
        """pronto_ate_develop só com item mesclado depois do Início: antes sem medida, depois com 60 min."""
        self.gravar("docs/pedidos/p.md", "# p\n\n## Histórico\n- 2026-11-10 10:00: entrega conferida " + "a" * 40
                    + "\n- 2026-11-10 11:00: PR mesclado na develop\n")
        linha = PROPOSTA.replace("taxa_forma prometido", "pronto_ate_develop prometido")
        rc, saida, erro = self.rodar(linha)
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("prometido: M-1 pronto_ate_develop · prometido -20% · real sem medida\n", saida)

    def test_proposta_sem_id_sai_com_interrogacao(self):
        rc, saida, _ = self.rodar(PROPOSTA.replace("| M-1 |", "|  |"), extra=("--json",))
        self.assertEqual(json.loads(saida)["prometidos"][0]["id"], "?", saida)

    def test_decimal_com_virgula_e_ganho_que_sobe(self):
        linha = PROPOSTA.replace("prometido: -20%", "prometido: +2,5%")
        rc, saida, _ = self.rodar(linha, conf=((10, 2), (10, 4)))
        self.assertEqual(rc, 0, saida)
        self.assertIn("prometido: M-1 taxa_forma · prometido +2.5% · real +100%\n", saida)


if __name__ == "__main__":
    unittest.main()
