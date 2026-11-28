"""K152 (v0478 E81.1): uma cópia de trabalho nova, sem as dependências da stack, não quebra o pre-push do projeto sem
explicar. O `bin/forge-init` grava no `.githooks/pre-push.local` o comando de instalar da stack (os argv do
`stacks/<stack>/instalar.json`, marcador `{{INSTALAR}}`); o modelo do pre-push.local (arquivo travado, só o dono grava)
ganha a conferência pelo patch de `docs/propostas/k152-pre-push.md`: programa do pronto rápido fora do PATH barra o envio
com a mensagem e o comando de instalar, sem nunca pular a checagem.

Cada teste roda numa cópia temporária do Forge (bin/forge-init, templates/projeto, stacks e o manifesto) com o patch da
proposta aplicado; com o patch já aplicado no modelo (o dono o aplicou), a cópia o usa como está.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import remoto_sem_manutencao, sem_git_herdado  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PROPOSTA = RAIZ / "docs" / "propostas" / "k152-pre-push.md"
LOCAL = Path(".githooks") / "pre-push.local"
INSTALAR_PYTHON = ("python3 -m venv .venv && .venv/bin/python -m pip install --require-hashes --no-deps -r requirements.lock"
                   " && .venv/bin/python -m pip install --no-deps -e .")
BASH = shutil.which("bash") or "/bin/bash"
# O envio precisa de git, bash e python3; o pre-push do modelo usa ainda os utilitários do sistema abaixo (sem `dirname`
# ele nem acha o pre-push.local). Os opcionais o hook confere com `command -v` e entram só se existem nesta máquina.
PROGRAMAS_DO_ENVIO = ("git", "bash", "python3", "dirname", "tr", "rm", "ps", "mkdir", "mktemp", "cat", "sleep", "stat",
                      "realpath", "date", "env", "id", "find", "mv")
OPCIONAIS_DO_ENVIO = ("flock", "timeout", "nice", "ionice")


def diff_da_proposta():
    """O bloco ```diff da proposta (um só), o texto que o dono passa ao `git apply`."""
    linhas = PROPOSTA.read_text(encoding="utf-8").splitlines(keepends=True)
    inicio = linhas.index("```diff\n") + 1
    fim = linhas.index("```\n", inicio)
    return "".join(linhas[inicio:fim])


def rodar(cmd, cwd, env, entrada=None):
    return subprocess.run(cmd, cwd=cwd, env=env, input=entrada, capture_output=True, text=True, timeout=120)


def copia_do_forge(destino):
    """Cópia mínima do Forge para o forge-init, com o patch da proposta aplicado no modelo (repositório próprio, para o
    `git apply` não cair num repositório de fora)."""
    (destino / "bin").mkdir(parents=True)
    shutil.copy2(RAIZ / "bin" / "forge-init", destino / "bin" / "forge-init")
    shutil.copytree(RAIZ / "templates" / "projeto", destino / "templates" / "projeto", symlinks=True)
    shutil.copytree(RAIZ / "stacks", destino / "stacks", symlinks=True)
    shutil.copytree(RAIZ / ".claude-plugin", destino / ".claude-plugin")
    env = sem_git_herdado({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(destino)})
    rodar(["git", "init", "-q", str(destino)], destino, env)
    patch = diff_da_proposta()
    if rodar(["git", "apply", "--check", "-"], destino, env, patch).returncode != 0:
        ja = rodar(["git", "apply", "-R", "--check", "-"], destino, env, patch)
        if ja.returncode != 0:
            raise AssertionError(f"o patch da proposta não aplica no modelo: {ja.stderr}")
        return destino
    r = rodar(["git", "apply", "-"], destino, env, patch)
    if r.returncode != 0:
        raise AssertionError(f"git apply: {r.stderr}")
    return destino


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="forge-k152-")))
        self.casa = self.tmp / "casa"
        self.casa.mkdir(mode=0o700)
        self.env = sem_git_herdado({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.casa),
                                    "XDG_RUNTIME_DIR": str(self.casa), "TMPDIR": str(self.casa), "LC_ALL": "C.UTF-8"},
                                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                   GIT_COMMITTER_EMAIL="t@t", GIT_TERMINAL_PROMPT="0")

    def projeto(self, stack="python", forge=None):
        forge = forge or copia_do_forge(self.tmp / "forge")
        proj = self.tmp / f"proj-{stack}"
        rodar(["git", "init", "-q", "-b", "develop", str(proj)], self.tmp, self.env)
        r = rodar([str(forge / "bin" / "forge-init"), "--stack", stack, "--sem-sandbox", str(proj)], proj, self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return proj

    def ferramentas(self, rc=None):
        """PATH só com o bash, o dirname e os programas falsos de `rc` ({nome: código de saída}), que anotam a chamada."""
        pasta = self.tmp / "ferramentas"
        shutil.rmtree(pasta, ignore_errors=True)
        pasta.mkdir()
        for nome in ("bash", "dirname"):
            (pasta / nome).symlink_to(shutil.which(nome))
        for nome, codigo in (rc or {}).items():
            arq = pasta / nome
            arq.write_text(f'#!{BASH}\necho "{nome} $*" >> "{self.tmp}/chamadas"\nexit {codigo}\n', encoding="utf-8")
            arq.chmod(0o755)
        return str(pasta)

    def path_sem_pronto(self):
        """PATH controlado: só links para o que o envio usa (nunca ruff nem mypy), para o teste rodar igual em toda
        máquina, com ou sem as ferramentas da stack instaladas."""
        pasta = self.tmp / "path-sem-pronto"
        pasta.mkdir()
        for nome in PROGRAMAS_DO_ENVIO + OPCIONAIS_DO_ENVIO:
            achado = shutil.which(nome)
            if achado is None and nome in OPCIONAIS_DO_ENVIO:
                continue
            self.assertIsNotNone(achado, f"{nome} fora do PATH: o teste precisa dele")
            (pasta / nome).symlink_to(achado)
        return str(pasta)

    def pre_push_local(self, proj, rc=None):
        """Roda o pre-push.local gerado com o PATH de `ferramentas(rc)`; devolve (rc, saída, chamadas)."""
        (self.tmp / "chamadas").unlink(missing_ok=True)
        r = rodar([BASH, str(proj / LOCAL)], proj, {**self.env, "PATH": self.ferramentas(rc)})
        chamadas = self.tmp / "chamadas"
        return r.returncode, r.stdout + r.stderr, chamadas.read_text(encoding="utf-8").splitlines() if chamadas.exists() else []


class ForgeInitGravaOComandoDeInstalar(Base):
    def test_cada_stack_grava_o_comando_do_instalar_json(self):
        forge = copia_do_forge(self.tmp / "forge")
        for stack, esperado in (("python", INSTALAR_PYTHON), ("node-react", "pnpm install --frozen-lockfile")):
            with self.subTest(stack=stack):
                texto = (self.projeto(stack, forge) / LOCAL).read_text(encoding="utf-8")
                self.assertIn(f"instalar='{esperado}'", texto)
                self.assertNotIn("{{", texto)

    def test_stack_sem_instalar_json_fica_sem_comando_e_a_mensagem_diz_o_que_instalar(self):
        forge = copia_do_forge(self.tmp / "forge")
        (forge / "stacks" / "python" / "instalar.json").unlink()
        proj = self.projeto("python", forge)
        self.assertIn("instalar=''", (proj / LOCAL).read_text(encoding="utf-8"))
        (proj / "pyproject.toml").write_text("[project]\nname = 'p'\n", encoding="utf-8")
        rc, saida, _ = self.pre_push_local(proj)
        self.assertEqual(rc, 1, saida)
        self.assertIn("instale as ferramentas do pronto rápido da stack python", saida)

    def test_comando_com_aspa_simples_fica_vazio(self):
        """O pre-push.local guarda o comando entre aspas simples: uma aspa nele quebraria o arquivo."""
        forge = copia_do_forge(self.tmp / "forge")
        (forge / "stacks" / "python" / "instalar.json").write_text(
            '{"detecta": ["x"], "comandos": [["echo", "it\'s"]]}', encoding="utf-8")
        local = self.projeto("python", forge) / LOCAL
        self.assertIn("instalar=''", local.read_text(encoding="utf-8"))
        self.assertEqual(rodar([BASH, "-n", str(local)], self.tmp, self.env).returncode, 0)


class PrePushLocalSemDependencias(Base):
    def setUp(self):
        super().setUp()
        self.proj = self.projeto("python")
        (self.proj / "pyproject.toml").write_text("[project]\nname = 'p'\n", encoding="utf-8")

    def test_sem_nenhuma_ferramenta_barra_com_o_comando_de_instalar_e_nao_roda_o_pronto(self):
        rc, saida, chamadas = self.pre_push_local(self.proj)
        self.assertEqual(rc, 1, saida)
        self.assertIn("falta no PATH: ruff mypy (", saida)
        self.assertIn(f"Instale e envie de novo: {INSTALAR_PYTHON};", saida)
        self.assertNotIn("pronto rápido:", saida)
        self.assertEqual(chamadas, [])

    def test_falta_so_uma_barra_e_nomeia_so_ela(self):
        rc, saida, chamadas = self.pre_push_local(self.proj, {"ruff": 0})
        self.assertEqual(rc, 1, saida)
        self.assertIn("falta no PATH: mypy (", saida)
        self.assertEqual(chamadas, [])

    def test_com_as_ferramentas_o_pronto_rapido_roda(self):
        rc, saida, chamadas = self.pre_push_local(self.proj, {"ruff": 0, "mypy": 0})
        self.assertEqual(rc, 0, saida)
        self.assertEqual(chamadas, ["ruff check .", "ruff format --check .", "mypy src"])

    def test_pronto_reprovado_barra_e_lembra_o_comando_de_instalar(self):
        rc, saida, chamadas = self.pre_push_local(self.proj, {"ruff": 1, "mypy": 0})
        self.assertEqual(rc, 1, saida)
        self.assertIn("o pronto rápido reprovou", saida)
        self.assertIn(f"instale antes as dependências: {INSTALAR_PYTHON}", saida)
        self.assertEqual(chamadas, ["ruff check ."])

    def com_pronto(self, rapido):
        """Troca o pronto rápido gerado por `rapido` (sem aspa simples), como o projeto que ajusta o seu."""
        local = self.proj / LOCAL
        linhas = [f"rapido='{rapido}'" if linha.startswith("rapido='") else linha
                  for linha in local.read_text(encoding="utf-8").splitlines()]
        local.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    def test_programa_depois_de_ou_logico_tambem_e_checado(self):
        """`a || b`: cada lado é um trecho; sem tratar o `||`, o trecho vazio entre as barras suja a lista."""
        self.com_pronto("ruff check . || mypy src")
        rc, saida, chamadas = self.pre_push_local(self.proj)
        self.assertEqual(rc, 1, saida)
        self.assertIn("falta no PATH: ruff mypy (", saida)
        self.assertEqual(chamadas, [])

    def test_programa_depois_de_pipe_tambem_e_checado(self):
        """`a | b`: o programa depois do pipe ausente barra o envio, mesmo com o primeiro instalado."""
        self.com_pronto("ruff check . | mypy src")
        rc, saida, chamadas = self.pre_push_local(self.proj, {"ruff": 0})
        self.assertEqual(rc, 1, saida)
        self.assertIn("falta no PATH: mypy (", saida)
        self.assertNotIn("pronto rápido:", saida)
        self.assertEqual(chamadas, [])


class EnvioDaCopiaNova(Base):
    """Ponta a ponta: projeto do forge-init, cópia nova por `git worktree add`, envio com código e um PATH
    controlado, sem ruff nem mypy (o teste roda igual em toda máquina)."""

    def test_copia_nova_sem_dependencias_barra_o_envio_explicando(self):
        proj = self.projeto("python")
        self.env = {**self.env, "PATH": self.path_sem_pronto()}
        remoto = self.tmp / "remoto.git"
        rodar(["git", "init", "-q", "--bare", str(remoto)], self.tmp, self.env)
        remoto_sem_manutencao(remoto)
        (proj / "pyproject.toml").write_text("[project]\nname = 'p'\n", encoding="utf-8")
        for cmd in (["git", "add", "-A"], ["git", "commit", "-q", "-m", "base"], ["git", "remote", "add", "origin", str(remoto)],
                    ["git", "worktree", "add", "-q", "--no-track", "-b", "feature/x", str(self.tmp / "copia"), "develop"]):
            r = rodar(cmd, proj, self.env)
            self.assertEqual(r.returncode, 0, r.stderr)
        copia = self.tmp / "copia"
        (copia / "src").mkdir()
        (copia / "src" / "p.py").write_text("x = 1\n", encoding="utf-8")
        for cmd in (["git", "add", "-A"], ["git", "commit", "-q", "-m", "codigo"]):
            self.assertEqual(rodar(cmd, copia, self.env).returncode, 0)
        r = rodar(["git", "push", "origin", "feature/x"], copia, self.env)
        self.assertNotEqual(r.returncode, 0, "sem as ferramentas o envio não passa: " + r.stderr)
        self.assertIn("falta no PATH: ruff mypy (cópia nova", r.stderr)
        self.assertIn(INSTALAR_PYTHON, r.stderr)
        self.assertNotIn("command not found", r.stderr, "falta utilitário no PATH controlado: o hook não roda inteiro")
        self.assertEqual(rodar(["git", "ls-remote", str(remoto)], self.tmp, self.env).stdout, "")


if __name__ == "__main__":
    unittest.main()
