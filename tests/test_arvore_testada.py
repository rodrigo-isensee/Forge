"""EST-M7, E3a-1: a decisão pura de scripts/arvore-testada.py (C-1 e C-3 de docs/security/ameacas/versao-040.md).
Sobre dicionários, sem git nem rede; os números citados são os casos de abuso do modelo de ameaças."""
import copy
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

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


class LinhaDeComando(unittest.TestCase):
    def test_rodar_o_arquivo_sai_1_ate_a_e3a_2(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("a suíte roda inteira", r.stderr)


if __name__ == "__main__":
    unittest.main()
