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

    def test_escopo_le_so_os_pareceres_e_o_pr_segue_cobrando_a_conferencia(self):
        """Regressão do L08: na ref viva, o escopo da merge-integracao lê só os pareceres (como o caminho do squash); a conferência do
        head (E7) continua portão do `forge-check pr` da linha de comando, no mesmo repositório."""
        self.commitar(review(self.codigo), "review")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual((rc, "conferência" in saida), (0, False), saida)
        rc, saida = self.check("pr", "x", "--ref", "melhoria/x", "--base", "develop")
        self.assertEqual((rc, "pr: conferência: sem o pedido de" in saida), (1, True), saida)

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
    def test_aceite_e_config_nunca_sao_anexo_nem_com_pareceres_aprovados(self):
        protegidos = self.commitar({"docs/security/aceites/x.md": "a\n", "tests/config.json": "{}\n"}, "aceite e config")
        pareceres = {**review(protegidos), "docs/qa/x.md": PARECER.format(t="qa", c=protegidos, p="aprovado", extra="escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\n", achados=""),
                     "docs/security/x.md": PARECER.format(t="revisao-seguranca", c=protegidos, p="aprovado", extra="revisor: forge:security-engineer\n", achados="")}
        self.commitar(pareceres, "pareceres")
        for nome, viva in {"ref viva": True, "mergeCommit": False}.items():
            with self.subTest(nome):
                rc, saida = self.entrega(etapa="merge-integracao", **({} if viva else {"branch": self.squash()}))
                self.assertNotIn(SEM_PARECER, saida)
                self.assertIn(OK_INTEGRACAO, saida)  # o arquivo do trabalho segue ok
                for arquivo in ("docs/security/aceites/x.md", "tests/config.json"):
                    self.assertIn(f'escopo: confira "{arquivo}"', saida)

    def test_dois_pedidos_nos_reviews_do_squash_reprovam(self):
        outro = review(self.codigo)["docs/reviews/x.md"].replace("pedido: x", "pedido: z")
        self.commitar({**review(self.codigo), "docs/reviews/z.md": outro}, "dois reviews")
        rc, saida = self.entrega(etapa="merge-integracao", branch=self.squash())
        self.assertEqual((rc, SEM_PARECER in saida), (1, True), saida)


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

    def test_parecer_trazido_por_merge_so_vale_com_tipo_parecer_e_branch_do_pedido(self):
        qa = PARECER.format(t="qa", c="0" * 40, p="aprovado", extra="escopo: completo\n", achados="")
        for nome, texto in {"parecer qualquer": qa.replace("parecer: aprovado", "parecer: talvez"), "outra branch": qa.replace("melhoria/x", "melhoria/y"),
                            "tipo trocado": qa.replace("tipo: qa", "tipo: review")}.items():
            with self.subTest(nome):
                lateral = "p" + nome.split()[0]
                git("switch", "-q", "-c", lateral, self.base, cwd=self.repo)
                self.commitar({"docs/qa/x.md": texto}, "parecer lateral")
                git("switch", "-q", "melhoria/x", cwd=self.repo)
                git("merge", "-q", "--no-ff", "-m", "traz", lateral, cwd=self.repo)
                saida = self.saida()
                git("reset", "-q", "--hard", "HEAD^", cwd=self.repo)
                self.assertIn('escopo: confira "docs/qa/x.md"', saida)

    def test_anexo_com_remocao_continua_confira(self):
        base = self.commitar({"changelog.d/x.md": "- a\n- b\n"}, "o fragmento já existe na base")
        git("branch", "-f", "develop", base, cwd=self.repo)
        self.commitar({"changelog.d/x.md": "- a\n"}, "remove uma linha")
        self.gravar_pedido()
        rc, saida = self.entrega(base_sha=base)
        self.assertEqual((rc, 'escopo: confira "changelog.d/x.md" +0 -1' in saida), (0, True), saida)


class PareceresPeloPedido(Repositorio):
    """E23.17 (v0457, c): na merge-integracao, os pareceres são achados pelo pedido (`p1`), como no `forge-check pr <pedido>`, não
    pelo slug `x` da branch."""

    def review(self, pedido):
        texto = PARECER.format(t="review", c=self.codigo, p="aprovado", extra="revisor: forge:tech-lead\n", achados="")
        self.commitar({"docs/reviews/x.md": texto.replace("pedido: x", f"pedido: {pedido}")}, "review")

    def setUp(self):
        super().setUp()
        self.codigo = self.commitar({"notas.md": "a\n"}, "trabalho")
        self.gravar_pedido()

    def test_parecer_com_o_pedido_do_brief_aprova(self):
        self.review("p1")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 0, saida)
        self.assertIn(OK_INTEGRACAO, saida)

    def test_id_do_pedido_vale_mais_que_o_nome_do_arquivo(self):
        self.gravar_pedido()
        self.pedido.write_text("---\nid: q1\n---\n" + self.pedido.read_text(encoding="utf-8"), encoding="utf-8")
        self.review("q1")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 0, saida)
        self.assertIn(OK_INTEGRACAO, saida)

    def test_parecer_de_outro_pedido_segue_reprovando(self):
        self.review("z")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 1, saida)
        self.assertIn(SEM_PARECER, saida)

    def test_parecer_de_outra_branch_com_o_id_nao_troca_o_slug(self):
        """Volta 1 (review A1, A3; sonda S1): o parecer de outra branch com o id do pedido (vindo da develop) não troca o slug pelo id; o
        parecer da branch, pelo slug, segue valendo."""
        texto = PARECER.format(t="review", c=self.codigo, p="aprovado", extra="revisor: forge:tech-lead\n", achados="")
        self.commitar({"docs/reviews/x.md": texto, "docs/reviews/p1.md": texto.replace("pedido: x", "pedido: p1")
                       .replace("branch: melhoria/x", "branch: melhoria/outra")}, "review e parecer de outra branch")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 0, saida)
        self.assertIn(OK_INTEGRACAO, saida)

    def test_arquivo_sem_frontmatter_em_docs_reviews_nao_quebra(self):
        """Um arquivo de docs/reviews/ sem frontmatter (lido antes do parecer, na ordem do ls-tree) não quebra a busca do pedido."""
        self.commitar({"docs/reviews/LEIAME.md": "# pareceres\n"}, "leiame")
        self.review("p1")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertNotIn("Traceback", saida)
        self.assertIn(OK_INTEGRACAO, saida)
