"""VOLTAS-REVISOR-WT (E6a-1): o `forge-check pr` confere as linhas `parecer conferido <sha40>` do `## Histórico` (M1 no `pr`, M5 na
leitura, M8, T-1, T-2; testes t1, t10, t11, t14 e t19 das ameaças). Só acrescenta recusa. E6a-2: `entrega --branch parecer/*` (M3, M5,
M9; t4 a t8, t15 e o caso 11). E6a-3: o `entrega` confere os merges do intervalo (M4, M2, C-11, M9 no merge; t1, t2, t9, t12,
t20 e o caso 12). Repositório temporário."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import git  # noqa: E402
from test_volta_por_delta import Repositorio, SHA_FALSO  # noqa: E402
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
        self.merge(p1, sem_commit=True)
        (self.repo / "src" / "app.txt").unlink()  # a remoção também é arquivo trazido pelo merge
        self.commitar({"docs/reviews/x.md": "outro\n", "src/b.txt": "b\n"}, "merge")
        m = self.head()[:7]
        self.assertEqual(self.foras(), (1, [f'escopo: fora (o merge {m} traz "docs/reviews/x.md" fora dos pareceres conferidos)',
                                            f'escopo: fora (o merge {m} traz "src/app.txt" fora dos pareceres conferidos)',
                                            f'escopo: fora (o merge {m} traz "src/b.txt" fora dos pareceres conferidos)',
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


if __name__ == "__main__":
    unittest.main()
