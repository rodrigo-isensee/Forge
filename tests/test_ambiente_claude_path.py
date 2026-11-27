"""E39.1 (DEVCONTAINER-CLAUDE-NO-PATH e pendentes do #926): o claude novo vem primeiro no PATH, o postStart para sem pasta
temporária e o comando manual da mensagem de ERRO parte da main, nunca da cópia de trabalho."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_ambiente_recriacao import FORGE, rodar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
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

    def test_readme_e_avisos_mandam_abrir_o_jarvis_pelo_binario_novo(self):
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("`/root/.local/bin/claude --agent forge:jarvis --permission-mode auto`", readme)
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
