"""AE1.1 (v0478 E58.1): `forge-check onde` (bin/forge_onde.py) diz onde está uma versão, um PR, um commit, uma branch ou um cartão,
lido do git e do gh; um teste por guarda, com o ramo de falha. O gh é um falso que confere o número e o `--head` exatos."""
import argparse
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_git_herdado, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
sys.path.insert(0, str(RAIZ / "bin"))
import forge_onde as O  # noqa: E402

fc = SourceFileLoader("forge_check_onde", str(FORGE_CHECK)).load_module()


class Repo:
    """c1 (tag v0.1.0) em origin/main; c2 cita AE1 em origin/homolog; c3 cita só AE10, AE1.1 e XAE1 em origin/develop; a branch local
    melhoria/x tem c4 sobre c2 (1 à frente e 1 atrás da develop)."""

    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.git("init", "-q", "-b", "main")
        self.c1 = self.commit("c1", "chore: inicio")
        self.git("tag", "v0.1.0")
        self.c2 = self.commit("c2", "feat: AE1 coisa (#5)")
        self.c3 = self.commit("c3", "fix: AE10, AE1.1 e XAE1 sem o outro")
        self.git("switch", "-q", "-c", "melhoria/x", self.c2)
        self.c4 = self.commit("c4", "feat: na branch")
        self.git("switch", "-q", "main")
        self.git("reset", "-q", "--hard", self.c1)
        for base, sha in (("main", self.c1), ("homolog", self.c2), ("develop", self.c3)):
            self.git("update-ref", f"refs/remotes/origin/{base}", sha)

    def git(self, *args):
        env = sem_manutencao(sem_git_herdado())
        env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        return subprocess.run(["git", "-C", str(self.pasta), *args], check=True, capture_output=True, text=True, env=env).stdout.strip()

    def commit(self, nome, mensagem):
        (self.pasta / nome).write_text(nome, encoding="utf-8")
        self.git("add", nome)
        self.git("commit", "-q", "-m", mensagem)
        return self.git("rev-parse", "HEAD")


class GhFalso:
    """Responde só ao número exato (`pr view`) e ao `--head` exato (`pr list`), como o gh; `None` imita a falha (teto ou rede)."""

    def __init__(self, prs=(), erro="sem resposta em 10 s"):
        self.prs, self.erro, self.chamadas = (None if prs is None else list(prs)), erro, []

    def __call__(self, raiz, *args):
        self.chamadas.append(args)
        if self.prs is None:
            return None, self.erro
        if args[:2] == ("pr", "view"):
            achado = [p for p in self.prs if str(p["number"]) == args[2]]
            return (achado[0], "") if achado else (None, f"no pull requests found for {args[2]}")
        if args[:2] == ("pr", "list"):
            cabeca = args[args.index("--head") + 1]
            return [p for p in self.prs if p.get("headRefName") == cabeca], ""
        return None, "comando inesperado"


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Repo(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def onde(self, alvo, gh=None, git=None):
        self.chamadas_git = []

        def espia(raiz, *args, **kw):
            self.chamadas_git.append(args)
            return (git or fc.git)(raiz, *args, **kw)

        ctx = {"git": espia, "gh_json": gh if gh is not None else GhFalso(), "seguro": fc.sem_controle}
        rc, linhas = O.onde(alvo, self.repo.pasta, ctx)
        return rc, "\n".join(linhas)


class Alvo(Base):
    def test_entrada_invalida_nao_chega_ao_git(self):
        for alvo in ("-x", "--output=/tmp/x", "a..b/c", "branch:a..b", "branch:-x", "branch:a/", "branch:a.lock", "branch:a//b",
                     "branch:", "develop", "#", "pr:", "v1.2", "ae1", "x y/z"):
            with self.subTest(alvo=alvo):
                rc, saida = self.onde(alvo)
                self.assertEqual(rc, 2)
                self.assertIn("alvo inválido", saida)
                self.assertEqual(self.chamadas_git, [])

    def test_branch_com_prefixo_e_sem_barra(self):
        self.assertEqual(O.tipo_do_alvo("branch:develop"), ("branch", "develop"))
        self.assertEqual(O.tipo_do_alvo("melhoria/x"), ("branch", "melhoria/x"))
        self.assertEqual(O.tipo_do_alvo("#705"), ("pr", "705"))
        self.assertEqual(O.tipo_do_alvo("pr:#705"), ("pr", "705"))
        self.assertEqual(O.tipo_do_alvo("AE1.1"), ("cartao", "AE1.1"))


class VersaoECommit(Base):
    def test_versao_presente_nas_tres_bases(self):
        rc, saida = self.onde("v0.1.0")
        self.assertEqual(rc, 0)
        for base in ("develop", "homolog", "main"):
            self.assertIn(f"onde: {base} sim (origin/{base} @", saida)

    def test_rev_parse_com_saida_que_nao_e_sha_nao_vale(self):
        def git(raiz, *args, **kw):
            return (0, "lixo") if args[0] == "rev-parse" else fc.git(raiz, *args, **kw)

        rc, saida = self.onde("v0.1.0", git=git)
        self.assertEqual(rc, 1)
        self.assertNotIn(" sim", saida)

    def test_versao_sem_tag_nao_existe(self):
        rc, saida = self.onde("v9.9.9")
        self.assertEqual(rc, 1)
        self.assertIn("nao-existe", saida)
        self.assertNotIn(" sim", saida)

    def test_commit_curto_so_na_develop(self):
        rc, saida = self.onde(self.repo.c3[:9])
        self.assertEqual(rc, 0)
        self.assertIn("onde: develop sim", saida)
        self.assertIn("onde: homolog nao", saida)
        self.assertIn("onde: main nao", saida)

    def test_sha_curto_com_tag_de_mesmo_nome_e_nao_verificavel(self):
        curto = self.repo.c1[:9]
        self.repo.git("tag", curto, self.repo.c3)  # o git prefere a ref ao objeto: lê c3 pedindo c1
        self.addCleanup(self.repo.git, "tag", "-d", curto)
        rc, saida = self.onde(curto)
        self.assertEqual(rc, 2)
        self.assertIn(f"onde: commit {curto} nao-verificavel (sha ambíguo com ref: leu {self.repo.c3[:12]})", saida)
        self.assertNotIn(" sim", saida)

    def test_git_sem_resposta_sai_rc_2_nao_1(self):
        def git(raiz, *args, **kw):
            raise subprocess.TimeoutExpired(["git", "-C", str(raiz), *args], 5)

        ctx = {"git": git, "gh_json": GhFalso(), "seguro": fc.sem_controle}
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            rc = O.executar(argparse.Namespace(alvo=self.repo.c1), self.repo.pasta, ctx)
        self.assertEqual(rc, 2)
        self.assertEqual(saida.getvalue(), "onde: nao-verificavel (git sem resposta)\n")

    def test_merge_base_que_falha_e_nao_verificavel_nunca_sim(self):
        def git(raiz, *args, **kw):
            return (128, "") if args[0] == "merge-base" else fc.git(raiz, *args, **kw)

        rc, saida = self.onde(self.repo.c1, git=git)
        self.assertEqual(rc, 2)
        self.assertEqual(saida.count("nao-verificavel"), 3)
        self.assertNotIn(" sim", saida)

    def test_sem_nenhuma_base_no_clone_e_nao_verificavel(self):
        def git(raiz, *args, **kw):
            return (1, "") if any("refs/remotes/origin/" in str(a) for a in args) else fc.git(raiz, *args, **kw)

        rc, saida = self.onde(self.repo.c1, git=git)
        self.assertEqual(rc, 2)
        self.assertEqual(saida.count("sem-branch"), 3)

    def test_uma_base_ausente_nao_derruba_o_rc(self):
        def git(raiz, *args, **kw):
            return (1, "") if any("origin/homolog" in str(a) for a in args) else fc.git(raiz, *args, **kw)

        rc, saida = self.onde(self.repo.c1, git=git)
        self.assertEqual(rc, 0)
        self.assertIn("onde: homolog sem-branch", saida)


class Pr(Base):
    def pr(self, **extra):
        dados = {"number": 7, "state": "MERGED", "baseRefName": "develop", "headRefName": "melhoria/x", "mergedAt": "2026-11-20T10:00:00Z",
                 "mergedBy": {"login": "dono"}, "mergeCommit": {"oid": self.repo.c3}}
        dados.update(extra)
        return GhFalso([dados])

    def test_pr_mesclado_e_onde_o_commit_esta(self):
        rc, saida = self.onde("#7", gh=self.pr())
        self.assertEqual(rc, 0)
        self.assertIn("onde: pr #7 estado=MERGED base=develop head=melhoria/x mesclado=2026-11-20T10:00:00Z por=dono", saida)
        self.assertIn("onde: develop sim", saida)
        self.assertIn("onde: main nao", saida)

    def test_gh_lento_e_nao_verificavel_nunca_sim(self):
        rc, saida = self.onde("pr:7", gh=GhFalso(None))
        self.assertEqual(rc, 2)
        self.assertIn("onde: pr #7 nao-verificavel (sem resposta em 10 s)", saida)
        self.assertNotIn(" sim", saida)

    def test_resposta_de_outro_pr_nao_vale(self):
        falso = self.pr()
        falso.prs[0]["number"] = 8
        rc, saida = self.onde("#7", gh=lambda raiz, *a: (falso.prs[0], ""))
        self.assertEqual(rc, 2)
        self.assertIn("onde: pr #7 nao-verificavel (resposta sem o PR)", saida)
        self.assertNotIn(" sim", saida)

    def test_pr_mesclado_sem_commit_do_merge_e_nao_verificavel(self):
        rc, saida = self.onde("#7", gh=self.pr(mergeCommit=None))
        self.assertEqual(rc, 2)
        self.assertIn("onde: commit - nao-verificavel (ausente no clone; rode git fetch)", saida)
        rc, saida = self.onde("#7", gh=self.pr(mergeCommit={"oid": None}))
        self.assertIn("onde: commit - nao-verificavel", saida)

    def test_commit_do_merge_que_nao_e_sha_nao_vira_ref(self):
        rc, saida = self.onde("#7", gh=self.pr(mergeCommit={"oid": "main"}))
        self.assertEqual(rc, 2)
        self.assertNotIn(" sim", saida)

    def test_pr_aberto_nao_le_as_bases(self):
        rc, saida = self.onde("#7", gh=self.pr(state="OPEN", mergedAt=None, mergedBy=None, mergeCommit=None))
        self.assertEqual(rc, 0)
        self.assertIn("estado=OPEN base=develop head=melhoria/x mesclado=- por=-", saida)
        self.assertNotIn("onde: develop", saida)

    def test_commit_do_merge_fora_do_clone_e_nao_verificavel(self):
        rc, saida = self.onde("#7", gh=self.pr(mergeCommit={"oid": "f" * 40}))
        self.assertEqual(rc, 2)
        self.assertIn("ausente no clone", saida)
        self.assertNotIn(" sim", saida)

    def test_texto_do_gh_sai_sem_controle(self):
        rc, saida = self.onde("#7", gh=self.pr(headRefName="a\x1b[31m\nonde: main sim b"))
        self.assertEqual(rc, 0)
        self.assertNotIn("\x1b", saida)
        self.assertNotIn(" ", saida)
        self.assertFalse(any(linha.startswith("onde: main sim") for linha in saida.splitlines()))


class Branch(Base):
    def test_branch_local_frente_atras_e_pr_de_nome_exato(self):
        gh = GhFalso([{"number": 1, "state": "OPEN", "baseRefName": "develop", "headRefName": "melhoria/x-outra", "mergedAt": None},
                      {"number": 2, "state": "CLOSED", "baseRefName": "develop", "headRefName": "melhoria/x", "mergedAt": None}])
        rc, saida = self.onde("melhoria/x", gh=gh)
        self.assertEqual(rc, 0)
        self.assertIn(f"onde: branch melhoria/x @{self.repo.c4[:12]}", saida)
        self.assertIn("onde: develop frente=1 atras=1", saida)
        self.assertIn("onde: pr #2 estado=CLOSED", saida)
        self.assertNotIn("#1", saida)

    def test_resposta_do_gh_com_outra_branch_fica_fora(self):
        alheio = ["lixo", {"number": 1, "state": "MERGED", "baseRefName": "develop", "headRefName": "melhoria/x-outra", "mergedAt": "x"}]
        rc, saida = self.onde("melhoria/x", gh=lambda raiz, *a: (alheio, ""))
        self.assertEqual(rc, 0)
        self.assertIn("onde: pr nenhum", saida)

    def test_branch_sem_pr(self):
        rc, saida = self.onde("branch:melhoria/x")
        self.assertEqual(rc, 0)
        self.assertIn("onde: pr nenhum", saida)

    def test_gh_fora_do_ar_e_nao_verificavel(self):
        rc, saida = self.onde("melhoria/x", gh=GhFalso(None, "gh não encontrado"))
        self.assertEqual(rc, 2)
        self.assertIn("onde: pr nao-verificavel (gh não encontrado)", saida)
        rc, saida = self.onde("melhoria/x", gh=GhFalso(None, ""))
        self.assertEqual(rc, 2)
        self.assertIn("onde: pr nao-verificavel (resposta ilegível)", saida)

    def test_branch_inexistente(self):
        rc, saida = self.onde("melhoria/nao-ha")
        self.assertEqual(rc, 1)
        self.assertIn("nao-existe", saida)

    def test_branch_de_origin_vence_a_local(self):
        self.repo.git("update-ref", "refs/remotes/origin/melhoria/y", self.repo.c3)
        self.repo.git("branch", "-f", "melhoria/y", self.repo.c1)
        rc, saida = self.onde("melhoria/y")
        self.assertIn(f"onde: branch origin/melhoria/y @{self.repo.c3[:12]}", saida)
        self.assertIn("onde: develop frente=0 atras=0", saida)

    def test_contagem_ilegivel_ou_que_falha_nao_imprime_frente(self):
        for resposta in ((0, "lixo"), (128, "3 4")):
            def git(raiz, *args, **kw):
                return resposta if args[0] == "rev-list" else fc.git(raiz, *args, **kw)

            with self.subTest(resposta=resposta):
                rc, saida = self.onde("melhoria/x", git=git)
                self.assertEqual(rc, 0)
                self.assertNotIn("frente=", saida)


class Cartao(Base):
    def test_id_inteiro_e_o_commit_mais_novo_de_cada_base(self):
        rc, saida = self.onde("AE1")
        self.assertEqual(rc, 0)
        self.assertIn(f"onde: develop sim (commit {self.repo.c2[:12]})", saida)
        self.assertIn(f"onde: homolog sim (commit {self.repo.c2[:12]})", saida)
        self.assertIn("onde: main nao (nenhum commit cita AE1)", saida)

    def test_id_mais_longo_casa_so_o_proprio(self):
        rc, saida = self.onde("AE1.1")
        self.assertEqual(rc, 0)
        self.assertIn(f"onde: develop sim (commit {self.repo.c3[:12]})", saida)
        self.assertIn("onde: homolog nao", saida)

    def test_cartao_sem_commit_nao_existe(self):
        rc, saida = self.onde("AE7")
        self.assertEqual(rc, 1)
        self.assertNotIn(" sim", saida)

    def test_git_log_que_falha_e_nao_verificavel(self):
        def git(raiz, *args, **kw):
            return (128, "") if args[0] == "log" else fc.git(raiz, *args, **kw)

        rc, saida = self.onde("AE1", git=git)
        self.assertEqual(rc, 2)
        self.assertEqual(saida.count("nao-verificavel"), 3)

    def test_sem_base_no_clone_e_nao_verificavel(self):
        def git(raiz, *args, **kw):
            return (1, "") if any("refs/remotes/origin/" in str(a) for a in args) else fc.git(raiz, *args, **kw)

        rc, _ = self.onde("AE7", git=git)
        self.assertEqual(rc, 2)


class PeloForgeCheck(Base):
    def test_subcomando_onde_imprime_e_sai_com_o_rc(self):
        env = sem_git_herdado({k: v for k, v in os.environ.items() if not k.startswith(("FORGE_", "PYTHON"))})
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "onde", "v0.1.0", "--raiz", str(self.repo.pasta)],
                           capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("onde: main sim (origin/main @", r.stdout)
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "onde", "a..b/c", "--raiz", str(self.repo.pasta)],
                           capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
