"""S3 (0.44.1): `bin/forge-status`, uma linha por pedido em curso para a statusLine, lida só do disco."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
STATUS = RAIZ / "bin" / "forge-status"
KANBAN = ("# Quadro\n\n## Aguardando o dono\n| ID | Cartão | Pedido | Responsável |\n|---|---|---|---|\n"
          "| K-1 | x | [p1](docs/pedidos/p1.md) | jarvis |\n\n## Em andamento (WIP 1 por agente)\n"
          "| ID | Cartão | Pedido | Responsável |\n|---|---|---|---|\n| K-2 | y | p2 | dev |\n\n## Pronto\n"
          "| ID | Cartão | Pedido | Responsável |\n|---|---|---|---|\n| K-3 | z | p3 | dev |\n")


class Status(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-status-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        (self.tmp / "KANBAN.md").write_text(KANBAN, encoding="utf-8")
        self.pedido("p1", "- 2026-11-09 10:00: aberto\n- 2026-11-09 11:00: pergunta ao dono sobre a fila\n")
        self.pedido("p2", "- 2026-11-09 09:00: aberto, PR #12\n- 2026-11-09 12:30: PR #15 aberto\x1b[31m vermelho\n")
        self.pedido("p3", "- 2026-11-09 13:00: mesclado\n")

    def pedido(self, nome, historico):
        (self.tmp / "docs" / "pedidos" / f"{nome}.md").write_text(f"# {nome}\n\n## Histórico\n{historico}", encoding="utf-8")

    def rodar(self, *args, entrada=""):
        r = subprocess.run([sys.executable, str(STATUS), *args], input=entrada, capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp)), timeout=30)
        return r.returncode, r.stdout.splitlines()

    def test_uma_linha_por_pedido_em_curso_do_mais_recente(self):
        cod, linhas = self.rodar(entrada=json.dumps({"workspace": {"current_dir": str(self.tmp)}}))
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, ["p2 · Em andamento · PR #15 · 12:30 PR #15 aberto [31m vermelho",
                                  "p1 · Aguardando o dono · 11:00 pergunta ao dono sobre a fila"])

    def test_controle_c1_vira_espaco(self):
        """Review da 0.44.1: o C1 (\\x80-\\x9f; o \\x9b é o CSI de 8 bits, o \\x85 quebra linha) sai como espaço, como o C0."""
        self.pedido("p2", "- 2026-11-09 12:30: PR #15\x9b31m vermelho\x85falso\n")
        cod, linhas = self.rodar("--raiz", str(self.tmp), "--max", "1")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, ["p2 · Em andamento · PR #15 · 12:30 PR #15 31m vermelho falso", "+1"])

    def test_raiz_pela_opcao_ou_pelo_cwd_do_json_e_o_maximo(self):
        self.pedido("p4", "sem histórico datado\n")
        cod, linhas = self.rodar("--raiz", str(self.tmp), "--max", "1")
        self.assertEqual(linhas, ["p2 · Em andamento · PR #15 · 12:30 PR #15 aberto [31m vermelho", "+2"])
        self.assertIn("p4 · fora do quadro · --:-- sem histórico", self.rodar(entrada=json.dumps({"cwd": str(self.tmp)}))[1])
        self.assertEqual(len(self.rodar("--raiz", str(self.tmp), "--max", "3")[1]), 3)

    def test_sem_pedido_em_curso_ou_entrada_invalida_nunca_falha(self):
        vazio = self.tmp / "vazio"
        vazio.mkdir()
        self.assertEqual(self.rodar("--raiz", str(vazio)), (0, ["forge: nenhum pedido em curso"]))
        self.assertEqual(self.rodar("--raiz", str(vazio), entrada="não é json")[1], ["forge: nenhum pedido em curso"])
        (self.tmp / "KANBAN.md").unlink()
        self.assertEqual(len(self.rodar("--raiz", str(self.tmp))[1]), 3, "sem quadro, todos ficam fora do quadro e aparecem")


if __name__ == "__main__":
    unittest.main()
