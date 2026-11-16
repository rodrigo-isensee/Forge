"""N-FECHAR-b, B5: o parecer é conferido no mesmo sha que o remoto tem e que vai ao merge (parecer em X, remoto = X, merge com X).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele. O
`forge-check` falso ganha aqui, só para estes testes, o gancho `CHECK_ANTES`: comando que simula o que outro agente faz na branch
enquanto o `forge-check` lê.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

CHECK_COM_GANCHO = ('#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\n'
                    '[ -z "${CHECK_ANTES:-}" ] || eval "$CHECK_ANTES"\n'
                    'exit "${CHECK_RC:-0}"\n')


class FecharShaConferido(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    criacoes = base.Fechar.criacoes

    def setUp(self):
        base.Fechar.setUp(self)
        (self.tmp / "check").write_text(CHECK_COM_GANCHO, encoding="utf-8")

    def commit_na_branch(self, empurra):
        proj = str(self.proj)
        comando = f"git -C '{proj}' switch -q melhoria/x && git -C '{proj}' commit -q --allow-empty -m 'feat: outro agente'"
        return comando + (f" && git -C '{proj}' push -q origin melhoria/x" if empurra else "")

    def test_o_forge_check_roda_no_sha_conferido_e_nao_no_nome_da_branch(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.chamadas()[0], "forge-check pr p1 --ref refs/heads/melhoria/x --base origin/develop")

    def test_commit_local_empurrado_durante_o_passo_1_para_sem_abrir_pr(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_ANTES=self.commit_na_branch(True))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 1", r.stderr)
        self.assertIn("mudou", r.stderr)
        self.assertEqual(self.criacoes(), [])
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_commit_local_sem_push_durante_o_passo_1_para(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_ANTES=self.commit_na_branch(False))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("mudou", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_o_merge_segue_preso_ao_mesmo_sha_do_parecer(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "head").write_text(sha)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}", self.chamadas())
        self.assertIn(f"head: {sha}", r.stdout)


class SoBranchRemota(unittest.TestCase):
    """FECHAR-BRANCH-LOCAL (0.43.2): `--ref` vale com a branch só no origin; o sha conferido vem do servidor (ls-remote), não da
    refs/remotes/origin, e a cadeia única (parecer, servidor e --match-head-commit no mesmo sha) continua."""

    tearDown, git, fechar = FecharShaConferido.tearDown, FecharShaConferido.git, FecharShaConferido.fechar
    chamadas, criacoes = FecharShaConferido.chamadas, FecharShaConferido.criacoes

    def setUp(self):
        FecharShaConferido.setUp(self)
        self.sha = self.git("rev-parse", "melhoria/x")
        self.git("branch", "-q", "-D", "melhoria/x")

    def envia_outro_commit(self, de=None):
        """Comando que põe outro commit no melhoria/x do servidor a partir de uma cópia `de` (padrão: o próprio projeto)."""
        pasta = str(de or self.proj)
        return (f"git -C '{pasta}' switch -q -c outro-agente {self.sha} && git -C '{pasta}' commit -q --allow-empty -m 'feat: outro'"
                f" && git -C '{pasta}' push -q origin outro-agente:melhoria/x && git -C '{pasta}' switch -q develop")

    def test_branch_so_no_servidor_fecha_no_sha_do_servidor(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertIn(r.returncode, (0, 3), r.stderr + r.stdout)
        self.assertIn(f"sem a branch local melhoria/x; confiro o head do servidor ({self.sha})", r.stderr)
        self.assertEqual(self.chamadas()[0], f"forge-check pr p1 --ref {self.sha} --base origin/develop")
        self.assertIn(f"gh pr merge melhoria/x --auto --squash --match-head-commit {self.sha}", self.chamadas())

    def test_servidor_que_anda_no_passo_1_para(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_ANTES=self.envia_outro_commit())
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 1: o head de melhoria/x mudou", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_ref_de_rastreio_velha_nao_vale(self):
        self.git("update-ref", "refs/remotes/origin/melhoria/x", self.git("rev-parse", "develop"))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertIn(r.returncode, (0, 3), r.stderr + r.stdout)
        self.assertEqual(self.chamadas()[0], f"forge-check pr p1 --ref {self.sha} --base origin/develop")

    def test_commit_que_falta_aqui_pede_o_fetch(self):
        outra = self.tmp / "outra"
        self.git("clone", "-q", str(self.remoto), str(outra), cwd=self.tmp)
        self.git("-C", str(outra), "fetch", "-q", "origin", "melhoria/x")
        r0 = self.git("-C", str(outra), "rev-parse", "FETCH_HEAD")
        self.assertEqual(r0, self.sha)
        base.subprocess.run(["bash", "-c", self.envia_outro_commit(outra)], env=self.env, check=True, capture_output=True)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("rode git fetch origin melhoria/x", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_base_que_andou_com_conflito_para_sem_envio_nem_branch_local(self):  # E8: o fechamento não traz a base
        self.git("switch", "-q", "develop")
        (self.proj / "b").write_text("da base\n")
        self.git("add", "b")
        self.git("commit", "-q", "-m", "feat: base anda")
        self.git("push", "-q", "origin", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 2b: o merge de origin/develop em melhoria/x tem conflito", r.stderr)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/melhoria/x").split()[0], self.sha)
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")


if __name__ == "__main__":
    unittest.main()
