"""N-FECHAR-b, B4: a parada do passo 4 imprime o comando para ler o log do check (só impresso, nunca executado);
FF-2 (E18): a linha `subida:` de cada passo no log.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

RUN = "https://github.com/o/r/actions/runs/{}/job/{}"


class FecharLogCheck(unittest.TestCase):
    setUp = base.Fechar.setUp
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    fechar_sem = base.Fechar.fechar_sem
    chamadas = base.Fechar.chamadas

    def checks(self, *linhas):
        (self.estado / "checks").write_text("".join(f"{l}\n" for l in linhas))

    def dicas(self, r):
        return [l for l in r.stderr.splitlines() if l.startswith("para ler: ")]

    def test_check_vermelho_imprime_o_comando_do_log_com_o_cache_no_tmpdir(self):
        cache = self.tmp / "cache"
        cache.mkdir()
        self.checks(f"bateria\tfail\t1m\t{RUN.format(12, 9)}")
        r = self.fechar("p1", "--ref", "melhoria/x", TMPDIR=str(cache))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.dicas(r), [f"para ler: XDG_CACHE_HOME='{cache}' gh run view 12 --log-failed"])
        self.assertFalse(any(c.startswith("gh run") for c in self.chamadas()))  # só imprime, nunca roda
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_o_nome_do_check_nunca_entra_no_comando_e_so_vale_o_numero_do_link(self):
        self.checks(f"x$(id);y\tfail\t1m\t{RUN.format(5, 1)}", f"outra\tfail\t1m\t{RUN.format(5, 2)}")
        r = self.fechar("p1", "--ref", "melhoria/x", TMPDIR=str(self.tmp))
        self.assertEqual(len(self.dicas(r)), 1, r.stderr)  # a mesma execução sai uma vez
        self.assertTrue(self.dicas(r)[0].endswith(" gh run view 5 --log-failed"), r.stderr)
        self.assertNotIn("$(id)", self.dicas(r)[0])

    def test_link_sem_numero_valido_nao_imprime_comando(self):
        for link in ("url", "https://x/actions/runs/12;id/job/9", "https://x/actions/runs/ab/job/9",
                     f"https://x/actions/runs/{'9' * 30}/job/9", "https://x/actions/runs/12/job/"):
            with self.subTest(link=link):
                self.checks(f"bateria\tfail\t1m\t{link}")
                r = self.fechar("p1", "--ref", "melhoria/x", TMPDIR=str(self.tmp))
                self.assertEqual(r.returncode, 1, r.stderr)
                self.assertEqual(self.dicas(r), [])

    def test_tmpdir_com_espaco_e_aspa_fica_entre_aspas_simples_e_sem_tmpdir_nao_leva_o_prefixo(self):
        self.checks(f"bateria\tfail\t1m\t{RUN.format(12, 9)}")
        pasta = self.tmp / "com espaço e 'aspa'"
        pasta.mkdir()
        aspa = chr(39)
        escapada = str(pasta).replace(aspa, aspa + chr(92) + aspa + aspa)
        r = self.fechar("p1", "--ref", "melhoria/x", TMPDIR=str(pasta))
        self.assertEqual(self.dicas(r), [f"para ler: XDG_CACHE_HOME='{escapada}' gh run view 12 --log-failed"])
        r = self.fechar_sem("p1", "--ref", "melhoria/x", remover=("TMPDIR",))
        self.assertEqual(self.dicas(r), ["para ler: gh run view 12 --log-failed"])

    def test_checks_verdes_continuam_com_run_e_job_pela_funcao_nova(self):
        self.checks(f"bateria\tpass\t5m\t{RUN.format(111, 222)}", "bateria (python 3.14)\tpass\t5m\turl", "catraca\tpass\t5s\turl", "extra\tskipping\t0\thttps://exemplo.test/sem-padrao")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("check bateria pass run=111 job=222", r.stdout)
        self.assertIn("check extra skipping run=? job=?", r.stdout)
        self.assertEqual(self.dicas(r), [])

    def test_pasta_do_log_do_proprio_usuario_com_modo_diferente_de_700_vira_700_com_aviso(self):
        for modo in (0o755, 0o777, 0o500, 0o2755, 0o4755, 0o6755):
            with self.subTest(modo=oct(modo)):
                pasta = self.tmp / f"logs-{modo:o}"
                pasta.mkdir()
                pasta.chmod(modo)
                r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(pasta))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(oct(pasta.stat().st_mode & 0o7777), "0o700")  # inclui o setgid e o setuid
                self.assertIn(f"ajustei para 700: {pasta}", r.stderr)
                self.assertEqual(len(list(pasta.glob("forge-fechar-*.log"))), 1)

    def test_o_chmod_da_pasta_do_log_age_sobre_a_pasta_ja_aberta_e_nao_sobre_o_caminho(self):
        # FECHAR-TOCTOU: entre a checagem do caminho e o chmod o caminho podia virar link; o chmod age sobre `.` depois de entrar na pasta
        registro = self.tmp / "chmod.args"
        falso = self.tmp / "bin" / "chmod"
        falso.write_text(f'#!/usr/bin/env bash\necho "$@" >> {registro}\nexec /bin/chmod "$@"\n')
        falso.chmod(0o755)
        pasta = self.tmp / "logs-toctou"
        pasta.mkdir()
        pasta.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(pasta))
        self.assertEqual(r.returncode, 0, r.stderr)
        chamadas = registro.read_text().splitlines()
        self.assertEqual(len(chamadas), 1, chamadas)
        self.assertTrue(chamadas[0].endswith(" ."), chamadas)
        self.assertNotIn(str(pasta), chamadas[0])

    def test_chmod_que_sai_0_sem_mudar_o_modo_faz_o_script_recusar(self):
        # QA A2: a conferência do modo depois do chmod (mutante L4: `|| die` trocado por `|| true`)
        falso = self.tmp / "bin" / "chmod"
        falso.write_text("#!/usr/bin/env bash\nexit 0\n")
        falso.chmod(0o755)
        pasta = self.tmp / "logs-chmod-falso"
        pasta.mkdir()
        pasta.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(pasta))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn(f"a pasta do log precisa ter modo 700: {pasta}", r.stderr)
        self.assertNotIn("ajustei", r.stderr)
        self.assertEqual(oct(pasta.stat().st_mode & 0o7777), "0o755")

    def test_pasta_com_modo_700_nao_traz_aviso_e_link_ou_nao_diretorio_continuam_recusados(self):
        certa = self.tmp / "certa"
        certa.mkdir(mode=0o700)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(certa))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("ajustei", r.stderr)
        aberta = self.tmp / "aberta"
        aberta.mkdir()
        aberta.chmod(0o755)
        link = self.tmp / "link"
        link.symlink_to(aberta)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(link))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("link simbólico", r.stderr)
        self.assertEqual(oct(aberta.stat().st_mode & 0o777), "0o755")  # o link nunca leva o chmod ao alvo
        arquivo = self.tmp / "arq"
        arquivo.write_text("x\n")
        arquivo.chmod(0o644)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(arquivo))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(oct(arquivo.stat().st_mode & 0o777), "0o644")


    # FF-2 (E18, SP6): o relógio da subida, uma linha `subida: <n> <início> <fim>` por passo, só no log.
    def subidas(self):
        logs = list((self.tmp / "logs").glob("forge-fechar-*.log"))
        self.assertEqual(len(logs), 1, logs)
        return [l.split(" ", 1)[1].split()[1:] for l in logs[0].read_text().splitlines() if l.split(" ", 1)[1].startswith("subida:")]

    def check_lento(self):
        lento = self.tmp / "check-lento"
        lento.write_text(f'#!/usr/bin/env bash\nsleep 1.2\nexec {self.tmp / "check"} "$@"\n')
        lento.chmod(0o755)
        return str(lento)

    def test_fechamento_grava_uma_linha_subida_por_passo_e_a_do_6_com_merged(self):
        head7 = self.git("rev-parse", "melhoria/x")[:7]
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_CHECK=self.check_lento())
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        linhas = self.subidas()
        self.assertEqual([l[0] for l in linhas], ["1", "1c", "2", "3", "2b", "4", "5", "6a", "6b", "6", "7", "8"])
        for l in linhas:
            self.assertRegex(l[1], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
            self.assertLessEqual(l[1], l[2], l)
        self.assertLess(linhas[0][1], linhas[0][2])  # o passo 1 (check de 1,2 s) fecha com a hora do fim, não a do início
        self.assertEqual(linhas[9][3:], ["MERGED", "0123456", head7])
        self.assertEqual(linhas[11][3:], ["rc", "0"])  # o último passo, agora o 8, fecha com o rc
        self.assertEqual([l[3:] for l in linhas[:9]], [[]] * 9)
        self.assertNotIn("subida:", r.stdout + r.stderr)  # só no log

    def test_parada_no_passo_4_fecha_a_linha_do_4_com_rc_1(self):
        self.checks("bateria\tfail\t1m\turl")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = self.subidas()
        self.assertEqual([l[0] for l in linhas], ["1", "1c", "2", "3", "2b", "4"])
        self.assertEqual(linhas[-1][3:], ["rc", "1"])

    def test_dry_run_nao_grava_linha_subida(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.subidas(), [])


if __name__ == "__main__":
    unittest.main()
