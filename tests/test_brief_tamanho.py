"""v0474 E3.48: o `brief gerar` num pedido grande fica abaixo do teto de 10.000 caracteres do R-BRIEF (o Fora do escopo vai só pelos
ids), manda o `forge-check proximo` só da etapa do Cobre (o pedido inteiro levava minutos) e o brief de portão traz o formato do
bloco `## Achados` do `_modelo.md`. Sem rede: o `gh`, a branch e o pre-push não rodam; a decisão é lida no brief montado."""
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_pre_envio_brief import fc  # noqa: E402  (o bin/forge-check carregado como módulo)

TETO_DO_BRIEF = 10000


def pedido(n_etapas):
    """`n_etapas` etapas em 6 grupos; a E1.1 do dev-exemplo (código), a E1.2 do revisor-exemplo, as outras de outros papéis."""
    etapas = ["- E1.1 (dev-exemplo): o recurso X em bin/forge-x e tests/test_x.py.", "- E1.2 (revisor-exemplo): review do recurso X."]
    etapas += [f"- E{g}.{i} (papel-{g}): parte {i} do grupo {g} do recurso X, com os testes e a documentação afetada pela mudança."
               for g in range(1, 7) for i in range(1, 101) if (g, i) not in ((1, 1), (1, 2))][:n_etapas - 2]
    return ("---\nid: grande\n---\n# Pedido GRANDE\n\n## Escopo\n- E1. Fazer o recurso X · `confirmado`\n\n## Etapas\n"
            + "\n".join(etapas) + '\n\n## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01): "A".\n')


class BriefDePedidoGrande(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-brief-tamanho-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        (self.tmp / "docs" / "pedidos" / "grande.md").write_text(pedido(600), encoding="utf-8")

    def gerar(self, etapa, cobre, destino):
        with mock.patch.object(fc, "e_o_forge", return_value=True), mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), \
                mock.patch.object(fc, "estado_da_branch", return_value=([], [])), mock.patch.object(fc, "pr_da_branch", return_value=({}, None)), \
                mock.patch.object(fc, "portao_na_branch", return_value=(None, None)), \
                mock.patch.object(fc, "base_sha_real", return_value="b" * 40), redirect_stderr(io.StringIO()):
            saida, rc, erros = fc.montar_brief(self.tmp, "grande", destino, "melhoria/x", "develop", etapa=etapa, cobre=cobre)
        self.assertEqual(rc, 0, erros)
        return saida

    def test_pedido_de_600_etapas_fica_abaixo_do_teto(self):
        self.assertEqual(len(fc.ler_pedido_brief(pedido(600))["etapas"]), 600)
        for etapa, cobre, destino in (("codigo", "E1.1", "forge:dev-exemplo"), ("review", "E1.2", "forge:revisor-exemplo")):
            with self.subTest(etapa):
                saida = self.gerar(etapa, cobre, destino)
                self.assertLess(len(saida), TETO_DO_BRIEF)
                fora = saida.split("## Fora do escopo", 1)[1].split("\n## ", 1)[0]
                self.assertEqual(fora.count(" · outras delegações\n"), 15)  # 599 ids, 40 por linha
                self.assertNotIn("parte 1 do grupo", fora)

    def test_proximo_so_da_etapa_do_cobre(self):
        saida = self.gerar("codigo", "E1.1", "forge:dev-exemplo")
        self.assertIn("- comece por `forge-check proximo grande --etapa E1.1` (passo, dono, bloqueios)", saida)

    def test_portao_traz_o_formato_dos_achados_e_o_autor_nao(self):
        saida = self.gerar("review", "E1.2", "forge:revisor-exemplo")
        self.assertIn(fc.LINHA_DOS_ACHADOS + "\n", saida)
        for trecho in ("- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>", "até 300 caracteres", '"nenhum"', '"informativo"'):
            self.assertIn(trecho, fc.LINHA_DOS_ACHADOS)
        self.assertNotIn(fc.LINHA_DOS_ACHADOS, self.gerar("codigo", "E1.1", "forge:dev-exemplo"))


if __name__ == "__main__":
    unittest.main()
