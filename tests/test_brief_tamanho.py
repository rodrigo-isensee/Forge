"""v0474 E3.48: o `brief gerar` num pedido grande fica abaixo do teto de 10.000 caracteres do R-BRIEF (o Fora do escopo vai só pelos
ids), manda o `forge-check proximo` só da etapa do Cobre (o pedido inteiro levava minutos) e o brief de portão traz o formato do
bloco `## Achados` do `_modelo.md`. Sem rede: o `gh`, a branch e o pre-push não rodam; a decisão é lida no brief montado."""
import hashlib
import io
import os
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


# PEDIDO-ARQUIVA-SOZINHO (ordem do dono 24/11): o pedido que cresce até o brief gerado passar do teto arquiva sozinho, na margem de
# 80% do teto, as etapas fechadas (entrega conferida, parecer aprovado ou `entregue`) em docs/pedidos/arquivo/<id>.md; o brief volta
# para baixo do teto, e a entrega conferida, os selos e os `parecer conferido` que o `pr` lê seguem no `## Histórico`. De ponta a
# ponta: `python3 -I`, ambiente limpo, `gh` falso (o `ComRepositorio` de test_forge_tamanho).
from test_forge_tamanho import ComRepositorio  # noqa: E402
from test_selo_e_entrega import fc as fcs  # noqa: E402

ITENS, POR_ITEM = 20, 60  # 19 itens fechados de 60 etapas e o E20 aberto: o Fora do escopo sozinho passa do teto


def pedido_que_cresce(historico):
    escopo = "".join(f"- E{n}. Item {n} · `confirmado`\n" for n in range(1, ITENS + 1))
    etapas = "".join(f"- E{n}.{m} ({'node-backend' if m % 2 else 'tech-lead'}): etapa {m} do item {n}\n"
                     for n in range(1, ITENS) for m in range(1, POR_ITEM + 1))
    etapas += "- E20.1 (node-backend): a etapa aberta\n- E20.2 (tech-lead): review da etapa aberta\n"
    return (f"---\nid: exemplo\n---\n# Pedido EXEMPLO\n\n## Escopo\n{escopo}\n## Etapas\n{etapas}\n"
            "## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01 10:00): \"regra geral A\".\n\n"
            f"## Histórico\n- 2026-01-01 09:00: aberto\n{historico}")


class ArquivaSozinho(ComRepositorio):
    def gerar(self):
        return self.rodar3("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:node-backend", "--cobre", "E20.1",
                           "--etapa", "codigo")

    def caminho(self):
        return self.proj / "docs" / "pedidos" / "exemplo.md"

    def arquivo(self):
        return (self.proj / "docs" / "pedidos" / "arquivo" / "exemplo.md").read_text(encoding="utf-8")

    def historico(self):
        return fcs.secoes_por(self.pedido(), fcs.CABECALHO_PEDIDO)["Histórico"]

    def fechamentos(self):
        """E1.1 pela entrega conferida do brief selado; E1.2 e E2.* por parecer aprovado; o resto por `entregue`; e um parecer conferido."""
        brief = self.gravar("docs/briefs/exemplo-node-backend-1.md", "Agente destino: forge:node-backend\nPedido: exemplo\nTipo: codigo\n"
                            f"Branch: melhoria/x   Base: develop   Base-sha: {self.base}\nEtapa: codigo   Cobre: E1.1\n\n## Entregar\n- x (E1.1)\n")
        self.gravar("docs/reviews/exemplo.md", "---\ntipo: review\nbranch: melhoria/x\n---\nparecer\n")
        self.git("add", "docs/reviews/exemplo.md")
        sha = self.commit("docs(review): parecer")
        selo = hashlib.sha256(brief.read_bytes()).hexdigest()
        linhas = [f"- 2026-01-01 09:01: brief selado docs/briefs/exemplo-node-backend-1.md {selo}\n",
                  f"- 2026-01-01 09:02: entrega conferida {sha}\n",
                  "- 2026-01-01 09:03: docs/reviews/exemplo.md=aprovado (E1.2) conferido pelo Jarvis\n",
                  f"- 2026-01-01 09:03: parecer conferido {sha}\n",
                  *(f"- 2026-01-01 09:04: docs/reviews/exemplo.md=aprovado por delta (E2.{m}, head abc)\n" for m in range(1, POR_ITEM + 1))]
        linhas += [f"- 2026-01-01 09:05: E{n}.{m} entregue\n" for n in range(3, ITENS) for m in range(1, POR_ITEM + 1)]
        linhas += [f"- 2026-01-01 09:05: E1.{m} entregue\n" for m in range(3, POR_ITEM + 1)]
        return "".join(linhas), sha

    def test_sem_etapa_fechada_o_brief_passa_do_teto_e_avisa(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce(""))
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertGreater(len(saida), TETO_DO_BRIEF)
        self.assertIn(f"brief gerar: aviso: o brief tem {len(saida)} caracteres, perto do teto de {TETO_DO_BRIEF}", erro)
        self.assertNotIn("arquivadas", erro)
        self.assertFalse((self.proj / "docs" / "pedidos" / "arquivo").exists())

    def test_arquiva_as_fechadas_e_o_brief_fica_abaixo_do_teto(self):
        historico, sha = self.fechamentos()
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce(historico))
        antes = self.historico()
        conferidas = fcs.etapas_conferidas(self.proj, self.caminho(), antes)
        pareceres = fcs.ultimos_do_historico(self.proj, self.pedido(), "melhoria/x", "HEAD")
        self.assertIn("E1.1", conferidas)
        self.assertTrue(pareceres[0])
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        fechadas = (ITENS - 1) * POR_ITEM
        self.assertIn(f"brief gerar: {fechadas} etapas fechadas arquivadas em docs/pedidos/arquivo/exemplo.md", erro)
        self.assertLess(len(saida), TETO_DO_BRIEF * 0.8)
        self.assertNotIn("caracteres, perto", erro)
        fora = saida.split("## Fora do escopo", 1)[1].split("\n## ", 1)[0]
        self.assertIn("E20.2", fora)
        self.assertNotIn("E1.2,", fora)
        texto = self.pedido()
        dados = fcs.ler_pedido_brief(texto)
        self.assertEqual(list(dados["etapas"]), ["E20.1", "E20.2"])
        self.assertEqual(len(dados["arquivadas"]), fechadas)
        self.assertLess(texto.index("\n## Etapas\n"), texto.index("\n## Etapas arquivadas\n"))
        self.assertLess(texto.index("\n## Etapas arquivadas\n"), texto.index("\n## Decisões"))
        self.assertIn("- E1.1 (node-backend): etapa 1 do item 1\n", self.arquivo())
        self.assertEqual(self.arquivo().count("\n- E"), fechadas)
        # o que a entrega conferida, o selo e o `pr` leem não mudou
        self.assertEqual(self.historico(), antes)
        self.assertIn("DECISÃO DO DONO (2026-01-01 10:00)", texto)
        self.assertEqual(fcs.etapas_conferidas(self.proj, self.caminho(), self.historico()), conferidas)
        self.assertIn(sha, fcs.entregas_conferidas(texto))
        self.assertEqual(fcs.ultimos_do_historico(self.proj, texto, "melhoria/x", "HEAD"), pareceres)

    def test_brief_antigo_cita_a_etapa_arquivada_e_o_corte_aceita_o_item_arquivado(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce(self.fechamentos()[0]))
        self.assertEqual(self.gerar()[0], 0)
        dados = fcs.ler_pedido_brief(self.pedido())
        citacoes = fcs.conferir_citacoes(self.proj, "", {"Entregar": ["- x (E1.1)"], "Fora do escopo": []}, dados)
        self.assertFalse([l for l, reprova in citacoes if reprova], citacoes)
        corte = fcs.conferir_corte({"Entregar": ["- a (E20.1)"], "Fora do escopo": ["- E20.2 · outras delegações"]}, dados,
                                   "forge:node-backend", "E20.1")
        self.assertFalse([l for l, reprova in corte if reprova], corte)
        self.assertIn(("corte: ok \"E1\" com as etapas arquivadas (PEDIDO-ARQUIVA-SOZINHO)", False), corte)
        self.assertIsNone(fcs.recusa_do_apontador(self.proj, "exemplo", self.pedido(), "E1.1"))

    def test_etapa_de_varias_linhas_fica_no_pedido(self):
        texto = pedido_que_cresce(self.fechamentos()[0]).replace("- E3.1 (node-backend): etapa 1 do item 3\n",
                                                                 "- E3.1 (node-backend): etapa 1 do item 3\n  continuação da etapa\n")
        self.gravar("docs/pedidos/exemplo.md", texto)
        self.assertEqual(self.gerar()[0], 0)
        self.assertEqual(set(fcs.ler_pedido_brief(self.pedido())["etapas"]), {"E3.1", "E20.1", "E20.2"})

    def test_segunda_rodada_acrescenta_ao_arquivo_e_a_secao(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce(self.fechamentos()[0]))
        self.assertEqual(self.gerar()[0], 0)
        texto = self.pedido().replace("- E20.2 (tech-lead): review da etapa aberta\n",
                                      "- E20.2 (tech-lead): review da etapa aberta\n- E20.3 (tech-lead): outra\n")
        self.caminho().write_text(texto + "- 2026-01-01 09:09: E20.2 entregue\n", encoding="utf-8")
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 1)
        dados = fcs.ler_pedido_brief(self.pedido())
        self.assertEqual(self.pedido().count("## Etapas arquivadas"), 1)
        self.assertIn("E20.2", dados["arquivadas"])
        self.assertEqual(list(dados["etapas"]), ["E20.1", "E20.3"])
        self.assertEqual(self.arquivo().count("# Arquivo do pedido"), 1)
        self.assertTrue(self.arquivo().endswith("- E20.2 (tech-lead): review da etapa aberta\n"))

    def test_brief_curto_nao_arquiva(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce("- 2026-01-01 09:05: E20.2 entregue\n").split("- E1.1 (")[0]
                    + "- E20.1 (node-backend): a etapa aberta\n- E20.2 (tech-lead): review\n\n## Histórico\n- 2026-01-01 09:05: E20.2 entregue\n")
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertLess(len(saida), TETO_DO_BRIEF * 0.8)
        self.assertNotIn("arquivadas", erro)
        self.assertIn("- E20.2 (tech-lead): review\n", self.pedido())
        self.assertFalse((self.proj / "docs" / "pedidos" / "arquivo").exists())

    def test_so_fechada_de_varias_linhas_nao_cria_o_arquivo(self):
        texto = pedido_que_cresce("- 2026-01-01 09:05: E3.1 entregue\n").replace(
            "- E3.1 (node-backend): etapa 1 do item 3\n", "- E3.1 (node-backend): etapa 1 do item 3\n  continuação da etapa\n")
        self.gravar("docs/pedidos/exemplo.md", texto)
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 0)
        self.assertEqual(self.pedido(), texto)
        self.assertFalse((self.proj / "docs" / "pedidos" / "arquivo").exists())

    def test_so_o_bloco_de_etapas_muda(self):
        nota = "- E1.3 (tech-lead): suposição que cita a etapa com a forma de etapa\n"
        texto = pedido_que_cresce(self.fechamentos()[0]).replace("## Decisões do usuário", f"## Suposições\n{nota}\n## Decisões do usuário")
        self.gravar("docs/pedidos/exemplo.md", texto)
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], (ITENS - 1) * POR_ITEM)
        self.assertIn(f"## Suposições\n{nota}", self.pedido())
        self.assertEqual(self.arquivo().count("- E1.3 ("), 1)

    def test_cabecalho_de_outro_nivel_nao_arquiva(self):
        texto = pedido_que_cresce(self.fechamentos()[0]).replace("## Etapas\n", "### Etapas\n")
        self.gravar("docs/pedidos/exemplo.md", texto)
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 0)
        self.assertEqual(self.pedido(), texto)

    def test_sem_fechada_nada_muda(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce(""))
        antes = self.pedido()
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 0)
        self.assertEqual(self.pedido(), antes)

    # Volta do #874 (A1 do review, do QA e da segurança): só a etapa que a própria linha fecha conta como fechada.
    def test_linha_que_cita_outra_etapa_so_fecha_a_atribuida(self):
        linhas = ["volta (E1.1) entregue no abc; review (E1.2) despachado",
                  "docs/qa/x.md=aprovado (E1.3); segurança (E1.4) despachada",
                  "docs/reviews/x.md=aprovado por delta (E1.5); docs/qa/x.md=reprovado por delta (E1.6, A1 bloqueante)",
                  "docs/qa/x.md=aprovado (E1.7, head abc; a volta E1.8 da segurança segue)",
                  "G2.0 entregue no #872; review (E1.9) despachado",
                  "E1.10 ainda não entregue",
                  "docs/reviews/x.md=reprovado (E1.11, o entregue segue com A1)",
                  "E1.12 despachado; item entregue no #9",
                  "review (E1.13) despachado e volta (E1.14) entregue"]
        texto = pedido_que_cresce("".join(f"- 2026-01-01 09:0{i % 10}: {l}\n" for i, l in enumerate(linhas)))
        self.gravar("docs/pedidos/exemplo.md", texto)
        self.assertEqual(fcs.etapas_fechadas(self.proj, self.caminho(), texto), {"E1.1", "E1.3", "E1.5", "E1.7"})
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 4)
        self.assertIn("- E1.1 (node-backend), E1.3 (node-backend), E1.5 (node-backend), E1.7 (node-backend)\n", self.pedido())
        self.assertIn("E1.2", fcs.ler_pedido_brief(self.pedido())["etapas"])

    # A2 do QA e S2 da segurança: o --cobre e as etapas citadas no Entregar nunca saem do pedido, mesmo entregues.
    def test_cobre_entregue_fica_no_pedido_e_o_brief_sai(self):
        historico, _ = self.fechamentos()
        self.gravar("docs/pedidos/exemplo.md", pedido_que_cresce(historico + "- 2026-01-01 09:06: E20.1 entregue\n"))
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertIn("Cobre: E20.1", saida)
        self.assertEqual(list(fcs.ler_pedido_brief(self.pedido())["etapas"]), ["E20.1", "E20.2"])

    # A2 do review e S3/S5 da segurança: junta delegações, papel errado e a contradição com o Fora do escopo barram igual depois.
    def test_corte_barra_igual_antes_e_depois_do_arquivo(self):
        texto = pedido_que_cresce(self.fechamentos()[0]).replace("## Decisões do usuário", "## Fora do escopo\n- E1.3 fica fora\n\n## Decisões do usuário")
        self.gravar("docs/pedidos/exemplo.md", texto)
        casos = [(["- a (E20.1)", "- b (E1.1)"], "etapa: junta delegações E1.1, E20.1 (R-BRIEF)"),
                 (["- a (E1.2)"], "etapa: papel errado E1.2"),
                 (["- c (E1.3)"], "contradição: o Entregar manda E1.3"),
                 (["- d (E1.1)"], None)]  # o papel arquivado (node-backend) é o do destino: nada reprova, antes e depois

        def reprovas():
            dados = fcs.ler_pedido_brief(self.pedido())
            saida = []
            for entregar, _ in casos:
                secoes = {"Entregar": entregar, "Fora do escopo": ["- E20.2 · outras delegações"]}
                saida.append([l for l, r in fcs.conferir_corte(secoes, dados, "forge:node-backend", "E20.1")
                              + fcs.conferir_pedido_contraditorio(secoes, dados) if r and l.startswith(("etapa:", "contradição:"))])
            return saida

        antes = reprovas()
        self.assertGreater(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 0)
        self.assertEqual(set(fcs.ler_pedido_brief(self.pedido())["etapas"]), {"E20.1", "E20.2"})
        self.assertEqual(reprovas(), antes)
        for (_, esperado), achadas in zip(casos, antes):
            self.assertTrue(any(l.startswith(esperado) for l in achadas) if esperado else not achadas, (esperado, achadas))

    def test_corte_de_pedido_so_com_arquivadas_ainda_barra(self):
        dados = {"escopo": {}, "etapas": {}, "arquivadas": {"E1.1": "tech-lead", "E1.2": "tech-lead"}, "texto": "", "fora": []}
        corte = fcs.conferir_corte({"Entregar": ["- a (E1.1)", "- b (E1.2)"]}, dados, "forge:tech-lead")
        self.assertIn(("etapa: junta delegações E1.1, E1.2 (R-BRIEF)", True), corte)
        dados["arquivadas"] = {"E1.1": None}  # arquivada sem papel: papel errado, com o papel vazio na mensagem
        corte = fcs.conferir_corte({"Entregar": ["- a (E1.1)"]}, dados, "forge:tech-lead")
        self.assertIn(("etapa: papel errado E1.1 (o pedido a põe em \"\", o destino é \"tech-lead\") (R-BRIEF)", True), corte)

    # A3 da segurança: a pasta e o arquivo do arquivo não seguem link nem escrevem em fifo; nada sai do pedido.
    def arquivar_recusado(self):
        texto = pedido_que_cresce(self.fechamentos()[0])
        self.gravar("docs/pedidos/exemplo.md", texto)
        self.assertEqual(fcs.arquivar_etapas_fechadas(self.proj, self.caminho())[0], 0)
        self.assertEqual(self.pedido(), texto)

    def test_pasta_do_arquivo_que_e_link_nao_recebe_nada(self):
        fora = self.proj / "fora"
        fora.mkdir()
        (self.proj / "docs" / "pedidos").mkdir(parents=True, exist_ok=True)
        (self.proj / "docs" / "pedidos" / "arquivo").symlink_to(fora)
        self.arquivar_recusado()
        self.assertEqual(list(fora.iterdir()), [])

    def test_arquivo_que_e_link_nao_recebe_nada(self):
        alvo = self.proj / "alvo.md"
        alvo.write_text("intacto\n", encoding="utf-8")
        (self.proj / "docs" / "pedidos" / "arquivo").mkdir(parents=True)
        (self.proj / "docs" / "pedidos" / "arquivo" / "exemplo.md").symlink_to(alvo)
        self.arquivar_recusado()
        self.assertEqual(alvo.read_text(encoding="utf-8"), "intacto\n")

    def test_arquivo_que_e_fifo_nao_recebe_nada(self):
        fifo = self.proj / "docs" / "pedidos" / "arquivo" / "exemplo.md"
        fifo.parent.mkdir(parents=True)
        os.mkfifo(fifo)
        leitor = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
        self.addCleanup(os.close, leitor)
        self.arquivar_recusado()
        self.assertEqual(os.read(leitor, 100), b"")


if __name__ == "__main__":
    unittest.main()
