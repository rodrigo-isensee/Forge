"""AGT-1 (R-TETO, FILA-ATIVOS-FORGE): o hook `agentes` registra e confere o teto também no clone do Forge e nas worktrees
dele, com o estado em `<diretório comum>/forge/run/` (no clone, `.forge` é um arquivo, não uma pasta)."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

# Sem importar test_hooks nem test_forge: quem os importa passa a executar o forge-check e entra no mapa FORGE_CHECK.
HOOKS = Path(__file__).resolve().parent.parent / "hooks"
PRAZO_GIT = "120"  # o git dos hooks tem 5 s em produção; com a suíte em paralelo a máquina carregada passaria disso
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; "
            "_comum.forge_check().GIT_TIMEOUT_S = int(sys.argv[3]); "
            "sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")


def montar_proc(pasta, load="0.1 0.1 0.1", mem_gb=8):
    """/proc simulado em `pasta/proc` (FORGE_PROC)."""
    proc = pasta / "proc"
    proc.mkdir()
    (proc / "loadavg").write_text(load + "\n", encoding="utf-8")
    (proc / "meminfo").write_text(f"MemTotal:       {16 * 1024 * 1024} kB\nMemFree:  1 kB\n"
                                  f"MemAvailable:   {int(mem_gb * 1024 * 1024)} kB\n", encoding="utf-8")
    return proc


def rodar_hook(nome, entrada, cwd, proc, extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, FORGE_PROC=str(proc), **(extra or {}))
    return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / f"{nome}.py"), PRAZO_GIT],
                          input=json.dumps(entrada), cwd=cwd, env=sem_manutencao(env), capture_output=True, text=True,
                          timeout=120)


def git(*args, cwd):
    env = sem_manutencao(dict(os.environ, HOME=str(cwd)))
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env, timeout=60)


class ClonePronto(unittest.TestCase):
    """O clone temporário tem o manifesto do Forge, `.forge` como arquivo vazio de modo 0444 e uma worktree."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-agt1-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.clone, self.wt = self.tmp / "clone", self.tmp / "wt" / "x"
        (self.clone / ".claude-plugin").mkdir(parents=True)
        (self.clone / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=self.clone)
        git("config", "user.email", "t@example.com", cwd=self.clone)
        git("config", "user.name", "Teste", cwd=self.clone)
        git("add", "-A", cwd=self.clone)
        git("commit", "-q", "-m", "base", cwd=self.clone)
        git("worktree", "add", "-q", "-b", "melhoria/x", str(self.wt), cwd=self.clone)
        (self.clone / ".forge").write_text("", encoding="utf-8")
        (self.clone / ".forge").chmod(0o444)
        self.comum = self.clone / ".git" / "forge" / "run"
        self.estado = self.comum / "agentes.json"

    def proc(self, nproc):
        pasta = self.tmp / f"proc{nproc}"
        pasta.mkdir(exist_ok=True)
        return pasta / "proc" if (pasta / "proc").exists() else montar_proc(pasta)

    def evento(self, nome, onde, nproc=4, **campos):
        entrada = {"hook_event_name": nome, "session_id": "s", "cwd": str(onde), **campos}
        return rodar_hook("agentes", entrada, onde, self.proc(nproc), {"FORGE_NPROC": str(nproc)})

    def lancar(self, onde, descricao="d", tipo="forge:x", nproc=4):
        return self.evento("PreToolUse", onde, nproc, tool_name="Agent",
                           tool_input={"subagent_type": tipo, "description": descricao, "prompt": "p"})

    def semear(self, quantos):
        self.comum.mkdir(parents=True, exist_ok=True)
        agentes = [{"id": f"a{i}", "tipo": "forge:y", "descricao": f"s{i}", "desde": time.time()} for i in range(quantos)]
        self.estado.write_text(json.dumps({"agentes": agentes}), encoding="utf-8")

    def registrados(self):
        return json.loads(self.estado.read_text(encoding="utf-8"))["agentes"]



class RegistroNoClone(ClonePronto):
    def test_teto_cheio_no_clone_bloqueia(self):
        self.semear(2)
        r = self.lancar(self.clone, nproc=2)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)

    def test_teto_cheio_na_worktree_bloqueia(self):
        self.semear(2)
        r = self.lancar(self.wt, nproc=2)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)

    def test_abaixo_do_teto_grava_a_reserva_no_diretorio_comum(self):
        r = self.lancar(self.clone)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([a["descricao"] for a in self.registrados()], ["d"])
        self.assertTrue((self.clone / ".forge").is_file(), "`.forge` do clone continua sendo o arquivo")
        self.assertFalse((self.wt / ".forge").exists())

    def test_pasta_de_estado_e_privada_e_ignorada(self):
        self.lancar(self.clone)
        self.assertEqual(stat.S_IMODE(self.comum.stat().st_mode), 0o700)
        self.assertEqual((self.comum / ".gitignore").read_text(encoding="utf-8"), "*\n")

    def test_worktree_e_clone_principal_somam_no_mesmo_registro(self):
        self.assertEqual(self.lancar(self.wt, descricao="da-worktree").returncode, 0)
        r = self.evento("SubagentStart", self.clone, agent_id="id1", agent_type="forge:x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([(a["id"], a["descricao"]) for a in self.registrados()], [("id1", "da-worktree")])
        r = self.evento("SubagentStop", self.clone, agent_id="id1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.registrados(), [])

    def test_mesma_descricao_no_clone_e_duplicado(self):
        self.assertEqual(self.lancar(self.clone, descricao="igual").returncode, 0)
        r = self.lancar(self.wt, descricao="igual")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("já há um agente", r.stderr)

    def test_erro_interno_no_clone_deixa_linha_no_erros_log(self):
        self.comum.mkdir(parents=True)
        self.estado.write_text("{truncado", encoding="utf-8")
        r = self.lancar(self.clone)
        self.assertEqual(r.returncode, 0, r.stderr)  # erro interno libera (ADR 0003), sem `critico`
        log = (self.comum / "erros.log").read_text(encoding="utf-8")
        self.assertIn("agentes JSONDecodeError", log)

    def test_guarda_aberta_nao_abre_o_teto(self):
        """A15: o `agentes` segue sem `critico`; `FORGE_GUARDA_ABERTA=1` não libera o teto cheio."""
        self.semear(2)
        entrada = {"hook_event_name": "PreToolUse", "session_id": "s", "cwd": str(self.clone), "tool_name": "Agent",
                   "tool_input": {"subagent_type": "forge:x", "description": "d", "prompt": "p"}}
        r = rodar_hook("agentes", entrada, self.clone, self.proc(2), {"FORGE_NPROC": "2", "FORGE_GUARDA_ABERTA": "1"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)


class ArquivoDeEstado(ClonePronto):
    """`agentes.arquivo_de_estado(raiz)`: o caminho que o hook usa, para projeto e para clone; o `forge-check fila` o lê."""

    def setUp(self):
        super().setUp()
        sys.path.insert(0, str(HOOKS))
        self.addCleanup(sys.path.remove, str(HOOKS))
        import agentes
        self.agentes = agentes
        self.projeto = self.tmp / "proj"
        (self.projeto / ".forge").mkdir(parents=True)
        (self.projeto / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=self.projeto)

    def test_clone_e_worktree_apontam_para_o_diretorio_comum(self):
        for raiz in (self.clone, self.wt):
            with self.subTest(raiz=raiz.name):
                self.assertEqual(self.agentes.arquivo_de_estado(raiz), self.estado)

    def test_projeto_aponta_para_forge_run_da_copia_principal(self):
        self.assertEqual(self.agentes.arquivo_de_estado(self.projeto), self.projeto / ".forge" / "run" / "agentes.json")

    def test_forge_check_conta_os_agentes_do_clone_e_da_worktree(self):
        import _comum
        modulo = _comum.forge_check()
        self.semear(2)
        for raiz in (self.clone, self.wt):
            with self.subTest(raiz=raiz.name):
                self.assertEqual(modulo.agentes_vigentes(raiz), 2)


if __name__ == "__main__":
    unittest.main()
