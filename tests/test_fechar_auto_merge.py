"""R7 / MERGE-LIBERADO (0.43.3): o passo 6 do forge-fechar usa o auto-merge do GitHub (`gh pr merge --auto`, preso ao head),
espera o MERGED até --espera e, com --armar, arma o merge sem esperar os checks e sai com código 4.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class AutoMerge(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    setUp = base.Fechar.setUp

    def merges(self):
        return [c for c in self.chamadas() if c.startswith("gh pr merge")]

    def test_merge_e_o_auto_merge_preso_ao_head_e_nunca_admin(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}"])
        codigo = [l for l in base.SCRIPT.read_text().splitlines() if '"$gh" pr merge' in l and not l.lstrip().startswith("#")]
        self.assertEqual(len(codigo), 1, codigo)
        self.assertIn("--auto", codigo[0])
        self.assertNotIn("--admin", base.SCRIPT.read_text().replace("nunca --admin", ""))

    def test_armado_espera_o_github_mesclar_e_fecha(self):
        (self.estado / "auto_arma").write_text("")
        (self.estado / "mescla_apos").write_text("3")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)
        self.assertEqual(len(self.merges()), 1, "o merge não se repete na espera")

    def test_armado_que_nao_mescla_no_prazo_para_sem_limpar(self):
        (self.estado / "auto_arma").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6: o auto-merge está armado", r.stderr)
        self.assertNotIn("Entrega p1 fechada", r.stdout)
        self.assertFalse([c for c in self.chamadas() if "push origin --delete" in c or "branch -D" in c])

    def test_armar_nao_espera_os_checks_e_sai_com_codigo_4(self):
        (self.estado / "auto_arma").write_text("")
        (self.estado / "checks").write_text("bateria\tpending\t1m\turl\n")  # CI ainda rodando: o --armar não espera
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--armar")
        self.assertEqual(r.returncode, 4, r.stderr + r.stdout)
        self.assertIn("auto-merge armado no PR #7", r.stdout)
        self.assertIn("forge-fechar p1 --ref melhoria/x --limpar", r.stdout)
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh pr checks")])
        self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}"])
        self.assertFalse([c for c in self.chamadas() if "push origin --delete" in c])

    def test_armar_ainda_recusa_rotulo_pedido_e_nao_aplicado(self):
        (self.estado / "texto").write_text("feat: afrouxa-regra no título\ncorpo\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--armar")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 5", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_armar_com_checks_ja_verdes_mescla_na_hora_e_limpa(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--armar")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)

    def test_armar_nao_combina_com_limpar_nem_com_esperar_rotulo(self):
        for extra in ("--limpar", "--esperar-rotulo"):
            with self.subTest(extra):
                r = self.fechar("p1", "--ref", "melhoria/x", "--armar", extra)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("não combinam", r.stderr)
                self.assertEqual(self.merges(), [])

    def test_dry_run_mostra_o_auto_merge(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("pr merge melhoria/x --auto --squash --match-head-commit", r.stdout)


if __name__ == "__main__":
    unittest.main()
