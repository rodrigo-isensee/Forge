"""AGENTE-PRESO-SEM-BAIXA (v048 E12.2, ordem do dono 28/11 07:48 item 1): o registro de agentes dá baixa no agente que a
notificação terminal do Claude Code prova parado também quando ela chega no meio do turno (anexo `queued_command`), o vigia
não conta esse agente como rodando nem como preso, e `hooks/agentes.py --limpar` aplica as mesmas provas sob demanda."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "hooks"))
import agentes  # noqa: E402
import vigia  # noqa: E402
from test_trava_agente_morto import AID, SESSAO, USO, Base, cabecalho, carimbo  # noqa: E402


# Sonda S9 da revisão de segurança no 116cc18 (o M6 de tests/mutantes/trava-agente-morto.json fora da fonte), refeita no CI:
# python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (no 2a310c7c)

def na_fila(quando, conteudo=None, isSidechain=False, **anexo):
    """A notificação do meio do turno, na forma que o Claude Code grava no transcript da sessão-mãe."""
    campos = {"type": "queued_command", "commandMode": "task-notification", "prompt": conteudo or cabecalho(),
              "origin": {"kind": "task-notification", "producer": "session-task"}, **anexo}
    return {"parentUuid": "p", "isSidechain": isSidechain, "type": "attachment", "timestamp": carimbo(quando),
            "sessionId": SESSAO, "attachment": campos}


class NotificacaoNaFila(Base):
    def test_anexo_da_fila_libera(self):
        for status in ("failed", "completed", "killed"):
            with self.subTest(status=status):
                self.escrever(na_fila(self.agora - 5, cabecalho(status=status)))
                sobra, soltos = self.solta()
                self.assertEqual((sobra, [s for _, s in soltos]), ([], [status]))

    def test_texto_digitado_no_meio_do_turno_nao_libera(self):
        self.escrever(na_fila(self.agora - 5, commandMode="prompt", origin={"kind": "human"}))
        self.assertMantem()

    def test_anexo_com_um_campo_fora_da_forma_nao_libera(self):
        for anexo in ({"type": "outro"}, {"commandMode": "prompt"}, {"origin": {"kind": "human"}}, {"origin": "task-notification"}):
            with self.subTest(anexo=anexo):
                self.escrever(na_fila(self.agora - 5, **anexo))
                self.assertMantem()

    def test_anexo_de_sidechain_nao_libera(self):
        for valor in (True, None):
            with self.subTest(isSidechain=valor):
                self.escrever(na_fila(self.agora - 5, isSidechain=valor))
                self.assertMantem()

    def test_anexo_sem_tool_use_id_nao_libera(self):  # C2 segue: sem o id do disparo, nada prova que é este agente
        self.escrever(na_fila(self.agora - 5, cabecalho().replace(f"<tool-use-id>{USO}</tool-use-id>\n", "")))
        self.assertMantem()


class VigiaSemOParado(Base):
    """O `Stop` do Jarvis lê o registro com a mesma prova: o agente parado não vira `preso há mais de 10 min`."""

    def rodando(self, *entradas):
        self.escrever(*entradas)
        (self.run / "agentes.json").write_text(json.dumps({"agentes": [self.registro()]}), encoding="utf-8")
        hook = vigia_hook(self.transcript)
        with mock.patch.object(agentes, "arquivo_de_estado", lambda _raiz: self.run / "agentes.json"):
            return vigia.agentes_rodando(hook, self.tmp)

    def test_parado_pela_notificacao_nao_roda(self):
        self.assertEqual(self.rodando(na_fila(self.agora - 5)), [])

    def test_sem_notificacao_segue_rodando(self):
        self.assertEqual([a["id"] for a in self.rodando()], [AID])

    def test_trava_pesado_e_a_da_pasta_do_registro(self):  # C9: escrita com o pesado ocupado nessa pasta fica
        (self.run / "pesado.json").write_text(json.dumps({"desde": self.agora, "pid": os.getpid()}), encoding="utf-8")
        self.escrever(na_fila(self.agora - 5))
        (self.run / "agentes.json").write_text(json.dumps({"agentes": [self.registro(escrita=["melhoria/x"])]}), encoding="utf-8")
        with mock.patch.object(agentes, "arquivo_de_estado", lambda _raiz: self.run / "agentes.json"), \
                mock.patch.object(agentes, "pid_vivo", lambda *_a: True):
            self.assertEqual([a["id"] for a in vigia.agentes_rodando(vigia_hook(self.transcript), self.tmp)], [AID])


def vigia_hook(transcript):
    hook = agentes.Hook("vigia")
    hook.entrada = {"hook_event_name": "Stop", "session_id": SESSAO, "transcript_path": str(transcript)}
    hook.expira_s = lambda: 7200
    return hook


class Limpar(Base):
    """`agentes.py --limpar`: as provas do hook sob demanda, nada além delas."""

    def limpar(self, registros, *entradas):
        self.escrever(*entradas)
        (self.run / "agentes.json").write_text(json.dumps({"agentes": registros}), encoding="utf-8")
        with mock.patch.object(agentes.Hook, "projeto", lambda h, *_a, **_k: self.tmp), \
                mock.patch.object(agentes.Hook, "run", lambda h: self.run), \
                mock.patch.object(agentes.Hook, "expira_s", lambda h: 7200), \
                mock.patch.object(agentes, "e_clone_do_forge", lambda _r: False), \
                mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            rc = agentes.limpar(self.tmp)
        return rc, json.loads((self.run / "agentes.json").read_text(encoding="utf-8"))

    def test_da_baixa_no_parado_e_deixa_lapide_e_log(self):
        rc, estado = self.limpar([self.registro()], na_fila(self.agora - 5))
        self.assertEqual((rc, estado["agentes"], [l["id"] for l in estado["lapides"]]), (0, [], [AID]))
        self.assertIn(f"id={AID} status=failed motivo=notificacao", (self.run / "liberacoes.log").read_text(encoding="utf-8"))

    def test_sem_prova_o_registro_fica(self):
        rc, estado = self.limpar([self.registro()])
        self.assertEqual((rc, [a["id"] for a in estado["agentes"]]), (0, [AID]))

    def test_dois_transcripts_da_mesma_sessao_nenhum_vale(self):
        outro = self.home / ".claude" / "projects" / "-q" / f"{SESSAO}.jsonl"
        outro.parent.mkdir(parents=True)
        outro.write_text(json.dumps(na_fila(self.agora - 5)) + "\n", encoding="utf-8")
        rc, estado = self.limpar([self.registro()], na_fila(self.agora - 5))
        self.assertEqual((rc, [a["id"] for a in estado["agentes"]]), (0, [AID]))

    def test_registro_fora_da_forma_nao_derruba(self):
        rc, estado = self.limpar([5, self.registro()], na_fila(self.agora - 5))
        self.assertEqual((rc, estado["agentes"]), (0, []))

    def test_sem_sessao_ainda_tira_o_vencido(self):  # a passada sem sessão aplica o prazo, como o hook
        vencido = self.registro(desde=self.agora - 99999)
        del vencido["sessao"]
        rc, estado = self.limpar([vencido])
        self.assertEqual((rc, estado["agentes"]), (0, []))

    def test_sessao_fora_da_forma_nao_procura_transcript(self):
        self.escrever()
        self.assertEqual(agentes.transcripts_da_sessao("*"), [])
        self.assertEqual(agentes.transcripts_da_sessao(None), [])
        self.assertEqual(agentes.transcripts_da_sessao(SESSAO), [self.transcript])

    def test_registro_ilegivel_recusa_sem_regravar(self):
        (self.run / "agentes.json").write_text("{", encoding="utf-8")
        with mock.patch.object(agentes.Hook, "projeto", lambda h, *_a, **_k: self.tmp), \
                mock.patch.object(agentes.Hook, "run", lambda h: self.run), \
                mock.patch.object(agentes, "e_clone_do_forge", lambda _r: False), mock.patch("sys.stderr"):
            self.assertEqual(agentes.limpar(self.tmp), 1)
        self.assertEqual((self.run / "agentes.json").read_text(encoding="utf-8"), "{")

    def test_fora_de_projeto_sai_1(self):
        with mock.patch.object(agentes.Hook, "projeto", lambda h, *_a, **_k: None), mock.patch("sys.stderr"):
            self.assertEqual(agentes.limpar(self.tmp), 1)


LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); sys.argv = sys.argv[2:]; "
            "runpy.run_path(sys.argv[0], run_name='__main__')")


class ComandoLimpar(unittest.TestCase):
    """O ramo do `__main__`: `--limpar` não lê o stdin do hook; fora de projeto, sai 1 e diz por quê."""

    def test_fora_de_projeto_pela_linha_de_comando(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = subprocess.run([sys.executable, "-I", "-c", LANCADOR, str(AQUI.parent / "hooks"),
                                    str(AQUI.parent / "hooks" / "agentes.py"), "--limpar"], cwd=pasta,
                                   env={"PATH": os.environ.get("PATH", ""), "HOME": pasta}, input="", capture_output=True,
                                   text=True, timeout=60)
        self.assertEqual((saida.returncode, saida.stderr.strip()), (1, "agentes.py --limpar: fora de um projeto do Forge"))


if __name__ == "__main__":
    unittest.main()
