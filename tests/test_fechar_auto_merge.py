"""FECHAR-SEM-AUTO-MERGE (decisão do dono de 21/11: merge automático proibido em qualquer PR): o passo 6 e o P6 do `bin/forge-fechar`
mesclam direto, preso ao head (`gh pr merge <branch> --squash|--merge --match-head-commit <sha>`), só depois de todo check-run obrigatório
do head verde (a catraca incluída): falha terminada para; pendente espera e relê logo antes do merge. O `--armar` recusa, com o porquê e o
comando certo, sem nada feito. O `gh` falso de `test_fechar` recusa (código 65) e registra todo `gh pr merge` com `--auto`, então qualquer
teste do forge-fechar que caia num merge automático fica vermelho.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

RECUSA_ARMAR = "--armar recusado: o merge automático é proibido pelo dono (FECHAR-SEM-AUTO-MERGE"


class SemAutoMerge(unittest.TestCase):
    setUp, tearDown, git, fechar = base.Fechar.setUp, base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar
    chamadas, merges = base.Fechar.chamadas, base.Fechar.merges

    def leituras_dos_check_runs(self):
        return [c for c in self.chamadas() if c.startswith("gh api repos/{owner}/{repo}/commits/")]

    def assert_sem_auto(self):
        self.assertFalse([c for c in self.chamadas() if " --auto" in c or c == "merge automático recusado"], self.chamadas())

    def test_merge_direto_preso_ao_head_sem_auto_nem_admin(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)
        self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --squash --match-head-commit {sha}"])
        self.assert_sem_auto()
        # o merge vem depois da última leitura dos check-runs do head (a conferência logo antes)
        chamadas = self.chamadas()
        self.assertLess(chamadas.index(self.leituras_dos_check_runs()[-1]), chamadas.index(self.merges()[0]))

    def test_armar_recusa_com_o_porque_e_o_comando_certo_sem_nada_feito(self):
        sha = self.git("rev-parse", "melhoria/x")
        casos = (("p1", "--ref", "melhoria/x", "--armar"), ("p1", "--armar", "--ref", "melhoria/x", "--dry-run"),
                 ("p1", "--ref", "melhoria/x", "--armar", "--limpar"), ("p1", "--ref", "melhoria/x", "--armar", "--esperar-rotulo"),
                 ("--lote", "p1:melhoria/x", "p2:melhoria/y", "--armar"), ("release-0.9.0", "--promover", sha, "--armar"))
        for args in casos:
            with self.subTest(args=args):
                self.registro.write_text("")
                r = self.fechar(*args)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn(RECUSA_ARMAR, r.stderr)
                self.assertIn("Rode sem ele: forge-fechar <pedido> --ref <branch>", r.stderr)
                self.assertEqual(self.chamadas(), [], "nada roda com o --armar")

    def test_check_run_pendente_espera_e_relê_antes_do_merge(self):
        (self.estado / "check_runs_pendentes").write_text("2")  # a catraca ainda rodando nas 2 primeiras leituras
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.leituras_dos_check_runs()), 3)
        self.assertIn(f"check-runs do head {sha[:12]}: espero catraca (in_progress/-)", r.stdout)
        self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --squash --match-head-commit {sha}"])
        self.assert_sem_auto()

    def test_check_run_pendente_no_fim_do_prazo_para_sem_merge(self):
        (self.estado / "check_runs_pendentes").write_text("99")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6: o check obrigatório catraca do head", r.stderr)
        self.assertIn("(lida: in_progress/-) após 0s; nada foi mesclado", r.stderr)
        self.assertEqual(self.merges(), [])
        self.assertFalse([c for c in self.chamadas() if "push origin --delete" in c or "branch -D" in c])

    def test_merged_atrasado_espera_e_fecha_sem_repetir_o_merge(self):
        (self.estado / "merged_apos").write_text("3")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)
        self.assertEqual(len(self.merges()), 1, "o merge não se repete na espera")

    def test_merge_que_nao_consta_merged_no_prazo_para_sem_limpar(self):
        (self.estado / "merged_apos").write_text("99")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6: o merge direto foi pedido, mas o PR #7 não consta MERGED após 0s", r.stderr)
        self.assertNotIn("Entrega p1 fechada", r.stdout)
        self.assertFalse([c for c in self.chamadas() if "push origin --delete" in c or "branch -D" in c])
        self.assert_sem_auto()

    def test_dry_run_mostra_o_merge_direto(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("pr merge melhoria/x --squash --match-head-commit <head conferido> (merge direto, nunca automático", r.stdout)
        self.assertIn("check-runs obrigatórios do head verdes", r.stdout)
        self.assertNotIn("--auto", r.stdout)

    def test_ajuda_sem_merge_automatico(self):
        r = self.fechar("--help")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("--auto", r.stdout)
        self.assertIn("--armar: recusado", r.stdout)
        self.assertIn("FECHAR-SEM-AUTO-MERGE", r.stdout)


if __name__ == "__main__":
    unittest.main()
