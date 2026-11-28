"""Orkastery 5 (0.44.2): o hook `pesado` espera a vez numa fila flock em vez de bloquear na hora; a versão em curso (a menor)
passa na frente; cartão em "Aguardando o dono" recusa; o teto vencido recusa com a posição (fixtures em tests/hooks/pesado)."""
import fcntl
import json
import os
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
sys.path.insert(0, str(RAIZ / "tests"))
import pesado  # noqa: E402
from test_hooks import PESADOS_DA_STACK, Fixture, ambiente_limpo, lancador  # noqa: E402


class Fila(unittest.TestCase):
    def test_prioridade_pela_versao_da_branch(self):
        self.assertLess(pesado.prioridade("melhoria/v0442"), pesado.prioridade("melhoria/v0450"))
        self.assertLess(pesado.prioridade("melhoria/v0450-adotar"), pesado.prioridade("melhoria/sem-versao"))
        self.assertEqual(pesado.prioridade("develop"), pesado.SEM_VERSAO)
        self.assertLess(pesado.prioridade("melhoria/v045"), pesado.prioridade("melhoria/v0451"))

    def test_fila_anda_pela_prioridade_e_descarta_a_morta(self):
        import tempfile
        pasta = Path(tempfile.mkdtemp(prefix="forge-fila-")) / "pesado.fila"
        tarde, f1 = pesado.entrar_na_fila(pasta, pesado.prioridade("melhoria/v0450"))
        cedo, f2 = pesado.entrar_na_fila(pasta, pesado.prioridade("melhoria/v0442"))
        morta = pasta / "000001-1-1"
        morta.write_text("")
        self.assertEqual(pesado.fila_viva(pasta), [cedo, tarde], "a versão em curso na frente; a sem flock sai")
        self.assertFalse(morta.exists())
        f1.close()
        f2.close()

    def test_aguardando_o_dono_so_na_secao(self):
        import tempfile
        raiz = Path(tempfile.mkdtemp(prefix="forge-kanban-"))
        (raiz / "KANBAN.md").write_text("## Fazendo\n| melhoria/v0450 |\n## Aguardando o dono\n| melhoria/v0442 |\n", encoding="utf-8")
        self.assertTrue(pesado.aguardando_o_dono(raiz, "melhoria/v0442"))
        self.assertFalse(pesado.aguardando_o_dono(raiz, "melhoria/v0450"))
        self.assertFalse(pesado.aguardando_o_dono(raiz, "melhoria/v044"), "nome inteiro, não prefixo")

    def test_quem_esta_na_fila_tem_a_vez_mesmo_livre(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="forge-pesado-fila-"))
        dados = json.loads((RAIZ / "tests/hooks/pesado/teto-diz-a-posicao.json").read_text(encoding="utf-8"))
        raiz, entrada = Fixture(RAIZ / "tests/hooks/pesado/teto-diz-a-posicao.json", dados).montar(tmp, os.getpid())
        trava = next(p for p in (raiz / ".forge" / "run", raiz / ".git" / "forge" / "run") if (p / "pesado.json").exists())
        (trava / "pesado.json").unlink()
        env = dict(ambiente_limpo(), FORGE_PESADO_ESPERA_S="1")
        _, preso = pesado.entrar_na_fila(Path(env["FORGE_MAQUINA"]) / "pesado.fila", 0)  # MP4: a fila é da máquina
        self.addCleanup(preso.close)
        r = subprocess.run(lancador("pesado"), input=json.dumps(entrada), cwd=raiz, env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2, "livre, mas outro está na fila na frente")
        self.assertIn("posição 2 de 2", r.stderr)

    def test_espera_a_vez_e_pega_quando_solta(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="forge-pesado-espera-"))
        outro = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(outro.kill)
        dados = json.loads((RAIZ / "tests/hooks/pesado/teto-diz-a-posicao.json").read_text(encoding="utf-8"))
        raiz, entrada = Fixture(RAIZ / "tests/hooks/pesado/teto-diz-a-posicao.json", dados).montar(tmp, outro.pid)
        trava = next(p for p in (raiz / ".forge" / "run", raiz / ".git" / "forge" / "run") if (p / "pesado.json").exists()) / "pesado.json"
        env = dict(ambiente_limpo(), FORGE_PESADO_ESPERA_S="20")
        threading.Timer(1.5, trava.unlink).start()
        t0 = time.monotonic()
        r = subprocess.run(lancador("pesado"), input=json.dumps(entrada), cwd=raiz, env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertGreater(time.monotonic() - t0, 1.0, "esperou a vez em vez de recusar")
        self.assertIn("toolu_9", trava.read_text(encoding="utf-8"))


class TravaDeVinteMinutos(unittest.TestCase):
    """MAQ-I9 (fatia 2): com o PID vivo, a trava de outra sessão vale até TRAVA_S = 1.200 s (a suíte em série vai a 693 s);
    ocupada, a vez é pela fila (Orkastery 5), e `expiracao_horas` menor ainda limita."""

    def rodar(self, idade, horas=None):
        import tempfile
        outro = subprocess.Popen([sys.executable, "-I", "-c", "import time; time.sleep(60)"], env=ambiente_limpo())
        self.addCleanup(outro.wait)
        self.addCleanup(outro.kill)
        caminho = RAIZ / "tests/hooks/pesado/teto-diz-a-posicao.json"
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        dados["estado"]["pesado.json"]["desde"] = f"{{agora-{idade}}}"
        if horas is not None:
            dados["config"] = {"pesados": PESADOS_DA_STACK, "expiracao_horas": horas}
        raiz, entrada = Fixture(caminho, dados).montar(Path(tempfile.mkdtemp(prefix="forge-pesado-1200-")), outro.pid)
        env = dict(ambiente_limpo(), FORGE_PESADO_ESPERA_S="1")
        r = subprocess.run(lancador("pesado"), input=json.dumps(entrada), cwd=raiz, env=env, capture_output=True, text=True, timeout=60)
        trava = next(p for p in (raiz / ".forge" / "run", raiz / ".git" / "forge" / "run") if (p / "pesado.json").exists())
        return r, (trava / "pesado.json").read_text(encoding="utf-8")

    def test_pid_vivo_ha_mais_de_10_min_segue_ocupado_e_vai_para_a_fila(self):
        r, trava = self.rodar(700)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("há 11 min", r.stderr)
        self.assertIn("posição 1 de 1", r.stderr)
        self.assertNotIn("toolu_9", trava)

    def test_pid_vivo_ha_mais_de_20_min_solta(self):
        r, trava = self.rodar(1300)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertIn("toolu_9", trava)

    def test_expiracao_menor_limita_os_20_min(self):
        r, trava = self.rodar(1000, horas=0.25)  # 900 s de `expiracao_horas` valem sobre os 1.200 s
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertIn("toolu_9", trava)


if __name__ == "__main__":
    unittest.main()
