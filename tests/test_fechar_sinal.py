"""N-FECHAR-a, A4: TERM, INT e HUP gravam `fim: código <n>` e cortam a espera de `bin/forge-fechar`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
import os
import signal
import subprocess
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
SCRIPT = base.SCRIPT


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    setUp = base.Fechar.setUp
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    resumo = base.Fechar.resumo
    log_de = base.Fechar.log_de
    merges = base.Fechar.merges
    criacoes = base.Fechar.criacoes

    # ---- N-FECHAR-a, A4: corte por sinal no meio da espera (o teto de 600 s do Bash manda TERM) ----
    def espera_cortada_por(self, sinal, grupo=False):
        """Roda com checks pendentes e `--espera 60`, manda `sinal` depois da linha `checks:` (ao pid, ou ao grupo de
        processos inteiro) e devolve (código de saída, linhas do log, segundos até o fim do processo)."""
        (self.estado / "checks").write_text("bateria\tpending\t0\turl\n")
        env = dict(self.env, FORGE_FECHAR_INTERVALO="30")  # intervalo longo: o sinal tem de cortar o sleep, não esperá-lo
        p = subprocess.Popen(["bash", str(SCRIPT), "p1", "--ref", "melhoria/x", "--espera", "60"], cwd=self.proj, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=grupo)
        try:
            log = Path(p.stdout.readline().strip()[len("log: "):])
            limite = time.monotonic() + 30
            while "checks:" not in log.read_text():
                self.assertLess(time.monotonic(), limite, "o script não chegou à espera dos checks")
                time.sleep(0.05)
            t0 = time.monotonic()
            (os.killpg if grupo else os.kill)(p.pid, sinal)
            rc = p.wait(timeout=30)
            gasto = time.monotonic() - t0
            while not log.read_text().splitlines()[-1].count("fim: código") and time.monotonic() < limite + 30:
                time.sleep(0.05)
            return rc, log.read_text().splitlines(), gasto
        finally:
            if p.poll() is None:
                p.kill()
            p.communicate()

    def test_l5_term_durante_a_espera_grava_fim_codigo_143(self):
        rc, linhas, gasto = self.espera_cortada_por(signal.SIGTERM)
        self.assertEqual(rc, 143)
        self.assertTrue(linhas[-1].endswith(" fim: código 143"), linhas[-3:])
        self.assertLess(gasto, 10)  # com o sleep de 30 s em curso: o `fim:` não espera o intervalo
        self.assertFalse(any("Entrega p1 fechada" in x for x in linhas))
        self.assertEqual([c for c in self.chamadas() if c.startswith("gh pr merge")], [])

    def test_l5_term_no_grupo_de_processos_tambem_grava_fim_codigo_143(self):
        rc, linhas, gasto = self.espera_cortada_por(signal.SIGTERM, grupo=True)
        self.assertEqual(rc, 143)
        self.assertTrue(linhas[-1].endswith(" fim: código 143"), linhas[-3:])
        self.assertLess(gasto, 10)

    def test_l5_int_e_hup_gravam_130_e_129(self):
        for sinal, codigo in ((signal.SIGINT, 130), (signal.SIGHUP, 129)):
            with self.subTest(sinal=sinal.name):
                rc, linhas, _ = self.espera_cortada_por(sinal)
                self.assertEqual(rc, codigo)
                self.assertTrue(linhas[-1].endswith(f" fim: código {codigo}"), linhas[-3:])

    def test_l5_rodada_seguinte_ao_corte_com_pr_ja_mesclado_so_termina_a_limpeza(self):
        # o corte deixou o PR MERGED e a branch local e a remota ainda lá: a rodada seguinte não abre PR nem mescla e fecha a limpeza
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        (self.estado / "estado").write_text("MERGED")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 0"))

    def test_o_sleep_das_esperas_roda_em_segundo_plano_com_wait(self):
        codigo = "\n".join(l for l in SCRIPT.read_text().splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn('sleep "$intervalo"', codigo)
        self.assertNotIn('sleep "$pausa"', codigo)
        self.assertEqual(codigo.count('sleep "$1" &'), 1)


if __name__ == "__main__":
    unittest.main()
