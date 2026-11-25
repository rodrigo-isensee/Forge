"""v0481 E13.1: o fechamento sem segunda rodada.

FECHAR-CI-TOPO: o CI do push no merge cancelado porque a develop andou não sai com 5; decide o CI do topo que contém o merge (vermelho
de verdade continua 5). FECHAR-COPIA-CERTA: rodado da cópia principal na própria branch, para antes do passo 1 e diz de onde rodar.
O caso da branch local que falta (FECHAR-CRIA-BRANCH) fica em `test_fechar_sha_conferido.SoBranchRemota`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh`, `git` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

MERGE = "0123456789abcdef0123456789abcdef01234567"  # o mergeCommit que o gh falso devolve
TOPO = "89abcdef0123456789abcdef0123456789abcdef"  # o topo da develop depois de outro item


class Ambiente(unittest.TestCase):
    setUp, tearDown, git, fechar, chamadas = (base.Fechar.setUp, base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar,
                                              base.Fechar.chamadas)

    def runs_de(self, sha):
        return [c for c in self.chamadas() if c.startswith(f"gh run list --branch develop --event push --commit {sha} ")]


class CiDoTopo(Ambiente):
    def merge_cancelado_e_develop_andou(self, status="ahead", ci_do_topo="1\tcompleted\tsuccess\n"):
        (self.estado / f"runs_{MERGE}").write_text("93\tcompleted\tcancelled\n")
        (self.estado / "topo_apos_merge").write_text(TOPO)
        (self.estado / f"compare_{MERGE}_{TOPO}").write_text(status + "\n")
        (self.estado / f"runs_{TOPO}").write_text(ci_do_topo)
        return self.fechar("p1", "--ref", "melhoria/x")

    def test_topo_verde_que_contem_o_merge_fecha_com_0(self):
        r = self.merge_cancelado_e_develop_andou()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"decide o CI do topo {TOPO[:7]}, que contém o merge", r.stdout)
        self.assertIn(f"CI do push na develop verde no {TOPO[:7]}.", r.stdout)
        self.assertTrue(self.runs_de(TOPO))

    def test_topo_identico_ao_merge_tambem_decide(self):
        r = self.merge_cancelado_e_develop_andou(status="identical")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_topo_vermelho_continua_5_com_a_reversao_do_merge(self):
        r = self.merge_cancelado_e_develop_andou(ci_do_topo="94\tcompleted\tfailure\n")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn(f"aviso: a develop está vermelha no {TOPO[:7]} (run 94 failure)", r.stderr)
        self.assertIn(f"git revert --no-edit {MERGE} ", r.stderr)

    def test_topo_que_nao_contem_o_merge_fica_cancelado(self):
        r = self.merge_cancelado_e_develop_andou(status="diverged")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn(f"o CI do push na develop no {MERGE[:7]} foi cancelado", r.stderr)
        self.assertEqual(self.runs_de(TOPO), [])

    def test_topo_que_nao_andou_fica_cancelado(self):
        (self.estado / f"runs_{MERGE}").write_text("93\tcompleted\tcancelled\n")
        (self.estado / "topo_apos_merge").write_text(MERGE)
        (self.estado / f"compare_{MERGE}_{MERGE}").write_text("identical\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("foi cancelado", r.stderr)
        self.assertEqual(len(self.runs_de(MERGE)), 1)


class CopiaCerta(Ambiente):
    def test_copia_principal_na_branch_para_antes_do_passo_1(self):
        self.git("switch", "-q", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(f"parou antes do passo 1: a cópia {self.proj.resolve()} está na branch melhoria/x", r.stderr)
        self.assertIn("bin/forge-copia clone <pasta> --base origin/develop", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_worktree_ligada_na_branch_nao_e_a_copia_principal(self):
        wt = self.tmp / "wt-x"
        self.git("worktree", "add", "-q", str(wt), "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertNotIn("parou antes do passo 1", r.stderr)


if __name__ == "__main__":
    unittest.main()
