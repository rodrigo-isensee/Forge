"""N-FECHAR-a, A3: teto e piso das esperas de `bin/forge-fechar`, recusados antes do passo 1.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class FecharFaixas(unittest.TestCase):
    setUp = base.Fechar.setUp
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas

    # ---- N-FECHAR-a, A3: teto e piso das esperas, antes de qualquer passo ----
    def recusada_antes_do_passo_1(self, r, trecho):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(trecho, r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_pausa_acima_do_teto_e_recusada_antes_do_passo_1(self):
        for valor in ("31", "99999999999999999999"):
            r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_PAUSA=valor)
            self.recusada_antes_do_passo_1(r, "FORGE_FECHAR_PAUSA")
            self.assertIn("a 30", r.stderr)
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_PAUSA="31", FORGE_FECHAR_INTERVALO="30", FORGE_FECHAR_TESTE="")
        self.assertIn("de 1 a 30", r.stderr)  # a faixa de produção, sem o modo de teste

    def test_intervalo_nao_numerico_e_recusado_antes_do_passo_1(self):
        for valor in ("abc", " 5", "5 ", "\u0663", "5\nabc", "-1", "1000"):
            r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_INTERVALO=valor)
            self.recusada_antes_do_passo_1(r, "FORGE_FECHAR_INTERVALO")

    def test_intervalo_zero_e_pausa_zero_sem_modo_de_teste_sao_recusados(self):
        sem_teste = {"FORGE_FECHAR_TESTE": ""}  # vazio: a trava só vale com 1
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_INTERVALO="0", FORGE_FECHAR_PAUSA="3", **sem_teste)
        self.recusada_antes_do_passo_1(r, "FORGE_FECHAR_INTERVALO")
        self.assertIn("5 a 120", r.stderr)
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_INTERVALO="30", FORGE_FECHAR_PAUSA="0", **sem_teste)
        self.recusada_antes_do_passo_1(r, "FORGE_FECHAR_PAUSA")

    def test_teto_vale_tambem_com_o_modo_de_teste_e_zero_so_la(self):
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_PAUSA="31")
        self.recusada_antes_do_passo_1(r, "FORGE_FECHAR_PAUSA")
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_INTERVALO="121")
        self.recusada_antes_do_passo_1(r, "FORGE_FECHAR_INTERVALO")
        # com o modo de teste, 0 passa (é o que a suíte usa) e `08` vale 8, sem o erro de base do bash
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_INTERVALO="08", FORGE_FECHAR_PAUSA="03")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("value too great", r.stderr)

    def test_espera_acima_do_teto_ou_enorme_e_recusada_antes_do_laco(self):
        for valor in ("7201", "100000", "99999999999999999999", "abc", "-1"):
            r = self.fechar("p1", "--ref", "melhoria/x", "--espera", valor)
            self.recusada_antes_do_passo_1(r, "--espera")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "99999999999999999999")
        self.assertIn("0 a 7200", r.stderr)
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x", "--espera", "07200").returncode, 0)


if __name__ == "__main__":
    unittest.main()
