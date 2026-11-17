"""v047 E1.185 (CONFERIDA-POR-BRANCH): a `entrega conferida <sha40>` de outro item do pedido que entrou na develop e chegou ao head
pelo merge da base não é o Desde da branch que trouxe a develop; a conferência dela não acusa arquivo do outro item."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_selo_e_entrega as se  # noqa: E402


class ConferidaDeOutroItem(se.Repositorio):
    """Item A (`melhoria/a`) conferido e integrado na develop; item B (`melhoria/x`) traz a develop e é conferido."""

    def item_a_conferido_e_integrado(self):
        self.git("switch", "-q", "-c", "melhoria/a", self.base)
        self.gravar("bin/a", "do item A\n")
        self.git("add", "bin/a")
        conferida = self.commit("feat: item A")
        with open(self.proj / "docs/pedidos/exemplo.md", "a", encoding="utf-8") as f:
            f.write(f"- 2026-01-01 10:00: entrega conferida {conferida}\n")
        self.gravar("bin/a", "do item A, mudado depois da conferida\n")  # A (ou outro item) volta ao arquivo antes de entrar na develop
        self.git("add", "bin/a")
        self.commit("fix: item A depois da conferida")
        self.git("switch", "-q", "develop")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge do item A", "melhoria/a")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        return conferida

    def entrega_de_b_com_a_develop(self):
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        self.entregar()
        conferida_a = self.item_a_conferido_e_integrado()
        self.git("fetch", "-q", "origin")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge da develop", "origin/develop")
        return conferida_a, self.git("rev-parse", "HEAD")

    def test_conferida_de_a_na_base_nao_e_o_desde_de_b(self):
        conferida_a, head = self.entrega_de_b_com_a_develop()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", "--sem-gravar")
        self.assertEqual(rc, 0, saida)
        self.assertNotIn('"bin/a"', saida)
        self.assertNotIn(conferida_a[:12], saida)
        self.assertIn("base: Base-sha do brief (sem conferida na branch)", saida)
        self.assertIn(f"commits: 5 em {self.base[:12]}..{head[:12]}", saida)  # o Desde é o Base-sha: f, A, A depois, 2 merges

    def test_forma_antiga_recusa_a_conferida_de_a_como_desde(self):
        """A regra é a mesma no `entrega --desde`: a conferida de A, já na develop, não é conferência anterior de B."""
        conferida_a, _ = self.entrega_de_b_com_a_develop()
        rc, saida = self.rodar("entrega", "exemplo", "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base,
                               "--etapa", "codigo", "--desde", conferida_a)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_desde_proposto_aos_briefs_e_o_base_sha(self):
        """O `desde_da_branch` (mensagem de entrega, `brief gerar --volta`, `brief selar`) propõe o Base-sha, não a conferida de A."""
        _, head = self.entrega_de_b_com_a_develop()
        base_ref = se.fc.ref_da_base(str(self.proj), "develop")
        self.assertEqual(se.fc.desde_da_branch(str(self.proj), self.pedido(), head, self.base, base_ref), (self.base, "base"))

    def test_conferida_da_propria_branch_segue_sendo_o_desde(self):
        """O controle: a conferida de B, fora da develop, continua valendo depois do merge da base."""
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        propria = self.entregar()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        self.item_a_conferido_e_integrado()
        self.git("fetch", "-q", "origin")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge da develop", "origin/develop")
        self.gravar("bin/app", "x\ny\nz\n")
        self.git("add", "bin/app")
        head = self.commit("feat: f de novo")
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", "--sem-gravar")
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"intervalo: {propria}..{head}", saida)  # o Desde segue sendo a conferida da própria branch


if __name__ == "__main__":
    unittest.main()
