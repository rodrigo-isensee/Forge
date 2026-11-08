"""VOLTAS-REVISOR-WT (E6a-1): o `forge-check pr` confere as linhas `parecer conferido <sha40>` do `## Histórico` (M1 no `pr`, M5 na
leitura, M8, T-1, T-2; testes t1, t10, t11, t14 e t19 das ameaças). Só acrescenta recusa. E6a-2: `entrega --branch parecer/*` (M3, M5,
M9; t4 a t8, t15 e o caso 11). E6a-3: o `entrega` confere os merges do intervalo (M4, M2, C-11, M9 no merge; t1, t2, t9, t12,
t20 e o caso 12). E6a-4: o "parecer trazido" (M1 no trazido, T-3, S4; t3, t13, A10 e os compostos A1, A5 e t20 com o arquivo
também trazido). E6b-1: a volta lê o último P de cada arquivo fora da `--ref` (T-2). Repositório temporário."""
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import git  # noqa: E402
from test_volta_por_delta import Repositorio, SHA_FALSO  # noqa: E402
import test_volta_por_delta as volta  # noqa: E402 (o módulo: os testes de lá não rodam de novo)
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

PARECER = ("---\ntipo: review\ncontrato: 1\npedido: x\nbranch: {branch}\ncommit: {commit}\nparecer: {parecer}\n"
           "revisor: forge:tech-lead\ndata: {data}\n---\n\n## Achados\n")
MARCAS = ("parecer conferido", "último parecer conferido", "vigente não é")


class ComParecer(Repositorio):
    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"src/app.txt": "v2\n"}, "código")
        brief = self.home / ".forge-contrib" / "docs" / "briefs" / "p1-tech-lead-1.md"  # o slug `x` acha o pedido `p1` pelo brief
        brief.parent.mkdir(parents=True)
        brief.write_text("Pedido: p1\nBranch: melhoria/x   Base: develop\n\n## Objetivo\nx\n", encoding="utf-8")

    def parecer(self, nome, parecer="aprovado", branch="melhoria/x", arquivo="docs/reviews/x.md", data="2026-11-06"):
        """P: um commit de parecer numa `parecer/<nome>` nascida do head de código, como a worktree do revisor."""
        git("switch", "-q", "-c", f"parecer/{nome}", self.c1, cwd=self.repo)
        p = self.commitar({arquivo: PARECER.format(branch=branch, commit=self.c1, parecer=parecer, data=data)}, f"parecer {nome}")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        return p

    def historico(self, *shas, forma="parecer conferido"):
        self.gravar_pedido(extra="".join(f"- 2026-11-06 18:0{i}: {forma} {s} (review)\n" for i, s in enumerate(shas)))


class PrLeParecerConferido(ComParecer):
    def novas(self, ref="melhoria/x", pedido="x"):
        rc, saida = self.check("pr", pedido, "--ref", ref)
        self.assertTrue(saida.strip(), "o forge-check caiu sem saída (a exceção vai ao stderr)")
        return [linha for linha in saida.splitlines() if any(m in linha for m in MARCAS)]

    def test_ultimo_conferido_fora_da_branch_e_violacao_e_o_superado_nao(self):  # t1 (lado pr), t19, M8
        p1, p2 = self.parecer("r1"), self.parecer("r2", parecer="reprovado")
        git("merge", "-q", "--no-edit", p1, cwd=self.repo)
        self.historico(p1, p2)
        self.assertEqual(self.novas(), [f"docs/reviews/x.md: parecer conferido {p2[:7]} fora da branch; quem retoma a branch o traz (R-REVIEW)"])
        self.historico(p2, p1)  # P1 é o último: P2 superado fora da branch não é violação
        self.assertEqual(self.novas(), [])

    def test_merge_s_ours_deixa_o_blob_diferente(self):  # t10
        p1 = self.parecer("r1")
        git("merge", "-q", "--no-edit", "-s", "ours", p1, cwd=self.repo)
        self.historico(p1)
        self.assertEqual(self.novas(), [f"docs/reviews/x.md: blob diferente do último parecer conferido {p1[:7]} (R-REVIEW)"])

    def test_merge_squash_deixa_o_parecer_fora_da_branch(self):  # t11
        p1 = self.parecer("r1")
        git("merge", "-q", "--squash", p1, cwd=self.repo)
        git("commit", "-q", "-m", "squash", cwd=self.repo)
        self.historico(p1)
        self.assertEqual(self.novas(), [f"docs/reviews/x.md: parecer conferido {p1[:7]} fora da branch; quem retoma a branch o traz (R-REVIEW)"])

    def test_parecer_mais_novo_nao_conferido_nao_vira_o_vigente(self):  # T-1
        p1 = self.parecer("r1", data="2026-11-05")
        git("merge", "-q", "--no-edit", p1, cwd=self.repo)
        self.commitar({"docs/reviews/y.md": PARECER.format(branch="melhoria/x", commit=self.c1, parecer="aprovado", data="2026-11-06")})
        self.historico(p1)
        self.assertEqual(self.novas(), ["docs/reviews/y.md: o parecer vigente não é o de um `parecer conferido` do Histórico (R-REVIEW)"])

    def test_parecer_conferido_de_outra_branch_do_pedido_nao_conta(self):  # o `pr` da branch só olha os pareceres dela (E11)
        p1, p2 = self.parecer("r1", branch="melhoria/outra", arquivo="docs/reviews/outra.md"), self.parecer("r2")
        self.historico(p1, p2)
        self.assertEqual(self.novas(), [f"docs/reviews/x.md: parecer conferido {p2[:7]} fora da branch; quem retoma a branch o traz (R-REVIEW)"])

    def test_sha_que_o_git_nao_le_e_violacao_so_na_branch_de_trabalho(self):  # falha fechada; na integração, como hoje
        self.historico(SHA_FALSO)
        self.assertEqual(self.novas(), [f"docs/pedidos: parecer conferido {SHA_FALSO[:7]}: o git não lê o commit nem o pai dele; "
                                        "rode git fetch (VOLTAS-REVISOR-WT)"])
        self.assertEqual(self.novas(ref="develop", pedido="p1"), [])  # integração: fora do `de_trabalho`

    def test_regex_nao_se_cruzam(self):  # t14 (M5): `conferida` não é `parecer conferido`, e vice-versa
        p1 = self.parecer("r1")
        self.historico(p1, forma="entrega conferida")
        self.assertEqual(self.novas(), [])
        self.historico(p1)
        self.assertEqual(self.novas(), [f"docs/reviews/x.md: parecer conferido {p1[:7]} fora da branch; quem retoma a branch o traz (R-REVIEW)"])
        git("merge", "-q", "--no-edit", p1, cwd=self.repo)
        rc, saida = self.entrega(desde=p1)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_sem_pedido_e_fora_do_historico_nada_muda(self):
        p1 = self.parecer("r1")
        self.assertEqual(self.novas(), [])  # o pedido não existe
        self.gravar_pedido(secao="Decisões", extra=f"- parecer conferido {p1} (review)\n")
        self.assertEqual(self.novas(), [])
        self.historico(p1)
        self.assertEqual(len(self.novas()), 1)


class EntregaDaBranchDeParecer(Repositorio):
    FORA = "escopo: fora (branch de parecer só leva parecer)"

    def setUp(self):
        super().setUp()
        self.s = self.commitar({"src/app.txt": "v2\n"}, "código")
        self.gravar_pedido([self.s])

    def revisor(self, arquivos, papel="tech-lead", brief="p1-tech-lead-1"):
        """P: o commit do revisor na `parecer/<brief>` nascida de S; o brief traz o papel (`Agente destino:`), ou não existe."""
        if papel:
            caminho = self.home / ".forge-contrib" / "docs" / "briefs" / f"{brief}.md"
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(f"Agente destino: forge:{papel}\nPedido: p1\n\n## Objetivo\nx\n", encoding="utf-8")
        git("switch", "-q", "-c", f"parecer/{brief}", self.s, cwd=self.repo)
        if arquivos is None:
            return git("commit", "-q", "--allow-empty", "-m", "vazio", cwd=self.repo)
        if callable(arquivos):  # link ou modo, que o `commitar` não grava
            arquivos, _ = {}, arquivos()
        return self.commitar(arquivos, "parecer")

    def conferir(self, brief="p1-tech-lead-1", desde=True):
        return self.entrega(desde=self.s if desde else None, etapa="review", branch=f"parecer/{brief}")

    def assert_fora(self, brief="p1-tech-lead-1", desde=True):
        rc, saida = self.conferir(brief, desde)
        self.assertEqual(rc, 1, saida)
        self.assertIn(self.FORA, saida)
        self.assertNotIn("linha-final", saida)  # t15: rc 1 não imprime a linha final

    def test_parecer_na_pasta_do_papel_imprime_a_linha_final(self):  # M5: só com rc 0, o sha do rev-parse
        for papel, pasta in (("tech-lead", "docs/reviews"), ("security-engineer", "docs/security")):
            p = self.revisor({f"{pasta}/x.md": "parecer\n"}, papel, f"p1-{papel}-1")
            rc, saida = self.conferir(f"p1-{papel}-1")
            self.assertEqual(rc, 0, saida)
            self.assertEqual(saida.splitlines()[-1], f"linha-final: parecer-conferido {p}")

    def test_branch_de_trabalho_nao_imprime_a_linha_final(self):
        rc, saida = self.entrega(desde=self.s, etapa="review")
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("linha-final", saida)

    def test_codigo_na_branch_de_parecer_reprova(self):  # t4, caso 11
        self.revisor({"docs/reviews/x.md": "parecer\n", "src/a.js": "x\n"})
        self.assert_fora()

    def test_aceite_na_branch_de_parecer_reprova(self):  # t5, M9
        self.revisor({"docs/security/aceites/p.md": "aceite\n"}, "security-engineer", "p1-security-engineer-1")
        self.assert_fora("p1-security-engineer-1")

    def test_pasta_de_outro_papel_reprova(self):  # t6
        self.revisor({"docs/security/x.md": "parecer\n"})
        self.assert_fora()

    def test_dois_commits_ou_merge_reprova(self):  # t7
        self.revisor({"docs/reviews/x.md": "parecer\n"})
        self.commitar({"docs/reviews/x.md": "parecer 2\n"})
        self.assert_fora()
        git("switch", "-q", "-c", "lado", self.s, cwd=self.repo)
        self.commitar({"docs/reviews/y.md": "outro\n"})
        self.revisor({"docs/reviews/x.md": "parecer\n"}, brief="p1-tech-lead-2")
        git("merge", "-q", "--no-ff", "--no-edit", "lado", cwd=self.repo)
        self.assert_fora("p1-tech-lead-2")

    def test_link_e_modo_executavel_reprovam(self):  # t8: um commit só sobre S, então só o modo reprova
        x = self.repo / "docs" / "reviews" / "x.md"

        def link():
            x.parent.mkdir(parents=True)
            os.symlink("../../src/app.txt", x)

        def executavel():
            x.parent.mkdir(parents=True)
            x.write_text("parecer\n", encoding="utf-8")
            x.chmod(0o755)
        for brief, gravar in (("p1-tech-lead-1", link), ("p1-tech-lead-2", executavel)):
            self.revisor(gravar, brief=brief)
            self.assert_fora(brief)

    def test_fora_do_md_sem_desde_vazio_e_nome_com_controle_reprovam(self):
        self.revisor({"docs/reviews/x.txt": "parecer\n"})
        self.assert_fora()
        self.revisor({"docs/reviews/x.md": "parecer\n"}, brief="p1-tech-lead-2")
        self.assert_fora("p1-tech-lead-2", desde=False)
        self.revisor({"docs/reviews/a\x01.md": "parecer\n"}, brief="p1-tech-lead-3")
        self.assert_fora("p1-tech-lead-3")
        self.revisor(None, brief="p1-tech-lead-4")
        self.assert_fora("p1-tech-lead-4")

    def test_papel_sem_pasta_ou_brief_ilegivel_reprova(self):  # docs/qa fica fora; o papel ausente não vira a pasta "None"
        self.revisor({"docs/qa/x.md": "parecer\n"}, "qa-engineer", "p1-qa-engineer-1")
        self.assert_fora("p1-qa-engineer-1")
        self.revisor({"None/x.md": "parecer\n"}, None, "p1-sem-brief-1")
        self.assert_fora("p1-sem-brief-1")
        self.revisor({"docs/reviews/x.md": "parecer\n"}, brief="a/b")  # o brief é arquivo de docs/briefs/, nunca de subpasta
        self.assert_fora("a/b")


class EntregaConfereOMerge(ComParecer):
    def merge(self, *shas, sem_commit=False):
        git("merge", "-q", "--no-ff", "--no-edit", *(["--no-commit"] if sem_commit else []), *shas, cwd=self.repo)

    def lado(self, nome, arquivos):
        """Um sha que não é parecer: um commit numa branch `nome` nascida do head de código."""
        git("switch", "-q", "-c", nome, self.c1, cwd=self.repo)
        sha = self.commitar(arquivos, nome)
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        return sha

    def foras(self, etapa="qa"):
        rc, saida = self.entrega(etapa=etapa)
        return rc, [linha for linha in saida.splitlines() if linha.startswith("escopo: fora")]

    def test_ultimo_conferido_passa_e_o_superado_reprova(self):  # t1 (lado entrega), M2
        p1, p2 = self.parecer("r1"), self.parecer("r2", parecer="reprovado")
        self.historico(p1, p2)
        self.merge(p2)
        self.commitar({"docs/qa/x.md": "parecer do QA\n"}, "qa")  # o do próprio QA não é parecer alheio
        self.assertEqual(self.foras(), (0, []))
        self.assertEqual(self.foras("codigo"), (0, []))
        self.historico(p2, p1)  # o head fica com os bytes de P2, agora superado por P1
        self.assertEqual(self.foras(), (1, ['escopo: fora (parecer não conferido ou superado) "docs/reviews/x.md"']))

    def test_merge_de_sha_nao_conferido_reprova(self):  # t2, t9 (A5), M4
        p1, p2 = self.parecer("r1"), self.parecer("r2", arquivo="docs/reviews/y.md")
        outro = self.lado("lado", {"KANBAN.md": "x\n"})
        self.historico(p1)
        self.merge(p1, p2, outro)
        m = self.head()[:7]
        self.assertEqual(self.foras("codigo"), (1, [f"escopo: fora (merge de {p2[:7]} não conferido)",
                                                   f"escopo: fora (merge de {outro[:7]} não conferido)",
                                                   f'escopo: fora (o merge {m} traz "KANBAN.md" fora dos pareceres conferidos)',
                                                   f'escopo: fora (o merge {m} traz "docs/reviews/y.md" fora dos pareceres conferidos)',
                                                   'escopo: fora (parecer não conferido ou superado) "docs/reviews/y.md"']))
        self.assertEqual(self.foras("review"), (0, []))  # fora de `qa` e `codigo`, como hoje

    def test_merge_que_traz_bytes_fora_do_parecer_reprova(self):  # t12 (--no-commit com o blob alterado)
        p1 = self.parecer("r1")
        self.historico(p1)
        self.commitar({"src/novo.txt": "n\n"}, "depois do P")
        self.merge(p1, sem_commit=True)
        (self.repo / "src" / "novo.txt").unlink()  # a remoção também é trazida, e o P também não tem o arquivo (blob vazio dos dois lados)
        self.commitar({"docs/reviews/x.md": "outro\n", "src/b.txt": "b\n"}, "merge")
        m = self.head()[:7]
        self.assertEqual(self.foras(), (1, [f'escopo: fora (o merge {m} traz "docs/reviews/x.md" fora dos pareceres conferidos)',
                                            f'escopo: fora (o merge {m} traz "src/b.txt" fora dos pareceres conferidos)',
                                            f'escopo: fora (o merge {m} traz "src/novo.txt" fora dos pareceres conferidos)',
                                            'escopo: fora (parecer não conferido ou superado) "docs/reviews/x.md"']))

    def test_sem_linha_no_pedido_so_o_parecer_e_o_aceite_reprovam(self):  # caso 12 (C-11), t20 e caso 14 (M9)
        self.historico()
        self.merge(self.lado("lado", {"KANBAN.md": "x\n"}))
        self.assertEqual(self.foras(), (0, []))  # merge que não é de `parecer/*` fica como hoje
        self.merge(self.parecer("r1"))
        self.assertEqual(self.foras(), (1, ["escopo: fora (parecer trazido sem registro no Histórico)"]))
        self.merge(self.lado("aceite", {"docs/security/aceites/p.md": "aceite\n"}))
        self.assertIn(f"escopo: fora (aceite trazido pelo merge {self.head()[:7]})", self.foras()[1])

    def test_git_que_falha_reprova(self):  # falha fechada: sem a árvore do merge, depois sem o commit do outro pai
        outro = self.lado("lado", {"KANBAN.md": "x\n"})
        self.historico()
        self.merge(outro)
        merge, arvore = self.head(), self.head("HEAD^{tree}")
        self.commitar({"src/c.txt": "c\n"}, "depois")
        for sha, passo in ((arvore, f"diff do merge {merge[:7]}"), (outro, "rev-list dos merges")):
            (self.repo / ".git" / "objects" / sha[:2] / sha[2:]).unlink()
            rc, saida = self.entrega(etapa="qa")
            self.assertIn(f"escopo: o git falhou ({passo}); o escopo não foi lido", saida.splitlines())

    def test_merge_da_base_nao_reprova(self):
        p1 = self.parecer("r1")
        self.historico(p1)
        self.merge(p1)
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar({"docs/security/aceites/z.md": "aceite de outro pedido\n"}, "base")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        self.merge("develop")
        self.assertEqual(self.foras(), (0, []))


class ParecerTrazido(ComParecer):
    """O QA traz por merge o último P conferido; o parecer antigo da branch tem linhas que o P remove (a A6 daria `confira`)."""
    merge, lado = EntregaConfereOMerge.merge, EntregaConfereOMerge.lado  # só os ajudantes; os testes de lá não rodam de novo

    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"docs/reviews/x.md": "antigo 1\nantigo 2\n"}, "parecer da volta anterior")

    def autoria(self, sha, nome="docs/reviews/x.md", papel="tech-lead"):
        texto = git("show", f"{sha}:{nome}", cwd=self.repo).stdout
        (self.repo / ".forge" / "run").mkdir(parents=True, exist_ok=True)
        with (self.repo / ".forge" / "run" / "autoria.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"caminho": nome, "sha256": hashlib.sha256(texto.strip().encode()).hexdigest(), "papel": papel}) + "\n")

    def conferir(self, *shas, etapa="qa"):
        self.gravar_pedido([self.c1], extra="".join(f"- 2026-11-06 18:0{i}: parecer conferido {s} (review)\n" for i, s in enumerate(shas)))
        rc, saida = self.entrega(desde=self.c1, etapa=etapa)
        return rc, [linha for linha in saida.splitlines() if linha.startswith("escopo:")]

    def test_o_ultimo_p_trazido_com_remocao_e_ok_em_qualquer_etapa(self):  # t3, S4
        p1, p2 = self.parecer("r1"), self.parecer("r2", parecer="reprovado")
        self.merge(p2)
        self.autoria(p2)
        for etapa in ("qa", "codigo", "review"):
            self.assertEqual(self.conferir(p1, p2, etapa=etapa), (0, [f'escopo: ok (parecer trazido {p2[:7]} de tech-lead) "docs/reviews/x.md"']))
        (self.repo / ".forge" / "run" / "autoria.jsonl").unlink()  # sem autoria, a regra de hoje
        self.assertEqual(self.conferir(p1, p2)[1], ['escopo: confira "docs/reviews/x.md" +12 -2'])

    def test_bytes_do_p_antigo_com_o_ultimo_ancestral_nao_sao_trazidos(self):  # t13, A10, T-3, A1
        p1, p2 = self.parecer("r1"), self.parecer("r2", parecer="reprovado")
        self.merge(p2)
        self.commitar({"docs/reviews/x.md": git("show", f"{p1}:docs/reviews/x.md", cwd=self.repo).stdout}, "volta aos bytes de P1")
        self.autoria(p1)
        self.assertEqual(self.conferir(p1, p2, etapa="review"), (0, [
            'escopo: confira "docs/reviews/x.md" +12 -2 (anexo com remoção do parecer de tech-lead: reprova se fora do "Entregar" '
            'da entrega do tech-lead)']))
        self.assertEqual(self.conferir(p1, p2), (1, ['escopo: fora (parecer não conferido ou superado) "docs/reviews/x.md"']))

    def test_os_bytes_do_p_sem_o_p_ancestral_nao_sao_trazidos(self):  # M1: P ancestral do head
        p1 = self.parecer("r1")
        self.commitar({"docs/reviews/x.md": git("show", f"{p1}:docs/reviews/x.md", cwd=self.repo).stdout}, "cópia sem o merge")
        self.autoria(p1)
        linhas = "".join(self.conferir(p1)[1])
        self.assertNotIn("parecer trazido", linhas)
        self.assertIn("anexo com remoção", linhas)

    def test_trazido_nao_escapa_do_merge_nao_conferido_nem_do_aceite(self):  # A5 e t20 com o arquivo trazido, M4, M9
        p1, ps = self.parecer("r1"), self.parecer("s1", arquivo="docs/security/aceites/p.md")
        outro = self.lado("lado", {"KANBAN.md": "x\n"})
        self.merge(p1, ps, outro)
        self.autoria(p1)
        self.autoria(ps, "docs/security/aceites/p.md", "seguranca")
        m = self.head()[:7]
        rc, linhas = self.conferir(p1, ps)
        self.assertEqual(rc, 1)
        for linha in (f'escopo: ok (parecer trazido {p1[:7]} de tech-lead) "docs/reviews/x.md"',
                      f"escopo: fora (aceite trazido pelo merge {m})", f"escopo: fora (merge de {outro[:7]} não conferido)"):
            self.assertIn(linha, linhas)
        self.assertNotIn("p.md", "".join(linha for linha in linhas if linha.startswith("escopo: ok")))


class VoltaLeParecerConferido(Repositorio):
    """E6b-1 (T-2): `brief gerar --volta` e a conferência da volta leem o último P de cada arquivo fora da `--ref` (`cat-file blob`)."""
    B = volta.BriefDeVolta
    gerar, conferir, preenchido = B.gerar, B.conferir, B.preenchido  # só os ajudantes

    def setUp(self):
        super().setUp()
        self.pedido = self.pedido.with_name("pedido-sintetico.md")
        self.c1 = self.commitar({"src/app.txt": "v2\n"}, "entrega")
        (self.repo / ".git" / "info" / "exclude").write_text("docs/briefs/\n", encoding="utf-8")
        git("update-ref", "refs/remotes/origin/develop", self.base, cwd=self.repo)
        self.rel_anterior = "docs/briefs/pedido-sintetico-dev-exemplo-1.md"
        (self.repo / "docs" / "briefs").mkdir(parents=True)
        (self.repo / self.rel_anterior).write_bytes(self.B.ANTERIOR.read_bytes())

    def p(self, nome, achados=B.ACHADOS, branch="melhoria/x", arquivo="docs/reviews/p1.md", tipo="review"):
        """P: o parecer reprovado numa `parecer/<nome>` nascida do head da branch, fora dela."""
        git("switch", "-q", "-c", f"parecer/{nome}", cwd=self.repo)
        texto = self.B.REVIEW.format(c=self.c1[:7], p="reprovado", corpo=achados)
        sha = self.commitar({arquivo: texto.replace("melhoria/x", branch).replace("review", tipo, 1)}, f"parecer {nome}")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        return sha

    def historico(self, *shas):
        self.pedido.write_text(self.B.PEDIDO_FIXTURE.read_text(encoding="utf-8") + "\n## Histórico\n" + "".join(
            f"- 2026-11-07 10:0{i}: parecer conferido {s} (review)\n" for i, s in enumerate(shas)), encoding="utf-8")

    def test_gerar_e_conferir_leem_o_p_fora_da_ref(self):  # o caso da seção 6 do desenho; marca e Ler com o sha do P
        p = self.p("r1")
        self.historico(p)
        rc, saida = self.gerar()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"- (review {p[:7]} A1) a função perde o erro de domínio [src/app.txt:3]\n", saida)
        self.assertIn(f"- docs/reviews/p1.md (parecer, lido de {p[:7]})", saida)
        self.assertEqual(self.gerar("--parecer", "docs/reviews/p1.md")[0], 0)  # com --parecer, do P que o contém
        self.assertNotIn("falta achado", self.conferir(self.preenchido(saida))[1])
        sem_a1 = self.preenchido(saida).replace(f"(review {p[:7]} A1)", "(sem A1)")
        self.assertIn('volta: falta achado "A1" de docs/reviews/p1.md', self.conferir(sem_a1)[1])
        self.historico(SHA_FALSO)  # falha fechada nos dois lados
        self.assertIn(f"parecer conferido {SHA_FALSO[:7]}: o git não lê o commit nem o pai dele", self.gerar()[1])
        self.assertIn(f"volta: parecer conferido {SHA_FALSO[:7]}: o git não lê", self.conferir(self.preenchido(saida))[1])

    def test_o_ultimo_p_fora_da_ref_vence_a_ref_e_o_de_dentro_nao(self):  # rodada 2: a ref tem o parecer da volta anterior
        git("merge", "-q", "--no-edit", self.p("r1"), cwd=self.repo)
        p2 = self.p("r2", "## Achados\n- A1 (bloqueante) src/app.txt:5 · erro da rodada 2\n")
        self.historico(p2)
        self.assertIn(f"(review {p2[:7]} A1) erro da rodada 2", self.gerar()[1])
        git("merge", "-q", "--no-edit", p2, cwd=self.repo)  # P2 já na ref: vale a ref, como hoje
        corpo = "## Achados\n- A1 (bloqueante) a.py:9 · da ref\n"
        self.commitar({"docs/reviews/p1.md": self.B.REVIEW.format(c=self.c1[:7], p="reprovado", corpo=corpo)})
        self.assertIn(f"(review {self.head()[:7]} A1) da ref", self.gerar()[1])

    def test_p_de_outra_branch_nao_e_lido_e_o_de_outra_pasta_so_no_tipo_dele(self):  # como o `pr` (E11)
        self.historico(self.p("r1", branch="melhoria/outra"))
        rc, saida = self.gerar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("nenhum parecer lido", saida)
        ps = self.p("s1", arquivo="docs/security/s1.md", tipo="revisao-seguranca")
        self.historico(ps)
        self.assertEqual(self.gerar()[1].count(f"(revisao-seguranca {ps[:7]} A1)"), 1)


QA = ("---\ntipo: qa\ncontrato: 1\npedido: x\nbranch: melhoria/x\ncommit: {commit}\nparecer: {parecer}\nescopo: completo\n"
      "bugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\ndata: 2026-11-06\n---\n\n## Achados\n")
SEM_PREVIO = ("bin/forge-fechar", "hooks/parecer.py", "tests/catraca.py", "scripts/promover-homolog.py")


class PrPrevio(ComParecer):
    """FC-6 (E15, PP-5/C-1 e C-2): `pr --previo` só rebaixa o parecer ausente a aviso; desatualizado e reprovado seguem rc 1."""

    def setUp(self):
        super().setUp()
        self.gravar_pedido(conferidas=(self.c1,))

    def pr(self, *extra):
        r = subprocess.run([sys.executable, "-I", volta.FORGE_CHECK, "--raiz", str(self.repo), "pr", "x", "--ref", "melhoria/x", *extra],
                           env=dict(volta.ambiente_limpo(), HOME=str(self.home)), capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr

    def pareceres(self, review="aprovado", qa="aprovado", commit=None):
        c = commit or self.c1
        return self.commitar({"docs/reviews/x.md": PARECER.format(branch="melhoria/x", commit=c, parecer=review, data="2026-11-06"),
                              "docs/qa/x.md": QA.format(commit=c, parecer=qa)}, "pareceres")

    def test_ausente_com_previo_e_aviso_e_sem_previo_e_violacao(self):
        rc, saida, erro = self.pr("--previo")
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("aviso: docs/reviews: review: sem parecer para o pedido `x`", erro)
        self.assertNotIn("veredito: aprovado", saida)  # o prévio sem parecer não é veredito
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1, saida)
        self.assertIn("docs/reviews: review: sem parecer para o pedido `x`", saida)

    def test_ausente_com_base_como_o_pre_voo_chama(self):  # PP-5: `pr --ref <sha> --base origin/develop --previo -- <slug>`
        rc, saida, erro = self.pr("--base", "origin/develop", "--previo")
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("aviso: docs/qa: qa: sem parecer para o pedido `x`", erro)
        self.assertEqual(self.pr("--base", "origin/develop")[0], 1)

    def test_parecer_so_de_outra_branch_tambem_e_ausente(self):
        self.commitar({"docs/reviews/x.md": PARECER.format(branch="melhoria/y", commit=self.c1, parecer="aprovado", data="2026-11-06")})
        self.gravar_pedido(conferidas=(self.head(),))
        rc, saida, erro = self.pr("--previo")
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("aviso: docs/reviews: review: sem parecer da branch \"melhoria/x\" para o pedido `x`", erro)
        self.assertEqual(self.pr()[0], 1)

    def test_desatualizado_com_previo_e_rc_1(self):
        self.pareceres()
        c2 = self.commitar({"src/app.txt": "v3\n"}, "o head andou")
        self.gravar_pedido(conferidas=(c2,))
        rc, saida, erro = self.pr("--previo")
        self.assertEqual(rc, 1, saida + erro)
        self.assertIn("docs/reviews/x.md: commit: desatualizado", saida)

    def test_reprovado_com_previo_e_rc_1(self):
        self.pareceres(review="reprovado")
        rc, saida, erro = self.pr("--previo")
        self.assertEqual(rc, 1, saida + erro)
        self.assertIn("docs/reviews/x.md: parecer: o último parecer não é aprovado", saida)

    def test_aprovado_com_previo_passa(self):
        self.pareceres()
        rc, saida, erro = self.pr("--previo")
        self.assertEqual(rc, 0, saida + erro)
        self.assertNotIn("aviso: docs/", erro)

    def test_cmd_pr_como_o_hook_parecer_chama_nao_le_ambiente(self):  # PP-5/C-1: `parecer.py` chama `fc.cmd_pr(raiz, pedido, ref, base)`
        nomes = ("FORGE_PREVIO", "FORGE_CHECK_PREVIO", "PREVIO")
        antes = {n: os.environ.get(n) for n in nomes}
        self.addCleanup(lambda: [os.environ.pop(n, None) if v is None else os.environ.__setitem__(n, v) for n, v in antes.items()])
        os.environ.update({n: "1" for n in nomes})
        fc = volta.carregar_forge_check()  # depois do ambiente: nem o padrão do parâmetro nem o corpo o leem
        violacoes = fc.cmd_pr(str(self.repo), "x", "melhoria/x", None)
        self.assertIn("docs/reviews: review: sem parecer para o pedido `x` (R-REVIEW)", violacoes)

    def test_previo_nao_vaza_para_o_merge_o_hook_a_catraca_e_o_ci(self):  # PREVIO-vaza (PP-5/C-1)
        alvos = [volta.RAIZ / a for a in SEM_PREVIO] + sorted((volta.RAIZ / ".github" / "workflows").glob("*.yml"))
        self.assertGreaterEqual(len(alvos), len(SEM_PREVIO) + 1)
        for alvo in alvos:
            texto = alvo.read_text(encoding="utf-8")
            self.assertNotIn("--previo", texto, alvo)
            self.assertNotIn("previo=True", texto, alvo)


if __name__ == "__main__":
    unittest.main()
