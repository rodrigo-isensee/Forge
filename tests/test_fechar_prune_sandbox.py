"""WORKTREE-PRUNE-SANDBOX: o passo 7 do `bin/forge-fechar` poda os registros órfãos também depois de uma remoção que deu certo, e os
metadados que o sandbox prende viram registro, sem pendência para o dono.

Reaproveita o ambiente de `test_fechar_orfao.Teste` (repositório temporário, `gh`, `forge-check` e `git` falsos) sem herdar os testes dele.
"""
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar_orfao as orfao  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

# $ESTADO/meta_presa guarda o caminho dos metadados da worktree: depois do `worktree remove` e do `worktree prune` reais, a pasta volta
# a existir, como a que o sandbox prende (config.worktree e commondir montados) e que nem o remove nem o prune da mesma sessão tiram.
GIT_META_PRESA = r'''#!/usr/bin/env bash
"$(dirname "$0")/git-orfao" "$@"; rc=$?
if [ -f "$ESTADO/meta_presa" ] && { [ "$1 $2" = "worktree remove" ] || [ "$1 $2" = "worktree prune" ]; }; then
  mkdir -p "$(cat "$ESTADO/meta_presa")" && : > "$(cat "$ESTADO/meta_presa")/config.worktree"
fi
exit "$rc"
'''


class Teste(unittest.TestCase):
    tearDown = orfao.Teste.tearDown
    git = orfao.Teste.git
    fechar = orfao.Teste.fechar
    chamadas = orfao.Teste.chamadas
    com_worktree = orfao.Teste.com_worktree
    resumo = orfao.Teste.resumo
    marcas = orfao.Teste.marcas
    log_de = orfao.Teste.log_de
    arvores = orfao.Teste.arvores

    def setUp(self):
        orfao.Teste.setUp(self)
        bin_ = self.tmp / "bin"
        (bin_ / "git").rename(bin_ / "git-orfao")
        (bin_ / "git").write_text(GIT_META_PRESA, encoding="utf-8")
        (bin_ / "git").chmod(0o755)

    def test_remocao_que_da_certo_poda_o_registro_orfao_de_outra_sessao(self):
        wt = self.com_worktree()
        outra = self.tmp / "wt-outra"
        self.git("worktree", "add", "-q", "-b", "melhoria/outra", str(outra))
        shutil.rmtree(outra)  # o registro que outra sessão deixou para trás
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertEqual(len(self.marcas("git worktree prune -v")), 1)
        self.assertLess(self.marcas("git worktree remove")[0], self.marcas("git worktree prune -v")[0])
        self.assertIn("registro: prune tirou 1 registro(s) de worktree órfã", r.stdout)
        self.assertIn("[prune] Removing worktrees/wt-outra", self.log_de(r).read_text())
        self.assertFalse((self.proj / ".git" / "worktrees" / "wt-outra").exists())
        self.assertFalse(wt.exists())
        self.assertNotIn("metadados da worktree ficaram", r.stdout)
        self.assertEqual(len(self.arvores()), 1)

    def test_metadados_presos_pelo_sandbox_viram_registro_sem_pendencia(self):
        self.com_worktree()
        meta = (self.proj / ".git" / "worktrees" / "wt-x").resolve()
        (self.estado / "meta_presa").write_text(str(meta))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertIn(f"registro: os metadados da worktree ficaram em {meta} (o sandbox os prende nesta sessão)", r.stdout)
        self.assertNotIn("pendente, rode:", r.stdout)
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")

    def test_worktree_suja_que_fica_nao_fala_de_metadados_presos(self):
        wt = self.com_worktree()
        (self.estado / "wt_busy").write_text("persiste")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(wt.exists())
        self.assertNotIn("metadados da worktree ficaram", r.stdout)
        self.assertEqual(self.marcas("git worktree prune"), [])


if __name__ == "__main__":
    unittest.main()
