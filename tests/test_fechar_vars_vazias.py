"""N-FECHAR-b, R2 do parecer de segurança do lote a: `tmp2b` e `dorme_pid` nascem vazios no topo do script, não vêm do ambiente.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class VariaveisVazias(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    fechar_sem = base.Fechar.fechar_sem
    chamadas = base.Fechar.chamadas
    setUp = base.Fechar.setUp

    def test_tmp2b_herdado_do_ambiente_nao_e_apagado_pelo_fim(self):
        alvo = self.tmp / "nao-e-do-script"
        alvo.mkdir()
        (alvo / "arquivo").write_text("x")
        for modo in (("--dry-run",), ()):
            with self.subTest(modo=modo):
                r = self.fechar("p1", "--ref", "melhoria/x", *modo, tmp2b=str(alvo))
                self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
                self.assertTrue((alvo / "arquivo").exists())
                self.setUp()

    def test_dorme_pid_herdado_do_ambiente_nao_recebe_kill(self):
        import subprocess
        vitima = subprocess.Popen(["sleep", "30"])
        try:
            r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", dorme_pid=str(vitima.pid))
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            self.assertIsNone(vitima.poll(), "o fim matou um pid que veio do ambiente")
        finally:
            vitima.kill()
            vitima.wait()

    def test_as_duas_variaveis_comecam_vazias_junto_das_iniciais(self):
        linha = next(l for l in base.SCRIPT.read_text().splitlines() if l.startswith("pedido=") and "espera=" in l)
        self.assertIn('tmp2b=""', linha)


if __name__ == "__main__":
    unittest.main()
