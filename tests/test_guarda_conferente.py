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
from test_forge import ARQ, Cenario, carregar_forge_check  # noqa: E402
from test_hooks import modulos_dos_hooks, montar_proc, rodar as rodar_hook  # noqa: E402  (só funções)
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)


class ProjetoDoConferente(Cenario):
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



class GuardaDoConferente(ProjetoDoConferente):
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

    def test_recusa_mensagem_com_varios_blocos(self):
        r = self.lancar(self.cabecalho() + "\n" + self.cabecalho(arquivo="Arquivo: /abs/docs/briefs/q-y-2.md", sha="b" * 64))  # adendo 3, B9
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-BRIEF", r.stderr)
        self.assertIn("um brief por mensagem", r.stderr)

    def test_outro_agente_passa_sem_cabecalho(self):
        r = self.lancar("faça algo", tipo="time:tech-lead")  # fora do plugin; o `forge:` pede o selo (0.43.1, test_selo_e_entrega)
        self.assertEqual(r.returncode, 0, r.stderr)


class LeituraDeGitDoConferente(ProjetoDoConferente):
    """E8 (C-1 a C-6): `git branch` e `git worktree` do `forge:conferente` só nas formas de leitura do modelo."""

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

    def test_qa_encadeamento_e_escape_seguem_recusados(self):
        """QA: lock/move/repair, `-c x=y`, `--git-dir`, `;`, `&&`, `|`, `||`, substituição, crase e redirecionamentos não escapam."""
        for comando in ("git worktree lock w", "git worktree unlock w", "git worktree move w x", "git worktree repair",
                        "git worktree list -v", "git worktree list --porcelain -z", "git -c x=y branch", "git -c x=y worktree list",
                        "git --git-dir=/tmp/x branch", "git --git-dir /tmp/x worktree list", "git --work-tree=/tmp branch",
                        "git branch; git branch -D x", "git branch && git branch -D x", "git branch | tee f", "git branch || true; rm x",
                        "git branch `pwd`", "git branch --list `pwd`", "git branch >> saida", "git branch 2> saida", "git worktree list > saida",
                        "git worktree list; git worktree add w", "git worktree list && git worktree prune",
                        "git branch --set-upstream-to=origin/x", "git branch --set-upstream-to origin/x", "git branch --unset-upstream",
                        "git branch --contains=$(pwd)", "git branch --contains=-D"):
            with self.subTest(comando):
                r = self.bash(comando)
                self.assertEqual(r.returncode, 2, r.stderr)

    def test_outro_papel_e_a_forca_de_leitura_nao_mudam(self):
        _comum, conformidade, _ = modulos_dos_hooks()
        self.assertNotIn("branch", conformidade.GIT_LEITURA)
        self.assertNotIn("worktree", conformidade.GIT_LEITURA)


class ConferenteDoBrief(Cenario):
    """ACELERA-P1 E1a (C-2, C-4, C-8, C-9): a linha `conferente:` do `forge-check brief`; até a E1f sai sempre `necessário`."""
    MECANICO = "conferente: necessário (dispensa fora de vigor; mecânico)"

    def setUp(self):
        super().setUp()
        self.gravar(".claude-plugin/plugin.json", '{"name": "forge"}\n')  # a raiz do pedido é um clone do Forge (C-8)
        self.gravar(ARQ, "Tipo: codigo\n" + self.completo)

    def conferente(self, *extra, rc=0, arquivo=ARQ):
        cod, saida = self.brief(*extra, arquivo=arquivo)
        linhas = [l for l in saida if l.startswith("conferente:")]
        self.assertEqual((cod, len(linhas)), (rc, 1), saida)  # C-9: o rc não muda e nunca sai `dispensado`
        self.assertNotIn("dispensado", linhas[0])
        return linhas[0]

    def test_tipos_da_lista_branca_saem_mecanicos(self):
        for tipo in ("codigo", "review", "qa"):
            with self.subTest(tipo):
                self.gravar(ARQ, f"Tipo: {tipo}\n" + self.completo)
                self.assertEqual(self.conferente(), self.MECANICO)

    def test_tipo_fora_da_lista_ou_ausente_pede_o_conferente(self):
        for cabeca in ("Tipo: merge\n", "Tipo: ato-github\n", "Tipo: volta\n", "Tipo: desconhecido\n", "Tipo: Codigo\n", ""):
            with self.subTest(cabeca):
                self.gravar(ARQ, cabeca + self.completo)
                self.assertIn("conferente: necessário (Tipo: ", self.conferente())

    def test_anterior_e_reprovado_pedem_o_conferente(self):
        self.gravar("docs/briefs/pedido-sintetico-dev-exemplo-0.md", "Tipo: codigo\n" + self.completo)
        self.assertEqual(self.conferente("--anterior", "docs/briefs/pedido-sintetico-dev-exemplo-0.md"),
                         "conferente: necessário (volta ou --anterior)")
        self.gravar(ARQ, "Tipo: codigo\n" + self.completo.replace("## Pronto quando", "## Pronto"))
        self.assertEqual(self.conferente(rc=1), "conferente: necessário (brief reprovado)")

    def test_caractere_disfarcado_pede_o_conferente(self):
        for c in ("\u200b", "\u202e", "\ue000", "\x07", "\r"):
            with self.subTest(hex(ord(c))):
                self.gravar(ARQ, "Tipo: codigo\n" + self.completo.replace("Recurso A", f"Recurso{c}A"))
                self.assertEqual(self.conferente(), f"conferente: necessário (caractere U+{ord(c):04X})")

    def test_fora_do_forge_ou_por_link_pede_o_conferente(self):
        link = self.tmp / "docs/briefs/pedido-sintetico-dev-exemplo-2.md"
        link.symlink_to(self.tmp / ARQ)
        self.assertEqual(self.conferente(arquivo=str(link)), "conferente: necessário (fora do Forge)")
        (self.tmp / ".claude-plugin" / "plugin.json").unlink()
        self.assertEqual(self.conferente(), "conferente: necessário (fora do Forge)")

    def test_area_do_forge_contrib_vale_sem_clone(self):
        (self.tmp / ".claude-plugin" / "plugin.json").unlink()
        (self.tmp / "home/.forge-contrib").mkdir(parents=True)
        (self.tmp / "docs").rename(self.tmp / "home/.forge-contrib/docs")
        self.assertEqual(self.conferente(), self.MECANICO)

    def test_nao_verificavel_e_aviso_fora_da_tupla_pedem_o_conferente(self):
        fc, texto = carregar_forge_check(), "Tipo: codigo\n" + self.completo
        pedido, brief = self.tmp / "docs/pedidos/pedido-sintetico.md", self.tmp / ARQ
        motivo = lambda linha: fc.motivo_do_conferente(self.tmp, texto, pedido, brief, [("forma: ok", False), (linha, False)], None)
        self.assertIsNone(motivo("aviso: suposição sem \"muda com\": x (R-DECISAO)"))
        self.assertEqual(motivo("citação: fonte não verificável x (y)"), "saída com não verificável")
        self.assertEqual(motivo("aviso: etapa: x"), "saída com aviso: etapa: x")
        self.assertEqual(motivo("decisões: x aviso: y"), "saída com decisões: x aviso: y")


if __name__ == "__main__":
    unittest.main()
