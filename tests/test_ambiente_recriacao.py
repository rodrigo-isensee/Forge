"""E119.1 (AMBIENTE-SOBREVIVE-RECRIACAO): o container recriado se prepara sozinho, também com o Claude Code atual.

Só /workspaces e ~/.claude sobrevivem à recriação; o home some, e o `claude` do PATH da imagem pode ser antigo. O preparo do
Forge (`scripts/preparar-estacao.sh --container`) e o do modelo de projeto (`.devcontainer/preparar-ambiente.sh`) instalam o
Claude Code atual em ~/.local/bin pelo instalador oficial, sem rede nos testes (curl falso), de forma idempotente.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
FORGE = "scripts/preparar-estacao.sh"
PROJETO = "templates/projeto/.devcontainer/preparar-ambiente.sh"
INSTALADOR = "https://claude.ai/install.sh"
# curl falso: grava a chamada e, para o instalador, entrega um script que cria o ~/.local/bin/claude
CURL_OK = r'''echo "curl $*" >> "$REGISTRO"
while [ $# -gt 0 ]; do [ "$1" = "-o" ] && saida="$2"; shift; done
printf '#!/bin/sh\nmkdir -p "$HOME/.local/bin"\nprintf "#!/bin/sh\\nexit 0\\n" > "$HOME/.local/bin/claude"\nchmod +x "$HOME/.local/bin/claude"\n' > "$saida"
exit 0
'''
CURL_FALHA = 'echo "curl $*" >> "$REGISTRO"\nexit 22\n'


def rodar(tmp, script, *args, curl=CURL_OK, claude_no_path=False, claude_local=False, sem_curl=False, bashrc=None):
    """Roda o script de preparo com home descartável e ferramentas falsas; devolve (resultado, home, chamadas)."""
    tmp = Path(tmp)
    home, persist, bin_falso, proj = tmp / "home", tmp / "persist", tmp / "bin", tmp / "proj"
    for d in (home, persist / "Forge" / "scripts", bin_falso, proj):
        d.mkdir(parents=True, exist_ok=True)
    if not (proj / ".git").exists():
        subprocess.run(["git", "init", "-q", str(proj)], check=True, capture_output=True,
                       env=sem_manutencao())
    registro = tmp / "chamadas"
    falsos = {
        "gh": 'case "$1" in --version) echo "gh version 2.104.0 (2026-11-12)"; exit 0 ;; esac\n[ "$1 $2" = "auth status" ] && exit 1\nexit 0\n',
        "tmux": "exit 0\n", "shellcheck": "exit 0\n", "sudo": "exit 1\n", "apt-get": "exit 1\n", "curl": curl,
    }
    if claude_no_path:  # o claude antigo da imagem: está no PATH, mas não é o de ~/.local/bin
        falsos["claude"] = "echo 2.1.224\n"
    for nome, corpo in falsos.items():
        (bin_falso / nome).write_text("#!/bin/sh\n" + corpo)
        (bin_falso / nome).chmod(0o755)
    if claude_local:
        (home / ".local/bin").mkdir(parents=True)
        (home / ".local/bin/claude").write_text("#!/bin/sh\nexit 0\n")
        (home / ".local/bin/claude").chmod(0o755)
    if bashrc is not None:
        (home / ".bashrc").write_text(bashrc)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GH_", "XDG_", "FORGE_"))}
    caminho = env["PATH"]
    if sem_curl:  # PATH sem curl: o falso sai de bin_falso e as demais ferramentas entram por link, menos o curl real
        (bin_falso / "curl").unlink()
        sem = tmp / "sem-curl"
        sem.mkdir()
        for d in dict.fromkeys(caminho.split(":")):
            for f in Path(d).iterdir() if Path(d).is_dir() else ():
                alvo = sem / f.name
                if f.name != "curl" and not alvo.is_symlink():  # is_symlink: link quebrado também ocupa o nome
                    alvo.symlink_to(f)
        caminho = str(sem)
    env.update(HOME=str(home), PATH=f"{bin_falso}:{caminho}", REGISTRO=str(registro), FORGE_PERSISTENTE=str(persist),
               FORGE_PROJETO=str(proj), FORGE_PREPARO_ESSENCIAL="1",
               FORGE_APT_CHAVE=str(tmp / "chave.gpg"), FORGE_APT_LISTA=str(tmp / "gh.list"))
    argv = list(args) if args else (["--container"] if script == FORGE else [])
    r = subprocess.run(["bash", str(RAIZ / script), *argv], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    return r, home, (registro.read_text() if registro.exists() else "")


class ClaudeNoPreparo(unittest.TestCase):
    def test_sem_claude_local_instala_pelo_instalador_oficial_e_a_segunda_rodada_nao_repete(self):
        for script in (FORGE, PROJETO):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                r, home, chamadas = rodar(tmp, script, claude_no_path=True)  # o claude do PATH (antigo) não conta
                self.assertIn("fez: instalou o Claude Code atual em", r.stdout, r.stdout + r.stderr)
                self.assertTrue(os.access(home / ".local/bin/claude", os.X_OK))
                self.assertEqual(chamadas.count(INSTALADOR), 1)
                self.assertRegex(chamadas, rf"curl -fsSL --proto =https --proto-redir =https --connect-timeout 20 --max-time 120 "
                                           rf"-o \S+/instalar\.sh {re.escape(INSTALADOR)}\n")
                r2, _, chamadas2 = rodar(tmp, script, claude_no_path=True)
                self.assertIn("fez: Claude Code já instalado em", r2.stdout, r2.stdout + r2.stderr)
                self.assertEqual(chamadas2.count(INSTALADOR), 1, "a segunda rodada não pode baixar de novo")
                bashrc = (home / ".bashrc").read_text()
                self.assertEqual(len(re.findall(r'export PATH="\$HOME/\.local/bin:\$PATH"', bashrc)), 1, bashrc)

    def test_instalacao_que_falha_vira_falta_e_nao_deixa_binario(self):
        for script in (FORGE, PROJETO):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                r, home, _ = rodar(tmp, script, curl=CURL_FALHA)
                self.assertIn("falta: instalar o Claude Code (o download ou a instalação falhou", r.stdout, r.stdout + r.stderr)
                self.assertIn(INSTALADOR, r.stdout)
                self.assertNotIn("| bash", r.stdout, "a falta dá o comando em dois passos, nunca curl | bash")
                self.assertIn("e depois rode bash instalar-claude.sh", r.stdout)
                self.assertFalse((home / ".local/bin/claude").exists())

    def test_o_instalador_e_baixado_e_nao_executado_por_pipe(self):
        """Download para arquivo e só então `bash arquivo`: um download cortado não executa metade de um script."""
        for script in (FORGE, PROJETO):
            with self.subTest(script=script):
                texto = (RAIZ / script).read_text(encoding="utf-8")
                self.assertIn("curl -fsSL --proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120 "
                              f'-o "$tmp/instalar.sh" {INSTALADOR}', texto)
                self.assertIn('bash "$tmp/instalar.sh"', texto)

    def test_sem_curl_vira_falta_em_dois_passos_sem_baixar_nem_instalar(self):
        for script in (FORGE, PROJETO):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                r, home, chamadas = rodar(tmp, script, sem_curl=True)
                self.assertIn("falta: instalar o Claude Code (sem curl aqui): baixe com curl", r.stdout, r.stdout + r.stderr)
                self.assertIn("e depois rode bash instalar-claude.sh", r.stdout)
                self.assertNotIn("| bash", r.stdout)
                self.assertEqual(chamadas, "")
                self.assertFalse((home / ".local/bin/claude").exists())

    def test_comentario_com_local_bin_no_bashrc_nao_conta_como_o_export(self):
        comentario = "# o claude fica em ~/.local/bin\n#export PATH=$HOME/.local/bin:$PATH\n"
        for script in (FORGE, PROJETO):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                _, home, _ = rodar(tmp, script, claude_local=True, bashrc=comentario)
                bashrc = (home / ".bashrc").read_text()
                self.assertTrue(bashrc.startswith(comentario), bashrc)
                self.assertEqual(len(re.findall(r'(?m)^export PATH="\$HOME/\.local/bin:\$PATH"', bashrc)), 1, bashrc)

    def test_simular_nao_grava_o_bashrc_e_nao_roda_o_instalador(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, home, chamadas = rodar(tmp, FORGE, "--simular", "--container", claude_local=True)
            self.assertFalse((home / ".bashrc").exists(), "o --simular não altera o home")
        with tempfile.TemporaryDirectory() as tmp:
            r, home, chamadas = rodar(tmp, FORGE, "--simular", "--container", claude_no_path=True)
            self.assertIn("[simular] baixar " + INSTALADOR, r.stdout, r.stdout + r.stderr)
            self.assertFalse((home / ".bashrc").exists() or (home / ".local").exists())
            self.assertEqual(chamadas, "")

    def test_verificar_diz_o_que_falta_sem_alterar_nada(self):
        for script in (FORGE, PROJETO):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                r, home, chamadas = rodar(tmp, script, "--verificar", claude_no_path=True)
                self.assertEqual(r.returncode, 1)
                self.assertRegex(r.stdout, r"(?m)^falta: Claude Code atual ausente em .*/home/\.local/bin/claude .*: rode bash ")
                self.assertFalse((home / ".local").exists() or (home / ".bashrc").exists())
                self.assertNotIn("curl", chamadas)
                (home / ".local/bin").mkdir(parents=True)
                (home / ".local/bin/claude").write_text("#!/bin/sh\nexit 0\n")
                (home / ".local/bin/claude").chmod(0o755)
                r, *_ = rodar(tmp, script, "--verificar", claude_no_path=True)
                self.assertNotIn("Claude Code", r.stdout)

    def test_com_claude_local_nada_e_baixado(self):
        for script in (FORGE, PROJETO):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                r, _, chamadas = rodar(tmp, script, claude_local=True)
                self.assertIn("fez: Claude Code já instalado em", r.stdout, r.stdout + r.stderr)
                self.assertNotIn(INSTALADOR, chamadas)


class ConfiguracaoDoContainer(unittest.TestCase):
    """O container sobe e se prepara sozinho: a configuração aciona o preparo a cada início, sem o dono e sem segredo."""

    @staticmethod
    def _cfg(caminho):
        return json.loads(re.sub(r"(?m)^\s*//.*$", "", (RAIZ / caminho).read_text(encoding="utf-8")))

    def test_postStart_roda_o_preparo_de_um_clone_novo_da_main_e_o_home_perdido_volta(self):
        casos = {".devcontainer/devcontainer.json": "preparar-estacao.sh\" --container",
                 "templates/projeto/.devcontainer/devcontainer.json": "preparar-ambiente.sh"}
        for caminho, chamada in casos.items():
            with self.subTest(caminho=caminho):
                cfg = self._cfg(caminho)
                cmd = cfg["postStartCommand"]
                self.assertIn("clone -q --depth 1 --branch main", cmd)
                self.assertIn(chamada, cmd)
                if caminho.startswith("templates"):
                    self.assertTrue(cmd.rstrip().endswith("true"), "falha do preparo nunca impede o container de subir")
                else:
                    self.assertNotRegex(cmd, r";\s*true\s*$", "DEVCONTAINER-SEM-GH: a falha aparece, não é engolida")
                self.assertEqual(cfg["shutdownAction"], "none")
                self.assertIn("target=/root/.claude", " ".join(cfg["mounts"]))
                for chave in ("remoteEnv", "containerEnv", "onCreateCommand", "postCreateCommand"):
                    self.assertNotIn(chave, cfg)

    def test_o_preparo_cobre_gh_tmux_claude_e_o_atalho_das_pastas_nos_dois_scripts(self):
        for script in (FORGE, PROJETO):
            with self.subTest(script=script):
                texto = (RAIZ / script).read_text(encoding="utf-8")
                for trecho in ("githubcli-archive-keyring.gpg", "install -y -qq tmux" if script == PROJETO else "tmux",
                               INSTALADOR, ".forge-contrib"):
                    self.assertIn(trecho, texto)


# E39.1 (DEVCONTAINER-CLAUDE-NO-PATH e pendentes do #926): o claude novo vem primeiro no PATH, o postStart para sem pasta
# temporária e o comando manual da mensagem de ERRO parte da main, nunca da cópia de trabalho.
URL = "https://github.com/rodrigo-isensee/Forge.git"


def comando(chave="postStartCommand"):
    texto = (RAIZ / ".devcontainer/devcontainer.json").read_text(encoding="utf-8")
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", texto))[chave]


def bash_com_falsos(tmp, cmd, mktemp_falha=False):
    """Roda `cmd` no bash com git e mktemp falsos (registram a chamada); devolve (resultado, chamadas)."""
    bin_falso, registro = Path(tmp) / "bin", Path(tmp) / "chamadas"
    bin_falso.mkdir()
    git = ('echo "git $*" >> "$REGISTRO"\nfor ultimo; do :; done\nmkdir -p "$ultimo/scripts"\n'
           'printf \'#!/bin/sh\\necho "preparo $0 $*" >> "$REGISTRO"\\n\' > "$ultimo/scripts/preparar-estacao.sh"\n'
           "echo '# FORGE_PREPARO_ESSENCIAL:-0' >> \"$ultimo/scripts/preparar-estacao.sh\"\n")
    falsos = {"git": git, "mktemp": 'echo "mktemp $*" >> "$REGISTRO"\n' + ("exit 1\n" if mktemp_falha else f'exec {subprocess.run(["which", "mktemp"], capture_output=True, text=True).stdout.strip()} "$@"\n')}
    for nome, corpo in falsos.items():
        (bin_falso / nome).write_text("#!/bin/sh\n" + corpo)
        (bin_falso / nome).chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_falso}:{os.environ['PATH']}", REGISTRO=str(registro), TMPDIR=str(tmp))
    r = subprocess.run(["bash", "-c", cmd], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    return r, (registro.read_text() if registro.exists() else "")


class ClaudeNovoPrimeiroNoPath(unittest.TestCase):
    def test_bashrc_com_local_bin_no_fim_do_path_ainda_ganha_a_linha_da_frente(self):
        antigas = ['export PATH="$PATH:$HOME/.local/bin"\n', 'export PATH="$HOME/.local/bin"\n', "export PATH=/usr/local/bin:$HOME/.local/bin:$PATH\n"]
        for antiga in antigas:
            with self.subTest(antiga=antiga), tempfile.TemporaryDirectory() as tmp:
                _, home, _ = rodar(tmp, FORGE, claude_local=True, bashrc=antiga)
                bashrc = (home / ".bashrc").read_text()
                self.assertTrue(bashrc.startswith(antiga), bashrc)
                self.assertEqual(len(re.findall(r'(?m)^export PATH="\$HOME/\.local/bin:\$PATH"$', bashrc)), 1, bashrc)

    def test_linha_que_ja_poe_local_bin_na_frente_nao_se_repete(self):
        for linha in ('export PATH="$HOME/.local/bin:$PATH"\n', "export PATH=/root/.local/bin:$PATH\n", 'export PATH="${HOME}/.local/bin:$PATH"\n'):
            with self.subTest(linha=linha), tempfile.TemporaryDirectory() as tmp:
                _, home, _ = rodar(tmp, FORGE, claude_local=True, bashrc=linha)
                self.assertEqual((home / ".bashrc").read_text(), linha)

    def test_na_sessao_nova_o_claude_do_local_bin_vence_o_antigo_do_usr_local_bin(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, home, _ = rodar(tmp, FORGE, claude_local=True, bashrc='export PATH="$PATH:$HOME/.local/bin"\n')
            antigo = Path(tmp) / "usr-local-bin"
            antigo.mkdir()
            (antigo / "claude").write_text("#!/bin/sh\necho 2.1.224\n")
            (antigo / "claude").chmod(0o755)
            env = dict(os.environ, HOME=str(home), PATH=f"{antigo}:/usr/bin:/bin")
            r = subprocess.run(["bash", "-c", '. "$HOME/.bashrc"; command -v claude'], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(r.stdout.strip(), str(home / ".local/bin/claude"), r.stdout + r.stderr)

    def test_avisos_mandam_abrir_o_jarvis_pelo_binario_novo(self):
        script = (RAIZ / FORGE).read_text(encoding="utf-8")
        self.assertIn("rode `~/.local/bin/claude --permission-mode auto`", script)
        with tempfile.TemporaryDirectory() as tmp:
            r, home, _ = rodar(tmp, FORGE, "--verificar", claude_no_path=True)
            self.assertIn(f"abra o Jarvis com {home}/.local/bin/claude", r.stdout, r.stdout + r.stderr)


class PostStartDoContainer(unittest.TestCase):
    def test_pasta_temporaria_que_falha_para_com_erro_e_nada_roda(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, chamadas = bash_com_falsos(tmp, comando(), mktemp_falha=True)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("ERRO:", r.stderr)
            self.assertNotIn("git ", chamadas, "sem pasta temporária nenhum clone nem preparo roda")
            self.assertNotIn("preparo ", chamadas)

    def test_com_a_pasta_o_postStart_clona_a_main_e_roda_o_preparo_dela(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, chamadas = bash_com_falsos(tmp, comando())
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(f"--branch main --single-branch -- {URL} ", chamadas)
            self.assertRegex(chamadas, r"preparo \S+/r/scripts/preparar-estacao\.sh --container")

    def test_comando_manual_da_mensagem_de_erro_parte_da_main_e_nao_da_copia_de_trabalho(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, _ = bash_com_falsos(tmp, comando() + "", mktemp_falha=True)
            m = re.search(r"a partir da main \(nunca da cópia de trabalho\): (.+)$", r.stderr.strip())
            self.assertIsNotNone(m, r.stderr)
            manual = m.group(1)
            self.assertNotIn("/workspaces/Forge", manual)
        with tempfile.TemporaryDirectory() as tmp:
            r, chamadas = bash_com_falsos(tmp, manual)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(f"--branch main --single-branch -- {URL} ", chamadas)
            self.assertRegex(chamadas, r"preparo \S+/r/scripts/preparar-estacao\.sh --container")
            self.assertNotIn("/workspaces/Forge", chamadas)


if __name__ == "__main__":
    unittest.main()
