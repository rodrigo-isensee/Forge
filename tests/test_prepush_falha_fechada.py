"""PREPUSH-MODELO-FALHA-ABERTA (v0478 E82.1): o pre-push do modelo falha fechado quando falta um utilitário.

O modelo (`templates/projeto/.githooks/pre-push`, arquivo travado, só o dono grava) ganha a correção pelo patch de
`docs/propostas/prepush-modelo-falha-aberta.md`: sem o `dirname`, o envio é barrado (antes a checagem do projeto era
pulada); sem o `tr`, o limite de tempo segue valendo; sem o `python3`, a chave `registros` barra o envio.

Cada teste aplica o bloco `diff` da proposta numa cópia temporária do hook (com o patch já aplicado no modelo, usa o hook
como está) e o roda direto, com a linha de ref no stdin, num repositório descartável e com o PATH só numa pasta de links
para os utilitários que o hook chama, menos o que o teste tira.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_git_herdado  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PROPOSTA = RAIZ / "docs" / "propostas" / "prepush-modelo-falha-aberta.md"
HOOK = Path("templates") / "projeto" / ".githooks" / "pre-push"
UTILITARIOS = ("bash", "git", "dirname", "mktemp", "rm", "tr", "ps", "sleep", "find", "mkdir", "id", "date", "flock", "mv",
               "nice", "ionice", "python3", "timeout")
BASH = shutil.which("bash") or "/bin/bash"
ZERO = "0" * 40


def diff_da_proposta():
    """O bloco ```diff da proposta (um só), o texto que o dono passa ao `git apply`."""
    linhas = PROPOSTA.read_text(encoding="utf-8").splitlines(keepends=True)
    inicio = linhas.index("```diff\n") + 1
    fim = linhas.index("```\n", inicio)
    return "".join(linhas[inicio:fim])


def rodar(cmd, cwd, env, entrada=None, prazo=120):
    return subprocess.run(cmd, cwd=cwd, env=env, input=entrada, capture_output=True, text=True, timeout=prazo)


def hook_corrigido(destino, env):
    """Cópia do hook do modelo com o patch da proposta (repositório próprio, para o `git apply` não cair noutro)."""
    (destino / HOOK).parent.mkdir(parents=True)
    shutil.copy2(RAIZ / HOOK, destino / HOOK)
    rodar(["git", "init", "-q", str(destino)], destino, env)
    patch = diff_da_proposta()
    if rodar(["git", "apply", "--check", "-"], destino, env, patch).returncode != 0:
        ja = rodar(["git", "apply", "-R", "--check", "-"], destino, env, patch)
        if ja.returncode != 0:
            raise AssertionError(f"o patch da proposta não aplica no modelo: {ja.stderr}")
        return destino / HOOK
    r = rodar(["git", "apply", "-"], destino, env, patch)
    if r.returncode != 0:
        raise AssertionError(f"git apply: {r.stderr}")
    return destino / HOOK


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="forge-falha-fechada-")))
        self.casa = self.tmp / "casa"
        self.casa.mkdir(mode=0o700)
        self.env = sem_git_herdado({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.casa),
                                    "XDG_RUNTIME_DIR": str(self.casa), "TMPDIR": str(self.casa), "LC_ALL": "C.UTF-8"},
                                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                   GIT_COMMITTER_EMAIL="t@t", GIT_TERMINAL_PROMPT="0", GIT_CONFIG_NOSYSTEM="1",
                                   GIT_CONFIG_GLOBAL=os.devnull)
        self.repo = self.tmp / "proj"
        rodar(["git", "init", "-q", "-b", "develop", str(self.repo)], self.tmp, self.env)
        (self.repo / ".githooks").mkdir()
        shutil.copy2(hook_corrigido(self.tmp / "forge", self.env), self.repo / ".githooks" / "pre-push")
        (self.repo / ".forge").mkdir()
        self.config({"caminhos_extra": []})
        self.local("exit 0")
        (self.repo / "a.txt").write_text("x\n", encoding="utf-8")
        rodar(["git", "add", "-A"], self.repo, self.env)
        rodar(["git", "commit", "-q", "-m", "base"], self.repo, self.env)
        self.sha = rodar(["git", "rev-parse", "HEAD"], self.repo, self.env).stdout.strip()

    def config(self, dados):
        (self.repo / ".forge" / "config.json").write_text(json.dumps(dados), encoding="utf-8")

    def local(self, corpo):
        """pre-push.local que anota que rodou e faz `corpo`."""
        arq = self.repo / ".githooks" / "pre-push.local"
        arq.write_text(f'#!{BASH}\necho rodou >> "{self.tmp}/rodou"\n{corpo}\n', encoding="utf-8")
        arq.chmod(0o755)

    def ferramentas(self, sem=(), falsos=None):
        """Pasta com links para os utilitários do hook, menos os de `sem`; `falsos` ({nome: script}) troca o link."""
        pasta = self.tmp / "ferramentas"
        shutil.rmtree(pasta, ignore_errors=True)
        pasta.mkdir()
        for nome in UTILITARIOS:
            caminho = shutil.which(nome)
            if nome not in sem and caminho:
                (pasta / nome).symlink_to(caminho)
        for nome, corpo in (falsos or {}).items():
            (pasta / nome).unlink(missing_ok=True)
            (pasta / nome).write_text(f"#!{BASH}\n{corpo}\n", encoding="utf-8")
            (pasta / nome).chmod(0o755)
        return str(pasta)

    def enviar(self, sem=(), falsos=None, **extra):
        """Roda o hook como o git: `$0` é o caminho relativo dele, cwd na raiz, a ref nova no stdin."""
        env = {**self.env, "PATH": self.ferramentas(sem, falsos), **extra}
        linha = f"refs/heads/feature/x {self.sha} refs/heads/feature/x {ZERO}\n"
        r = rodar([BASH, ".githooks/pre-push", "origin", str(self.tmp / "remoto.git")], self.repo, env, linha)
        return r.returncode, r.stdout + r.stderr, (self.tmp / "rodou").exists()


class DirnameAusente(Base):
    def test_controle_com_tudo_no_path_a_checagem_roda(self):
        self.local("exit 1")
        rc, saida, rodou = self.enviar()
        self.assertEqual(rc, 1, saida)
        self.assertTrue(rodou, saida)

    def test_sem_dirname_barra_o_envio(self):
        self.local("exit 0")
        rc, saida, rodou = self.enviar(sem=("dirname",))
        self.assertEqual(rc, 1, saida)
        self.assertIn("o dirname (coreutils) falta no PATH ou falhou", saida)
        self.assertFalse(rodou, saida)

    def test_dirname_com_erro_barra_mesmo_com_a_pasta_certa(self):
        rc, saida, _ = self.enviar(falsos={"dirname": "echo .githooks; exit 3"})
        self.assertEqual(rc, 1, saida)
        self.assertIn("o dirname (coreutils) falta no PATH ou falhou", saida)

    def test_dirname_com_saida_vazia_barra(self):
        rc, saida, rodou = self.enviar(falsos={"dirname": "exit 0"})
        self.assertEqual(rc, 1, saida)
        self.assertIn("o dirname (coreutils) falta no PATH ou falhou", saida)
        self.assertFalse(rodou, saida)


class LimiteSemTr(Base):
    def test_sem_tr_o_limite_encerra_a_checagem_longa(self):
        self.local(f"{shutil.which('sleep')} 20; exit 0")
        rc, saida, rodou = self.enviar(sem=("tr",), FORGE_PREPUSH_TIMEOUT="1")
        self.assertTrue(rodou, saida)
        self.assertEqual(rc, 1, saida)
        self.assertIn("passou de 1 s e foi encerrada", saida)


class RegistrosSemPython(Base):
    def test_controle_com_python3_os_registros_rodam(self):
        self.config({"registros": "false"})
        rc, saida, _ = self.enviar(falsos={"python3": f'exec "{sys.executable}" "$@"'})
        self.assertEqual(rc, 1, saida)
        self.assertIn("a conferência de registros saiu 1", saida)

    def test_sem_python3_com_a_chave_barra(self):
        self.config({"registros": "false"})
        rc, saida, _ = self.enviar(sem=("python3",))
        self.assertEqual(rc, 1, saida)
        self.assertIn("falta no PATH: python3; a chave registros", saida)

    def test_sem_python3_sem_a_chave_segue_com_aviso(self):
        self.config({"caminhos_extra": []})
        rc, saida, rodou = self.enviar(sem=("python3",))
        self.assertEqual(rc, 0, saida)
        self.assertTrue(rodou, saida)
        self.assertIn("sem a chave registros, nada a conferir", saida)


if __name__ == "__main__":
    unittest.main()
