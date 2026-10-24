"""FECHAR-MASTER: `bin/forge-fechar` recusa `--ref` de branch longa antes de qualquer ação (sonda do QA da LIMPEZA-REGRA, A1/CT-05)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    estado_do_repo = base.Fechar.estado_do_repo

    def setUp(self):
        base.Fechar.setUp(self)

    def cria_branch_local(self, nome):
        self.git("branch", nome)
        self.git("push", "-q", "origin", nome)

    def recusa(self, ref, *extra):
        antes = self.git("branch", "-a")
        r = self.fechar("p1", "--ref", ref, *extra)
        self.assertNotEqual(r.returncode, 0, f"{ref} {extra}: {r.stdout}")
        self.assertIn("branch da entrega não pode ser", r.stderr)
        self.assertEqual(self.git("branch", "-a"), antes, ref)
        self.assertEqual(self.chamadas(), [], ref)

    def test_branches_longas_fixas_sao_recusadas_com_e_sem_limpar(self):
        for ref in ("main", "master", "develop", "homolog"):
            if ref != "develop":
                self.cria_branch_local(ref)
            self.recusa(ref)
            self.recusa(ref, "--limpar")

    def test_branch_de_integracao_do_claude_md_e_recusada(self):
        (self.proj / "CLAUDE.md").write_text("# Projeto\n\n- Branch de integração: `trunk`\n", encoding="utf-8")
        self.cria_branch_local("trunk")
        self.recusa("trunk")
        self.recusa("trunk", "--limpar")

    def test_sem_a_linha_no_claude_md_branch_de_trabalho_segue_valida(self):
        (self.proj / "CLAUDE.md").write_text("# Projeto\n\nsem a linha\n", encoding="utf-8")
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_claude_md_com_a_linha_nao_barra_a_branch_de_trabalho(self):
        (self.proj / "CLAUDE.md").write_text("- Branch de integração: `trunk`\n", encoding="utf-8")
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
