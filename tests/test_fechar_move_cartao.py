"""FECHAR-MOVE-CARTAO: com o merge provado, o `forge-fechar --cartao ID` move o cartão para Pronto pelo `forge-check movimento`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` falso) sem herdar os testes dele. O `forge-check` falso
anota cada chamada; com $ESTADO/mov_falha, o `movimento` falha. O `movimento` do `forge-check` real fica em `test_fechar_forge_check_real`
(o módulo que o MAPA FORGE_CHECK do `forge-testes` lista).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

CHECK = '''#!/usr/bin/env bash
echo "forge-check $*" >> "$REGISTRO"
if [ "$1" = movimento ] && [ -f "$ESTADO/mov_falha" ]; then echo "movimento: coluna fora do KANBAN.md; nada gravado"; exit 1; fi
exit 0
'''
KANBAN = ("# Quadro\n\n## Em andamento (WIP 1 por agente)\n| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n"
          "|---|---|---|---|---|---|---|\n| K-1 | um cartão | p1 | forge:tech-lead | 2026-11-01 | 2026-11-01 | — |\n\n"
          "## Code review (WIP 2)\n| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n\n"
          "## Pronto\n| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n")
CABECALHO = "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"


class Teste(unittest.TestCase):
    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown

    def setUp(self):
        base.Fechar.setUp(self)
        (self.tmp / "check").write_text(CHECK, encoding="utf-8")
        self.quadro = self.tmp / ".forge-contrib"  # HOME é o tmp: o quadro padrão é o do Forge, ~/.forge-contrib
        (self.quadro / "docs" / "kanban").mkdir(parents=True)
        (self.quadro / "KANBAN.md").write_text(KANBAN, encoding="utf-8")
        self.historico = self.quadro / "docs" / "kanban" / "historico.md"

    def com_historico(self, *linhas):
        self.historico.write_text(CABECALHO + "".join(f"| {l} |\n" for l in linhas), encoding="utf-8")

    def movimentos(self):
        return [c for c in self.chamadas() if c.startswith("forge-check movimento")]

    def test_merge_move_o_cartao_da_coluna_do_historico_para_pronto_depois_do_merge(self):
        self.com_historico("2026-11-01T10:00:00-03:00 | K-1 | Em andamento | Code review | —",
                           "2026-11-01T11:00:00-03:00 | K-2 | Em andamento | Pronto | —",
                           "lixo | K-1 | Code review | Pronto | —")  # linha sem hora ISO não é movimento (como no montar_quadro)
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        esperado = f"forge-check movimento K-1 --de Code review --para Pronto --motivo mesclado em develop: PR #7, merge 0123456 --raiz {self.quadro}"
        self.assertEqual(self.movimentos(), [esperado])
        chamadas = self.chamadas()
        self.assertLess(chamadas.index(next(c for c in chamadas if c.startswith("gh pr merge"))), chamadas.index(esperado))
        self.assertIn("cartão K-1: Code review -> Pronto (mesclado em develop: PR #7, merge 0123456)", r.stdout)
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)

    def test_sem_linha_no_historico_a_coluna_vem_da_secao_do_quadro(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.movimentos()), 1)
        self.assertIn(" movimento K-1 --de Em andamento --para Pronto ", self.movimentos()[0])

    def test_cartao_que_nao_esta_no_quadro_nem_no_historico_sai_de_travessao(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-9")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(" movimento K-9 --de — --para Pronto ", self.movimentos()[0])

    def test_cartao_ja_em_pronto_nao_grava_de_novo(self):
        self.com_historico("2026-11-01T10:00:00-03:00 | K-1 | Code review | Pronto | —")
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.movimentos(), [])
        self.assertIn("cartão K-1: já em Pronto; nada gravado", r.stdout)

    def test_movimento_que_falha_fica_pendente_com_o_comando_e_sai_com_3(self):
        (self.estado / "mov_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-1")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("aviso: não movi o cartão K-1 para Pronto; rode: forge-check movimento K-1 --de Em\\ andamento --para Pronto", r.stderr)
        self.assertIn("limpeza: remota=ok worktree=ok branch=ok", r.stdout)  # a limpeza segue: o cartão não a prende
        self.assertIn("Entrega p1 fechada em develop; com pendência (código 3)", r.stdout)

    def test_sem_cartao_nao_move_nada_nem_pede_quadro(self):
        (self.quadro / "KANBAN.md").unlink()
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.movimentos(), [])

    def test_cartao_fora_da_forma_ou_quadro_sem_kanban_param_antes_do_passo_1(self):
        for args, texto in ((["--cartao", "K-1;rm"], "--cartao fora da forma"), (["--cartao", "-x"], "--cartao fora da forma"),
                            (["--cartao", "K-1", "--quadro", str(self.tmp / "nada")], "não há KANBAN.md")):
            with self.subTest(args=args):
                self.registro.write_text("")
                r = self.fechar("p1", "--ref", "melhoria/x", *args)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn(texto, r.stderr)
                self.assertEqual(self.chamadas(), [])

    def test_limpar_move_o_cartao_com_a_prova_do_merge(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"7 MERGED develop {sha}\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.movimentos()), 1)
        self.assertIn("--motivo mesclado em develop (forge-fechar --limpar)", self.movimentos()[0])

    def test_limpar_com_movimento_que_falha_sai_com_3(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"7 MERGED develop {sha}\n")
        (self.estado / "mov_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--cartao", "K-1")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("aviso: não movi o cartão K-1 para Pronto", r.stderr)
        self.assertNotIn("Limpeza de melhoria/x concluída.", r.stdout)

    def test_limpar_sem_prova_de_merge_nao_move_o_cartao(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--cartao", "K-1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertEqual(self.movimentos(), [])

    def test_dry_run_descreve_o_movimento_sem_gravar(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"cartão K-1: depois do merge, forge-check movimento K-1 --de Em andamento --para Pronto --raiz {self.quadro}", r.stdout)
        self.assertEqual(self.movimentos(), [])

    def test_armar_manda_o_limpar_com_o_cartao_e_o_quadro(self):
        (self.estado / "auto_arma").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x", "--armar", "--cartao", "K-1")
        self.assertEqual(r.returncode, 4, r.stderr + r.stdout)
        self.assertIn(f"forge-fechar p1 --ref melhoria/x --limpar --cartao K-1 --quadro {self.quadro}", r.stdout)
        self.assertEqual(self.movimentos(), [])


if __name__ == "__main__":
    unittest.main()
