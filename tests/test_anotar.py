"""P4 (LOTE-FORGE-CHECK-0.28.0): decisão e hora gravadas por comando. `forge-check anotar` grava a linha do dono no pedido com a hora
do relógio; `brief gerar --retomada` avisa a decisão que cita o pedido e falta nele. Sem rede."""
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from apoio_jarvis import texto_do_jarvis  # noqa: E402

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
MARCA = f" · atributos: confere=mede; forge={fc.versao_da_propria_copia() or 'desconhecida'}"  # E8: a decisão leva --confere
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
            return fc.cmd_anotar(self.tmp, "exemplo", tipo, literal, contexto, confere="mede" if tipo == "decisao" else None)
        finally:
            fc.datetime = original

    def anotar_em(self, pedido):
        original = fc.datetime
        fc.datetime = RelogioFixo
        try:
            return fc.cmd_anotar(self.tmp, str(pedido), "decisao", "forjada", confere="mede")
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
        nova = 'DECISÃO DO DONO (2030-05-06 07:08): P1 do estudo → "B"' + MARCA
        self.assertIn('DECISÃO DO DONO (2026-01-01 10:00): "A".\n' + nova + "\n\n## Histórico", texto)
        self.assertTrue(fc.e_linha_de_decisao(nova))
        self.assertEqual(texto.replace(nova + "\n", ""), COM_SECAO)  # nenhuma linha existente muda
        self.assertEqual(fc.FRASES_DO_ANOTAR["decisao"], fc.FRASE_DO_DONO)

    def test_sem_a_secao_ela_nasce_antes_do_historico(self):
        self.com(SEM_SECAO)
        _, rc = self.anotar("decisao", "sim")
        self.assertEqual(rc, 0)
        texto = self.pedido.read_text(encoding="utf-8")
        self.assertIn('## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2030-05-06 07:08): "sim"' + MARCA + '\n\n## Histórico', texto)

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
        rc, saida, _ = self.rodar("anotar", "--pedido", alvos["docs/regras/R-X.md"], "--tipo", "decisao", "--confere", "mede", "--literal", "C")
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
        rc, saida, _ = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "C")
        self.assertEqual(rc, 0, saida)
        self.assertRegex(saida, r'^anotado: exemplo\.md: DECISÃO DO DONO \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}\): "C" · atributos: confere=mede; forge=\S+\n$')
        rc, _, _ = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "C", "--hora", "2020-01-01 00:00")
        self.assertEqual(rc, 2)

    def test_o_gerar_seguinte_cita_o_bloco_com_a_decisao_gravada(self):
        """P4 (0.43.1): o brief cita as decisões por referência; a decisão nova entra no hash do bloco que o gerar seguinte cita."""
        self.com(COM_SECAO)
        rc, antes, _ = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo")
        self.assertEqual(rc, 0, antes)
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "D", "--contexto", "item novo")
        rc, saida, _ = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo")
        self.assertEqual(rc, 0, saida)
        referencia = re.compile(r"^- decisões: pedido exemplo até ([0-9a-f]{64}) \((\d+) linhas", re.M)
        (hash_antes, n_antes), (hash_depois, n_depois) = referencia.search(antes).groups(), referencia.search(saida).groups()
        self.assertNotEqual(hash_antes, hash_depois)
        self.assertEqual(int(n_depois), int(n_antes) + 1)


BRIEF = """Pedido: {pedido}

## Decisões e restrições
- DECISÃO DO DONO (2026-01-01 10:00): "A".

### Restrições do time
- sem push.

## Pronto quando
"""


class Propagar(Base):
    """B15: `anotar --tipo decisao` lista os briefs em voo do pedido; com `--propagar`, grava o brief seguinte com a linha nova."""
    def brief(self, nome, pedido="exemplo", aprovado=True, texto=None):
        arq = self.tmp / "docs" / "briefs" / f"{nome}.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto or BRIEF.format(pedido=pedido), encoding="utf-8")
        if aprovado:
            arq.chmod(0o444)

    def conferencias(self, *linhas):
        arq = self.tmp / "docs" / "kanban" / "conferencias.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text("| data-hora | pedido | brief | modo | rodada | resultado |\n|---|---|---|---|---|---|\n"
                       + "".join(f"| 2026-01-01 10:00 | exemplo | {b} | {m} | 1 | {r} |\n" for b, m, r in linhas), encoding="utf-8")

    def anotar_p(self, tipo="decisao", propagar=False):
        original = fc.datetime
        fc.datetime = RelogioFixo
        try:
            return fc.cmd_anotar(self.tmp, "exemplo", tipo, "B", None, propagar, "mede" if tipo == "decisao" else None)
        finally:
            fc.datetime = original

    def cenario(self):
        self.com(COM_SECAO)
        self.brief("exemplo-dev-1")
        self.brief("exemplo-tech-lead-2", aprovado=False)  # aprovado só pela linha da conferência
        self.brief("exemplo-dev-3")  # entrega aprovada: fora
        self.brief("exemplo-qa-4")  # entrega reprovada: segue em voo
        self.brief("exemplo-dev-5", aprovado=False)  # não aprovado
        self.brief("exemplo-b-dev-1", pedido="exemplo-b")  # outro pedido com o mesmo prefixo
        self.brief("exemplo-notas", texto=BRIEF.format(pedido="exemplo"))
        (self.tmp / "docs" / "briefs" / "exemplo-dev-6.md").symlink_to(self.tmp / "docs" / "briefs" / "exemplo-dev-1.md")
        self.conferencias(("docs/briefs/exemplo-tech-lead-2.md", "brief", "aprovado"), ("exemplo-dev-3", "entrega", "cumpriu"),
                          ("docs/briefs/exemplo-qa-4.md", "entrega", "reprovado"), ("exemplo-dev-5", "brief", "reprovado"))

    def test_sem_propagar_lista_os_briefs_em_voo(self):
        self.cenario()
        linhas, rc = self.anotar_p()
        self.assertEqual(rc, 0, linhas)
        self.assertEqual(linhas[1:], ["decisao: em voo exemplo-dev-1.md", "decisao: em voo exemplo-qa-4.md",
                                      "decisao: em voo exemplo-tech-lead-2.md"])

    def test_com_propagar_grava_o_seguinte_e_o_anterior_fica(self):
        self.cenario()
        pasta = self.tmp / "docs" / "briefs"
        antes = {p.name: p.read_bytes() for p in pasta.iterdir()}
        linhas, rc = self.anotar_p(propagar=True)
        self.assertEqual(rc, 0, linhas)  # o novo vai antes da linha em branco e do `### `
        self.assertEqual([l.split()[:3] for l in linhas[1:]], [["brief", "gravado:", f"docs/briefs/exemplo-{n}.md"] for n in ("dev-7", "qa-5", "tech-lead-3")])
        for nome, novo in (("exemplo-dev-1", "exemplo-dev-7"), ("exemplo-qa-4", "exemplo-qa-5"), ("exemplo-tech-lead-2", "exemplo-tech-lead-3")):
            esperado = antes[f"{nome}.md"].decode().replace('"A".\n', '"A".\n- DECISÃO DO DONO (2030-05-06 07:08): "B"' + MARCA + '\n', 1)
            self.assertEqual((pasta / f"{novo}.md").read_text(encoding="utf-8"), esperado)
        for nome, conteudo in antes.items():
            self.assertEqual((pasta / nome).read_bytes(), conteudo)
        self.assertEqual((pasta / "exemplo-dev-1.md").stat().st_mode & 0o777, 0o444)

    def test_brief_sem_a_secao_de_decisoes_nao_grava(self):
        self.com(COM_SECAO)
        self.brief("exemplo-dev-1", texto="Pedido: exemplo\n\n## Objetivo\nX.\n")
        linhas, rc = self.anotar_p(propagar=True)
        self.assertEqual(rc, 1, linhas)
        self.assertIn("sem \"## Decisões e restrições\"", linhas[1])
        self.assertEqual(sorted(p.name for p in (self.tmp / "docs" / "briefs").iterdir()), ["exemplo-dev-1.md"])

    def test_falha_do_gravar_sai_com_erro_mesmo_com_o_seguinte_gravado(self):  # A1 do QA g4: rc do gravar não se perde
        self.com(COM_SECAO)
        self.brief("exemplo-dev-1")
        self.brief("exemplo-qa-1")
        real = fc.proximo_numero
        fc.proximo_numero = lambda pasta, prefixo: 1 if prefixo == "exemplo-dev" else real(pasta, prefixo)  # corrida: o seguinte já existe
        try:
            linhas, rc = self.anotar_p(propagar=True)
        finally:
            fc.proximo_numero = real
        self.assertEqual(rc, 2, linhas)
        self.assertIn("exemplo-dev-1.md já existe", linhas[1])
        self.assertTrue(linhas[2].startswith("brief gravado: docs/briefs/exemplo-qa-2.md "), linhas)

    def test_propagar_fora_da_decisao_e_recusado_e_pergunta_nao_lista(self):
        self.cenario()
        for tipo in ("historico", "pergunta"):
            with self.subTest(tipo=tipo):
                linhas, rc = self.anotar_p(tipo, propagar=True)
                self.assertEqual(rc, 2, linhas)
                self.assertEqual(self.pedido.read_text(encoding="utf-8"), COM_SECAO)
        linhas, rc = self.anotar_p("pergunta")
        self.assertEqual((rc, len(linhas)), (0, 1), linhas)
        rc, saida, _ = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "historico", "--literal", "x", "--propagar")
        self.assertEqual(rc, 2, saida)
        rc, saida, _ = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "C", "--propagar")
        self.assertEqual(rc, 0, saida)
        self.assertIn("brief gravado: docs/briefs/exemplo-dev-7.md ", saida)


class TextoDoJarvis(unittest.TestCase):
    def test_jarvis_manda_anotar_o_historico(self):  # LOTE E3: sem a frase, o Jarvis escrevia o Histórico à mão, com hora estimada
        texto = texto_do_jarvis(RAIZ)
        self.assertIn("forge-check anotar", texto)
        self.assertIn("Linhas do `## Histórico` e decisões do dono, por `forge-check anotar`", texto)


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
