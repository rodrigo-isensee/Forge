"""MEDIR-M14B: as medidas que dão a linha de base do processo antes de qualquer afrouxamento (esperas, PR `fix` que corrige PR
mesclado, defeito escapado, rótulo `afrouxa-regra` que era afrouxamento real) e o casamento do `--pedido` do custo com os cartões."""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import Raiz  # noqa: E402

CABECALHO_HISTORICO = "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"


class CustoCasaOPedidoComOsCartoes(Raiz):
    """`transcricao custo --pedido`: o cartão do histórico não leva o id do pedido; o casamento é por nome, família ou coluna Pedido."""

    def setUp(self):
        super().setUp()
        for pedido in ("fix-x-pr", "outro"):
            self.gravar(f"docs/pedidos/{pedido}.md", "# Pedido\n")
        pasta = self.tmp / "home" / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(self.tmp.resolve()))
        pasta.mkdir(parents=True)
        horas = ["2026-10-20T09:00:00Z", "2026-10-20T10:30:00Z", "2026-10-20T11:30:00Z", "2026-10-20T14:00:00Z"]
        (pasta / "s.jsonl").write_text("\n".join(json.dumps(
            {"type": "assistant", "sessionId": "s", "isSidechain": False, "timestamp": h,
             "message": {"id": f"m{i}", "model": "m", "usage": {"input_tokens": 1, "output_tokens": 0}}}) for i, h in enumerate(horas)) + "\n",
            encoding="utf-8")

    def historico(self, *linhas):
        self.gravar("docs/kanban/historico.md", CABECALHO_HISTORICO + "".join(
            f"| 2026-10-20T{hora}:00+00:00 | {cartao} | A | B | x |\n" for hora, cartao in linhas))

    def custo(self, *args):
        cod, linhas, _ = self.rodar("transcricao", "custo", *args)
        return cod, linhas

    def test_cartao_da_mesma_familia_de_nome_casa_com_o_pedido(self):  # FIX-SUITE-LOCAL x FIX-SUITE-LOCAL-PR no histórico real
        self.historico(("10:00", "FIX-X"), ("11:00", "FIX-X"), ("12:30", "OUTRO-CARTAO"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: cartões: FIX-X", linhas)
        self.assertIn("custo: pedido: fix-x-pr janela 2026-10-20T10:00:00+00:00 a 2026-10-20T11:00:00+00:00", linhas)
        self.assertIn("custo: total: entrada=1 saida=0 cache_criacao=0 cache_leitura=0 total=1", linhas)
        self.assertNotIn("custo: aviso: 1 outros cartões em movimento na janela (o principal se mistura)", linhas)  # 12:30 fica fora

    def test_cartao_com_o_pedido_na_coluna_pedido_do_quadro_casa_e_os_outros_sao_avisados(self):
        self.gravar("KANBAN.md", "# Quadro\n\n| ID | Cartão | Pedido | Responsável |\n|---|---|---|---|\n| E7 | trabalho | fix-x-pr | forge:tech-lead |\n"
                    "| E8 | outro trabalho | outro | forge:tech-lead |\n")
        self.historico(("10:00", "E7"), ("10:40", "E8"), ("11:00", "E7"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: cartões: E7", linhas)
        self.assertIn("custo: aviso: 1 outros cartões em movimento na janela (o principal se mistura)", linhas)

    def test_cartao_que_nao_e_do_pedido_nao_entra_na_janela(self):
        self.historico(("10:00", "OUTRO-CARTAO"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 1)
        self.assertTrue(any("sem movimento de cartão do pedido" in l for l in linhas), linhas)

    def test_prefixo_sem_hifen_nao_e_da_familia(self):
        self.historico(("10:00", "FIX"), ("10:10", "FIX-XA"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 1)

    def test_nome_de_cartao_com_controle_nao_forja_linha(self):
        self.historico(("10:00", "OUTRO-\x1b[31mvermelho"), ("11:00", "OUTRO-\x1b[31mvermelho"))
        cod, linhas = self.custo("--pedido", "outro")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: cartões: OUTRO- [31mvermelho", linhas)
        self.assertFalse(any("\x1b" in l for l in linhas), linhas)


class Esperas(Raiz):
    """`forge-check esperas`: o registro de `forge-check movimento` vira minutos de espera pelo dono e por credencial."""
    HISTORICO = CABECALHO_HISTORICO + "".join(l + "\n" for l in (
        "| 2026-10-22T10:00:00-03:00 | K-1 | Em andamento | Aguardando o dono | decisão de escopo |",
        "| 2026-10-22T10:30:00-03:00 | K-1 | Aguardando o dono | Em andamento | dono decidiu |",
        "| 2026-10-22T11:00:00-03:00 | K-1 | Em andamento | Sem credencial | sem token do gh |",
        "| 2026-10-22T11:45:00-03:00 | K-1 | Sem credencial | Em andamento | token chegou |",
        "| 2026-10-22T12:00:00-03:00 | K-1 | Code review | Bloqueado | Aguardando o dono: rótulo no PR |",
        "| 2026-10-22T13:00:00-03:00 | K-2 | Em andamento | Bloqueado | dependência |",
        "| 2026-10-22T13:20:00-03:00 | K-2 | Bloqueado | Em andamento | liberou |",
        "| 2026-10-22T14:00:00-03:00 | K-3 | Em andamento | Aguardando o dono | pergunta |",
        "| 2026-10-22T14:10:00-03:00 | K-3 | Aguardando o dono | Bloqueado | Aguardando o dono: pergunta |",
        "| 2026-10-22T14:50:00-03:00 | K-3 | Bloqueado | Em andamento | respondeu |",
        "| sem-hora | K-3 | Em andamento | Aguardando o dono | linha sem hora ISO não conta |",
    ))

    def setUp(self):
        super().setUp()
        self.gravar("docs/kanban/historico.md", self.HISTORICO)

    def test_lista_cada_espera_com_tipo_e_minutos_e_o_total_por_tipo(self):
        cod, linhas, _ = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, [
            "esperas: K-1 dono inicio=2026-10-22T10:00:00-03:00 minutos=30",
            "esperas: K-1 credencial inicio=2026-10-22T11:00:00-03:00 minutos=45",
            "esperas: K-1 dono inicio=2026-10-22T12:00:00-03:00 minutos=aberta",
            "esperas: K-2 outra inicio=2026-10-22T13:00:00-03:00 minutos=20",
            "esperas: K-3 dono inicio=2026-10-22T14:00:00-03:00 minutos=50",  # Aguardando o dono -> Bloqueado (mesmo motivo) é a mesma espera
            "esperas: total: dono=3 minutos_dono=80 credencial=1 minutos_credencial=45 outra=1 minutos_outra=20 abertas=1 cartoes=3",
        ])

    def test_pedido_filtra_pelos_cartoes_do_pedido(self):
        self.gravar("KANBAN.md", "# Quadro\n\n| ID | Cartão | Pedido |\n|---|---|---|\n| K-2 | x | ped-a |\n| K-3 | y | ped-a |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-a")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas[0], "esperas: K-2 outra inicio=2026-10-22T13:00:00-03:00 minutos=20")
        self.assertEqual(linhas[-1], "esperas: total: dono=1 minutos_dono=50 credencial=0 minutos_credencial=0 outra=1 minutos_outra=20 abertas=0 cartoes=2")

    def test_pedido_sem_cartao_rc_1_e_sem_historico_so_avisa(self):
        cod, linhas, _ = self.rodar("esperas", "--pedido", "nenhum")
        self.assertEqual(cod, 1)
        self.assertTrue(linhas[0].startswith("esperas: pedido"), linhas)

    def test_sem_historico_rc_0_com_total_zerado_e_aviso(self):
        (self.tmp / "docs/kanban/historico.md").unlink()
        cod, linhas, erro = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, ["esperas: total: dono=0 minutos_dono=0 credencial=0 minutos_credencial=0 outra=0 minutos_outra=0 abertas=0 cartoes=0"])
        self.assertIn("aviso", erro)

    def test_o_movimento_do_jarvis_alimenta_as_esperas(self):  # o registro real, não só a linha escrita à mão
        self.gravar("KANBAN.md", "# Quadro\n")
        (self.tmp / "docs/kanban/historico.md").unlink()
        self.assertEqual(self.rodar("movimento", "K-9", "--de", "Em andamento", "--para", "Aguardando o dono", "--motivo", "validar")[0], 0)
        cod, linhas, _ = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertRegex(linhas[0], r"^esperas: K-9 dono inicio=\S+ minutos=aberta$")


if __name__ == "__main__":
    unittest.main()
