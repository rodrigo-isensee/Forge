"""EST-M7 (E3a-1 e SP4 da 0.43.3): a decisão pura de scripts/arvore-testada.py (C-1 e C-3 de docs/security/ameacas/versao-040.md).
Sobre dicionários, sem git nem rede; os números citados são os casos de abuso do modelo de ameaças."""
import copy
import http.server
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "arvore-testada.py"
_spec = importlib.util.spec_from_file_location("arvore_testada", SCRIPT)
at = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(at)

REPO, D = "dono/forge", "a" * 40
CI, REL = f"{REPO}/.github/workflows/ci.yml@refs/heads/x", f"{REPO}/.github/workflows/release.yml@refs/heads/main"


def chamar(f, *args):
    try:
        return f(*args)
    except Exception as erro:  # o contrato é não lançar: entrada estranha não prova (C-7)
        return "lançou", type(erro).__name__


def env(evento="pull_request", base="homolog", head="develop", head_repo=REPO, ref="", wf=CI):
    return {"REPO": REPO, "EVENTO": evento, "BASE_REF": base, "HEAD_REF": head, "HEAD_REPO": head_repo, "REF": ref,
            "GITHUB_WORKFLOW_REF": wf}


class EventoElegivel(unittest.TestCase):
    def test_lista_branca_sai_verdadeiro(self):
        for e in (env(), env(base="main", head="homolog"), env("push", ref="refs/heads/homolog"),
                  env("push", ref="refs/heads/main"), env("push", ref="refs/heads/main", wf=REL)):
            with self.subTest(e):
                self.assertEqual(at.evento_elegivel(e)[0], True)
                self.assertTrue(at.evento_elegivel(e)[1].endswith(": elegível"))

    def test_fora_da_lista_sai_falso(self):  # casos 9 e 4 (fork), PR para a develop, push da develop, dispatch, tag
        for e in (env(base="develop", head="homolog"), env(head="melhoria/x"), env(head_repo="fork/forge"),
                  env(base="main", head="develop"), env("push", ref="refs/heads/develop"), env("push", ref="refs/tags/develop"),
                  env("workflow_dispatch", ref="refs/heads/main"), env("push", ref="refs/heads/homolog", wf=REL),
                  env(wf=REL), env(wf="outro/forge/.github/workflows/ci.yml@x"), env(wf=CI.replace("ci.yml", "outro.yml")),
                  {**env(), "REPO": None}, {**env(), "GITHUB_WORKFLOW_REF": 3}, {}, None, {**env(), "EVENTO": None},
                  env(wf=".github/workflows/ci.yml@x"), {**env(head_repo=""), "REPO": "", "GITHUB_WORKFLOW_REF": "/.github/workflows/ci.yml@x"}):
            with self.subTest(e):
                self.assertFalse(chamar(at.evento_elegivel, e)[0])
        self.assertTrue(at.evento_elegivel(env(base="develop"))[1].endswith(": fora da lista"))
        self.assertEqual(at.evento_elegivel({**env(), "EVENTO": None})[1], "(sem evento)  em .github/workflows/ci.yml: fora da lista")

    def test_subclasse_de_str_nao_passa_por_str(self):  # campo exige o tipo exato
        class Texto(str):
            pass
        self.assertFalse(at.evento_elegivel({k: Texto(v) for k, v in env().items()})[0])


def execucao(**muda):
    e = {"id": 7, "run_attempt": 2, "event": "push", "head_branch": "develop", "head_sha": D, "status": "completed",
         "path": ".github/workflows/ci.yml", "repository": {"full_name": REPO}, "head_repository": {"full_name": REPO}}
    return {**e, **muda}


def job(**muda):
    return {"name": "checagem rápida (push na develop)", "conclusion": "success", "head_sha": D, "run_id": 7,
            "run_attempt": 2, **muda}


class ProvaValida(unittest.TestCase):
    def prova(self, execucoes=None, jobs=None, d=D, python="3.12"):
        return chamar(at.prova_valida, [execucao()] if execucoes is None else execucoes,
                      {7: [job()]} if jobs is None else jobs, d, python, REPO)

    def test_prova_completa_sai_verdadeiro_com_run_e_job(self):
        self.assertEqual(self.prova(), (True, "develop aaaaaaa, run 7, job checagem rápida (push na develop)"))
        nome = "checagem rápida (push na develop, python 3.14)"
        self.assertTrue(self.prova(jobs={7: [job(), job(name=nome)]}, python="3.14")[0])

    def test_execucao_que_nao_prova_sai_falso(self):  # casos 1 a 4 e 6 (status)
        for muda in ({"event": "workflow_dispatch"}, {"event": "pull_request"}, {"path": ".github/workflows/outro.yml"},
                     {"head_repository": {"full_name": "fork/forge"}}, {"repository": {"full_name": "fork/forge"}},
                     {"status": "in_progress"}, {"head_branch": "homolog"}, {"head_sha": "b" * 40}, {"id": "7"},
                     {"id": True}, {"run_attempt": None}, {"repository": None}):
            with self.subTest(muda):
                self.assertFalse(self.prova([execucao(**muda)])[0])

    def test_job_que_nao_prova_sai_falso(self):  # casos 5 e 6
        for jobs in ({7: [job(conclusion="failure")]}, {7: [job(conclusion="cancelled")]}, {7: [job(conclusion="skipped")]},
                     {7: [job(run_attempt=1)]}, {7: [job(run_attempt=1), job(conclusion="failure")]}, {7: [job(), job()]},
                     {7: [job(head_sha="b" * 40)]}, {7: [job(run_id=8)]}, {7: [job(name="bateria")]}, {8: [job()]},
                     {7: [{k: v for k, v in job().items() if k != "conclusion"}]}, {7: None}, {7: [job(run_id=7.0)]}):
            with self.subTest(jobs):
                self.assertFalse(self.prova(jobs=copy.deepcopy(jobs))[0])
        self.assertFalse(self.prova([execucao(run_attempt=1)], {7: [job(run_attempt=True)]})[0])  # True == 1, mas bool não é int

    def test_entrada_fora_do_formato_sai_falso(self):
        for args in ({"python": "3.13"}, {"python": "3.14"}, {"d": "A" * 40}, {"d": D[:7]}, {"d": None},
                     {"execucoes": {}}, {"jobs": []}, {"execucoes": [execucao(head_sha="")], "jobs": {7: [job(head_sha="")]}, "d": ""}):
            with self.subTest(args):
                self.assertFalse(self.prova(**args)[0])
        self.assertFalse(at.prova_valida([execucao()], {7: [job()]}, D, "3.12", "dono/forge x")[0])


ARVORE, OUTRA = "e" * 40, "f" * 40


def ler_falso(execucoes, jobs, chamadas=None):
    """`ler(caminho)` da API sem rede: runs do commit pedido (pelo head_sha da consulta) e jobs por id."""
    def ler(caminho):
        (chamadas if chamadas is not None else []).append(caminho)
        if "/jobs" in caminho:
            return {"jobs": jobs.get(int(caminho.split("/runs/")[1].split("/")[0]), [])}
        sha = caminho.split("head_sha=")[1].split("&")[0]
        return {"workflow_runs": [e for e in execucoes if e.get("head_sha") == sha]}
    return ler


class NomesDaProva(unittest.TestCase):
    def test_jobs_de_prova_sao_os_nomes_das_rapidas_do_ci(self):  # test_suite_partes confere o lado do ci.yml
        self.assertEqual(at.JOBS_DE_PROVA, {"3.12": "checagem rápida (push na develop)",
                                            "3.14": "checagem rápida (push na develop, python 3.14)"})


class Candidatos(unittest.TestCase):
    def test_so_commits_com_a_mesma_arvore_na_ordem_e_sem_repetir(self):
        log = f"{'1' * 40} {ARVORE}\n{'2' * 40} {OUTRA}\n{D} {ARVORE}\n{D} {ARVORE}\nlixo\n{'3' * 39} {ARVORE}\n"
        self.assertEqual(at.candidatos(ARVORE, log), ["1" * 40, D])

    def test_limite_e_entrada_fora_do_formato(self):
        log = "".join(f"{str(n) * 40} {ARVORE}\n" for n in range(1, 10))
        self.assertEqual(len(at.candidatos(ARVORE, log)), at.LIMITE_DE_CANDIDATOS)
        for arvore, entrada in ((ARVORE[:7], log), (None, log), (ARVORE, None), (ARVORE.upper(), log)):
            self.assertEqual(at.candidatos(arvore, entrada), [])


class Provar(unittest.TestCase):
    """SP4: a prova é da ÁRVORE: commit de mesma tree-sha no HEAD e o job de prova dele verde na develop."""

    def provar(self, log=None, execucoes=None, jobs=None, e=None, python="3.12", chamadas=None):
        return chamar(at.provar, e or env(), python, ARVORE, f"{'9' * 40} {ARVORE}\n{D} {ARVORE}\n" if log is None else log,
                      ler_falso([execucao()] if execucoes is None else execucoes, {7: [job()]} if jobs is None else jobs, chamadas))

    def test_merge_de_promocao_com_a_mesma_arvore_da_develop_prova(self):
        chamadas = []
        ok, motivo = self.provar(chamadas=chamadas)
        self.assertTrue(ok, motivo)
        self.assertEqual(motivo, f"árvore {ARVORE[:7]} igual à de develop aaaaaaa, run 7, job checagem rápida (push na develop)")
        self.assertIn(f"repos/{REPO}/actions/runs?head_sha={D}&event=push&branch=develop&per_page=100", chamadas)
        self.assertIn(f"repos/{REPO}/actions/runs/7/jobs?per_page=100", chamadas)

    def test_arvore_diferente_nao_prova_mesmo_com_o_job_verde(self):  # a prova é da árvore, não do commit
        ok, motivo = self.provar(log=f"{D} {OUTRA}\n")
        self.assertFalse(ok)
        self.assertIn("nenhum commit", motivo)

    def test_job_vermelho_ou_de_outro_python_nao_prova(self):
        self.assertFalse(self.provar(jobs={7: [job(conclusion="failure")]})[0])
        self.assertFalse(self.provar(python="3.14")[0])
        nome = "checagem rápida (push na develop, python 3.14)"
        self.assertTrue(self.provar(jobs={7: [job(), job(name=nome)]}, python="3.14")[0])

    def test_evento_fora_da_lista_nao_le_a_api(self):
        chamadas = []
        ok, motivo = self.provar(e=env(base="develop", head="melhoria/x"), chamadas=chamadas)
        self.assertFalse(ok)
        self.assertTrue(motivo.endswith("fora da lista"))
        self.assertEqual(chamadas, [])

    def test_execucao_de_outro_workflow_nao_tem_jobs_lidos(self):
        chamadas = []
        self.assertFalse(self.provar(execucoes=[execucao(path=".github/workflows/catraca.yml")], chamadas=chamadas)[0])
        self.assertFalse([c for c in chamadas if "/jobs" in c])

    def test_resposta_estranha_da_api_nao_prova(self):
        for resposta in (None, [], {"workflow_runs": None}, {"workflow_runs": [None]}, {"workflow_runs": "x"}):
            with self.subTest(resposta=resposta):
                self.assertFalse(chamar(at.provar, env(), "3.12", ARVORE, f"{D} {ARVORE}\n", lambda c, r=resposta: r)[0])


class ServidorFalso(http.server.BaseHTTPRequestHandler):
    """A API do GitHub para a linha de comando: runs e jobs fixos; `status` != 200 responde erro; guarda o cabeçalho."""
    execucoes, jobs, status, vistos = [], {}, 200, []

    def do_GET(self):  # noqa: N802 (nome do http.server)
        type(self).vistos.append((self.path, self.headers.get("Authorization")))
        corpo = json.dumps(ler_falso(self.execucoes, self.jobs)(self.path.lstrip("/"))).encode()
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args):
        pass


class LinhaDeComando(unittest.TestCase):
    """O script de verdade (git e HTTP), num repositório temporário e com a API num servidor local."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="arvore-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.amb = sem_manutencao({"PATH": os.environ["PATH"], "HOME": str(self.tmp), "GIT_CONFIG_GLOBAL": "/dev/null",
                                   "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
        self.git("init", "-q", "-b", "develop")
        (self.tmp / "a.txt").write_text("a\n")
        self.git("add", "a.txt")
        self.git("commit", "-qm", "a")
        self.d = self.git("rev-parse", "HEAD")
        self.git("checkout", "-qb", "homolog")
        self.git("commit", "-q", "--allow-empty", "-m", "merge da develop na homolog (mesma árvore)")
        ServidorFalso.execucoes = [execucao(head_sha=self.d)]
        ServidorFalso.jobs = {7: [job(head_sha=self.d)]}
        ServidorFalso.status, ServidorFalso.vistos = 200, []
        self.servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ServidorFalso)
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        self.addCleanup(self.servidor.server_close)
        self.addCleanup(self.servidor.shutdown)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.tmp, env=self.amb, capture_output=True, text=True, check=True).stdout.strip()

    def roda(self, *args, **muda):
        e = {**self.amb, **env("push", ref="refs/heads/homolog"), "GH_TOKEN": "segredo-do-teste",
             "GITHUB_API_URL": f"http://127.0.0.1:{self.servidor.server_port}", **muda}
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=self.tmp, env=e, capture_output=True, text=True)

    def test_prova_completa_sai_0_e_usa_o_token(self):
        r = self.roda("--python", "3.12")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("arvore-testada: provada: árvore", r.stdout)
        self.assertNotIn("segredo-do-teste", r.stdout + r.stderr)
        self.assertTrue(ServidorFalso.vistos)
        self.assertTrue(all(h == "Bearer segredo-do-teste" for _, h in ServidorFalso.vistos), ServidorFalso.vistos)

    def test_sem_prova_sai_1_e_a_suite_roda(self):
        ServidorFalso.jobs = {7: [job(head_sha=self.d, conclusion="failure")]}
        r = self.roda("--python", "3.12")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("a suíte roda inteira", r.stdout)

    def test_erro_da_api_sai_1_sem_detalhe(self):
        ServidorFalso.status = 500
        r = self.roda("--python", "3.12")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("erro ao ler a prova (HTTPError)", r.stdout)
        self.assertNotIn("segredo-do-teste", r.stdout + r.stderr)

    def test_arvore_mudada_sai_1(self):
        (self.tmp / "a.txt").write_text("b\n")
        self.git("commit", "-qam", "muda")
        self.assertEqual(self.roda("--python", "3.12").returncode, 1)

    def test_evento_fora_da_lista_e_python_fora_do_formato_saem_1(self):
        self.assertEqual(self.roda("--python", "3.12", EVENTO="workflow_dispatch").returncode, 1)
        self.assertEqual(self.roda("--python", "3.12; x").returncode, 1)
        self.assertEqual(ServidorFalso.vistos, [])

    def test_fora_de_um_repositorio_git_sai_1(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT)], cwd="/", capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin", **env("push", ref="refs/heads/main")})
        self.assertEqual(r.returncode, 1)
        self.assertIn("a suíte roda inteira", r.stdout)


if __name__ == "__main__":
    unittest.main()
