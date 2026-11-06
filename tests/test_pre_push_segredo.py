"""I3 (0.37 E8): o pre-push varre o delta de cada ref enviada atrás de segredo com o script da base, antes da suíte.

Roda o hook de verdade num repositório descartável: a base (refs/remotes/origin/develop) traz o script da árvore
em teste e uma suíte de brinquedo que marca que rodou; a branch acrescenta o conteúdo de cada caso.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})
TOKEN = "ghp" + "_" + "Ab3" * 8  # montado aqui para a própria varredura do Forge não achar este arquivo
SUITE = "import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_roda(self):\n        pathlib.Path('rodou').write_text('sim')\n"
ZERO = "0" * 40


class PrePushSegredo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-segredo-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = self.tmp / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "tests").mkdir()
        (self.repo / "home").mkdir()
        self.git("init", "-q", "-b", "develop")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "teste")
        shutil.copy(RAIZ / "scripts/verificar-contribuicao.sh", self.repo / "scripts")
        (self.repo / "tests/test_x.py").write_text(SUITE)
        (self.repo / ".gitignore").write_text("rodou\nhome/\n")
        self.commit("base")
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.git("checkout", "-q", "-b", "melhoria/x")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            (self.repo / nome).write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def hook(self, *refs, **extra):
        refs = refs or (("melhoria/x", self.git("rev-parse", "HEAD")),)
        entrada = "".join(f"refs/heads/x {sha} refs/{'' if n.startswith('tags/') else 'heads/'}{n} {ZERO}\n" for n, sha in refs)
        env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.tmp), HOME=str(self.repo / "home"), FORGE_TRAVA_ESPERA="20", **extra)
        r = subprocess.run([str(HOOK), "origin", "url"], cwd=self.repo, env=env, input=entrada,
                           capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr

    def recusa(self, *refs, onde=None, **extra):
        codigo, saida = self.hook(*refs, **extra)
        self.assertEqual(codigo, 1, saida)
        self.assertIn("varredura de segredo", saida)
        self.assertNotIn(TOKEN, saida, "o valor não pode sair")
        self.assertFalse((self.repo / "rodou").exists(), "a suíte rodou antes da recusa")
        if onde:
            self.assertIn(onde, saida)

    def test_token_no_delta_recusa_antes_da_suite_sem_imprimir_o_valor(self):
        self.commit("token", **{"a.md": f"t = {TOKEN}\n"})
        self.recusa(onde="a.md:1")
        self.recusa(onde="a.md:1", SHELLOPTS="xtrace")  # C-5: o script roda sem o xtrace herdado

    def test_exemplo_marcado_e_delta_limpo_passam(self):
        for nome, texto in (("ex.md", f"t = {TOKEN} forge:exemplo\n"), ("limpo.md", "nada aqui\n")):
            with self.subTest(nome):
                self.commit(nome, **{nome: texto})
                codigo, saida = self.hook()
                self.assertEqual(codigo, 0, saida)
                self.assertTrue((self.repo / "rodou").exists())

    def test_script_da_branch_que_sempre_passa_nao_esconde_o_token(self):
        self.commit("burla", **{"scripts/verificar-contribuicao.sh": "exit 0\n", "b.md": f"{TOKEN}\n"})
        self.recusa(onde="b.md:1")

    def test_nome_com_acento_espaco_ou_tab_e_gitattributes_nao_escondem(self):
        casos = {"ação.md": "ação.md:1", "com espaço.md": "com espaço.md:1", "t\tb.md": "t\\tb.md:1", ".gitattributes": "c.md:1",
                 "d.md": "d.md:1"}  # d.md: linha de conteúdo "++ b/..." não vira cabeçalho
        for nome, onde in casos.items():
            with self.subTest(nome):
                self.git("checkout", "-q", "-B", "melhoria/x", "refs/remotes/origin/develop")
                extra = {"c.md": f"{TOKEN}\n", ".gitattributes": "*.md -diff\n"} if nome == ".gitattributes" else {nome: f"{TOKEN}\n"}
                extra = {"d.md": f"++ b/{TOKEN}\n"} if nome == "d.md" else extra
                self.commit(nome, **extra)
                self.recusa(onde=onde)

    def test_token_so_na_segunda_ref_ou_numa_tag_recusa_o_envio_inteiro(self):
        limpo = self.commit("limpo", **{"l.md": "ok\n"})
        sujo = self.commit("sujo", **{"s.md": f"{TOKEN}\n"})
        self.git("checkout", "-q", limpo)
        self.recusa(("melhoria/x", limpo), ("melhoria/y", sujo), onde="s.md:1")
        self.recusa(("tags/v1", sujo), onde="s.md:1")

    def test_sem_a_base_local_avisa_e_segue(self):
        self.commit("token", **{"a.md": f"{TOKEN}\n"})
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        codigo, saida = self.hook()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("varredura pulada", saida)


if __name__ == "__main__":
    unittest.main()
