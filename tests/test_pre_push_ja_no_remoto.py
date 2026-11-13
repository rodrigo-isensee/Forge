"""PUSH-PARECER-JA-NO-REMOTO: o pre-push pula a suíte só se o destino do push ($2, a URL de envio) já tem a ref."""
import fcntl, http.server, os, subprocess, sys, tempfile, termios, threading, time, unittest  # noqa: E401
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))
                           and k.lower() not in ("ssh_askpass", "http_proxy", "https_proxy", "all_proxy")})
AMBIENTE["FORGE_PREPUSH_SUITE"] = "afetados"  # ENVIO-LEVE: o padrão do hook não roda teste; estes testes exercitam o plano dos afetados
SUITE_FALHA = "import unittest\nclass T(unittest.TestCase):\n    def test_f(self):\n        self.fail('rodou')\n"
ZERO, RODOU, PULOU = "0" * 40, "AssertionError: rodou", "o remoto já tem o que seria enviado"
# PREPUSH-REFS (v0457): duas branches com código no mesmo envio recusam antes do pulo.
DUAS_BRANCHES = "mais de uma branch com código"


class PrePushJaNoRemoto(unittest.TestCase):
    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.run_dir, self.repo, self.bare, self.vazio = (self.base / n for n in ("run", "repo", "r.git", "v.git"))
        self.run_dir.mkdir()
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(self.base), FORGE_TRAVA_ESPERA="30",
                        no_proxy="*", NO_PROXY="*")
        for bare in (self.bare, self.vazio):
            self.git("init", "-q", "--bare", str(bare), cwd=self.base)
            remoto_sem_manutencao(bare)
        self.git("init", "-q", str(self.repo), cwd=self.base)
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_x.py").write_text(SUITE_FALHA)
        self.git("remote", "add", "origin", str(self.bare))
        self.c1, self.c2 = [self.git("commit", "-q", "--allow-empty", "-m", m) or self.git("rev-parse", "HEAD") for m in "ab"]
        mestre, self.tty = os.openpty()  # terminal de controle: sem GIT_TERMINAL_PROMPT=0 o git pede usuário nele
        self.addCleanup(lambda: (os.close(mestre), os.close(self.tty)))

    def git(self, *args, cwd=None):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd or self.repo,
                              env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    @staticmethod
    def linha(ref, sha, remoto=ZERO):
        return f"refs/heads/x {sha} {ref if ref.startswith('refs/') else 'refs/heads/' + ref} {remoto}\n"

    def roda(self, entrada, *args):
        r = subprocess.run([str(HOOK), *(args or ("origin", str(self.bare)))], cwd=self.repo, env=self.env,
                           input=entrada, capture_output=True, text=True, timeout=90, start_new_session=True,
                           pass_fds=(self.tty,), preexec_fn=lambda: fcntl.ioctl(self.tty, termios.TIOCSCTTY, 0))
        return r.returncode, r.stdout + r.stderr

    def test_pula_so_com_prova_positiva_no_destino(self):
        self.git("push", "-q", str(self.bare), f"{self.c1}:refs/heads/melhoria/x", *(f"{self.c2}:refs/{r}" for r in (
            "heads/p heads/q heads/a/refs/heads/melhoria/z heads/outra tags/t1 heads/main heads/homolog heads/develop".split())))
        c3 = self.git("--git-dir", str(self.bare), "commit-tree", "-p", self.c2, "-m", "c", f"{self.c2}^{{tree}}")
        self.git("--git-dir", str(self.bare), "update-ref", "refs/heads/w", c3)  # C-1: o remoto tem w num commit que aqui falta
        self.git("config", "remote.origin.pushurl", str(self.vazio))  # A1: a url tem o commit, a pushurl não
        self.env.update(dict.fromkeys(("FORGE_PULAR_SUITE", "FORGE_JA_NO_REMOTO", "FORGE_PULO"), "1"),
                        FORGE_REMOTO=str(self.bare), FORGE_REMOTE="origin")  # C-10: nenhuma variável liga o pulo
        dormir = [25]  # C-1: só a primeira consulta ao lento espera; sem o timeout de 20 s, o hook pendura

        class Pede(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                time.sleep(dormir.pop() if "lento" in self.path and dormir else 0)
                self.send_response(401)
                for chave, valor in (("WWW-Authenticate", 'Basic realm="x"'), ("Content-Length", "0")):
                    self.send_header(chave, valor)
                self.end_headers()
            log_message = lambda *_: None  # noqa: E731
        servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Pede)
        servidor.handle_error = lambda *_: None
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        self.addCleanup(lambda: (servidor.shutdown(), servidor.server_close()))
        http_url = f"http://127.0.0.1:{servidor.server_port}"
        p, x1, ok = self.linha("p", self.c2), self.linha("melhoria/x", self.c1), self.linha("outra", self.c2)
        casos = {  # os que pulam vêm antes: nenhum pode deixar trava, fila ou prova na pasta
            "igual": (p, (), f"{PULOU} (p em {self.c2[:7]})"),
            "ancestral": (self.linha("p", self.c1), (), f"{PULOU} (p em {self.c2[:7]})"),
            "duas refs enviadas": (p + self.linha("q", self.c2), (), DUAS_BRANCHES),
            "sha diferente, local não ancestral": (self.linha("melhoria/x", self.c2), (), RODOU),
            "destino inexistente": (x1, ("origin", str(self.base / "nada.git")), RODOU),
            "destino que parece opção": (x1, ("origin", "-x"), RODOU),
            "pushurl sem o commit, url com ele (A1)": (ok, ("origin", str(self.vazio)), RODOU),
            "destino pede credencial": (ok, ("origin", f"{http_url}/pede.git"), RODOU),
            "destino lento": (ok, ("origin", f"{http_url}/lento.git"), RODOU),
            "casamento pela cauda": (self.linha("melhoria/z", self.c2), (), RODOU),
            "ref nova com sha de outra ref": (self.linha("nova", self.c2), (), RODOU),
            "objeto remoto ausente aqui": (self.linha("w", self.c2), (), RODOU),
            "uma enviada e uma nova": (ok + self.linha("nova", self.c2), (), DUAS_BRANCHES),
            "uma enviada e uma tag": (ok + self.linha("refs/tags/t1", self.c2), (), RODOU),
            "uma enviada e uma remoção": (ok + self.linha("melhoria/x", ZERO, self.c1), (), RODOU),
            "--suite": (ok, ("--suite",), RODOU),
            "--status": (ok, ("--status",), "nenhuma suíte do Forge rodando"),
            "stdin vazio (T-6)": ("", (), "nada a enviar"),
            "não fast-forward": (self.linha("melhoria/x", self.c1, self.c2), (), "envio não fast-forward para melhoria/x"),
            **{r: (self.linha(r, self.c2), (), f"envio direto para {r} bloqueado") for r in ("main", "homolog", "develop")},
        }
        for nome, (entrada, args, esperado) in casos.items():
            with self.subTest(nome):
                inicio, pula = time.monotonic(), esperado.startswith(PULOU)
                codigo, saida = self.roda(entrada, *args)
                self.assertEqual((codigo, esperado in saida, PULOU in saida), (int(bool(entrada) and not pula), True, pula), saida)
                self.assertLess(time.monotonic() - inicio, 24 if "lento" in nome else 15)
                self.assertTrue(not pula or list(self.run_dir.iterdir()) == [], "o pulo pegou a trava ou anotou prova")
        texto = HOOK.read_text()  # C-10: nem o pulo nem as suas chamadas leem FORGE_*
        chamadas = [ln for ln in texto.splitlines() if "ja_no_remoto \"" in ln]
        self.assertNotIn("FORGE_", texto.split("\nja_no_remoto() {")[1].split("\n}\n")[0] + "".join(chamadas), chamadas)

    def test_destino_ganha_a_ref_durante_a_espera_pula_e_solta_fila_e_trava(self):
        trava, fila = (self.run_dir / f"forge-suite-{os.getuid()}.{s}" for s in ("lock", "fila"))
        resultado, fim = [], time.monotonic() + 15
        hook = threading.Thread(target=lambda: resultado.append(self.roda(self.linha("melhoria/x", self.c2))))
        with open(trava, "a") as dono:  # outra suíte segura a trava; o hook entra na fila
            fcntl.flock(dono, fcntl.LOCK_EX)
            hook.start()
            while not any(fila.glob("[0-9]*")) and time.monotonic() < fim:
                time.sleep(0.05)
            self.assertTrue(any(fila.glob("[0-9]*")), "o hook não entrou na fila")
            self.git("push", "-q", str(self.bare), f"{self.c2}:refs/heads/melhoria/x")
        hook.join(90)
        self.assertEqual((resultado[0][0], f"{PULOU} (melhoria/x em {self.c2[:7]})" in resultado[0][1]), (0, True), resultado)
        self.assertEqual(list(fila.iterdir()), [], "a senha da fila ficou")
        self.assertEqual(trava.read_text(), "", "o pulo gravou na trava como se a suíte fosse rodar")
