"""N-FECHAR-a, A1: registro órfão com o prune negado e comandos pendentes escapados em `bin/forge-fechar`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
import os
import shutil
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
SCRIPT = base.SCRIPT
GIT_PRUNE = r'''#!/usr/bin/env bash
if [ "$1 $2" = "worktree prune" ] && [ -f "$ESTADO/prune_nega" ]; then
  echo "git $*" >> "$REGISTRO"
  echo "error: cannot prune: operation not permitted" >&2; exit 1
fi
exec "$(dirname "$0")/git-base" "$@"
'''


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    com_worktree = base.Fechar.com_worktree
    resumo = base.Fechar.resumo
    marcas = base.Fechar.marcas
    log_de = base.Fechar.log_de
    arvores = base.Fechar.arvores

    def setUp(self):
        base.Fechar.setUp(self)
        # o `prune` pode ser negado ($ESTADO/prune_nega, como no sandbox); o resto vai para o git falso da suíte
        bin_ = self.tmp / "bin"
        (bin_ / "git").rename(bin_ / "git-base")
        (bin_ / "git").write_text(GIT_PRUNE, encoding="utf-8")
        (bin_ / "git").chmod(0o755)

    # ---- N-FECHAR-a, A1: registro órfão com o prune negado; comandos impressos escapados ----
    def test_c3_prune_negado_com_diretorio_ausente_imprime_prune_e_nao_remove(self):
        wt = self.com_worktree()
        (self.estado / "wt_busy").write_text("apaga")
        (self.estado / "prune_nega").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        pendentes = r.stdout.split("pendente, rode:\n")[1].splitlines()
        self.assertIn("git worktree prune", pendentes)
        self.assertFalse(any(l.startswith("git worktree remove") for l in pendentes), pendentes)
        self.assertIn("registro órfão", r.stderr)
        self.assertIn("repositório todo", r.stderr)
        self.assertFalse(wt.exists())
        self.assertEqual(len(self.marcas("git branch -D")), 0)  # a branch local espera o registro sumir
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 3"))

    def test_c3_prune_automatico_lista_no_log_o_que_removeu(self):
        self.com_worktree()
        outra = self.tmp / "wt-outra"
        self.git("worktree", "add", "-q", "-b", "melhoria/outra", str(outra))
        shutil.rmtree(outra)  # diretório ausente com registro: o prune do repositório tira este também
        (self.estado / "wt_busy").write_text("apaga")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.marcas("git worktree prune -v")), 1)
        self.assertIn("Removing worktrees/wt-outra", self.log_de(r).read_text())
        self.assertEqual(self.git("branch", "--list", "melhoria/outra"), "melhoria/outra")  # só o registro some

    def argumentos_da_linha(self, linha):
        """Roda a linha impressa com `git` trocado por um eco dos argumentos, como faria quem a cola no shell."""
        r = subprocess.run(["bash", "-c", 'git() { printf "%s\\n" "$@"; }\n' + linha], capture_output=True, text=True,
                           cwd=self.tmp, env={"PATH": os.environ["PATH"]})
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.splitlines()

    def test_c3_comandos_pendentes_escapam_o_nome_da_branch_e_o_caminho_da_worktree(self):
        ref = "melhoria/y;echo$IFS/p"
        self.git("switch", "-q", "-c", ref)
        (self.proj / "c").write_text("3\n")
        self.git("add", "c")
        self.git("commit", "-q", "-m", "feat: c")
        self.git("push", "-q", "origin", ref)
        self.git("switch", "-q", "develop")
        wt = self.tmp / "wt com espaço;z"
        self.git("worktree", "add", "-q", str(wt), ref)
        (self.estado / "wt_busy").write_text("persiste")
        (self.estado / "falha_delete").write_text("3")
        r = self.fechar("p1", "--ref", ref)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=pendente branch=pendente"])
        linhas = [l for l in r.stdout.split("pendente, rode:\n")[1].splitlines() if l.startswith("git ")]
        esperado = [["worktree", "remove", str(wt)], ["branch", "-D", ref], ["push", "origin", "--delete", f"refs/heads/{ref}"]]
        self.assertEqual([self.argumentos_da_linha(l) for l in linhas], esperado)
        self.assertTrue(wt.exists())  # o caminho com espaço foi lido inteiro (o awk antigo cortava no espaço)
        final = [l for l in r.stdout.splitlines() if "ou forge-fechar" in l][0]  # o aviso final também é colado: ref escapado
        self.assertEqual(self.argumentos_da_linha("forge-fechar() { printf '%s\\n' \"$@\"; }; " + final.split("ou ")[1].rstrip(".")),
                         ["p1", "--ref", ref, "--limpar"])

    # ---- LOTE-FECHAR-031, E2: rodado de dentro da worktree da própria branch ----
    def test_de_dentro_da_worktree_da_branch_sai_para_a_principal_remove_e_fecha_com_0(self):
        wt = self.com_worktree()
        r = base.subprocess.run(["bash", str(SCRIPT), "p1", "--ref", "melhoria/x"], cwd=wt, env=self.env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertIn(f"registro: saí da worktree de melhoria/x para a principal: {self.proj}", r.stdout)
        self.assertNotIn("saia dela", r.stderr)
        self.assertFalse(wt.exists())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")
        self.assertEqual(len(self.arvores()), 1)
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 0"))

    def test_de_dentro_da_worktree_com_commit_nao_mesclado_continua_pendente_sem_apagar(self):
        # --limpar com o PR MERGED no head antigo: o passo 7 roda de dentro da worktree e só a guarda de sha impede o `worktree remove`
        sha_mesclado = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha_mesclado}\n")
        wt = self.com_worktree()
        (wt / "c").write_text("3\n")
        self.git("add", "c", cwd=wt)
        self.git("commit", "-q", "-m", "feat: c", cwd=wt)
        r = self.fechar_em(wt, "p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.assertIn("tem commit que não foi mesclado", r.stderr)
        self.assertEqual(self.marcas("git worktree remove"), [])
        self.assertTrue(wt.exists())
        self.assertIn("melhoria/x", self.git("branch", "--list", "melhoria/x"))

    def fechar_em(self, cwd, *args):
        return base.subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd, env=self.env, capture_output=True, text=True, timeout=60)

    # ---- LOTE-FECHAR-031, E3: --sem-limpar ----
    def test_sem_limpar_mescla_pula_o_passo_7_imprime_os_comandos_e_sai_com_3(self):
        wt = self.com_worktree()
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn(f"gh pr merge melhoria/x --squash --match-head-commit {sha}", self.chamadas())
        self.assertEqual(self.resumo(r), ["limpeza: pulada (--sem-limpar)"])
        pendentes = r.stdout.split("pendente, rode:\n")[1].splitlines()
        self.assertEqual(pendentes[:4], ["forge-fechar p1 --ref melhoria/x --limpar", f"git worktree remove {wt}",
                                        "git branch -D melhoria/x", "git push origin --delete refs/heads/melhoria/x"])
        self.assertEqual(len(self.marcas("git branch -D")), 0)
        self.assertEqual(len(self.marcas("git worktree remove")), 0)
        self.assertTrue(wt.exists())
        self.assertIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 3"))

    def test_sem_limpar_sem_branch_local_nao_imprime_branch_d_e_poe_o_limpar_primeiro(self):
        # a branch local some entre o passo 1 e o passo 7: o falso do GitHub a apaga ao mesclar
        falso = self.tmp / "gh"
        falso.rename(self.tmp / "gh-base")
        falso.write_text(f'#!/usr/bin/env bash\n[ "$1 $2" = "pr merge" ] && git -C "{self.proj}" branch -q -D melhoria/x\nexec "{self.tmp / "gh-base"}" "$@"\n')
        falso.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        pendentes = r.stdout.split("pendente, rode:\n")[1].splitlines()
        self.assertEqual(pendentes[:2], ["forge-fechar p1 --ref melhoria/x --limpar", "git push origin --delete refs/heads/melhoria/x"])
        self.assertFalse(any("branch -D" in l for l in pendentes), pendentes)

    def test_sem_limpar_com_limpar_e_erro_de_uso_antes_de_qualquer_passo(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--sem-limpar")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("não combinam", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_sem_limpar_com_dry_run_so_descreve(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--sem-limpar: o passo 7 é pulado", r.stdout)
        self.assertEqual(self.chamadas(), [])


if __name__ == "__main__":
    unittest.main()
