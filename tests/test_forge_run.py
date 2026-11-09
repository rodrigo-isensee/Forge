"""S5 (0.44.2): `forge-check rodar <slug> -- <cmd>` grava a execução como prova (.forge/run/<slug>/run.json) e o PQ `cmd` que a cita
é lido do JSON na conferência (sem rodar de novo); PQ com pipe segue no modo de antes."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")


def git(pasta, *args):
    return subprocess.run(["git", "-C", str(pasta), "-c", "user.name=t", "-c", "user.email=t@t", *args], capture_output=True, text=True,
                          env=sem_manutencao(dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1"))).stdout.strip()


class Rodar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-run-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git(self.tmp, "init", "-q")
        git(self.tmp, "commit", "-q", "--allow-empty", "-m", "x")

    def rodar(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "rodar", *args], capture_output=True, text=True,
                           cwd=self.tmp, env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout

    def run_json(self, slug):
        return json.loads((self.tmp / ".forge" / "run" / slug / "run.json").read_text(encoding="utf-8"))

    def test_grava_rc_tempo_por_passo_e_log_completo(self):
        rc, out = self.rodar("a1", "--", sys.executable, "-c", "print('x' * 5000)", ";", sys.executable, "-c", "import sys; sys.exit(3)")
        self.assertEqual(rc, 3, out)
        d = self.run_json("a1")
        self.assertEqual(d["rc"], 3)
        self.assertEqual([p["rc"] for p in d["passos"]], [0, 3])
        self.assertTrue(all(isinstance(p["segundos"], float) for p in d["passos"]))
        self.assertEqual(d["head"], git(self.tmp, "rev-parse", "HEAD"))
        log = (self.tmp / ".forge" / "run" / "a1" / d["passos"][0]["log"]).read_text()
        self.assertEqual(log, "x" * 5000 + "\n", "log completo, sem corte")

    def test_tira_o_separador_do_inicio(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        try:
            import forge_run  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        self.assertEqual(forge_run.rodar(self.tmp, "a0", ["--", "true"]), 0)
        self.assertEqual(self.run_json("a0")["argv"], ["true"])

    def test_para_no_primeiro_passo_que_falha(self):
        self.rodar("a2", "--", sys.executable, "-c", "raise SystemExit(1)", ";", "touch", "nao-devia")
        self.assertEqual(len(self.run_json("a2")["passos"]), 1)
        self.assertFalse((self.tmp / "nao-devia").exists())

    def test_pasta_run_link_recusa(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        (self.tmp / ".forge").mkdir()
        (self.tmp / ".forge" / "run").symlink_to(fora)
        self.assertEqual(self.rodar("a6", "--", "true")[0], 2)
        self.assertEqual(list(fora.iterdir()), [])

    def test_sem_shell(self):
        rc, _ = self.rodar("a3", "--", "echo", "$HOME", "|", "cat")
        self.assertEqual(rc, 0)
        self.assertEqual((self.tmp / ".forge/run/a3/passo-1.log").read_text(), "$HOME | cat\n")

    def test_slug_repetido_ou_invalido_recusa(self):
        self.assertEqual(self.rodar("a4", "--", "true")[0], 0)
        rc, out = self.rodar("a4", "--", "false")
        self.assertEqual(rc, 2)
        self.assertIn("já usado", out)
        self.assertEqual(self.run_json("a4")["argv"], ["true"], "a prova gravada não se sobrescreve")
        self.assertEqual(self.rodar("../fora", "--", "true")[0], 2)
        self.assertEqual(self.rodar("a5", "--", "true", ";")[0], 2, "passo vazio")


class PqCitaORun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = SourceFileLoader("forge_check_run", FORGE_CHECK).load_module()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-run-pq-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git(self.tmp, "init", "-q")
        git(self.tmp, "commit", "-q", "--allow-empty", "-m", "x")
        self.head = git(self.tmp, "rev-parse", "HEAD")

    def gravar(self, slug, argv, rc, log, head=None):
        pasta = self.tmp / ".forge" / "run" / slug
        pasta.mkdir(parents=True)
        (pasta / "passo-1.log").write_text(log, encoding="utf-8")
        (pasta / "run.json").write_text(json.dumps({"argv": argv, "head": head or self.head, "rc": rc,
                                                    "passos": [{"passo": 1, "argv": argv, "rc": rc, "segundos": 0.1, "log": "passo-1.log"}]}))

    def conferir(self, pq, so_leitura=False):
        texto = f"## Pronto quando\n- PQ-1 (cmd): `{pq}` · espera: rc=0 e contém 'OK'\n"
        return self.fc.conferir_provas(self.tmp, texto, "melhoria/x", self.head, self.tmp, so_leitura)

    def test_le_o_json_e_confere_a_espera_sem_rodar(self):
        self.gravar("t1", ["python3", "-m", "unittest", "tests.x"], 0, "Ran 3 tests\nOK\n")
        (linha, reprova), = self.conferir("forge-check rodar t1 -- python3 -m unittest tests.x", so_leitura=True)
        self.assertFalse(reprova, linha)
        self.assertIn("run t1: ok", linha)

    def test_rc_ou_log_que_diverge_reprova(self):
        self.gravar("t2", ["python3", "-m", "unittest", "tests.x"], 1, "FAILED\n")
        (linha, reprova), = self.conferir("forge-check rodar t2 -- python3 -m unittest tests.x")
        self.assertTrue(reprova, linha)

    def test_run_de_outro_comando_ou_commit_ou_ausente_reprova(self):
        self.gravar("t3", ["python3", "-m", "unittest", "tests.y"], 0, "OK\n")
        self.gravar("t4", ["python3", "-m", "unittest", "tests.x"], 0, "OK\n", head="0" * 40)
        for pq, motivo in (("forge-check rodar t3 -- python3 -m unittest tests.x", "outro comando"),
                           ("forge-check rodar t4 -- python3 -m unittest tests.x", "outro commit"),
                           ("forge-check rodar t9 -- python3 -m unittest tests.x", "ausente")):
            (linha, reprova), = self.conferir(pq)
            self.assertTrue(reprova, pq)
            self.assertIn(motivo, linha)

    def test_slug_invalido_e_outro_programa_nao_leem_run(self):
        (linha, reprova), = self.conferir("forge-check rodar ../x -- python3 -m unittest tests.x")
        self.assertTrue(reprova, linha)
        self.assertIn("slug inválido", linha)
        self.assertIsNone(self.fc.modulo_do_bin("forge_run").citado(["git", "rodar", "t1", "--", "x"]))

    def test_pq_com_pipe_segue_no_modo_de_antes(self):
        (linha, reprova), = self.conferir("git log | head -1")
        self.assertFalse(reprova, linha)
        self.assertIn("não reexecutada", linha)


if __name__ == "__main__":
    unittest.main()
