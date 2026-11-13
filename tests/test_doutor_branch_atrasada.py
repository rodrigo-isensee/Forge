"""ATUALIZAR-BRANCH-ATRASADA (decisão Q4 = A de 2026-11-03): numa branch longa, atrás da develop, o doutor explica o atraso e mostra o
cherry-pick do commit da versão (`bin/forge-doutor`); a recusa de árvore suja do `forge-upgrade` continua.

Reaproveita o ambiente de `test_doutor.Base` (projeto temporário com origin, `gh` falso e HOME próprio).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_doutor as td  # noqa: E402  (o módulo, não as classes: as de teste seriam coletadas de novo aqui)


class BranchAtrasada(td.Base):
    def setUp(self):
        super().setUp()
        # a branch longa nasce da develop na versão antiga; depois a develop registra a versão do plugin
        self.git("switch", "-q", "develop")
        self.escrever(".forge/versao", "0.0.1\n")
        self.git("commit", "-q", "-am", "chore(forge): registra versão 0.0.1")
        self.git("switch", "-q", "-c", "trabalho")
        self.escrever("a.txt", "trabalho\n")
        self.git("add", "a.txt")
        self.git("commit", "-q", "-m", "feat: trabalho longo")
        self.git("switch", "-q", "develop")
        self.escrever(".forge/versao", td.VERSAO + "\n")
        self.git("commit", "-q", "-am", f"chore(forge): registra versão {td.VERSAO}")
        self.commit_versao = self.git("rev-parse", "HEAD")
        self.escrever("b.txt", "depois\n")
        self.git("add", "b.txt")
        self.git("commit", "-q", "-m", "feat: depois da versão")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "trabalho")

    def test_branch_atras_da_develop_mostra_o_cherry_pick_do_commit_da_versao(self):
        r = self.doutor("--rapido")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("a branch está atrás da develop", r.stdout)
        self.assertIn(f"git cherry-pick {self.commit_versao}", r.stdout)
        self.assertIn("forge-upgrade` continua pedindo a árvore limpa", r.stdout)

    def test_depois_do_cherry_pick_a_versao_fica_em_ordem(self):
        self.git("cherry-pick", self.commit_versao)
        r = self.doutor("--rapido")
        self.assertNotIn("cherry-pick", r.stdout)
        self.assertNotIn(".forge/versao", r.stdout)
        self.assertNotIn("forge-upgrade", r.stdout)

    def test_versao_antiga_com_o_commit_da_develop_ja_na_branch_volta_ao_conselho_de_sempre(self):
        self.git("merge", "-q", "--no-edit", "origin/develop")
        self.escrever(".forge/versao", "0.0.2\n")  # o arquivo andou para trás depois do merge: o commit da develop já está aqui
        r = self.doutor("--rapido")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("cherry-pick", r.stdout)
        self.assertIn("forge-upgrade --simular", r.stdout)

    def test_develop_tambem_antiga_nao_fala_de_atraso(self):
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")  # a develop lida (sem fetch) na versão antiga da branch
        r = self.doutor("--rapido")
        self.assertNotIn("cherry-pick", r.stdout)
        self.assertIn("forge-upgrade --simular", r.stdout)

    def test_develop_com_a_mesma_versao_noutro_commit_que_falta_na_branch_nao_fala_de_atraso(self):
        # só versão maior que a da branch é atraso: o commit da develop que grava a mesma versão não vira cherry-pick
        self.git("switch", "-q", "develop")
        self.escrever(".forge/versao", "0.0.1\n")
        self.git("commit", "-q", "-am", "chore(forge): volta à versão 0.0.1")
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.git("switch", "-q", "trabalho")
        r = self.doutor("--rapido")
        self.assertNotIn("cherry-pick", r.stdout)
        self.assertIn("forge-upgrade --simular", r.stdout)

    def test_sem_a_origin_develop_local_nao_adivinha(self):
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        r = self.doutor("--rapido")
        self.assertNotIn("cherry-pick", r.stdout)
        self.assertIn("forge-upgrade --simular", r.stdout)


if __name__ == "__main__":
    unittest.main()
