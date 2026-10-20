"""DV-4: a checagem de release roda no PR para a main e no PR develop -> homolog (só se a versão subiu). Sem rede."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "conferir-release.py"
CI = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


def passo_de_release():
    m = re.search(r"(?m)^      - name: release exige.*?(?=^      - name: )", CI, re.S)
    assert m, "passo de release não encontrado no ci.yml"
    return m.group(0)


class PassoNoCI(unittest.TestCase):
    def test_uma_so_funcao_chamada_na_main_e_na_homolog(self):
        passo = passo_de_release()
        self.assertIn("github.base_ref == 'main'", passo)
        self.assertIn("github.base_ref == 'homolog'", passo)
        self.assertEqual(CI.count("release exige versão nova"), 1)  # um passo só, sem texto duplicado
        self.assertNotIn("a <= b", CI)  # a regra mora no script, não inline
        self.assertEqual(len(re.findall(r"scripts/conferir-release\.py --base", passo)), 2)

    def test_condicao_da_homolog_e_so_na_homolog(self):
        passo = passo_de_release()
        com, sem = [l for l in passo.splitlines() if "conferir-release.py" in l]
        self.assertIn("--so-se-versao-mudou", com)
        self.assertNotIn("--so-se-versao-mudou", sem)  # a main segue sem condição
        self.assertRegex(passo, r'if \[ "\$BASE_REF" = homolog \]')
        self.assertLess(passo.index("--so-se-versao-mudou"), passo.index("else"))

    def test_entrada_nao_confiavel_so_por_env(self):
        run = passo_de_release().split("run:")[1]
        self.assertNotIn("${{", run)


class Comportamento(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        for rel in ("scripts/conferir-release.py", "bin/forge-changelog"):
            (self.dir / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.dir / rel).write_text((RAIZ / rel).read_text(encoding="utf-8"), encoding="utf-8")
        self.git("init", "-q")
        self.versao("0.1.0")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, capture_output=True, text=True, check=True,
                              env=sem_manutencao()).stdout

    def versao(self, v, changelog=None):
        (self.dir / ".claude-plugin").mkdir(exist_ok=True)
        (self.dir / ".claude-plugin" / "plugin.json").write_text(json.dumps({"version": v}), encoding="utf-8")
        (self.dir / "CHANGELOG.md").write_text(
            changelog if changelog is not None else f"# Changelog\n\n## [Não publicado]\n\n## [{v}] - 2026-01-01\n- x\n",
            encoding="utf-8")

    def roda(self, *extra):
        return subprocess.run([sys.executable, str(self.dir / "scripts" / "conferir-release.py"), "--base", self.base, *extra],
                              cwd=self.dir, capture_output=True, text=True)

    def test_homolog_sem_versao_nova_nao_roda_a_checagem(self):
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "esquecido.md").write_text("### Adicionado\n- x\n", encoding="utf-8")  # reprovaria se rodasse
        r = self.roda("--so-se-versao-mudou")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("não é release", r.stdout)

    def test_homolog_com_versao_nova_roda_a_checagem_e_pega_fragmento_esquecido(self):
        self.versao("0.2.0")
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "esquecido.md").write_text("### Adicionado\n- x\n", encoding="utf-8")
        r = self.roda("--so-se-versao-mudou")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("esquecido.md", r.stdout + r.stderr)

    def test_homolog_com_versao_nova_e_changelog_fechado_passa(self):
        self.versao("0.2.0")
        r = self.roda("--so-se-versao-mudou")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_homolog_com_versao_nova_sem_entrada_no_changelog_reprova(self):
        self.versao("0.2.0", "# Changelog\n\n## [Não publicado]\n\n## [0.1.0] - 2026-01-01\n- x\n")
        self.assertNotEqual(self.roda("--so-se-versao-mudou").returncode, 0)

    def test_main_continua_exigindo_versao_nova(self):
        r = self.roda()  # sem a flag: versão igual à da base reprova
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Suba a versão", r.stdout + r.stderr)

    def test_main_com_release_fechada_passa(self):
        self.versao("0.1.1")
        self.assertEqual(self.roda().returncode, 0)

    def test_main_reprova_nao_publicado_com_conteudo(self):
        self.versao("0.1.1", "# Changelog\n\n## [Não publicado]\n- sobrou\n\n## [0.1.1] - 2026-01-01\n- x\n")
        self.assertNotEqual(self.roda().returncode, 0)


if __name__ == "__main__":
    unittest.main()
