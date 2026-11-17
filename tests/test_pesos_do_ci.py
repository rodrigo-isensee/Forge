"""CI-RAPIDO (v047, A2 do parecer de segurança): `scripts/pesos-do-ci.py` refaz os pesos com as anotações de tempo das pernas do CI.

A leitura da API é injetada (sem rede). Classe do defeito: peso vindo de quem não deve (PR, fork, execução vermelha, perna
de outra parte), unidade inventada, número absurdo (NaN, negativo, acima do teto) ou conjunto parcial de pernas mexendo na
partição; e o script escrever no repositório sozinho.
"""
import importlib.util
import json
import math
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "pesos-do-ci.py"
REPO = "dono/forge"
CONHECIDAS = {"test_a", "test_b", "test_b.K"}


def carregar():
    spec = importlib.util.spec_from_file_location("pesos_do_ci", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def execucao(id_=1, **muda):
    base = {"id": id_, "event": "push", "head_branch": "develop", "path": ".github/workflows/ci.yml",
            "repository": {"full_name": REPO}, "head_repository": {"full_name": REPO}, "status": "completed",
            "conclusion": "success"}
    return {**base, **muda}


def job(id_, python="3.12", k=1, n=2, run_id=1, **muda):
    base = {"id": id_, "run_id": run_id, "conclusion": "success",
            "name": f"suíte (push na develop, python {python}, parte {k}/{n})"}
    return {**base, **muda}


def nota(parte="1/2", python="3.12", t=None, titulo=None, **muda):
    mensagem = {"v": 1, "parte": parte, "python": python, "bloco": [1, 1], "t": {"test_a": 10.0} if t is None else t}
    return {"title": titulo or f"forge-tempos {parte} bloco 1/1", "message": json.dumps({**mensagem, **muda})}


class FalsaApi:
    """GET por caminho: runs, jobs de cada run e anotações de cada job."""

    def __init__(self, execucoes, jobs_por_run, notas_por_job):
        self.execucoes, self.jobs, self.notas, self.pedidos = execucoes, jobs_por_run, notas_por_job, []

    def __call__(self, caminho):
        self.pedidos.append(caminho)
        if "/actions/workflows/ci.yml/runs" in caminho:
            return {"workflow_runs": self.execucoes}
        if "/jobs?" in caminho:
            return {"jobs": self.jobs.get(int(caminho.split("/runs/")[1].split("/")[0]), [])}
        if "/check-runs/" in caminho:
            return self.notas.get(int(caminho.split("/check-runs/")[1].split("/")[0]), [])
        raise AssertionError(caminho)


def api_completa(**muda_nota):
    """Um run válido com as 2 pernas do 3.12 (test_a 10 s e test_b 4 s) e as 2 do 3.14 (test_a 14 s)."""
    jobs = {1: [job(11, "3.12", 1), job(12, "3.12", 2), job(21, "3.14", 1), job(22, "3.14", 2)]}
    notas = {11: [nota("1/2", "3.12", {"test_a": 10.0})], 12: [nota("2/2", "3.12", {"test_b": 4.0})],
             21: [nota("1/2", "3.14", {"test_a": 14.0})], 22: [nota("2/2", "3.14", {"test_b": 6.0})]}
    return jobs, notas


class Leitura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar()

    def coleta(self, execucoes, jobs, notas):
        return self.p.coletar(REPO, FalsaApi(execucoes, jobs, notas), CONHECIDAS)[0]

    def test_run_valido_junta_os_dois_pythons_pela_media(self):
        jobs, notas = api_completa()
        amostras = self.coleta([execucao()], jobs, notas)
        self.assertEqual(self.p.juntar(amostras), {"test_a": 12.0, "test_b": 5.0})

    def test_execucao_que_nao_e_push_na_develop_do_proprio_repositorio_nao_entra(self):  # A2: PR e fork
        jobs, notas = api_completa()
        ruins = {"evento de PR": {"event": "pull_request"}, "branch de PR": {"head_branch": "melhoria/x"},
                 "outro workflow": {"path": ".github/workflows/outro.yml"},
                 "fork": {"head_repository": {"full_name": "fork/forge"}},
                 "outro repositório": {"repository": {"full_name": "outro/forge"}},
                 "vermelha": {"conclusion": "failure"}, "cancelada": {"conclusion": "cancelled"},
                 "em andamento": {"status": "in_progress"}, "sem id": {"id": "1"}}
        for nome, muda in ruins.items():
            with self.subTest(nome):
                self.assertEqual(self.coleta([execucao(**muda)], jobs, notas), {})

    def test_perna_vermelha_pulada_ou_de_outro_nome_nao_entra(self):
        for muda in ({"conclusion": "failure"}, {"conclusion": "skipped"}, {"name": "suíte (python 3.12, parte 1/2)"},
                     {"name": "suíte (push na develop, python 3.12, parte 3/2)"}, {"run_id": 99}):
            with self.subTest(muda):
                jobs, notas = api_completa()
                jobs[1][0] = {**jobs[1][0], **muda}
                self.assertNotIn(("3.12", "test_a"), self.coleta([execucao()], jobs, notas))  # a perna 1 caiu: conjunto parcial

    def test_conjunto_parcial_de_pernas_nao_entra(self):
        jobs, notas = api_completa()
        del jobs[1][1]  # falta a parte 2/2 do 3.12
        amostras = self.coleta([execucao()], jobs, notas)
        self.assertEqual({py for py, _ in amostras}, {"3.14"})

    def test_anotacao_fora_do_formato_e_descartada_inteira(self):
        base = {"test_a": 10.0}
        ruins = {"unidade inventada": {"test_a": 10.0, "test_inventado": 1.0},
                 "nome fora do alfabeto": {"test_a": 1.0, "a::b": 1.0}, "NaN": {"test_a": float("nan")},
                 "infinito": {"test_a": math.inf}, "negativo": {"test_a": -1.0}, "acima do teto": {"test_a": 901.0},
                 "texto": {"test_a": "10"}, "booleano": {"test_a": True}, "vazio": {}}
        for nome, t in ruins.items():
            with self.subTest(nome):
                jobs, notas = api_completa()
                notas[11] = [{"title": "forge-tempos 1/2 bloco 1/1", "message": json.dumps({"v": 1, "parte": "1/2",
                              "python": "3.12", "bloco": [1, 1], "t": t}, allow_nan=True)}]
                self.assertNotIn(("3.12", "test_a"), self.coleta([execucao()], jobs, notas))
        outras = {"parte de outra perna": nota("2/2", "3.12", base), "python de outra perna": nota("1/2", "3.14", base),
                  "versão": nota("1/2", "3.12", base, v=2), "título alheio": nota("1/2", "3.12", base, titulo="aviso"),
                  "JSON ilegível": {"title": "forge-tempos 1/2", "message": "{quebrado"},
                  "sem mensagem": {"title": "forge-tempos 1/2"}, "não é objeto": {"title": "forge-tempos 1/2", "message": "[1]"}}
        for nome, anotacao in outras.items():
            with self.subTest(nome):
                jobs, notas = api_completa()
                notas[11] = [anotacao]
                self.assertNotIn(("3.12", "test_a"), self.coleta([execucao()], jobs, notas))

    def test_blocos_da_mesma_perna_somam(self):
        jobs, notas = api_completa()
        notas[11] = [nota("1/2", "3.12", {"test_a": 10.0}), nota("1/2", "3.12", {"test_b": 2.0}, bloco=[2, 2])]
        amostras = self.coleta([execucao()], jobs, notas)
        self.assertEqual(amostras[("3.12", "test_b")], [2.0, 4.0])

    def test_so_as_n_ultimas_execucoes_validas(self):
        jobs, notas = api_completa()
        runs = [execucao(1), execucao(2), execucao(3)]
        for r in (2, 3):
            jobs[r] = [{**j, "run_id": r} for j in jobs[1]]
        api = FalsaApi(runs, jobs, notas)
        resumo = self.p.coletar(REPO, api, CONHECIDAS, 2)[1]
        self.assertIn("2 execução(ões) válida(s)", resumo)
        self.assertFalse([c for c in api.pedidos if "/runs/3/jobs" in c])


class Pesos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar()

    def test_gerar_mantem_o_atual_sem_medida_e_tira_o_que_nao_e_mais_unidade(self):
        novos, sem = self.p.gerar({"test_a": 1.0, "test_b": 2.0, "test_velho": 9.0}, {"test_a": 5.5}, {"test_a", "test_b", "test_c"})
        self.assertEqual(novos, {"test_a": 5.5, "test_b": 2.0})
        self.assertEqual(sem, ["test_b"])

    def test_juntar_arredonda_e_ordena(self):
        self.assertEqual(self.p.juntar({("3.12", "test_b"): [1.0, 2.0], ("3.14", "test_b"): [4.0], ("3.12", "test_a"): [1.04]}),
                         {"test_a": 1.0, "test_b": 2.8})


class Principal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar()

    def roda(self, *args, api=None, conhecidas=CONHECIDAS, env=None):
        jobs, notas = api_completa()
        api = api or FalsaApi([execucao()], jobs, notas)
        with unittest.mock.patch.object(self.p.sys, "stderr", new_callable=__import__("io").StringIO) as erro, \
                unittest.mock.patch.object(self.p.sys, "stdout", new_callable=__import__("io").StringIO) as saida:
            codigo = self.p.main(list(args), env or {}, api, conhecidas)
        return codigo, saida.getvalue(), erro.getvalue()

    def test_sem_saida_escreve_so_no_stdout_e_nao_toca_nos_pesos_do_repositorio(self):
        antes = self.p.PESOS.read_bytes()
        codigo, saida, erro = self.roda("--repo", REPO)
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(json.loads(saida), {"test_a": 12.0, "test_b": 5.0})  # a conhecida sem medida só entra se já tinha peso
        self.assertEqual(self.p.PESOS.read_bytes(), antes)

    def test_saida_em_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / "pesos.json"
            self.assertEqual(self.roda("--repo", REPO, "--saida", str(alvo))[0], 0)
            self.assertEqual(json.loads(alvo.read_text()), {"test_a": 12.0, "test_b": 5.0})

    def test_sem_amostra_valida_nao_gera_nada(self):
        api = FalsaApi([execucao(event="pull_request")], *api_completa())
        codigo, saida, erro = self.roda("--repo", REPO, api=api)
        self.assertEqual((codigo, saida), (1, ""))
        self.assertIn("nenhuma amostra válida", erro)

    def test_repo_ou_execucoes_fora_do_formato_e_uso_invalido(self):
        for args in (("--repo", "sem-barra"), ("--repo", "a/b;c"), ("--repo", REPO, "--execucoes", "0"),
                     ("--repo", REPO, "--execucoes", "31"), ()):
            with self.subTest(args):
                self.assertEqual(self.roda(*args)[0], 2)

    def test_erro_da_api_sai_sem_detalhe_e_sem_o_token(self):
        def falha(_caminho):
            raise OSError("Authorization: Bearer ghp_segredo")

        codigo, _, erro = self.roda("--repo", REPO, api=falha, env={"GH_TOKEN": "ghp_segredo"})
        self.assertEqual(codigo, 1)
        self.assertNotIn("ghp_", erro)
        self.assertIn("OSError", erro)

    def test_leitor_manda_o_token_so_no_cabecalho(self):
        visto = {}

        def abre(pedido, timeout):
            visto.update(pedido.header_items())
            visto["url"] = pedido.full_url
            raise OSError

        with unittest.mock.patch.object(self.p.urllib.request, "urlopen", abre):
            with self.assertRaises(OSError):
                self.p.leitor_da_api({"GH_TOKEN": "t0k", "GITHUB_API_URL": "https://api.exemplo/"})("repos/x/y")
        self.assertEqual(visto["Authorization"], "Bearer t0k")
        self.assertEqual(visto["url"], "https://api.exemplo/repos/x/y")


class SemEscritaNoRepositorio(unittest.TestCase):
    def test_o_script_so_escreve_em_saida_e_nunca_chama_git_nem_gh(self):  # R-MAIN: nenhum caminho grava na árvore
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(texto.count(".write_text("), 1)
        for proibido in ("subprocess", "os.system", "git commit", "git push", "gh api"):
            self.assertNotIn(proibido, texto)


if __name__ == "__main__":
    unittest.main()
