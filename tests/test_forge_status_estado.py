"""S1a (v0481 E20.1): `forge-check status` (bin/forge_estado.py) imprime o estado da fábrica lido na hora; leitura que falha vira
`não verificável`, nunca erro. Um teste por item e por guarda, com o ramo de falha; o gh é um falso (sem rede, R-CUSTO)."""
import datetime as dt
import os
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_git_herdado, sem_manutencao  # noqa: E402
from gh_falso import pasta_com_gh  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
sys.path.insert(0, str(RAIZ / "bin"))
import forge_estado as E  # noqa: E402

AGORA = dt.datetime(2026, 11, 26, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=-3)))
COMMIT = {"sha": "a" * 40, "commit": {"committer": {"date": "2026-11-26T14:30:00Z"}, "message": "feat: x (#9)\n\ncorpo"}}
RELEASE = {"tagName": "v0.47.18", "publishedAt": "2026-11-24T18:00:00Z"}


def pr(n, titulo="feat: x", mergeable="MERGEABLE", rotulos=(), checks=()):
    return {"number": n, "title": titulo, "mergeable": mergeable, "labels": [{"name": r} for r in rotulos],
            "statusCheckRollup": list(checks)}


def ctx(respostas=None, abertas=None, versao="0.47.19", plugin=RAIZ):
    """Contexto falso: `respostas` por 1.º e 2.º argumento do gh (ausente: sem saída, como sem rede)."""
    respostas = respostas or {}

    def gh_json(raiz, *args):
        return respostas.get(args[:2], (None, "gh falso: sem rede"))

    return {"gh_json": gh_json, "seguro": lambda t: t, "versao": lambda: versao, "plugin": Path(plugin), "pedidos": RAIZ,
            "abertas": abertas or (lambda pasta: (["Não há decisão sua pendente"], 0))}


def rodar(contexto, agora="2026-11-26T12:00-03:00"):
    saida = StringIO()
    with redirect_stdout(saida):
        rc = E.executar(Namespace(agora=agora), RAIZ, contexto)
    return rc, saida.getvalue()


class Idade(unittest.TestCase):
    def test_minutos_horas_e_dias_e_futuro(self):
        self.assertEqual(E.idade(AGORA - dt.timedelta(minutes=59), AGORA), "há 59 min")
        self.assertEqual(E.idade(AGORA - dt.timedelta(minutes=60), AGORA), "há 1 h")
        self.assertEqual(E.idade(AGORA - dt.timedelta(hours=47, minutes=59), AGORA), "há 47 h")
        self.assertEqual(E.idade(AGORA - dt.timedelta(hours=48), AGORA), "há 2 d")
        self.assertEqual(E.idade(AGORA + dt.timedelta(hours=3), AGORA), "há 0 min")


class Itens(unittest.TestCase):
    def test_ultimo_merge_com_sha_idade_e_titulo(self):
        texto = E.ultimo_merge(ctx({("api", "repos/{owner}/{repo}/commits/develop"): (COMMIT, "")}), RAIZ, AGORA)
        self.assertEqual(texto, "aaaaaaaaa há 30 min (2026-11-26T14:30:00Z) · feat: x (#9)")

    def test_ultimo_merge_fora_da_forma_e_data_ilegivel_nao_verificaveis(self):
        for dados in ({"sha": "a"}, {**COMMIT, "commit": {"committer": {"date": "ontem"}, "message": "m"}}):
            with self.subTest(dados=dados), self.assertRaises(E.NaoVerificavel):
                E.ultimo_merge(ctx({("api", "repos/{owner}/{repo}/commits/develop"): (dados, "")}), RAIZ, AGORA)

    def test_gh_sem_saida_e_sem_stderr_diz_gh_sem_saida(self):
        with self.assertRaisesRegex(E.NaoVerificavel, "^gh sem saída$"):
            E.ultimo_merge(ctx({("api", "repos/{owner}/{repo}/commits/develop"): (None, "")}), RAIZ, AGORA)

    def test_pr_sem_rotulos_nem_checks_espera_revisao(self):
        sem_listas = {"number": 8, "title": "feat: x [afrouxa-regra: y]", "labels": None, "statusCheckRollup": None}
        self.assertEqual(E.grupo_do_pr(sem_listas), 1)
        self.assertEqual(E.grupo_do_pr({**sem_listas, "title": "feat: x"}), 0)

    def test_prs_nos_quatro_grupos(self):
        prs = [pr(1), pr(2, "fix: y [afrouxa-regra: z]"), pr(3, "fix: y [afrouxa-regra: z]", rotulos=["afrouxa-regra"]),
               pr(4, mergeable="CONFLICTING", checks=[{"conclusion": "FAILURE"}]), pr(5, checks=[{"conclusion": "FAILURE"}]),
               pr(6, checks=[{"state": "ERROR"}]), pr(7, checks=[{"conclusion": "SUCCESS"}, {"state": "PENDING"}])]
        texto = E.prs_abertos(ctx({("pr", "list"): (prs, "")}), RAIZ, AGORA)
        self.assertEqual(texto, "7 · esperando revisão 3 (#1 #3 #7) · esperando rótulo do dono 1 (#2) · em conflito 1 (#4) · "
                                "quebrados 2 (#5 #6)")

    def test_prs_lista_vazia_e_fora_da_forma(self):
        self.assertTrue(E.prs_abertos(ctx({("pr", "list"): ([], "")}), RAIZ, AGORA).startswith("0 · esperando revisão 0 ·"))
        for dados in ({"number": 1}, [{"number": "1"}]):
            with self.subTest(dados=dados), self.assertRaises(E.NaoVerificavel):
                E.prs_abertos(ctx({("pr", "list"): (dados, "")}), RAIZ, AGORA)

    def test_ultima_versao_publicada(self):
        self.assertEqual(E.ultima_versao(ctx({("release", "view"): (RELEASE, "")}), RAIZ, AGORA),
                         "v0.47.18 há 45 h (2026-11-24T18:00:00Z)")
        for dados in ([RELEASE], {"tagName": ""}):
            with self.subTest(dados=dados), self.assertRaises(E.NaoVerificavel):
                E.ultima_versao(ctx({("release", "view"): (dados, "")}), RAIZ, AGORA)

    def test_decisoes_abertas_e_a_mais_antiga(self):
        linhas = ["aberta: escopo | p1 | 2026-11-26 09:00 | a? | recomendada: —", "aberta: outro | p2 | — | b? | recomendada: —",
                  "aberta: outro | p3 | 2026-11-25 | c? | recomendada: —", "abertas: total=3"]
        self.assertEqual(E.decisoes(ctx(abertas=lambda p: (linhas, 0)), RAIZ, AGORA), "3 · a mais antiga há 36 h (2026-11-25)")
        self.assertEqual(E.decisoes(ctx(), RAIZ, AGORA), "0")
        sem_data = ["aberta: outro | p2 | — | b? | recomendada: —"]
        self.assertEqual(E.decisoes(ctx(abertas=lambda p: (sem_data, 0)), RAIZ, AGORA), "1 · idade não verificável (sem data)")

    def test_decisoes_leitura_recusada_nao_verificavel(self):
        with self.assertRaisesRegex(E.NaoVerificavel, "link simbólico"):
            E.decisoes(ctx(abertas=lambda p: (["abertas: erro: docs é link simbólico; recusado"], 1)), RAIZ, AGORA)
        with self.assertRaisesRegex(E.NaoVerificavel, "^leitura recusada$"):
            E.decisoes(ctx(abertas=lambda p: ([], 1)), RAIZ, AGORA)

    def test_plugin_da_sessao(self):
        self.assertEqual(E.plugin_da_sessao(ctx(), RAIZ, AGORA), "0.47.19")
        self.assertEqual(E.plugin_da_sessao(ctx(versao=""), RAIZ, AGORA), "não verificável (plugin.json ilegível)")


class Contador(unittest.TestCase):
    def plugin(self, corpo):
        pasta = Path(tempfile.mkdtemp(prefix="forge-status-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(pasta)], check=False))
        (pasta / "bin").mkdir()
        (pasta / "bin" / "forge-contador").write_text(corpo, encoding="utf-8")
        return pasta

    def test_primeira_linha_do_contador(self):
        texto = E.contador(ctx(plugin=self.plugin("print('0.47.20: 8 de 20')\nprint('backlog: x')\n")), RAIZ, AGORA)
        self.assertEqual(texto, "0.47.20: 8 de 20")

    def test_contador_que_falha_ou_cala_nao_verificavel(self):
        falha_com_saida = "import sys\nprint('0.1.0: 1 de 20')\nsys.exit('forge-contador: sem ref')\n"
        for corpo, motivo in ((falha_com_saida, "sem ref"), ("pass\n", "sem saída")):
            with self.subTest(corpo=corpo), self.assertRaisesRegex(E.NaoVerificavel, motivo):
                E.contador(ctx(plugin=self.plugin(corpo)), RAIZ, AGORA)

    def test_contador_lento_nao_verificavel(self):
        lento = self.plugin("import time\ntime.sleep(5)\nprint('1.0.0: 1 de 20')\n")
        antes, E.TETO_DO_CONTADOR_S = E.TETO_DO_CONTADOR_S, 0.3
        self.addCleanup(setattr, E, "TETO_DO_CONTADOR_S", antes)
        with self.assertRaisesRegex(E.NaoVerificavel, "TimeoutExpired"):
            E.contador(ctx(plugin=lento), RAIZ, AGORA)


class Executar(unittest.TestCase):
    def test_sem_rede_as_linhas_do_gh_sao_nao_verificaveis_e_rc_0(self):
        rc, saida = rodar(ctx(plugin=Path("/nao/existe")))
        self.assertEqual(rc, 0)
        linhas = saida.splitlines()
        self.assertEqual([l.split(":")[1].strip() for l in linhas], [n for n, _ in E.ITENS])
        for i in (0, 1, 2, 4):
            self.assertIn(": não verificável (", linhas[i])
        self.assertEqual(linhas[3], "status: decisões do dono abertas: 0")
        self.assertEqual(linhas[5], "status: plugin da sessão: 0.47.19")

    def test_sem_agora_vale_a_hora_local(self):
        rc, saida = rodar(ctx(), None)
        self.assertEqual(rc, 0)
        self.assertIn("status: plugin da sessão: 0.47.19", saida)

    def test_agora_sem_fuso_ou_ilegivel_sai_com_2(self):
        for agora in ("2026-11-26T12:00", "ontem"):
            with self.subTest(agora=agora):
                rc, saida = rodar(ctx(), agora)
                self.assertEqual(rc, 2)
                self.assertIn("--agora ilegível ou sem fuso", saida)


class PeloForgeCheck(unittest.TestCase):
    """O subcomando de ponta a ponta: gh falso sem rede, HOME temporário, Python isolado (-I)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-status-fc-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.tmp)], check=False))
        self.raiz, self.home = self.tmp / "projeto", self.tmp / "home"
        self.raiz.mkdir()
        (self.home / ".forge-contrib" / "docs" / "pedidos").mkdir(parents=True)
        (self.home / ".forge-contrib" / "docs" / "pedidos" / "p1.md").write_text(
            "# p1\n\n## Histórico\n- PERGUNTA AO DONO (2026-11-26 09:00): A ou B?\n", encoding="utf-8")

    def rodar(self, *extra):
        env = sem_manutencao(sem_git_herdado({"PATH": str(pasta_com_gh()) + os.pathsep + "/usr/bin:/bin", "HOME": str(self.home),
                                              "LANG": "C.UTF-8", "XDG_CACHE_HOME": str(self.tmp)}))
        return subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.raiz), "status",
                               "--agora", "2026-11-26T12:00-03:00", *extra],
                              capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, timeout=60)

    def test_sem_rede_rc_0_e_decisoes_da_raiz_com_docs_pedidos(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("status: último merge na develop: não verificável (gh falso: sem rede no teste)", r.stdout)
        self.assertIn("status: PRs abertos: não verificável (", r.stdout)
        self.assertIn("status: última versão publicada: não verificável (", r.stdout)
        self.assertIn("status: decisões do dono abertas: 1 · a mais antiga há 3 h (2026-11-26 09:00)", r.stdout)

    def test_raiz_pedidos_explicita_vence_a_da_raiz(self):
        (self.raiz / "docs" / "pedidos").mkdir(parents=True)  # sem a opção, a raiz (sem pergunta) vem primeiro
        self.assertIn("status: decisões do dono abertas: 0", self.rodar().stdout)
        r = self.rodar("--raiz-pedidos", str(self.home / ".forge-contrib"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("status: decisões do dono abertas: 1 ·", r.stdout)


if __name__ == "__main__":
    unittest.main()
