"""PREPUSH-REFS (v0457 E9.3, defesa D2 de docs/security/ameacas/v0457-hook-shell-pipe.md): a política de refs no laço
`while read` do pre-push do Forge e do modelo de projeto, igual nos dois. Vale para as refs reais do envio, qualquer que
seja a sintaxe: ref remota fora de refs/heads/ e refs/tags/ recusa; mais de uma branch com código no mesmo envio recusa;
mais de uma remoção no mesmo envio recusa (item 3 da D2, decisão do dono de 2026-11-10 23:45, que muda a PREPUSH-DELETE).

Os hooks em vigor só mudam pelo patch que o dono aplica (decisão 4a de 2026-11-12 11:22, R-CONFORMIDADE); o patch foi
aplicado na E9.4 e as classes rodam sem pulo.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOKS = {"forge": RAIZ / ".githooks" / "pre-push", "modelo": RAIZ / "templates" / "projeto" / ".githooks" / "pre-push"}
ZERO = "0" * 40
REF_FORA, DUAS_BRANCHES, DUAS_REMOCOES = "não é branch (refs/heads/) nem tag", "mais de uma branch com código", "mais de uma remoção"
RECUSAS = (REF_FORA, DUAS_BRANCHES, DUAS_REMOCOES)


class Base:
    """Repositório descartável com remoto bare; ambiente montado do zero (nada herdado além do PATH)."""
    HOOK = None

    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.base / "run").mkdir(mode=0o700)
        self.env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.base),
                                   "XDG_RUNTIME_DIR": str(self.base / "run"), "LC_ALL": "C.UTF-8",
                                   "GIT_TERMINAL_PROMPT": "0"})
        self.repo, self.remoto = self.base / "repo", self.base / "r.git"
        self.git("init", "-q", "--bare", str(self.remoto), cwd=self.base)
        remoto_sem_manutencao(self.remoto)
        self.git("init", "-q", "-b", "melhoria/a", str(self.repo), cwd=self.base)
        self.git("remote", "add", "origin", str(self.remoto))
        self.git("commit", "-q", "--allow-empty", "-m", "a")
        self.sha = self.git("rev-parse", "HEAD")

    def git(self, *args, cwd=None, check=True):
        r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
                           cwd=cwd or self.repo, env=self.env, capture_output=True, text=True, timeout=60)
        if check and r.returncode != 0:
            self.fail(f"git {args}: {r.stderr}")
        return r.stdout.strip() if check else r

    def roda(self, linhas, env=None):
        """Roda o hook com as linhas de refs no stdin, como o git faz."""
        r = subprocess.run([str(self.HOOK), "origin", str(self.remoto)], cwd=self.repo, env=env or self.env,
                           input="".join(f"{ln}\n" for ln in linhas), capture_output=True, text=True, timeout=120,
                           start_new_session=True)
        return r.returncode, r.stdout + r.stderr

    def envio(self, ref, sha=None):
        return f"refs/heads/x {sha or self.sha} {ref} {ZERO}"

    def remocao(self, ref):
        return f"(delete) {ZERO} {ref} {self.sha}"

    def push(self, *args):
        """Envio de verdade pelo git, com o hook em teste no core.hooksPath."""
        r = self.git("-c", f"core.hooksPath={self.HOOK.parent}", "push", "origin", *args, check=False)
        return r.returncode, r.stdout + r.stderr

    def refs_no_remoto(self):
        return sorted(self.git("--git-dir", str(self.remoto), "for-each-ref", "--format=%(refname)").split())

    def assertRecusa(self, resultado, texto):
        codigo, saida = resultado
        self.assertEqual((codigo != 0, texto in saida), (True, True), saida)


class Politica(Base):
    """As três recusas e o que segue livre, com as refs no stdin."""

    def test_ref_remota_fora_de_heads_e_tags_recusa(self):
        for ref in ("refs/remotes/origin/x", "refs/notes/commits", "refs/stash", "refs/pull/1/head", "refs/heads/", "x"):
            with self.subTest(ref):
                self.assertRecusa(self.roda([self.envio(ref)]), REF_FORA)
        self.assertRecusa(self.roda([self.remocao("refs/notes/commits")]), REF_FORA)

    def test_duas_branches_com_codigo_recusa(self):
        self.assertRecusa(self.roda([self.envio("refs/heads/melhoria/a"), self.envio("refs/heads/melhoria/b")]),
                          DUAS_BRANCHES)

    def test_duas_remocoes_recusa(self):
        for refs in (("refs/heads/melhoria/a", "refs/heads/melhoria/b"), ("refs/heads/melhoria/a", "refs/tags/v1"),
                     ("refs/tags/v1", "refs/tags/v2")):
            with self.subTest(refs):
                self.assertRecusa(self.roda([self.remocao(r) for r in refs]), DUAS_REMOCOES)

    def test_contadores_nao_vem_do_ambiente(self):
        env = dict(self.env, refs_branches="-9", refs_remocoes="-9")
        self.assertRecusa(self.roda([self.envio("refs/heads/melhoria/a"), self.envio("refs/heads/melhoria/b")], env),
                          DUAS_BRANCHES)
        self.assertRecusa(self.roda([self.remocao("refs/heads/a"), self.remocao("refs/heads/b")], env), DUAS_REMOCOES)

    def test_uma_remocao_passa(self):
        for ref in ("refs/heads/melhoria/a", "refs/tags/v1"):
            with self.subTest(ref):
                codigo, saida = self.roda([self.remocao(ref)])
                self.assertEqual(codigo, 0, saida)

    def test_branch_com_tags_e_uma_remocao_nao_recusa_pela_politica(self):
        """Uma branch com código, tags e uma remoção juntas: nenhuma das três recusas (tag não conta como branch)."""
        linhas = [self.envio("refs/heads/melhoria/a"), self.envio("refs/tags/v1"), self.envio("refs/tags/v2"),
                  self.remocao("refs/heads/melhoria/velha")]
        codigo, saida = self.roda(linhas)
        self.assertEqual([t for t in RECUSAS if t in saida], [], saida)
        if self.HOOK == HOOKS["modelo"]:  # o do Forge segue para as checagens do envio, fora do alcance deste teste
            self.assertEqual(codigo, 0, saida)


class EnvioDeVerdade(Base):
    """A política vale qualquer que seja a sintaxe: o git monta as refs e o hook recusa antes de o remoto mudar."""

    def setUp(self):
        super().setUp()
        self.git("branch", "melhoria/b")

    def test_branches_e_mirror_recusam_sem_mudar_o_remoto(self):
        for args in (("--branches",), ("--all",), ("--mirror",), ("melhoria/a", "melhoria/b")):
            with self.subTest(args):
                self.assertRecusa(self.push(*args), DUAS_BRANCHES)
                self.assertEqual(self.refs_no_remoto(), [])

    def test_ref_de_notas_recusa(self):
        self.assertRecusa(self.push("HEAD:refs/notes/x"), REF_FORA)
        self.assertEqual(self.refs_no_remoto(), [])

    def test_prune_com_curinga_nao_apaga_em_massa(self):
        for ref in ("melhoria/a", "melhoria/b", "melhoria/c"):  # o remoto já tem as três (o repositório novo não tem hook)
            self.git("push", "-q", str(self.remoto), f"{self.sha}:refs/heads/{ref}")
        antes = self.refs_no_remoto()
        self.git("checkout", "-q", "--detach")
        self.git("branch", "-D", "melhoria/b", "melhoria/a")
        self.assertRecusa(self.push("--prune", "refs/heads/melhoria/*:refs/heads/melhoria/*"), DUAS_REMOCOES)
        self.assertEqual(self.refs_no_remoto(), antes)

    def test_uma_branch_por_envio_passa(self):
        codigo, saida = self.push("melhoria/a")
        self.assertEqual([t for t in RECUSAS if t in saida], [], saida)
        if self.HOOK == HOOKS["modelo"]:
            self.assertEqual((codigo, self.refs_no_remoto()), (0, ["refs/heads/melhoria/a"]), saida)


class PoliticaForge(Politica, unittest.TestCase):
    HOOK = HOOKS["forge"]


class PoliticaModelo(Politica, unittest.TestCase):
    HOOK = HOOKS["modelo"]


class EnvioDeVerdadeForge(EnvioDeVerdade, unittest.TestCase):
    HOOK = HOOKS["forge"]


class EnvioDeVerdadeModelo(EnvioDeVerdade, unittest.TestCase):
    HOOK = HOOKS["modelo"]


if __name__ == "__main__":
    unittest.main()
