"""FECHAR-CHECKS-ANTES-DO-MERGE (v0478): antes do merge, o `bin/forge-fechar` lê os check-runs do head conferido e, por nome de `bateria`,
`bateria (python 3.14)` e `catraca`, julga só a execução mais recente (id maior; E75.6). No merge direto, recusa se ela falta ou não está em
completed/success (a conta do dono passaria pelo bypass do ruleset). Com --armar, recusa só a que já terminou fora de success; rodando ou
ausente, arma (E75.2 e E75.6).

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
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assert_recusou(r, f"o check obrigatório {nome} do head")
                self.assertIn(texto, r.stderr)

    def test_nome_mais_longo_verde_nao_vale_pelo_exigido(self):
        self.runs(VERDES[1:])  # só `bateria (python 3.14)`: a `bateria` não está entre os check-runs
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "o check obrigatório bateria do head")

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

    def test_com_armar_e_check_rodando_ou_ausente_arma(self):
        # E75.2: o --armar arma antes do CI terminar; rodando ou ainda sem execução não para (E75.6)
        for nome, linhas in {"rodando": [*VERDES[:2], "catraca\t13\tqueued\t-"], "ausente": VERDES[:2]}.items():
            with self.subTest(caso=nome):
                self.setUp()
                (self.estado / "auto_arma").write_text("")
                self.runs(linhas)
                sha = self.git("rev-parse", "melhoria/x")
                r = self.fechar("p1", "--ref", "melhoria/x", "--armar")
                self.assertEqual(r.returncode, 4, r.stderr + r.stdout)
                self.assertIn("auto-merge armado no PR #7", r.stdout)
                self.assertIn("sem falha terminada", r.stdout)
                self.assertNotIn("o check obrigatório", r.stderr)
                self.assertEqual(len(self.leituras()), 1)
                self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}"])

    def test_com_armar_e_check_terminado_com_falha_recusa(self):
        # E75.6 (A1 da segurança): o --auto da conta do dono mesclaria na hora pelo bypass
        for conclusao in ("failure", "cancelled", "timed_out"):
            with self.subTest(conclusao=conclusao):
                self.setUp()
                (self.estado / "auto_arma").write_text("")
                self.runs(["catraca\t5\tcompleted\tsuccess", *VERDES[:2], f"catraca\t13\tcompleted\t{conclusao}"])
                r = self.fechar("p1", "--ref", "melhoria/x", "--armar")
                self.assert_recusou(r, "o check obrigatório catraca do head")
                self.assertIn(f"terminou em {conclusao} na execução mais recente; nada foi mesclado nem armado", r.stderr)

    def test_leitura_dos_check_runs_que_falha_para(self):
        (self.estado / "falha_check_runs").write_text("3")
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "não consegui ler os check-runs do head")


if __name__ == "__main__":
    unittest.main()
