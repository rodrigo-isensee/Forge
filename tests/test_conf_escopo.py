"""T1-CONF-ESCOPO: `forge-check entrega` na etapa merge-integracao (E1) e os anexos implícitos por acréscimo (E2). Repositório temporário."""
import sys
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import git  # noqa: E402
from test_volta_por_delta import Repositorio  # noqa: E402
from test_selo_e_entrega import Repositorio as ProjetoSelado, fc  # noqa: E402
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


CONFIG = "templates/projeto/.forge/config.json"
OUTRO = "templates/projeto/.githooks/pre-push"


class PatchDoDono(ProjetoSelado):
    """CONFERENCIA-PATCH-DO-DONO (v047; a 3a do v0457; ameaças P1-P12 e casos C1-C15 de docs/security/v047-e1-ameacas.md): o arquivo
    que o dono aplicou (git apply, decisão 4a), fora da lista do brief, só não reprova com a linha `patch do dono aplicado` no
    `## Histórico`, a `DECISÃO DO DONO` que cita o sha40 e o caminho, e o head com o blob e o modo do commit do dono."""

    def setUp(self):
        super().setUp()
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        self.x = self.do_dono({CONFIG: '{"ritmo": "equilibrado"}\n'})
        self.entregar()
        self.original = self.pedido()

    def do_dono(self, arquivos):
        for rel, texto in arquivos.items():
            self.gravar(rel, texto)
        self.git("add", *arquivos)
        return self.commit("chore: patch aplicado pelo dono")

    def declarar(self, nome=CONFIG, sha=None, decisao="`{nome}` {sha}", linha=None):
        sha = sha or self.x
        texto = self.original
        if decisao:
            texto = texto.replace("\n## Histórico", f"DECISÃO DO DONO (2026-11-12 11:37): aplicado {decisao.format(nome=nome, sha=sha)}\n\n## Histórico")
        texto += f"- 2026-11-12 11:37: patch do dono aplicado `{nome}` commit {sha}\n" if linha is None else linha
        (self.proj / "docs/pedidos/exemplo.md").write_text(texto, encoding="utf-8")
        return texto

    def conferir(self):
        return self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", "--sem-gravar")

    def fora(self, nome=CONFIG, motivo=None):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f'escopo: fora do declarado no brief "{nome}"', saida)
        if motivo:
            self.assertIn(motivo, saida)
        return saida

    def isencao(self, texto, sha, base_sha=None, nome=CONFIG):
        return fc.isencao_do_dono(self.proj, "exemplo", texto, [sha], nome, base_sha or self.base, self.git("rev-parse", "HEAD"), None)

    def test_c_leg_nome_commit_e_decisao_cumprem(self):
        self.fora()  # sem a declaração, o arquivo do dono reprova (a 3a)
        self.declarar()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertRegex(saida, rf'escopo: ok \(patch do dono {self.x[:7]}, DECISÃO DO DONO exemplo:\d+\) "{CONFIG}"')

    def test_declaracao_que_nao_isenta(self):
        x, blob = self.x, self.git("rev-parse", f"HEAD:{CONFIG}")
        forma = "linha fora da forma"
        casos = {
            "C1 fora do Histórico": dict(linha="", decisao="`{nome}` {sha}\n- 2026-11-12 11:37: patch do dono aplicado " + CONFIG + " commit {sha}"),
            "C2 sem decisão": dict(decisao=None, motivo="sem `DECISÃO DO DONO`"),
            "C3 decisão com outro sha": dict(decisao="`{nome}` " + "1" * 40, motivo="sem `DECISÃO DO DONO`"),
            "C3 decisão com outro caminho": dict(decisao="`templates/projeto/.forge/` {sha}", motivo="sem `DECISÃO DO DONO`"),
            "C3 decisão com caminho mais longo": dict(decisao="`{nome}.antigo` {sha}", motivo="sem `DECISÃO DO DONO`"),
            "C5 sha curto": dict(sha=x[:7], decisao="`{nome}` " + x, motivo=forma),
            "C5 sha maiúsculo": dict(sha=x.upper(), motivo=forma),
            "C5 HEAD~1": dict(sha="HEAD~1", motivo=forma),
            "C5 sha de blob": dict(sha=blob, motivo="o sha não é commit"),
            "C5 sha inexistente": dict(sha="e" * 40, motivo="o sha não é commit"),
            "C10 pasta": dict(nome="templates/projeto/.forge/"),
            "C10 curinga": dict(nome="templates/projeto/.forge/*.json"),
            "C10 ponto": dict(nome="./" + CONFIG),
            "C10 barra dupla": dict(nome=CONFIG.replace("/", "//", 1)),
        }
        for caso, kw in casos.items():
            with self.subTest(caso):
                motivo = kw.pop("motivo", None)
                self.declarar(**kw)
                self.fora(motivo=motivo)

    def test_c6_c7_conteudo_modo_ou_symlink_depois_do_commit_do_dono(self):
        for caso, mudar, motivo in (("C6 conteúdo", lambda: self.gravar(CONFIG, "{}\n"), "o conteúdo mudou depois do commit do dono"),
                                    ("C7 modo", lambda: (self.proj / CONFIG).chmod(0o755), "o modo mudou depois do commit do dono")):
            with self.subTest(caso):
                mudar()
                self.git("add", CONFIG)
                self.commit("o agente mexe depois do dono")
                self.declarar()
                self.fora(motivo=motivo)
                self.git("reset", "-q", "--hard", "HEAD^")
        (self.proj / "templates/link").symlink_to("projeto/.forge/config.json")
        self.git("add", "templates/link")
        link = self.commit("chore: symlink do dono")
        self.declarar(nome="templates/link", sha=link)
        self.fora(nome="templates/link", motivo="symlink, submódulo ou ausente no head")
        self.git("update-index", "--add", "--cacheinfo", f"160000,{self.base},templates/sub")
        sub = self.commit("chore: submódulo do dono")
        self.declarar(nome="templates/sub", sha=sub)
        self.fora(nome="templates/sub", motivo="symlink, submódulo ou ausente no head")

    def test_c9_c14_commit_solto_ou_de_merge(self):
        solto = self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit-tree", "HEAD^{tree}", "-p", self.base, "-m", "solto")
        self.declarar(sha=solto)
        self.fora(motivo="commit fora da branch")
        self.git("switch", "-q", "-c", "lado", self.base)
        self.do_dono({OUTRO: "#!/bin/sh\n"})
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge", "lado")
        self.declarar(nome=OUTRO, sha=self.git("rev-parse", "HEAD"))
        self.fora(nome=OUTRO, motivo="commit de merge")

    def test_c8_commit_ja_na_base(self):
        texto = self.declarar()
        self.assertEqual(self.isencao(texto, self.x)[0][1], False)
        self.assertEqual(self.isencao(texto, self.x, base_sha=self.x),
                         (None, [(f'patch do dono: {self.x[:7]} não isenta "{CONFIG}" (commit fora da branch)', False)]))

    def test_c11_so_o_arquivo_declarado_do_commit_do_dono(self):
        x2 = self.do_dono({OUTRO: "#!/bin/sh\n", "templates/projeto/README.md": "r\n"})
        self.declarar(nome=OUTRO, sha=x2)
        saida = self.fora(nome="templates/projeto/README.md")
        self.assertIn(f'escopo: ok (patch do dono {x2[:7]}', saida)
        self.declarar(sha=x2)  # x2 não altera o CONFIG, ainda que o blob seja o mesmo no head
        self.fora(motivo="o commit não altera o arquivo")

    def test_c4_c13_pedido_na_entrega_e_caminhos_que_nunca_isentam(self):
        nunca = ("docs/reviews/x.md", "docs/security/aceites/x.md", "tests/test_oraculo_x.py")
        x3 = self.do_dono(dict.fromkeys(nunca, "r\n"))
        for nome in nunca:
            with self.subTest(nome):
                self.declarar(nome=nome, sha=x3)
                self.fora(nome=nome, motivo="caminho que nunca isenta")
        self.do_dono({"docs/pedidos/outro.md": "p\n"})
        self.declarar()
        self.fora(motivo="a entrega mexe em docs/pedidos/")

    def test_c15_git_que_falha_reprova(self):
        texto, real = self.declarar(), fc.git
        for passo in ("ls-tree", "rev-list"):
            with self.subTest(passo), mock.patch.object(fc, "git", lambda raiz, *a, **kw: (1, b"") if passo in a else real(raiz, *a, **kw)):
                self.assertEqual(self.isencao(texto, self.x), ((f'escopo: o git falhou (patch do dono) "{CONFIG}"', True), []))
