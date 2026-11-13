"""O `git()` do forge-check nos comandos de rede (`ls-remote`, `fetch`) herda a configuração que o ambiente injeta
(`GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n` e `GIT_CONFIG_PARAMETERS`: proxy, credencial, insteadOf) e continua apagando o
resto das `GIT_*` (GIT_DIR, GIT_CONFIG_GLOBAL...); nos demais comandos apaga todas.

Origem: v046 E12.1, a prova de push da conferência de entrega falhava atrás do proxy ('Proxy CONNECT aborted'). O
remoto é um repositório local alcançado só por um insteadOf do ambiente (`falso://r`): sem a configuração herdada, o
git não acha o transporte `falso` e o comando falha, sem rede."""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao  # noqa: E402
from test_forge import carregar_forge_check, git  # noqa: E402

URL_FALSA = "falso://r"


class GitRedeConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = carregar_forge_check()
        cls.tmp = Path(tempfile.mkdtemp(prefix="git-rede-"))
        cls.remoto = cls.tmp / "remoto.git"
        cls.trabalho = cls.tmp / "trabalho"
        cls.remoto.mkdir()
        cls.trabalho.mkdir()
        git("init", "-q", "--bare", cwd=cls.remoto)
        remoto_sem_manutencao(cls.remoto)
        git("init", "-q", "-b", "develop", cwd=cls.trabalho)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "c", cwd=cls.trabalho)
        git("push", "-q", str(cls.remoto), "develop", cwd=cls.trabalho)
        git("remote", "add", "origin", URL_FALSA, cwd=cls.trabalho)
        cls.head = git("rev-parse", "HEAD", cwd=cls.trabalho).stdout.strip()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _ambiente(self, **extra):
        """Ambiente sem nenhuma GIT_* herdada de quem roda a suíte, mais `extra`."""
        base = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        return mock.patch.dict(os.environ, {**base, **extra}, clear=True)

    def _insteadof(self, chave=None, **extra):
        return self._ambiente(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0=chave or f"url.{self.remoto}.insteadOf",
                              GIT_CONFIG_VALUE_0=URL_FALSA, **extra)

    def _ls_remote(self):
        return self.fc.git(self.trabalho, "ls-remote", "origin", "refs/heads/develop")

    def test_ls_remote_herda_a_configuracao_do_ambiente(self):
        with self._insteadof():
            cod, saida = self._ls_remote()
        self.assertEqual(cod, 0, saida)
        self.assertEqual(saida.split()[0], self.head)

    def test_fetch_herda_a_configuracao_do_ambiente(self):
        with self._insteadof():
            cod, saida = self.fc.git(self.trabalho, "fetch", "-q", "origin", "develop")
        self.assertEqual(cod, 0, saida)

    def test_ls_remote_herda_git_config_parameters(self):
        with self._ambiente(GIT_CONFIG_PARAMETERS=f"'url.{self.remoto}.insteadof'='{URL_FALSA}'"):
            cod, saida = self._ls_remote()
        self.assertEqual(cod, 0, saida)

    def test_ls_remote_continua_sem_git_dir(self):
        with self._insteadof(GIT_DIR=str(self.tmp / "nao-existe")):
            cod, saida = self._ls_remote()
        self.assertEqual(cod, 0, saida)
        self.assertEqual(saida.split()[0], self.head)

    def test_ls_remote_continua_sem_git_config_global(self):
        config = self.tmp / "global"
        config.write_text(f'[url "{self.remoto}"]\n\tinsteadOf = {URL_FALSA}\n', encoding="utf-8")
        with self._ambiente(GIT_CONFIG_GLOBAL=str(config)):
            cod, _ = self._ls_remote()
        self.assertNotEqual(cod, 0)

    def test_comando_local_nao_herda_a_configuracao_do_ambiente(self):
        with self._insteadof(chave="forge.sonda"):
            cod, saida = self.fc.git(self.trabalho, "config", "--get", "forge.sonda")
        self.assertEqual((cod, saida), (1, ""))


if __name__ == "__main__":
    unittest.main()
