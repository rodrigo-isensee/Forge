"""Nenhum módulo de teste pesa mais que 25% do teto do job `bateria` (HOOKS-CORPUS-RAPIDO, E3).

A suite-paralela (D4) divide a suíte por módulo: um módulo é indivisível, e o caminho crítico de um processo nunca é menor
que o maior. Um módulo que passa de um quarto do teto de 15 min do job deixa de caber no runner mais lento (2 CPUs, com os
outros processos disputando as mesmas); o remédio é dividi-lo em módulos menores, não subir o teto."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

PESOS = Path(__file__).resolve().parent / "pesos-d4.json"
TETO_DO_JOB_S = 15 * 60  # `timeout-minutes: 15` do job que roda `scripts/suite-paralela.py` em .github/workflows/ci.yml
LIMITE_DO_MODULO_S = TETO_DO_JOB_S * 25 // 100  # 225 s


def acima_do_limite(pesos, limite=LIMITE_DO_MODULO_S):
    """[(módulo, peso)] dos módulos de `pesos` (módulo -> segundos) que passam de `limite`, do mais pesado ao mais leve."""
    return sorted(((m, p) for m, p in pesos.items() if p > limite), key=lambda item: -item[1])


class PesosDoD4(unittest.TestCase):
    def test_nenhum_modulo_passa_de_25_por_cento_do_teto_do_job(self):
        pesos = json.loads(PESOS.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(pesos), 50, "tests/pesos-d4.json quase vazio: a medição se perdeu")
        for modulo, peso in acima_do_limite(pesos):
            with self.subTest(modulo=modulo):
                self.fail(f"{modulo} pesa {peso} s, acima de {LIMITE_DO_MODULO_S} s (25% do teto de {TETO_DO_JOB_S} s do "
                          "job bateria): divida o módulo em módulos menores e regrave os pesos com FORGE_SUITE_MEDIR=1")

    def test_o_limite_e_de_225_segundos_e_o_peso_acima_dele_e_apontado(self):
        self.assertEqual(LIMITE_DO_MODULO_S, 225)
        self.assertEqual(acima_do_limite({"test_a": 225.0, "test_b": 225.1, "test_c": 400.0, "test_d": 1.0}),
                         [("test_c", 400.0), ("test_b", 225.1)])
        self.assertEqual(acima_do_limite({}), [])


if __name__ == "__main__":
    unittest.main()
