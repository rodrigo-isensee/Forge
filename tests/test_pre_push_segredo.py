"""I3 (0.37 E8): o pre-push varre o delta de cada ref enviada com o script da base, antes da suíte (hook de verdade
num repositório descartável; a base traz o script em teste e uma suíte de brinquedo que marca que rodou)."""
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
AMBIENTE["FORGE_PREPUSH_SUITE"] = "afetados"  # ENVIO-LEVE: o padrão do hook não roda teste; estes testes exercitam o plano dos afetados
TOKEN = "ghp" + "_" + "Ab3" * 8  # montado aqui para a própria varredura do Forge não achar este arquivo
SUITE = "import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_roda(self):\n        pathlib.Path('rodou').write_text('sim')\n"


class PrePushSegredo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-segredo-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = self.tmp / "repo"
        for pasta in ("scripts", "tests", "home"):
            (self.repo / pasta).mkdir(parents=True)
        self.git("init", "-q", "-b", "develop")
        shutil.copy(RAIZ / "scripts/verificar-contribuicao.sh", self.repo / "scripts")
        (self.repo / "tests/test_x.py").write_text(SUITE)
        (self.repo / ".gitignore").write_text("rodou\nhome/\n")
        self.commit("base")
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.git("checkout", "-q", "-b", "melhoria/x")

    def git(self, *args):
        comando = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args]
        return subprocess.run(comando, cwd=self.repo, env=AMBIENTE, check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            (self.repo / nome).write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def hook(self, *refs, **extra):
        refs = refs or (("melhoria/x", self.git("rev-parse", "HEAD")),)
        entrada = "".join(f"refs/heads/x {sha} refs/{'' if n.startswith('tags/') else 'heads/'}{n} {'0' * 40}\n" for n, sha in refs)
        env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.tmp), HOME=str(self.repo / "home"), FORGE_TRAVA_ESPERA="20", **extra)
        r = subprocess.run([str(HOOK), "origin", "url"], cwd=self.repo, env=env, input=entrada, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr

    def recusa(self, *refs, onde, **extra):
        codigo, saida = self.hook(*refs, **extra)
        self.assertEqual(codigo, 1, saida)
        self.assertIn("varredura de segredo", saida)
        self.assertNotIn(TOKEN, saida, "o valor não pode sair")
        self.assertFalse((self.repo / "rodou").exists(), "a suíte rodou antes da recusa")
        self.assertIn(onde, saida)

    def test_token_no_delta_recusa_antes_da_suite_sem_imprimir_o_valor(self):
        self.commit("token", **{"a.md": f"t = {TOKEN}\n"})
        self.recusa(onde="a.md:1")
        self.recusa(onde="a.md:1", SHELLOPTS="xtrace")  # C-5: o script roda sem o xtrace herdado

    def test_cor_forcada_pela_config_nao_esconde_o_token(self):  # C-4: --no-color nos dois git diff do script
        self.commit("token", **{"a.md": f"t = {TOKEN}\n"})
        self.recusa(onde="a.md:1", GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="color.ui", GIT_CONFIG_VALUE_0="always")

    def passa(self, nome, texto):
        self.commit(nome, **{nome: texto})
        codigo, saida = self.hook()
        self.assertEqual(codigo, 0, saida)
        self.assertTrue((self.repo / "rodou").exists())
        return saida

    def test_exemplo_marcado_e_delta_limpo_passam(self):
        self.passa("ex.md", f"t = {TOKEN} forge:exemplo\n")
        self.passa("limpo.md", "nada aqui\n")

    def test_script_da_branch_que_sempre_passa_nao_esconde_o_token(self):
        self.commit("burla", **{"scripts/verificar-contribuicao.sh": "exit 0\n", "b.md": f"{TOKEN}\n"})
        self.recusa(onde="b.md:1")

    def test_nome_com_acento_espaco_ou_tab_e_gitattributes_nao_escondem(self):
        casos = (({"ação.md": TOKEN}, "ação.md:1"), ({"com espaço.md": TOKEN}, "com espaço.md:1"), ({"t\tb.md": TOKEN}, "t\\tb.md:1"),
                 ({".gitattributes": "*.md -diff", "c.md": TOKEN}, "c.md:1"), ({"d.md": "++ b/" + TOKEN}, "d.md:1"))  # d: não é cabeçalho
        for arquivos, onde in casos:
            with self.subTest(onde):
                self.git("checkout", "-q", "-B", "melhoria/x", "refs/remotes/origin/develop")
                self.commit(onde, **{nome: texto + "\n" for nome, texto in arquivos.items()})
                self.recusa(onde=onde)

    def test_token_so_na_segunda_ref_ou_numa_tag_recusa_o_envio_inteiro(self):
        limpo = self.commit("limpo", **{"l.md": "ok\n"})
        sujo = self.commit("sujo", **{"s.md": f"{TOKEN}\n"})
        self.git("checkout", "-q", limpo)
        self.recusa(("melhoria/x", limpo), ("tags/v0", sujo), onde="s.md:1")  # PREPUSH-REFS: uma branch por envio
        self.recusa(("tags/v1", sujo), onde="s.md:1")

    def test_sem_a_base_local_avisa_e_segue(self):  # o CI varre
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        self.assertIn("varredura pulada", self.passa("a.md", f"{TOKEN}\n"))

    def segue_com_aviso(self, aviso, *refs):  # C-8 e C-10: o ramo avisa, não varre a ref e a suíte roda (o CI varre)
        codigo, saida = self.hook(*refs)
        self.assertEqual(codigo, 0, saida)
        self.assertIn(aviso, saida)
        self.assertTrue((self.repo / "rodou").exists(), saida)

    def test_ref_que_nao_descasca_a_commit_avisa_e_segue(self):  # pre-push:192
        self.commit("limpo", **{"l.md": "ok\n"})
        self.segue_com_aviso("refs/tags/arvore não é commit", ("tags/arvore", self.git("rev-parse", "HEAD^{tree}")))

    def test_ref_sem_base_comum_avisa_e_segue(self):  # pre-push:194
        self.git("checkout", "-q", "--orphan", "melhoria/orfa")
        self.commit("orfa", **{"o.md": f"{TOKEN}\n"})
        self.segue_com_aviso("refs/heads/melhoria/orfa sem base comum", ("melhoria/orfa", self.git("rev-parse", "HEAD")))

    def test_script_da_base_sem_a_marca_varre_so_o_head(self):  # pre-push:196, a transição C-10
        script = self.repo / "scripts/verificar-contribuicao.sh"
        script.write_text("".join(l for l in script.read_text().splitlines(True) if not l.startswith("# forge:ponta")))
        self.commit("base sem a marca")
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        limpo = self.commit("limpo", **{"l.md": "ok\n"})
        sujo = self.commit("sujo", **{"s.md": f"{TOKEN}\n"})
        self.git("checkout", "-q", limpo)
        self.segue_com_aviso("não aceita a ponta; refs/heads/melhoria/y não foi varrida", ("melhoria/y", sujo))
        (self.repo / "rodou").unlink()
        self.git("checkout", "-q", sujo)
        self.recusa(("melhoria/y", sujo), onde="s.md:1")
