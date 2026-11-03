"""L02 (D-1): o autor abre o PR em rascunho na entrega; o `forge-fechar` reusa o PR aberto do mesmo head e só depois dos passos de
parecer, checks e rótulo roda `gh pr ready`, preso ao head conferido (C-02a a C-02c do modelo de ameaças do lote-unico-032).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class RascunhoDaEntrega(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    criacoes = base.Fechar.criacoes
    merges = base.Fechar.merges
    setUp = base.Fechar.setUp

    def prontos(self):
        return [c for c in self.chamadas() if c.startswith("gh pr ready")]

    def test_rascunho_do_mesmo_head_e_reusado_e_vira_pronto_antes_do_merge(self):
        (self.estado / "aberto").write_text("9 develop\n")
        (self.estado / "pre").write_text("develop true\n")
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("PR #9 já aberto; reusado.", r.stdout)
        self.assertEqual(self.criacoes(), [])
        chamadas = self.chamadas()
        self.assertEqual(self.prontos(), ["gh pr ready melhoria/x"])
        iprd = chamadas.index("gh pr ready melhoria/x")
        self.assertLess(max(i for i, c in enumerate(chamadas) if c.startswith("gh pr checks 9")), iprd)
        self.assertEqual(chamadas[iprd + 1], f"gh pr merge melhoria/x --squash --match-head-commit {sha}")

    def test_rascunho_com_head_diferente_do_conferido_para_no_passo_3(self):
        (self.estado / "aberto").write_text("9 develop\n")
        (self.estado / "pre").write_text("develop true\n")
        (self.estado / "aberto_head").write_text("0" * 40)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 3", r.stderr)
        self.assertIn("não o conferido", r.stderr)
        self.assertEqual(self.prontos(), [])
        self.assertEqual(self.merges(), [])
        self.assertFalse(any(c.startswith("gh pr checks") for c in self.chamadas()))

    def test_dois_prs_abertos_do_mesmo_head_param_no_passo_3(self):
        (self.estado / "aberto").write_text("9 develop\n10 develop\n")
        (self.estado / "pre").write_text("develop true\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 3", r.stderr)
        self.assertIn("2 PRs abertos", r.stderr)
        self.assertEqual(self.prontos(), [])
        self.assertEqual(self.merges(), [])


if __name__ == "__main__":
    unittest.main()
