"""DV-4: a checagem de release roda no PR para a main e no PR develop -> homolog (só se a versão subiu). Sem rede."""
import json
import os
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


class ConferirPromocao(unittest.TestCase):
    """DV-3(b) E2a: ok só com 2 pais e a árvore do 2.º; squash, octopus e conteúdo próprio dão 1; o resto, 2."""
    def setUp(self, formato="sha1"):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name) / "repo"
        self.env = sem_manutencao({k: v for k, v in os.environ.items() if k != "CI" and not k.startswith("GIT_DIR")})
        self.git("init", "-q", "-b", "main", f"--object-format={formato}", str(self.dir), cwd=self._tmp.name)
        self.commit("a.txt")
        self.git("checkout", "-qb", "homolog")
        self.commit("b.txt")
        self.git("checkout", "-q", "main")

    def git(self, *args, cwd=None):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
                              cwd=cwd or self.dir, capture_output=True, text=True, check=True, env=self.env).stdout.strip()

    def commit(self, nome):
        (self.dir / nome).write_text(nome, encoding="utf-8")
        self.git("add", "--", nome)
        self.git("commit", "-qm", nome)

    def roda(self, *args, cwd=None):  # o script mora fora do repositório conferido: confere o diretório corrente (C-3)
        return subprocess.run([sys.executable, "-I", str(RAIZ / "scripts" / "conferir-promocao.py"), *args],
                              cwd=cwd or self.dir, capture_output=True, text=True, env=self.env)

    def test_merge_sem_conteudo_proprio_da_ok_com_os_sha_do_repositorio_corrente(self):
        self.git("merge", "-q", "--no-ff", "-m", "promove", "homolog")
        r = self.roda("--ref", "HEAD")
        head, p2 = self.git("rev-parse", "HEAD", "HEAD^2").split()
        self.assertEqual((r.returncode, r.stdout.strip()), (0, f"promoção: ok {head[:7]} (2 pais, árvore igual a {p2[:7]})"))

    def test_squash_tem_um_pai(self):
        self.git("merge", "-q", "--squash", "homolog")
        self.git("commit", "-qm", "squash")
        r = self.roda("--ref", "main")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tem 1 pai (squash", r.stdout)

    def test_conteudo_proprio_no_merge_reprova_so_com_a_contagem(self):  # casos de abuso 2 e 6
        self.git("merge", "-q", "--no-ff", "--no-commit", "homolog")
        self.commit("a\n## ok.md")
        r = self.roda("--ref", "HEAD")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"\Apromoção: [0-9a-f]{7} difere do segundo pai em 1 arquivos \(conteúdo próprio")
        self.assertNotIn("## ok", r.stdout + r.stderr)

    def test_octopus_reprova(self):
        self.git("checkout", "-qb", "vazio", "main")
        self.git("commit", "-q", "--allow-empty", "-m", "vazio")
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "octopus", "homolog", "vazio")
        r = self.roda("--ref", "HEAD")
        self.assertEqual((r.returncode, "tem 3 pais" in r.stdout), (1, True), r.stdout + r.stderr)

    def test_nunca_ok_quando_nao_da_para_verificar(self):
        self.git("merge", "-q", "--no-ff", "-m", "promove", "homolog")
        self.git("clone", "-q", "--depth", "1", "--branch", "main", self.dir.as_uri(), "raso", cwd=self._tmp.name)
        casos = {"raso": self.roda("--ref", "HEAD", cwd=Path(self._tmp.name) / "raso"),
                 "rev-list falhou": self.roda("--ref", "nao-existe"),
                 "fora de repositório": self.roda("--ref", "HEAD", cwd=self._tmp.name)}
        for nome, r in casos.items():
            with self.subTest(nome):
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("promoção: não verificável", r.stdout)
        self.assertIn("rev-list falhou", casos["rev-list falhou"].stdout)

    def test_ref_com_traco_ou_controle_recusa_antes_do_git(self):  # caso de abuso 5
        alvo = Path(self._tmp.name) / "x"
        for ref in ("-x", f"--output={alvo}", "a\nb", "a\x1bb"):
            with self.subTest(ref=ref):
                r = self.roda(f"--ref={ref}")
                self.assertEqual((r.returncode, r.stdout.strip()), (2, "promoção: não verificável (ref inválida)"))
        self.assertFalse(alvo.exists())

    def test_sha256_fora_do_formato_esperado_nao_da_ok(self):
        self.setUp(formato="sha256")
        self.git("merge", "-q", "--no-ff", "-m", "promove", "homolog")
        r = self.roda("--ref", "HEAD")
        self.assertEqual((r.returncode, "rev-list fora do formato" in r.stdout), (2, True), r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
