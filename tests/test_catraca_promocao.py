"""v047 E1.245 (A1 do review, da segurança e do devops): a tabela única dos pares de promoção (PROMOCOES em tests/catraca.py).

O passo "Nada pula degrau" do CI roda o modo `degrau` da catraca da develop do servidor; a catraca (pareceres e promoção) e o
scripts/arvore-testada.py leem a mesma tabela. O par promocao/X.Y.Z -> homolog só vale do próprio repositório e com o head
ancestral da develop do servidor (refs/remotes/origin/develop). PR para a homolog ou a main fora da tabela é recusado.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
SCRIPT = AQUI / "catraca.py"
_spec = importlib.util.spec_from_file_location("catraca_promocao", SCRIPT)
catraca = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(catraca)
_spec_at = importlib.util.spec_from_file_location("arvore_testada_promocao", AQUI.parent / "scripts" / "arvore-testada.py")
at = importlib.util.module_from_spec(_spec_at)
_spec_at.loader.exec_module(at)

REPO = "dono/forge"


class Repo(unittest.TestCase):
    """Repositório com a develop do servidor (refs/remotes/origin/develop) em `na_develop` e um commit fora dela em `fora`."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="promocao-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@exemplo.test",
                        GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@exemplo.test")
        self.git("init", "-q", "-b", "develop")
        self.na_develop = self.commit("a")
        self.git("update-ref", "refs/remotes/origin/develop", self.na_develop)
        self.git("switch", "-q", "-c", "melhoria/x")
        self.fora = self.commit("b")

    def git(self, *args):
        r = subprocess.run(["git", "-C", str(self.tmp), *args], env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, nome):
        (self.tmp / nome).write_text(nome + "\n")
        self.git("add", nome)
        self.git("commit", "-q", "-m", nome)
        return self.git("rev-parse", "HEAD")


class Tabela(unittest.TestCase):
    def test_pares_da_tabela_e_fora_dela(self):
        for head, base, linha in (("develop", "homolog", True), ("promocao/0.47.2", "homolog", True), ("homolog", "main", True),
                                  ("promocao/0.47.2", "main", False), ("develop", "main", False), ("melhoria/y", "homolog", False),
                                  ("promocao/x", "homolog", False), ("promocao/0.47", "homolog", False),
                                  ("promocao/0.47.2-rc1", "homolog", False), ("promocao/0.47.2\n", "homolog", False),
                                  ("xdevelop", "homolog", False), ("homolog", "develop", False), (None, "homolog", False)):
            with self.subTest(head=head, base=base):
                self.assertEqual(catraca.linha_de_promocao(head, base) is not None, linha)


class Degrau(Repo):
    def degrau(self, ramo, base_ref, head, repo_head=REPO, repo_base=REPO):
        return catraca.violacoes_do_degrau(self.tmp, ramo, base_ref, head, repo_head, repo_base)

    def test_promocao_da_develop_e_do_ramo_da_marca_passam(self):
        self.assertEqual(self.degrau("develop", "homolog", self.na_develop), [])
        self.assertEqual(self.degrau("promocao/0.9.0", "homolog", self.na_develop), [])
        self.assertEqual(self.degrau("homolog", "main", self.fora), [])
        self.assertEqual(self.degrau("melhoria/x", "develop", self.fora), [])  # a develop não é degrau

    def test_head_fora_da_tabela_para_homolog_ou_main_e_recusado(self):
        for ramo, base_ref in (("melhoria/x", "homolog"), ("melhoria/x", "main"), ("develop", "main"), ("promocao/0.9.0", "main"),
                               ("promocao/x", "homolog")):
            with self.subTest(ramo=ramo, base=base_ref):
                viol = self.degrau(ramo, base_ref, self.na_develop)
                self.assertEqual(len(viol), 1)
                self.assertIn("fora da tabela de promoções", viol[0])

    def test_ramo_da_marca_fora_da_develop_ou_de_fork_e_recusado(self):
        self.assertTrue(self.degrau("promocao/0.9.0", "homolog", self.fora))
        self.assertTrue(self.degrau("promocao/0.9.0", "homolog", "f" * 40))
        self.assertTrue(self.degrau("promocao/0.9.0", "homolog", "--all"))
        self.assertTrue(self.degrau("promocao/0.9.0", "homolog", ""))
        self.assertTrue(self.degrau("promocao/0.9.0", "homolog", self.na_develop, repo_head="fork/forge"))
        self.assertTrue(self.degrau("develop", "homolog", self.na_develop, repo_head="fork/forge"))
        sem_repo = self.degrau("develop", "homolog", self.na_develop, repo_head="", repo_base="")
        self.assertEqual(len(sem_repo), 1)
        self.assertIn("(repositório desconhecido)", sem_repo[0])

    def test_sem_a_develop_do_servidor_o_ramo_da_marca_e_recusado(self):
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        self.assertTrue(self.degrau("promocao/0.9.0", "homolog", self.na_develop))
        self.assertEqual(self.degrau("develop", "homolog", self.na_develop), [])

    def test_modo_degrau_pela_linha_de_comando(self):
        env = {k: v for k, v in self.env.items() if k not in ("HEAD_REPO", "BASE_REPO", "GITHUB_STEP_SUMMARY", "GITHUB_ACTIONS")}

        def roda(ramo, base_ref, head):
            return subprocess.run([sys.executable, "-I", str(SCRIPT), "--modo", "degrau", "--raiz", str(self.tmp), "--ramo", ramo,
                                   "--base-ref", base_ref, "--head", head], env=dict(env, HEAD_REPO=REPO, BASE_REPO=REPO),
                                  capture_output=True, text=True, timeout=60)
        self.assertEqual(roda("promocao/0.9.0", "homolog", self.na_develop).returncode, 0)
        r = roda("melhoria/x", "homolog", self.fora)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("R-FLUXO", r.stdout)


class Promocao(Repo):
    def pr(self, ramo, base_ref, sha, repo_head=REPO):
        return {"head": {"ref": ramo, "sha": sha, "repo": {"full_name": repo_head}}, "base": {"ref": base_ref, "repo": {"full_name": REPO}}}

    def test_eh_promocao_reconhece_o_par_novo_nas_mesmas_condicoes(self):
        self.assertTrue(catraca.eh_promocao(self.pr("promocao/0.9.0", "homolog", self.na_develop), REPO, self.tmp))
        self.assertFalse(catraca.eh_promocao(self.pr("promocao/0.9.0", "homolog", self.fora), REPO, self.tmp))
        self.assertFalse(catraca.eh_promocao(self.pr("promocao/0.9.0", "homolog", self.na_develop, "fork/forge"), REPO, self.tmp))
        self.assertFalse(catraca.eh_promocao(self.pr("melhoria/x", "homolog", self.na_develop), REPO, self.tmp))

    def test_pareceres_nao_sao_exigidos_so_na_promocao_aceita(self):
        self.assertEqual(catraca._violacoes_de_pareceres(self.tmp, self.na_develop, self.na_develop, "promocao/0.9.0", "homolog"), [])

        class Conferiu(Exception):
            pass
        with mock.patch.object(catraca, "base_efetiva", side_effect=Conferiu):  # head fora da develop: a conferência começa
            with self.assertRaises(Conferiu):
                catraca._violacoes_de_pareceres(self.tmp, self.na_develop, self.fora, "promocao/0.9.0", "homolog")

    def test_arvore_testada_le_a_mesma_tabela(self):
        ci = f"{REPO}/.github/workflows/ci.yml@refs/heads/x"

        def env(head, sha):
            return {"REPO": REPO, "EVENTO": "pull_request", "BASE_REF": "homolog", "HEAD_REF": head, "HEAD_REPO": REPO,
                    "HEAD_SHA": sha, "REF": "", "GITHUB_WORKFLOW_REF": ci}
        self.assertTrue(at.evento_elegivel(env("promocao/0.9.0", self.na_develop), self.tmp)[0])
        self.assertFalse(at.evento_elegivel(env("promocao/0.9.0", self.fora), self.tmp)[0])
        self.assertFalse(at.evento_elegivel(env("melhoria/x", self.na_develop), self.tmp)[0])
        self.assertEqual(at.CATRACA.PROMOCOES, catraca.PROMOCOES)


if __name__ == "__main__":
    unittest.main()
