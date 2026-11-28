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
                linhas = [l for l in saida.splitlines() if l.startswith("- envio: ")]
                self.assertEqual(len(linhas), 1, saida)  # sem a linha, falha por asserção (vermelho conclusivo na base)
                linha = linhas[0]
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


class ModeloDePedidoNoGerar(Base):
    """MODELO-PEDIDO-E-BRIEF, o resto no `brief gerar`: K-166 (uma etapa por delegação), K-252 (`.githooks/` como proposta) e K-156
    (o brief que grava parecer propõe o `forge-check pr`)."""

    def test_etapa_ja_conferida_recusa_a_delegacao_nova(self):
        saida, rc, erros = self.montar("codigo", "E1.1", "forge:dev-exemplo", conferidas={"E1.1"})
        self.assertEqual((saida, rc), (None, 1))
        self.assertEqual(len(erros), 1)
        self.assertTrue(erros[0].startswith("brief gerar: recusado: E1.1 já tem entrega conferida"), erros)
        self.assertIn("(K-166)", erros[0])
        self.assertIn("Cobre: E1.1", self.montar("codigo", "E1.1", "forge:dev-exemplo", conferidas={"E1.2"})[0])

    def test_etapa_conferida_le_o_historico_do_pedido(self):
        texto = PEDIDO + "\n## Histórico\n- 2026-01-01 10:00: nota\n"
        (self.tmp / "docs" / "pedidos" / "trilha.md").write_text(texto, encoding="utf-8")
        with mock.patch.object(fc, "etapas_conferidas", return_value=set()) as conferidas, redirect_stderr(io.StringIO()):
            fc.montar_brief(self.tmp, "trilha", "forge:dev-exemplo", None, "develop", etapa="codigo", cobre="E1.1")
        self.assertEqual(conferidas.call_args.args[2], ["- 2026-01-01 10:00: nota"])

    def test_githooks_no_escopo_da_etapa_vira_proposta(self):
        self.assertIn(fc.LINHA_DO_GITHOOKS + "\n", self.gerar("codigo", "E1.3", "forge:dev-exemplo"))
        self.assertNotIn(fc.LINHA_DO_GITHOOKS, self.gerar("codigo", "E1.1", "forge:dev-exemplo"))
        for trecho in ("é do usuário", "proposta", "não edite o arquivo"):
            self.assertIn(trecho, fc.LINHA_DO_GITHOOKS)

    def test_portao_propoe_o_pq_do_forge_check_pr(self):
        pq = "- PQ-N (cmd): `forge-check pr trilha --previo --base develop` · espera: rc=0, rodado depois do commit do parecer\n"
        for etapa in ("review", "seguranca", "qa"):
            with self.subTest(etapa):
                self.assertIn(pq, self.gerar(etapa, "E1.2", "forge:revisor-exemplo"))
        self.assertNotIn("`forge-check pr ", self.gerar("codigo", "E1.1", "forge:dev-exemplo"))

    def test_base_fora_da_forma_nao_vai_ao_pq(self):
        with mock.patch.object(fc, "e_o_forge", return_value=True), mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), \
                mock.patch.object(fc, "portao_na_branch", return_value=(None, None)), redirect_stderr(io.StringIO()):
            saida, rc, _ = fc.montar_brief(self.tmp, "trilha", "forge:revisor-exemplo", None, "a..b", etapa="review", cobre="E1.2")
        self.assertEqual(rc, 0)
        self.assertNotIn("`forge-check pr ", saida)


class DocsNoFluxoDeEntrega(Base):
    """FC-DOCS-CAMINHO: o PQ do portão confere só os documentos do diff (`--base`); a cópia do parecer de segurança fora da pasta
    acusa o `- Nenhum.` do ## Achados como a da pasta."""

    def test_pq_do_portao_passa_a_base_do_fluxo(self):
        self.assertIn("- PQ-N (cmd): `forge-check docs --base develop` · espera: rc=0\n", self.gerar("review", "E1.2", "forge:revisor-exemplo"))

    def test_base_fora_do_fluxo_fica_sem_a_opcao(self):
        with mock.patch.object(fc, "e_o_forge", return_value=True), mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), \
                mock.patch.object(fc, "portao_na_branch", return_value=(None, None)), redirect_stderr(io.StringIO()):
            saida, _, _ = fc.montar_brief(self.tmp, "trilha", "forge:revisor-exemplo", None, "outra", etapa="qa", cobre="E1.2")
        self.assertIn("- PQ-N (cmd): `forge-check docs` · espera: rc=0\n", saida)

    def test_copia_do_parecer_de_seguranca_acusa_o_nenhum(self):
        fora = Path(tempfile.mkdtemp(prefix="forge-trilha-fora-")).resolve()
        self.addCleanup(shutil.rmtree, fora, True)
        texto = ("---\ntipo: revisao-seguranca\ncontrato: 1\npedido: trilha\nbranch: melhoria/x\ncommit: abc1234\nparecer: aprovado\n"
                 "revisor: forge:security-engineer\ndata: 2026-11-21\n---\n# S\n\n## Achados\n- Nenhum.\n")
        (self.tmp / "docs" / "security").mkdir(parents=True)
        for arq in (self.tmp / "docs" / "security" / "trilha.md", fora / "copia.md"):
            arq.write_text(texto, encoding="utf-8")
            with self.subTest(arq.name), mock.patch.object(fc, "RAIZES_DE_BRIEF", ()), redirect_stderr(io.StringIO()):
                self.assertEqual(fc.cmd_docs(self.tmp, [str(arq)]), [
                    f'{arq}: achados: linha do bloco ## Achados fora do formato (uma linha, sem caractere de controle; sem achados, '
                    'omita o bloco): "- Nenhum." (R-SEGURANCA)'])


if __name__ == "__main__":
    unittest.main()
