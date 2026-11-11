"""N-FECHAR-b, R2 do parecer de segurança do lote a: `dorme_pid` nasce vazio no topo do script, não vem do ambiente (o `tmp2b` saiu na E8).

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

    def test_dorme_pid_comeca_vazio_junto_das_iniciais(self):
        linha = next(l for l in base.SCRIPT.read_text().splitlines() if l.startswith("pedido=") and "espera=" in l)
        self.assertIn('dorme_pid=""', linha)


if __name__ == "__main__":
    unittest.main()
