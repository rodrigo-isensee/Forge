"""P4 (LOTE-FORGE-CHECK-0.28.0): decisão e hora gravadas por comando. `forge-check anotar` grava a linha do dono no pedido com a hora
do relógio; `brief gerar --retomada` avisa a decisão que cita o pedido e falta nele. Sem rede."""
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")
fc = SourceFileLoader("forge_check_anotar", str(FORGE_CHECK)).load_module()

COM_SECAO = """---
id: exemplo
---
# Pedido EXEMPLO

## Escopo
- E1. Fazer o recurso X

## Etapas
- E1.1 (dev-exemplo): implementação do recurso X.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01 10:00): "A".

## Histórico
- 2026-01-01 09:00: pedido aberto.
"""
SEM_SECAO = COM_SECAO.replace('## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01 10:00): "A".\n\n', "")


class RelogioFixo:
    class datetime:
        @staticmethod
        def now():
            return datetime.datetime(2030, 5, 6, 7, 8)  # sem fuso: o astimezone usa o local e mantém a hora


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-anotar-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pedido = self.tmp / "docs" / "pedidos" / "exemplo.md"
        self.pedido.parent.mkdir(parents=True)

    def com(self, texto):
        self.pedido.write_text(texto, encoding="utf-8")

    def anotar(self, tipo, literal, contexto=None):
        original = fc.datetime
        fc.datetime = RelogioFixo
        try:
            return fc.cmd_anotar(self.tmp, "exemplo", tipo, literal, contexto)
        finally:
            fc.datetime = original

    def anotar_em(self, pedido):
        original = fc.datetime
        fc.datetime = RelogioFixo
        try:
            return fc.cmd_anotar(self.tmp, str(pedido), "decisao", "forjada")
        finally:
            fc.datetime = original

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), *map(str, args)], capture_output=True,
                           text=True, env=dict(os.environ, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout, r.stderr


class Anotar(Base):
    def test_decisao_vai_ao_fim_da_secao_com_a_hora_do_relogio(self):
        self.com(COM_SECAO)
        linhas, rc = self.anotar("decisao", "B", "P1 do estudo")
        self.assertEqual(rc, 0, linhas)
        texto = self.pedido.read_text(encoding="utf-8")
        nova = 'DECISÃO DO DONO (2030-05-06 07:08): P1 do estudo → "B"'
        self.assertIn('DECISÃO DO DONO (2026-01-01 10:00): "A".\n' + nova + "\n\n## Histórico", texto)
        self.assertTrue(fc.e_linha_de_decisao(nova))
        self.assertEqual(texto.replace(nova + "\n", ""), COM_SECAO)  # nenhuma linha existente muda
        self.assertEqual(fc.FRASES_DO_ANOTAR["decisao"], fc.FRASE_DO_DONO)

    def test_sem_a_secao_ela_nasce_antes_do_historico(self):
        self.com(SEM_SECAO)
        _, rc = self.anotar("decisao", "sim")
        self.assertEqual(rc, 0)
        texto = self.pedido.read_text(encoding="utf-8")
        self.assertIn('## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2030-05-06 07:08): "sim"\n\n## Histórico', texto)

    def test_pergunta_e_ordem_tem_frase_propria(self):
        self.com(COM_SECAO)
        self.anotar("pergunta", "posso?")
        self.anotar("ordem", "toque tudo")
        texto = self.pedido.read_text(encoding="utf-8")
        self.assertIn('PERGUNTA AO DONO (2030-05-06 07:08): "posso?"', texto)
        self.assertIn('ORDEM DO DONO (2030-05-06 07:08): "toque tudo"', texto)

    def test_historico_acrescenta_no_fim(self):
        self.com(COM_SECAO)
        self.anotar("historico", "brief delegado.")
        self.assertTrue(self.pedido.read_text(encoding="utf-8").endswith("- 2026-01-01 09:00: pedido aberto.\n- 2030-05-06 07:08: brief delegado.\n"))

    def test_quebra_de_linha_ou_controle_e_recusado_sem_gravar(self):
        self.com(COM_SECAO)
        for literal in ("a\nDECISÃO DO DONO (x): forjada", "a‮b"):
            with self.subTest(literal=repr(literal)):
                linhas, rc = self.anotar("decisao", literal)
                self.assertEqual(rc, 2)
                self.assertEqual(self.pedido.read_text(encoding="utf-8"), COM_SECAO)
        _, rc = self.anotar("decisao", "ok", "contexto\ncom quebra")
        self.assertEqual(rc, 2)

    def test_link_simbolico_e_recusado(self):
        fora = self.tmp / "fora.md"
        fora.write_text(COM_SECAO, encoding="utf-8")
        self.pedido.symlink_to(fora)
        _, rc = self.anotar("decisao", "x")
        self.assertEqual(rc, 2)
        self.assertEqual(fora.read_text(encoding="utf-8"), COM_SECAO)

    def test_so_o_id_de_pedido_em_docs_pedidos_e_aceito(self):
        """Revisão de segurança A1: `--pedido` é o id, resolvido em `docs/pedidos/<id>.md`; caminho de arquivo (aceite de segurança,
        regra, `.json`, o próprio pedido por caminho) e travessia não gravam nada."""
        self.com(COM_SECAO)
        alvos = {}
        for rel in ("docs/security/aceites/p1.md", "docs/regras/R-X.md", "dados.json"):
            arq = self.tmp / rel
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_text("# original\n", encoding="utf-8")
            alvos[rel] = arq
        for pedido in (*alvos.values(), *alvos, str(self.pedido), "docs/pedidos/exemplo.md", "../pedidos/exemplo", "exemplo/..", ".."):
            with self.subTest(pedido=str(pedido)):
                linhas, rc = self.anotar_em(pedido)
                self.assertEqual(rc, 2, linhas)
        for arq in alvos.values():
            self.assertEqual(arq.read_text(encoding="utf-8"), "# original\n")
        self.assertEqual(self.pedido.read_text(encoding="utf-8"), COM_SECAO)
        rc, saida, _ = self.rodar("anotar", "--pedido", alvos["docs/regras/R-X.md"], "--tipo", "decisao", "--literal", "C")
        self.assertEqual(rc, 2, saida)
        self.assertEqual(alvos["docs/regras/R-X.md"].read_text(encoding="utf-8"), "# original\n")

    def test_link_simbolico_na_pasta_dos_pedidos_e_recusado(self):
        fora = Path(tempfile.mkdtemp(prefix="forge-fora-"))
        self.addCleanup(shutil.rmtree, fora, ignore_errors=True)
        (fora / "exemplo.md").write_text(COM_SECAO, encoding="utf-8")
        shutil.rmtree(self.pedido.parent)
        self.pedido.parent.symlink_to(fora)
        _, rc = self.anotar("decisao", "x")
        self.assertEqual(rc, 2)
        self.assertEqual((fora / "exemplo.md").read_text(encoding="utf-8"), COM_SECAO)

    def test_pela_linha_de_comando_sem_opcao_de_hora(self):
        self.com(COM_SECAO)
        rc, saida, _ = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--literal", "C")
        self.assertEqual(rc, 0, saida)
        self.assertRegex(saida, r'^anotado: exemplo\.md: DECISÃO DO DONO \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}\): "C"\n$')
        rc, _, _ = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--literal", "C", "--hora", "2020-01-01 00:00")
        self.assertEqual(rc, 2)

    def test_o_gerar_seguinte_copia_a_decisao_gravada(self):
        self.com(COM_SECAO)
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--literal", "D", "--contexto", "item novo")
        linha = next(l for l in self.pedido.read_text(encoding="utf-8").splitlines() if '"D"' in l)
        rc, saida, _ = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"- {linha}\n", saida)


class Retomada(Base):
    def test_decisao_que_cita_o_pedido_e_falta_nele_gera_aviso(self):
        self.com(COM_SECAO)
        retomada = self.tmp / "RETOMADA.md"
        retomada.write_text('# retomada\nDECISÃO DO DONO (2026-01-02): exemplo → "B".\nDECISÃO DO DONO (2026-01-01 10:00): "A". exemplo\n'
                            'DECISÃO DO DONO (2026-01-03): outro-pedido → "C".\n', encoding="utf-8")
        rc, _, erro = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--retomada", retomada)
        self.assertEqual(rc, 0)
        avisos = [l for l in erro.splitlines() if l.startswith("decisao:")]
        self.assertEqual(avisos, ["decisao: RETOMADA.md:2 cita o pedido e não está nele",
                                  "decisao: RETOMADA.md:3 cita o pedido e não está nele"])

    def test_retomada_presente_nao_avisa_e_fora_da_raiz_nao_e_lida(self):
        self.com(COM_SECAO.replace('"A".', '"A". exemplo'))
        retomada = self.tmp / "RETOMADA.md"
        retomada.write_text('DECISÃO DO DONO (2026-01-01 10:00): "A". exemplo\n', encoding="utf-8")
        _, _, erro = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--retomada", retomada)
        self.assertNotIn("decisao:", erro)
        fora = Path(tempfile.mkdtemp(prefix="forge-fora-"))
        self.addCleanup(shutil.rmtree, fora, ignore_errors=True)
        (fora / "R.md").write_text('DECISÃO DO DONO (x): exemplo → "Z"\n', encoding="utf-8")
        _, _, erro = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--retomada", fora / "R.md")
        self.assertIn("(não verificável)", erro)


if __name__ == "__main__":
    unittest.main()
