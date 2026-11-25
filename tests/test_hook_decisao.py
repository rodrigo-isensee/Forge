"""ANTI-ALUC-F4-HOOK-DECISAO, fatia L28a (v0478 E172.6): o hook `decisao` no Stop do Jarvis só avisa o usuário
(`systemMessage`, código 0) quando a mensagem final traz mais de um grupo de opções ou um grupo sem "Recomendo", pela regra
do `forge-check transcricao decisoes` (`medir_decisoes`); nunca bloqueia. Cada ramo de silêncio tem o seu caso.
O hook roda em subprocesso com ambiente limpo e Python `-I` (o lançador põe hooks/ no caminho, como o `python3 -s -E` do
hooks.json faz pelo diretório do script)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HOOKS = RAIZ / "hooks"
LANCADOR = "import runpy, sys; sys.path.insert(0, sys.argv[1]); runpy.run_path(sys.argv[2], run_name='__main__')"

DUAS_DECISOES = "Primeira:\nA) manter\nB) trocar\nRecomendo A.\n\nSegunda:\nA) agora\nB) depois\nRecomendo A."
SEM_RECOMENDO = "Qual caminho?\nA) manter\nB) trocar"
UMA_COM_RECOMENDO = "Qual caminho?\nA) manter\nB) trocar\nRecomendo A: menos risco."
SEM_OPCOES = "Pendências:\n- revisar o PR\n- rodar a suíte"


class HookDecisao(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-decisao-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.projeto = self.tmp / "proj"
        (self.projeto / ".git").mkdir(parents=True)
        (self.projeto / ".forge").mkdir()
        (self.projeto / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        (self.tmp / "home").mkdir()

    def rodar(self, mensagem=None, evento="Stop", agente="forge:jarvis", cwd=None, transcrito=None):
        entrada = {"hook_event_name": evento, "session_id": "s1", "cwd": str(cwd or self.projeto)}
        if agente is not None:
            entrada["agent_type"] = agente
        if mensagem is not None:
            entrada["last_assistant_message"] = mensagem
        if transcrito is not None:
            entrada["transcript_path"] = str(transcrito)
        ambiente = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp / "home"), "LANG": "C.UTF-8"}
        return subprocess.run([sys.executable, "-I", "-c", LANCADOR, str(HOOKS), str(HOOKS / "decisao.py")],
                              input=json.dumps(entrada), capture_output=True, text=True, env=ambiente,
                              cwd=cwd or self.projeto, timeout=60)

    def assertAvisa(self, r):
        self.assertEqual(r.returncode, 0, r.stderr)
        saida = json.loads(r.stdout)
        self.assertEqual(list(saida), ["systemMessage"], "só ao usuário, nunca decision nem additionalContext (ADR 0003)")
        self.assertIn("R-DECISAO", saida["systemMessage"])
        self.assertNotIn("\n", saida["systemMessage"])
        self.assertLessEqual(len(saida["systemMessage"]), 200)

    def assertCala(self, r):
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)
        self.assertFalse((self.projeto / ".forge" / "run" / "erros.log").exists(), "o silêncio não é erro interno")

    def test_dois_grupos_de_opcoes_avisam_e_nao_bloqueiam(self):
        self.assertAvisa(self.rodar(DUAS_DECISOES))

    def test_grupo_sem_recomendo_avisa(self):
        self.assertAvisa(self.rodar(SEM_RECOMENDO))

    def test_um_grupo_com_recomendo_cala(self):
        self.assertCala(self.rodar(UMA_COM_RECOMENDO))

    def test_lista_de_pendencias_sem_opcoes_cala(self):
        self.assertCala(self.rodar(SEM_OPCOES))

    def test_sem_mensagem_nem_transcrito_cala_sem_erro(self):
        self.assertCala(self.rodar())

    def test_sem_o_campo_le_a_ultima_mensagem_do_transcrito(self):
        transcrito = self.tmp / "t.jsonl"
        linha = {"type": "assistant", "message": {"content": [{"type": "text", "text": SEM_RECOMENDO}]}}
        transcrito.write_text(json.dumps(linha) + "\n", encoding="utf-8")
        self.assertAvisa(self.rodar(transcrito=transcrito))

    def test_outro_evento_cala(self):
        self.assertCala(self.rodar(DUAS_DECISOES, evento="SubagentStop"))

    def test_sessao_que_nao_e_do_jarvis_cala(self):
        self.assertCala(self.rodar(DUAS_DECISOES, agente="forge:tech-lead"))

    def test_sessao_sem_agent_type_cala(self):
        self.assertCala(self.rodar(DUAS_DECISOES, agente=None))

    def test_fora_de_projeto_do_forge_cala(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        r = self.rodar(DUAS_DECISOES, cwd=fora)
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def test_hooks_json_liga_o_decisao_so_no_stop_com_teto_de_10_s(self):
        config = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        onde = [(evento, h["timeout"]) for evento, grupos in config.items() for g in grupos for h in g["hooks"]
                if h["args"][-1].endswith("/hooks/decisao.py")]
        self.assertEqual(onde, [("Stop", 10)])


if __name__ == "__main__":
    unittest.main()
