"""PUSH-PARECER-JA-NO-REMOTO: o pre-push não roda a suíte quando o remoto já tem a ref no commit enviado. O hook roda
num repositório descartável com remoto bare e uma suíte que falha; o stdin traz o `remote_sha` velho (zerado)."""
import fcntl
import http.server
import os
import re
import subprocess
import sys
import tempfile
import termios
import threading
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

    def roda(self, entrada, remoto="origin", *args, **kw):
        r = subprocess.run([str(HOOK), *(args or (remoto, str(self.bare)))], cwd=self.repo, env=self.env,
                           input=entrada, capture_output=True, text=True, timeout=90, **kw)
        return r.returncode, r.stdout + r.stderr

    def suite_rodou(self, codigo, saida):
        self.assertEqual(codigo, 1, saida)
        self.assertIn("AssertionError: rodou", saida)
        self.assertNotIn("o remoto já tem", saida)

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

    def test_c1_remoto_lento_prompt_ou_objeto_ausente_a_suite_roda(self):
        # C-1: o remoto lento responde (com a ref no sha) só depois de 25 s; sem o timeout de 20 s o hook pularia.
        self.no_remoto(self.c2, "melhoria/x")
        lento = self.repo.parent / "lento.sh"
        lento.write_text(f"#!/bin/sh\n[ -e {lento}.1 ] && exit 1\n: > {lento}.1; sleep 25\n"
                         'exec git-upload-pack "$@"\n')
        lento.chmod(0o755)
        self.git("remote", "add", "lento", str(self.bare))
        self.git("config", "remote.lento.uploadpack", str(lento))
        inicio = time.monotonic()
        self.suite_rodou(*self.roda(self.linha("melhoria/x", self.c2), "lento"))
        self.assertLess(time.monotonic() - inicio, 24)
        # C-1: objeto remoto ausente aqui (outro clone avançou a ref): sem prova de ancestral, a suíte roda.
        outro = self.repo.parent / "outro"
        self.git("clone", "-q", "-b", "melhoria/x", str(self.bare), str(outro), cwd=self.repo.parent)
        self.git("commit", "-q", "--allow-empty", "-m", "c", cwd=outro)
        self.git("push", "-q", "origin", "HEAD:refs/heads/melhoria/x", cwd=outro)
        self.suite_rodou(*self.roda(self.linha("melhoria/x", self.c2)))

    def test_c1_prompt_de_credencial_nao_pendura_o_hook(self):
        class Pede(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(401)
                self.send_header("WWW-Authenticate", 'Basic realm="x"')
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *_):
                pass
        servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Pede)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        self.addCleanup(lambda: (servidor.shutdown(), servidor.server_close()))
        for k in ("SSH_ASKPASS", "GIT_ASKPASS", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
            self.env.pop(k, None)
        self.env.update(no_proxy="*", NO_PROXY="*")
        # Terminal de controle de verdade: sem GIT_TERMINAL_PROMPT=0 o git pede usuário nele e espera o timeout.
        mestre, escravo = os.openpty()
        self.addCleanup(lambda: (os.close(mestre), os.close(escravo)))
        url = f"http://127.0.0.1:{servidor.server_port}/r.git"
        inicio = time.monotonic()
        self.suite_rodou(*self.roda(self.linha("melhoria/x", self.c2), "", url, url, start_new_session=True,
                                    pass_fds=(escravo,),
                                    preexec_fn=lambda: fcntl.ioctl(escravo, termios.TIOCSCTTY, 0)))
        self.assertLess(time.monotonic() - inicio, 15)

    def test_c5_t5_recusas_vem_antes_do_pulo_e_suite_status_nao_pulam(self):
        for ref in ("main", "homolog", "melhoria/x"):
            self.no_remoto(self.c2, ref)
        for ref in ("main", "homolog"):
            with self.subTest(ref):
                codigo, saida = self.roda(self.linha(ref, self.c2))
                self.assertEqual(codigo, 1)
                self.assertIn(f"envio direto para {ref} bloqueado", saida)
        with self.subTest("não fast-forward"):
            codigo, saida = self.roda(self.linha("melhoria/x", self.c1, self.c2))
            self.assertEqual(codigo, 1)
            self.assertIn("envio não fast-forward para melhoria/x", saida)
        with self.subTest("--suite"):
            self.suite_rodou(*self.roda(self.linha("melhoria/x", self.c2), "", "--suite"))
        with self.subTest("--status"):
            codigo, saida = self.roda(self.linha("melhoria/x", self.c2), "", "--status")
            self.assertEqual((codigo, saida.strip()), (1, "nenhuma suíte do Forge rodando"))

    def test_t6_stdin_vazio_nao_passa_pelo_pulo(self):
        codigo, saida = self.roda("")
        self.assertEqual(codigo, 0)
        self.assertIn("nada a enviar", saida)
        self.assertNotIn("o remoto já tem", saida)

    def test_c10_nenhuma_variavel_forge_liga_o_pulo(self):
        self.no_remoto(self.c2, "melhoria/x")
        vazio = self.repo.parent / "vazio.git"
        self.git("init", "-q", "--bare", str(vazio))
        remoto_sem_manutencao(vazio)
        self.git("remote", "add", "vazio", str(vazio))
        self.env.update({k: "1" for k in ("FORGE_PULAR_SUITE", "FORGE_JA_NO_REMOTO", "FORGE_PULO")},
                        FORGE_REMOTO="origin", FORGE_REMOTE="origin")
        self.suite_rodou(*self.roda(self.linha("melhoria/x", self.c2), "vazio"))
        texto = HOOK.read_text()
        pulo = re.search(r"^ja_no_remoto\(\) \{\n.*?^\}\n", texto, re.S | re.M).group(0)
        chamadas = [ln for ln in texto.splitlines() if "ja_no_remoto " in ln and "()" not in ln]
        self.assertEqual(len(chamadas), 2, chamadas)
        self.assertNotIn("FORGE_", pulo + "\n".join(chamadas))
