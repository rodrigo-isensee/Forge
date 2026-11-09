"""0.44.1: a conversa com o dono e entre sessões no disco (`bin/forge_dono.py`, pelo `bin/forge-check`): resposta por código
curto (O4), fala do dono literal (S2), recado entre sessões (S8) e pausa por limite de uso com retomada (X1)."""
import datetime
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402

PERGUNTA = ('# p\n\n## Decisões do usuário (registro literal)\nPERGUNTA AO DONO (2026-11-09 10:00): duas questões → '
            '"1a) usar a fila [recomendada] 1b) usar o banco 2a) apagar a branch velha [recomendada] [irreversível] 2b) manter"\n')
VERSAO = json.loads((Path(FORGE_CHECK).parent.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


class Resposta(Raiz):  # O4
    def setUp(self):
        super().setUp()
        self.gravar("docs/pedidos/xpto.md", PERGUNTA)

    def resposta(self, texto):
        return self.rodar("decisoes", "--pedido", "xpto", "--resposta", texto)

    def test_codigos_curtos_viram_as_opcoes_da_pergunta(self):
        cod, linhas, _ = self.resposta("1B 2b")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[:2], ["resposta: 1 -> 1b: usar o banco", "resposta: 2 -> 2b: manter"])
        self.assertIn("forge-check anotar --pedido xpto --tipo decisao", linhas[-1])

    def test_codigo_parcial_deixa_a_outra_pendente(self):
        cod, linhas, _ = self.resposta("1a")
        self.assertEqual(cod, 0)
        self.assertIn("resposta: 2 -> sem resposta: segue pendente", linhas)

    def test_palavra_solta_aprova_a_recomendada_e_nunca_a_irreversivel(self):
        cod, linhas, _ = self.resposta("aprovo")
        self.assertEqual(cod, 1, linhas)
        self.assertIn("a questão 2 é irreversível", linhas[0])
        self.assertTrue(any(l.startswith("pergunta: 2) 2a) apagar") for l in linhas), linhas)
        cod, linhas, _ = self.resposta("2a, aprovo")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[:2], ["resposta: 1 -> 1a: usar a fila [recomendada]",
                                      "resposta: 2 -> 2a: apagar a branch velha [recomendada] [irreversível]"])

    def test_ambigua_volta_como_pergunta(self):
        for texto, motivo in (("pode", "`pode` fora do vocabulário"), ("1c", "o código 1c não existe"), ("3a", "o código 3a não existe"),
                              ("1a 1b", "duas opções para a questão 1"), ("", "nenhuma questão respondida")):
            with self.subTest(texto):
                cod, linhas, _ = self.resposta(texto)
                self.assertEqual(cod, 1, linhas)
                self.assertIn(motivo, linhas[0])
                self.assertIn("volta ao dono como pergunta", linhas[0])

    def test_sem_recomendada_unica_a_palavra_solta_nao_vale(self):
        self.gravar("docs/pedidos/xpto.md", PERGUNTA.replace(" [recomendada] 1b)", " 1b)"))
        cod, linhas, _ = self.resposta("sim 2b")
        self.assertEqual(cod, 1)
        self.assertIn("a questão 1 não tem uma recomendada só", linhas[0])

    def test_sem_pergunta_com_opcoes_ou_sem_pedido_nao_le(self):
        self.gravar("docs/pedidos/vazio.md", "# p\n")
        self.assertEqual(self.rodar("decisoes", "--pedido", "vazio", "--resposta", "1a")[0], 2)
        self.assertEqual(self.rodar("decisoes", "--pedido", "nao-existe", "--resposta", "1a")[0], 2)

    def test_vale_a_ultima_pergunta(self):
        self.gravar("docs/pedidos/xpto.md", PERGUNTA + 'PERGUNTA AO DONO (2026-11-09 11:00): "1a) sim 1b) não"\n')
        self.assertEqual(self.resposta("2b")[0], 1)
        self.assertEqual(self.resposta("1b")[1][0], "resposta: 1 -> 1b: não")


if __name__ == "__main__":
    unittest.main()
