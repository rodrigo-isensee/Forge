"""FECHAR-REF-POR-NOME: com a branch local, o `forge-check pr` recebe o nome da branch (não o sha), para ler os pareceres da branch; o
sha conferido segue preso na cadeia (head relido, remoto, `--match-head-commit`). Só a branch no origin, sem a local, segue pelo sha."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar_sha_conferido as sc  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class FecharRefPorNome(unittest.TestCase):
    tearDown, git, fechar, chamadas = sc.FecharShaConferido.tearDown, sc.FecharShaConferido.git, sc.FecharShaConferido.fechar, sc.FecharShaConferido.chamadas
    setUp, commit_na_branch = sc.FecharShaConferido.setUp, sc.FecharShaConferido.commit_na_branch

    def test_com_branch_local_o_forge_check_recebe_o_nome(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.chamadas()[0], "forge-check pr p1 --ref refs/heads/melhoria/x --base origin/develop")
        self.assertIn(f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}", self.chamadas())

    def test_tag_de_mesmo_nome_nao_desvia_a_conferencia(self):
        sha_branch = self.git("rev-parse", "refs/heads/melhoria/x")
        tag_sha = self.git("rev-parse", "develop")
        self.git("tag", "melhoria/x", tag_sha)
        self.assertEqual(self.git("rev-parse", "melhoria/x"), tag_sha)  # o nome curto já casa a tag
        self.assertNotEqual(sha_branch, tag_sha)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.chamadas()[0], "forge-check pr p1 --ref refs/heads/melhoria/x --base origin/develop")
        self.assertIn(f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha_branch}", self.chamadas())

    def test_dry_run_descreve_o_nome(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pr p1 --ref refs/heads/melhoria/x --base", r.stdout)

    def test_head_que_anda_durante_a_conferencia_ainda_para(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_ANTES=self.commit_na_branch(True))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("mudou", r.stderr)

    def test_sem_branch_local_segue_pelo_sha_do_servidor(self):
        sha = self.git("rev-parse", "melhoria/x")
        self.git("branch", "-q", "-D", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertIn(r.returncode, (0, 3), r.stderr + r.stdout)
        self.assertEqual(self.chamadas()[0], f"forge-check pr p1 --ref {sha} --base origin/develop")


if __name__ == "__main__":
    unittest.main()
