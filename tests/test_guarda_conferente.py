"""M6 (R-BRIEF): a guarda do hook `agentes` ao lançar o `forge:conferente` (só a forma do cabeçalho)."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_forge import ARQ, Cenario  # noqa: E402
from test_hooks import montar_proc, rodar as rodar_hook  # noqa: E402  (só funções)
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)


class GuardaDoConferente(Cenario):
    """M6 (R-BRIEF): o hook `agentes` recusa o `forge:conferente` sem o cabeçalho da mensagem; só a forma, sem ler o arquivo."""

    HASH = "a" * 64

    def setUp(self):
        super().setUp()
        self.projeto = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.projeto, True)
        subprocess.run(["git", "init", "-q"], cwd=self.projeto, check=True, env=dict(os.environ, HOME=str(self.projeto)))
        (self.projeto / ".forge").mkdir()
        (self.projeto / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        self.proc = montar_proc(self.projeto, {"loadavg": "0.1 0.1 0.1", "mem_gb": 8})

    def lancar(self, prompt, tipo="forge:conferente", descricao="d"):
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(self.projeto),
                   "tool_input": {"subagent_type": tipo, "description": descricao, "prompt": prompt}}
        return rodar_hook("agentes", entrada, self.projeto, self.proc, {"FORGE_NPROC": "8"})

    def recusado(self, prompt):
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-BRIEF", r.stderr)
        self.assertIn("forge-check brief mensagem", r.stderr)

    def cabecalho(self, modo="modo: brief", arquivo="Arquivo: docs/briefs/p-x-1.md", sha=None):
        sha = self.HASH if sha is None else sha
        return "\n".join(l for l in (modo, "Pedido: docs/pedidos/p.md   Agente destino: forge:x   Etapa: -", arquivo,
                                      f"Brief-sha256: {sha}   Bytes: 10" if sha != "" else None) if l) + "\n<<<BRIEF\ncorpo\nBRIEF>>>\n"

    def test_recusa_sem_modo(self):
        self.recusado(self.cabecalho(modo="Pedido: x"))

    def test_recusa_modo_que_nao_e_a_primeira_linha(self):
        self.recusado("introdução\n" + self.cabecalho())

    def test_recusa_modo_desconhecido(self):
        self.recusado(self.cabecalho(modo="modo: outro"))

    def test_recusa_sem_arquivo(self):
        self.recusado(self.cabecalho(arquivo=""))

    def test_recusa_arquivo_fora_de_docs_briefs(self):
        self.recusado(self.cabecalho(arquivo="Arquivo: docs/pedidos/p.md"))

    def test_recusa_sem_hash(self):
        self.recusado(self.cabecalho(sha=""))

    def test_recusa_hash_curto(self):
        self.recusado(self.cabecalho(sha="a" * 63))

    def test_recusa_hash_nao_hexadecimal(self):
        self.recusado(self.cabecalho(sha="g" * 64))

    def test_recusa_prompt_vazio(self):
        self.recusado("")

    def test_passa_a_saida_real_do_brief_mensagem(self):
        rc, saida = self.mensagem()
        self.assertEqual(rc, 0, saida)
        r = self.lancar(saida.decode())
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_passa_com_arquivo_relativo(self):
        rc, saida = self.mensagem()
        self.assertEqual(rc, 0, saida)
        relativa = saida.decode().replace(f"Arquivo: {(self.tmp / ARQ).resolve()}", f"Arquivo: {ARQ}")
        self.assertIn(f"Arquivo: {ARQ}\n", relativa)
        r = self.lancar(relativa)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_passa_mensagem_de_entrega(self):
        r = self.lancar(self.cabecalho(modo="modo: entrega"))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_passa_mensagem_com_varios_blocos(self):
        r = self.lancar(self.cabecalho() + "\n" + self.cabecalho(arquivo="Arquivo: /abs/docs/briefs/q-y-2.md", sha="b" * 64))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_outro_agente_passa_sem_cabecalho(self):
        r = self.lancar("faça algo", tipo="forge:tech-lead")
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
