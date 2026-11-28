"""bin/forge-copia (v048 E4.1): a origem local clona do remoto dela (FORGE-COPIA-ORIGEM-LOCAL), a worktree parte da branch remota
e desfaz a branch que criou quando falha (FORGE-COPIA-FALHA-SEM-DESFAZER) e o clone D2 nasce destacado na base (FORGE-COPIA-D2)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge_copia import Base  # noqa: E402

AUTOR = ("-c", "user.name=t", "-c", "user.email=t@t")


class Comum(Base):
    def commit(self, repo, branch, msg):
        """Commit novo em `repo`, na branch dada (criada se falta); devolve o sha."""
        self.git(repo, "switch", "-q", "-C", branch)
        self.git(repo, *AUTOR, "commit", "-q", "--allow-empty", "-m", msg)
        return self.git(repo, "rev-parse", "HEAD").stdout.strip()

    def head(self, d):
        return self.git(d, "rev-parse", "HEAD").stdout.strip()

    def tem_ref(self, repo, ref):
        return self.git(repo, "for-each-ref", ref).stdout.strip() != ""


class OrigemLocal(Comum):
    """O repositório principal não faz fetch no sandbox: a develop dele fica velha e a branch remota falta nele."""

    def setUp(self):
        super().setUp()
        self.remoto = self.fora / "remoto"
        self.git(self.fora, "clone", "-q", str(self.origem), str(self.remoto))
        self.dev_remota = self.commit(self.remoto, "develop", "nova no remoto")
        self.branch_remota = self.commit(self.remoto, "melhoria/r", "r")
        self.git(self.remoto, "switch", "-q", "develop")
        self.git(self.origem, "remote", "set-url", "origin", str(self.remoto))

    def test_pasta_local_clona_da_url_do_remoto_e_parte_da_develop_dele(self):
        d = self.pasta / "o1"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), self.dev_remota)
        self.assertIn("clono do remoto origin dela", r.stderr)

    def test_branch_so_no_remoto_parte_do_head_remoto(self):
        d = self.pasta / "o2"
        r = self.copia("clone", str(d), "--branch", "melhoria/r", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), self.branch_remota)

    def test_url_relativa_vale_a_partir_da_origem(self):
        self.git(self.origem, "remote", "set-url", "origin", "../../../fora/remoto")
        d = self.pasta / "o3"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem), cwd=self.fora)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), self.dev_remota)

    def test_pasta_local_sem_remoto_origin_e_recusada(self):
        self.git(self.origem, "remote", "remove", "origin")
        d = self.pasta / "o4"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("pasta local sem remoto origin", r.stderr)
        self.assertFalse(d.exists())


class Worktree(Comum):
    def test_branch_que_ja_existe_no_remoto_parte_do_head_dela(self):
        remoto = self.commit(self.origem, "outra", "remota")
        self.git(self.origem, "switch", "-q", "develop")
        self.git(self.origem, "update-ref", "refs/remotes/origin/melhoria/w", remoto)
        d = self.pasta / "wt" / "w1"
        r = self.copia("worktree", str(d), "--branch", "melhoria/w")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), remoto)
        self.assertIn("já existe no remoto", r.stderr)

    def test_worktree_que_falha_apaga_a_branch_que_criou(self):
        (self.pasta / "arq").write_text("x")
        r = self.copia("worktree", str(self.pasta / "arq" / "w"), "--branch", "melhoria/w")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(self.tem_ref(self.origem, "refs/heads/melhoria/w"), "a branch criada pela worktree que falhou não fica")
        self.assertIn("apaguei a branch melhoria/w", r.stderr)

    def test_branch_que_ja_existia_fica_quando_a_worktree_falha(self):
        self.git(self.origem, "branch", "melhoria/w", "develop")
        r = self.copia("worktree", str(self.pasta / "wt" / "w2"), "--branch", "melhoria/w")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(self.tem_ref(self.origem, "refs/heads/melhoria/w"), "só a branch nova sai; a que já existia fica")

    def test_base_que_nao_existe_sai_1_com_as_refs_tentadas(self):
        r = self.copia("worktree", str(self.pasta / "wt" / "w3"), "--branch", "melhoria/w", "--base", "nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("nenhuma destas refs existe no clone: origin/melhoria/w, nada, origin/nada", r.stderr)
        self.assertFalse(self.tem_ref(self.origem, "refs/heads/melhoria/w"))


class D2(Comum):
    def test_clone_d2_nasce_destacado_na_develop_sem_branch(self):
        self.commit(self.origem, "main", "main")  # o clone nasce na main: a develop só existe como origin/develop
        dev = self.git(self.origem, "rev-parse", "develop").stdout.strip()
        d = self.pasta / "d2"
        r = self.copia("clone", str(d), "--origem", str(self.origem), "--d2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), dev)
        self.assertEqual(self.branch_de(d), "", "o clone D2 fica destacado")
        self.assertIn(f"criei o clone D2 destacado em {dev} (de origin/develop)", r.stderr)

    def test_branch_remota_chamada_none_nao_desvia_o_d2(self):
        dev = self.git(self.origem, "rev-parse", "develop").stdout.strip()
        self.commit(self.origem, "None", "none")
        self.git(self.origem, "switch", "-q", "develop")
        d = self.pasta / "d2n"
        r = self.copia("clone", str(d), "--origem", str(self.origem), "--d2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), dev)

    def test_d2_sem_a_base_apaga_o_clone(self):
        d = self.pasta / "d2b"
        r = self.copia("clone", str(d), "--origem", str(self.origem), "--d2", "--base", "origin/nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(d.exists())
        self.assertIn("não criei o clone D2: nenhuma destas refs existe no clone: origin/nada;", r.stderr)

    def test_d2_com_branch_revisao_ou_worktree_e_recusado(self):
        for extra in (["clone", "--origem", str(self.origem), "--branch", "melhoria/x"],
                      ["clone", "--origem", str(self.origem), "--revisao"], ["worktree"]):
            with self.subTest(extra=extra):
                d = self.pasta / "d2r"
                r = self.copia(extra[0], str(d), *extra[1:], "--d2")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("--d2 é só do clone", r.stderr)
                self.assertFalse(d.exists())

    def test_d2_em_destino_ocupado_sugere_nome_unico(self):
        (self.pasta / "d2").mkdir()
        (self.pasta / "d2" / "x").write_text("x")
        r = self.copia("clone", str(self.pasta / "d2"), "--origem", str(self.origem), "--d2")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'd2-2'}", r.stderr)


if __name__ == "__main__":
    unittest.main()
