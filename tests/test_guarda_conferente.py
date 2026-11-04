"""M6 (R-BRIEF): a guarda do hook `agentes` ao lançar o `forge:conferente` (a forma do cabeçalho; o hash do arquivo é conferido
em `test_agentes_hash_brief`, e aqui só o caminho feliz com o arquivo de verdade)."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ARQ, Cenario  # noqa: E402
from test_hooks import modulos_dos_hooks, montar_proc, rodar as rodar_hook  # noqa: E402  (só funções)
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)


class GuardaDoConferente(Cenario):
    """M6 (R-BRIEF): o hook `agentes` recusa o `forge:conferente` sem o cabeçalho da mensagem; o arquivo do brief existe no
    projeto e o hash do cabeçalho é o dele (AGT-2: o hook o recalcula)."""

    def setUp(self):
        super().setUp()
        self.projeto = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.projeto, True)
        subprocess.run(["git", "init", "-q"], cwd=self.projeto, check=True, env=sem_manutencao(dict(os.environ, HOME=str(self.projeto))))
        (self.projeto / ".forge").mkdir()
        (self.projeto / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        self.proc = montar_proc(self.projeto, {"loadavg": "0.1 0.1 0.1", "mem_gb": 8})
        conteudo = b"# brief\ncorpo\n"
        for nome in ("p-x-1.md", "meu brief.md"):
            (self.projeto / "docs" / "briefs").mkdir(parents=True, exist_ok=True)
            (self.projeto / "docs" / "briefs" / nome).write_bytes(conteudo)
        self.HASH = hashlib.sha256(conteudo).hexdigest()

    def no_projeto(self, mensagem):
        """A mensagem real do `forge-check brief mensagem` (gerada na raiz do cenário) com o brief copiado para o projeto do hook."""
        origem = (self.tmp / ARQ).resolve()
        destino = self.projeto / ARQ
        destino.write_bytes(origem.read_bytes())
        return mensagem.replace(f"Arquivo: {origem}", f"Arquivo: {destino}")

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
        r = self.lancar(self.no_projeto(saida.decode()))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_passa_com_arquivo_relativo(self):
        rc, saida = self.mensagem()
        self.assertEqual(rc, 0, saida)
        relativa = self.no_projeto(saida.decode()).replace(f"Arquivo: {self.projeto / ARQ}", f"Arquivo: {ARQ}")
        self.assertIn(f"Arquivo: {ARQ}\n", relativa)
        r = self.lancar(relativa)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_passa_arquivo_absoluto_com_espaco(self):
        r = self.lancar(self.cabecalho(arquivo=f"Arquivo: {self.projeto / 'docs' / 'briefs' / 'meu brief.md'}"))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_recusa_arquivo_com_espaco_sem_nome_em_docs_briefs(self):
        self.recusado(self.cabecalho(arquivo="Arquivo: /mnt/c/Meus Projetos/docs/briefs/"))

    def test_passa_mensagem_de_entrega(self):
        r = self.lancar(self.cabecalho(modo="modo: entrega"))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_passa_mensagem_com_varios_blocos(self):
        r = self.lancar(self.cabecalho() + "\n" + self.cabecalho(arquivo="Arquivo: /abs/docs/briefs/q-y-2.md", sha="b" * 64))  # só o 1º bloco vale
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_outro_agente_passa_sem_cabecalho(self):
        r = self.lancar("faça algo", tipo="forge:tech-lead")
        self.assertEqual(r.returncode, 0, r.stderr)


class LeituraDeGitDoConferente(Cenario):
    """E8 (C-1 a C-6): `git branch` e `git worktree` do `forge:conferente` só nas formas de leitura do modelo."""

    def setUp(self):
        GuardaDoConferente.setUp(self)  # o mesmo projeto e o mesmo proc, sem repetir os testes do lançamento

    def bash(self, comando):
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "session_id": "s", "cwd": str(self.projeto),
                   "agent_type": "forge:conferente", "tool_input": {"command": comando}}
        return rodar_hook("conformidade", entrada, self.projeto, self.proc, {"FORGE_NPROC": "8"})

    def test_passam_as_formas_de_leitura(self):
        for comando in ("git branch", "git branch --list 'melhoria/*'", "git branch -r", "git branch --contains 928e61b",
                        "git branch --contains=928e61b", "git branch -r --contains origin/develop", "git branch -r --list x",
                        "git -C . --no-pager branch", "git worktree list"):
            with self.subTest(comando):
                r = self.bash(comando)
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_recusam_as_formas_de_escrita_e_fora_do_limite(self):
        for comando in ("git branch x", "git branch -D develop", "git branch -d x", "git branch -m a b", "git branch -f x HEAD",
                        "git branch -u origin/x", "git branch --edit-description", "git branch --del x", "git branch --cont x",
                        "git branch --contains -D", "git branch --contains", "git branch --contains x novo", "git branch -rd x",
                        "git branch -a", "git branch -v", "git branch --show-current", "git branch --list -x",
                        "git worktree add ../w", "git worktree prune", "git worktree remove w", "git worktree list --porcelain",
                        "git worktree", "git -c core.pager=x branch", "git branch $(pwd)", "git branch > saida"):
            with self.subTest(comando):
                r = self.bash(comando)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("R-CONFORMIDADE", r.stderr)

    def test_outro_papel_e_a_forca_de_leitura_nao_mudam(self):
        _comum, conformidade, _ = modulos_dos_hooks()
        self.assertNotIn("branch", conformidade.GIT_LEITURA)
        self.assertNotIn("worktree", conformidade.GIT_LEITURA)


if __name__ == "__main__":
    unittest.main()
