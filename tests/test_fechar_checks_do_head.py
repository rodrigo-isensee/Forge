"""FECHAR-CHECKS-ANTES-DO-MERGE (v0478): antes do merge, o `bin/forge-fechar` lê os check-runs do head conferido e recusa se `bateria`,
`bateria (python 3.14)` ou `catraca` não estiver em completed/success (a conta do dono passaria pelo bypass do ruleset); só no merge
direto: com --armar, arma como antes (E75.2).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

VERDES = ["bateria\tcompleted\tsuccess", "bateria (python 3.14)\tcompleted\tsuccess", "catraca\tcompleted\tsuccess"]


class FecharChecksDoHead(unittest.TestCase):
    setUp, tearDown, git, fechar = base.Fechar.setUp, base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar
    chamadas, merges = base.Fechar.chamadas, base.Fechar.merges

    def runs(self, linhas):
        (self.estado / "check_runs").write_text("".join(f"{l}\n" for l in linhas))

    def assert_recusou(self, r, texto):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(texto, r.stderr)
        self.assertEqual(self.merges(), [])
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh pr ready")])

    def test_check_runs_verdes_leem_o_head_conferido_e_mesclam(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        leituras = [c for c in self.chamadas() if c.startswith("gh api repos/{owner}/{repo}/commits/")]
        self.assertEqual(leituras, [f"gh api repos/{{owner}}/{{repo}}/commits/{sha}/check-runs?filter=latest&per_page=100 "
                                    '--jq .check_runs[] | [.name, .status, (.conclusion // "-")] | @tsv'])
        self.assertIn(f"check-runs obrigatórios do head {sha[:12]} verdes", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_exigido_vermelho_rodando_ou_ausente_recusa_o_merge(self):
        casos = {
            "catraca": [*VERDES[:2], "catraca\tcompleted\tfailure"],
            "bateria": ["bateria\tin_progress\t-", *VERDES[1:]],
            "bateria (python 3.14)": [VERDES[0], VERDES[2]],
        }
        for nome, linhas in casos.items():
            with self.subTest(nome=nome):
                self.setUp()
                self.runs(linhas)
                self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), f"o check obrigatório {nome} do head")

    def test_nome_mais_longo_verde_nao_vale_pelo_exigido(self):
        self.runs(VERDES[1:])  # só `bateria (python 3.14)`: a `bateria` não está entre os check-runs
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "o check obrigatório bateria do head")

    def test_duplicata_do_exigido_precisa_de_todas_verdes(self):
        self.runs([*VERDES, "catraca\tcompleted\tcancelled"])
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "o check obrigatório catraca do head")

    def test_com_armar_e_check_rodando_arma(self):
        # E75.2: o --armar arma antes do CI terminar (o auto-merge espera os obrigatórios); a recusa por check vale só no merge direto
        (self.estado / "auto_arma").write_text("")
        self.runs([*VERDES[:2], "catraca\tqueued\t-"])
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--armar")
        self.assertEqual(r.returncode, 4, r.stderr + r.stdout)
        self.assertIn("auto-merge armado no PR #7", r.stdout)
        self.assertNotIn("o check obrigatório", r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh api repos/{owner}/{repo}/commits/")])
        self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}"])

    def test_leitura_dos_check_runs_que_falha_para(self):
        (self.estado / "falha_check_runs").write_text("3")
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"), "não consegui ler os check-runs do head")


if __name__ == "__main__":
    unittest.main()
