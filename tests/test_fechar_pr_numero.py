"""N-FECHAR-b, B3: as leituras do PR vão pelo número (lido no passo 3) e MERGED só vale com o head conferido, a base alvo e commit de merge.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class PrPorNumero(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    criacoes = base.Fechar.criacoes
    merges = base.Fechar.merges
    setUp = base.Fechar.setUp

    def leituras_de_pr(self):
        return [c for c in self.chamadas() if c.startswith("gh pr view")]

    def test_numero_do_pr_criado_vem_da_url_e_as_leituras_usam_o_numero(self):
        (self.estado / "numero_criado").write_text("12")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        leituras = self.leituras_de_pr()
        self.assertTrue(leituras)
        self.assertTrue(all(c.startswith("gh pr view 12 ") for c in leituras), leituras)
        self.assertTrue(any(c.startswith("gh pr checks 12") for c in self.chamadas()))

    def test_pr_reusado_usa_o_numero_do_pr_aberto(self):
        (self.estado / "aberto").write_text("9 develop\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.criacoes(), [])
        self.assertTrue(all(c.startswith("gh pr view 9 ") for c in self.leituras_de_pr()), self.leituras_de_pr())

    def test_o_merge_continua_por_nome_de_branch_com_o_head_preso(self):
        sha = self.git("rev-parse", "melhoria/x")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)
        self.assertIn(f"gh pr merge melhoria/x --squash --match-head-commit {sha}", self.chamadas())
        codigo = [l for l in base.SCRIPT.read_text().splitlines() if '"$gh" pr merge' in l and not l.lstrip().startswith("#")]
        self.assertTrue(codigo)
        for l in codigo:
            self.assertIn('"$ref"', l)
            self.assertIn("--match-head-commit", l)
            self.assertNotIn("$pr_n", l)

    def test_merged_de_outro_head_depois_do_merge_com_erro_nao_conta_como_sucesso(self):
        (self.estado / "merge_502_mas_mescla").write_text("")
        (self.estado / "head_final").write_text("0" * 40)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 6", r.stderr)
        self.assertNotIn("Entrega p1 fechada", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_merged_de_outro_head_sem_merge_com_erro_tambem_nao_conta(self):
        (self.estado / "estado").write_text("MERGED")
        (self.estado / "head_final").write_text("0" * 40)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 6", r.stderr)
        self.assertNotIn("Entrega p1 fechada", r.stdout)

    def test_merged_com_base_diferente_da_alvo_nao_conta(self):
        (self.estado / "base_final").write_text("homolog")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 6", r.stderr)

    def test_merged_sem_commit_de_merge_nao_conta(self):
        (self.estado / "merge_commit_vazio").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 6", r.stderr)

    def test_saida_do_create_sem_numero_para_com_a_mensagem_do_pr_criado(self):
        for saida in ("criado\n", "https://github.com/o/r/pull/abc\n", "https://github.com/o/r/pull/7\nhttps://github.com/o/r/pull/8\n",
                      "https://github.com/o/r/pull/\n", ""):
            with self.subTest(saida=saida):
                self.setUp()
                (self.estado / "saida_create").write_text(saida)
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("o PR foi criado, mas o número não foi lido; rode de novo", r.stderr)
                self.assertFalse(any(c.startswith(("gh pr view", "gh pr checks", "gh pr merge")) for c in self.chamadas()))

    def test_pr_aberto_de_fork_com_o_mesmo_nome_de_branch_para(self):
        (self.estado / "aberto").write_text("9 develop\n")
        (self.estado / "aberto_fork").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("isCrossRepository", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_pr_de_fork_visto_no_passo_6_para_antes_do_merge(self):
        (self.estado / "cross").write_text("true")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 6", r.stderr)
        self.assertIn("isCrossRepository", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_head_diferente_na_leitura_do_passo_6_para_antes_do_merge(self):
        # a conferência do head do PR contra o conferido no passo 2, antes do merge (pre_head): sem ela este teste fica vermelho
        (self.estado / "head").write_text("0" * 40)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 6", r.stderr)
        self.assertIn("difere do conferido", r.stderr)
        self.assertEqual(self.merges(), [])


if __name__ == "__main__":
    unittest.main()
