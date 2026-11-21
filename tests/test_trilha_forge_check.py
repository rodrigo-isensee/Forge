"""v0478 E91.1, trilha do bin/forge-check: BRIEF-PORTAO-REBASE (o brief de portão manda `git pull --rebase` e traz o `pedido:` do
parecer), o resto do MODELO-PEDIDO-E-BRIEF no `brief gerar` e FC-DOCS-CAMINHO. Sem rede: o `gh`, a branch e o pre-push não rodam;
a decisão é lida no brief montado."""
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

PEDIDO = ("---\nid: trilha\n---\n# Pedido TRILHA\n\n## Escopo\n- E1. Fazer o recurso X · `confirmado`\n\n## Etapas\n"
          "- E1.1 (dev-exemplo): o recurso X em bin/forge-x e tests/test_x.py.\n- E1.2 (revisor-exemplo): review do recurso X.\n"
          "- E1.3 (dev-exemplo): a proposta do gancho em .githooks/pre-push.\n"
          '\n## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01): "A".\n')


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-trilha-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        (self.tmp / "docs" / "pedidos" / "trilha.md").write_text(PEDIDO, encoding="utf-8")

    def montar(self, etapa, cobre, destino, branch="melhoria/x", conferidas=frozenset()):
        with mock.patch.object(fc, "e_o_forge", return_value=True), mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), \
                mock.patch.object(fc, "estado_da_branch", return_value=([], [])), mock.patch.object(fc, "pr_da_branch", return_value=({}, None)), \
                mock.patch.object(fc, "portao_na_branch", return_value=(None, None)), \
                mock.patch.object(fc, "etapas_conferidas", return_value=set(conferidas)), \
                mock.patch.object(fc, "base_sha_real", return_value="b" * 40), redirect_stderr(io.StringIO()):
            return fc.montar_brief(self.tmp, "trilha", destino, branch, "develop", etapa=etapa, cobre=cobre)

    def gerar(self, etapa, cobre, destino, branch="melhoria/x"):
        saida, rc, erros = self.montar(etapa, cobre, destino, branch)
        self.assertEqual(rc, 0, erros)
        return saida


class EnvioDoParecer(Base):
    """BRIEF-PORTAO-REBASE: o portão envia por `git pull --rebase` (o papel e o pre-push), nunca por merge entre pareceres."""

    def test_portao_manda_rebase_e_traz_o_id_do_pedido(self):
        for etapa in ("review", "seguranca", "qa"):
            with self.subTest(etapa):
                saida = self.gerar(etapa, "E1.2", "forge:revisor-exemplo")
                linha = next(l for l in saida.splitlines() if l.startswith("- envio: "))
                self.assertIn("`pedido: trilha`", linha)
                self.assertIn("`git push origin melhoria/x`", linha)
                self.assertIn("`git pull --rebase`", linha)
                self.assertIn("nunca merge nem `--force`", linha)
                self.assertNotIn("traga por merge", saida)

    def test_autor_e_portao_sem_branch_nao_ganham_a_linha(self):
        self.assertNotIn("- envio: ", self.gerar("codigo", "E1.1", "forge:dev-exemplo"))
        self.assertNotIn("- envio: ", self.gerar("review", "E1.2", "forge:revisor-exemplo", branch=None))

    def test_branch_fora_da_forma_nao_vai_ao_comando(self):  # G-5: o envio é um comando que o portão copia
        self.assertNotIn("- envio: ", self.gerar("review", "E1.2", "forge:revisor-exemplo", branch="melhoria/x;id"))


if __name__ == "__main__":
    unittest.main()
