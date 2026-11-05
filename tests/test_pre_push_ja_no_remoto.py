"""PUSH-PARECER-JA-NO-REMOTO: o pre-push não roda a suíte quando o remoto já tem a ref no commit enviado.

O hook roda de verdade num repositório descartável com um remoto bare local e uma suíte que falha: se ela rodar,
o hook sai 1. O stdin traz o `remote_sha` zerado, o estado velho que o git entrega antes de outro envio terminar.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})
SUITE_FALHA = "import unittest\nclass T(unittest.TestCase):\n    def test_f(self):\n        self.fail('rodou')\n"
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
        self.c1 = self.commit("um")
        self.c2 = self.commit("dois")

    def git(self, *args, cwd=None):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd or self.repo,
                              env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def no_remoto(self, sha, ref):
        self.git("push", "-q", "origin", f"{sha}:refs/heads/{ref}")

    @staticmethod
    def linha(ref, sha, remoto=ZERO):
        return f"refs/heads/x {sha} {ref if ref.startswith('refs/') else 'refs/heads/' + ref} {remoto}\n"

    def hook(self, entrada, remoto="origin"):
        return subprocess.Popen([str(HOOK), remoto, str(self.bare)], cwd=self.repo, env=self.env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def roda(self, entrada, remoto="origin"):
        p = self.hook(entrada, remoto)
        _, erro = p.communicate(entrada, timeout=60)
        return p.returncode, erro

    def test_remoto_ja_tem_a_ref_no_mesmo_sha_ou_descendente_pula(self):
        self.no_remoto(self.c2, "melhoria/x")
        self.no_remoto(self.c2, "melhoria/y")
        for nome, entrada in (("igual", self.linha("melhoria/x", self.c2)), ("ancestral", self.linha("melhoria/x", self.c1)),
                              ("duas", self.linha("melhoria/x", self.c2) + self.linha("melhoria/y", self.c2))):
            with self.subTest(nome):
                codigo, erro = self.roda(entrada)
                self.assertEqual(codigo, 0, erro)
                self.assertIn(f"o remoto já tem o que seria enviado (melhoria/x em {self.c2[:7]}", erro)
                self.assertEqual(list(self.run_dir.iterdir()), [], "o pulo pegou a trava ou anotou prova")

    def test_sem_prova_positiva_a_suite_roda(self):
        self.no_remoto(self.c1, "melhoria/x")
        self.no_remoto(self.c2, "a/melhoria/z")
        self.no_remoto(self.c2, "outra")
        self.git("tag", "t1", self.c2)
        casos = {
            "sha diferente, local não ancestral": (self.linha("melhoria/x", self.c2), "origin"),
            "remoto inexistente": (self.linha("melhoria/x", self.c1), "naoexiste"),
            "remoto que parece opção": (self.linha("melhoria/x", self.c1), "-x"),
            "casamento pela cauda": (self.linha("melhoria/z", self.c2), "origin"),
            "ref nova com sha de outra ref": (self.linha("nova", self.c2), "origin"),
            "uma enviada e uma nova": (self.linha("outra", self.c2) + self.linha("nova", self.c2), "origin"),
            "uma enviada e uma tag": (self.linha("outra", self.c2) + self.linha("refs/tags/t1", self.c2), "origin"),
            "uma enviada e uma remoção": (self.linha("outra", self.c2) + self.linha("melhoria/x", ZERO, self.c1), "origin"),
        }
        for nome, (entrada, remoto) in casos.items():
            with self.subTest(nome):
                codigo, erro = self.roda(entrada, remoto)
                self.assertEqual(codigo, 1, erro)
                self.assertIn("testes do Forge falharam", erro)
                self.assertNotIn("o remoto já tem", erro)

    def test_envio_para_develop_segue_barrado(self):
        self.no_remoto(self.c2, "develop")
        codigo, erro = self.roda(self.linha("develop", self.c2))
        self.assertEqual(codigo, 1)
        self.assertIn("envio direto para develop bloqueado", erro)
        self.assertNotIn("o remoto já tem", erro)


if __name__ == "__main__":
    unittest.main()
