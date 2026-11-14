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

    def lancar(self, onde, descricao="d", tipo="Explore", nproc=4):  # só de leitura: o selo (0.43.1, D2 da 0.44.0) é de test_selo_e_entrega
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

    def recusas(self):
        arq = self.comum / "recusas.log"
        return arq.read_text(encoding="utf-8").splitlines() if arq.exists() else []

    def test_recusa_do_teto_e_do_duplicado_deixa_linha_em_recusas_log(self):  # RN-6 (0.43.3)
        self.assertEqual(self.lancar(self.clone, descricao="segredo-da-descricao").returncode, 0)
        self.assertEqual(self.lancar(self.clone, descricao="segredo-da-descricao").returncode, 2)
        self.semear(2)
        self.assertEqual(self.lancar(self.clone, nproc=2).returncode, 2)
        linhas = self.recusas()
        self.assertEqual(len(linhas), 2, linhas)
        self.assertRegex(linhas[0], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} agentes R-TETO mem_gb=- nproc=- ativos=1 motivo=duplicado$")
        self.assertRegex(linhas[1], r" agentes R-TETO mem_gb=8\.00 nproc=2 ativos=2 motivo=teto$")
        self.assertNotIn("segredo", "".join(linhas))  # nunca a descrição do disparo

    def test_recusa_por_memoria_e_registrada_e_liberacao_nao(self):  # RN-6 (0.43.3)
        self.assertEqual(self.lancar(self.clone).returncode, 0)
        self.assertEqual(self.recusas(), [])
        pasta = self.tmp / "pouca"
        pasta.mkdir()
        entrada = {"hook_event_name": "PreToolUse", "session_id": "s", "cwd": str(self.clone), "tool_name": "Agent",
                   "tool_input": {"subagent_type": "Explore", "description": "outra", "prompt": "p"}}
        r = rodar_hook("agentes", entrada, self.clone, montar_proc(pasta, mem_gb=0.5), {"FORGE_NPROC": "4"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertRegex(self.recusas()[-1], r" mem_gb=0\.50 nproc=4 ativos=1 motivo=memoria$")

    def test_recusas_log_que_e_link_nao_e_seguido_e_a_recusa_segue(self):  # RN-6: O_NOFOLLOW, falha calada
        self.semear(2)
        alvo = self.tmp / "alvo.txt"
        alvo.write_text("", encoding="utf-8")
        (self.comum / "recusas.log").symlink_to(alvo)
        r = self.lancar(self.clone, nproc=2)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "")

    def test_estado_ilegivel_no_clone_recusa_e_deixa_linha_no_erros_log(self):
        """HOOK-ESTADO-ILEGIVEL-LIBERA (A1): no clone, o agentes.json ilegível recusa com R-TETO e fica como estava."""
        self.comum.mkdir(parents=True)
        self.estado.write_text("{truncado", encoding="utf-8")
        r = self.lancar(self.clone)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO: registro de agentes ilegível", r.stderr)
        self.assertEqual(self.estado.read_text(encoding="utf-8"), "{truncado")
        log = (self.comum / "erros.log").read_text(encoding="utf-8")
        self.assertIn("agentes EstadoIlegivel", log)

    def test_guarda_aberta_nao_abre_o_teto(self):
        """A15: o `agentes` segue sem `critico`; `FORGE_GUARDA_ABERTA=1` não libera o teto cheio."""
        self.semear(2)
        entrada = {"hook_event_name": "PreToolUse", "session_id": "s", "cwd": str(self.clone), "tool_name": "Agent",
                   "tool_input": {"subagent_type": "Explore", "description": "d", "prompt": "p"}}
        r = rodar_hook("agentes", entrada, self.clone, self.proc(2), {"FORGE_NPROC": "2", "FORGE_GUARDA_ABERTA": "1"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)


class EstadoDoCloneInerte(ClonePronto):
    """FORGE-RUN-INERTE (0.43.2, E2a do desenho da 0.60): com `.forge` arquivo na cópia principal do clone, o `Hook.run()` comum
    recua para `<diretório comum>/forge/run/`; antes o `mkdir` falhava e o `pesado` e o erros.log ficavam inertes."""

    SUITE = "python3 -m unittest discover"

    def pesado(self, onde, agente, uso, evento="PreToolUse"):
        entrada = {"hook_event_name": evento, "session_id": "s", "cwd": str(onde), "tool_name": "Bash", "agent_id": agente,
                   "tool_use_id": uso, "tool_input": {"command": self.SUITE}}
        return rodar_hook("pesado", entrada, onde, self.proc(4), {"FORGE_PESADO_ESPERA_S": "0"})  # 0.44.2: sem espera na fila, recusa na hora

    def test_suite_de_outro_agente_no_clone_e_na_worktree_bloqueia(self):
        self.assertEqual(self.pesado(self.clone, "a1", "u1").returncode, 0)
        self.assertTrue((self.comum / "pesado.json").is_file(), "o estado do pesado vai para o diretório comum")
        self.assertEqual(stat.S_IMODE(self.comum.stat().st_mode), 0o700)
        self.assertEqual((self.comum / ".gitignore").read_text(encoding="utf-8"), "*\n")
        r = self.pesado(self.wt, "a2", "u2")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)
        recusas = (self.comum / "recusas.log").read_text(encoding="utf-8").splitlines()  # RN-6 (0.43.3): a recusa do pesado também
        self.assertEqual(len(recusas), 1, recusas)
        self.assertRegex(recusas[0], r" pesado R-TETO mem_gb=- nproc=- ativos=- motivo=pesado$")
        self.assertEqual(self.pesado(self.clone, "a1", "u1", "PostToolUse").returncode, 0)
        self.assertEqual(self.pesado(self.wt, "a2", "u3").returncode, 0)
        self.assertTrue((self.clone / ".forge").is_file(), "`.forge` do clone continua sendo o arquivo")

    def test_erro_interno_vai_para_o_erros_log_comum(self):
        self.comum.mkdir(parents=True, exist_ok=True)
        (self.comum / "pesado.json").write_text("{truncado", encoding="utf-8")
        self.assertEqual(self.pesado(self.wt, "a1", "u1").returncode, 0)  # erro interno libera (ADR 0003)
        self.assertIn("pesado JSONDecodeError", (self.comum / "erros.log").read_text(encoding="utf-8"))

    def test_forge_pasta_continua_com_o_estado_em_forge_run(self):
        (self.clone / ".forge").chmod(0o644)
        (self.clone / ".forge").unlink()
        (self.clone / ".forge").mkdir()
        self.assertEqual(self.pesado(self.wt, "a1", "u1").returncode, 0)
        self.assertTrue((self.clone / ".forge" / "run" / "pesado.json").is_file())
        self.assertFalse((self.comum / "pesado.json").exists())


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
