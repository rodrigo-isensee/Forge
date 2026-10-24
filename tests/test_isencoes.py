"""M13 (LOTE-FORGE-CHECK-0.28.0, D-M13 = A): uma regra só de isenção (`isencoes_da_entrega`), usada pelo `forge-check pr`, pelo hook
`parecer` e pelo `brief gerar`. Diff só de `.md` comum isento de QA e sempre com review; `.md` de controle sem isenção. Sem rede."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")
fc = SourceFileLoader("forge_check_isencoes", str(FORGE_CHECK)).load_module()

REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
          "revisor: forge:tech-lead\ndata: 2026-10-12\n---\n# Review\n")


def ambiente_do_git():
    """Sem GIT_* herdado (um hook do git exporta GIT_DIR) e sem config global ou de sistema: o git só vê o repositório temporário."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return sem_manutencao(env)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=ambiente_do_git()).stdout.strip()


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-isencoes-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git("init", "-q", "-b", "develop", cwd=self.tmp)
        git("config", "user.email", "t@example.com", cwd=self.tmp)
        git("config", "user.name", "Teste", cwd=self.tmp)
        self.commitar({"README.md": "x\n", "src/app.py": "v1\n"}, "base")
        git("switch", "-q", "-c", "melhoria/x", cwd=self.tmp)

    def commitar(self, arquivos, mensagem):
        for rel, texto in arquivos.items():
            arq = self.tmp / rel
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_text(texto, encoding="utf-8")
        git("add", "-A", cwd=self.tmp)
        git("commit", "-q", "-m", mensagem, cwd=self.tmp)
        return git("rev-parse", "HEAD", cwd=self.tmp)

    def entrega(self, arquivos, com_review=True):
        head = self.commitar(arquivos, "entrega")
        if com_review:
            self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head)}, "review")

    def pr(self):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "pr", "p1", "--base", "develop"],
                           capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout, r.stderr


class IsencaoDoDiff(unittest.TestCase):
    def test_regra_unica(self):
        self.assertEqual(fc.isencoes_do_diff(["docs/x.md", "README.md"]), {"qa"})
        for controle in ("agents/x.md", "skills/a/SKILL.md", "stacks/s/agents/x.md", "stacks/s/skills/y/SKILL.md", "docs/regras/R-X.md",
                         "stacks/s/seguranca.md", "stacks/s/pronto.md", "templates/projeto/README.md", "templates/projeto/docs/x.md",
                         "CLAUDE.md", ".claude/CLAUDE.md"):
            with self.subTest(controle=controle):
                self.assertEqual(fc.isencoes_do_diff(["docs/x.md", controle]), set())
        self.assertEqual(fc.isencoes_do_diff(["docs/x.md", "src/a.py"]), set())
        self.assertEqual(fc.isencoes_do_diff(["stacks/s/README.md", "docs/guia/CLAUDE-notas.md"]), {"qa"})
        self.assertEqual(fc.isencoes_do_diff([]), set())


class PrComIsencao(Repo):
    def test_md_comum_com_review_e_sem_qa_passa(self):
        self.entrega({"docs/x.md": "# x\n"})
        rc, saida, erro = self.pr()
        self.assertEqual(rc, 0, saida)
        self.assertIn("pr: isento de QA", erro)

    def test_md_comum_sem_review_reprova_pela_r_review(self):
        self.entrega({"docs/x.md": "# x\n"}, com_review=False)
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1)
        self.assertIn("review: sem parecer para o pedido `p1` (R-REVIEW)", saida)
        self.assertNotIn("qa: sem parecer", saida)

    def test_md_de_controle_sem_qa_reprova(self):
        for rel in ("agents/x.md", "docs/regras/R-X.md", "stacks/s/seguranca.md", "stacks/s/pronto.md", "templates/projeto/README.md", "CLAUDE.md"):
            with self.subTest(rel=rel):
                self.setUp()
                self.entrega({rel: "# x\n"})
                rc, saida, erro = self.pr()
                self.assertEqual(rc, 1)
                self.assertIn("qa: sem parecer para o pedido `p1` (R-QA)", saida)
                self.assertNotIn("isento de QA", erro)

    def test_md_e_codigo_exigem_tudo(self):
        self.entrega({"docs/x.md": "# x\n", "src/app.py": "v2\n"})
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1)
        self.assertIn("qa: sem parecer", saida)


if __name__ == "__main__":
    unittest.main()
