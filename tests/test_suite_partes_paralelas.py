"""E4.1 (0.45.7, R-TETO): `scripts/suite-partes.py --duas-partes` roda a suíte em 2 partes, em paralelo só com folga
(load1 < nproc e memória livre acima do piso) e em série sem ela. Classe do defeito: paralelizar com a máquina cheia
(o que gera FLAKY por carga) ou dar verde com uma parte só."""
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "suite-partes.py"


def carregar():
    spec = importlib.util.spec_from_file_location("suite_partes_paralelas", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Filho:
    def __init__(self, codigo, registro, comando):
        self.codigo, self.registro, self.comando = codigo, registro, comando

    def wait(self):
        self.registro.append(("wait", self.comando[-1]))
        return self.codigo


class FolgaDaMaquina(unittest.TestCase):
    def setUp(self):
        self.sp = carregar()

    def test_folga_exige_load_abaixo_dos_nucleos_e_memoria_acima_do_piso(self):
        self.assertTrue(self.sp.ha_folga(3.0, 8.0, 12, 2.0))
        self.assertFalse(self.sp.ha_folga(12.0, 8.0, 12, 2.0))  # load1 == nproc já não é folga
        self.assertFalse(self.sp.ha_folga(14.0, 8.0, 12, 2.0))
        self.assertFalse(self.sp.ha_folga(3.0, 2.0, 12, 2.0))  # memória == piso já não é folga
        self.assertFalse(self.sp.ha_folga(3.0, 1.0, 12, 2.0))

    def test_sem_medida_nao_ha_folga(self):
        self.assertFalse(self.sp.ha_folga(None, 8.0, 12, 2.0))
        self.assertFalse(self.sp.ha_folga(3.0, None, 12, 2.0))
        self.assertFalse(self.sp.ha_folga(3.0, 8.0, None, 2.0))
        self.assertFalse(self.sp.ha_folga(0.0, 8.0, 0, 2.0))

    def test_piso_de_memoria_vem_da_config_e_invalido_vale_o_padrao(self):
        self.assertEqual(self.sp.piso_de_memoria({"piso_memoria_gb": 4}), 4.0)
        for ruim in ("zero", 0, -1, True, None):
            self.assertEqual(self.sp.piso_de_memoria({"piso_memoria_gb": ruim}), 2.0, ruim)
        for config in ({}, None, [], "texto"):
            try:
                piso = self.sp.piso_de_memoria(config)
            except Exception as erro:  # noqa: BLE001 - config ruim tem de valer o padrão, não estourar
                self.fail(f"config {config!r} estourou: {erro!r}")
            self.assertEqual(piso, 2.0, config)


class DuasPartes(unittest.TestCase):
    def setUp(self):
        self.sp = carregar()
        self.paralela = unittest.mock.Mock()
        self.paralela.RAIZ = Path(tempfile.mkdtemp(prefix="forge-duas-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(self.paralela.RAIZ, ignore_errors=True))

    def rodar(self, medida, codigos, piso=None):
        if piso is not None:
            (self.paralela.RAIZ / ".forge").mkdir()
            (self.paralela.RAIZ / ".forge" / "config.json").write_text(json.dumps({"piso_memoria_gb": piso}))
        self.paralela.medir_carga.return_value = medida
        registro, comandos = [], []

        def lancar(comando):
            comandos.append(comando)
            registro.append(("lancou", comando[-1]))
            return Filho(codigos[len(comandos) - 1], registro, comando)

        with unittest.mock.patch.object(self.sp.os, "cpu_count", return_value=12), \
                unittest.mock.patch.object(self.sp.sys, "stderr"):
            codigo = self.sp.por_duas_partes(self.paralela, {"FORGE_SUITE_PULADOS": "x"}, lancar)
        return codigo, registro, comandos

    def test_com_folga_lanca_as_duas_antes_de_esperar(self):
        codigo, registro, comandos = self.rodar((2.0, 10.0, 31.0), [0, 0])
        self.assertEqual(codigo, 0)
        self.assertEqual([r[0] for r in registro], ["lancou", "lancou", "wait", "wait"])
        self.assertEqual([c[-1] for c in comandos], ["1/2", "2/2"])
        self.assertEqual(comandos[0][1], "-I")

    def test_o_aviso_diz_o_modo_escolhido(self):
        for medida, modo in (((2.0, 10.0, 31.0), "paralelo"), ((14.0, 10.0, 31.0), "em série")):
            with unittest.mock.patch.object(self.sp.os, "cpu_count", return_value=12), \
                    unittest.mock.patch.object(self.sp.sys, "stderr", new_callable=io.StringIO) as erro:
                self.paralela.medir_carga.return_value = medida
                self.sp.por_duas_partes(self.paralela, {}, lambda comando: Filho(0, [], comando))
            self.assertIn(f"2 partes {modo} ", erro.getvalue())

    def test_sem_folga_roda_em_serie(self):
        codigo, registro, _ = self.rodar((14.0, 10.0, 31.0), [0, 0])
        self.assertEqual(codigo, 0)
        self.assertEqual([r[0] for r in registro], ["lancou", "wait", "lancou", "wait"])

    def test_memoria_abaixo_do_piso_da_config_roda_em_serie(self):
        _, registro, _ = self.rodar((2.0, 5.0, 31.0), [0, 0], piso=6)
        self.assertEqual([r[0] for r in registro], ["lancou", "wait", "lancou", "wait"])

    def test_sem_medida_roda_em_serie(self):
        _, registro, _ = self.rodar((None, None, None), [0, 0])
        self.assertEqual([r[0] for r in registro], ["lancou", "wait", "lancou", "wait"])

    def test_parte_que_falha_reprova_em_paralelo(self):
        for codigos in ([1, 0], [0, 1], [1, 1]):
            codigo, registro, _ = self.rodar((2.0, 10.0, 31.0), codigos)
            self.assertEqual(codigo, 1, codigos)
            self.assertEqual(len([r for r in registro if r[0] == "wait"]), 2)  # espera as duas

    def test_em_serie_a_primeira_que_falha_encerra_sem_lancar_a_segunda(self):
        codigo, _, comandos = self.rodar((14.0, 10.0, 31.0), [1, 0])
        self.assertEqual(codigo, 1)
        self.assertEqual(len(comandos), 1)

    def test_em_serie_a_segunda_que_falha_reprova(self):
        codigo, _, comandos = self.rodar((14.0, 10.0, 31.0), [0, 1])
        self.assertEqual(codigo, 1)
        self.assertEqual(len(comandos), 2)

    def test_filho_roda_com_ci_e_sem_o_arquivo_de_pulados(self):
        env = {}
        with unittest.mock.patch.object(self.sp.subprocess, "Popen") as popen, \
                unittest.mock.patch.object(self.sp.os, "cpu_count", return_value=12), \
                unittest.mock.patch.object(self.sp.sys, "stderr"):
            popen.return_value.wait.return_value = 0
            self.paralela.medir_carga.return_value = (2.0, 10.0, 31.0)
            self.sp.por_duas_partes(self.paralela, {"FORGE_SUITE_PULADOS": "x", "A": "1"})
            env = popen.call_args.kwargs["env"]
        self.assertEqual(env.get("CI"), "1")
        self.assertNotIn("FORGE_SUITE_PULADOS", env)
        self.assertEqual(env["A"], "1")

    def test_main_aceita_so_a_chamada_sem_argumento_extra(self):
        with unittest.mock.patch.object(self.sp, "por_duas_partes", return_value=0) as por, \
                unittest.mock.patch.object(self.sp, "carregar_paralela"), unittest.mock.patch.object(self.sp.sys, "stderr"):
            self.assertEqual(self.sp.main(["--duas-partes"], {}), 0)
            por.assert_called_once()
            self.assertEqual(self.sp.main(["--duas-partes", "x"], {}), 2)


if __name__ == "__main__":
    unittest.main()
