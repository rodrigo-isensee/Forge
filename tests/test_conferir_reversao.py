"""`scripts/conferir-reversao.py` (M10): aviso por commit, sem escrever no repositório real."""
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "conferir-reversao.py"
AMBIENTE = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                           "GIT_COMMITTER_EMAIL": "t@t"})
TESTE_BASE = "import unittest\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.assertTrue(True)\n"
# Plano dirigido no repositório falso: o diff da branch só toca `README.md` (-> test_forge, test_doutor) e `CONTRIBUTING.md`
# (-> test_forge, test_changelog), regras do MAPA de `bin/forge-testes` cujos módulos a base traz. Acoplamento
# de propósito: se o MAPA mudar essas regras, o plano cai na suíte inteira e estes casos quebram alto (sem falso verde).
# O `test_forge` da base grava a marca (CONFERIR_MARCA) quando é carregado: a marca prova que alguma suíte rodou.
EXIGE = "exige CONTRIBUTING\n"  # README.md com este texto exige CONTRIBUTING.md: a suíte falha sem ele
SAI_2 = "sai 2\n"  # CONTRIBUTING.md com este texto e sem README.md: a suíte sai 2 (sem veredito do forge-testes)
TESTE_FORGE = ("import os\nimport unittest\nfrom pathlib import Path\n"
               "if os.environ.get('CONFERIR_MARCA'):\n    Path(os.environ['CONFERIR_MARCA']).touch()\n"
               "def ler(n):\n    return Path(n).read_text() if Path(n).is_file() else None\n"
               "class T(unittest.TestCase):\n    def test_contrato(self):\n"
               f"        if ler('CONTRIBUTING.md') == {SAI_2!r} and ler('README.md') is None:\n"
               "            os._exit(2)\n"
               f"        if ler('README.md') == {EXIGE!r}:\n"
               "            self.assertIsNotNone(ler('CONTRIBUTING.md'))\n")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=AMBIENTE, check=True).stdout.strip()


def impressao(raiz):
    """Hash de tudo sob `raiz` (conteúdo e caminhos), para provar que nada foi escrito."""
    h = hashlib.sha256()
    for p in sorted(Path(raiz).rglob("*")):
        h.update(str(p.relative_to(raiz)).encode())
        if p.is_file() and not p.is_symlink():
            h.update(p.read_bytes())
    return h.hexdigest()


class ConferirReversao(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        (self.repo / "tests").mkdir(parents=True)
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "tests" / "test_forge.py").write_text(TESTE_FORGE)
        (self.repo / "tests" / "test_changelog.py").write_text(TESTE_BASE)
        (self.repo / "tests" / "test_doutor.py").write_text(TESTE_BASE)  # o MAPA leva README.md também ao test_doutor
        self.marca = Path(self._tmp.name) / "marca"
        self.commitar("base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "switch", "-q", "-c", "feat")

    def commitar(self, msg):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", msg)
        return git(self.repo, "rev-parse", "--short=7", "HEAD")

    def rodar(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd or self.repo, capture_output=True,
                              text=True, env={**AMBIENTE, "CONFERIR_MARCA": str(self.marca)})

    def escrever(self, nome, texto):
        (self.repo / nome).write_text(texto)

    def test_commit_que_se_reverte(self):
        self.escrever("CONTRIBUTING.md", "x\n")
        sha = self.commitar("add contributing")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), f"{sha} reverte")

    def test_commit_que_nao_se_reverte(self):
        self.escrever("CONTRIBUTING.md", "c\n")
        ruim = self.commitar("contributing")
        self.escrever("README.md", EXIGE)
        conflita = self.commitar("readme que exige o contributing")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)  # aviso, não portão
        linhas = r.stdout.strip().splitlines()
        self.assertEqual(len(linhas), 2)
        self.assertTrue(linhas[0].startswith(f"{ruim} nao-reverte: "), linhas[0])
        self.assertTrue(linhas[1].startswith(f"{conflita} "), linhas[1])

    def test_conflito_ao_reverter_avisa(self):
        self.escrever("CONTRIBUTING.md", "um\n")
        primeiro = self.commitar("um")
        self.escrever("CONTRIBUTING.md", "um\ndois\n")
        self.commitar("dois")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"{primeiro} nao-reverte: conflito", r.stdout)

    def test_nao_escreve_no_original(self):
        self.escrever("CONTRIBUTING.md", "c\n")
        self.commitar("contributing")
        self.escrever("README.md", EXIGE)
        self.commitar("readme")
        antes = impressao(self.repo)
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(impressao(self.repo), antes)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_suite_afetada_falha_sem_o_commit(self):
        self.escrever("CONTRIBUTING.md", "c\n")
        ruim = self.commitar("contributing")
        self.escrever("README.md", EXIGE)
        self.commitar("readme que exige o contributing")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0], f"{ruim} nao-reverte: a suíte afetada falha sem o commit")

    def test_ambiente_com_git_index_file_nao_toca_o_original(self):
        self.escrever("CONTRIBUTING.md", "x\n")
        extra = self.commitar("add contributing")
        self.escrever("README.md", "o\n")
        outro = self.commitar("add readme")
        antes = impressao(self.repo / ".git")
        env = {**AMBIENTE, "GIT_INDEX_FILE": str(self.repo / ".git" / "index")}
        r = subprocess.run([sys.executable, str(SCRIPT), self.base, "feat"], cwd=self.repo, capture_output=True,
                           text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), [f"{extra} reverte", f"{outro} reverte"])
        self.assertEqual(impressao(self.repo / ".git"), antes)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_ponta_ja_vermelha_avisa_e_nao_classifica(self):
        self.escrever("README.md", EXIGE)  # sem CONTRIBUTING.md: a suíte afetada (dirigida) já falha na ponta
        self.commitar("readme que exige um contributing ausente")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("já falha na ponta", r.stdout)
        self.assertNotIn(" reverte", r.stdout)
        self.assertNotIn("nao-reverte", r.stdout)

    def test_commit_de_mescla_fica_fora(self):
        git(self.repo, "switch", "-q", "-c", "lado")
        self.escrever("README.md", "l\n")
        lado = self.commitar("add lado")
        git(self.repo, "switch", "-q", "feat")
        self.escrever("CONTRIBUTING.md", "x\n")
        extra = self.commitar("add extra")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "mescla lado", "lado")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(l.split()[0] for l in r.stdout.splitlines()), sorted([lado, extra]))

    def test_ponta_que_pede_a_suite_inteira_nao_roda_nada(self):
        self.escrever("CONTRIBUTING.md", "x\n")
        self.commitar("dirigido")
        self.assertEqual(self.rodar(self.base, "feat").returncode, 0)
        self.assertTrue(self.marca.exists())  # controle: com o plano dirigido a suíte roda e grava a marca
        self.marca.unlink()
        self.escrever("extra.txt", "x\n")  # sem regra no MAPA: o plano da ponta é a suíte inteira
        self.commitar("add extra")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("a ponta pede a suíte inteira, que só roda na trava (R-TETO) e no CI do PR; nada classificado.",
                      r.stdout)
        self.assertNotIn(" reverte", r.stdout)
        self.assertNotIn("nao-reverte", r.stdout)
        self.assertFalse(self.marca.exists())  # nenhuma suíte rodou, nem na ponta nem por commit

    def test_listar_que_sai_diferente_de_0_conta_como_suite_inteira(self):
        falso = Path(self._tmp.name) / "falso"  # cópia do script com forge-testes falso: --listar dirigido e rc 1
        for nome, texto in (("scripts/c.py", SCRIPT.read_text()), ("bin/forge-testes", "import os, sys\n"
                            "print('forge-testes: dirigido (test_forge).')\nif '--listar' in sys.argv: sys.exit(1)\n"
                            "open(os.environ['CONFERIR_MARCA'], 'w')\n")):  # sem --listar: grava a marca
            (falso / nome).parent.mkdir(parents=True, exist_ok=True)
            (falso / nome).write_text(texto)
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "vazio")
        r = subprocess.run([sys.executable, "-I", str(falso / "scripts/c.py"), self.base, "feat"], cwd=self.repo,
                           capture_output=True, text=True, env={**AMBIENTE, "CONFERIR_MARCA": str(self.marca)})
        self.assertEqual((r.returncode, r.stdout), (0, "conferir-reversao: a ponta pede a suíte inteira, que só roda "
                                                       "na trava (R-TETO) e no CI do PR; nada classificado.\n"))
        self.assertFalse(self.marca.exists())  # nenhuma suíte rodou

    def test_forge_testes_que_sai_2_vira_sem_veredito(self):
        self.escrever("README.md", "r\n")
        sem = self.commitar("readme")
        self.escrever("CONTRIBUTING.md", SAI_2)
        self.commitar("contributing")
        r = self.rodar(self.base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0], f"{sem} sem-veredito: o forge-testes saiu 2 sem o commit")

    def test_erro_de_uso_e_repositorio_invalido_saem_com_2(self):
        self.assertEqual(self.rodar().returncode, 2)
        self.assertEqual(self.rodar(self.base, "nao-existe").returncode, 2)
        with tempfile.TemporaryDirectory() as fora:
            self.assertEqual(self.rodar("a", "b", cwd=fora).returncode, 2)

    def test_revert_que_pede_a_suite_inteira_nao_roda_nada(self):
        # Abuso 9 (C-7): a ponta é dirigida, mas o revert de c2 traz de volta extra.txt (sem mapa). Todo passo dirigido
        # carrega test_forge e grava a marca; a marca `.completa` vem de um módulo da base que só a suíte inteira carrega.
        completa = Path(f"{self.marca}.completa")
        (self.repo / "tests" / "test_so_na_completa.py").write_text(
            f"from pathlib import Path\nPath({str(completa)!r}).touch()\n")
        base = self.commitar("base com um módulo que só a suíte inteira carrega")
        self.escrever("README.md", "r\n")
        c0 = self.commitar("c0")
        self.escrever("extra.txt", "x\n")
        c1 = self.commitar("c1")
        git(self.repo, "rm", "-q", "extra.txt")
        c2 = self.commitar("c2")
        r = self.rodar(base, "feat")
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual([l.split()[0] for l in linhas], [c0, c1, c2])
        self.assertNotIn("sem-veredito", linhas[0] + linhas[1])
        self.assertEqual(linhas[2], f"{c2} sem-veredito: o revert pede a suíte inteira (R-TETO)")
        self.assertTrue(self.marca.exists())  # controle: os passos dirigidos rodaram e gravaram a marca
        self.assertFalse(completa.exists())  # a suíte inteira não rodou no revert de c2


if __name__ == "__main__":
    unittest.main()
