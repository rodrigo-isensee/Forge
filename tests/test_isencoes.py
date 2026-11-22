"""M13 (LOTE-FORGE-CHECK-0.28.0) substituída pela G1.3 (v0478, ORDEM DO DONO de 21/11 22:13; D2): a isenção de QA saiu e a classe T
decide, a mesma regra no `forge-check pr`, no hook `parecer` e no `brief gerar`. Diff só de `.md`, comum ou de agente, skill e modelo, pede
só o review; `docs/regras/` pede review e segurança (gatilho), sem QA; o review vale sempre. Sem rede."""
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
from apoio_conferida import gravar_conferida  # noqa: E402

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

    def pr(self, conferir=True):
        if conferir:  # E7: a conferida do head (o teste é da isenção); sem parecer nenhum, o pedido gravado daria o `uso:` (rc 2)
            gravar_conferida(self.tmp / "home", self.tmp, "p1")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "pr", "p1", "--base", "develop"],
                           capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout, r.stderr


class RegraUnica(unittest.TestCase):
    def test_classe_t_decide_por_todos(self):  # G1.3: a isenção do M13 virou a classe T, uma regra só
        exigidos = {}
        for nomes in (["docs/x.md", "README.md"], ["docs/x.md", "agents/x.md"], ["stacks/s/skills/y/SKILL.md", "templates/projeto/docs/x.md"],
                      ["CLAUDE.md", ".claude/CLAUDE.md"], ["stacks/s/seguranca.md", "stacks/s/pronto.md"], ["docs/regras/R-X.md"]):
            infra, gatilhos = fc.gatilhos_do_diff(nomes)
            classe = fc.classe_das_mudancas([fc.Mudanca(n) for n in nomes], fc.catraca_da_classe(), None)[0]
            exigidos[nomes[0]] = fc.pareceres_exigidos(classe, infra, gatilhos)
        self.assertEqual(exigidos.pop("docs/regras/R-X.md"), ["review", "revisao-seguranca"])
        self.assertEqual(set(map(tuple, exigidos.values())), {("review",)})


class PrComIsencao(Repo):
    def test_md_comum_com_review_e_sem_qa_passa(self):
        self.entrega({"docs/x.md": "# x\n"})
        rc, saida, erro = self.pr()
        self.assertEqual(rc, 0, saida)
        self.assertIn("pr: classe T (só documentação fora dos caminhos de controle)", erro)
        self.assertNotIn("isento de QA", erro)  # G1.3: a linha do M13 saiu

    def test_md_comum_sem_review_reprova_pela_r_review(self):
        self.entrega({"docs/x.md": "# x\n"}, com_review=False)
        rc, saida, _ = self.pr(conferir=False)
        self.assertEqual(rc, 1)
        self.assertIn("review: sem parecer para o pedido `p1` (R-REVIEW)", saida)
        self.assertNotIn("qa: sem parecer", saida)

    def test_md_de_agente_skill_e_modelo_com_review_e_sem_qa_passa(self):  # G1.3
        for rel in ("agents/x.md", "stacks/s/seguranca.md", "stacks/s/pronto.md", "templates/projeto/README.md", "CLAUDE.md"):
            with self.subTest(rel=rel):
                self.setUp()
                self.entrega({rel: "# x\n"})
                rc, saida, erro = self.pr()
                self.assertEqual(rc, 0, saida)
                self.assertIn("pr: classe T (só texto, inclusive de agente, skill, modelo ou regra (G1.3))", erro)

    def test_md_de_controle_sem_review_reprova(self):
        self.entrega({"agents/x.md": "# x\n"}, com_review=False)
        rc, saida, _ = self.pr(conferir=False)
        self.assertEqual(rc, 1)
        self.assertIn("review: sem parecer para o pedido `p1` (R-REVIEW)", saida)

    def test_md_de_regra_sem_seguranca_reprova_e_sem_qa(self):  # G1.3, D2: docs/regras/ segue com a segurança
        self.entrega({"docs/regras/R-X.md": "# x\n"})
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1)
        self.assertIn("revisao-seguranca: sem parecer para o pedido `p1` (controles do Forge: docs/regras/R-X.md) (R-SEGURANCA)", saida)
        self.assertNotIn("qa: sem parecer", saida)

    def test_md_e_codigo_exigem_tudo(self):  # P5: com mais de 20 linhas de código (classe N); até 20, a entrega é T (tests/test_classe_risco.py)
        self.entrega({"docs/x.md": "# x\n", "src/app.py": "".join(f"v{i}\n" for i in range(21))})
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1)
        self.assertIn("qa: sem parecer", saida)


if __name__ == "__main__":
    unittest.main()
