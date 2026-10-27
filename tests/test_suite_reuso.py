"""K6 (METADE-K6): scripts/suite-paralela.py reaproveita a execução verde sobre a mesma árvore (hash pelo git)."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "suite-paralela.py"
ENV = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_", "CI"))}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")


def carregar():
    spec = importlib.util.spec_from_file_location("suite_paralela_reuso", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Reuso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = carregar()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self.git("init", "-q")
        for caminho in ("bin/x", "docs/reviews/p.md", "docs/qa/p.md", "docs/devops/p.md", "docs/security/p.md",
                        "changelog.d/p.md", "docs/outro.md"):
            self.escrever(caminho, "v1\n")
        self.commitar()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True, capture_output=True, text=True)

    def escrever(self, caminho, texto):
        alvo = self.repo / caminho
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8")

    def commitar(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def carimbar(self):
        self.s.gravar_carimbo(self.repo, self.s.hash_da_arvore(self.repo))

    def reusa(self, **env):
        return self.s.reuso(self.repo, {**env})

    def test_mesmo_hash_reusa(self):
        self.carimbar()
        igual = self.reusa()
        self.assertEqual(igual[0], self.s.hash_da_arvore(self.repo))

    def test_sem_carimbo_roda(self):
        self.assertIsNone(self.reusa())

    def test_hash_diferente_roda(self):
        self.carimbar()
        self.escrever("bin/x", "v2\n")
        self.commitar()
        self.assertIsNone(self.reusa())

    def test_arvore_suja_roda(self):
        self.carimbar()
        self.escrever("bin/x", "sujo\n")
        self.assertIsNone(self.reusa())
        self.assertIsNone(self.s.hash_da_arvore(self.repo))

    def test_arquivo_novo_nao_versionado_roda(self):
        self.carimbar()
        self.escrever("bin/novo", "n\n")
        self.assertIsNone(self.reusa())

    def test_python_diferente_roda(self):
        self.s.gravar_carimbo(self.repo, self.s.hash_da_arvore(self.repo), python="outro 0.0")
        self.assertIsNone(self.reusa())

    def test_carimbo_corrompido_roda(self):
        self.carimbar()
        for lixo in ("{nao json", "[]", '{"hash": 1}', ""):
            with self.subTest(lixo=lixo):
                self.s.caminho_do_carimbo(self.repo).write_text(lixo, encoding="utf-8")
                self.assertIsNone(self.reusa())

    def test_sem_reuso_forca_a_execucao(self):
        self.carimbar()
        self.assertIsNone(self.reusa(FORGE_SUITE_SEM_REUSO="1"))
        self.assertIsNotNone(self.reusa(FORGE_SUITE_SEM_REUSO="0"))

    def test_ci_nunca_reusa(self):
        self.carimbar()
        self.assertIsNone(self.reusa(CI="true"))

    def test_caminho_de_parecer_e_changelog_nao_muda_o_hash(self):
        antes = self.s.hash_da_arvore(self.repo)
        for caminho in ("docs/reviews/p.md", "docs/qa/p.md", "docs/devops/p.md", "docs/security/p.md",
                        "changelog.d/p.md", "docs/reviews/novo.md", "changelog.d/novo.md"):
            self.escrever(caminho, "mudou\n")
        self.commitar()
        self.assertEqual(self.s.hash_da_arvore(self.repo), antes)

    def test_arquivo_de_codigo_ou_doc_comum_muda_o_hash(self):
        for caminho in ("bin/x", "docs/outro.md", "bin/y", "docs/reviewsx/p.md"):
            with self.subTest(caminho=caminho):
                antes = self.s.hash_da_arvore(self.repo)
                self.escrever(caminho, "mudou\n")
                self.commitar()
                self.assertNotEqual(self.s.hash_da_arvore(self.repo), antes)

    def test_chamada_a_mao_imprime_reusa_e_ok(self):
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "suite-paralela.py").write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
        self.commitar()
        mod = self.s
        mod.gravar_carimbo(self.repo, mod.hash_da_arvore(self.repo))
        r = subprocess.run([sys.executable, str(self.repo / "scripts" / "suite-paralela.py")], cwd=self.repo,
                           env=ENV, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.strip().splitlines()
        self.assertTrue(linhas[0].startswith("suite: reusa "), linhas)
        self.assertEqual(linhas[-1], "OK")
        r = subprocess.run([sys.executable, str(self.repo / "scripts" / "suite-paralela.py")], cwd=self.repo,
                           env={**ENV, "FORGE_SUITE_SEM_REUSO": "1"}, capture_output=True, text=True)
        self.assertNotIn("suite: reusa", r.stdout)
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
