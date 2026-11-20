"""AE1.1 (v0478 E58.1): `forge-check onde` (bin/forge_onde.py) diz onde está uma versão, um PR, um commit, uma branch ou um cartão,
lido do git e do gh; um teste por guarda, com o ramo de falha. O gh é um falso que confere o número e o `--head` exatos."""
import argparse
import contextlib
import io
import json
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

    def __init__(self, prs=(), erro="sem resposta em 10 s", repo=None):
        self.prs, self.erro, self.chamadas, self.repo = (None if prs is None else list(prs)), erro, [], repo

    def __call__(self, raiz, *args):
        self.chamadas.append(args)
        if self.prs is None:
            return None, self.erro
        if self.repo is not None and args[-2:] != ("--repo", self.repo):  # com `repo`, só responde preso a ele, como o gh com --repo
            return None, f"could not resolve to a Repository ({args[-1]})"
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

class ProvaDoMovimento(Base):
    """AE1.2 (E58.19): a `--prova` do movimento para Pronto ou Fechado*; um teste por guarda de `prova_do_movimento` e `prova_git`.
    O clone tem origin no GitHub (E58.29: caminho local não prova) e o gh falso só responde preso a ele."""

    REPO = "github.com/teste/forge"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.repo.git("remote", "add", "origin", "https://github.com/teste/forge.git")

    def prova(self, prova, cartao="AE1.1", gh=None, git=None, colunas=None, raiz=None):
        colunas = colunas or {}
        ctx = {"git": git or fc.git, "gh_json": gh if gh is not None else GhFalso(), "seguro": fc.sem_controle,
               "coluna": colunas.get, "final": fc.coluna_final, "desde": lambda c: "2026-11-20T09:00:00-03:00"}
        return O.prova_do_movimento(prova, cartao, raiz or self.repo.pasta, ctx)

    def gh(self, **extra):
        dados = {"number": 7, "state": "MERGED", "baseRefName": "develop", "headRefName": "melhoria/x", "mergedAt": "2026-11-20T10:00:00Z",
                 "mergedBy": {"login": "dono"}, "mergeCommit": {"oid": self.repo.c3}, "title": "feat: AE1.1 movimento", "body": ""}
        dados.update(extra)
        return GhFalso([dados], repo=self.REPO)

    def com_origin(self, cod, url):
        def git(raiz, *args, **kw):
            return (cod, url) if args == ("remote", "get-url", "origin") else fc.git(raiz, *args, **kw)
        return git

    def test_pr_mesclado_na_develop_que_cita_o_cartao_vale_com_o_sha(self):
        estado, texto = self.prova("pr:#7", gh=self.gh())
        self.assertEqual(estado, "ok", texto)
        self.assertIn(f"pr:#7 {self.repo.c3[:12]} origem={self.REPO} (onde: develop sim", texto)

    def test_origin_local_ou_ausente_recusa(self):  # E58.29 (segurança A2): o clone de caminho local ou file:// não prova
        for cod, url in ((0, "/tmp/remoto.git"), (0, "file:///tmp/remoto.git"), (2, "https://github.com/teste/forge.git"), (0, "http://exemplo.test/o/r.git"),
                         (0, "https://github.com/so-dono")):
            for prova in (f"commit:{self.repo.c3}", "pr:#7"):
                with self.subTest(url=url, prova=prova):
                    estado, texto = self.prova(prova, gh=self.gh(), git=self.com_origin(cod, url))
                    self.assertEqual((estado, "sem origin https ou ssh" in texto), ("recusa", True), texto)

    def test_origin_ssh_ou_com_credencial_vale_e_a_linha_leva_so_o_repositorio(self):
        for url, repo in (("git@github.com:teste/forge.git", self.REPO), ("https://x-token:segredo@github.com/teste/forge", self.REPO),
                          ("ssh://git@github.com/teste/forge.git", self.REPO)):
            with self.subTest(url=url):
                estado, texto = self.prova(f"commit:{self.repo.c3}", git=self.com_origin(0, url))
                self.assertEqual(estado, "ok", texto)
                self.assertIn(f" origem={repo} ", texto)
                self.assertNotIn("segredo", texto)

    def test_pr_lido_no_repositorio_do_origin(self):  # o gh preso ao origin: o PR 7 de outro repositório não prova
        estado, texto = self.prova("pr:#7", gh=self.gh(), git=self.com_origin(0, "https://github.com/outro/repo.git"))
        self.assertEqual((estado, "github.com/outro/repo" in texto), ("nao-verificavel", True), texto)
        falso = self.gh()
        self.assertEqual(self.prova("pr:#7", gh=falso)[0], "ok")
        self.assertEqual([a[-2:] for a in falso.chamadas], [("--repo", self.REPO)] * 2)

    def test_pr_de_outro_cartao_recusa(self):
        estado, texto = self.prova("pr:#7", gh=self.gh(title="feat: AE10 e AE1.1x", body="XAE1.1"))
        self.assertEqual((estado, "não cita o cartão AE1.1" in texto), ("recusa", True), texto)

    def test_pr_nao_mesclado_recusa(self):
        estado, texto = self.prova("pr:7", gh=self.gh(state="OPEN", mergedAt=None, mergeCommit=None))
        self.assertEqual((estado, "não está na develop" in texto), ("recusa", True), texto)

    def test_pr_mesclado_em_outra_base_recusa_mesmo_com_o_commit_na_develop(self):
        estado, texto = self.prova("pr:#7", gh=self.gh(baseRefName="homolog", mergeCommit={"oid": self.repo.c2}))
        self.assertEqual(estado, "recusa", texto)

    def test_pr_cujo_merge_nao_esta_na_develop_recusa(self):
        estado, texto = self.prova("pr:#7", gh=self.gh(mergeCommit={"oid": self.repo.c4}))
        self.assertEqual((estado, "não está na develop" in texto), ("recusa", True), texto)

    def test_gh_fora_do_ar_e_nao_verificavel(self):
        estado, texto = self.prova("pr:#7", gh=GhFalso(None))
        self.assertEqual((estado, "sem resposta em 10 s" in texto), ("nao-verificavel", True), texto)

    def test_titulo_do_pr_sem_leitura_e_nao_verificavel(self):
        falso = self.gh()

        def gh(raiz, *args):
            if "number,title,body" in args:
                return {"number": 8, "title": "AE1.1"}, "outro PR"
            return falso(raiz, *args)

        estado, texto = self.prova("pr:#7", gh=gh)
        self.assertEqual((estado, "sem título lido" in texto), ("nao-verificavel", True), texto)

    def test_commit_na_develop_que_cita_o_cartao_vale(self):
        estado, texto = self.prova(f"commit:{self.repo.c3[:10]}")
        self.assertEqual(estado, "ok", texto)
        self.assertIn(self.repo.c3[:12], texto)

    def test_commit_que_nao_cita_o_cartao_recusa(self):
        self.assertEqual(self.prova(f"commit:{self.repo.c3}", cartao="AE1")[0], "recusa")  # c3 cita AE10, AE1.1 e XAE1, nunca AE1

    def test_commit_cujo_log_falha_recusa(self):
        def git(raiz, *args, **kw):
            return (128, "AE1.1") if args[0] == "log" else fc.git(raiz, *args, **kw)

        self.assertEqual(self.prova(f"commit:{self.repo.c3}", git=git)[0], "recusa")

    def test_commit_fora_da_develop_inexistente_ou_fora_da_forma_recusa(self):
        for prova in (f"commit:{self.repo.c4}", "commit:" + "e" * 40, "commit:-x", "commit:AE1.1", "pr:-1", "pr:#7 x"):
            with self.subTest(prova=prova):
                self.assertEqual(self.prova(prova, gh=self.gh())[0], "recusa")

    def test_nao_verificavel_traz_a_linha_que_falhou(self):
        def git(raiz, *args, **kw):
            return (128, "") if args[0] == "merge-base" and args[-1] == self.repo.c3 else fc.git(raiz, *args, **kw)

        estado, texto = self.prova(f"commit:{self.repo.c3}", git=git)
        self.assertEqual(estado, "nao-verificavel")
        self.assertTrue(texto.startswith("onde: develop nao-verificavel"), texto)

    def test_git_sem_resposta_e_nao_verificavel(self):
        def git(raiz, *args, **kw):
            raise subprocess.TimeoutExpired("git", 1)

        self.assertEqual(self.prova(f"commit:{self.repo.c3}", git=git), ("nao-verificavel", "git sem resposta"))

    def test_rodar_so_do_mesmo_cartao_e_da_mesma_raiz(self):  # E58.29 (segurança A1): o run.json grava o cartão e a raiz
        with tempfile.TemporaryDirectory() as tmp:
            raiz, fora = Path(tmp) / "r", Path(tmp) / "fora"
            r, f = str(raiz.resolve()), str(fora.resolve())
            for pasta, slug, dados in ((raiz, "ok", {"rc": 0, "head": "abc", "cartao": "AE1.1", "raiz": r}),
                                       (raiz, "falhou", {"rc": 1, "cartao": "AE1.1", "raiz": r}),
                                       (raiz, "outro", {"rc": 0, "cartao": "AE1", "raiz": r}), (raiz, "sem", {"rc": 0, "raiz": r}),
                                       (raiz, "clone", {"rc": 0, "cartao": "AE1.1", "raiz": f}), (raiz, "lixo", "{"), (raiz, "lista", [0]),
                                       (fora, "alheio", {"rc": 0, "cartao": "AE1.1", "raiz": f})):
                (pasta / ".forge" / "run" / slug).mkdir(parents=True)
                (pasta / ".forge" / "run" / slug / "run.json").write_text(dados if isinstance(dados, str) else json.dumps(dados),
                                                                          encoding="utf-8")
            (raiz / ".forge" / "run" / "link").symlink_to(fora / ".forge" / "run" / "alheio")
            self.assertEqual(self.prova("rodar:ok", raiz=raiz), ("ok", f"rodar:ok rc=0 head=abc raiz={r}"))  # a linha leva a raiz lida
            for slug, motivo in (("outro", "não é do cartão AE1.1"), ("sem", "não é do cartão AE1.1"), ("clone", "gravado em outra raiz"),
                                 ("lista", "fora da forma"), ("falhou", "rc=1"), ("lixo", "ilegível"), ("link", "link simbólico"),
                                 ("nada", "sem run.json"), ("../../fora/.forge/run/alheio", "sem run.json"), ("Ok", "sem run.json")):
                with self.subTest(slug=slug):
                    estado, texto = self.prova(f"rodar:{slug}", raiz=raiz)
                    self.assertEqual((estado, motivo in texto), ("recusa", True), texto)

    def test_rodar_do_forge_check_grava_o_cartao_e_a_raiz_que_a_prova_confere(self):  # E58.29: o caminho real, sem run.json à mão
        env = sem_git_herdado({k: v for k, v in os.environ.items() if not k.startswith(("FORGE_", "PYTHON"))})
        with tempfile.TemporaryDirectory() as tmp:
            for args in (["--cartao", "AE1.1", "com"], ["sem"], ["--cartao", "a;b", "torto"]):
                r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "rodar", *args, "--", sys.executable, "-I", "-c", "pass"],
                                   cwd=tmp, capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
                self.assertEqual(r.returncode, 2 if args[-1] == "torto" else 0, r.stdout + r.stderr)
            self.assertFalse((Path(tmp) / ".forge" / "run" / "torto").exists())
            self.assertEqual(self.prova("rodar:com", raiz=tmp)[0], "ok")
            self.assertEqual(self.prova("rodar:com", cartao="AE1", raiz=tmp)[0], "recusa")
            self.assertEqual(self.prova("rodar:sem", raiz=tmp)[0], "recusa")

    def test_juntado_so_em_outro_cartao_ativo(self):
        colunas = {"AE9": "Em andamento", "AE8": "Pronto", "AE7": "Fechado sem entrega", "AE1.1": "Em andamento"}
        self.assertEqual(self.prova("juntado:AE9", colunas=colunas),
                         ("ok", "juntado:AE9 (em Em andamento, no quadro desde 2026-11-20T09:00:00-03:00)"))  # E58.29: o destino para a auditoria
        for alvo in ("AE8", "AE7", "AE1.1", "ae1.1", "AE6", "-x"):
            with self.subTest(alvo=alvo):
                self.assertEqual(self.prova(f"juntado:{alvo}", colunas=colunas)[0], "recusa")

    def test_tipo_sem_leitor_recusa(self):
        for prova in ("ruleset:develop", "dono-disse:10h", "", "#7"):
            with self.subTest(prova=prova):
                self.assertEqual(self.prova(prova, gh=self.gh())[0], "recusa")


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
