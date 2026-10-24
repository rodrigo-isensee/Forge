"""Arquivo de provas na branch (EST-030-L2, M15): formato do modelo e texto da regra que o descreve."""
import re
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DOCS = AQUI.parent / "docs"
LINHA_CMD = re.compile(r"^- PQ-(\d+) \(cmd\): `([^`]+)` · espera: (.+)$")


class ModeloDeProvas(unittest.TestCase):
    def test_modelo_traz_linhas_cmd_no_formato_da_regra(self):
        linhas = (DOCS / "provas" / "_modelo.md").read_text(encoding="utf-8").splitlines()
        cmd = [LINHA_CMD.match(l) for l in linhas if "(cmd)" in l and l.startswith("- PQ-")]
        self.assertEqual(len(cmd), 2)
        self.assertTrue(all(cmd))

    def test_regra_descreve_o_arquivo_a_lista_permitida_e_a_falha_fechada(self):
        regra = (DOCS / "regras" / "R-PROVA.md").read_text(encoding="utf-8")
        for trecho in ("docs/provas/<pedido>.md", "scripts/reexecutar-provas.py", "sem shell", "lista permitida",
                       "falha fechada", "pull_request_target"):
            self.assertIn(trecho, regra)


if __name__ == "__main__":
    unittest.main()
