"""T1-CONF-ESCOPO: `forge-check entrega` na etapa merge-integracao (E1) e os anexos implícitos por acréscimo (E2). Repositório temporário."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import git  # noqa: E402
from test_volta_por_delta import Repositorio  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

PARECER = "---\ntipo: {t}\ncontrato: 1\npedido: x\nbranch: melhoria/x\ncommit: {c}\nparecer: {p}\n{extra}data: 2026-10-29\n---\n# {t}\n{achados}"
ACHADO = "\n## Achados\n- A1 (bloqueante) notas.md:1 · corrige\n"
OK_INTEGRACAO = 'escopo: ok (merge-integracao: branch com os pareceres aprovados no head) "notas.md"'
SEM_PARECER = "escopo: merge-integracao sem os pareceres aprovados no head"


def review(commit, parecer="aprovado"):
    return {"docs/reviews/x.md": PARECER.format(t="review", c=commit, p=parecer, extra="revisor: forge:tech-lead\n",
                                                achados=ACHADO if parecer == "reprovado" else "")}


class MergeIntegracao(Repositorio):
    """E1: o escopo é a branch com os pareceres aprovados no head; sem eles, reprova; a ref apagada é lida do mergeCommit."""

    def setUp(self):
        super().setUp()
        self.codigo = self.commitar({"notas.md": "a\n"}, "trabalho")  # só .md fora do controle: o QA é isento
        self.gravar_pedido()

    def squash(self):
        git("switch", "-q", "develop", cwd=self.repo)
        git("merge", "-q", "--squash", "melhoria/x", cwd=self.repo)
        git("commit", "-q", "-m", "squash", cwd=self.repo)
        git("branch", "-q", "-D", "melhoria/x", cwd=self.repo)  # o forge-fechar apagou a ref
        return self.head()

    def test_branch_com_parecer_aprovado_no_head_nao_marca_arquivo_fora(self):
        self.commitar(review(self.codigo), "review")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 0, saida)
        self.assertIn(OK_INTEGRACAO, saida)

    def test_sem_parecer_ou_com_parecer_reprovado_continua_reprovando(self):
        for nome, arquivos in {"ausente": {}, "reprovado": review(self.codigo, "reprovado")}.items():
            with self.subTest(nome):
                if arquivos:
                    self.commitar(arquivos, "review")
                rc, saida = self.entrega(etapa="merge-integracao")
                self.assertEqual(rc, 1, saida)
                self.assertIn(SEM_PARECER, saida)
                self.assertIn('escopo: confira "notas.md"', saida)

    def test_ref_apagada_le_o_merge_commit_do_squash(self):
        self.commitar(review(self.codigo), "review")
        merge = self.squash()
        rc, saida = self.entrega(etapa="merge-integracao", branch=merge)
        self.assertEqual((rc, OK_INTEGRACAO in saida, f"intervalo: {self.head(f'{merge}^')}..{merge}" in saida), (0, True, True), saida)

    def test_merge_commit_sem_parecer_reprova(self):
        rc, saida = self.entrega(etapa="merge-integracao", branch=self.squash())
        self.assertEqual((rc, SEM_PARECER in saida, "review: sem parecer do pedido na entrega" in saida), (1, True, True), saida)
