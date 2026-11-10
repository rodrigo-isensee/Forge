"""PARECER-CONTEUDO (0.43.1, P3, decisão do dono de 08/11): o parecer fica preso ao conteúdo do seu domínio, não ao commit.
`commit_vale` com `dominio`, `testes_do_qa` (o teste do QA aprovado não derruba o review), `dominio_mais` e `forge-check parecer delta`,
em repositório temporário."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_volta_por_delta import FORGE_CHECK, Repositorio, carregar_forge_check  # noqa: E402

fc = carregar_forge_check()
BASE = {"src/app.py": "a = 1\n", "tests/test_app.py": "# teste\n", "docs/guia.md": "guia\n", "docs/regras/R-X.md": "regra\n",
        ".github/workflows/ci.yml": "name: CI\n", "bin/ferramenta": "#!/bin/sh\n", "tests/catraca.py": "x = 1\n",
        "tests/config.json": '{"invariantes": {"docs/inv.md": ["x"]}}', "docs/inv.md": "x\n", "README.md": "leia\n"}
REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
          "revisor: forge:tech-lead\ndata: 2026-11-08\n{extra}---\n# r\n")
QA = ("---\ntipo: qa\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: {p}\nescopo: completo\n"
      "bugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\ndata: 2026-11-08\n---\n# q\n")
SEGURANCA = ("---\ntipo: revisao-seguranca\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
             "revisor: forge:security-engineer\ndata: 2026-11-08\n---\n# s\n")


class Dominio(unittest.TestCase):
    """A tabela: na dúvida, no domínio."""

    def test_tabela_por_tipo(self):
        casos = {
            "revisao-seguranca": {"src/app.py": True, "hooks/x.py": True, "bin/forge-check": True, ".github/workflows/ci.yml": True,
                                  "package-lock.json": True, ".env.local": True, "tests/catraca.py": True, "tests/config.json": True,
                                  "docs/regras/R-X.md": True, "docs/adr/0001-x.md": True, "docs/api/contrato.yaml": True,
                                  "agents/jarvis.md": True, "docs/guia.md": False, "README.md": False, "changelog.d/x.md": False,
                                  "tests/test_app.py": False, "src/app.test.ts": False, "docs/inv.md": True},
            "revisao-devops": {".github/workflows/ci.yml": True, "Dockerfile": True, "infra/main.tf": True, "compose.yaml": True,
                               ".githooks/pre-push": True, "scripts/x.sh": True, "tests/config.json": True, "go.sum": True,
                               "Makefile": True, "src/app.py": False, "docs/guia.md": False, "tests/test_app.py": False},
            "review": {"src/app.py": True, "tests/test_app.py": True, "docs/guia.md": True},
            "qa": {"src/app.py": True, "tests/test_app.py": True},
        }
        for tipo, nomes in casos.items():
            for nome, esperado in nomes.items():
                with self.subTest(tipo=tipo, nome=nome):
                    self.assertEqual(fc.no_dominio(tipo, nome, frozenset({"docs/inv.md"})), esperado)

    def test_dominio_mais_alarga_e_e_validado(self):
        self.assertTrue(fc.no_dominio("revisao-devops", "src/deploy/x.py", mais=("src/deploy/",)))
        self.assertEqual(fc.dominio_mais({"dominio_mais": "[src/deploy/, ../fora, a b, docs/x.md]"}), ("src/deploy/", "docs/x.md"))
        self.assertEqual(fc.problemas_do_dominio_mais({"dominio_mais": "[src/, ok]"}), [])
        self.assertTrue(fc.problemas_do_dominio_mais({"dominio_mais": "[../fora]"}))
        self.assertTrue(fc.problemas_do_dominio_mais({"dominio_mais": "src/"}))
        campos, viol = fc.validar_documento("docs/reviews/p1.md", REVIEW.format(c="a" * 40, extra="dominio_mais: [*]\n"))
        self.assertTrue(any("dominio_mais" in v for v in viol), viol)


class CommitValePorDominio(Repositorio):
    def setUp(self):
        super().setUp()
        self.antes = self.commitar(BASE, "base do item")

    def vale(self, tipo, arquivos, **extra):
        git("reset", "-q", "--hard", self.antes, cwd=self.repo)
        self.commitar(arquivos, "depois do parecer")
        return fc.commit_vale(self.repo, self.antes, "HEAD", dominio=tipo, **extra)

    def test_fora_do_dominio_nao_invalida(self):
        self.assertIsNone(self.vale("revisao-devops", {"src/app.py": "a = 2\n"}))
        self.assertIsNone(self.vale("revisao-seguranca", {"docs/guia.md": "guia novo\n"}))  # docs não derruba segurança
        self.assertIsNone(self.vale("revisao-seguranca", {"tests/test_app.py": "# teste do QA\n"}))

    def test_dentro_do_dominio_invalida_e_diz_o_arquivo(self):
        for tipo, rel in (("revisao-devops", ".github/workflows/ci.yml"), ("revisao-seguranca", "src/app.py"),
                          ("revisao-seguranca", "tests/catraca.py"), ("revisao-seguranca", "docs/regras/R-X.md"),
                          ("revisao-seguranca", "docs/inv.md"), ("review", "docs/guia.md"), ("qa", "tests/test_app.py")):
            with self.subTest(tipo=tipo, rel=rel):
                motivo = self.vale(tipo, {rel: "mudou depois\n"})
                self.assertIn(f"desatualizado: {rel} mudou depois do parecer; peça novo parecer; {rel} é do domínio do parecer de {tipo}",
                              motivo or "")

    def test_sem_dominio_e_como_antes(self):  # a conferência de entrega não tem domínio: tudo fora de LIVRES conta
        self.assertIn("desatualizado: docs/guia.md", self.vale(None, {"docs/guia.md": "guia novo\n"}) or "")

    def test_dominio_mais_alarga_o_que_desatualiza(self):
        self.assertIn("src/app.py", self.vale("revisao-devops", {"src/app.py": "a = 2\n"}, mais=("src/",)) or "")

    def test_com_base_o_arquivo_fora_do_dominio_tambem_nao_diverge(self):
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar({"outro.txt": "da base\n"}, "base andou")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("reset", "-q", "--hard", self.antes, cwd=self.repo)
        git("merge", "-q", "--no-edit", "develop", cwd=self.repo)
        self.commitar({"docs/guia.md": "guia novo\n"}, "doc depois do parecer")
        self.assertIsNone(fc.commit_vale(self.repo, self.antes, "HEAD", "develop", dominio="revisao-seguranca"))
        self.commitar({"src/app.py": "a = 3\n"}, "código depois do parecer")
        self.assertIn("src/app.py", fc.commit_vale(self.repo, self.antes, "HEAD", "develop", dominio="revisao-seguranca") or "")


class TesteDoQaNaoDerrubaOReview(Repositorio):
    """O review de R; o QA escreve o teste em commit próprio (Q) e aprova com `commit: Q`."""

    def setUp(self):
        super().setUp()
        self.r = self.commitar(BASE, "entrega")
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=self.r, extra="")}, "review")

    def qa(self, arquivos, parecer="aprovado"):
        q = self.commitar(arquivos, "teste do QA")
        self.commitar({"docs/qa/p1.md": QA.format(c=q, p=parecer)}, "parecer do QA")
        return q

    def review(self):
        return [l for l in fc.cmd_pr(self.repo, "p1", "HEAD") if l.startswith("docs/reviews/") and "desatualizado" in l]

    def test_teste_do_qa_aprovado_nao_derruba(self):
        q = self.qa({"tests/test_app.py": "# teste do QA\n", "tests/test_novo.py": "# novo\n"})
        self.assertEqual(self.review(), [])
        self.assertEqual(fc.testes_do_qa(self.repo, "p1", "melhoria/x", "HEAD", self.r), (q, {"tests/test_app.py", "tests/test_novo.py"}))

    def test_commit_do_qa_com_codigo_derruba(self):
        self.qa({"tests/test_app.py": "# teste do QA\n", "src/app.py": "a = 2\n"})
        self.assertTrue(self.review())

    def test_teste_que_muda_depois_do_qa_derruba(self):
        self.qa({"tests/test_app.py": "# teste do QA\n"})
        self.commitar({"tests/test_app.py": "# mudou depois do QA\n"}, "depois do QA")
        self.assertIn("tests/test_app.py", "".join(self.review()))

    def test_qa_reprovado_nao_dispensa(self):
        self.qa({"tests/test_app.py": "# teste do QA\n"}, parecer="reprovado")
        self.assertIn("tests/test_app.py", "".join(self.review()))

    def test_teste_de_controle_nunca_e_dispensado(self):
        self.qa({"tests/catraca.py": "x = 2\n"})
        self.assertIn("tests/catraca.py", "".join(self.review()))


class ParecerDelta(Repositorio):
    def setUp(self):
        super().setUp()
        self.antes = self.commitar(BASE, "entrega")
        self.commitar({"docs/security/p1.md": SEGURANCA.format(c=self.antes)}, "parecer de segurança")

    def roda(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "parecer", "delta", *args, "--raiz", str(self.repo)],
                           capture_output=True, text=True, cwd=self.repo)
        return r.returncode, r.stdout

    def test_so_o_diff_do_dominio(self):
        self.commitar({"docs/guia.md": "guia novo\n", "src/app.py": "a = 2\n", "tests/test_app.py": "# t\n"}, "depois")
        rc, saida = self.roda("docs/security/p1.md")
        self.assertEqual(rc, 0, saida)
        self.assertIn("parecer: docs/security/p1.md (revisao-seguranca)", saida)
        self.assertIn('fora do dominio: "docs/guia.md"', saida)
        self.assertIn('fora do dominio: "tests/test_app.py"', saida)
        self.assertIn('no dominio: "src/app.py"', saida)
        self.assertIn("+a = 2", saida)
        self.assertNotIn("+guia novo", saida)

    def test_nada_no_dominio_e_ate(self):
        meio = self.commitar({"docs/guia.md": "guia novo\n"}, "só doc")
        self.commitar({"src/app.py": "a = 2\n"}, "código")
        rc, saida = self.roda("docs/security/p1.md", "--ate", meio)
        self.assertEqual(rc, 0, saida)
        self.assertIn("delta: nenhum arquivo do domínio mudou", saida)

    def test_rc_2_fora_das_pastas_ou_commit_que_nao_existe(self):
        self.assertEqual(self.roda("src/app.py")[0], 2)
        self.commitar({"docs/security/p1.md": SEGURANCA.format(c="1" * 40)}, "commit inexistente")
        rc, saida = self.roda("docs/security/p1.md")
        self.assertEqual(rc, 2, saida)
        self.assertIn("não existe", saida)


if __name__ == "__main__":
    unittest.main()
