"""T1-CONF-ESCOPO: `forge-check entrega` na etapa merge-integracao (E1) e os anexos implícitos por acréscimo (E2). Repositório temporário."""
import hashlib
import json
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
        return fc.isencao_do_dono(self.proj, "exemplo", texto, [sha], nome, base_sha or self.base, self.git("rev-parse", "HEAD"), None,
                                  "melhoria/x")

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
        x2 = self.do_dono({OUTRO: "#!/bin/sh\n", "templates/projeto/LEIAME.md": "r\n"})
        self.declarar(nome=OUTRO, sha=x2)
        saida = self.fora(nome="templates/projeto/LEIAME.md")
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


HOOK, PATCH, DONO = ".githooks/pre-push", "docs/notas/pp1.patch", "dono@exemplo"
HOOK_NOVO = "#!/bin/sh\nexit 0\n"


class PatchRevisadoDoDono(ProjetoSelado):
    """PP1-APLICADO-PELO-DONO (v0478 E52, decisão do dono 18/11): o arquivo em vigor aplicado pelo dono sai do escopo só com (a) o
    commit idêntico, na árvore inteira e no modo, ao `.patch` revisado da branch aplicado sobre a base (cada caminho igual no pai, no
    Base-sha e na develop atual, E52.5 A1), (b) autor e committer do dono (`emails_do_dono` da configuração do Base-sha, A2), (c) o
    sha256 do patch, citado por parecer de segurança aprovado (A3), e o sha40 do commit gravados no Histórico e (d) o patch
    adulterado recusado. Casos reais: o PP1 (`.githooks/pre-push`) e a A3 (#713, `.claude/settings.json`)."""

    declarar, conferir, fora = PatchDoDono.declarar, PatchDoDono.conferir, PatchDoDono.fora

    def setUp(self):
        super().setUp()
        self.git("switch", "-q", "develop")  # A3: o parecer de segurança que cita o sha256 do PATCH já está na base (no head)
        self.gravar(PATCH, self.patch_de(HOOK_NOVO))
        self.aprovar()
        self.git("add", "docs/security")
        self.commit("docs(security): parecer do patch")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("merge", "-q", "--ff-only", "develop")
        self.base = self.git("rev-parse", "HEAD")
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        (self.proj / ".git/info/exclude").write_text(".forge/\n", encoding="utf-8")
        self.configurar([DONO.upper()])  # o e-mail vale sem caixa
        self.entregar()
        self.original = self.pedido()

    def aprovar(self, parecer="aprovado", tipo="revisao-seguranca", sha256=None, cru=False, pedido="exemplo", branch="melhoria/x",
                caminho="docs/security/x.md"):
        """O parecer em `caminho` que cita o sha256 do PATCH (ou `sha256`), sem commit; `cru`: só o sha256, sem frontmatter. O
        `pedido:` e a `branch:` são os da entrega conferida, salvo pedido em contrário (A4)."""
        sha256 = sha256 or hashlib.sha256((self.proj / PATCH).read_bytes()).hexdigest()
        if cru:
            return self.gravar(caminho, f"sha256 {sha256}\n")
        texto = PARECER.format(t=tipo, c=self.base, p=parecer, extra="revisor: forge:security-engineer\n",
                               achados=f"\nPatch lido: `{PATCH}` sha256 {sha256}\n")
        self.gravar(caminho, texto.replace("pedido: x\n", f"pedido: {pedido}\n").replace("branch: melhoria/x\n", f"branch: {branch}\n"))

    def configurar(self, emails):
        """`emails_do_dono` na configuração da raiz; None apaga o arquivo; `(texto,)` grava o texto cru."""
        pasta = self.proj / ".forge"
        pasta.mkdir(exist_ok=True)
        if emails is None:
            (pasta / "config.json").unlink(missing_ok=True)
        else:
            (pasta / "config.json").write_text(emails[0] if isinstance(emails, tuple) else json.dumps({"emails_do_dono": emails}), encoding="utf-8")

    def patch_de(self, conteudo, modo=0o755):
        """O `.patch` que o `git diff` gera para criar o HOOK com `conteudo` e `modo` (o arquivo de correção do autor)."""
        arq = self.gravar(HOOK, conteudo)
        arq.chmod(modo)
        self.git("add", HOOK)
        texto = self.git_em(self.proj, "diff", "--cached", "--no-color") + "\n"
        self.git("rm", "-q", "--cached", HOOK)
        arq.unlink()
        return texto

    def aplicar(self, conteudo=None, autor=DONO, committer=DONO, modo=0o755):
        """O commit do dono: `git apply` do PATCH (ou o HOOK com `conteudo`, à mão) e o commit com autor e committer dados."""
        if conteudo is None:
            self.git("apply", PATCH)
        else:
            self.gravar(HOOK, conteudo)
        (self.proj / HOOK).chmod(modo)
        self.git("add", HOOK)
        self.git("-c", f"user.email={committer}", "-c", "user.name=Dono", "commit", "-q", f"--author=Dono <{autor}>", "-m", "chore: PP1")
        return self.git("rev-parse", "HEAD")

    def declarar_patch(self, sha, patch=PATCH):
        return self.declarar(nome=HOOK, sha=sha, linha=f"- 2026-11-20 10:00: patch do dono aplicado `{HOOK}` commit {sha} patch {patch}\n")

    def test_quatro_condicoes_cumprem_e_a_conferencia_grava_os_shas(self):
        x = self.aplicar()
        self.declarar_patch(x)
        sha_patch = hashlib.sha256((self.proj / PATCH).read_bytes()).hexdigest()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        self.assertRegex(saida, rf'escopo: ok \(patch do dono {x}, patch "{PATCH}" sha256 {sha_patch}, DECISÃO DO DONO exemplo:\d+\) "{HOOK}"')
        self.assertRegex(self.pedido(), rf'\n- [0-9-]+ [0-9:]+: aplicado pelo dono conferido "{HOOK}" patch "{PATCH}" sha256 {sha_patch} commit {x}\n'
                                        rf'- [0-9-]+ [0-9:]+: entrega conferida {x}\n')

    def test_patch_adulterado_ou_aplicado_diferente_recusa(self):
        difere = "o commit difere do .patch revisado aplicado sobre o pai"
        casos = (("d: o commit com uma linha a mais", dict(conteudo=HOOK_NOVO + "echo a mais\n"), None, difere),
                 ("d: o patch com uma linha a mais", dict(conteudo=HOOK_NOVO), HOOK_NOVO + "echo a mais\n", difere),
                 ("a: o modo diferente do patch", dict(modo=0o644), None, difere),
                 ("a: o patch que não se aplica", {}, "corrompido\n", "o .patch revisado não se aplica sobre o pai"))
        for caso, aplicar, adulterado, motivo in casos:
            with self.subTest(caso):
                if adulterado:
                    self.gravar(PATCH, adulterado if adulterado == "corrompido\n" else self.patch_de(adulterado))
                    self.git("add", PATCH)
                    self.commit("docs: patch adulterado")
                if "conteudo" not in aplicar and adulterado == "corrompido\n":
                    aplicar = dict(conteudo=HOOK_NOVO)
                self.declarar_patch(self.aplicar(**aplicar))
                self.fora(nome=HOOK, motivo=motivo)
                self.git("reset", "-q", "--hard", "HEAD^" if not adulterado else "HEAD~2")

    def test_commit_que_nao_e_do_dono_recusa(self):
        motivo = "autor ou committer não é o dono"
        for caso, kw, emails in (("b: committer de outro", dict(committer="a@b"), [DONO]),
                                 ("b: autor de outro", dict(autor="a@b"), [DONO]),
                                 ("b: sem emails_do_dono", {}, []),
                                 ("b: sem a configuração", {}, None),
                                 ("b: emails_do_dono que não é lista", {}, DONO),
                                 ("b: emails_do_dono nulo", {}, ('{"emails_do_dono": null}',)),
                                 ("b: configuração que não é objeto", {}, (f'["{DONO}"]',)),
                                 ("b: e-mail que não é texto", {}, [1]),
                                 ("b: e-mail que só contém o do dono", {}, ["ono@exemplo"])):
            with self.subTest(caso):
                self.configurar(emails)
                self.declarar_patch(self.aplicar(**kw))
                self.fora(nome=HOOK, motivo=motivo)
                self.git("reset", "-q", "--hard", "HEAD^")

    def test_linha_sem_patch_ou_patch_fora_da_branch_recusa(self):
        x = self.aplicar()
        sem = "sem ` patch <caminho>` válido"
        for caso, linha, motivo in (("sem patch", f"- 2026-11-20 10:00: patch do dono aplicado `{HOOK}` commit {x}\n", sem),
                                    ("patch com ..", f"- 2026-11-20 10:00: patch do dono aplicado `{HOOK}` commit {x} patch ../pp1.patch\n", sem),
                                    ("patch de outra linha", f"- 2026-11-20 10:00: patch do dono aplicado `{HOOK}` commit {x}\n"
                                     f"- 2026-11-20 10:01: patch do dono aplicado `bin/app` commit {x} patch {PATCH}\n", sem),
                                    ("patch ausente no pai", None, "o .patch não está na branch no pai do commit do dono")):
            with self.subTest(caso):
                if linha:
                    self.declarar(nome=HOOK, sha=x, linha=linha)
                else:
                    self.declarar_patch(x, patch="docs/notas/outro.patch")
                self.fora(nome=HOOK, motivo=motivo)

    def test_git_que_falha_ou_politica_ilegivel_recusa(self):
        texto, real = self.declarar_patch(self.aplicar()), fc.git
        head = self.git("rev-parse", "HEAD")
        for passo in ("read-tree", "log", "grep"):
            with self.subTest(passo), mock.patch.object(fc, "git", lambda raiz, *a, **kw: (1, "") if passo in a else real(raiz, *a, **kw)):
                linha, avisos = fc.isencao_do_dono(self.proj, "exemplo", texto, [head], HOOK, self.base, head, self.base, "melhoria/x")
                self.assertIsNone(linha)
                self.assertIn("não isenta", avisos[0][0])
        with mock.patch.object(fc, "carregar_politica", lambda: {}):  # sem a lista dos arquivos em vigor, todo arquivo pede o patch
            self.assertTrue(fc.em_vigor("templates/projeto/LEIAME.md"))
        self.assertFalse(fc.em_vigor("templates/projeto/.githooks/pre-push"))
        self.assertFalse(fc.em_vigor("CLAUDE.md"))  # na lista da conformidade, mas não é `arquivo em vigor`
        self.assertTrue(fc.em_vigor(".claude/settings.json"))

    def test_indice_do_repositorio_intacto(self):
        texto, head = self.declarar_patch(self.aplicar()), self.git("rev-parse", "HEAD")
        self.gravar("docs/notas/b.md", "b\n")
        self.git("add", "docs/notas/b.md")
        linha, _ = fc.isencao_do_dono(self.proj, "exemplo", texto, [head], HOOK, self.base, head, self.base, "melhoria/x")
        self.assertIn("escopo: ok (patch do dono", linha[0])
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "docs/notas/b.md")  # o patch se aplica num índice temporário

    def test_s1_mudanca_anterior_da_branch_no_arquivo_recusa(self):
        """A1 (sonda S1 do review e da segurança): um commit de agente cria o hook com uma linha não revisada; o `.patch` revisado só
        soma `# revisado`; o dono o aplica sobre o pai. O pai difere do Base-sha no caminho: recusa, e o head não sai lavado."""
        self.gravar(HOOK, "#!/bin/sh\necho NAO-REVISADO\n").chmod(0o755)
        self.git("add", HOOK)
        self.commit("chore: hook do agente")
        self.gravar(HOOK, "#!/bin/sh\necho NAO-REVISADO\n# revisado\n")
        self.gravar(PATCH, self.git_em(self.proj, "diff", "--no-color", "--", HOOK) + "\n")
        self.git("checkout", "-q", "--", HOOK)
        self.aprovar()
        self.git("add", PATCH, "docs/security")
        self.commit("docs: patch revisado")
        self.declarar_patch(self.aplicar())
        self.assertIn("NAO-REVISADO", (self.proj / HOOK).read_text(encoding="utf-8"))
        self.fora(nome=HOOK, motivo=f'"{HOOK}" difere entre o pai do commit do dono, o Base-sha e a develop atual')

    def test_develop_atual_diferente_ou_sem_resolver_recusa(self):
        """A1: a develop atual que mudou o caminho, ou que não se resolve, recusa; o git que falha no ls-tree também."""
        texto, head = self.declarar_patch(self.aplicar()), self.git("rev-parse", "HEAD")
        outra = self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit-tree", "-p", self.base, "-m", "develop com o hook", f"{head}^{{tree}}")
        for caso, base_ref, motivo in (("develop com o hook", outra, "difere entre o pai do commit do dono"),
                                       ("develop sem resolver", None, "a develop atual não se resolve")):
            with self.subTest(caso):
                linha, avisos = fc.isencao_do_dono(self.proj, "exemplo", texto, [head], HOOK, self.base, head, base_ref, "melhoria/x")
                self.assertIsNone(linha)
                self.assertIn(motivo, avisos[0][0])
        real = fc.entrada_na_arvore
        with mock.patch.object(fc, "entrada_na_arvore", lambda raiz, ref, nome: None if ref == f"{head}^1" else real(raiz, ref, nome)):
            linha, avisos = fc.isencao_do_dono(self.proj, "exemplo", texto, [head], HOOK, self.base, head, self.base, "melhoria/x")
        self.assertIsNone(linha)
        self.assertIn("(o git falhou)", avisos[0][0])

    def test_emails_da_arvore_do_base_sha_e_nao_da_branch(self):
        """A2: a lista versionada no Base-sha vale sobre a do disco; versionada só na branch, nada isenta (nem pelo disco)."""
        self.git("add", "-f", ".forge/config.json")
        versionada = self.commit("chore: lista na branch")
        self.configurar(["outro@x"])
        self.assertEqual(fc.emails_do_dono(self.proj, versionada, versionada), {DONO})
        self.assertEqual(fc.emails_do_dono(self.proj, self.base, versionada), set())
        self.assertEqual(fc.emails_do_dono(self.proj, self.base, self.base), {"outro@x"})
        self.configurar([DONO])
        self.declarar_patch(self.aplicar())
        self.fora(nome=HOOK, motivo="autor ou committer não é o dono")

    def test_patch_sem_parecer_de_seguranca_aprovado_que_o_cite_recusa(self):
        """A3: o sha256 do .patch aplicado tem de estar num parecer de segurança aprovado no head."""
        motivo = "nenhum parecer de segurança aprovado da branch e do pedido, no head, cita o sha256 do .patch"
        for caso, kw in (("reprovado", dict(parecer="reprovado")), ("parecer de review", dict(tipo="review")), ("sem frontmatter", dict(cru=True)),
                         ("outro sha256", dict(sha256="0" * 64)), ("sha256 como parte de palavra", dict(sha256="a" + hashlib.sha256(
                             (self.proj / PATCH).read_bytes()).hexdigest()))):
            with self.subTest(caso):
                self.aprovar(**kw)
                self.git("add", "docs/security")
                self.commit("docs: parecer")
                self.declarar_patch(self.aplicar())
                self.fora(nome=HOOK, motivo=motivo)
                self.git("reset", "-q", "--hard", "HEAD~2")

    def test_a4_so_o_parecer_aprovado_da_propria_branch_e_pedido_vale(self):
        """A4 (E52.6; sondas S3 e S4 da segurança): o parecer que cita o sha256 vale só com `branch:` e `pedido:` da entrega conferida,
        `parecer: aprovado` e fora de docs/security/aceites/ e ameacas/; o parecer do setUp, que valia, sai do caso."""
        motivo = "nenhum parecer de segurança aprovado da branch e do pedido, no head, cita o sha256 do .patch"
        for caso, kw in (("S3: parecer de outra branch", dict(branch="melhoria/outra")),
                         ("parecer de outro pedido", dict(pedido="outro")),
                         ("riscos-aceitos", dict(parecer="riscos-aceitos")),
                         ("S4: em aceites/", dict(caminho="docs/security/aceites/exemplo.md")),
                         ("em ameacas/", dict(caminho="docs/security/ameacas/exemplo.md"))):
            with self.subTest(caso):
                self.git("rm", "-q", "docs/security/x.md")
                self.aprovar(**kw)
                self.git("add", "docs/security")
                self.commit("docs: parecer")
                self.declarar_patch(self.aplicar())
                self.fora(nome=HOOK, motivo=motivo)
                self.git("reset", "-q", "--hard", "HEAD~2")
        self.aprovar(caminho="docs/security/outro.md")  # o mesmo parecer, válido, fora das pastas recusadas: isenta
        self.git("rm", "-q", "docs/security/x.md")
        self.git("add", "docs/security")
        self.commit("docs: parecer")
        texto, head = self.declarar_patch(self.aplicar()), self.git("rev-parse", "HEAD")
        linha, _ = fc.isencao_do_dono(self.proj, "exemplo", texto, [head], HOOK, self.base, head, self.base, "melhoria/x")
        self.assertIn("escopo: ok (patch do dono", linha[0])
