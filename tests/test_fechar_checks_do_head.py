"""FECHAR-CHECKS-ANTES-DO-MERGE (v0478): antes do merge, o `bin/forge-fechar` lê os check-runs do head conferido e, por nome de `bateria`,
`bateria (python 3.14)` e `catraca`, julga só a execução mais recente (id maior; E75.6). No merge direto, recusa se ela falta ou não está em
completed/success (a conta do dono passaria pelo bypass do ruleset): terminada fora de success para; rodando ou ausente espera até
--espera e relê (FECHAR-SEM-AUTO-MERGE; aqui com --espera 0, sem espera). O --armar recusa (test_fechar_sem_auto_merge).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

# a saída do --jq do script: nome, id, status, conclusão
VERDES = ["bateria\t11\tcompleted\tsuccess", "bateria (python 3.14)\t12\tcompleted\tsuccess", "catraca\t13\tcompleted\tsuccess"]
JQ = '--jq .check_runs[] | [.name, .id, .status, (.conclusion // "-")] | @tsv'


class FecharChecksDoHead(unittest.TestCase):
    setUp, tearDown, git, fechar = base.Fechar.setUp, base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar
    chamadas, merges = base.Fechar.chamadas, base.Fechar.merges

    def runs(self, linhas):
        (self.estado / "check_runs").write_text("".join(f"{l}\n" for l in linhas))

    def leituras(self):
        return [c for c in self.chamadas() if c.startswith("gh api repos/{owner}/{repo}/commits/")]

    def assert_recusou(self, r, texto):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(texto, r.stderr)
        self.assertEqual(self.merges(), [])
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh pr ready")])

    def test_check_runs_verdes_leem_o_head_conferido_e_mesclam(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.leituras(), [f"gh api repos/{{owner}}/{{repo}}/commits/{sha}/check-runs?filter=latest&per_page=100 {JQ}"])
        self.assertIn(f"check-runs obrigatórios do head {sha[:12]} verdes", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_exigido_vermelho_rodando_ou_ausente_recusa_o_merge(self):
        casos = {
            "catraca": ([*VERDES[:2], "catraca\t13\tcompleted\tfailure"], "terminou em failure na execução mais recente"),
            "bateria": (["bateria\t11\tin_progress\t-", *VERDES[1:]], "não está verde (completed/success)"),
            "bateria (python 3.14)": ([VERDES[0], VERDES[2]], "não está verde (completed/success)"),
        }
        for nome, (linhas, texto) in casos.items():
            with self.subTest(nome=nome):
                self.setUp()
                self.runs(linhas)
                r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
                self.assert_recusou(r, f"o check obrigatório {nome} do head")
                self.assertIn(texto, r.stderr)

    def test_nome_mais_longo_verde_nao_vale_pelo_exigido(self):
        self.runs(VERDES[1:])  # só `bateria (python 3.14)`: a `bateria` não está entre os check-runs
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x", "--espera", "0"), "o check obrigatório bateria do head")

    def test_rotulo_aplicado_catraca_velha_cancelled_e_nova_verde_mescla(self):
        # E75.6 (A2 do review): a forma real do PR 745; o filter=latest devolve as duas suítes da catraca, em qualquer ordem
        velha = "catraca\t7\tcompleted\tcancelled"
        for ordem in ([velha, *VERDES], [*VERDES, velha]):
            with self.subTest(velha_primeiro=ordem[0] == velha):
                self.setUp()
                self.runs(ordem)
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
                self.assertIn("check-runs obrigatórios do head", r.stdout)
                self.assertEqual(len(self.merges()), 1)

    def test_execucao_mais_nova_com_falha_recusa_mesmo_com_a_velha_verde(self):
        for ordem in ([*VERDES, "catraca\t20\tcompleted\tfailure"], ["catraca\t20\tcompleted\tfailure", *VERDES]):
            with self.subTest(nova_primeiro=ordem[0].endswith("failure")):
                self.setUp()
                self.runs(ordem)
                self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "o check obrigatório catraca do head")

    def test_rodando_ou_ausente_espera_e_para_no_prazo_sem_merge(self):
        # FECHAR-SEM-AUTO-MERGE: o pendente não arma nada; espera até --espera (aqui 0) e para, sem merge
        for nome, linhas in {"rodando": [*VERDES[:2], "catraca\t13\tqueued\t-"], "ausente": VERDES[:2]}.items():
            with self.subTest(caso=nome):
                self.setUp()
                self.runs(linhas)
                r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
                self.assert_recusou(r, "o check obrigatório catraca do head")
                self.assertIn(f"(lida: {'queued/-' if nome == 'rodando' else 'ausente'}) após 0s; nada foi mesclado", r.stderr)
                self.assertEqual(len(self.leituras()), 1)

    def test_terminado_com_falha_recusa_sem_esperar(self):
        # E75.6 (A1 da segurança): a execução mais recente terminada fora de success para na hora, mesmo com prazo
        for conclusao in ("failure", "cancelled", "timed_out"):
            with self.subTest(conclusao=conclusao):
                self.setUp()
                self.runs(["catraca\t5\tcompleted\tsuccess", *VERDES[:2], f"catraca\t13\tcompleted\t{conclusao}"])
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assert_recusou(r, "o check obrigatório catraca do head")
                self.assertIn(f"terminou em {conclusao} na execução mais recente; nada foi mesclado", r.stderr)
                self.assertEqual(len(self.leituras()), 1)

    def test_leitura_dos_check_runs_que_falha_para(self):
        (self.estado / "falha_check_runs").write_text("3")
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "não consegui ler os check-runs do head")


if __name__ == "__main__":
    unittest.main()
