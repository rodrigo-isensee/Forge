"""D2 do PR-EM-MINUTOS: o pre-push de um push que só acrescenta pareceres sobre código já testado roda só as
classes de teste que leem pareceres; qualquer outra coisa roda a suíte inteira (falha fechada).

Cada teste roda o hook de verdade, num repositório descartável com uma suíte mínima de quatro classes
(as três dos pareceres e uma outra), para não disparar a suíte do Forge de dentro dela.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
ZERO = "0" * 40

SUITE = '''import unittest, pathlib
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
class Outra(unittest.TestCase):
    def test_a(self):
        marca("rodou-outra")
'''
CURTAS = ("rodou-neutralidade", "rodou-referencias", "rodou-antiduplicacao")


class PrePushSoParecer(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        self.repo = base / "repo"
        (self.repo / "tests").mkdir(parents=True)
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), FORGE_TRAVA_ESPERA="20")
        (self.repo / "tests" / "test_forge.py").write_text(SUITE)
        (self.repo / ".gitignore").write_text("rodou-*\n__pycache__/\n")
        self.codigo = self.commit("codigo")

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            alvo = self.repo / nome.replace("__", "/")
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def limpa_marcas(self):
        for p in self.repo.glob("rodou-*"):
            p.unlink()

    def roda(self, local, remoto, destino="melhoria/x"):
        self.limpa_marcas()
        entrada = f"refs/heads/x {local} refs/heads/{destino} {remoto}\n"
        r = subprocess.run([str(HOOK), "origin", "u"], cwd=self.repo, env=self.env, input=entrada,
                           capture_output=True, text=True, timeout=120)
        marcas = {p.name for p in self.repo.glob("rodou-*")}
        return r.returncode, marcas, r.stderr

    def verde(self):
        """Primeiro push da branch (ref nova): suíte inteira e anota a árvore verde."""
        codigo, marcas, erro = self.roda(self.codigo, ZERO)
        self.assertEqual(codigo, 0, erro)
        self.assertIn("rodou-outra", marcas)

    def commit_parecer(self, pasta="reviews"):
        return self.commit("parecer", **{f"docs__{pasta}__p.md": "parecer\n"})

    def test_so_parecer_roda_so_as_classes_curtas(self):
        self.verde()
        novo = self.commit_parecer()
        codigo, marcas, erro = self.roda(novo, self.codigo)
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, set(CURTAS))

    def test_as_quatro_pastas_valem(self):
        self.verde()
        remoto = self.codigo
        for pasta in ("reviews", "security", "qa", "devops"):
            with self.subTest(pasta):
                novo = self.commit_parecer(pasta)
                codigo, marcas, erro = self.roda(novo, remoto)
                self.assertEqual(codigo, 0, erro)
                self.assertEqual(marcas, set(CURTAS))
                remoto = novo

    def test_cadeia_de_pareceres_continua_curta(self):
        self.verde()
        p1 = self.commit_parecer("reviews")
        self.assertEqual(self.roda(p1, self.codigo)[1], set(CURTAS))
        p2 = self.commit_parecer("qa")
        self.assertEqual(self.roda(p2, p1)[1], set(CURTAS))

    def test_parecer_mais_codigo_roda_a_suite_inteira(self):
        self.verde()
        novo = self.commit("misto", docs__reviews__p="x\n", src__app="y\n")
        codigo, marcas, erro = self.roda(novo, self.codigo)
        self.assertEqual(codigo, 0, erro)
        self.assertIn("rodou-outra", marcas)

    def test_arquivo_fora_das_quatro_pastas_roda_a_suite_inteira(self):
        self.verde()
        for caminho in ("docs__outra__p.md", "docs__reviews_x.md", "README.md"):
            with self.subTest(caminho):
                novo = self.commit("fora", **{caminho: "x\n"})
                _, marcas, _ = self.roda(novo, self.codigo)
                self.assertIn("rodou-outra", marcas)

    def test_prova_ausente_roda_a_suite_inteira(self):
        # nenhuma suíte verde antes: não há árvore anotada
        novo = self.commit_parecer()
        codigo, marcas, erro = self.roda(novo, self.codigo)
        self.assertEqual(codigo, 0, erro)
        self.assertIn("rodou-outra", marcas)

    def test_remoto_com_arvore_nao_anotada_roda_a_suite_inteira(self):
        self.verde()
        intermediario = self.commit("sem prova", src__app="y\n")  # nunca testado pelo hook
        novo = self.commit_parecer()
        _, marcas, _ = self.roda(novo, intermediario)
        self.assertIn("rodou-outra", marcas)

    def test_ref_nova_roda_a_suite_inteira(self):
        self.verde()
        novo = self.commit_parecer()
        _, marcas, _ = self.roda(novo, ZERO)
        self.assertIn("rodou-outra", marcas)

    def test_arvore_suja_roda_a_suite_inteira(self):
        self.verde()
        novo = self.commit_parecer()
        (self.repo / "solto.txt").write_text("sem commit")
        _, marcas, _ = self.roda(novo, self.codigo)
        self.assertIn("rodou-outra", marcas)

    def test_commit_enviado_diferente_do_head_roda_a_suite_inteira(self):
        self.verde()
        novo = self.commit_parecer()
        self.commit_parecer("qa")
        _, marcas, _ = self.roda(novo, self.codigo)
        self.assertIn("rodou-outra", marcas)

    def test_suite_vermelha_nao_anota_a_prova(self):
        (self.repo / "tests" / "test_forge.py").write_text(SUITE + "\nclass Quebra(unittest.TestCase):\n"
                                                           "    def test_a(self):\n        self.fail('x')\n")
        quebrado = self.commit("quebrado")
        codigo, _, _ = self.roda(quebrado, ZERO)
        self.assertEqual(codigo, 1)
        novo = self.commit_parecer()
        codigo, marcas, _ = self.roda(novo, quebrado)
        self.assertEqual(codigo, 1)
        self.assertIn("rodou-outra", marcas)

    def test_mudanca_em_tests_roda_a_suite_inteira(self):
        self.verde()
        (self.repo / "tests" / "test_forge.py").write_text(
            SUITE.replace('marca("rodou-referencias")', 'self.fail("de proposito")'))
        quebrado = self.commit_parecer()  # o commit leva também o teste alterado: fora das 4 pastas
        _, marcas, _ = self.roda(quebrado, self.codigo)
        self.assertIn("rodou-outra", marcas)

    def test_varias_refs_rodam_a_suite_inteira(self):
        self.verde()
        novo = self.commit_parecer()
        self.limpa_marcas()
        entrada = (f"refs/heads/x {novo} refs/heads/a {self.codigo}\n"
                   f"refs/heads/x {novo} refs/heads/b {self.codigo}\n")
        r = subprocess.run([str(HOOK), "origin", "u"], cwd=self.repo, env=self.env, input=entrada,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.repo / "rodou-outra").exists())

    def test_prova_que_e_link_e_ignorada(self):
        self.verde()
        prova = self.run_dir / f"forge-suite-{os.getuid()}.verde"
        conteudo = prova.read_text()
        prova.unlink()
        (self.run_dir / "real").write_text(conteudo)
        prova.symlink_to(self.run_dir / "real")
        novo = self.commit_parecer()
        _, marcas, _ = self.roda(novo, self.codigo)
        self.assertIn("rodou-outra", marcas)


if __name__ == "__main__":
    unittest.main()
