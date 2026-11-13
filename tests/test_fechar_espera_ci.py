"""FECHAR-ESPERA-CI-DEVELOP (passo 6c): depois do merge, o `forge-fechar` espera o CI do push na develop verde, seguindo o run do head
atual da develop (não o do sha do merge, que a concorrência cancela); vermelho, cancelado sem run mais novo, leitura que falha ou sem fim
até --espera saem com código 5, sem a limpeza. O `gh run list` falso lê `$ESTADO/runs` (ver GH_FALSO em test_fechar)."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as tf  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class FecharEsperaCi(unittest.TestCase):
    setUp, tearDown, git, chamadas = tf.Fechar.setUp, tf.Fechar.tearDown, tf.Fechar.git, tf.Fechar.chamadas

    def fechar(self, runs=None, *args):
        if runs is not None:
            (self.estado / "runs").write_text("".join(f"{r}\n" for r in runs))
        return subprocess.run(["bash", str(tf.SCRIPT), "p1", "--ref", "melhoria/x", *args], cwd=self.proj, env=self.env,
                              capture_output=True, text=True, timeout=30)

    def leituras_do_ci(self):
        return [c for c in self.chamadas() if c.startswith("gh run list")]

    def assert_parou(self, r, *trechos):
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("parou no passo 6c", r.stderr)
        for t in ("o merge em develop já foi feito", "prioridade máxima", "forge-fechar p1 --ref melhoria/x --limpar", *trechos):
            self.assertIn(t, r.stderr)
        self.assertIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))  # sem limpeza

    def test_verde_segue_o_head_atual_da_develop_e_limpa(self):
        cab = self.git("ls-remote", "origin", "refs/heads/develop").split()[0]
        r = self.fechar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.leituras_do_ci(), [
            f"gh run list --branch develop --event push --workflow ci.yml --commit {cab} --limit 1 --json databaseId,status,conclusion "
            '--jq .[] | "\\(.databaseId) \\(.status) \\(.conclusion)"'])
        self.assertIn(f"CI do push em develop verde: run 1 (head {cab[:7]})", r.stdout)
        self.assertLess(r.stdout.index("[6c]"), r.stdout.index("[7]"))
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)

    def test_pendente_espera_e_segue_verde(self):
        r = self.fechar(["2 in_progress -", "2 completed success"])
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.leituras_do_ci()), 2)

    def test_vermelho_sai_com_5_e_diz_o_que_fazer(self):
        self.assert_parou(self.fechar(["9 completed failure"]), "vermelho (run 9, failure", "gh run view 9 --log-failed")

    def test_cancelado_com_run_mais_novo_segue_o_head_novo(self):
        r = self.fechar(["3 completed cancelled avanca", "4 completed success"])
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        novo = self.git("ls-remote", "origin", "refs/heads/develop").split()[0]
        primeira, segunda = self.leituras_do_ci()
        self.assertNotIn(novo, primeira)
        self.assertIn(f"--commit {novo} ", segunda)
        self.assertIn(f"develop andou para {novo[:7]}; sigo o run dele", r.stdout)
        self.assertIn("verde: run 4", r.stdout)

    def test_cancelado_sem_run_mais_novo_sai_com_5(self):
        self.assert_parou(self.fechar(["3 completed cancelled"]), "cancelado sem run mais novo", "gh run rerun 3")

    def test_sem_fim_ate_a_espera_sai_com_5(self):
        self.assert_parou(self.fechar(["2 in_progress -"], "--espera", "0"), "não terminou em 0s", "segundo plano")

    def test_leitura_do_ci_que_falha_sai_com_5(self):
        self.assert_parou(self.fechar(["falha"], "--espera", "0"), "não consegui ler o CI do push")

    def test_develop_que_some_sai_com_5(self):
        self.assert_parou(self.fechar(["2 in_progress - apaga"]), "a branch develop não existe no origin")

    def test_remoto_ilegivel_sai_com_5(self):
        r = self.fechar(["2 in_progress - quebra"])
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("não consegui ler o head de develop no origin", r.stderr)

    def test_remoto_ilegivel_depois_do_cancelado_sai_com_5(self):
        r = self.fechar(["3 completed cancelled quebra"])
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("não consegui reler o head de develop depois do run 3 cancelado", r.stderr)

    def test_dry_run_descreve_o_6c(self):
        r = self.fechar(None, "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("[6c]", r.stdout)
        self.assertFalse(self.leituras_do_ci())


if __name__ == "__main__":
    unittest.main()
