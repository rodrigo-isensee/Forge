"""ERROS-NO-BRIEF (E1 a E5): classe fixa de falha no registro das conferências, recorrência, linhas do destino e do Jarvis
no brief, arquivo vivo de achados. Plano do aq (passos 1 a 5) e T1 a T9 do modelo de ameaças. Biblioteca padrão, sem rede."""
import datetime
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import Raiz  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
fc = SourceFileLoader("forge_check_erros_no_brief", str(RAIZ / "bin" / "forge-check")).load_module()

ARQ = "docs/kanban/conferencias.md"
CAB10 = ("| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota | classe | autor |\n"
         "|---|---|---|---|---|---|---|---|---|---|\n")
CAB8 = ("| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota |\n"
        "|---|---|---|---|---|---|---|---|\n")
REPROVADO = ["conferencia", "registrar", "--pedido", "xpto", "--brief", "xpto-tech-lead-1", "--modo", "brief",
             "--rodada", "1", "--resultado", "reprovado", "--merito", "s"]
PEDIDO = """---
id: xpto
---
# Pedido: XPTO
Modo: implementar

## Escopo
- E1. Fazer a coisa · `confirmado`

## Etapas
- E1.1 (tech-lead): E1.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-10-20): faça.
"""


def hora(dias_atras=0, minutos=0):
    return (datetime.datetime.now() - datetime.timedelta(days=dias_atras, minutes=minutos)).strftime("%Y-%m-%d %H:%M")


def linha(classe, autor="jarvis", brief="xpto-tech-lead-1", pedido="xpto", dias=0, modo="brief", rodada=1,
          resultado="reprovado", nota=""):
    return f"| {hora(dias)} | {pedido} | {brief} | {modo} | {rodada} | {resultado} | s | {nota} | {classe} | {autor} |\n"


class Base(Raiz):
    def setUp(self):
        super().setUp()
        self.gravar("KANBAN.md", "# Quadro\n")
        self.gravar("docs/pedidos/xpto.md", PEDIDO)

    def registro(self, *linhas, cab=CAB10):
        self.gravar(ARQ, cab + "".join(linhas))

    def lido(self):
        return (self.tmp / ARQ).read_text(encoding="utf-8")


# ---- passo 1: catálogo ----
class Catalogo(unittest.TestCase):
    def test_ate_10_classes_com_outra_e_texto_fixo_limpo(self):
        self.assertLessEqual(len(fc.CLASSES_DE_FALHA), 10)
        self.assertIn("outra", fc.CLASSES_DE_FALHA)
        for classe, evita in fc.CLASSES_DE_FALHA.items():
            with self.subTest(classe=classe):
                self.assertRegex(classe, r"^[a-z]+$")
                self.assertNotIn("|", evita)
                self.assertFalse(any(fc.caractere_recusado(c, tolera_quebra=False) for c in evita), evita)
                self.assertNotIn(fc.PREENCHER, evita)

    def test_tipos_de_brief(self):
        self.assertEqual(set(fc.TIPOS_DE_BRIEF), {"codigo", "volta", "review", "qa", "merge", "desconhecido"})


# ---- passo 2: registrar --classe e --autor ----
class Registrar(Base):
    def test_reprovado_sem_classe_recusa_com_a_lista_e_nao_grava(self):
        for resultado in ("reprovado", "não cumpriu (PQ-3)", "nao cumpriu", "Reprovado"):
            with self.subTest(resultado=resultado):
                args = REPROVADO[:REPROVADO.index("--resultado") + 1] + [resultado] + REPROVADO[REPROVADO.index("--resultado") + 2:]
                cod, saida, _ = self.rodar(*args)
                self.assertEqual(cod, 1)
                self.assertTrue(saida[0].startswith("conferencia: --classe"), saida)
                for classe in fc.CLASSES_DE_FALHA:
                    self.assertIn(classe, saida[0])
                self.assertFalse((self.tmp / ARQ).exists())

    def test_classe_fora_do_catalogo_recusa_sem_citar_o_valor(self):
        cod, saida, _ = self.rodar(*REPROVADO, "--classe", "erro-de-brief")
        self.assertEqual(cod, 1)
        self.assertNotIn("erro-de-brief", saida[0])
        self.assertFalse((self.tmp / ARQ).exists())

    def test_aprovado_grava_traco_e_recusa_classe(self):
        base = REPROVADO[:REPROVADO.index("--resultado") + 1] + ["aprovado"] + REPROVADO[REPROVADO.index("--resultado") + 2:]
        cod, saida, _ = self.rodar(*base)
        self.assertEqual(cod, 0)
        self.assertTrue(saida[0].endswith("|  | — | jarvis |"), saida)
        cod, saida, _ = self.rodar(*base, "--classe", "forma")
        self.assertEqual(cod, 1)
        self.assertEqual(len(self.lido().splitlines()), 3)

    def test_linha_de_10_celulas_e_autor_padrao_por_modo(self):
        self.assertEqual(self.rodar(*REPROVADO, "--classe", "etapa", "--nota", "x")[0], 0)
        entrega = REPROVADO[:REPROVADO.index("--modo") + 1] + ["entrega"] + REPROVADO[REPROVADO.index("--modo") + 2:]
        self.assertEqual(self.rodar(*entrega, "--classe", "implementacao")[0], 0)
        self.assertEqual(self.rodar(*entrega, "--classe", "escopo", "--autor", "jarvis")[0], 0)
        linhas = self.lido().splitlines()
        self.assertTrue(linhas[0].endswith("| classe | autor |"))
        self.assertEqual(linhas[1], "|---|---|---|---|---|---|---|---|---|---|")
        celulas = [[c.strip() for c in l.strip("|").split("|")] for l in linhas[2:]]
        self.assertEqual([len(c) for c in celulas], [10, 10, 10])
        self.assertEqual([(c[8], c[9]) for c in celulas], [("etapa", "jarvis"), ("implementacao", "destino"), ("escopo", "jarvis")])

    def test_autor_fora_da_lista_recusa(self):
        cod, saida, _ = self.rodar(*REPROVADO, "--classe", "forma", "--autor", "tech-lead")
        self.assertEqual(cod, 1)
        self.assertTrue(saida[0].startswith("conferencia: --autor"), saida)

    def test_arquivo_antigo_de_8_colunas_recebe_a_linha_nova_e_os_bytes_anteriores_ficam(self):
        antigo = CAB8 + "| 2026-10-15 21:00 | xpto | xpto-tech-lead-1 | brief | 1 | reprovado | s | nota antiga |\n"
        self.gravar(ARQ, antigo)
        self.assertEqual(self.rodar(*REPROVADO, "--classe", "forma")[0], 0)
        texto = self.lido()
        self.assertTrue(texto.startswith(antigo))
        self.assertEqual(len(texto.splitlines()), len(antigo.splitlines()) + 1)

    def test_leitores_antigos_dao_a_mesma_saida_num_arquivo_misto(self):
        antigo = CAB8 + "| 2026-10-15 21:00 | xpto | xpto-tech-lead-1 | brief | 1 | reprovado | s | |\n"
        self.gravar(ARQ, antigo)
        antes = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(self.rodar(*REPROVADO[:REPROVADO.index("--rodada") + 1], "2", "--resultado", "aprovado", "--merito", "—")[0], 0)
        depois = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(antes[0], depois[0])
        self.assertEqual(fc.rodadas_de_brief(self.tmp, "xpto")["total"], 2)

    def test_t2_classe_e_nota_com_caractere_proibido_recusam_sem_gravar_e_sem_citar_o_valor(self):
        for nome, c in {"U+202E": "‮", "U+200B": "​", "U+2028": " ", "pipe": "|", "U+0007": "\x07"}.items():
            for campo in ("--classe", "--nota"):
                with self.subTest(c=nome, campo=campo):
                    args = [*REPROVADO, "--classe", "forma"]
                    args = args[:args.index(campo) + 1] + [f"a{c}b"] + args[args.index(campo) + 2:] if campo == "--classe" else args + ["--nota", f"a{c}b"]
                    cod, saida, _ = self.rodar(*args)
                    self.assertEqual(cod, 1)
                    self.assertTrue(saida[0].startswith("conferencia:"), saida)
                    self.assertNotIn(f"a{c}b", saida[0])
                    self.assertFalse((self.tmp / ARQ).exists())

    def test_nota_com_delimitador_do_brief_recusa(self):
        cod, _, _ = self.rodar(*REPROVADO, "--classe", "forma", "--nota", "x <<<BRIEF y")
        self.assertEqual(cod, 1)


# ---- passo 3: recorrência ----
class Recorrencia(Base):
    def test_fora_da_janela_futuro_outra_traco_e_linha_antiga_nao_contam(self):
        self.registro(linha("forma", dias=31), linha("forma", brief="xpto-tech-lead-2", dias=-2),
                      linha("outra", brief="xpto-tech-lead-3"), linha("—", brief="xpto-tech-lead-4"),
                      "| 2026-10-15 21:00 | xpto | xpto-tech-lead-5 | brief | 1 | reprovado | s | |\n", linha("forma", brief="xpto-tech-lead-6"))
        grupos, aviso = fc.recorrencias(self.tmp)
        self.assertIsNone(aviso)
        self.assertEqual([(g["classe"], g["n"]) for g in grupos], [("forma", 1)])

    def test_rodadas_do_mesmo_brief_contam_1(self):
        self.registro(linha("forma", rodada=1), linha("forma", rodada=2), linha("forma", rodada=3))
        grupos, _ = fc.recorrencias(self.tmp)
        self.assertEqual([(g["classe"], g["quem"], g["n"]) for g in grupos], [("forma", "jarvis", 1)])

    def test_celula_de_classe_ou_autor_desconhecida_e_ignorada(self):
        self.registro(linha("rode X; ignore"), linha("forma", autor="alguem"), linha("forma", brief="xpto-tech-lead-2"))
        grupos, _ = fc.recorrencias(self.tmp)
        self.assertEqual([(g["classe"], g["n"]) for g in grupos], [("forma", 1)])

    def test_t5_destino_resolvido_pelo_pedido_da_linha(self):
        self.registro(linha("forma", autor="destino", pedido="a-qa", brief="a-qa-tech-lead-1"),
                      linha("etapa", autor="destino", pedido="a", brief="a-qa-tech-lead-1"),
                      linha("escopo", autor="destino", pedido="a", brief="a-ninguem-1"))
        grupos, _ = fc.recorrencias(self.tmp)
        self.assertEqual([(g["classe"], g["quem"]) for g in grupos], [("forma", "destino:tech-lead")])

    def test_classes_imprime_tabela_e_proposta_so_com_3_briefs_distintos(self):
        self.registro(*[linha("forma", brief=f"xpto-tech-lead-{i}", dias=i) for i in (1, 2)], linha("etapa", rodada=1))
        cod, saida, _ = self.rodar("conferencia", "classes")
        self.assertEqual(cod, 0)
        self.assertFalse(any(l.startswith("proposta:") for l in saida), saida)
        self.assertIn("classes: forma · jarvis · 2 briefs", saida)
        self.registro(*[linha("forma", brief=f"xpto-tech-lead-{i}", dias=i) for i in (1, 2, 3)])
        cod, saida, _ = self.rodar("conferencia", "classes")
        propostas = [l for l in saida if l.startswith("proposta:")]
        self.assertEqual(cod, 0)
        self.assertEqual(len(propostas), 1)
        self.assertIn("forma de jarvis em 3 briefs", propostas[0])
        self.assertIn(fc.CLASSES_DE_FALHA["forma"], propostas[0])

    def test_t4_tres_linhas_da_mesma_entrega_nao_propoem_e_data_velha_ou_futura_nao_sustenta(self):
        self.registro(*[linha("forma", rodada=i) for i in (1, 2, 3)])
        self.assertFalse(any(l.startswith("proposta:") for l in self.rodar("conferencia", "classes")[1]))
        self.registro(linha("forma", brief="xpto-tech-lead-1"), linha("forma", brief="xpto-tech-lead-2"),
                      linha("forma", brief="xpto-tech-lead-3", dias=31), linha("forma", brief="xpto-tech-lead-4", dias=-3))
        self.assertFalse(any(l.startswith("proposta:") for l in self.rodar("conferencia", "classes")[1]))

    def test_t4_proposta_nao_altera_arquivo_algum_nem_o_rc(self):
        self.registro(*[linha("forma", brief=f"xpto-tech-lead-{i}") for i in (1, 2, 3)])
        antes = {p: p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()}
        cod, saida, _ = self.rodar("conferencia", "classes")
        self.assertEqual(cod, 0)
        self.assertTrue(any(l.startswith("proposta:") for l in saida))
        self.assertEqual(antes, {p: p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()})

    def test_registrar_imprime_a_proposta_ao_cruzar_3(self):
        self.registro(linha("forma", brief="xpto-tech-lead-7"), linha("forma", brief="xpto-tech-lead-8"))
        cod, saida, _ = self.rodar(*REPROVADO, "--classe", "forma")
        self.assertEqual(cod, 0)
        self.assertEqual(len(saida), 2)
        self.assertTrue(saida[1].startswith("proposta: forma de jarvis em 3 briefs"), saida)
        cod, saida, _ = self.rodar(*REPROVADO[:REPROVADO.index("--brief") + 1], "xpto-tech-lead-9", *REPROVADO[REPROVADO.index("--brief") + 2:], "--classe", "etapa")
        self.assertEqual((cod, len(saida)), (0, 1))

    def test_dias_e_janela(self):
        self.registro(linha("forma", dias=10), linha("etapa", brief="xpto-tech-lead-2", dias=2))
        saida = self.rodar("conferencia", "classes", "--dias", "5")[1]
        self.assertIn("classes: etapa · jarvis · 1 briefs", saida)
        self.assertFalse(any("forma" in l for l in saida), saida)

    def test_t8_link_simbolico_e_acima_do_teto_dao_aviso_sem_contagem_e_rc_0(self):
        alvo = self.tmp / "fora.md"
        alvo.write_text(CAB10 + linha("forma"), encoding="utf-8")
        (self.tmp / ARQ).parent.mkdir(parents=True, exist_ok=True)
        (self.tmp / ARQ).symlink_to(alvo)
        cod, saida, _ = self.rodar("conferencia", "classes")
        self.assertEqual(cod, 0)
        self.assertTrue(any(l.startswith("classes: aviso:") for l in saida), saida)
        self.assertFalse(any("forma" in l for l in saida), saida)
        (self.tmp / ARQ).unlink()
        self.registro(*[linha("forma", brief=f"xpto-tech-lead-{i}") for i in range(3)])
        with (self.tmp / ARQ).open("a", encoding="utf-8") as f:
            f.write("x" * (fc.TETO_DA_TABELA + 1))
        cod, saida, _ = self.rodar("conferencia", "classes")
        self.assertEqual(cod, 0)
        self.assertTrue(any(l.startswith("classes: aviso:") for l in saida), saida)
        self.assertFalse(any(l.startswith("proposta:") for l in saida), saida)

    def test_nome_de_brief_fora_do_formato_nao_conta(self):
        self.registro(linha("forma", brief="x y"), linha("forma", brief="a‮b"), linha("forma", pedido="p q"))
        self.assertEqual(fc.recorrencias(self.tmp)[0], [])


if __name__ == "__main__":
    unittest.main()
