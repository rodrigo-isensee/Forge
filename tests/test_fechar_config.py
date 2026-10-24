"""N-FECHAR-a, A2: aviso de lock do config na limpeza da branch de `bin/forge-fechar`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
SCRIPT = base.SCRIPT
GIT_CONFIG = r'''#!/usr/bin/env bash
# $ESTADO/config_ilegivel: a leitura do config falha como com o arquivo ilegível (código 128)
if [ "$1 $2" = "config --local" ] && [ -f "$ESTADO/config_ilegivel" ] && [[ "$*" == *--get-regexp* ]]; then
  echo "fatal: bad config file" >&2; exit 128
fi
exec "$(dirname "$0")/git-base" "$@"
'''


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    resumo = base.Fechar.resumo
    log_de = base.Fechar.log_de

    def setUp(self):
        base.Fechar.setUp(self)
        bin_ = self.tmp / "bin"
        (bin_ / "git").rename(bin_ / "git-base")
        (bin_ / "git").write_text(GIT_CONFIG, encoding="utf-8")
        (bin_ / "git").chmod(0o755)

    # ---- N-FECHAR-a, A2: aviso de lock do config na limpeza da branch ----
    def branch_com_config_travado(self, nome, secoes=()):
        """Cria e envia a branch `nome`, grava as variáveis em `secoes` e trava o config (config.lock como diretório: o git
        avisa "could not lock config file" e sai 0 no `branch -D`, como no sandbox, e o config continua legível)."""
        if nome != "melhoria/x":
            self.git("switch", "-q", "-c", nome)
            (self.proj / f"f-{len(nome)}").write_text("3\n")
            self.git("add", ".")
            self.git("commit", "-q", "-m", "feat: f")
            self.git("push", "-q", "origin", nome)
            self.git("switch", "-q", "develop")
        for chave in secoes:
            self.git("config", "--local", chave, "valor")
        (self.proj / ".git" / "config.lock").mkdir(exist_ok=True)

    def test_c3_aviso_de_lock_sem_secao_fica_ok_e_citado(self):
        self.branch_com_config_travado("melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok config=ok (aviso do git sem efeito)"])
        self.assertIn("could not lock config file", self.log_de(r).read_text())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")

    def test_c3_aviso_de_lock_com_secao_fica_pendente_com_o_comando(self):
        self.git("config", "--local", "branch.melhoria/x.remote", "origin")
        self.git("config", "--local", "branch.melhoria/x.merge", "refs/heads/melhoria/x")
        self.branch_com_config_travado("melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok config=pendente"])
        self.assertIn("git config --local --remove-section branch.melhoria/x", r.stdout.split("pendente, rode:\n")[1].splitlines())
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 3"))

    def test_c3_secao_de_outra_branch_com_ponto_no_nome_nao_e_a_desta(self):
        # ref `a`: só existe a seção de `a.b` (o prefixo `branch.a.` casaria branch.a.b.remote; o nome exato da seção não)
        self.git("config", "--local", "branch.a.b.remote", "origin")
        self.git("config", "--local", "branch.a.b.merge", "refs/heads/a.b")
        self.branch_com_config_travado("a")
        r = self.fechar("p1", "--ref", "a")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok config=ok (aviso do git sem efeito)"])

    def test_c3_secao_de_branch_com_ponto_no_nome_casa_pelo_nome_exato(self):
        # ref `a.b` com a seção dela: pendente (um regex com o `.` do nome também casaria branch.aXb; o texto fixo não)
        self.git("config", "--local", "branch.aXb.remote", "origin")
        self.git("config", "--local", "branch.a.b.remote", "origin")
        self.branch_com_config_travado("a.b")
        r = self.fechar("p1", "--ref", "a.b")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok config=pendente"])
        self.assertIn("git config --local --remove-section branch.a.b", r.stdout.split("pendente, rode:\n")[1].splitlines())

    def test_c3_secao_de_nome_parecido_nao_e_a_desta_branch(self):
        # só a seção de `aXc` (nome parecido, não igual) existe para a branch `a.c`
        self.git("config", "--local", "branch.aXc.remote", "origin")
        self.branch_com_config_travado("a.c")
        r = self.fechar("p1", "--ref", "a.c")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok config=ok (aviso do git sem efeito)"])

    def test_c3_config_ilegivel_depois_do_branch_d_nunca_vira_ok(self):
        self.branch_com_config_travado("melhoria/x")
        (self.estado / "config_ilegivel").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok config=pendente"])
        self.assertIn("git config --local --list", r.stdout.split("pendente, rode:\n")[1].splitlines())

    def test_c3_sem_aviso_e_sem_secao_a_linha_da_limpeza_nao_ganha_campo(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])


if __name__ == "__main__":
    unittest.main()
