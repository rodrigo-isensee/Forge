"""S-18: `forge-check conferencia registrar` grava a conferência em formato fixo e o leitor da T-1 a lê."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import Raiz  # noqa: E402

ARQ = "docs/kanban/conferencias.md"
BASE = ["conferencia", "registrar", "--pedido", "xpto", "--brief", "xpto-tech-lead-1", "--modo", "brief",
        "--rodada", "1", "--resultado", "aprovado", "--merito", "—"]


def com(base, **troca):
    args = list(base)
    for chave, valor in troca.items():
        args[args.index("--" + chave) + 1] = valor
    return args


class Registrar(Raiz):
    def lido(self):
        return (self.tmp / ARQ).read_text(encoding="utf-8")

    def test_cria_o_arquivo_com_cabecalho_e_grava_linha_de_8_colunas_com_hora_real(self):
        cod, saida, _ = self.rodar(*BASE, "--nota", "tudo certo")
        self.assertEqual(cod, 0)
        linhas = self.lido().splitlines()
        self.assertTrue(linhas[0].startswith("| data-hora | pedido | brief | modo | rodada | resultado |"))
        self.assertEqual(linhas[1], "|---|---|---|---|---|---|---|---|")
        self.assertRegex(linhas[2], r"^\| \d{4}-\d{2}-\d{2} \d{2}:\d{2} \| xpto \| xpto-tech-lead-1 \| brief \| 1 \| "
                                    r"aprovado \| — \| tudo certo \|$")
        self.assertEqual(saida, [linhas[2]])
        self.assertEqual(len(linhas), 3)

    def test_acrescenta_sem_mexer_no_que_existe_e_conserta_falta_de_quebra(self):
        antigo = "# Registro\n\n| h | p |\n|---|---|\n| 2026-10-15 21:20 | a | b | brief | 1 | aprovado | — | |"
        self.gravar(ARQ, antigo)
        self.assertEqual(self.rodar(*com(BASE, rodada="2"))[0], 0)
        texto = self.lido()
        self.assertTrue(texto.startswith(antigo + "\n| "))
        self.assertEqual(len(texto.splitlines()), len(antigo.splitlines()) + 1)

    def test_recusas_nao_gravam(self):
        casos = [com(BASE, modo="outro"), com(BASE, merito="talvez"), com(BASE, rodada="1.5"), com(BASE, rodada="x"),
                 com(BASE, rodada="0"), com(BASE, rodada="-1"), com(BASE, resultado="a|b"),
                 com(BASE, resultado="a\nb"), com(BASE, brief="x|y"), com(BASE, pedido="p\nq"),
                 BASE + ["--nota", "a|b"], BASE + ["--nota", "a\nb"], com(BASE, resultado="  ")]
        for args in casos:
            with self.subTest(args=args):
                cod, saida, _ = self.rodar(*args)
                self.assertNotEqual(cod, 0)
                self.assertTrue(saida and saida[0].startswith("conferencia:"), saida)
                self.assertFalse((self.tmp / ARQ).exists())

    def test_recusa_separadores_de_linha_unicode_em_cada_campo(self):
        # O leitor usa str.splitlines(); U+2028, U+2029, U+0085 e afins partiriam a linha gravada (S-18-R1).
        # Cada subcaso tem o diretório próprio, para a falha de um não cair nos outros.
        separadores = {"U+2028": "\u2028", "U+2029": "\u2029", "U+0085": "\x85", "U+000B": "\x0b", "U+000C": "\x0c",
                       "U+001C": "\x1c", "U+001D": "\x1d", "U+001E": "\x1e"}
        for nome, sep in separadores.items():
            for campo in ("pedido", "brief", "resultado", "nota"):
                with self.subTest(separador=nome, campo=campo), tempfile.TemporaryDirectory() as pasta:
                    self.tmp = Path(pasta)
                    args = com(BASE, **{campo: f"a{sep}b"}) if campo != "nota" else BASE + ["--nota", f"a{sep}b"]
                    cod, saida, _ = self.rodar(*args)
                    self.assertNotEqual(cod, 0)
                    self.assertTrue(saida and saida[0].startswith("conferencia:"), saida)
                    self.assertFalse((Path(pasta) / ARQ).exists())

    def test_vocabulario_aceito(self):
        for modo in ("brief", "entrega"):
            for merito in ("s", "n", "parcial", "—"):
                self.assertEqual(self.rodar(*com(BASE, modo=modo, merito=merito))[0], 0)
        self.assertEqual(len(self.lido().splitlines()), 2 + 8)

    def test_recusa_link_simbolico(self):
        alvo = self.tmp / "fora.md"
        alvo.write_text("x\n", encoding="utf-8")
        (self.tmp / ARQ).parent.mkdir(parents=True)
        (self.tmp / ARQ).symlink_to(alvo)
        self.assertNotEqual(self.rodar(*BASE)[0], 0)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "x\n")

    def test_o_voltas_e_a_soma_de_rodadas_leem_a_linha_gravada(self):
        self.assertEqual(self.rodar(*com(BASE, resultado="reprovado", merito="s"))[0], 0)
        self.assertEqual(self.rodar(*com(BASE, rodada="2"))[0], 0)
        self.assertEqual(self.rodar(*com(BASE, modo="entrega"))[0], 0)  # entrega não conta como rodada de brief
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(cod, 0)
        self.assertTrue(any(re.match(r"voltas: xpto brief inicio=\S+ \S+ minutos=\S+ ref=xpto-tech-lead-1", l)
                            for l in linhas), linhas)
        pasta = self.tmp / "sessoes"
        pasta.mkdir()
        (pasta / "a.jsonl").write_text(
            '{"type": "assistant", "timestamp": "2026-10-17T10:00:00Z", "sessionId": "s", "isSidechain": false, '
            '"message": {"id": "m1", "model": "m", "usage": {"input_tokens": 1, "output_tokens": 1}}}\n',
            encoding="utf-8")
        cod, linhas, _ = self.rodar("transcricao", "custo", str(pasta), "--entregas", "--entrega", "xpto")
        self.assertEqual(cod, 0)
        self.assertIn("| 2 |", linhas[0])
        self.assertIn("fonte=conferencias", linhas[0])


if __name__ == "__main__":
    unittest.main()
