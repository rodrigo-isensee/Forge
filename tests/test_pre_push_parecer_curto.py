"""LOTE-PREPUSH-PARECER (PREPUSH-PRIMEIRO-PARECER, PARECER-PUSH-CORRIDA): o envio só de parecer é curto também logo
depois do código e não espera a fila da suíte; o envio atrás do remoto falha na hora e manda fazer `git pull --rebase`.

Cada teste roda o hook de verdade num repositório descartável: a suíte de brinquedo marca `rodou-<nome>` por módulo,
o `bin/forge-testes` é a cópia do Forge e a `origin/develop` é local. A trava é segurada por um `flock` de fora para
simular a suíte de outro agente.
"""
import os
import shutil
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
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})
ZERO = "0" * 40
BOA = ("import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_a(self):\n"
       "        pathlib.Path('rodou-{}').write_text('sim')\n")
# As quatro classes que o caminho curto roda, num módulo `test_forge` (que o mapa dá a `bin/forge-sugerir`).
FORGE = '''import unittest, pathlib
def marca(nome):
    pathlib.Path(nome).write_text("sim")
class Neutralidade(unittest.TestCase):
    def test_a(self):
        marca("rodou-neutralidade")
class Referencias(unittest.TestCase):
    def test_a(self):
        marca("rodou-referencias")
class AntiDuplicacao(unittest.TestCase):
    def test_a(self):
        marca("rodou-antiduplicacao")
class NeutralidadeDoNucleo(unittest.TestCase):
    def test_a(self):
        marca("rodou-nucleo")
class Outra(unittest.TestCase):
    def test_a(self):
        marca("rodou-outra")
'''
CURTAS = {"rodou-neutralidade", "rodou-referencias", "rodou-antiduplicacao", "rodou-nucleo"}


class PrePushParecerCurto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        self.repo = base / "repo"
        (self.repo / "tests").mkdir(parents=True)
        (self.repo / "bin").mkdir()
        shutil.copy(RAIZ / "bin" / "forge-testes", self.repo / "bin" / "forge-testes")
        self.git("init", "-q", "-b", "melhoria/x")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), FORGE_TRAVA_ESPERA="20")
        (self.repo / ".gitignore").write_text("rodou-*\n__pycache__/\n/.forge\n")
        self.base = self.commit("base", tests__test_a_py=BOA.format("a"), bin__forge_sugerir="x = 1\n",
                                tests__test_sugerir_py=BOA.format("sugerir"), tests__test_forge_py=FORGE)
        self.git("update-ref", "refs/remotes/origin/develop", self.base)
        stem = f"forge-suite-{os.getuid()}"
        self.trava = self.run_dir / f"{stem}.lock"
        self.verde = self.run_dir / f"{stem}.verde"
        self.dirigida = self.run_dir / f"{stem}.dirigida"
        self.segurador = None

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            alvo = self.repo / nome.replace("_py", ".py").replace("__", "/").replace("forge_sugerir", "forge-sugerir")
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def roda(self, local, remoto, destino="melhoria/x"):
        for p in self.repo.glob("rodou-*"):
            p.unlink()
        entrada = f"refs/heads/x {local} refs/heads/{destino} {remoto}\n"
        inicio = time.monotonic()
        r = subprocess.run([str(HOOK), "origin", "u"], cwd=self.repo, env=self.env, input=entrada,
                           capture_output=True, text=True, timeout=120)
        self.duracao = time.monotonic() - inicio
        return r.returncode, {p.name for p in self.repo.glob("rodou-*")}, r.stderr

    def segura_a_trava(self):
        """Outra suíte do Forge segura a trava (um flock de fora) até o fim do teste."""
        self.trava.touch()
        self.segurador = subprocess.Popen(["flock", str(self.trava), "sleep", "60"])
        self.addCleanup(self.segurador.wait)
        self.addCleanup(self.segurador.terminate)
        for _ in range(100):
            if subprocess.run(["flock", "-n", str(self.trava), "true"]).returncode != 0:
                return
            time.sleep(0.05)
        self.fail("o flock de fora não segurou a trava")

    def codigo_dirigido(self):
        """O envio do código de uma melhoria/*: só os módulos do mapa rodam (decisão M8) e a branch vai ao remoto."""
        codigo_sha = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        rc, marcas, erro = self.roda(codigo_sha, ZERO)
        self.assertEqual(rc, 0, erro)
        self.assertIn("rodando só os testes afetados", erro)
        self.assertNotIn("rodou-a", marcas)
        return codigo_sha

    def parecer(self, nome="p"):
        return self.commit("parecer", **{f"docs__reviews__{nome}.md": "parecer\n"})

    # E1: a causa. O envio de código dirigido não anotava prova alguma; o primeiro parecer achava a prova ausente.
    def test_primeiro_parecer_depois_do_envio_dirigido_roda_so_as_classes_curtas(self):
        codigo_sha = self.codigo_dirigido()
        rc, marcas, erro = self.roda(self.parecer(), codigo_sha)
        self.assertEqual(rc, 0, erro)
        self.assertEqual(marcas, CURTAS, "o primeiro parecer depois do código não pode rodar a suíte inteira")
        self.assertIn("só acrescenta pareceres", erro)

    def test_so_o_dirigido_verde_anota_a_prova_dirigida_e_nunca_a_da_suite_inteira(self):
        codigo_sha = self.codigo_dirigido()
        arvore = self.git("rev-parse", f"{codigo_sha}^{{tree}}")
        self.assertIn(arvore, self.dirigida.read_text().split())
        self.assertFalse(self.verde.exists(), "a prova da suíte inteira só nasce da suíte inteira")

    def test_dirigido_vermelho_nao_anota_e_o_parecer_roda_a_suite_inteira(self):
        (self.repo / "tests" / "test_sugerir.py").write_text(BOA.format("sugerir") + "        self.fail('x')\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "teste vermelho já na base")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        quebra = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        rc, _, _ = self.roda(quebra, ZERO)
        self.assertEqual(rc, 1)
        self.assertFalse(self.dirigida.exists())
        _, marcas, _ = self.roda(self.parecer(), quebra)
        self.assertIn("rodou-outra", marcas)

    def test_prova_dirigida_que_e_link_e_ignorada(self):
        codigo_sha = self.codigo_dirigido()
        conteudo = self.dirigida.read_text()
        self.dirigida.unlink()
        (self.run_dir / "real").write_text(conteudo)
        self.dirigida.symlink_to(self.run_dir / "real")
        _, marcas, _ = self.roda(self.parecer(), codigo_sha)
        self.assertIn("rodou-a", marcas)

    def test_codigo_junto_com_o_parecer_continua_rodando_o_plano_do_codigo(self):
        codigo_sha = self.codigo_dirigido()
        misto = self.commit("misto", docs__reviews__p_md="x\n", novo_txt="y\n")
        _, marcas, erro = self.roda(misto, codigo_sha)
        self.assertNotIn("só acrescenta pareceres", erro)
        self.assertIn("rodou-a", marcas)

    # E2: o envio curto não espera a fila; o pesado continua esperando.
    def test_envio_so_de_parecer_nao_espera_a_trava_da_suite_alheia(self):
        codigo_sha = self.codigo_dirigido()
        self.segura_a_trava()
        self.env["FORGE_TRAVA_ESPERA"] = "3"
        rc, marcas, erro = self.roda(self.parecer(), codigo_sha)
        self.assertEqual(rc, 0, erro)
        self.assertEqual(marcas, CURTAS)
        self.assertNotIn("esperando a vez", erro)
        arvore = self.git("rev-parse", "HEAD^{tree}")
        self.assertIn(arvore, self.verde.read_text().split(), "o parecer anota a árvore mesmo sem a trava")

    def test_envio_de_codigo_continua_esperando_a_trava_e_e_barrado_sem_a_vez(self):
        self.segura_a_trava()
        self.env["FORGE_TRAVA_ESPERA"] = "2"
        novo = self.commit("codigo", bin__forge_sugerir="x = 3\n")
        rc, marcas, erro = self.roda(novo, ZERO)
        self.assertEqual(rc, 1)
        self.assertEqual(marcas, set())
        self.assertIn("a vez não chegou", erro)

    # E1: o envio atrás do remoto falha antes da trava, com a instrução do rebase.
    def test_envio_atras_do_remoto_falha_na_hora_mandando_fazer_o_pull_rebase(self):
        codigo_sha = self.codigo_dirigido()
        remoto_andou = self.parecer("outro")
        self.git("reset", "-q", "--hard", codigo_sha)
        meu = self.parecer("meu")
        self.segura_a_trava()
        self.env["FORGE_TRAVA_ESPERA"] = "30"
        rc, marcas, erro = self.roda(meu, remoto_andou)
        self.assertEqual(rc, 1)
        self.assertEqual(marcas, set())
        self.assertIn("git pull --rebase", erro)
        self.assertNotIn("esperando a vez", erro)
        self.assertLess(self.duracao, 10)

    def test_remoto_que_andou_e_nao_esta_aqui_manda_fazer_o_pull_rebase(self):
        codigo_sha = self.codigo_dirigido()
        rc, _, erro = self.roda(self.parecer(), "1" * 40)
        self.assertEqual(rc, 1)
        self.assertIn("git pull --rebase", erro)
        self.assertNotEqual(codigo_sha, "1" * 40)


if __name__ == "__main__":
    unittest.main()
