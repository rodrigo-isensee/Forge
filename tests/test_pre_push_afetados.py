"""EST-M8: o pre-push roda só os testes afetados pelo mapa do `bin/forge-testes`; a suíte completa fica no CI do PR.

Cada teste roda o hook de verdade num repositório descartável com duas suítes mínimas (`test_a` e `test_b`, que
deixam uma marca `rodou-<nome>`), a cópia do `bin/forge-testes` e uma `origin/develop` local como base. Classe do
defeito: o portão rodar mais do que o afetado (ou, pior, menos do que o seguro). Variantes: caminho mapeado (só o
módulo), caminho sem mapa, sem base, sem a ferramenta, mais de uma ref, árvore suja, HEAD diferente do enviado,
falha no módulo afetado, falha em módulo não afetado, bloqueios de conteúdo, e a prova de árvore verde (só a
suíte completa anota).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})
ZERO = "0" * 40
BOA = "import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_a(self):\n        pathlib.Path('rodou-{}').write_text('sim')\n"
RUIM = BOA + "        self.fail('de proposito')\n"


class PrePushAfetados(unittest.TestCase):
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
        self.base = self.commit("base", tests__test_a_py=BOA.format("a"), tests__test_b_py=BOA.format("b"))
        self.git("update-ref", "refs/remotes/origin/develop", self.base)
        self.verde = self.run_dir / f"forge-suite-{os.getuid()}.verde"

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            alvo = self.repo / nome.replace("_py", ".py").replace("__", "/")
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def roda(self, local=None, remoto=ZERO, destino="melhoria/x", entrada=None):
        for p in self.repo.glob("rodou-*"):
            p.unlink()
        local = local or self.git("rev-parse", "HEAD")
        entrada = entrada if entrada is not None else f"refs/heads/x {local} refs/heads/{destino} {remoto}\n"
        r = subprocess.run([str(HOOK), "origin", "u"], cwd=self.repo, env=self.env, input=entrada,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, {p.name for p in self.repo.glob("rodou-*")}, r.stderr

    def test_so_o_modulo_afetado_roda_e_nao_anota_a_arvore_verde(self):
        self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, {"rodou-a"})
        self.assertIn("forge-testes", erro)
        self.assertFalse(self.verde.exists(), "só a suíte completa anota a prova de árvore verde")

    def test_falha_em_modulo_nao_afetado_nao_barra_e_no_afetado_barra(self):
        self.commit("b quebra", tests__test_b_py=RUIM.format("b"))
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        self.assertEqual(self.roda()[0], 0)
        self.commit("a quebra", tests__test_a_py=RUIM.format("a"))
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("testes do Forge falharam", erro)

    def test_caminho_sem_mapa_roda_a_suite_inteira_e_anota(self):
        self.commit("novo", novo_txt="x\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, {"rodou-a", "rodou-b"})
        self.assertTrue(self.verde.exists())

    def test_sem_a_base_origin_develop_roda_a_suite_inteira(self):
        self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        self.assertEqual(self.roda()[1], {"rodou-a", "rodou-b"})

    def test_sem_a_ferramenta_roda_a_suite_inteira(self):
        (self.repo / "bin" / "forge-testes").unlink()
        self.commit("sem ferramenta", tests__test_a_py=BOA.format("a") + "# x\n")
        self.assertEqual(self.roda()[1], {"rodou-a", "rodou-b"})

    def test_arvore_suja_roda_a_suite_inteira(self):
        self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        (self.repo / "sujo.txt").write_text("x")
        self.assertEqual(self.roda()[1], {"rodou-a", "rodou-b"})

    def test_commit_enviado_diferente_do_head_roda_a_suite_inteira(self):
        anterior = self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        self.commit("toca a de novo", tests__test_a_py=BOA.format("a") + "# y\n")
        self.assertEqual(self.roda(local=anterior)[1], {"rodou-a", "rodou-b"})

    def test_varias_refs_rodam_a_suite_inteira(self):
        sha = self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        entrada = (f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\nrefs/heads/y {sha} refs/heads/melhoria/y {ZERO}\n")
        self.assertEqual(self.roda(entrada=entrada)[1], {"rodou-a", "rodou-b"})

    def test_ref_que_nao_e_branch_roda_a_suite_inteira(self):
        sha = self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        entrada = f"refs/tags/v1 {sha} refs/tags/v1 {ZERO}\n"
        self.assertEqual(self.roda(entrada=entrada)[1], {"rodou-a", "rodou-b"})

    def test_bloqueios_de_conteudo_valem_antes_do_filtro(self):
        sha = self.commit("toca a", tests__test_a_py=BOA.format("a") + "# x\n")
        for destino in ("main", "homolog", "develop"):
            with self.subTest(destino):
                codigo, marcas, erro = self.roda(local=sha, destino=destino)
                self.assertEqual(codigo, 1)
                self.assertEqual(marcas, set())
                self.assertIn("bloqueado", erro)
        # histórico reescrito: o remoto tem um commit que o enviado não contém
        self.git("switch", "-q", "-c", "outro", self.base)
        divergente = self.commit("diverge", tests__test_a_py=BOA.format("a") + "# z\n")
        codigo, marcas, erro = self.roda(local=divergente, remoto=sha)
        self.assertEqual(codigo, 1)
        self.assertEqual(marcas, set())
        self.assertIn("não fast-forward", erro)


class NaoRecuaDoHook(unittest.TestCase):
    """O texto do hook guarda a falha fechada que os testes acima exercitam."""

    def test_o_hook_cita_o_forge_testes_e_o_recuo_para_a_suite_inteira(self):
        texto = HOOK.read_text(encoding="utf-8")
        self.assertIn("bin/forge-testes", texto)
        self.assertIn("python3 scripts/suite-paralela.py", texto)  # o recuo continua a suíte inteira em paralelo
        self.assertIn("discover -s tests", texto)


if __name__ == "__main__":
    unittest.main()
