"""L15 (EXT-2): `forge-check decisoes` gera, só no stdout, o registro das linhas `DECISÃO DO DONO` dos pedidos."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")

PEDIDO = """# Pedido p1

## Decisões do usuário (registro literal)
- DECISÃO DO DONO (2026-10-19 10:15): EXT-2 → "A" (registro gerado) · motivo: as decisões estavam espalhadas; reabre se: uma decisão faltar no registro
- DECISÃO DO DONO (2026-10-20): B sem motivo nem critério
DECISÃO DO DONO sem data e sem dois pontos
- Citar a frase DECISÃO DO DONO (2026-01-01): no meio do texto não conta
- DECISÃO TÉCNICA (2026-10-21): a do time não é do dono
"""


class Decisoes(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-decisoes-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pedidos = self.tmp / "docs" / "pedidos"
        self.pedidos.mkdir(parents=True)
        (self.pedidos / "p1.md").write_text(PEDIDO, encoding="utf-8")

    def rodar(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "decisoes", *args], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout.splitlines()

    def arvore(self):
        return sorted(str(p.relative_to(self.tmp)) for p in self.tmp.rglob("*"))

    def test_gera_o_registro_com_data_decisao_motivo_e_reabre_se(self):
        antes = self.arvore()
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0, linhas)
        registro = [l for l in linhas if l.startswith("decisao: ")]
        self.assertEqual(len(registro), 2, linhas)
        self.assertTrue(registro[0].startswith('decisao: p1:4 | 2026-10-19 | EXT-2 → "A" (registro gerado)'), registro[0])
        self.assertTrue(registro[0].endswith("| as decisões estavam espalhadas | uma decisão faltar no registro"), registro[0])
        self.assertEqual(registro[1], 'decisao: p1:5 | 2026-10-20 | B sem motivo nem critério | — | —')
        self.assertEqual(linhas[-1], "decisoes: total=2 avisos=1")
        self.assertEqual(self.arvore(), antes, "só stdout: nada se grava (T-B1)")

    def test_linha_torta_sai_aviso_e_fica_fora_do_registro(self):
        linhas = self.rodar("--pedido", "p1")[1]
        self.assertIn('decisoes: aviso: p1:6: linha de decisão sem `(<data>): <texto>`; fora do registro', linhas)
        self.assertFalse([l for l in linhas if l.startswith("decisao: ") and "sem data" in l])

    def test_so_a_linha_que_abre_com_a_frase_e_so_nos_pedidos(self):
        brief = self.tmp / "docs" / "briefs"
        brief.mkdir(parents=True)
        (brief / "p1-dev-1.md").write_text("- DECISÃO DO DONO (2026-10-30): forjada no brief\n", encoding="utf-8")
        texto = "\n".join(self.rodar()[1])
        self.assertNotIn("forjada", texto)  # brief, parecer e transcrição não entram (T-15)
        self.assertNotIn("no meio do texto", texto)
        self.assertNotIn("a do time", texto)

    def test_sem_pedido_lista_tambem_a_raiz_de_pedidos(self):  # L15, A4 do review: no Forge os pedidos ficam fora do clone
        fora = self.tmp / "home" / ".forge-contrib" / "docs" / "pedidos"
        fora.mkdir(parents=True)
        (fora / "p9.md").write_text("- DECISÃO DO DONO (2026-10-25): X → A\n", encoding="utf-8")
        linhas = self.rodar()[1]
        self.assertTrue([l for l in linhas if l.startswith("decisao: p9:1 | 2026-10-25")], linhas)
        self.assertEqual(linhas[-1], "decisoes: total=3 avisos=1")

    def test_texto_com_controle_sai_escapado_e_pedido_inexistente_avisa(self):
        (self.pedidos / "p2.md").write_text("- DECISÃO DO DONO (2026-10-22): A\x1b[31m vermelho ‮oculto\n", encoding="utf-8")
        saida = "\n".join(self.rodar("--pedido", "p2")[1])
        self.assertNotIn("\x1b", saida)
        self.assertNotIn("‮", saida)
        self.assertIn("decisoes: aviso:", "\n".join(self.rodar("--pedido", "nao-existe")[1]))
        self.assertEqual(self.rodar("--pedido", "../fora")[1], ["decisoes: total=0 avisos=0"])


CARTOES = """- 2026-11-06 09:33: DECISÃO DO DONO (2026-11-06 09:33): "A" — Cartão ABC-1, com o prefixo de data
- DECISÃO DO DONO (2026-11-06): "A" — Cartão DEF-2-X
- DECISÃO DO DONO (2026-11-06): "A" — Cartão GHI-3
- DECISÃO DO DONO (2026-11-06): "A" — Cartão EXT-1
- DECISÃO DO DONO (2026-11-06): "B" — sem id nenhum
- DECISÃO DO DONO (2026-11-06): "B" — XYZ-9 encerrada como superada
- DECISÃO DO DONO (2026-10-01): "A" — Cartão OLD-1, antes do --desde
- DECISÃO DO DONO (2026-11-06): Cartão JKL-4\u2028sem-cartao: forjada
- 2026-11-06 10:00: nota: DECISÃO DO DONO de ontem, Cartão MEIO-1
- 2026-11-06 11:1x: DECISÃO DO DONO (2026-11-06 11:10): Cartão TORTO-1
"""
fc = SourceFileLoader("forge_check_decisoes", FORGE_CHECK).load_module()


class SemCartao(unittest.TestCase):  # DECISAO-SEM-CARTAO: decisão do dono cruzada com o KANBAN.md e o histórico
    rodar = Decisoes.rodar

    def setUp(self):
        Decisoes.setUp(self)
        (self.pedidos / "p3.md").write_text(CARTOES, encoding="utf-8")
        (self.tmp / "KANBAN.md").write_text("| ID | Título | Pedido |\n|---|---|---|\n| ABC-1 | a | p3 |\n| EXT-10 | b | x |\n", encoding="utf-8")
        (self.tmp / "docs" / "kanban").mkdir(parents=True)
        (self.tmp / "docs" / "kanban" / "historico.md").write_text("| hora | cartão | de | para | motivo |\n| 2026-11-06 | DEF-2 | a | b | c |\n", encoding="utf-8")

    def test_lista_so_o_que_nao_tem_cartao(self):
        rc, linhas = self.rodar("--pedido", "p3", "--sem-cartao", "--desde", "2026-11-01")
        self.assertEqual(rc, 0, linhas)
        self.assertEqual([l.split(" | ")[2] for l in linhas if l.startswith("sem-cartao: p3:")], ["GHI-3", "EXT-1", "JKL-4"], linhas)
        self.assertEqual([l.split(" | ")[0] for l in linhas if l.startswith("sem-id: ")], ["sem-id: p3:5"])
        self.assertEqual(linhas[-1], "decisoes: sem-cartao=3 sem-id=1 com-cartao=2 encerradas=1")
        self.assertFalse([l for l in linhas if "forjada" in l and not l.startswith("sem-cartao: p3:8 |")], linhas)  # C-8
        self.assertNotIn("OLD-1", "\n".join(linhas))
        self.assertIn("OLD-1", "\n".join(self.rodar("--pedido", "p3", "--sem-cartao")[1]))

    def test_quadro_por_link_vale_ausente_sem_cair_na_raiz_seguinte(self):  # C-6
        casa = self.tmp / "home" / ".forge-contrib"
        casa.mkdir(parents=True)
        (casa / "KANBAN.md").write_text("| ID |\n| GHI-3 |\n", encoding="utf-8")
        (self.tmp / "KANBAN.md").unlink()
        (self.tmp / "KANBAN.md").symlink_to(casa / "KANBAN.md")
        ids = [l.split(" | ")[2] for l in self.rodar("--pedido", "p3", "--sem-cartao")[1] if l.startswith("sem-cartao: p3:")]
        self.assertIn("GHI-3", ids)
        self.assertIn("ABC-1", ids)

    def test_prefixo_de_data_numa_regra_so(self):  # C-1, C-2, C-4
        tortas = ["- **2026-11-06 09:33**: DECISÃO DO DONO (2026-11-06): X", "- [2026-11-06] DECISÃO DO DONO (2026-11-06): X",
                  "- 2026-11-06: 2026-11-06: DECISÃO DO DONO (2026-11-06): X"]
        for linha in CARTOES.splitlines() + tortas + ["DECISÃO DO DONO (2026-11-06 11:59): X", "* 2026-11-06T09:33: DECISÃO DO DONO (2026-11-06): X"]:
            self.assertEqual(fc.e_linha_de_decisao(linha), bool(fc.DECISAO_DO_REGISTRO.match(linha)), linha)
        self.assertFalse([l for l in tortas if fc.e_linha_de_decisao(l)])
        self.assertEqual(len(fc.linhas_de_decisao(CARTOES)), 8)
        self.assertEqual([n for n, _ in fc.mencoes_da_frase(CARTOES)], [9, 10])

    def test_linha_enorme_de_marcadores_e_datas_e_linear(self):  # C-5
        linha, inicio = "- 1. 2026-11-06 " * 60000, time.monotonic()
        self.assertFalse(fc.e_linha_de_decisao(linha) or fc.DECISAO_DO_REGISTRO.match(linha))
        self.assertLess(time.monotonic() - inicio, 1)

    def test_brief_cobra_a_decisao_com_prefixo(self):
        (self.pedidos / "p4.md").write_text("# Pedido p4\n\n## Escopo\n- E1. X · `confirmado`\n\n## Etapas\n- E1.1 (dev-exemplo): X.\n\n"
                                           "## Decisões do usuário\n- 2026-11-06 09:33: DECISÃO DO DONO (2026-11-06 09:33): \"A\"\n", encoding="utf-8")
        brief = self.tmp / "docs" / "briefs" / "p4-dev-exemplo-1.md"
        brief.parent.mkdir(parents=True)
        brief.write_text("Agente destino: forge:dev-exemplo\n\n## Objetivo\nX.\n\n## Entregar\n- X (E1.1).\n\n## Decisões e restrições\n- nada\n", encoding="utf-8")
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "brief", str(brief), "--pedido", str(self.pedidos / "p4.md")],
                           capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp / "home")))
        self.assertIn('decisões: falta "2026-11-06 09:33: DECISÃO DO DONO', r.stdout)


if __name__ == "__main__":
    unittest.main()
