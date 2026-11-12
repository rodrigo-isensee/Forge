"""Primeiro uso (F3): `forge doutor` e o hook `doutor` (ADR 0003), com HOME, git e `gh` falsos, sem rede.

O projeto de partida está em ordem; cada teste estraga uma coisa e confere o aviso em linguagem simples.
"""
import json
import os
import pty
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import SINAIS_DE_CUSTO, remoto_sem_manutencao, sem_manutencao  # noqa: E402
import apoio_versao_defasada as ap  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DOUTOR = RAIZ / "bin" / "forge-doutor"
HOOK = RAIZ / "hooks" / "doutor.py"
VERSAO = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
HOJE = "2026-10-13"

# `gh` falso: registra o argv e responde por endpoint. Por padrão as três branches estão protegidas; um teste troca a resposta gravando
# `gh-<nome>` (o texto; vai ao stdout se a saída é 0, senão ao stderr) e `gh-<nome>.rc` (o código), com nome `repo`, `regras-<branch>` ou `protecao-<branch>`.
GH_FALSO = r"""#!/usr/bin/env bash
echo "$*" >> "@LOG@"
H="@HOME@"
[ -e "$H/gh-sem-login" ] && { echo "not logged in" >&2; exit 1; }
responder() {  # nome, stdout padrão, código padrão, stderr padrão
  if [ -e "$H/gh-$1" ]; then
    rc=0; [ -e "$H/gh-$1.rc" ] && rc=$(cat "$H/gh-$1.rc")
    if [ "$rc" = 0 ]; then cat "$H/gh-$1"; else cat "$H/gh-$1" >&2; fi
    exit "$rc"
  fi
  [ -n "$4" ] && echo "$4" >&2
  printf '%s' "$2"; exit "$3"
}
if [ "$1 $2" = "auth status" ]; then
  responder auth '' 0
fi
if [ "$1 $2" = "repo view" ]; then
  responder repo '{"nameWithOwner":"dono/proj","url":"https://github.com/dono/proj"}' 0
fi
ep=""; for a in "$@"; do case "$a" in repos/*) ep="$a";; esac; done
case "$ep" in
  */rules/branches/*) responder "regras-${ep##*/}" '[{"type":"pull_request"},{"type":"required_status_checks"}]' 0 ;;
  */branches/*/protection) b="${ep%/protection}"; responder "protecao-${b##*/}" '' 1 "gh: Branch not protected (HTTP 404)" ;;
esac
exit 0
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="doutor-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home = self.tmp / "home"
        self.bin = self.tmp / "bin"
        self.home.mkdir()
        self.bin.mkdir()
        self.gh_log = self.tmp / "gh.log"
        (self.bin / "gh").write_text(GH_FALSO.replace("@LOG@", str(self.gh_log)).replace("@HOME@", str(self.home)), encoding="utf-8")
        (self.bin / "gh").chmod(0o755)
        self.gitconfig = self.home / "gitconfig"
        self.gitconfig.write_text("[user]\n\tname = Pessoa Teste\n\temail = pessoa@exemplo.test\n", encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CLAUDE_PROJECT_DIR"
                    and k not in SINAIS_DE_CUSTO}
        self.env.update(HOME=str(self.home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.gitconfig),
                        PATH=f"{self.bin}:{os.environ['PATH']}", FORGE_HOJE=HOJE, FORGE_VERIFICAR_VERSAO="0")
        self.env.pop("XDG_STATE_HOME", None)
        self.env.pop("CLAUDE_ENV_FILE", None)  # E18.1: o arquivo de ambiente da sessão de quem roda os testes nunca é tocado
        self.env = sem_manutencao(self.env)
        self.remoto = self.tmp / "remoto.git"
        self.proj = self.tmp / "proj"
        self.git("init", "-q", "--bare", "-b", "main", str(self.remoto), cwd=self.tmp)
        remoto_sem_manutencao(self.remoto)
        self.git("clone", "-q", str(self.remoto), str(self.proj), cwd=self.tmp)
        self.escrever(".forge/versao", VERSAO + "\n")
        self.escrever(".claude/settings.json", json.dumps({"agent": "forge:jarvis", "enabledPlugins": {"forge@forge": True}}))
        self.escrever(".githooks/pre-push", "#!/bin/sh\nexit 0\n")
        (self.proj / ".githooks" / "pre-push").chmod(0o755)
        self.escrever(".gitignore", ".forge/run/\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: inicio")
        self.git("push", "-q", "origin", "main")
        for ramo in ("develop", "homolog"):
            self.git("branch", ramo)
            self.git("push", "-q", "origin", ramo)
        self.git("config", "core.hooksPath", ".githooks")
        self.escrever_home(".claude/plugins/installed_plugins.json",
                           json.dumps({"version": 2, "plugins": {"forge@forge": [{"scope": "user", "version": VERSAO}]}}))
        self.escrever_home(".claude/settings.json", json.dumps({"sandbox": {"enabled": True}}))

    def git(self, *args, cwd=None):
        r = subprocess.run(["git", *args], cwd=cwd or self.proj, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def escrever(self, rel, texto):
        arq = self.proj / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def escrever_home(self, rel, texto):
        arq = self.home / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def doutor(self, *args, cwd=None, env=None):
        return subprocess.run([sys.executable, str(DOUTOR), *args], env=env or self.env, cwd=cwd or self.proj,
                              capture_output=True, text=True, timeout=60)

    def doutor_tty(self, resposta, *args):
        """Roda o doutor num terminal de verdade (pty), respondendo `resposta` à pergunta."""
        mestre, escravo = pty.openpty()
        os.write(mestre, resposta.encode())
        p = subprocess.Popen([sys.executable, str(DOUTOR), *args], env=self.env, cwd=self.proj, stdin=escravo,
                             stdout=escravo, stderr=escravo, close_fds=True)
        os.close(escravo)
        saida = b""
        limite = time.time() + 30
        while time.time() < limite:
            try:
                bloco = os.read(mestre, 4096)
            except OSError:
                break
            if not bloco:
                break
            saida += bloco
        p.wait(timeout=30)
        os.close(mestre)
        return p.returncode, saida.decode("utf-8", "replace")


class Diagnostico(Base):
    def test_tudo_em_ordem_fica_em_silencio(self):
        for args in ((), ("--rapido",)):
            r = self.doutor(*args)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), args)

    def test_detalhado_diz_que_esta_tudo_bem_em_uma_linha(self):
        r = self.doutor("-v")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(len(r.stdout.strip().splitlines()), 1)
        self.assertIn(VERSAO, r.stdout)

    def test_fora_de_projeto_do_forge_nao_diz_nada(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        r = self.doutor(cwd=fora)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_plugin_nao_instalado(self):
        (self.home / ".claude/plugins/installed_plugins.json").write_text('{"plugins": {}}', encoding="utf-8")
        self.escrever(".claude/settings.json", json.dumps({"agent": "forge:jarvis"}))
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("plugin do Forge não está instalado", r.stdout)

    def test_projeto_sem_versao(self):
        (self.proj / ".forge/versao").unlink()
        r = self.doutor(cwd=self.proj)  # sem .forge/versao não é projeto do Forge: nada a dizer
        self.assertEqual(r.stdout, "")
        self.escrever(".forge/versao", "lixo\n")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn(".forge/versao", r.stdout)

    def test_projeto_na_versao_antiga_manda_atualizar_o_projeto(self):
        self.escrever(".forge/versao", "0.0.1\n")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("0.0.1", r.stdout)
        self.assertIn("forge-upgrade", r.stdout)

    def test_projeto_na_versao_mais_nova_que_o_plugin(self):
        self.escrever(".forge/versao", "99.0.0\n")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("99.0.0", r.stdout)
        self.assertIn("plugin", r.stdout)

    def test_hooks_do_git_desligados(self):
        self.git("config", "--unset", "core.hooksPath")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("proteção do git", r.stdout)

    def test_hook_do_git_sem_permissao_de_execucao(self):
        (self.proj / ".githooks/pre-push").chmod(0o644)
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("pre-push", r.stdout)

    def test_gh_sem_login_so_no_modo_completo(self):
        (self.home / "gh-sem-login").write_text("", encoding="utf-8")
        self.assertEqual(self.doutor("--rapido").stdout, "")
        self.assertFalse(self.gh_log.exists() and self.gh_log.read_text(), "o modo rápido não chama o gh")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("gh auth login", r.stdout)

    def escopos(self, linha):
        (self.home / "gh-auth").write_text("github.com\n  ✓ Logged in to github.com account pessoa (keyring)\n" + linha + "\n",
                                           encoding="utf-8")

    def test_gh_sem_escopo_workflow_diz_como_corrigir(self):
        self.escopos("  - Token scopes: 'gist', 'read:org', 'repo'")
        self.assertEqual(self.doutor("--rapido").stdout, "", "o modo rápido não chama o gh")
        r = self.doutor()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("não tem a permissão `workflow`", r.stdout)
        self.assertIn("gh auth refresh -h github.com -s repo,workflow", r.stdout)

    def test_gh_sem_repo_nem_workflow(self):
        self.escopos("  - Token scopes: 'gist', 'read:org'")
        r = self.doutor()
        self.assertIn("não tem a permissão `repo` nem a `workflow`", r.stdout)

    def test_gh_com_os_escopos_ou_sem_a_linha_fica_em_silencio(self):
        for linha in ("  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'", "  - Token: gho_****"):
            with self.subTest(linha=linha):
                self.escopos(linha)
                r = self.doutor()
                self.assertNotIn("permissão", r.stdout)

    def test_gh_ausente(self):
        sem_gh = self.tmp / "sem-gh"
        sem_gh.mkdir()
        for nome in ("git", "python3"):
            (sem_gh / nome).symlink_to(shutil.which(nome))
        env = {**self.env, "PATH": str(sem_gh)}
        r = self.doutor(env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("gh", r.stdout)
        self.assertIn("instale", r.stdout)

    def test_identidade_do_git(self):
        self.gitconfig.write_text("", encoding="utf-8")
        r = self.doutor("--rapido")
        self.assertEqual(r.returncode, 1)
        self.assertIn("nome", r.stdout)
        self.assertIn("e-mail", r.stdout)
        self.assertIn("git config --global user.name", r.stdout)

    def test_settings_sem_o_jarvis(self):
        self.escrever(".claude/settings.json", json.dumps({"enabledPlugins": {"forge@forge": True}}))
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Jarvis", r.stdout)

    def test_settings_ausente_ou_invalido(self):
        self.escrever(".claude/settings.json", "{ quebrado")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn(".claude/settings.json", r.stdout)
        self.assertEqual((self.proj / ".claude/settings.json").read_text(encoding="utf-8"), "{ quebrado")

    def test_sandbox_desligado(self):
        self.escrever_home(".claude/settings.json", "{}")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("sandbox", r.stdout)
        self.assertIn("/sandbox", r.stdout)

    def test_sandbox_ligado_no_projeto_basta(self):
        self.escrever_home(".claude/settings.json", "{}")
        self.escrever(".claude/settings.json", json.dumps({"agent": "forge:jarvis", "sandbox": {"enabled": True},
                                                           "enabledPlugins": {"forge@forge": True}}))
        self.assertEqual(self.doutor().stdout, "")

    def test_falta_a_branch_homolog(self):
        self.git("branch", "-D", "homolog")
        self.git("push", "-q", "origin", "--delete", "homolog")
        self.git("update-ref", "-d", "refs/remotes/origin/homolog")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("homolog", r.stdout)
        self.assertNotIn("develop", r.stdout)

    def test_varios_problemas_viram_lista_com_cabecalho(self):
        self.git("config", "--unset", "core.hooksPath")
        self.escrever(".forge/versao", "0.0.1\n")
        r = self.doutor()
        linhas = r.stdout.strip().splitlines()
        self.assertIn("2", linhas[0])
        self.assertEqual(len([x for x in linhas if x.startswith("- ")]), 2)

    def test_linguagem_simples_sem_jargao_de_codigo(self):
        self.git("config", "--unset", "core.hooksPath")
        self.assertNotIn("Traceback", self.doutor().stdout + self.doutor().stderr)

    def test_modo_rapido_nao_usa_rede(self):
        self.git("config", "--unset", "core.hooksPath")
        self.doutor("--rapido")
        self.assertFalse(self.gh_log.exists() and self.gh_log.read_text())


class PythonMinimo(Base):
    """E21 da 0.75: o doutor avisa Python abaixo do mínimo, e o mínimo é o que o CI prova e o README declara."""

    def doutor_em(self, versao):
        """Roda o doutor com `sys.version_info` simulado em `versao` (o resto do Python é o de verdade)."""
        codigo = (f"import runpy, sys; sys.version_info = {versao!r}; sys.argv = [{str(DOUTOR)!r}, '--rapido']; "
                  f"runpy.run_path({str(DOUTOR)!r}, run_name='__main__')")
        return subprocess.run([sys.executable, "-I", "-c", codigo], env=self.env, cwd=self.proj,
                              capture_output=True, text=True, timeout=60)

    def minimo(self):
        from importlib.machinery import SourceFileLoader
        from importlib.util import module_from_spec, spec_from_loader
        spec = spec_from_loader("forge_doutor", SourceFileLoader("forge_doutor", str(DOUTOR)))
        modulo = module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo.PYTHON_MINIMO

    def test_python_abaixo_do_minimo_avisa(self):
        r = self.doutor_em((3, 11, 9, "final", 0))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("Python 3.11 abaixo do mínimo 3.12 do Forge", r.stdout)

    def test_python_no_minimo_fica_em_silencio(self):
        r = self.doutor_em((3, 12, 0, "final", 0))
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_minimo_e_o_menor_python_do_ci(self):
        versoes = set()
        for arquivo in (RAIZ / ".github/workflows/ci.yml", RAIZ / ".github/workflows/release.yml"):
            texto = arquivo.read_text(encoding="utf-8")
            versoes.update(tuple(int(n) for n in v.split(".")) for v in re.findall(r'python-version:\s*"(\d+\.\d+)"', texto))
        self.assertGreaterEqual(len(versoes), 2)  # 3.12 e 3.14: a leitura achou as baterias
        self.assertEqual(self.minimo(), min(versoes))

    def test_readme_declara_o_minimo(self):
        x, y = self.minimo()
        self.assertIn(f"Python {x}.{y} ou mais novo", (RAIZ / "README.md").read_text(encoding="utf-8"))


class Conserto(Base):
    def estrago(self):
        self.git("config", "--unset", "core.hooksPath")
        (self.proj / ".githooks/pre-push").chmod(0o644)

    def test_sem_terminal_nao_conserta_e_explica(self):
        self.estrago()
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("forge doutor", r.stdout)
        self.assertNotEqual(subprocess.run(["git", "config", "core.hooksPath"], cwd=self.proj, env=self.env,
                                           capture_output=True, text=True).stdout.strip(), ".githooks")
        self.assertFalse((self.proj / ".githooks/pre-push").stat().st_mode & 0o111)

    def test_rapido_nunca_conserta_nem_pergunta(self):
        self.estrago()
        codigo, saida = self.doutor_tty("s\n", "--rapido")
        self.assertEqual(codigo, 1)
        self.assertNotIn("[s/N]", saida)
        self.assertEqual(subprocess.run(["git", "config", "core.hooksPath"], cwd=self.proj, env=self.env,
                                        capture_output=True, text=True).stdout.strip(), "")

    def test_com_terminal_e_sim_conserta_as_protecoes_do_git(self):
        self.estrago()
        codigo, saida = self.doutor_tty("s\n")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.git("config", "core.hooksPath"), ".githooks")
        self.assertTrue((self.proj / ".githooks/pre-push").stat().st_mode & 0o100)
        self.assertEqual(self.doutor().stdout, "")  # idempotente: depois, silêncio

    def test_conserto_guarda_e_cita_o_core_hookspath_anterior(self):
        self.git("config", "core.hooksPath", "/outro/gerenciador")  # repositório temporário do teste
        codigo, saida = self.doutor_tty("s\n")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("/outro/gerenciador", saida)
        self.assertEqual(self.git("config", "core.hooksPath"), ".githooks")
        guardado = list(Path(self.home).rglob("core.hooksPath"))
        self.assertEqual([g.read_text().strip() for g in guardado], ["/outro/gerenciador"])

    def test_segundo_conserto_nao_sobrescreve_o_backup_com_githooks(self):
        self.git("config", "core.hooksPath", "/outro/gerenciador")
        self.assertEqual(self.doutor_tty("s\n")[0], 0)
        (self.proj / ".githooks/pre-push").chmod(0o644)  # agora só a permissão está errada; core.hooksPath já é .githooks
        self.assertEqual(self.doutor_tty("s\n")[0], 0)
        guardado = list(Path(self.home).rglob("core.hooksPath"))
        self.assertEqual([g.read_text().strip() for g in guardado], ["/outro/gerenciador"])

    def test_com_terminal_e_nao_nada_muda(self):
        self.estrago()
        codigo, saida = self.doutor_tty("n\n")
        self.assertEqual(codigo, 1, saida)
        self.assertEqual(subprocess.run(["git", "config", "core.hooksPath"], cwd=self.proj, env=self.env,
                                        capture_output=True, text=True).stdout.strip(), "")

    def test_enter_sozinho_conta_como_nao(self):
        self.estrago()
        codigo, _ = self.doutor_tty("\n")
        self.assertEqual(codigo, 1)
        self.assertFalse((self.proj / ".githooks/pre-push").stat().st_mode & 0o111)

    def test_restaura_o_jarvis_no_settings_com_copia_de_seguranca(self):
        antes = {"enabledPlugins": {"forge@forge": True}, "permissions": {"deny": ["Read(./.env)"]}}
        self.escrever(".claude/settings.json", json.dumps(antes))
        codigo, saida = self.doutor_tty("s\n")
        self.assertEqual(codigo, 0, saida)
        depois = json.loads((self.proj / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(depois["agent"], "forge:jarvis")
        self.assertEqual(depois["permissions"], antes["permissions"], "o resto do arquivo fica como estava")
        copias = list((self.home / ".local/state/forge/backup").rglob("settings.json"))
        self.assertEqual(len(copias), 1, saida)
        self.assertEqual(json.loads(copias[0].read_text(encoding="utf-8")), antes)
        self.assertIn("backup", saida.lower() + "backup")

    def test_settings_invalido_nao_e_consertado(self):
        self.escrever(".claude/settings.json", "{ quebrado")
        codigo, _ = self.doutor_tty("s\n")
        self.assertEqual(codigo, 1)
        self.assertEqual((self.proj / ".claude/settings.json").read_text(encoding="utf-8"), "{ quebrado")

    def test_cria_a_branch_local_que_so_existe_no_remoto(self):
        self.git("branch", "-D", "homolog")
        codigo, saida = self.doutor_tty("s\n")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("homolog", self.git("branch", "--list", "homolog"))
        self.assertEqual(self.git("rev-parse", "homolog"), self.git("rev-parse", "origin/homolog"))

    def test_o_que_nao_e_seguro_continua_na_lista(self):
        self.estrago()
        (self.home / "gh-sem-login").write_text("", encoding="utf-8")
        codigo, saida = self.doutor_tty("s\n")
        self.assertEqual(codigo, 1)
        self.assertIn("gh auth login", saida)
        self.assertEqual(self.git("config", "core.hooksPath"), ".githooks")

    def test_o_doutor_nao_usa_comandos_destrutivos(self):
        texto = DOUTOR.read_text(encoding="utf-8")
        for proibido in ("--force", "--no-verify", "reset --hard", "clean -f", "push"):
            self.assertNotIn(proibido, texto)


class HookDoutor(Base):
    def hook(self, evento, extra=None):
        entrada = {"hook_event_name": evento, "session_id": "s1", "cwd": str(self.proj), **(extra or {})}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=self.env, cwd=self.proj,
                              capture_output=True, text=True, timeout=30)

    def cache(self):
        arq = self.proj / ".forge/run/doutor"
        return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None

    def estrago(self):
        self.git("config", "--unset", "core.hooksPath")

    def test_ao_abrir_e_silencioso_mesmo_com_problema_e_grava_a_data(self):
        self.estrago()
        r = self.hook("SessionStart", {"source": "startup"})
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), "SessionStart não escreve (ADR 0003)")
        self.assertEqual(self.cache()["data"], HOJE)
        self.assertEqual(len(self.cache()["problemas"]), 1)

    def test_tudo_bem_nao_diz_nada_em_nenhum_evento(self):
        for evento in ("SessionStart", "Stop", "Stop"):
            r = self.hook(evento)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), evento)
        self.assertEqual(self.cache()["problemas"], [])

    def test_problema_vira_uma_linha_so_para_o_usuario_e_so_uma_vez(self):
        self.estrago()
        self.hook("SessionStart", {"source": "startup"})
        r = self.hook("Stop")
        saida = json.loads(r.stdout)
        self.assertEqual(list(saida), ["systemMessage"], "nunca additionalContext (ADR 0003)")
        self.assertNotIn("\n", saida["systemMessage"])
        self.assertLessEqual(len(saida["systemMessage"]), 200)
        self.assertTrue(saida["systemMessage"].startswith("Forge doutor: "))
        self.assertIn("forge doutor", saida["systemMessage"])
        self.assertEqual(self.hook("Stop").stdout, "", "já avisado hoje")

    def test_resume_e_compact_nao_reabrem_o_aviso_do_dia(self):
        self.estrago()
        self.hook("SessionStart", {"source": "startup"})
        self.assertNotEqual(self.hook("Stop").stdout, "")
        for origem in ("resume", "compact", "clear"):
            self.hook("SessionStart", {"source": origem})
            self.assertEqual(self.hook("Stop").stdout, "", origem)
        self.assertTrue(self.cache()["avisado"])

    def test_problema_novo_no_mesmo_dia_avisa_de_novo(self):
        self.estrago()
        self.hook("SessionStart", {"source": "startup"})
        self.hook("Stop")
        self.gitconfig.write_text("", encoding="utf-8")  # some a identidade do git: problema novo
        self.hook("SessionStart", {"source": "resume"})
        self.assertNotEqual(self.hook("Stop").stdout, "")

    def test_uma_vez_por_dia_o_cache_da_data_vale(self):
        self.hook("SessionStart", {"source": "startup"})  # hoje, tudo bem
        self.estrago()  # estraga depois: o cache de hoje manda, não reexamina
        self.assertEqual(self.hook("Stop").stdout, "")
        self.assertEqual(self.cache()["problemas"], [])

    def test_dia_novo_reexamina_e_avisa(self):
        self.hook("SessionStart", {"source": "startup"})
        self.estrago()
        (self.proj / ".forge/run/doutor").write_text(json.dumps({"data": "2026-10-12", "problemas": [], "avisado": False}),
                                                      encoding="utf-8")
        r = self.hook("Stop")
        self.assertIn("systemMessage", json.loads(r.stdout))
        self.assertEqual(self.cache()["data"], HOJE)
        self.assertEqual(self.hook("Stop").stdout, "")

    def test_cache_corrompido_reexamina(self):
        self.estrago()
        (self.proj / ".forge/run").mkdir(parents=True, exist_ok=True)
        (self.proj / ".forge/run/doutor").write_text("{", encoding="utf-8")
        self.assertIn("systemMessage", json.loads(self.hook("Stop").stdout))

    def test_fora_de_projeto_do_forge_nao_age(self):
        (self.proj / ".forge/versao").unlink()
        r = self.hook("SessionStart", {"source": "startup"})
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertFalse((self.proj / ".forge/run").exists())

    def test_o_hook_nao_chama_gh_nem_a_rede(self):
        (self.home / "gh-sem-login").write_text("", encoding="utf-8")
        self.hook("SessionStart", {"source": "startup"})
        self.assertEqual(self.hook("Stop").stdout, "")
        self.assertFalse(self.gh_log.exists() and self.gh_log.read_text())

    def test_hook_desligado_na_config(self):
        self.estrago()
        self.escrever(".forge/config.json", json.dumps({"hooks_desligados": ["doutor"]}))
        self.assertEqual(self.hook("Stop").stdout, "")

    def test_erro_interno_libera_e_registra(self):
        self.escrever(".forge/config.json", "{")
        r = self.hook("Stop")
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertIn("doutor JSONDecodeError", (self.proj / ".forge/run/erros.log").read_text(encoding="utf-8"))

    def test_abrir_em_menos_de_cem_ms_em_media(self):
        """O `Stop` com o cache de hoje só lê o arquivo: o custo próprio do hook (CPU dele e dos filhos, menos a subida
        do interpretador medida na mesma execução) fica abaixo de 0,25 s em média. Era 0,3 s de relógio, que a máquina
        carregada passava sem o hook mudar (P3 da 0.43.1): o relógio de um `python3` vazio vai de 0,09 a 0,39 s com
        carga, a CPU fica em 0,03 s; a do hook, em 0,10 s. O hook que espera a rede não gasta CPU: quem o pega é
        `test_o_hook_nao_chama_gh_nem_a_rede`."""
        self.hook("SessionStart", {"source": "startup"})
        vazio = self.cpu_media_dos_filhos(lambda: subprocess.run(
            [sys.executable, "-c", "import json, sys; json.load(sys.stdin)"], input="{}", env=self.env, cwd=self.proj,
            capture_output=True, text=True, timeout=30))
        hook = self.cpu_media_dos_filhos(lambda: self.hook("Stop"))  # com o cache de hoje: só lê o arquivo
        self.assertLess(hook - vazio, 0.25, f"CPU média: hook {hook:.3f} s, interpretador vazio {vazio:.3f} s")

    @staticmethod
    def cpu_media_dos_filhos(rodar, vezes=5):
        """Segundos de CPU (usuário + sistema) de `rodar()` em média, pelos filhos já esperados (`RUSAGE_CHILDREN`)."""
        def filhos():
            uso = resource.getrusage(resource.RUSAGE_CHILDREN)
            return uso.ru_utime + uso.ru_stime
        antes = filhos()
        for _ in range(vezes):
            rodar()
        return (filhos() - antes) / vezes

    def git_falso(self, quando, segundos):
        """Um `git` que demora `segundos` quando a linha de comando contém `quando`; o resto vai ao git de verdade."""
        real = shutil.which("git", path=os.environ["PATH"])
        (self.bin / "git").write_text(
            f'#!/usr/bin/env bash\ncase "$*" in *"{quando}"*) sleep {segundos};; esac\nexec {real} "$@"\n', encoding="utf-8")
        (self.bin / "git").chmod(0o755)

    def test_git_lento_demais_diz_que_nao_conseguiu_checar_e_nao_afirma_falsidade(self):
        for quando, falso in (("--list", ("proteção", "não sabe seu")), ("for-each-ref", ("não existe",))):
            with self.subTest(quando=quando):
                self.git_falso(quando, 6)
                self.hook("SessionStart")
                texto = " ".join(self.cache()["problemas"])
                self.assertIn("Não consegui checar o git", texto)
                for frase in falso:
                    self.assertNotIn(frase, texto)

    def test_duas_sessoes_no_stop_avisam_uma_vez_so(self):
        self.estrago()
        self.hook("SessionStart")  # cache de hoje com problema ainda não avisado
        # `hoje` lento alarga a janela entre ler o cache e gravar "avisado": quem decide fora da trava avisa em dobro
        codigo = ("import sys, time; sys.path.insert(0, sys.argv[1]); import doutor; h = doutor.hoje; "
                  "doutor.hoje = lambda: (time.sleep(0.4), h())[1]; doutor.executar('doutor', doutor.principal)")
        entrada = json.dumps({"hook_event_name": "Stop", "session_id": "s", "cwd": str(self.proj)})
        procs = [subprocess.Popen([sys.executable, "-c", codigo, str(HOOK.parent)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, env=self.env, cwd=self.proj) for _ in range(2)]
        for p in procs:  # as duas recebem a entrada antes de qualquer uma terminar
            p.stdin.write(entrada)
            p.stdin.close()
        saidas = [p.stdout.read() for p in procs]
        for p in procs:
            p.wait(timeout=30)
        self.assertEqual(len([o for o in saidas if o.strip()]), 1, saidas)

    def test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop(self):
        d = json.loads((RAIZ / "hooks/hooks.json").read_text(encoding="utf-8"))
        for evento in ("SessionStart", "Stop"):
            comandos = {h["args"][0].rsplit("/", 1)[-1] for g in d["hooks"][evento] for h in g["hooks"]}
            self.assertIn("doutor.py", comandos, evento)
        self.assertNotIn("UserPromptSubmit", d["hooks"], "o stdout dele viraria contexto (ADR 0003)")


class CaminhosNaSessao(Base):
    """E18.1 (0.45.7): no SessionStart o doutor põe as pastas de `caminhos_extra` no fim do PATH da sessão (`CLAUDE_ENV_FILE`)."""

    def setUp(self):
        super().setUp()
        self.arquivo_env = self.tmp / "sessao.env"
        self.pasta = self.tmp / "fer ra'mentas"  # espaço e aspa: a linha precisa sair citada
        self.pasta.mkdir()
        self.pasta.chmod(0o755)
        self.cache = self.proj / ".forge" / "run" / "doutor"

    def config(self, *pastas):
        self.escrever(".forge/config.json", json.dumps({"caminhos_extra": [str(p) for p in pastas]}))

    def abrir(self, com_arquivo=True):
        env = dict(self.env, **({"CLAUDE_ENV_FILE": str(self.arquivo_env)} if com_arquivo else {}))
        entrada = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.proj), "source": "startup"}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def erros(self):
        log = self.proj / ".forge" / "run" / "erros.log"
        return log.read_text(encoding="utf-8") if log.exists() else ""

    def path_da_sessao(self):
        r = subprocess.run(["bash", "--noprofile", "--norc", "-c", '. "$1"; printf %s "$PATH"', "_", str(self.arquivo_env)],
                           env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_pasta_boa_vai_ao_fim_do_path(self):
        self.config(self.pasta)
        self.abrir()
        self.assertEqual(self.path_da_sessao(), f"/usr/bin:/bin:{self.pasta}")
        self.assertTrue(self.cache.exists(), "o diagnóstico segue depois")

    def test_pasta_que_nao_passa_fica_de_fora_com_aviso_e_nada_se_grava(self):
        aberta = self.tmp / "aberta"
        aberta.mkdir()
        aberta.chmod(0o777)
        self.config(aberta, "relativa")
        self.abrir()
        self.assertFalse(self.arquivo_env.exists(), "sem pasta boa, o arquivo de ambiente não muda")
        self.assertIn("ignorada (precisa ser do usuário", self.erros())
        self.assertIn("ignorada (precisa ser caminho absoluto", self.erros())

    def test_sem_arquivo_de_ambiente_nada_muda_e_o_diagnostico_segue(self):
        self.config(self.pasta)
        self.abrir(com_arquivo=False)
        self.assertEqual(self.erros(), "")
        self.assertTrue(self.cache.exists())

    def test_resume_e_compact_nao_repetem_a_linha(self):
        self.config(self.pasta)
        for _ in range(3):
            self.abrir()
        self.assertEqual(len(self.arquivo_env.read_text(encoding="utf-8").splitlines()), 1)

    def test_arquivo_sem_quebra_no_fim_ganha_linha_propria(self):
        self.arquivo_env.write_text("export A=1", encoding="utf-8")
        self.config(self.pasta)
        self.abrir()
        linhas = self.arquivo_env.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[0], "export A=1")
        self.assertEqual(self.path_da_sessao(), f"/usr/bin:/bin:{self.pasta}")


class Frequencia(Base):
    """Antes de abrir o Jarvis, antes de atualizar o projeto e antes de abrir PR."""

    def test_atalho_jarvis_roda_o_doutor_antes_do_claude(self):
        cache = self.home / ".claude/plugins/cache/forge/forge/9.9.9/bin"
        cache.mkdir(parents=True)
        (cache / "forge-doutor").write_text(f'#!/usr/bin/env bash\necho doutor >> {self.tmp}/ordem\n', encoding="utf-8")
        (cache / "forge-doutor").chmod(0o755)
        (self.bin / "claude").write_text(f'#!/usr/bin/env bash\n[ "$1" = plugin ] || echo claude >> {self.tmp}/ordem\n', encoding="utf-8")
        (self.bin / "claude").chmod(0o755)
        r = subprocess.run(["bash", str(RAIZ / "scripts/jarvis"), "--sem-tmux"], env=self.env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.tmp / "ordem").read_text(encoding="utf-8").split(), ["doutor", "claude"])

    def test_atalho_sem_o_plugin_instalado_abre_o_jarvis_do_mesmo_jeito(self):
        (self.bin / "claude").write_text(f'#!/usr/bin/env bash\n[ "$1" = plugin ] || echo claude >> {self.tmp}/ordem\n', encoding="utf-8")
        (self.bin / "claude").chmod(0o755)
        r = subprocess.run(["bash", str(RAIZ / "scripts/jarvis"), "--sem-tmux"], env=self.env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.tmp / "ordem").read_text(encoding="utf-8").split(), ["claude"])

    def test_forge_upgrade_chama_o_doutor_antes_de_atualizar(self):
        texto = (RAIZ / "bin/forge-upgrade").read_text(encoding="utf-8")
        self.assertIn("forge-doutor", texto)

    def test_doutor_e_subcomando_do_forge(self):
        r = subprocess.run(["bash", str(RAIZ / "bin/forge"), "doutor", "--rapido"], env=self.env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertIn("doutor", subprocess.run(["bash", str(RAIZ / "bin/forge")], env=self.env, capture_output=True,
                                               text=True).stdout)

    def test_o_tech_lead_roda_o_doutor_antes_de_abrir_pr(self):
        texto = (RAIZ / "agents/tech-lead.md").read_text(encoding="utf-8")
        self.assertIn("forge doutor --rapido", texto)


class CacheDoPlugin(unittest.TestCase):
    """M11: só saem do cache as versões antigas do Forge fora de todo installPath, nunca as duas maiores nem atalho."""
    def setUp(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        import forge_versoes
        self.fv = forge_versoes
        self.casa = Path(tempfile.mkdtemp(prefix="cache-"))
        self.addCleanup(shutil.rmtree, self.casa, ignore_errors=True)
        self.forge = self.casa / ".claude" / "plugins" / "cache" / "mkt" / "forge"
        for v in ("0.40.0", "0.41.0", "0.42.0", "0.43.0"):
            self.versao(v)
        self.instalados(["0.41.0"])

    def versao(self, v, nome="forge"):
        pasta = self.forge / v / ".claude-plugin"
        pasta.mkdir(parents=True)
        (pasta / "plugin.json").write_text(json.dumps({"name": nome, "version": v}), encoding="utf-8")

    def instalados(self, versoes):
        dados = {"version": 2, "plugins": {"forge@mkt": [{"installPath": str(self.forge / v)} for v in versoes]}}
        (self.casa / ".claude" / "plugins" / "installed_plugins.json").write_text(json.dumps(dados), encoding="utf-8")

    def sem_erro(self, funcao, *args):
        """Na dúvida, nada sai: o cache fora da forma nunca derruba o doutor (a exceção vira falha do teste, não erro)."""
        try:
            return funcao(*args)
        except Exception as erro:  # noqa: BLE001
            self.fail(f"{funcao.__name__} levantou {type(erro).__name__}: {erro}")

    def antigas(self):
        return sorted(p.name for p in self.sem_erro(self.fv.versoes_antigas_do_cache, self.casa)[0])

    def test_fica_a_em_uso_e_as_duas_maiores(self):
        self.assertEqual(self.antigas(), ["0.40.0"])

    def test_sem_conferir_o_em_uso_nada_sai(self):
        (self.casa / ".claude" / "plugins" / "installed_plugins.json").write_text("{", encoding="utf-8")
        self.assertEqual(self.antigas(), [])
        self.instalados(["9.9.9"])  # installPath que não resolve
        self.assertEqual(self.antigas(), [])

    def test_pasta_fora_da_forma_ou_atalho_nao_sai(self):
        self.versao("0.39.0", nome="outro")
        (self.forge / "0.38.0").symlink_to(self.forge / "0.40.0")
        (self.forge / "lixo").mkdir()
        self.assertEqual(self.antigas(), ["0.40.0"])

    def test_remover_apaga_registra_e_pula_a_que_passou_a_ser_usada(self):
        self.versao("0.39.0")
        lista = self.sem_erro(self.fv.versoes_antigas_do_cache, self.casa)[0]
        self.instalados(["0.41.0", "0.39.0"])
        estado = self.casa / "estado"
        with unittest.mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(estado)}):
            apagadas, puladas = self.sem_erro(self.fv.remover_do_cache, lista, self.casa)
        self.assertEqual(([p.name for p in apagadas], [p.name for p in puladas]), (["0.40.0"], ["0.39.0"]))
        self.assertFalse((self.forge / "0.40.0").exists())
        self.assertTrue((self.forge / "0.39.0").exists())
        self.assertIn("0.40.0", (estado / "forge" / "cache-removido.log").read_text(encoding="utf-8"))


    def test_sem_casa_vale_a_do_usuario(self):  # Q55: o padrão de `casa_` é a casa do usuário
        with unittest.mock.patch.object(self.fv, "casa", return_value=self.casa):
            self.assertEqual(sorted(p.name for p in self.sem_erro(self.fv.versoes_antigas_do_cache)[0]), ["0.40.0"])

    def test_cache_ausente_ou_installed_ilegivel_nada_sai(self):  # Q44 e Q53, sem erro
        self.assertEqual(self.sem_erro(self.fv.fora_de_uso, [self.forge / "0.40.0"], None, []), [])
        shutil.rmtree(self.casa / ".claude" / "plugins" / "cache")
        self.assertEqual(self.sem_erro(self.fv.candidatas_do_cache, self.casa), [])

    def test_installpath_fora_da_forma_nada_sai(self):  # Q50
        dados = {"version": 2, "plugins": {"forge@mkt": [{"installPath": 3}]}}
        (self.casa / ".claude" / "plugins" / "installed_plugins.json").write_text(json.dumps(dados), encoding="utf-8")
        self.assertIsNone(self.sem_erro(self.fv.caminhos_em_uso, self.casa))
        self.assertEqual(self.antigas(), [])

    def test_protege_a_copia_do_claude_plugin_root(self):  # Q52
        with unittest.mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(self.forge / "0.40.0")}):
            self.assertEqual(self.antigas(), [])
        with unittest.mock.patch.dict(os.environ):
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            self.assertNotIn(self.forge / "0.40.0", self.sem_erro(self.fv.protegidas_da_sessao))

    def test_tamanho_soma_os_bytes_e_respeita_o_teto(self):  # Q56 (CM-11)
        (self.forge / "0.40.0" / "dados.bin").write_bytes(b"x" * 1000)
        total = self.sem_erro(self.fv.tamanho, self.forge / "0.40.0")
        self.assertIsInstance(total, int)
        self.assertGreaterEqual(total, 1000)
        with unittest.mock.patch.object(self.fv.time, "monotonic", side_effect=[0.0, 10.0, 10.0]):
            self.assertIsNone(self.sem_erro(self.fv.tamanho, self.forge / "0.40.0", 5.0))


class DoutorVersao(ap.Base):
    """VD-2 reduzida: consulta com falha não marca o dia; o cache diz `defasado`; o texto certo por superfície."""

    def setUp(self):
        super().setUp()
        self.publicado = self.tmp / "publicado.git"
        self.g("init", "-q", "--bare", "-b", "main", str(self.publicado), cwd=self.tmp)
        remoto_sem_manutencao(self.publicado)
        semente = self.tmp / "semente"
        self.g("clone", "-q", str(self.publicado), str(semente), cwd=self.tmp)
        (semente / "a").write_text("1\n", encoding="utf-8")
        self.g("add", "-A", cwd=semente)
        self.g("commit", "-q", "-m", "a", cwd=semente)
        self.g("push", "-q", "origin", "main", cwd=semente)
        self.semente = semente
        self.proj = self.tmp / "proj"
        self.g("init", "-q", "-b", "main", str(self.proj), cwd=self.tmp)
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge/versao").write_text("0.1.0\n", encoding="utf-8")
        self.env.update(FORGE_HOJE=HOJE, FORGE_PERMITE_LOCAL="1", FORGE_REPO_URL=str(self.publicado))
        self.versao = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]

    def tag(self, nome):
        self.g("tag", nome, cwd=self.semente)
        self.g("push", "-q", "origin", f"refs/tags/{nome}", cwd=self.semente)

    def stop(self):
        entrada = {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(self.proj)}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=self.env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def cache(self):
        arq = self.proj / ".forge/run/versao-nova"
        return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None

    def mais_nova(self):
        a, b, c = (int(n) for n in self.versao.split("."))
        return f"{a}.{b}.{c + 1}"

    def test_versao_nova_avisa_com_o_comando_do_projeto_e_grava_o_cache(self):
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        r = self.stop()
        self.assertIn(f"Saiu a versão {nova}", r.stdout)
        self.assertIn("`forge atualizar`", r.stdout)
        self.assertNotIn("jarvis-forge", r.stdout)
        cache = self.cache()
        self.assertEqual((cache["data"], cache["defasado"], cache["atual"], cache["ultima"]), (HOJE, True, self.versao, nova))

    def _virar_o_dia(self):
        antigo = self.cache()
        antigo["data"] = "2026-10-19"
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(antigo), encoding="utf-8")

    def test_a_mesma_versao_nova_nao_avisa_de_novo_no_dia_seguinte(self):
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.assertIn(f"Saiu a versão {nova}", self.stop().stdout)
        self._virar_o_dia()
        self.assertNotIn("Saiu a versão", self.stop().stdout)
        cache = self.cache()
        self.assertEqual((cache["data"], cache["defasado"], cache["avisado"]), (HOJE, True, True))  # o atraso segue provado

    def test_versao_ainda_mais_nova_avisa_no_dia_seguinte(self):
        self.tag(f"v{self.mais_nova()}")
        self.stop()
        a, b, c = (int(n) for n in self.versao.split("."))
        outra = f"{a}.{b}.{c + 2}"
        self.tag(f"v{outra}")
        self._virar_o_dia()
        self.assertIn(f"Saiu a versão {outra}", self.stop().stdout)

    def test_versao_em_uso_diferente_com_a_mesma_ultima_avisa_no_dia_seguinte(self):
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.stop()
        antigo = self.cache()
        antigo.update(data="2026-10-19", atual="0.0.1")  # o plugin em uso era outro quando se avisou
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(antigo), encoding="utf-8")
        self.assertIn(f"Saiu a versão {nova}", self.stop().stdout)

    def test_versao_nova_ainda_nao_avisada_de_dia_anterior_avisa_no_dia_seguinte(self):
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.stop()
        antigo = self.cache()
        antigo.update(data="2026-10-19", avisado=False)  # o aviso daquele dia nunca saiu
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(antigo), encoding="utf-8")
        self.assertIn(f"Saiu a versão {nova}", self.stop().stdout)

    def test_falha_do_relogio_no_stop_nao_come_o_aviso_de_versao(self):
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        codigo = ("import sys; sys.path.insert(0, sys.argv[1]); import doutor\n"
                  "def quebra(hook): raise OSError('disco cheio')\n"
                  "doutor.aviso_de_relogio = quebra; doutor.executar('doutor', doutor.principal)")
        entrada = json.dumps({"hook_event_name": "Stop", "session_id": "s", "cwd": str(self.proj)})
        r = subprocess.run([sys.executable, "-c", codigo, str(HOOK.parent)], input=entrada, capture_output=True, text=True,
                           env=self.env, cwd=self.proj, timeout=30)
        self.assertIn(f"Saiu a versão {nova}", r.stdout)

    def test_em_dia_grava_o_cache_sem_defasado_e_marca_o_dia(self):
        self.tag(f"v{self.versao}")
        self.assertNotIn("Saiu a versão", self.stop().stdout)
        cache = self.cache()
        self.assertEqual((cache["data"], cache["defasado"]), (HOJE, False))

    def test_consulta_com_falha_nao_marca_o_dia_e_tenta_de_novo(self):
        self.env["FORGE_REPO_URL"] = str(self.tmp / "nao-existe.git")
        self.assertNotIn("Saiu a versão", self.stop().stdout)
        cache = self.cache()
        self.assertNotEqual(cache.get("data"), HOJE)
        self.assertIn("falhou_em", cache)
        # o endereço volta e a espera da falha passou: a próxima consulta avisa (o dia não tinha sido marcado)
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.env["FORGE_REPO_URL"] = str(self.publicado)
        cache["falhou_em"] = time.time() - 3600
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(cache), encoding="utf-8")
        self.assertIn(f"Saiu a versão {nova}", self.stop().stdout)
        self.assertEqual(self.cache()["data"], HOJE)

    def test_depois_de_uma_falha_espera_antes_de_consultar_de_novo(self):
        self.env["FORGE_REPO_URL"] = str(self.tmp / "nao-existe.git")
        self.stop()
        primeira = self.cache()["falhou_em"]
        self.stop()  # dentro da espera: não consulta, não regrava
        self.assertEqual(self.cache()["falhou_em"], primeira)

    def test_falha_nao_apaga_a_prova_de_atraso_ja_gravada(self):
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.stop()
        antigo = self.cache()
        antigo["data"] = "2026-10-19"  # outro dia, e agora a consulta falha
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(antigo), encoding="utf-8")
        self.env["FORGE_REPO_URL"] = str(self.tmp / "nao-existe.git")
        self.stop()
        cache = self.cache()
        self.assertEqual((cache["defasado"], cache["ultima"], cache["data"]), (True, nova, "2026-10-19"))

    def test_consulta_desligada_fica_no_cache_e_nao_apaga_a_prova_de_atraso(self):
        self.env["FORGE_VERIFICAR_VERSAO"] = "0"
        self.stop()
        self.assertEqual(self.cache()["consulta"], "desligada")  # o forge-check diz `versão não conferida`, não fica mudo
        antigo = {"data": "2026-10-19", "defasado": True, "atual": self.versao, "ultima": self.mais_nova(), "texto": "x"}
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(antigo), encoding="utf-8")
        self.stop()
        cache = self.cache()
        self.assertEqual((cache["defasado"], cache["ultima"], cache["consulta"]), (True, antigo["ultima"], "desligada"))

    def test_o_aviso_do_hook_nunca_entra_no_contexto_do_modelo(self):
        self.tag(f"v{self.mais_nova()}")
        saida = json.loads(self.stop().stdout)
        self.assertEqual(list(saida), ["systemMessage"])  # ADR 0003: só ao usuário

    def test_o_texto_da_sessao_do_forge_manda_o_comando_da_copia_vigente(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        import forge_versoes
        texto = forge_versoes.texto_de_versao_nova("0.20.0", "0.22.0", "forge")
        self.assertIn("jarvis-forge --atualizar-vigente", texto)
        self.assertNotIn("forge atualizar`", texto.replace("jarvis-forge --atualizar-vigente", ""))
        self.assertIn("`forge atualizar`", forge_versoes.texto_de_versao_nova("0.20.0", "0.22.0", "projeto"))


class JarvisForgeDefasagem(ap.Base):
    """VD-1: o `jarvis-forge` avisa em toda abertura e reanexação quando a cópia vigente está atrás da origin/develop."""

    def setUp(self):
        super().setUp()
        self.origem = self.tmp / "origem.git"
        self.g("init", "-q", "--bare", "-b", "develop", str(self.origem), cwd=self.tmp)
        remoto_sem_manutencao(self.origem)
        self.semente = self.tmp / "semente"
        self.g("clone", "-q", str(self.origem), str(self.semente), cwd=self.tmp)
        (self.semente / "bin").mkdir()
        fc = self.semente / "bin/forge-check"
        fc.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        fc.chmod(0o755)
        self.publicar("inicial")
        self.g("clone", "-q", str(self.origem), str(self.home / "Forge"), cwd=self.tmp)
        self.vigente = self.home / ".local/share/forge/vigente"
        self.log = self.tmp / "chamadas"
        falsos = self.tmp / "bin"
        falsos.mkdir()
        for nome in ("claude", "tmux"):
            falso = falsos / nome
            falso.write_text(f'#!/usr/bin/env bash\necho "{nome} $*" >> "{self.log}"\n', encoding="utf-8")
            falso.chmod(0o755)
        self.env.update(PATH=f"{falsos}:{self.env['PATH']}", XDG_STATE_HOME=str(self.tmp / "estado"))
        self.assertEqual(self.rodar().returncode, 0)  # cria a cópia vigente
        self.head_inicial = self.head()

    def publicar(self, msg):
        (self.semente / "a.txt").write_text(msg + "\n", encoding="utf-8")
        self.g("add", "-A", cwd=self.semente)
        self.g("commit", "-q", "-m", msg, cwd=self.semente)
        self.g("push", "-q", "origin", "develop", cwd=self.semente)

    def head(self):
        return self.g("rev-parse", "HEAD", cwd=self.vigente)

    def data_da_copia(self):
        return self.g("log", "-1", "--format=%cs", "HEAD", cwd=self.vigente)

    def rodar(self, *args, sem_tmux=True):
        return subprocess.run(["bash", str(RAIZ / "scripts/jarvis-forge"), *args, *(["--sem-tmux"] if sem_tmux else [])],
                              env=self.env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=90, cwd=self.tmp)

    def test_com_a_sessao_aberta_atras_avisa_a_data_e_o_comando_sem_trocar_o_plugin(self):
        self.publicar("novo")
        r = self.rodar(sem_tmux=False)  # o tmux falso diz que a sessão já existe
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"a sessão aberta usa a cópia de {self.data_da_copia()}", r.stderr)
        self.assertIn("jarvis-forge --atualizar-vigente", r.stderr)
        self.assertEqual(self.head(), self.head_inicial, "o plugin foi trocado sob a sessão aberta")

    def test_o_aviso_se_repete_em_toda_reanexacao(self):
        self.publicar("novo")
        for _ in range(2):
            self.assertIn("a sessão aberta usa a cópia de", self.rodar(sem_tmux=False).stderr)

    def test_com_a_sessao_aberta_em_dia_fica_em_silencio(self):
        r = self.rodar(sem_tmux=False)
        self.assertNotIn("ATRASADO", r.stderr)
        self.assertNotIn("a sessão aberta usa", r.stderr)

    def test_com_a_sessao_aberta_e_sem_rede_diz_atrasado_desde_a_data(self):
        self.origem.rename(self.tmp / "sumiu.git")
        r = self.rodar(sem_tmux=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"ATRASADO desde {self.data_da_copia()}", r.stderr)
        self.assertIn("jarvis-forge --atualizar-vigente", r.stderr)

    def test_rev_list_com_falha_depois_do_fetch_diz_atrasado_desde_a_data(self):
        git_real = shutil.which("git", path=self.env["PATH"])
        falso = self.tmp / "bin" / "git"
        falso.write_text(f'#!/usr/bin/env bash\n[[ " $* " == *" rev-list "* ]] && exit 128\nexec "{git_real}" "$@"\n', encoding="utf-8")
        falso.chmod(0o755)
        r = self.rodar(sem_tmux=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"ATRASADO desde {self.data_da_copia()}", r.stderr)

    def test_abertura_sem_rede_diz_atrasado_desde_a_data(self):
        self.origem.rename(self.tmp / "sumiu.git")
        r = self.rodar()
        self.assertIn(f"ATRASADO desde {self.data_da_copia()}", r.stderr)
        self.assertEqual(len([l for l in r.stderr.splitlines() if "sem rede" in l]), 1)

    def test_abertura_com_recusa_diz_atrasado_desde_a_data(self):
        (self.vigente / "a.txt").write_text("sujo\n", encoding="utf-8")
        self.publicar("novo")
        r = self.rodar()
        self.assertIn("mudanças locais", r.stderr)
        self.assertIn(f"ATRASADO desde {self.data_da_copia()}", r.stderr)

    def test_abertura_que_atualiza_nao_avisa_atraso(self):
        self.publicar("novo")
        r = self.rodar()
        self.assertIn("atualizada", r.stderr)
        self.assertNotIn("ATRASADO", r.stderr)

    def test_dev_nao_avisa(self):
        self.publicar("novo")
        self.assertNotIn("ATRASADO", self.rodar("--dev").stderr)


if __name__ == "__main__":
    unittest.main()
