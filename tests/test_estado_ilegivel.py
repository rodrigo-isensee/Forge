"""HOOK-ESTADO-ILEGIVEL-LIBERA (v047 E1.138; plano docs/security/v047-serie-hooks-pos-550.md, lote A): o `agentes.json` ilegível, o
erro ao fixar a pasta do estado do clone e o `.forge/config.json` ilegível recusam o disparo com R-TETO e nunca viram lista vazia;
`SubagentStart` e `SubagentStop` saem com 0 sem regravar o arquivo.

Os casos de ponta a ponta são os fixtures de tests/hooks/agentes/ (o hook roda como o Claude Code o roda); aqui, a leitura estrita
`ler_estado` nos ramos que o fixture não alcança para qualquer usuário: FIFO com JSON válido (o `S_ISREG`), o teto de tamanho e o
`PermissionError` (forçado no módulo, porque `chmod 000` não vale como root, AR-4) e o JSON aninhado fundo (RecursionError)."""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, HOOKS, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))
import agentes  # noqa: E402

DO_PEDIDO = ("estado-ilegivel-*.json", "estado-sem-chave-*.json", "config-ilegivel-*.json", "config-raiz-*.json", "erro-interno.json",
             "errointerno-clone-sem-estado-*.json", "errointerno-estado-corrompido-*.json")


class PeloHook(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_fixtures_do_pedido(self):
        """A1 a A3: cada forma ilegível recusa o disparo e a retomada; o início e o fim saem com 0 sem regravar; `{}` libera."""
        achados = sorted({p for padrao in DO_PEDIDO for p in (FIXTURES / "agentes").glob(padrao)})
        casos = [(f"agentes/{p.stem}", Fixture(p)) for p in minimo(achados, 20, "fixtures do estado ilegível")]
        self.assertEqual(self.executar_em_lote(casos), len(casos), "todo caso é verificado")


class LerEstado(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="forge-estado-"))
        self.addCleanup(shutil.rmtree, self.pasta, ignore_errors=True)
        self.arquivo = self.pasta / "agentes.json"

    def test_ausente_e_o_registro_vazio(self):
        self.assertEqual(agentes.ler_estado(self.arquivo), {"agentes": []})

    def test_registro_valido_volta_inteiro(self):
        dados = {"agentes": [{"id": "a1"}], "lapides": []}
        self.arquivo.write_text(json.dumps(dados), encoding="utf-8")
        self.assertEqual(agentes.ler_estado(self.arquivo), dados)

    def test_fifo_com_json_valido_e_ilegivel(self):
        """S_ISREG: a FIFO com um escritor aberto entrega um JSON válido ao `read`; só o tipo do arquivo a recusa."""
        os.mkfifo(self.arquivo)
        leitor = os.open(self.arquivo, os.O_RDONLY | os.O_NONBLOCK)  # deixa o escritor abrir sem bloquear
        escritor = os.open(self.arquivo, os.O_WRONLY | os.O_NONBLOCK)
        self.addCleanup(os.close, escritor)
        os.write(escritor, b'{"agentes": []}')
        os.close(leitor)  # o dado fica no cano enquanto o escritor segue aberto
        with self.assertRaises(agentes.EstadoIlegivel) as erro:
            agentes.ler_estado(self.arquivo)
        self.assertEqual(str(erro.exception), f"{self.arquivo}: não é arquivo regular", "o EstadoIlegivel de dentro sai como está")

    def test_acima_do_teto_de_tamanho_e_ilegivel(self):
        """O teto de tamanho: JSON válido de LIMITE_DO_ESTADO + 1 bytes recusa; no teto, passa."""
        corpo = '{"agentes": []}'
        self.arquivo.write_text(corpo + " " * (agentes.LIMITE_DO_ESTADO - len(corpo)), encoding="utf-8")
        self.assertEqual(agentes.ler_estado(self.arquivo), {"agentes": []})
        with open(self.arquivo, "a", encoding="utf-8") as f:
            f.write(" ")
        with self.assertRaises(agentes.EstadoIlegivel) as erro:
            agentes.ler_estado(self.arquivo)
        self.assertIn("passa de", str(erro.exception))

    def test_json_aninhado_fundo_e_ilegivel(self):
        """Volta do A1 (sondas S1 e S2): o `[` aninhado fundo, abaixo do teto, lança RecursionError no `json.loads`; é ilegível."""
        for corpo in ("[" * 200000, '{"agentes":' + "[" * 200000):
            with self.subTest(inicio=corpo[:12]):
                self.arquivo.write_text(corpo, encoding="utf-8")
                with self.assertRaises(agentes.EstadoIlegivel) as erro:
                    agentes.ler_estado(self.arquivo)
                self.assertIn("RecursionError", str(erro.exception))

    def test_erro_de_permissao_e_ilegivel(self):
        """O `OSError` da abertura (modo 000 de outro usuário) é ilegível, forçado no módulo (AR-4)."""
        self.arquivo.write_text('{"agentes": []}', encoding="utf-8")
        with mock.patch.object(agentes.os, "open", side_effect=PermissionError(13, "negado")), \
                self.assertRaises(agentes.EstadoIlegivel) as erro:
            agentes.ler_estado(self.arquivo)
        self.assertIn("PermissionError", str(erro.exception))

    def test_link_para_json_valido_e_ilegivel(self):
        alvo = self.pasta / "alvo.json"
        alvo.write_text('{"agentes": []}', encoding="utf-8")
        self.arquivo.symlink_to(alvo)
        with self.assertRaises(agentes.EstadoIlegivel):
            agentes.ler_estado(self.arquivo)

    def test_fifo_sem_escritor_nao_bloqueia(self):
        """Sanidade do teste da FIFO: sem escritor, a FIFO também é ilegível (nunca bloqueia a leitura)."""
        os.mkfifo(self.arquivo)
        resultado = []
        leitura = threading.Thread(target=lambda: resultado.append(self._tenta()))
        leitura.start()
        leitura.join(5)
        self.assertFalse(leitura.is_alive(), "a leitura da FIFO não pode bloquear")
        self.assertEqual(resultado, ["ilegível"])

    def _tenta(self):
        try:
            agentes.ler_estado(self.arquivo)
        except agentes.EstadoIlegivel:
            return "ilegível"
        return "lido"


if __name__ == "__main__":
    unittest.main()
