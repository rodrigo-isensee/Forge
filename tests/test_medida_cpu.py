"""A medida de tempo dos testes de desempenho dos hooks (PROP-TEMPO-CPU): CPU do processo e dos filhos, e não o relógio."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import MedidaDeCpu, fator_de_carga, limite_de_cpu_do_corpus, limite_de_cpu_do_corpus_sob_carga  # noqa: E402

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

    def test_limite_do_corpus_e_90_s_por_trabalhador(self):
        for nucleos, trabalhadores in ((1, 1), (2, 1), (4, 2), (8, 4), (64, 4)):
            with self.subTest(nucleos=nucleos), mock.patch("os.cpu_count", return_value=nucleos):
                self.assertEqual(limite_de_cpu_do_corpus(), 90 * trabalhadores)


class LimitesPelaCargaDaMaquina(unittest.TestCase):
    """TESTE-CPU-CORPUS e TESTE-TEMPO-CARGA: o limite acompanha a carga medida e não passa do dobro."""

    def test_fator_segue_a_carga_por_nucleo_entre_1_e_2(self):
        for carga, nucleos, esperado in ((0.2, 4, 1.0), (4, 4, 1.0), (6, 4, 1.5), (8, 4, 2.0), (400, 4, 2.0)):
            with self.subTest(carga=carga, nucleos=nucleos):
                self.assertEqual(fator_de_carga(carga, nucleos), esperado)

    def test_carga_ilegivel_deixa_o_limite_de_sempre(self):
        with mock.patch("os.getloadavg", side_effect=OSError):
            self.assertEqual(fator_de_carga(None, 4), 1.0)

    def test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha(self):
        with mock.patch("os.cpu_count", return_value=8):
            base = limite_de_cpu_do_corpus()
            self.assertEqual(limite_de_cpu_do_corpus_sob_carga(0.5, 8), base)
            self.assertEqual(limite_de_cpu_do_corpus_sob_carga(12, 8), base * 1.5)
            self.assertEqual(limite_de_cpu_do_corpus_sob_carga(999, 8), base * 2)


if __name__ == "__main__":
    unittest.main()
