"""Pacote de stack python (0.45.0): o forge-init e o forge adotar aceitam `--stack python`, e o adotar o detecta."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PACOTE = RAIZ / "stacks" / "python"


class StackPython(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="stack-python-"))
        (self.tmp / "home").mkdir()
        self.env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        self.env.update(HOME=str(self.tmp / "home"), GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="T",
                        GIT_COMMITTER_EMAIL="t@t", PATH="/usr/bin:/bin")
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.git("init", "-q", "-b", "main")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.proj), *args], env=self.env, check=True, capture_output=True, text=True)

    def test_forge_init_aceita_a_stack_python_com_pronto_e_pesados_do_pacote(self):
        r = subprocess.run(["bash", str(RAIZ / "bin" / "forge-init"), "--stack", "python", str(self.proj)], env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        claude = (self.proj / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("python -m pytest", claude)
        config = json.loads((self.proj / ".forge" / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["pesados"], json.loads((PACOTE / "pesados.json").read_text(encoding="utf-8")))

    def test_forge_adotar_detecta_python_e_o_pronto_que_o_projeto_ja_tem(self):
        (self.proj / "pyproject.toml").write_text("[project]\nname = \"x\"\n\n[tool.pytest.ini_options]\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "inicial")
        r = subprocess.run([sys.executable, str(RAIZ / "bin" / "forge-adotar"), "--so-ler"], cwd=self.proj, env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("stack: python (detectada", r.stdout)
        self.assertIn("pronto: python -m pytest (o projeto já tem (pyproject.toml))", r.stdout)
        r = subprocess.run([sys.executable, str(RAIZ / "bin" / "forge-adotar"), "--so-ler", "--stack", "python"],
                           cwd=self.proj, env=self.env, capture_output=True, text=True)
        self.assertIn("stack: python (escolhida", r.stdout)

    def test_pacote_listado_no_plugin(self):
        plugin = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("./stacks/python/agents/python-backend.md", plugin["agents"])
        self.assertIn("./stacks/python/skills/python-backend", plugin["skills"])


if __name__ == "__main__":
    unittest.main()
