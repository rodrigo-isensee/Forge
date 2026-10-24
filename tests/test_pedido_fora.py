"""FC-PEDIDO-FORA: o `forge-check` acha o pedido e o brief em `~/.forge-contrib` (E1) e o quadro só grava onde há KANBAN.md (E2)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import Raiz  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "brief"
PEDIDO = (FIXTURES / "pedido.md").read_text(encoding="utf-8")
BRIEF = (FIXTURES / "etapa-outro-papel.md").read_text(encoding="utf-8")
REGISTRAR = ["conferencia", "registrar", "--pedido", "p", "--brief", "p-dev-exemplo-1", "--modo", "brief",
             "--rodada", "1", "--resultado", "aprovado", "--merito", "—"]
MOVER = ["movimento", "K-1", "--de", "a", "--para", "b"]


class Fora(Raiz):
    """A raiz do projeto (self.tmp) não tem o pedido nem o brief; a raiz de brief falsa é HOME/.forge-contrib."""

    def setUp(self):
        super().setUp()
        self.fora = self.tmp / "home" / ".forge-contrib"
        (self.fora / "docs" / "pedidos").mkdir(parents=True)
        (self.fora / "docs" / "briefs").mkdir(parents=True)
        self.pedido = self.fora / "docs" / "pedidos" / "pedido-sintetico.md"
        self.pedido.write_text(PEDIDO, encoding="utf-8")
        self.brief = self.fora / "docs" / "briefs" / "pedido-sintetico-dev-exemplo-1.md"
        self.brief.write_text(BRIEF, encoding="utf-8")

    def test_pedido_e_brief_na_raiz_de_brief_sao_lidos_com_origem(self):
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", "pedido-sintetico")
        texto = "\n".join(saida)
        self.assertNotIn("não consegui ler", texto)
        self.assertIn(f"origem: {self.pedido.resolve()}", saida)
        self.assertIn(f"origem: {self.brief.resolve()}", saida)
        self.assertIn(rc, (0, 1), texto)  # a conferência de forma roda; origem nunca reprova

    def test_pedido_absoluto_com_arquivo_relativo(self):
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", str(self.pedido))
        self.assertNotIn("não consegui ler", "\n".join(saida))
        self.assertIn(f"origem: {self.brief.resolve()}", saida)

    def test_brief_gerar_acha_o_pedido_fora(self):
        rc, saida, _ = self.rodar("brief", "gerar", "--pedido", "pedido-sintetico", "--destino", "forge:dev-exemplo", "--cobre", "E1.1")
        self.assertEqual(rc, 0, saida)
        self.assertIn("Pedido: pedido-sintetico", saida)

    def test_entrega_acha_o_pedido_pelo_id(self):
        rc, saida, _ = self.rodar("entrega", "pedido-sintetico", "--branch", "melhoria/x", "--base", "develop", "--base-sha", "0" * 40, "--etapa", "codigo")
        texto = "\n".join(saida)
        self.assertNotIn("não consegui ler o pedido", texto)
        self.assertEqual(rc, 2, texto)  # chegou à conferência das refs, que não existem aqui

    def test_travessia_e_link_para_fora_sao_recusados(self):
        (self.fora / "docs" / "segredo.md").write_text(PEDIDO, encoding="utf-8")
        alvo = self.tmp / "alheio.md"
        alvo.write_text(PEDIDO, encoding="utf-8")
        (self.fora / "docs" / "pedidos" / "elo.md").symlink_to(alvo)
        for pedido in ("../segredo", "../../docs/segredo", "elo"):
            with self.subTest(pedido):
                rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", pedido)
                self.assertEqual(rc, 2, saida)
                self.assertFalse([l for l in saida if l.startswith("origem:")], saida)
        (self.fora / "docs" / "briefs" / "elo.md").symlink_to(alvo)
        (self.fora / "docs" / "outro.md").write_text(BRIEF, encoding="utf-8")
        for arquivo in ("docs/briefs/elo.md", "docs/outro.md", "../../x.md"):
            with self.subTest(arquivo):
                self.assertEqual(self.rodar("brief", arquivo, "--pedido", "pedido-sintetico")[0], 2)

    def test_mesmo_nome_nas_duas_raizes_a_raiz_do_repositorio_vence(self):
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        propria = self.tmp / "docs" / "pedidos" / "pedido-sintetico.md"
        propria.write_text(PEDIDO + "\nPropria.\n", encoding="utf-8")
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", "pedido-sintetico")
        self.assertNotIn(f"origem: {self.pedido.resolve()}", saida)
        self.assertNotIn(f"origem: {propria.resolve()}", saida)  # a da raiz é a conhecida: sem linha de origem


class QuadroSemKanban(Raiz):
    def arvore(self):
        return sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*"))

    def test_movimento_e_conferencia_registrar_recusam_sem_kanban_e_sem_criar_pasta(self):
        for args in (MOVER, REGISTRAR):
            with self.subTest(args[0]):
                antes = self.arvore()
                rc, saida, _ = self.rodar(*args)
                self.assertEqual(rc, 1, saida)
                self.assertIn("KANBAN.md", "\n".join(saida))
                self.assertIn("--raiz", "\n".join(saida))
                self.assertEqual(self.arvore(), antes)
                self.assertFalse((self.tmp / "docs" / "kanban").exists())

    def test_com_kanban_nada_muda(self):
        self.gravar("KANBAN.md", "# Quadro\n")
        self.assertEqual(self.rodar(*MOVER)[0], 0)
        self.assertEqual(self.rodar(*REGISTRAR)[0], 0)
        self.assertTrue((self.tmp / "docs" / "kanban" / "historico.md").is_file())
        self.assertTrue((self.tmp / "docs" / "kanban" / "conferencias.md").is_file())


if __name__ == "__main__":
    unittest.main()
