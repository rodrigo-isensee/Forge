"""N-FECHAR-a, A6: `bin/forge-fechar` confere o sha da branch local antes de remover a worktree.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
SCRIPT = base.SCRIPT


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    setUp = base.Fechar.setUp
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    com_worktree = base.Fechar.com_worktree
    resumo = base.Fechar.resumo
    marcas = base.Fechar.marcas

    # ---- N-FECHAR-a, A6: o sha da branch é conferido antes de remover a worktree ----
    def test_c3_branch_com_commit_novo_deixa_a_worktree_e_os_arquivos_ignorados(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")  # PR antigo mesclado com o nome reaproveitado
        wt = self.com_worktree()
        (self.proj / ".git" / "info" / "exclude").write_text("*.local\n")
        (wt / "ambiente.local").write_text("conteudo que so existe aqui\n")
        (wt / "novo").write_text("trabalho novo\n")
        self.git("add", "novo", cwd=wt)
        self.git("commit", "-q", "-m", "feat: trabalho novo", cwd=wt)
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.assertEqual(self.marcas("git worktree remove"), [])
        self.assertEqual((wt / "ambiente.local").read_text(), "conteudo que so existe aqui\n")
        self.assertIn("não removi a worktree", r.stderr)
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "+ melhoria/x")

    def test_c3_branch_no_sha_mesclado_continua_removendo_a_worktree(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        self.com_worktree()
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertEqual(len(self.marcas("git worktree remove")), 1)


if __name__ == "__main__":
    unittest.main()
