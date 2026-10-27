"""A medida de tempo dos testes de desempenho dos hooks (PROP-TEMPO-CPU): CPU do processo e dos filhos, e não o relógio."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import MedidaDeCpu  # noqa: E402

DORME = "import time; time.sleep(1.5)"
GASTA = "import time\nwhile time.process_time() < 0.8: pass"


def filho(codigo):
    subprocess.run([sys.executable, "-I", "-c", codigo], check=True, timeout=60)


class MedidaDeCpuDosTestesDeDesempenho(unittest.TestCase):
    def test_filho_que_dorme_nao_conta_e_o_relogio_passa_do_limite(self):
        with MedidaDeCpu() as medida:
            filho(DORME)
        self.assertGreaterEqual(medida.relogio, 1.4)
        self.assertLess(medida.cpu, 0.5, medida.texto())

    def test_filho_que_gasta_cpu_conta(self):
        with MedidaDeCpu() as medida:
            filho(GASTA)
        self.assertGreaterEqual(medida.cpu, 0.7, medida.texto())

    def test_o_trabalho_do_proprio_processo_conta(self):
        with MedidaDeCpu() as medida:
            soma = 0
            for i in range(6_000_000):
                soma += i
        self.assertGreater(medida.cpu, 0.1, medida.texto())

    def test_o_texto_diz_cpu_e_relogio(self):
        with MedidaDeCpu() as medida:
            pass
        self.assertRegex(medida.texto(), r"^CPU \d+\.\d\d s, relógio \d+\.\d\d s$")


if __name__ == "__main__":
    unittest.main()
