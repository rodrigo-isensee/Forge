"""CONF-BASE-DONO: `forge-check entrega` aceita a base do delta fixada pelo dono (E1), isola o merge de integração (E2) e lê
pedido e briefs de uma raiz enquanto o git é de outra (`--raiz-pedidos`, E3). Repositório temporário."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ambiente_limpo, git  # noqa: E402
from test_volta_por_delta import Repositorio, SHA_FALSO  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


def linha_do_dono(sha):
    return f"- 2026-10-23 15:56: LACUNA R-PROVA (decisão B do dono): base do delta fixada pelo dono {sha}; implementação sem conferência formal\n"


class BaseDoDono(Repositorio):
    """E1: a forma é `base do delta fixada pelo dono <sha40>` numa linha do `## Histórico`."""

    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"a.txt": "1\n"}, "1a")
        self.c2 = self.commitar({"b.txt": "2\n"}, "2a")
        self.c3 = self.commitar({"c.txt": "3\n"}, "3a")

    def test_desde_aceita_a_base_fixada_pelo_dono_e_diz_de_onde_veio(self):
        self.gravar_pedido(extra=linha_do_dono(self.c2))
        rc, saida = self.entrega(desde=self.c2)
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.splitlines(), [f"intervalo: {self.c2}..{self.c3}",
                                              "base: fixada pelo dono (linha do Histórico)", 'escopo: confira "c.txt" +1 -0'])

    def test_sem_a_linha_do_dono_o_comportamento_e_o_de_hoje(self):
        self.gravar_pedido()
        rc, saida = self.entrega(desde=self.c2)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)
        self.assertNotIn("base:", saida)

    def test_a_base_do_dono_so_vale_no_historico_com_sha40_da_branch(self):
        casos = {"fora do Histórico": (dict(secao="Decisões", extra=linha_do_dono(self.c2)), self.c2),
                 "sha abreviado": (dict(extra=linha_do_dono(self.c2[:7])), self.c2),
                 "sha fora da branch": (dict(extra=linha_do_dono(SHA_FALSO)), SHA_FALSO),
                 "sem a palavra dono": (dict(extra=f"- 2026-10-23 15:56: base do delta fixada {self.c2}\n"), self.c2)}
        for nome, (kwargs, desde) in casos.items():
            with self.subTest(nome):
                self.gravar_pedido(**kwargs)
                rc, saida = self.entrega(desde=desde)
                self.assertEqual(rc, 1, saida)
                self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_vale_a_linha_mais_recente_entre_a_conferida_e_a_do_dono(self):
        self.gravar_pedido([self.c1], extra=linha_do_dono(self.c2))
        self.assertEqual(self.entrega(desde=self.c2)[0], 0)
        self.assertEqual(self.entrega(desde=self.c1)[0], 1)  # a do dono é a mais recente
        self.gravar_pedido(extra=linha_do_dono(self.c1) + f"- 2026-10-23 16:30: entrega conferida {self.c2}; delegado\n")
        rc, saida = self.entrega(desde=self.c2)
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("base:", saida)  # veio da conferida: a saída de hoje

    def test_a_base_do_dono_nao_vale_gravada_na_propria_entrega(self):
        self.gravar_pedido(extra=linha_do_dono(self.c2))
        self.commitar({"docs/pedidos/p1.md": "x\n"}, "mexe no pedido")
        rc, saida = self.entrega(desde=self.c2)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde gravado na própria entrega", saida)

    def test_a_base_do_dono_nao_vale_nas_etapas_de_branch_inteira(self):
        self.gravar_pedido(extra=linha_do_dono(self.c2))
        rc, saida = self.entrega(desde=self.c2, etapa="pr")
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde fora da etapa", saida)


class IntegracaoNaBranch(Repositorio):
    """E2: com o head um commit de integração, o escopo é o que difere dos dois pais."""

    def integrar(self, conflito=False):
        self.c1 = self.commitar({"a.txt": "1\n", "f.txt": "branch\n" if conflito else "0\n"}, "trabalho da branch")
        git("switch", "-q", "develop", cwd=self.repo)
        self.d1 = self.commitar({"d.txt": "d\n", "f.txt": "develop\n"} if conflito else {"d.txt": "d\n"}, "develop andou")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        if conflito:
            subprocess.run(["git", "-C", str(self.repo), "merge", "--no-edit", "develop"], env=ambiente_limpo(),
                           capture_output=True)  # sai com conflito em f.txt
            (self.repo / "f.txt").write_text("resolvido\n", encoding="utf-8")
            git("add", "f.txt", cwd=self.repo)
            git("commit", "-q", "--no-edit", cwd=self.repo)
        else:
            git("merge", "-q", "--no-edit", "develop", cwd=self.repo)
        self.m = self.head()

    def test_integracao_limpa_nao_tem_escopo_proprio(self):
        self.integrar()
        self.gravar_pedido([self.c1])
        rc, saida = self.entrega(desde=self.c1, etapa="review")  # na etapa codigo o intervalo sem arquivo segue pendente
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.splitlines(), [f"intervalo: {self.c1}..{self.m}",
                                              "escopo: integração da base (o que difere dos dois pais)",
                                              "escopo: sem commit (nada a conferir)"])

    def test_integracao_com_conflito_resolvido_so_mostra_o_arquivo_resolvido(self):
        self.integrar(conflito=True)
        self.gravar_pedido([self.c1])
        rc, saida = self.entrega(desde=self.c1)
        self.assertEqual(rc, 0, saida)
        self.assertIn('escopo: confira "f.txt"', saida)
        for fora in ("d.txt", "a.txt"):
            self.assertNotIn(fora, saida)

    def test_com_commit_proprio_depois_da_integracao_a_conferencia_e_a_de_hoje(self):
        self.integrar()
        c = self.commitar({"z.txt": "z\n"}, "depois da integração")
        self.gravar_pedido([self.c1])
        rc, saida = self.entrega(desde=self.c1)
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("integração da base", saida)
        self.assertIn('confira "z.txt"', saida)
        self.assertIn(f"intervalo: {self.c1}..{c}", saida)


class PedidoForaDoClone(Repositorio):
    """E3: `--raiz-pedidos <dir>`: pedido e briefs numa raiz, git em outra."""

    def setUp(self):
        super().setUp()
        self.fora = self.tmp / "fora"
        (self.fora / "docs" / "pedidos").mkdir(parents=True)
        (self.fora / "docs" / "briefs").mkdir(parents=True)
        self.c1 = self.commitar({"a.txt": "1\n"}, "1a")
        self.pedido = self.fora / "docs" / "pedidos" / "p1.md"
        self.gravar_pedido()

    def entrega_por_id(self, *extra):
        return self.check("entrega", "p1", "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base,
                          "--etapa", "codigo", *extra)

    def test_sem_a_opcao_o_pedido_so_pelo_id_nao_e_achado(self):
        rc, saida = self.entrega_por_id()
        self.assertEqual(rc, 2, saida)

    def test_com_a_opcao_o_pedido_vem_da_outra_raiz_e_o_git_do_clone(self):
        rc, saida = self.entrega_por_id("--raiz-pedidos", self.fora)
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"intervalo: {self.base}..{self.c1}", saida)
        self.assertIn('escopo: confira "a.txt" +1 -0', saida)
        self.assertIn("origem:", saida)

    def test_a_opcao_vale_antes_do_subcomando(self):
        rc, saida = self.check("--raiz-pedidos", self.fora, "entrega", "p1", "--branch", "melhoria/x", "--base", "develop",
                               "--base-sha", self.base, "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)

    def test_brief_gerar_le_o_pedido_da_outra_raiz(self):
        rc, saida = self.check("brief", "gerar", "--pedido", "p1", "--raiz-pedidos", self.fora, "--destino", "forge:tech-lead",
                               "--branch", "melhoria/x", "--base", "develop")
        self.assertEqual(rc, 0, saida)
        self.assertIn("Pedido: p1", saida)
        self.assertIn("Branch: melhoria/x   Base: develop", saida)  # sem origin no repositório, o Base-sha fica PREENCHER

    def test_o_brief_de_uniao_vem_da_outra_raiz(self):
        brief = self.fora / "docs" / "briefs" / "b1.md"
        brief.write_text(f"Agente destino: forge:tech-lead\nPedido: p1\nBranch: melhoria/x   Base: develop   Base-sha: {self.base}\n",
                         encoding="utf-8")
        rc, saida = self.entrega_por_id("--raiz-pedidos", self.fora, "--brief", "docs/briefs/b1.md")
        self.assertEqual(rc, 0, saida)
        self.assertIn("brief: docs/briefs/b1.md sha256 ", saida)


if __name__ == "__main__":
    unittest.main()
