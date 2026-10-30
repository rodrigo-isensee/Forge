"""FECHAR-R1-WORKTREE (C1, C1-2 do modelo de ameaças): pendência por commit sem merge imprime leitura, não comando que apaga.

Vale para `limpar_entrega` (--limpar e passo 7) e para o bloco do `--sem-limpar`. Com sha mesclado nada muda (regressão).
Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

APAGAM = ("git worktree remove", "git branch -D", "git push origin --delete")
CONFIRA = "confira; só apague depois de decidir"


class SemMerge(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    setUp = base.Fechar.setUp
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    com_worktree = base.Fechar.com_worktree
    resumo = base.Fechar.resumo
    marcas = base.Fechar.marcas

    def pendentes(self, r):
        return r.stdout.split("pendente, rode:\n")[1].splitlines()

    def sem_comando_que_apaga(self, texto):
        for apaga in APAGAM:
            self.assertNotIn(apaga, texto)

    def test_limpar_com_commit_novo_na_worktree_imprime_leitura_e_nao_comando_que_apaga(self):  # AB-C1-1
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")  # PR antigo mesclado com o nome reaproveitado
        wt = self.com_worktree()
        (self.proj / ".git" / "info" / "exclude").write_text("*.local\n")
        (wt / "ambiente.local").write_text("conteudo que so existe aqui\n")
        (wt / "novo").write_text("trabalho novo\n")
        self.git("add", "novo", cwd=wt)
        self.git("commit", "-q", "-m", "feat: trabalho novo", cwd=wt)
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.sem_comando_que_apaga(r.stdout + r.stderr)
        self.assertIn("git log --oneline origin/develop..refs/heads/melhoria/x", self.pendentes(r))
        self.assertIn(CONFIRA, r.stdout)
        self.assertEqual((wt / "ambiente.local").read_text(), "conteudo que so existe aqui\n")
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "+ melhoria/x")

    def test_limpar_de_dentro_da_worktree_principal_com_commit_sem_merge_nao_manda_apagar(self):  # AB-C1-2
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "novo").write_text("trabalho novo\n")
        self.git("add", "novo")
        self.git("commit", "-q", "-m", "feat: trabalho novo")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("commit que não foi mesclado", r.stderr)
        self.sem_comando_que_apaga(r.stdout + r.stderr)
        self.assertIn("git log --oneline origin/develop..refs/heads/melhoria/x", self.pendentes(r))

    def test_limpar_com_remota_sem_merge_imprime_leitura_do_sha_remoto(self):  # AB-C1-3
        sha_remoto = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {self.git('rev-parse', 'develop')}\n")
        self.git("branch", "-q", "-D", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=ok branch=ok"])
        self.sem_comando_que_apaga(r.stdout + r.stderr)
        self.assertEqual(self.marcas("git push origin --delete"), [])
        self.assertIn(f"git log --oneline origin/develop..{sha_remoto}", self.pendentes(r))
        self.assertIn(CONFIRA, r.stdout)

    def test_sem_limpar_com_commit_local_depois_do_passo_2_imprime_leitura(self):  # AB-C1-4 (C1-2)
        wt = self.com_worktree()
        falso = self.tmp / "gh"
        falso.rename(self.tmp / "gh-base")
        # o commit entra durante o merge (a espera pode durar até 7200 s): depois do passo 2, que conferiu local == remoto
        falso.write_text(f'#!/usr/bin/env bash\n[ "$1 $2" = "pr merge" ] && git -C "{wt}" commit -q --allow-empty -m "feat: depois do passo 2"\n'
                         f'exec "{self.tmp / "gh-base"}" "$@"\n')
        falso.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        pendentes = self.pendentes(r)
        self.assertEqual(pendentes[0], "forge-fechar p1 --ref melhoria/x --limpar")
        self.sem_comando_que_apaga("\n".join(l for l in pendentes if "--delete refs/heads" not in l) + r.stderr)
        self.assertIn("git log --oneline origin/develop..refs/heads/melhoria/x", pendentes)
        self.assertIn("git push origin --delete refs/heads/melhoria/x", pendentes)  # a remota é o head mesclado: fica
        self.assertTrue(wt.exists())

    def test_ref_com_caractere_do_shell_sai_escapada_na_linha_de_leitura(self):  # AB-C1-5
        ref = "melhoria/a$b"
        self.git("switch", "-q", "-c", ref, "develop")
        (self.proj / "novo").write_text("trabalho novo\n")
        self.git("add", "novo")
        self.git("commit", "-q", "-m", "feat: novo")
        self.git("push", "-q", "origin", ref)
        self.git("switch", "-q", "develop")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {self.git('rev-parse', 'develop')}\n")
        r = self.fechar("p1", "--ref", ref, "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("git log --oneline origin/develop..refs/heads/melhoria/a\\$b", self.pendentes(r))
        self.sem_comando_que_apaga(r.stdout + r.stderr)

    def test_sha_mesclado_com_worktree_ocupada_continua_imprimindo_o_comando(self):  # AB-C1-6 (regressão)
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        wt = self.com_worktree()
        (self.estado / "wt_busy").write_text("persiste")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn(f"git worktree remove {wt}", self.pendentes(r))
        self.assertIn("git branch -D melhoria/x", self.pendentes(r))
        self.assertNotIn("git log --oneline", r.stdout)


if __name__ == "__main__":
    unittest.main()
