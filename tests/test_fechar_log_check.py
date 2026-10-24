"""N-FECHAR-b, B4: a parada do passo 4 imprime o comando para ler o log do check (só impresso, nunca executado).

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
        self.checks(f"bateria\tpass\t5m\t{RUN.format(111, 222)}", "extra\tskipping\t0\thttps://exemplo.test/sem-padrao")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("check bateria pass run=111 job=222", r.stdout)
        self.assertIn("check extra skipping run=? job=?", r.stdout)
        self.assertEqual(self.dicas(r), [])


if __name__ == "__main__":
    unittest.main()
