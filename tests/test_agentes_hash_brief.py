"""AGT-2 (R-BRIEF): a mensagem ao `forge:conferente` confere o hash do arquivo do brief, não só a forma do cabeçalho.
Módulo à parte do AGT-1 (cada commit se reverte sozinho): os apoios de execução do hook são repetidos aqui."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

HOOKS = Path(__file__).resolve().parent.parent / "hooks"
PRAZO_GIT = "120"  # o git dos hooks tem 5 s em produção; com a suíte em paralelo a máquina carregada passaria disso
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; "
            "_comum.forge_check().GIT_TIMEOUT_S = int(sys.argv[3]); "
            "sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")
TETO = 256 * 1024


class HashDoBrief(unittest.TestCase):
    def setUp(self):
        self.projeto = Path(tempfile.mkdtemp(prefix="forge-agt2-")).resolve()
        self.addCleanup(shutil.rmtree, self.projeto, True)
        self.home = self.projeto / "home"
        env = sem_manutencao(dict(os.environ, HOME=str(self.projeto)))
        subprocess.run(["git", "init", "-q"], cwd=self.projeto, check=True, env=env)
        (self.projeto / ".forge").mkdir()
        (self.projeto / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        proc = self.projeto / "proc"
        proc.mkdir()
        (proc / "loadavg").write_text("0.1 0.1 0.1\n", encoding="utf-8")
        (proc / "meminfo").write_text(f"MemTotal: {16 * 1024 * 1024} kB\nMemFree: 1 kB\nMemAvailable: {8 * 1024 * 1024} kB\n",
                                      encoding="utf-8")
        self.proc = proc
        self.conteudo = b"# brief\ncorpo do brief\n"
        self.arquivo = self.gravar("docs/briefs/p-x-1.md", self.conteudo)

    def gravar(self, relativo, conteudo, base=None):
        caminho = (base or self.projeto) / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(conteudo)
        return caminho

    def mensagem(self, arquivo="docs/briefs/p-x-1.md", sha=None, modo="modo: brief", extra_no_cabecalho=(), corpo="corpo"):
        sha = hashlib.sha256(self.conteudo).hexdigest() if sha is None else sha
        linhas = [modo, "Pedido: docs/pedidos/p.md   Agente destino: forge:x   Etapa: -", f"Arquivo: {arquivo}",
                  f"Brief-sha256: {sha}   Bytes: {len(self.conteudo)}", *extra_no_cabecalho]
        return "\n".join(linhas) + f"\n<<<BRIEF\n{corpo}\nBRIEF>>>\n"

    def lancar(self, prompt, tipo="forge:conferente", home=None):
        self.chamadas = getattr(self, "chamadas", 0) + 1  # descrição única: a mesma duas vezes seria o duplicado do R-TETO
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(self.projeto),
                   "tool_input": {"subagent_type": tipo, "description": f"d{self.chamadas}", "prompt": prompt}}
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, FORGE_PROC=str(self.proc), FORGE_NPROC="8",
                   HOME=str(home or self.home))
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / "agentes.py"), PRAZO_GIT],
                              input=json.dumps(entrada), cwd=self.projeto, env=sem_manutencao(env), capture_output=True,
                              text=True, timeout=120)

    def recusado(self, prompt, trecho="R-BRIEF"):
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(trecho, r.stderr)
        self.assertIn("forge-check brief mensagem", r.stderr)
        return r

    def aceito(self, prompt, **kw):
        r = self.lancar(prompt, **kw)
        self.assertEqual(r.returncode, 0, r.stderr)

    # O caminho feliz e o hash ---------------------------------------------------------------
    def test_hash_do_arquivo_passa_relativo_e_absoluto(self):
        self.aceito(self.mensagem())
        self.aceito(self.mensagem(arquivo=str(self.arquivo)))

    def test_hash_diferente_do_arquivo_bloqueia(self):
        r = self.recusado(self.mensagem(sha="a" * 64))
        self.assertIn("hash do brief não bate", r.stderr)

    def test_brief_editado_depois_de_gerar_a_mensagem_bloqueia(self):
        mensagem = self.mensagem()
        self.arquivo.write_bytes(self.conteudo + b"linha nova\n")
        self.recusado(mensagem)

    def test_mensagem_de_entrega_tambem_confere_o_hash(self):
        self.aceito(self.mensagem(modo="modo: entrega"))
        self.recusado(self.mensagem(modo="modo: entrega", sha="b" * 64))

    def test_outro_agente_nao_e_conferido(self):
        self.aceito(self.mensagem(sha="a" * 64), tipo="forge:tech-lead")

    # Caminho -----------------------------------------------------------------------------
    def test_arquivo_inexistente_bloqueia(self):
        self.recusado(self.mensagem(arquivo="docs/briefs/nao-existe.md"))

    def test_atalho_de_docs_briefs_para_fora_bloqueia(self):
        fora = self.gravar("segredo.txt", self.conteudo)
        (self.projeto / "docs" / "briefs" / "atalho.md").symlink_to(fora)
        self.recusado(self.mensagem(arquivo="docs/briefs/atalho.md"))

    def test_travessia_com_ponto_ponto_bloqueia(self):
        self.gravar("docs/pedidos/p.md", self.conteudo)
        self.recusado(self.mensagem(arquivo="docs/briefs/../pedidos/p.md"))

    def test_dispositivo_por_atalho_bloqueia(self):
        (self.projeto / "docs" / "briefs" / "dev.md").symlink_to("/dev/null")
        self.recusado(self.mensagem(arquivo="docs/briefs/dev.md", sha=hashlib.sha256(b"").hexdigest()))

    def test_arquivo_de_nome_com_espaco_passa(self):
        caminho = self.gravar("docs/briefs/meu brief.md", self.conteudo)
        self.aceito(self.mensagem(arquivo=str(caminho)))

    def test_raiz_de_brief_do_forge_contrib_vale(self):
        caminho = self.gravar(".forge-contrib/docs/briefs/q-y-1.md", self.conteudo, base=self.home)
        self.aceito(self.mensagem(arquivo=str(caminho)))
        self.recusado(self.mensagem(arquivo=str(caminho), sha="c" * 64))

    def test_docs_briefs_de_outra_pasta_nao_vale(self):
        fora = self.gravar("outro/docs/briefs/q-y-1.md", self.conteudo)
        self.recusado(self.mensagem(arquivo=str(fora)))

    # Cabeçalho ---------------------------------------------------------------------------
    def test_duas_linhas_arquivo_no_cabecalho_bloqueiam(self):
        self.recusado(self.mensagem(extra_no_cabecalho=["Arquivo: docs/briefs/p-x-1.md"]))

    def test_duas_linhas_de_hash_no_cabecalho_bloqueiam(self):
        self.recusado(self.mensagem(extra_no_cabecalho=["Brief-sha256: " + "d" * 64]))

    def test_arquivo_so_dentro_do_corpo_nao_conta(self):
        mensagem = f"modo: brief\nBrief-sha256: {hashlib.sha256(self.conteudo).hexdigest()}\n<<<BRIEF\nArquivo: docs/briefs/p-x-1.md\nBRIEF>>>\n"
        self.recusado(mensagem)

    def test_linha_arquivo_extra_no_corpo_nao_atrapalha(self):
        self.aceito(self.mensagem(corpo="Arquivo: docs/briefs/outro.md\nBrief-sha256: " + "e" * 64))

    def test_so_o_primeiro_bloco_e_conferido(self):
        """Mensagem de dois blocos (brief e entrega): vale o cabeçalho do primeiro; o Jarvis manda o brief sozinho."""
        self.aceito(self.mensagem() + "\n" + self.mensagem(arquivo="/abs/docs/briefs/q-y-2.md", sha="b" * 64))

    # Leitura limitada ----------------------------------------------------------------------
    def test_fifo_bloqueia_sem_travar(self):
        os.mkfifo(self.projeto / "docs" / "briefs" / "fila.md")
        inicio = time.monotonic()
        self.recusado(self.mensagem(arquivo="docs/briefs/fila.md", sha=hashlib.sha256(b"").hexdigest()))
        self.assertLess(time.monotonic() - inicio, 10)

    def test_arquivo_acima_de_256_kib_bloqueia_e_no_limite_passa(self):
        grande = b"x" * (TETO + 1)
        self.gravar("docs/briefs/grande.md", grande)
        self.recusado(self.mensagem(arquivo="docs/briefs/grande.md", sha=hashlib.sha256(grande).hexdigest()))
        limite = b"y" * TETO
        self.gravar("docs/briefs/limite.md", limite)
        self.aceito(self.mensagem(arquivo="docs/briefs/limite.md", sha=hashlib.sha256(limite).hexdigest()))


if __name__ == "__main__":
    unittest.main()
