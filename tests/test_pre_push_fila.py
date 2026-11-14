"""FILA-SUITE-ESPERA: quem espera a suíte vê a posição e quem está na frente, ouve o aviso de trava velha (sem nada ser
liberado) e o envio barrado pela espera fica registrado em <trava>.barrados.

Roda o hook de verdade num repositório descartável com a trava em XDG_RUNTIME_DIR temporário e HOME temporário.
"""
import fcntl
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))})
SUITE = "import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_roda(self):\n        pathlib.Path('rodou').write_text('sim')\n"
SEGURA = "import fcntl, sys, time\nf = open(sys.argv[1], 'a')\nfcntl.flock(f, fcntl.LOCK_EX)\nprint('pronto', flush=True)\ntime.sleep(600)\n"
MEU_NS = re.sub(r"\D", "", os.readlink("/proc/self/ns/pid"))
SENHA = "0000000001000000000-777"  # chegou em 1970-01-01 00:00:01 UTC, pid 777
FORA_DA_FAIXA = "1000000000000000000000000000-778"  # o `date` não converte: a hora sai "?"


class FilaDaSuite(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.run_dir, self.repo, home = base / "run", base / "repo", base / "home"
        for pasta in (self.run_dir, self.repo / "tests", home):
            pasta.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True, env=AMBIENTE)
        (self.repo / "tests" / "test_x.py").write_text(SUITE)
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(home), TZ="UTC",
                        FORGE_PREPUSH_SUITE="afetados", FORGE_TRAVA_ESPERA="2", FORGE_FILA_INTERVALO="60")
        self.trava = self.run_dir / f"forge-suite-{os.getuid()}.lock"
        self.barrados = self.run_dir / f"forge-suite-{os.getuid()}.barrados"

    def segura(self, caminho):
        p = subprocess.Popen([sys.executable, "-I", "-c", SEGURA, str(caminho)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(lambda: (p.kill(), p.wait(), p.stdout.close()))
        self.assertEqual(p.stdout.readline().strip(), "pronto")
        return p

    def dona(self, pid, ns=MEU_NS, idade=0):
        """A trava presa por outro processo, com o texto `pid <pid> ns <ns>` e o mtime de `idade` segundos atrás."""
        self.trava.write_text(f"pid {pid} ns {ns} desde 01:02:03\n")
        os.utime(self.trava, (time.time() - idade,) * 2)
        return self.segura(self.trava)

    def roda(self, *args, **extra):
        p = subprocess.Popen([str(HOOK), *args], cwd=self.repo, env=dict(self.env, **extra), stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, erro = p.communicate(f"refs/heads/x {'1' * 40} refs/heads/melhoria/x {'0' * 40}\n", timeout=60)
        return p.returncode, erro, p.pid

    @staticmethod
    def morto():
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_posicao_e_quem_esta_na_frente_ao_entrar(self):
        self.dona(4242)
        fila = self.run_dir / f"forge-suite-{os.getuid()}.fila"
        fila.mkdir(mode=0o700)
        for senha in (SENHA, FORA_DA_FAIXA):
            (fila / senha).write_text("")
            self.segura(fila / senha)
        codigo, erro, pid = self.roda()
        self.assertEqual(codigo, 1, erro)
        linhas = [linha for linha in erro.splitlines() if "fila da suíte" in linha]
        self.assertEqual(len(linhas), 1, erro)  # intervalo de 60 s: só a linha da entrada
        self.assertIn(f"posição 3; trava com pid 4242 ns {MEU_NS} desde 01:02:03; na frente", linhas[0])
        self.assertTrue(linhas[0].endswith("na frente: pid 777 desde 00:00:01, pid 778 desde ?"), linhas[0])
        self.assertNotIn(f"pid {pid} desde", linhas[0])
        self.assertFalse((self.repo / "rodou").exists())

    def test_fila_que_e_link_nao_e_listada(self):
        alvo = self.run_dir / "alvo"
        alvo.mkdir()
        (alvo / SENHA).write_text("")
        self.segura(alvo / SENHA)
        (self.run_dir / f"forge-suite-{os.getuid()}.fila").symlink_to(alvo)
        self.dona(4242)
        codigo, erro, _ = self.roda()
        self.assertEqual(codigo, 1, erro)
        self.assertIn("posição 1; trava com pid 4242", erro)
        self.assertNotIn("na frente", erro)

    def test_atualiza_a_cada_intervalo_e_intervalo_invalido_e_recusado(self):
        self.dona(4242)
        _, erro, _ = self.roda(FORGE_TRAVA_ESPERA="3", FORGE_FILA_INTERVALO="1")
        self.assertGreaterEqual(erro.count("fila da suíte"), 2, erro)
        codigo, erro, _ = self.roda(FORGE_FILA_INTERVALO="1m")
        self.assertEqual(codigo, 1)
        self.assertIn("FORGE_FILA_INTERVALO deve ser", erro)
        self.assertNotIn("pre-push: entrou", erro)  # recusado antes de entrar na fila

    def test_dona_morta_avisa_uma_vez_e_nao_libera(self):
        morto = self.morto()
        dona = self.dona(morto)
        codigo, erro, _ = self.roda(FORGE_TRAVA_ESPERA="3", FORGE_FILA_INTERVALO="1")
        self.assertEqual(codigo, 1, erro)
        self.assertEqual(erro.count("parece velha"), 1, erro)
        self.assertIn(f"dona pid {morto} morta", erro)
        self.assertIn(f"ps -o pid,etime,args -p {morto}", erro)
        self.assertIsNone(dona.poll())
        with self.trava.open() as f:  # a trava segue presa pela dona: nada a liberou
            self.assertRaises(BlockingIOError, fcntl.flock, f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.assertFalse((self.repo / "rodou").exists())

    def test_dona_viva_ou_de_outro_namespace_nao_avisa(self):
        for pid, ns in ((os.getpid(), MEU_NS), (self.morto(), "1"), ("x1", MEU_NS)):
            with self.subTest(pid=pid, ns=ns):
                dona = self.dona(pid, ns)
                _, erro, _ = self.roda()
                self.assertNotIn("parece velha", erro)
                dona.kill()
                dona.wait()

    def test_trava_sem_troca_de_dona_ha_mais_de_35_min_avisa(self):
        self.dona(os.getpid(), idade=36 * 60)
        _, erro, _ = self.roda()
        self.assertIn("sem troca de dona há 36 min", erro)
        self.assertIn(".githooks/pre-push --status", erro)

    def test_barrado_registra_uma_linha_por_envio(self):
        self.dona(4242)
        inicio = time.monotonic()
        self.roda()
        self.assertLess(time.monotonic() - inicio, 20, "a espera passou do FORGE_TRAVA_ESPERA")
        self.roda("--suite")
        linhas = self.barrados.read_text().splitlines()
        self.assertEqual(len(linhas), 2, linhas)
        self.assertRegex(linhas[0], r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d push 2$")
        self.assertTrue(linhas[1].endswith(" suite 2"), linhas)

    def test_registro_que_e_link_nao_e_seguido(self):
        alvo = self.run_dir / "alvo"
        alvo.write_text("")
        self.barrados.symlink_to(alvo)
        self.dona(4242)
        codigo, erro, _ = self.roda()
        self.assertEqual(codigo, 1, erro)
        self.assertEqual(alvo.read_text(), "")


if __name__ == "__main__":
    unittest.main()
