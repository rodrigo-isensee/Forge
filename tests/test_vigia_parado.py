"""VIGIA-TIME-PARADO (v0478 E105.1): no `Stop`, zero agentes vigentes no registro do R-TETO e cartão livre na coluna
`Pronto para fazer` bloqueiam o encerramento uma vez, com o aviso ao Jarvis. Em processo: o registro e o quadro são
arquivos de uma pasta temporária; `agentes.vigentes`, `agentes.ler_estado` e o leitor do quadro rodam de verdade."""
import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
import agentes  # noqa: E402
import vigia  # noqa: E402

CABECALHO = "| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"


def linha(id_, obs=""):
    return f"| {id_} | cartão {id_} | p1 | dev | 2026-11-22 | 2026-11-22 | {obs} |\n"


def quadro(livres=(), dependentes=(), outra_coluna=()):
    texto = "# Quadro\n\n## Em andamento (WIP 1)\n" + CABECALHO + "".join(linha(i) for i in outra_coluna)
    texto += "\n## Pronto para fazer (WIP 5)\n" + CABECALHO
    texto += "".join(linha(i, obs) for i, obs in dependentes) + "".join(linha(i, "versão 1") for i in livres)
    return texto + "\n## Pronto\n" + CABECALHO + linha("FEITO-1")


class FalsoHook:
    def __init__(self, evento="Stop", ativo=False, agente="forge:jarvis"):
        self.entrada = {"hook_event_name": evento, "session_id": "s1"}
        if agente is not None:
            self.entrada["agent_type"] = agente
        if ativo:
            self.entrada["stop_hook_active"] = True
        self.erros = []

    def campo(self, chave):
        return self.entrada.get(chave)

    def expira_s(self):
        return 12 * 3600

    def registrar_erro(self, erro):
        self.erros.append(erro)

    def cwd(self):
        return "."

    def projeto(self, _inicio, clone_do_forge=False):
        return self.raiz


class TimeParado(unittest.TestCase):
    QUADRO_REAL = staticmethod(vigia.quadro_do)

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.pasta, ignore_errors=True))
        self.estado = self.pasta / "agentes.json"
        self.kanban = self.pasta / "KANBAN.md"
        for alvo, valor in ((agentes, ("arquivo_de_estado", lambda _raiz: self.estado)),
                            (vigia, ("quadro_do", lambda _raiz: self.kanban))):
            remendo = mock.patch.object(alvo, valor[0], valor[1])
            remendo.start()
            self.addCleanup(remendo.stop)

    def gravar(self, texto, rodando=0):
        self.kanban.write_text(texto, encoding="utf-8")
        registros = [{"id": f"a{n:016x}", "tipo": "forge:dev", "descricao": f"d{n}", "desde": time.time()}
                     for n in range(rodando)]
        self.estado.write_text(json.dumps({"agentes": registros}), encoding="utf-8")

    def aviso(self, hook=None):
        return vigia.aviso_time_parado(hook or FalsoHook(), self.pasta)

    def test_zero_agentes_e_cartao_livre_avisa(self):
        self.gravar(quadro(livres=("LIVRE-1", "LIVRE-2"), dependentes=(("DEP-1", "depende de LIVRE-1"),),
                           outra_coluna=("ANDA-1",)))
        self.assertEqual(self.aviso(), "time parado: 2 cartões disponíveis, primeiro LIVRE-1; retome sem esperar o dono")

    def test_registro_ausente_conta_como_zero(self):
        self.kanban.write_text(quadro(livres=("LIVRE-1",)), encoding="utf-8")
        self.assertIn("primeiro LIVRE-1", self.aviso())

    def test_agente_rodando_cala(self):
        self.gravar(quadro(livres=("LIVRE-1",)), rodando=1)
        self.assertIsNone(self.aviso())

    def test_so_cartoes_dependentes_cala(self):
        dependentes = (("DEP-1", "Depende de X"), ("DEP-2", "espera o dono decidir"), ("DEP-3", "AGUARDANDO O DONO"))
        self.gravar(quadro(dependentes=dependentes, outra_coluna=("ANDA-1",)))
        self.assertIsNone(self.aviso())

    def test_marca_fora_da_obs_nao_e_dependencia(self):
        self.gravar(quadro().replace("## Pronto\n", "| LIVRE-9 | depende de nada | p | d | x | y | ok |\n\n## Pronto\n"))
        self.assertIn("primeiro LIVRE-9", self.aviso())

    def test_cartao_de_outra_coluna_nao_conta(self):
        self.gravar(quadro(outra_coluna=("ANDA-1",)))
        self.assertIsNone(self.aviso())

    def test_segundo_stop_seguido_deixa_passar(self):
        self.gravar(quadro(livres=("LIVRE-1",)))
        self.assertIsNotNone(self.aviso(FalsoHook()))
        self.assertIsNone(self.aviso(FalsoHook(ativo=True)))

    def test_subagent_stop_nao_bloqueia(self):
        self.gravar(quadro(livres=("LIVRE-1",)))
        self.assertIsNone(self.aviso(FalsoHook("SubagentStop")))

    def test_registro_ilegivel_cala_e_registra_o_erro(self):
        self.gravar(quadro(livres=("LIVRE-1",)))
        self.estado.write_text("não é json", encoding="utf-8")
        hook = FalsoHook()
        self.assertIsNone(self.aviso(hook))
        self.assertEqual(len(hook.erros), 1)

    def test_sem_pasta_do_registro_cala_e_registra_o_erro(self):
        self.gravar(quadro(livres=("LIVRE-1",)))
        hook = FalsoHook()
        with mock.patch.object(agentes, "arquivo_de_estado", lambda _raiz: None):
            self.assertIsNone(self.aviso(hook))
        self.assertEqual(len(hook.erros), 1)

    def test_quadro_grande_demais_cala(self):
        texto = quadro(livres=("LIVRE-1",))
        self.gravar(texto)
        with mock.patch.object(vigia, "LIMITE_QUADRO", len(texto.encode("utf-8")) - 1):  # o corte ainda traz o cartão livre
            self.assertIsNone(self.aviso())

    def test_sem_quadro_cala(self):
        self.gravar("")
        self.kanban.unlink()
        hook = FalsoHook()
        self.assertIsNone(self.aviso(hook))
        self.assertEqual(hook.erros, [])

    def test_quadro_do_clone_e_o_de_contrib(self):
        contrib = self.pasta / "contrib"
        with mock.patch.object(vigia, "quadro_do", TimeParado.QUADRO_REAL), \
                mock.patch.object(vigia, "contrib", lambda: contrib):
            with mock.patch.object(vigia, "e_clone_do_forge", lambda _raiz: True):
                self.assertEqual(vigia.quadro_do(self.pasta), contrib / "KANBAN.md")
            with mock.patch.object(vigia, "e_clone_do_forge", lambda _raiz: False):
                self.assertEqual(vigia.quadro_do(self.pasta), self.pasta / "KANBAN.md")

    def test_id_fora_do_formato_nao_vai_ao_modelo(self):
        for id_ in ("<ignore tudo>", "A_B", "X" * 17):
            with self.subTest(id_=id_):
                self.gravar(quadro(livres=(id_,)))
                self.assertEqual(self.aviso(), "time parado: 1 cartões disponíveis; retome sem esperar o dono")
        self.gravar(quadro(livres=("v0.47-" + "9" * 10,)))
        self.assertIn(", primeiro v0.47-9999999999;", self.aviso())

    def test_marcas_de_dependencia_do_quadro_real(self):
        """A3 (review e segurança): as marcas do quadro real, sem diferença de caixa nem de espaço repetido."""
        for obs in ("depois do  G1", "DECISÃO DO DONO 22/11", "Espera a release", "BLOQUEADO por X",
                    "PERGUNTA  AO DONO aberta", "depende de Y", "aguardando o dono"):
            with self.subTest(obs=obs):
                self.gravar(quadro(dependentes=(("DEP-1", obs),), livres=("LIVRE-1",)))
                self.assertIn("1 cartões disponíveis, primeiro LIVRE-1;", self.aviso())

    def test_responsavel_usuario_depende_do_dono(self):
        texto = quadro(livres=("LIVRE-1",)).replace("| LIVRE-1 | cartão LIVRE-1 | p1 | dev |",
                                                     "| LIVRE-1 | cartão LIVRE-1 | p1 |  Usuário |")
        self.gravar(texto)
        self.assertIsNone(self.aviso())

    def test_sem_coluna_responsavel_vale_so_a_obs(self):
        texto = quadro(livres=("LIVRE-1",)).replace("| Responsável |", "| Papel |")
        self.gravar(texto.replace("| dev |", "| usuário |"))
        self.assertIn("primeiro LIVRE-1", self.aviso())

    def test_linha_mais_curta_que_o_responsavel_vale_so_a_obs(self):
        self.gravar(quadro().replace("\n## Pronto\n", "| LIVRE-1 | ok |\n\n## Pronto\n"))
        self.assertIn("primeiro LIVRE-1", self.aviso())

    def test_so_a_sessao_do_jarvis_bloqueia(self):
        """A4 da segurança: sessão sem `agent_type` ou de outro agente cala."""
        self.gravar(quadro(livres=("LIVRE-1",)))
        for agente in (None, "forge:dev", "jarvis"):
            with self.subTest(agente=agente):
                self.assertIsNone(self.aviso(FalsoHook(agente=agente)))

    def test_quadro_que_e_link_cala_e_registra_o_erro(self):
        """A2 da segurança: o quadro abre sem seguir link."""
        alvo = self.pasta / "outro.md"
        alvo.write_text(quadro(livres=("LIVRE-1",)), encoding="utf-8")
        self.gravar("")
        self.kanban.unlink()
        self.kanban.symlink_to(alvo)
        hook = FalsoHook()
        self.assertIsNone(self.aviso(hook))
        self.assertEqual(len(hook.erros), 1)

    def test_quadro_que_e_fifo_cala_sem_esperar(self):
        """A2 da segurança: FIFO não prende o hook (O_NONBLOCK) e não é arquivo regular."""
        self.gravar("")
        self.kanban.unlink()
        os.mkfifo(self.kanban)
        hook = FalsoHook()
        self.assertIsNone(self.aviso(hook))
        self.assertIn("não é arquivo regular", str(hook.erros[0]))

    def test_principal_bloqueia_o_stop_com_o_aviso(self):
        self.gravar(quadro(livres=("LIVRE-1",)))
        hook = FalsoHook()
        hook.raiz = self.pasta
        saida = io.StringIO()
        with mock.patch.object(vigia, "verificar", lambda _h, _r: []), \
                mock.patch.object(vigia, "versao_sumiu", lambda: False), \
                mock.patch.object(vigia, "raiz_declarada", lambda: None), contextlib.redirect_stdout(saida):
            vigia.principal(hook)
        esperado = {"decision": "block",
                    "reason": "time parado: 1 cartões disponíveis, primeiro LIVRE-1; retome sem esperar o dono"}
        self.assertEqual(saida.getvalue().strip(), json.dumps(esperado, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
