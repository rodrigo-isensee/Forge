"""FC-PR-PARECER-FORJADO (v0478 E2.1): o `forge-check pr` escolhia o parecer por (data, nome) e aceitava um aprovado forjado em outro
arquivo da pasta do portão. Mais de um parecer do mesmo tipo, pedido e branch com veredito, revisor ou `commit:` divergentes recusa,
com os arquivos na mensagem. Repositório temporário, sem rede."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_volta_por_delta import Repositorio, carregar_forge_check  # noqa: E402

fc = carregar_forge_check()
REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: {b}\ncommit: {c}\nparecer: {p}\n"
          "revisor: {r}\ndata: {d}\n---\n# r\n")


class ParecerForjado(Repositorio):
    def setUp(self):
        super().setUp()
        self.c = self.commitar({"src/app.txt": "v2\n"}, "entrega")

    def review(self, nome, parecer="aprovado", revisor="forge:tech-lead", data="2026-11-08", commit=None, branch="melhoria/x"):
        return {f"docs/reviews/{nome}.md": REVIEW.format(b=branch, c=commit or self.c, p=parecer, r=revisor, d=data)}

    def linhas(self):
        return [l for l in fc.cmd_pr(self.repo, "p1", "HEAD") if l.startswith("docs/reviews")]

    def test_aprovado_forjado_em_outro_arquivo_recusa_e_diz_os_arquivos(self):
        self.commitar({**self.review("p1", parecer="reprovado"), **self.review("p1-z", data="2026-11-09")}, "pareceres")
        saida = "\n".join(self.linhas())
        self.assertIn("pareceres divergentes", saida)
        self.assertIn("docs/reviews/p1.md", saida)
        self.assertIn("docs/reviews/p1-z.md", saida)

    def test_revisor_divergente_recusa(self):
        self.commitar({**self.review("p1"), **self.review("p1-z", revisor="forge:outro")}, "pareceres")
        self.assertIn("pareceres divergentes", "\n".join(self.linhas()))

    def test_commit_divergente_recusa(self):
        antes = self.head("HEAD~1")
        self.commitar({**self.review("p1", commit=antes), **self.review("p1-z", data="2026-11-09")}, "pareceres")
        self.assertIn("pareceres divergentes", "\n".join(self.linhas()))

    def test_dois_iguais_ou_de_outra_branch_nao_recusam(self):
        self.commitar({**self.review("p1"), **self.review("p1-z"), **self.review("p1-y", parecer="reprovado", branch="melhoria/y")},
                      "pareceres")
        self.assertNotIn("pareceres divergentes", "\n".join(self.linhas()))

    def test_sem_branch_so_a_branch_do_vigente_conta(self):  # o sha da catraca e a promoção: os pareceres de outras branches do pedido
        self.commitar({**self.review("p1", data="2026-11-09"), **self.review("p1-y", parecer="reprovado", branch="melhoria/y")},
                      "pareceres")
        saida = "\n".join(l for l in fc.cmd_pr(self.repo, "p1", self.head()) if l.startswith("docs/reviews"))
        self.assertNotIn("pareceres divergentes", saida)

    def test_um_so_parecer_nao_recusa(self):
        self.commitar(self.review("p1"), "parecer")
        self.assertNotIn("pareceres divergentes", "\n".join(self.linhas()))

    def test_tipo_nao_exigido_forjado_nao_esconde_o_reprovado(self):  # P5: o devops sem infraestrutura
        devops = REVIEW.replace("tipo: review", "tipo: revisao-devops").replace("forge:tech-lead", "forge:devops-engineer")
        self.commitar({"docs/devops/p1.md": devops.format(b="melhoria/x", c=self.c, p="reprovado", r="{r}", d="2026-11-08"),
                       "docs/devops/p1-z.md": devops.format(b="melhoria/x", c=self.c, p="aprovado", r="{r}", d="2026-11-09")},
                      "pareceres")
        saida = "\n".join(fc.nao_exigidos_que_nao_aprovam(self.repo, "p1", "HEAD", "melhoria/x", ("review",)))
        self.assertIn("docs/devops: revisao-devops: pareceres divergentes", saida)
        self.assertIn("docs/devops/p1-z.md", saida)


if __name__ == "__main__":
    unittest.main()
