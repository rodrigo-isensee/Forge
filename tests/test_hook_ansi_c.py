"""HOOK-ANSI-C (cartão LEITOR-ANSI-C): o leitor dos hooks não junta `$'it\\'s'` com o `\\'` seguinte numa palavra só.

O bash lê `$'…'` até o `'` que fecha (`\\'` dentro é aspa literal); o `shlex` toma `\\'` por fecho de aspas simples e,
sozinho, liberaria `echo $'it\\'s'; cat .env\\'`. O leitor fiel (`palavras_do_texto`) sabe a diferença e `leituras`
falha fechado nela. Só arquivos de um diretório temporário: nenhum teste lê ou apaga `.env` ou `.git` reais."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOKS = RAIZ / "hooks"  # o hook sai de `HOOKS / f"{nome}.py"`: o mapa do bin/forge-testes (fora desta entrega) ainda não lista este módulo


def ambiente_limpo():
    """Sem as variáveis GIT_* e FORGE_* nem `CLAUDE_PROJECT_DIR`, sem config global do git (como o de test_forge)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return sem_manutencao(env)


SEM_PAR = "aspas sem par na leitura do hook"
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; _comum.forge_check().GIT_TIMEOUT_S = 120; "
            "_comum.PRAZO_DA_DECISAO_S = 120.0; sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")

CASO_ENV = "echo $'it\\'s'; cat .env\\'"
CASO_GIT = "echo $'it\\'s'; rm -rf .git \\'"


class HookAnsiC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = Path(tempfile.mkdtemp(prefix="forge-ansi-c-"))
        env = ambiente_limpo()
        for args in (("init", "-q", "-b", "develop"), ("config", "user.email", "t@example.com"),
                     ("config", "user.name", "Teste")):
            subprocess.run(["git", "-C", str(cls.raiz), *args], env=env, check=True, capture_output=True)
        (cls.raiz / ".forge").mkdir()
        (cls.raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        (cls.raiz / ".forge" / "config.json").write_text("{}", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.raiz, ignore_errors=True)

    def conformidade(self, comando, nome="conformidade"):
        entrada = {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": "forge:node-backend",
                   "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"}
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / f"{nome}.py")], input=json.dumps(entrada),
                              cwd=self.raiz, env=ambiente_limpo(), capture_output=True, text=True, timeout=120)

    def bash(self, comando, arquivos):
        """O bash real roda `comando` num diretório temporário só dele, com os `arquivos` {nome: conteúdo | None (pasta)}."""
        pasta = Path(tempfile.mkdtemp(prefix="forge-ansi-c-bash-"))
        self.addCleanup(shutil.rmtree, pasta, ignore_errors=True)
        for nome, conteudo in arquivos.items():
            if conteudo is None:
                (pasta / nome).mkdir()
            else:
                (pasta / nome).write_text(conteudo, encoding="utf-8")
        r = subprocess.run(["bash", "--norc", "--noprofile", "-c", comando], cwd=pasta, capture_output=True, text=True,
                           timeout=30)
        return r, pasta

    def test_o_bash_roda_o_segundo_comando(self):
        r, _ = self.bash(CASO_ENV, {".env'": "SEGREDO-FALSO\n"})
        self.assertEqual(r.stdout, "it's\nSEGREDO-FALSO\n")
        r, pasta = self.bash(CASO_GIT, {".git": None, "'": ""})
        self.assertEqual(r.stdout, "it's\n")
        self.assertFalse((pasta / ".git").exists(), "o bash separou o `;` e rodou o rm")

    def test_os_dois_casos_do_cartao_saem_2(self):
        for comando in (CASO_ENV, CASO_GIT):
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn(SEM_PAR, r.stderr)

    def test_a_aspa_escapada_mais_adiante_na_linha_tambem_falha_fechado(self):
        for comando in ("true && echo $'x\\'y' && cat .env\\'", "echo $'a\\\\b' $'it\\'s'; cat .env\\'",
                        "echo \"$(echo $'it\\'s'; cat .env\\')\""):
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual(r.returncode, 2, r.stderr)

    def test_controles_a_decisao_de_hoje_nao_muda(self):
        for comando in ("echo $'it\\'s'", "printf %s $'a\\'b'"):  # sem par para o `shlex`: já saíam 2
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual((r.returncode, SEM_PAR in r.stderr), (2, True), r.stderr)
        for comando in ("echo $'a\\\\b\\nc'", "echo $'a\\nb'", "echo $'a\\\\'", "echo it\\'s; echo ok"):  # saíam 0
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_barra_barra_antes_do_fecho_nao_e_aspa_escapada(self):
        r = self.conformidade("echo $'a\\\\'; cat .env")  # o `\\` é a barra; o `'` fecha; o `;` separa e o cat é recusado
        self.assertEqual(r.returncode, 2)
        self.assertIn("ler .env", r.stderr)
        self.assertNotIn(SEM_PAR, r.stderr)

    def test_o_leitor_fiel_marca_so_a_aspa_escapada(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        import _comum
        self.assertTrue(_comum.palavras_do_texto("echo $'it\\'s'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo $'a\\\\'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo $'a\\nb'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo 'it\\'; echo ok").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo \"$'\\'\"").aspa_escapada)


if __name__ == "__main__":
    unittest.main()
