"""N-FECHAR-a, A5: passo 2b de `bin/forge-fechar`, que para antes do PR quando a base andou com arquivo em comum.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import os
import shutil
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
SCRIPT = base.SCRIPT
# comm falso: $ESTADO/comm_falha faz o `comm` da interseção do passo 2b falhar; sem o arquivo, chama o comm de verdade
COMM_FALSO = r'''#!/usr/bin/env bash
[ ! -f "$ESTADO/comm_falha" ] || { echo "comm: falha simulada" >&2; exit 1; }
PATH="${PATH#*:}" exec comm "$@"
'''
# sort falso: $ESTADO/sort_falha_em guarda "a" ou "b"; só o sort cujo arquivo de entrada termina nessa letra (lista da base ou da branch) falha
SORT_FALSO = r'''#!/usr/bin/env bash
[ ! -f "$ESTADO/sort_falha_em" ] || case "${@: -1}" in */"$(cat "$ESTADO/sort_falha_em")") echo "sort: falha simulada" >&2; exit 2 ;; esac
PATH="${PATH#*:}" exec sort "$@"
'''
GIT_BASE_ANDOU = r'''#!/usr/bin/env bash
case "$1 $2" in
  "ls-remote origin")
    # $ESTADO/ls_develop_falha: sem resposta do servidor para a develop (só ela)
    if [ -f "$ESTADO/ls_develop_falha" ] && [ "$3" = refs/heads/develop ]; then echo "fatal: unable to access" >&2; exit 128; fi
    # $ESTADO/ls_ref_falha: sem resposta do servidor para a branch da entrega (passo 2); $ESTADO/ls_ref_lixo: a coluna 1 não é sha
    if [ -f "$ESTADO/ls_ref_falha" ] && [ "$3" = refs/heads/melhoria/x ]; then echo "fatal: unable to access" >&2; exit 128; fi
    if [ -f "$ESTADO/ls_ref_lixo" ] && [ "$3" = refs/heads/melhoria/x ]; then printf '%s\t%s\n' "$(cat "$ESTADO/ls_ref_lixo")" "$3"; exit 0; fi ;;
  "push origin")
    # $ESTADO/depois_do_envio: um script que roda depois do envio (a base anda de novo entre o merge e a cadeia seguinte)
    "$REAL_GIT_FALSO" "$@"; rc=$?
    if [ "$rc" = 0 ] && [ -f "$ESTADO/depois_do_envio" ]; then sh "$ESTADO/depois_do_envio" >&2; rm -f "$ESTADO/depois_do_envio"; fi
    exit "$rc" ;;
  "merge-tree --write-tree")
    # $ESTADO/merge_tree_falha: o git não sabe `merge-tree --write-tree` (anterior ao 2.38) ou falha ao calcular
    if [ -f "$ESTADO/merge_tree_falha" ]; then echo "usage: git merge-tree" >&2; exit 129; fi ;;
  "rev-list --count")
    # $ESTADO/revlist_falha: a contagem de commits da base (passo 2b) falha
    if [ -f "$ESTADO/revlist_falha" ]; then echo "fatal: bad object" >&2; exit 128; fi ;;
  "diff --no-renames")
    # $ESTADO/diff_falha: o diff da conta do passo 2b falha (objeto ausente)
    if [ -f "$ESTADO/diff_falha" ]; then echo "fatal: bad object" >&2; exit 128; fi
    # $ESTADO/diff_falha_em: só o diff cujo último argumento é o sha gravado ali falha (a base ou a branch, não os dois)
    if [ -f "$ESTADO/diff_falha_em" ] && [ "${@: -1}" = "$(cat "$ESTADO/diff_falha_em")" ]; then echo "fatal: bad object" >&2; exit 128; fi ;;
esac
exec "$(dirname "$0")/git-base" "$@"
'''


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    criacoes = base.Fechar.criacoes
    merges = base.Fechar.merges

    def setUp(self):
        base.Fechar.setUp(self)
        bin_ = self.tmp / "bin"
        (bin_ / "git").rename(bin_ / "git-base")
        (bin_ / "git").write_text(GIT_BASE_ANDOU, encoding="utf-8")
        (bin_ / "git").chmod(0o755)
        (bin_ / "comm").write_text(COMM_FALSO, encoding="utf-8")
        (bin_ / "comm").chmod(0o755)
        (bin_ / "sort").write_text(SORT_FALSO, encoding="utf-8")
        (bin_ / "sort").chmod(0o755)

    # ---- N-FECHAR-a, A5: base que andou com arquivo em comum (passo 2b) ----
    def base_anda(self, arquivos, renomear=None, ramo="develop"):
        """Um commit novo na develop (e no origin) que grava `arquivos` ({nome: texto}) ou renomeia `renomear` = (de, para)."""
        self.git("switch", "-q", ramo)
        if renomear:
            self.git("mv", *renomear)
        for nome, texto in arquivos.items():
            (self.proj / nome).write_text(texto)
            self.git("add", "--", nome)
        self.git("commit", "-q", "-m", "feat: base anda")
        self.git("push", "-q", "origin", ramo)

    def ramo_que_edita(self, nome, arquivo, texto):
        self.git("switch", "-q", "-c", nome, "develop")
        (self.proj / arquivo).write_text(texto)
        self.git("add", "--", arquivo)
        self.git("commit", "-q", "-m", "feat: edita")
        self.git("push", "-q", "origin", nome)
        self.git("switch", "-q", "develop")

    def test_c5_base_que_andou_com_arquivo_em_comum_para_antes_do_pr(self):
        self.base_anda({"b": "da base\n"})
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 2b", r.stderr)
        self.assertIn("git merge origin/develop", r.stderr)
        self.assertEqual([l for l in r.stderr.splitlines() if l.startswith("  ")], ["  b"])
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_c5_base_renomeou_o_arquivo_que_a_branch_editou_para(self):
        self.ramo_que_edita("melhoria/r", "a", "editado\n")
        self.base_anda({"g": "outro conteúdo\n"}, renomear=("a", "g"))  # renomeio com edição: conflito, a lista traz o `a`
        r = self.fechar("p1", "--ref", "melhoria/r")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("  a", r.stderr.splitlines())
        self.assertEqual(self.criacoes(), [])

    def test_c5_nome_com_quebra_de_linha_em_comum_lista_o_nome_inteiro(self):
        self.ramo_que_edita("melhoria/n", "n\nx", "da branch\n")
        self.base_anda({"n\nx": "da base\n"})
        r = self.fechar("p1", "--ref", "melhoria/n")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("  $'n\\nx'", r.stderr.splitlines())
        self.assertEqual(self.criacoes(), [])

    def test_c5_base_que_andou_sem_arquivo_em_comum_avisa_e_segue(self):
        self.base_anda({"outro": "x\n"})
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("a base andou 1 commit sem arquivo em comum", r.stdout)
        self.assertEqual(len(self.criacoes()), 1)

    def test_c5_base_local_atras_do_servidor_para_e_pede_fetch(self):
        # o servidor tem um commit a mais na develop que o origin/develop local não conhece
        self.git("clone", "-q", "-b", "develop", str(self.remoto), str(self.tmp / "outro"), cwd=self.tmp)
        outro = self.tmp / "outro"
        (outro / "z").write_text("z\n")
        self.git("add", "z", cwd=outro)
        self.git("commit", "-q", "-m", "feat: z", cwd=outro)
        self.git("push", "-q", "origin", "develop", cwd=outro)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("git fetch origin develop", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_c5_sem_resposta_do_servidor_na_develop_para(self):
        (self.estado / "ls_develop_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui ler a develop no servidor", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_c5_diff_que_falha_nunca_segue(self):
        self.base_anda({"outro": "x\n"})
        (self.estado / "diff_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("git fetch origin develop", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_c5_base_que_ja_esta_no_head_nao_avisa_nem_para(self):
        self.git("switch", "-q", "melhoria/x")
        self.git("merge", "-q", "origin/develop", "-m", "merge base")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("a base andou", r.stdout)

    def test_c5_head_ja_mesclado_nao_roda_o_2b(self):
        self.git("merge", "-q", "--no-ff", "melhoria/x", "-m", "merge x")
        self.git("push", "-q", "origin", "develop")
        self.git("fetch", "-q", "origin")
        (self.estado / "ls_develop_falha").write_text("1")  # se o 2b rodasse, pararia aqui
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_c5_dry_run_imprime_o_2b_e_nao_le_o_servidor(self):
        (self.estado / "ls_develop_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("[2b]", r.stdout)
        self.assertEqual(self.chamadas(), [])

    # ---- LOTE-FECHAR2: guardas do passo 2b e do passo 2 que a QA mostrou sem teste ----
    def criss_cross(self, arquivos=False):
        """develop e melhoria/c com dois pontos de partida (B e C), sem diferença de árvore: cada lado traz o commit do outro.
        Com `arquivos`, B grava `so_b` e C grava `so_c`: cada arquivo só aparece nos diffs de um dos dois pontos de partida."""
        self.git("switch", "-q", "-c", "melhoria/c", "develop")
        if arquivos:
            (self.proj / "so_b").write_text("b\n")
            self.git("add", "--", "so_b")
        self.git("commit", "-q", "--allow-empty", "-m", "chore: B")
        b = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "develop")
        if arquivos:
            (self.proj / "so_c").write_text("c\n")
            self.git("add", "--", "so_c")
        self.git("commit", "-q", "--allow-empty", "-m", "chore: C")
        c = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "melhoria/c")
        self.git("merge", "-q", "--no-ff", "-m", "traz C", c)
        self.git("switch", "-q", "develop")
        self.git("merge", "-q", "--no-ff", "-m", "traz B", b)
        self.git("push", "-q", "origin", "develop", "melhoria/c")
        self.assertEqual(sorted(self.git("merge-base", "--all", "develop", "melhoria/c").split()), sorted([b, c]))

    def test_varios_pontos_de_partida_entram_todos_na_contagem_da_base(self):
        self.criss_cross()
        r = self.fechar("p1", "--ref", "melhoria/c")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        # só o merge da base é da base; com um só ponto de partida na conta, o commit C também entraria (2 commits)
        self.assertIn("a base andou 1 commit sem arquivo em comum", r.stdout)

    def test_arquivo_em_comum_so_no_diff_do_segundo_ponto_de_partida_para_e_lista_os_dois(self):
        self.criss_cross(arquivos=True)
        r = self.fechar("p1", "--ref", "melhoria/c", "--trazida")  # com --trazida o merge não se repete: só a listagem que para
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        # so_b só entra no diff de B e so_c só no de C: o laço sobre um só ponto de partida listaria um deles
        self.assertEqual([l for l in r.stderr.splitlines() if l.startswith("  ")], ["  so_b", "  so_c"])
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_comm_que_falha_para_no_passo_2b_sem_abrir_pr(self):
        self.base_anda({"outro": "x\n"})
        (self.estado / "comm_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui cruzar as listas de arquivos", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_ls_remote_da_branch_que_falha_para_no_passo_2_com_a_mensagem_da_leitura(self):
        (self.estado / "ls_ref_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 2: não consegui ler a branch melhoria/x no origin", r.stderr)
        self.assertNotIn("não está no origin", r.stderr)
        self.assertEqual(self.criacoes(), [])

    def test_coluna_1_que_nao_e_sha_e_leitura_que_falhou_e_nao_valor(self):
        for lixo in ("nao-e-sha", "abc123", "z" * 40):  # fora do hexadecimal, hexadecimal curto, 40 caracteres que não são hexadecimais
            with self.subTest(lixo=lixo):
                (self.estado / "ls_ref_lixo").write_text(lixo)
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("parou no passo 2: não consegui ler a branch melhoria/x no origin", r.stderr)
                self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def _diff_que_falha_so_em(self, rev, mensagem):
        self.base_anda({"outro": "x\n"})
        (self.estado / "diff_falha_em").write_text(self.git("rev-parse", rev))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(mensagem, r.stderr)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_diff_da_base_que_falha_sozinho_para_no_passo_2b(self):
        self._diff_que_falha_so_em("origin/develop", "parou no passo 2b: o diff da base falhou")

    def test_diff_da_branch_que_falha_sozinho_para_no_passo_2b(self):
        self._diff_que_falha_so_em("origin/melhoria/x", "parou no passo 2b: o diff da branch falhou")

    def _sort_que_falha_so_em(self, lado):
        self.base_anda({"b": "da base\n"})  # arquivo em comum: a falha do sort não pode virar "sem arquivo em comum"
        (self.estado / "sort_falha_em").write_text(lado)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui cruzar as listas de arquivos", r.stderr)
        self.assertNotIn("sem arquivo em comum", r.stderr + r.stdout)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_sort_da_lista_da_base_que_falha_para_no_passo_2b(self):
        self._sort_que_falha_so_em("a")

    def test_sort_da_lista_da_branch_que_falha_para_no_passo_2b(self):
        self._sort_que_falha_so_em("b")

    def test_contagem_de_commits_da_base_que_falha_para_no_passo_2b(self):
        self.base_anda({"outro": "x\n"})
        (self.estado / "revlist_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui contar os commits da base", r.stderr)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    # ---- L37 (D-3): a base andou e tocou arquivo da branch; com `git merge-tree` limpo o integrador faz o merge ----
    def renomeio_limpo(self, nome="melhoria/r"):
        """A branch edita `a` e a base só o renomeia para `g`: arquivo em comum, mas o merge-tree sai limpo."""
        self.base_anda({"a": "l1\nl2\nl3\nl4\nl5\n"})
        self.ramo_que_edita(nome, "a", "editado\nl2\nl3\nl4\nl5\n")
        self.base_anda({}, renomear=("a", "g"))

    def head_remoto(self, nome):
        return self.git("ls-remote", "origin", f"refs/heads/{nome}").split()[0]

    def test_l37_base_com_arquivo_em_comum_sem_conflito_faz_o_merge_e_recomeca_a_cadeia(self):
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        base_sha = self.head_remoto("develop")
        arvore = self.git("merge-tree", "--write-tree", "--no-messages", antigo, base_sha)
        r = self.fechar("p1", "--ref", "melhoria/r", "--sem-limpar")  # a branch fica para o teste conferir o head
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        novo = self.git("rev-parse", "melhoria/r")
        self.assertNotEqual(novo, antigo)
        self.assertEqual(self.git("rev-list", "--parents", "-n", "1", novo).split(), [novo, antigo, base_sha])  # pais: head e base
        self.assertEqual(self.git("rev-parse", f"{novo}^{{tree}}"), arvore)  # a árvore é a do merge-tree, nada à mão
        # a cadeia recomeçou no head novo: o forge-check leu o antigo e depois o novo; o PR e o merge ficaram presos ao novo
        pr = [c for c in self.chamadas() if c.startswith("forge-check pr")]
        self.assertEqual([c.split()[4] for c in pr], [antigo, novo])
        self.assertEqual(len(self.criacoes()), 1)
        self.assertEqual(len(self.merges()), 1)
        self.assertIn(novo, self.merges()[0])
        self.assertNotIn(antigo, self.merges()[0])
        self.assertIn("merge limpo em melhoria/r", r.stdout)

    def test_l37_o_merge_sobe_pelo_envio_normal_e_a_worktree_da_branch_anda_junto(self):
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        arvore = self.tmp / "wt-r"
        self.git("worktree", "add", "-q", str(arvore), "melhoria/r")
        r = self.fechar("p1", "--ref", "melhoria/r", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)  # fechado, limpeza pendente
        novo = self.git("rev-parse", "melhoria/r")
        self.assertNotEqual(novo, antigo)
        self.assertEqual(self.git("-C", str(arvore), "rev-parse", "HEAD"), novo)  # a worktree acompanhou (fast-forward)
        self.assertEqual(self.git("-C", str(arvore), "status", "--porcelain"), "")
        self.assertEqual(self.head_remoto("melhoria/r"), novo)

    def test_l37_worktree_com_mudanca_nao_commitada_para_sem_mexer_na_branch(self):
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        arvore = self.tmp / "wt-r"
        self.git("worktree", "add", "-q", str(arvore), "melhoria/r")
        (arvore / "rascunho").write_text("x\n")
        self.git("add", "rascunho", cwd=arvore)
        r = self.fechar("p1", "--ref", "melhoria/r")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("tem mudança não commitada", r.stderr)
        self.assertEqual((self.git("rev-parse", "melhoria/r"), self.head_remoto("melhoria/r")), (antigo, antigo))
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_l37_com_conflito_para_sem_merge_sem_envio_e_sem_pr(self):
        self.base_anda({"b": "da base\n"})  # a branch também criou `b`, com outro conteúdo: conflito
        antigo = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("tem conflito", r.stderr)
        self.assertIn("git merge origin/develop", r.stderr)
        self.assertEqual((self.git("rev-parse", "melhoria/x"), self.head_remoto("melhoria/x")), (antigo, antigo))
        self.assertEqual(self.git("rev-list", "--merges", "-n", "1", "melhoria/x"), "")
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_l37_branch_fora_de_melhoria_nunca_recebe_o_merge(self):  # C-37c
        self.renomeio_limpo("feature/z")
        antigo = self.git("rev-parse", "feature/z")
        r = self.fechar("p1", "--ref", "feature/z")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 2b", r.stderr)
        self.assertEqual((self.git("rev-parse", "feature/z"), self.head_remoto("feature/z")), (antigo, antigo))
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_l37_so_um_merge_por_cadeia_a_base_que_anda_de_novo_para(self):  # T-37b
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        r = self.fechar("p1", "--ref", "melhoria/r", "--trazida")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertEqual(self.git("rev-parse", "melhoria/r"), antigo)
        self.assertEqual(self.criacoes(), [])

    def test_l37_a_base_que_anda_de_novo_depois_do_merge_para_na_cadeia_seguinte(self):  # T-37b: o recomeço leva --trazida
        self.renomeio_limpo()
        (self.estado / "depois_do_envio").write_text(
            f'set -e\nG="$REAL_GIT_FALSO"\nd="$(mktemp -d)"\n"$G" clone -q -b develop {self.remoto} "$d/c"\ncd "$d/c"\n'
            'printf "l1\\nl2\\nl3\\nl4\\nmais\\n" > g\n"$G" add g\n"$G" commit -q -m "feat: base anda de novo"\n"$G" push -q origin develop\n', encoding="utf-8")
        r = self.fechar("p1", "--ref", "melhoria/r")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 2b", r.stderr)
        self.assertEqual(r.stdout.count("merge limpo em melhoria/r"), 1, "um merge por cadeia")
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_l37_git_sem_merge_tree_ou_com_falha_para_sem_mexer_na_branch(self):  # falha fechada
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        (self.estado / "merge_tree_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/r")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui calcular o merge", r.stderr)
        self.assertEqual((self.git("rev-parse", "melhoria/r"), self.head_remoto("melhoria/r")), (antigo, antigo))
        self.assertEqual(self.criacoes(), [])

    def test_l37_envio_recusado_para_sem_abrir_pr_e_diz_onde_o_merge_ficou(self):
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        gancho = self.remoto / "hooks" / "pre-receive"
        gancho.write_text("#!/bin/sh\necho recusado de proposito >&2\nexit 1\n", encoding="utf-8")
        gancho.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/r")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("o envio do merge foi recusado", r.stderr)
        self.assertEqual(self.head_remoto("melhoria/r"), antigo)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_l37_nunca_usa_no_verify_nem_force_no_envio(self):  # T-37c
        texto = SCRIPT.read_text(encoding="utf-8")
        corpo = texto[texto.index("trazer_a_base() {"):texto.index("# conferir_base (passo 2b")]
        self.assertIn('git push origin "$ramo:$ramo"', corpo)
        for proibido in ("--no-verify", "--force", " -f ", "-X ", "--allow-unrelated-histories", "+refs"):
            self.assertNotIn(proibido, corpo)

    # ---- LOTE-0307-A, E1: index.lock na pasta git da worktree da branch ----
    def worktree_de_x(self):
        arvore = self.tmp / "wt-x"
        self.git("worktree", "add", "-q", str(arvore), "melhoria/x")
        return Path(self.git("-C", str(arvore), "rev-parse", "--absolute-git-dir"))

    def test_lock_presente_na_worktree_da_branch_para_com_codigo_1_e_nao_apaga(self):
        pasta_git = self.worktree_de_x()
        lock = pasta_git / "index.lock"
        lock.write_text("")
        antes = time.time() - 7 * 60
        os.utime(lock, (antes, antes))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(str(lock), r.stderr)
        self.assertIn("idade: 7 min", r.stderr)
        self.assertIn(f"rm {lock}", r.stderr)
        self.assertTrue(lock.exists())
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_lock_ausente_na_worktree_da_branch_segue(self):
        self.worktree_de_x()
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.criacoes()), 1)

    def test_lock_na_worktree_principal_com_o_fechamento_rodando_em_outra_arvore_para(self):
        # git-dir relativo (".git") só se completa com a pasta da worktree da branch; o cwd do script é outra árvore
        self.git("switch", "-q", "melhoria/x")
        outra = self.tmp / "wt-develop"
        self.git("worktree", "add", "-q", str(outra), "develop")
        lock = self.proj / ".git" / "index.lock"
        lock.write_text("")
        r = base.subprocess.run(["bash", str(base.SCRIPT), "p1", "--ref", "melhoria/x"], cwd=outra, env=self.env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(str(lock), r.stderr)
        self.assertTrue(lock.exists())

    def test_worktree_da_branch_com_a_pasta_apagada_nao_para_no_lock(self):
        arvore = self.tmp / "wt-x"
        self.git("worktree", "add", "-q", str(arvore), "melhoria/x")
        shutil.rmtree(arvore)  # registro órfão: o passo 7 trata com prune
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotIn("pasta git", r.stderr)
        self.assertNotIn("lock do git", r.stderr)


if __name__ == "__main__":
    unittest.main()
