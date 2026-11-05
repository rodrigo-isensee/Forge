"""PUSH-PARECER-JA-NO-REMOTO: o pre-push não roda a suíte quando o remoto já tem a ref no commit enviado.

O hook roda de verdade num repositório descartável com remoto bare local e uma suíte que falha (se rodar, o hook
sai 1). O stdin traz o `remote_sha` zerado, o estado velho que o git entrega antes de outro envio terminar."""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})
SUITE_FALHA = "import unittest\nclass T(unittest.TestCase):\n    def test_f(self):\n        self.fail('rodou')\n"
SEGURA = "import fcntl,sys,time\nf=open(sys.argv[1],'a')\nfcntl.flock(f,fcntl.LOCK_EX)\nprint('ok',flush=True)\ntime.sleep(600)"
ZERO = "0" * 40


class PrePushJaNoRemoto(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.run_dir, self.repo, self.bare = base / "run", base / "repo", base / "remoto.git"
        self.run_dir.mkdir()
        (base / "home").mkdir()
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(base / "home"), FORGE_TRAVA_ESPERA="30")
        self.git("init", "-q", "--bare", str(self.bare), cwd=base)
        remoto_sem_manutencao(self.bare)
        self.git("init", "-q", str(self.repo), cwd=base)
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_x.py").write_text(SUITE_FALHA)
        self.git("remote", "add", "origin", str(self.bare))
        self.git("add", "-A")
        self.c1, self.c2 = [self.git("commit", "-q", "--allow-empty", "-m", m) or self.git("rev-parse", "HEAD") for m in "ab"]

    def git(self, *args, cwd=None):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd or self.repo,
                              env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    def no_remoto(self, sha, ref):
        self.git("push", "-q", "origin", f"{sha}:refs/heads/{ref}")

    @staticmethod
    def linha(ref, sha, remoto=ZERO):
        return f"refs/heads/x {sha} {ref if ref.startswith('refs/') else 'refs/heads/' + ref} {remoto}\n"

    def roda(self, entrada, remoto="origin"):
        r = subprocess.run([str(HOOK), remoto, str(self.bare)], cwd=self.repo, env=self.env, input=entrada,
                           capture_output=True, text=True, timeout=60)
        return r.returncode, r.stderr

    def test_remoto_ja_tem_a_ref_no_mesmo_sha_ou_descendente_pula(self):
        self.no_remoto(self.c2, "melhoria/x")
        self.no_remoto(self.c2, "melhoria/y")
        x, y = self.linha("melhoria/x", self.c2), self.linha("melhoria/y", self.c2)
        for nome, entrada in (("igual", x), ("ancestral", self.linha("melhoria/x", self.c1)), ("duas", x + y)):
            with self.subTest(nome):
                codigo, erro = self.roda(entrada)
                self.assertEqual(codigo, 0, erro)
                self.assertIn(f"o remoto já tem o que seria enviado (melhoria/x em {self.c2[:7]}", erro)
                self.assertEqual(list(self.run_dir.iterdir()), [], "o pulo pegou a trava ou anotou prova")

    def test_sem_prova_positiva_a_suite_roda(self):
        for sha, ref in ((self.c1, "melhoria/x"), (self.c2, "a/refs/heads/melhoria/z"), (self.c2, "outra")):
            self.no_remoto(sha, ref)
        self.git("tag", "t1", self.c2)
        self.git("push", "-q", "origin", "refs/tags/t1")
        enviada = self.linha("outra", self.c2)
        casos = {
            "sha diferente, local não ancestral": (self.linha("melhoria/x", self.c2), "origin"),
            "remoto inexistente": (self.linha("melhoria/x", self.c1), "naoexiste"),
            "remoto que parece opção": (self.linha("melhoria/x", self.c1), "-x"),
            "casamento pela cauda": (self.linha("melhoria/z", self.c2), "origin"),
            "ref nova com sha de outra ref": (self.linha("nova", self.c2), "origin"),
            "uma enviada e uma nova": (enviada + self.linha("nova", self.c2), "origin"),
            "uma enviada e uma tag": (enviada + self.linha("refs/tags/t1", self.c2), "origin"),
            "uma enviada e uma remoção": (enviada + self.linha("melhoria/x", ZERO, self.c1), "origin"),
        }
        for nome, (entrada, remoto) in casos.items():
            with self.subTest(nome):
                codigo, erro = self.roda(entrada, remoto)
                self.assertEqual(codigo, 1, erro)
                self.assertIn("testes do Forge falharam", erro)

    def test_envio_para_develop_segue_barrado(self):
        self.no_remoto(self.c2, "develop")
        codigo, erro = self.roda(self.linha("develop", self.c2))
        self.assertEqual(codigo, 1)
        self.assertIn("envio direto para develop bloqueado", erro)
        self.assertNotIn("o remoto já tem", erro)

    def test_remoto_ganha_a_ref_durante_a_espera_pula_e_solta_fila_e_trava(self):
        trava, fila = (self.run_dir / f"forge-suite-{os.getuid()}.{s}" for s in ("lock", "fila"))
        dono = subprocess.Popen([sys.executable, "-I", "-c", SEGURA, str(trava)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(lambda: (dono.kill(), dono.wait(), dono.stdout.close()))
        self.assertEqual(dono.stdout.readline().strip(), "ok")
        p = subprocess.Popen([str(HOOK), "origin", str(self.bare)], cwd=self.repo, env=self.env, text=True,
                             stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        p.stdin.write(self.linha("melhoria/x", self.c2))
        p.stdin.close()
        fim = time.monotonic() + 15
        while not any(fila.glob("[0-9]*")) and time.monotonic() < fim:
            time.sleep(0.05)
        self.assertTrue(any(fila.glob("[0-9]*")), "o hook não entrou na fila")
        self.no_remoto(self.c2, "melhoria/x")
        dono.kill()
        self.assertEqual(p.wait(timeout=60), 0)
        erro = p.stderr.read()
        p.stderr.close()
        self.assertIn(f"o remoto já tem o que seria enviado (melhoria/x em {self.c2[:7]})", erro)
        self.assertEqual(list(fila.iterdir()), [], "a senha da fila ficou")
        self.assertEqual(trava.read_text(), "", "o pulo gravou na trava como se a suíte fosse rodar")


if __name__ == "__main__":
    unittest.main()
