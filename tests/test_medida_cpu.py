"""A medida de tempo dos testes de desempenho dos hooks (PROP-TEMPO-CPU): CPU do processo e dos filhos, e não o relógio."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import (  # noqa: E402
    MedidaDeCpu, fator_de_carga, limite_de_cpu_do_corpus, limite_de_cpu_do_corpus_sob_carga, menor_custo)

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

    def test_le_a_carga_de_1_minuto_e_nao_a_de_15(self):  # A1 do QA
        with mock.patch("os.getloadavg", return_value=(6.0, 0.0, 0.0)):
            self.assertEqual(fator_de_carga(None, 4), 1.5)

    def test_carga_dada_vale_mais_que_a_lida(self):
        with mock.patch("os.getloadavg", return_value=(0.0, 0.0, 0.0)):
            self.assertEqual(fator_de_carga(6, 4), 1.5)

    def test_sem_nucleos_dados_usa_os_do_processo(self):  # A2 do QA
        with mock.patch("apoio_volta_unica.nucleos_do_processo", return_value=4):
            self.assertEqual(fator_de_carga(6, None), 1.5)

    def test_sem_leitura_de_nucleos_conta_um(self):
        with mock.patch("apoio_volta_unica.nucleos_do_processo", return_value=None):
            self.assertEqual(fator_de_carga(1.5, None), 1.5)

    def test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha(self):
        with mock.patch("os.cpu_count", return_value=8):
            base = limite_de_cpu_do_corpus()
            self.assertEqual(limite_de_cpu_do_corpus_sob_carga(0.5, 8), base)
            self.assertEqual(limite_de_cpu_do_corpus_sob_carga(12, 8), base * 1.5)
            self.assertEqual(limite_de_cpu_do_corpus_sob_carga(999, 8), base * 2)



class MenorCustoDasMedidas(unittest.TestCase):
    """TESTE-HEREDOCS-ORCAMENTO-ESTAVEL: só a medida acima do limite se repete, até 3 vezes, e vale a menor."""

    @staticmethod
    def medidas(*custos):
        fila, chamadas = iter(custos), []

        def medir():
            chamadas.append(next(fila))
            return chamadas[-1], f"m{len(chamadas)}"
        return medir, chamadas

    def test_abaixo_do_limite_mede_uma_vez(self):
        medir, chamadas = self.medidas(2.9, 0.1, 0.1)
        self.assertEqual(menor_custo(medir, 3.0), (2.9, "m1"))
        self.assertEqual(chamadas, [2.9])

    def test_no_limite_ou_acima_mede_de_novo_e_vale_a_menor(self):
        for custos, esperado in (((3.0, 2.0, 0.1), (2.0, "m2")), ((4.0, 3.5, 3.2), (3.2, "m3")),
                                 ((3.5, 4.0, 3.9), (3.5, "m1"))):
            with self.subTest(custos=custos):
                medir, _ = self.medidas(*custos, 0.0)
                self.assertEqual(menor_custo(medir, 3.0), esperado)

    def test_regressao_passa_do_limite_nas_tres_e_para_na_terceira(self):
        medir, chamadas = self.medidas(9.0, 12.0, 10.0, 0.1)
        self.assertEqual(menor_custo(medir, 3.0), (9.0, "m1"))
        self.assertEqual(chamadas, [9.0, 12.0, 10.0])


if __name__ == "__main__":
    unittest.main()
