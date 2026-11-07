"""VOLTAS-REVISOR-WT (E6a-1): o `forge-check pr` confere as linhas `parecer conferido <sha40>` do `## Histórico` (M1 no `pr`, M5 na
leitura, M8, T-1, T-2; testes t1, t10, t11, t14 e t19 das ameaças). Só acrescenta recusa. Repositório temporário."""
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


class PrLeParecerConferido(Repositorio):
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

    def novas(self, ref="melhoria/x", pedido="x"):
        rc, saida = self.check("pr", pedido, "--ref", ref)
        self.assertNotIn("Traceback", saida)
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


if __name__ == "__main__":
    unittest.main()
