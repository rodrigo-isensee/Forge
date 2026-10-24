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
        self.assertEqual(self.chamadas()[0], f"forge-check pr p1 --ref {sha} --base origin/develop")

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
        self.assertIn(f"gh pr merge melhoria/x --squash --match-head-commit {sha}", self.chamadas())
        self.assertIn(f"head: {sha}", r.stdout)


if __name__ == "__main__":
    unittest.main()
