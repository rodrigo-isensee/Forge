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
from test_hooks import Fixture, ambiente_limpo, lancador  # noqa: E402


class Fila(unittest.TestCase):
    def test_prioridade_pela_versao_da_branch(self):
        self.assertLess(pesado.prioridade("melhoria/v0442"), pesado.prioridade("melhoria/v0450"))
        self.assertLess(pesado.prioridade("melhoria/v0450-adotar"), pesado.prioridade("melhoria/sem-versao"))
        self.assertEqual(pesado.prioridade("develop"), pesado.SEM_VERSAO)

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


if __name__ == "__main__":
    unittest.main()
