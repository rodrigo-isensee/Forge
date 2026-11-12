"""M12 (v046, E14.2): `bin/forge-pesado` mostra quem tem a vez da bateria pesada e espera a vez com teto, só lendo o estado
que o hook `pesado` grava (`pesado.json` e a fila `pesado.fila/`). Cada teste roda o comando num projeto temporário,
com o ambiente limpo e o Python com `-I`."""
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tests"))
from ambiente_git import sem_manutencao  # noqa: E402

BIN = RAIZ / "bin" / "forge-pesado"
PID_MORTO = 4_194_303 + 1  # acima do pid_max de 64 bits do Linux: nunca é processo vivo


class ForgePesado(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-pesado-m12-"))
        self.addCleanup(shutil.rmtree, self.raiz, True)
        self.env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.raiz), "LANG": "C.UTF-8",
                                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
        subprocess.run(["git", "init", "-q", str(self.raiz)], env=self.env, check=True, stdin=subprocess.DEVNULL)
        (self.raiz / ".forge").mkdir()
        (self.raiz / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        self.run_dir = self.raiz / ".forge" / "run"
        (self.run_dir / "pesado.fila").mkdir(parents=True)

    def rodar(self, *args, cwd=None, prazo=30):
        try:
            return subprocess.run([sys.executable, "-I", str(BIN), *args], cwd=cwd or self.raiz, env=self.env,
                                  capture_output=True, text=True, timeout=prazo, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            self.fail(f"forge-pesado {' '.join(args)} não saiu em {prazo} s")

    def trava(self, **campos):
        dados = {"pid": os.getpid(), "agente": "agente-x", "comando": "bin/forge-testes --completa", "desde": time.time(),
                 "tool_use_id": "toolu_1"}
        dados.update(campos)
        (self.run_dir / "pesado.json").write_text(json.dumps(dados), encoding="utf-8")

    def senha_viva(self, nome="000100-1-1"):
        f = open(self.run_dir / "pesado.fila" / nome, "w", encoding="utf-8")  # noqa: SIM115 - preso até o fim do teste
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(f.close)
        return f

    def test_status_livre_sem_trava(self):
        r = self.rodar("status")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "pesado: livre · fila: 0"), r.stderr)

    def test_status_ocupada_diz_quem_desde_quando_e_o_pid_vivo(self):
        self.trava()
        r = self.rodar("status")
        self.assertEqual(r.returncode, 0, r.stderr)
        for trecho in ("pesado: ocupada", '"agente-x"', '"bin/forge-testes --completa"', "desde: ", f"pid {os.getpid()}: vivo"):
            self.assertIn(trecho, r.stdout)

    def test_pid_morto_aparece_mas_nao_solta_a_trava(self):
        self.trava(pid=PID_MORTO)
        r = self.rodar("status")
        self.assertIn("pesado: ocupada", r.stdout, "o pid não decide: o de outro namespace não aparece")
        self.assertIn(f"pid {PID_MORTO}: não visto", r.stdout)

    def test_trava_vencida_fica_livre(self):
        self.trava(desde=time.time() - 601)
        self.assertEqual(self.rodar("status").stdout.strip(), "pesado: livre · fila: 0")

    def test_trava_sem_desde_numerico_ou_que_nao_e_objeto_fica_livre(self):
        self.trava(desde="ontem")
        self.assertEqual(self.rodar("status").stdout.strip(), "pesado: livre · fila: 0")
        (self.run_dir / "pesado.json").write_text("[1]", encoding="utf-8")
        self.assertEqual(self.rodar("status").stdout.strip(), "pesado: livre · fila: 0")

    def test_comando_com_caractere_de_controle_sai_escapado(self):
        self.trava(comando="x\x1b[2Jy")
        r = self.rodar("status")
        self.assertNotIn("\x1b", r.stdout)
        self.assertIn("\\u001b", r.stdout)

    def test_fila_conta_so_a_senha_presa_sem_apagar_a_morta_nem_seguir_link(self):
        self.senha_viva()
        morta = self.run_dir / "pesado.fila" / "000100-2-2"
        morta.write_text("", encoding="utf-8")
        presa_fora = self.raiz / "fora"
        presa = open(presa_fora, "w", encoding="utf-8")  # noqa: SIM115 - preso até o fim do teste
        fcntl.flock(presa, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(presa.close)
        (self.run_dir / "pesado.fila" / "000100-3-3").symlink_to(presa_fora)
        r = self.rodar("status")
        self.assertEqual(r.stdout.strip(), "pesado: livre · fila: 1", "só a senha presa conta; o link fica de fora")
        self.assertTrue(morta.exists(), "só leitura: a senha morta fica para o hook limpar")

    def test_json_ilegivel_sai_2(self):
        (self.run_dir / "pesado.json").write_text("{", encoding="utf-8")
        r = self.rodar("status")
        self.assertEqual(r.returncode, 2)
        self.assertIn("estado ilegível", r.stderr)

    def test_fora_de_projeto_sai_2(self):
        fora = Path(tempfile.mkdtemp(prefix="forge-pesado-fora-"))
        self.addCleanup(shutil.rmtree, fora, True)
        r = self.rodar("status", cwd=fora)
        self.assertEqual(r.returncode, 2)
        self.assertIn("fora de projeto do Forge", r.stderr)

    def test_esperar_livre_sai_0_na_primeira_volta(self):
        r = self.rodar("esperar", "--teto", "5", "--passo", "0.2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), ["volta 1: pesado: livre · fila: 0", "fim=livre"])

    def test_esperar_ocupada_sai_1_no_teto_com_progresso(self):
        self.trava()
        t0 = time.monotonic()
        r = self.rodar("esperar", "--teto", "1", "--passo", "0.3", prazo=15)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertGreaterEqual(time.monotonic() - t0, 1.0)
        linhas = r.stdout.splitlines()
        self.assertTrue(linhas[-1].startswith("fim=teto"), r.stdout)
        self.assertGreaterEqual(sum(x.startswith("volta ") for x in linhas), 3, "uma linha de progresso por volta")

    def test_esperar_com_fila_viva_nao_tem_a_vez(self):
        self.senha_viva()
        r = self.rodar("esperar", "--teto", "0.5", "--passo", "0.2", prazo=15)
        self.assertEqual(r.returncode, 1, "livre, mas há quem espere na frente")
        self.assertIn("fila: 1", r.stdout)

    def test_esperar_pega_a_vez_quando_a_trava_some(self):
        self.trava()
        threading.Timer(1.0, (self.run_dir / "pesado.json").unlink, kwargs={"missing_ok": True}).start()
        r = self.rodar("esperar", "--teto", "20", "--passo", "0.3", prazo=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pesado: ocupada", r.stdout)
        self.assertEqual(r.stdout.splitlines()[-1], "fim=livre")

    def test_teto_e_passo_fora_da_faixa_saem_2(self):
        for args in (("--teto", "0"), ("--teto", "541"), ("--teto", "1", "--passo", "0"), ("--teto", "nan")):
            with self.subTest(args=args):
                r = self.rodar("esperar", *args)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn("--teto vai de mais de 0 a 540 s", r.stderr)

    def test_teto_no_limite_vale(self):
        r = self.rodar("esperar", "--teto", "540", "--passo", "0.1")
        self.assertEqual((r.returncode, r.stdout.splitlines()[-1:]), (0, ["fim=livre"]), r.stderr)


if __name__ == "__main__":
    unittest.main()
