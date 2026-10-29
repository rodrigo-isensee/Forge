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
    return {"docs/reviews/x.md": PARECER.format(t="review", c=commit, p=parecer, extra="revisor: forge:tech-lead\n", achados=ACHADO * (parecer == "reprovado"))}


class MergeIntegracao(Repositorio):
    """E1: o escopo é a branch com os pareceres aprovados no head; sem eles, reprova; a ref apagada é lida do mergeCommit."""

    def setUp(self):
        super().setUp()
        self.codigo = self.commitar({"notas.md": "a\n"}, "trabalho")  # só .md fora do controle: o QA é isento
        self.gravar_pedido()

    def squash(self):
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar({"outro.txt": "o\n"}, "outro PR já na develop")  # o primeiro pai do squash não é o Base-sha
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

class AnexosImplicitos(Repositorio):
    """E2: o que o conferente já aceita por regra sai `escopo: ok (anexo implícito: ...)`, só por acréscimo; o resto continua `confira`."""

    def saida(self):
        self.gravar_pedido()
        rc, saida = self.entrega()
        self.assertEqual(rc, 0, saida)
        return saida

    def test_fragmento_do_changelog_da_propria_branch(self):
        self.commitar({"changelog.d/x.md": "- x\n", "changelog.d/y.md": "- y\n", "src/app.txt": "v2\n"}, "trabalho")
        saida = self.saida()
        self.assertIn('escopo: ok (anexo implícito: fragmento do changelog) "changelog.d/x.md"', saida)
        self.assertIn('escopo: confira "changelog.d/y.md"', saida)  # fragmento de outra branch
        self.assertIn('escopo: confira "src/app.txt"', saida)  # arquivo de código não nomeado continua fora

    def test_parecer_da_propria_branch_so_vale_trazido_por_merge(self):
        qa = PARECER.format(t="qa", c="0" * 40, p="aprovado", extra="escopo: completo\n", achados="")
        self.commitar({"notas.md": "a\n"}, "trabalho")
        git("switch", "-q", "-c", "portao", self.base, cwd=self.repo)
        self.commitar({"docs/qa/x.md": qa}, "parecer do portão")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("merge", "-q", "--no-ff", "-m", "traz o parecer", "portao", cwd=self.repo)
        self.assertIn('escopo: ok (anexo implícito: parecer da própria branch trazido por merge) "docs/qa/x.md"', self.saida())
        self.commitar({"docs/qa/x.md": qa + "\nedição própria\n"}, "o autor edita depois do merge")
        self.assertIn('escopo: confira "docs/qa/x.md"', self.saida())


    def test_anexo_com_remocao_continua_confira(self):
        base = self.commitar({"changelog.d/x.md": "- a\n- b\n"}, "o fragmento já existe na base")
        git("branch", "-f", "develop", base, cwd=self.repo)
        self.commitar({"changelog.d/x.md": "- a\n"}, "remove uma linha")
        self.gravar_pedido()
        rc, saida = self.entrega(base_sha=base)
        self.assertEqual((rc, 'escopo: confira "changelog.d/x.md" +0 -1' in saida), (0, True), saida)
