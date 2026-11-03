"""L15 (EXT-2): `forge-check decisoes` gera, só no stdout, o registro das linhas `DECISÃO DO DONO` dos pedidos."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
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

    def test_texto_com_controle_sai_escapado_e_pedido_inexistente_avisa(self):
        (self.pedidos / "p2.md").write_text("- DECISÃO DO DONO (2026-10-22): A\x1b[31m vermelho ‮oculto\n", encoding="utf-8")
        saida = "\n".join(self.rodar("--pedido", "p2")[1])
        self.assertNotIn("\x1b", saida)
        self.assertNotIn("‮", saida)
        self.assertIn("decisoes: aviso:", "\n".join(self.rodar("--pedido", "nao-existe")[1]))
        self.assertEqual(self.rodar("--pedido", "../fora")[1], ["decisoes: total=0 avisos=0"])


if __name__ == "__main__":
    unittest.main()
