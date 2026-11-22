"""N-FECHAR-a, A5, E8 (0.45.6) e H4 (0.47.5): passos 2b e 6a de `bin/forge-fechar`: a base que andou só para com conflito real; sem ele,
em melhoria/* o 2b a traz por merge e recomeça a cadeia (H4), e fora dela ou no 6a segue sem trazer (E8).

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
GIT_BASE_ANDOU = r'''#!/usr/bin/env bash
# H4: $ESTADO/falha_<commit-tree|update-ref|ff>: o passo falha; $ESTADO/falha_apos_envio: depois do envio, o ls-remote da branch falha
for f in commit-tree update-ref; do if [ "$1" = "$f" ] && [ -f "$ESTADO/falha_$f" ]; then exit 1; fi; done
# FECHAR-6A-DEVELOP-ANDOU: $ESTADO/falha_fetch_develop: a busca da develop (refspec exato do passo 6a) falha
if [ "$1 $2 $3 $4" = "fetch -q origin +refs/heads/develop:refs/remotes/origin/develop" ] && [ -f "$ESTADO/falha_fetch_develop" ]; then exit 1; fi
# $ESTADO/antes_do_fetch: roda (uma vez) antes da busca da develop do passo 6a; a develop do servidor anda de novo depois do ls-remote
if [ "$1 $2 $3 $4" = "fetch -q origin +refs/heads/develop:refs/remotes/origin/develop" ] && [ -f "$ESTADO/antes_do_fetch" ]; then
  mv "$ESTADO/antes_do_fetch" "$ESTADO/antes_do_fetch.rodou"; sh "$ESTADO/antes_do_fetch.rodou" >&2
fi
case "$*" in *"merge --ff-only"*) if [ -f "$ESTADO/falha_ff" ]; then exit 1; fi ;; esac
if [ "$1 $2" = "push origin" ] && [ -f "$ESTADO/falha_apos_envio" ]; then touch "$ESTADO/ls_ref_falha"; fi
case "$1 $2" in
  "ls-remote origin")
    # $ESTADO/ls_develop_falha: sem resposta do servidor para a develop (só ela)
    if [ -f "$ESTADO/ls_develop_falha" ] && [ "$3" = refs/heads/develop ]; then echo "fatal: unable to access" >&2; exit 128; fi
    # $ESTADO/ls_ref_falha: sem resposta do servidor para a branch da entrega (passo 2); $ESTADO/ls_ref_lixo: a coluna 1 não é sha
    if [ -f "$ESTADO/ls_ref_falha" ] && [ "$3" = refs/heads/melhoria/x ]; then echo "fatal: unable to access" >&2; exit 128; fi
    if [ -f "$ESTADO/ls_ref_lixo" ] && [ "$3" = refs/heads/melhoria/x ]; then printf '%s\t%s\n' "$(cat "$ESTADO/ls_ref_lixo")" "$3"; exit 0; fi ;;
  "merge-tree --write-tree")
    # $ESTADO/merge_tree_falha: o git não sabe `merge-tree --write-tree` (anterior ao 2.38) ou falha ao calcular
    if [ -f "$ESTADO/merge_tree_falha" ]; then echo "usage: git merge-tree" >&2; exit 129; fi
    if [ -f "$ESTADO/merge_tree_lixo" ]; then echo "lixo"; exit 0; fi ;;
  "rev-list --count")
    # $ESTADO/revlist_falha: a contagem de commits da base (passo 2b) falha
    if [ -f "$ESTADO/revlist_falha" ]; then echo "fatal: bad object" >&2; exit 128; fi ;;
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

    def test_c5_base_que_andou_com_conflito_para_antes_do_pr(self):
        self.base_anda({"b": "da base\n"})  # a branch também criou `b`, com outro conteúdo
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 2b: o merge de origin/develop em melhoria/x tem conflito", r.stderr)
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

    def test_c5_nome_com_quebra_de_linha_em_conflito_lista_o_nome_inteiro(self):
        self.ramo_que_edita("melhoria/n", "n\nx", "da branch\n")
        self.base_anda({"n\nx": "da base\n"})
        r = self.fechar("p1", "--ref", "melhoria/n")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn('  "n\\nx"', r.stderr.splitlines())
        self.assertEqual(self.criacoes(), [])

    def test_c5_base_que_andou_sem_conflito_traz_a_base_e_segue(self):
        self.base_anda({"outro.md": "x\n"})
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("a base andou 1 commit sem conflito com melhoria/x; trago a base por merge (H4)", r.stdout)
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
        self.assertIn("sem conflito, em melhoria/* faz o merge da base (árvore do merge-tree), git push origin melhoria/x", r.stdout)
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
        self.assertIn("a base andou 1 commit sem conflito", r.stdout)

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

    def test_contagem_de_commits_da_base_que_falha_para_no_passo_2b(self):
        self.base_anda({"outro": "x\n"})
        (self.estado / "revlist_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui contar os commits da base", r.stderr)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    # ---- E8 (0.45.6): a base que andou sem conflito real nunca é trazida no fechamento (passo 2b) ----
    def renomeio_limpo(self, nome="melhoria/r"):
        """A branch edita `a` e a base só o renomeia para `g`: arquivo em comum, mas o merge-tree sai limpo."""
        self.base_anda({"a": "l1\nl2\nl3\nl4\nl5\n"})
        self.ramo_que_edita(nome, "a", "editado\nl2\nl3\nl4\nl5\n")
        self.base_anda({}, renomear=("a", "g"))

    def head_remoto(self, nome):
        return self.git("ls-remote", "origin", f"refs/heads/{nome}").split()[0]

    def assert_segue_sem_trazer(self, ref, antigo, r):
        """Fechado com o head de antes: nenhum commit de merge da base, nada enviado, cadeia única e merge preso ao head antigo."""
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn(f"sem conflito com {ref}; não trago a base (E8)", r.stdout)
        self.assertEqual((self.git("rev-parse", ref), self.head_remoto(ref)), (antigo, antigo))
        self.assertEqual([c.split()[4] for c in self.chamadas() if c.startswith("forge-check pr")], [f"refs/heads/{ref}"])
        self.assertEqual(len(self.criacoes()), 1)
        self.assertEqual(len(self.merges()), 1)
        self.assertIn(antigo, self.merges()[0])

    def _arquivo_em_comum_sem_conflito(self, ref):
        self.renomeio_limpo(ref)
        antigo = self.git("rev-parse", ref)
        self.assert_segue_sem_trazer(ref, antigo, self.fechar("p1", "--ref", ref, "--sem-limpar"))

    def assert_trouxe(self, ref, antigo, r):
        """H4: o head novo é o merge da base (pais: o antigo e a base; árvore do merge-tree), enviado; a cadeia recomeçou nele."""
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        novo, base_sha = self.head_remoto(ref), self.head_remoto("develop")
        self.assertEqual(self.git("rev-list", "--parents", "-n", "1", novo).split(), [novo, antigo, base_sha])
        self.assertEqual(self.git("rev-parse", f"{novo}^{{tree}}"), self.git("merge-tree", "--write-tree", antigo, base_sha))
        self.assertEqual(len([c for c in self.chamadas() if c.startswith("forge-check pr")]), 2)  # a cadeia recomeçou
        self.assertEqual((len(self.criacoes()), len(self.merges())), (1, 1))
        self.assertIn(novo, self.merges()[0])
        self.assertEqual(r.stdout.count("trago a base por merge (H4)"), 1, "um merge por cadeia")
        return novo

    def test_h4_arquivo_em_comum_sem_conflito_traz_a_base_e_recomeca(self):
        self.renomeio_limpo()
        antigo = self.git("rev-parse", "melhoria/r")
        novo = self.assert_trouxe("melhoria/r", antigo, self.fechar("p1", "--ref", "melhoria/r", "--sem-limpar"))
        self.assertEqual(self.git("rev-parse", "melhoria/r"), novo)

    def test_h4_worktree_da_branch_anda_junto(self):
        self.renomeio_limpo()
        antigo, arvore = self.git("rev-parse", "melhoria/r"), self.tmp / "wt-r"
        self.git("worktree", "add", "-q", str(arvore), "melhoria/r")
        novo = self.assert_trouxe("melhoria/r", antigo, self.fechar("p1", "--ref", "melhoria/r", "--sem-limpar"))
        self.assertEqual(self.git("-C", str(arvore), "rev-parse", "HEAD"), novo)

    def test_h4_sem_a_branch_local_envia_o_merge_e_recomeca(self):
        self.base_anda({"outro.md": "x\n"})
        antigo = self.git("rev-parse", "melhoria/x")
        self.git("branch", "-D", "melhoria/x")
        self.assert_trouxe("melhoria/x", antigo, self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar"))

    def assert_parou_sem_trazer(self, r, texto, ref="melhoria/x", antigo=None):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(texto, r.stderr)
        if antigo:
            self.assertEqual((self.git("rev-parse", ref), self.head_remoto(ref)), (antigo, antigo))
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_h4_falha_de_cada_passo_do_merge_para_sem_pr(self):
        for marca, texto in (("merge_tree_lixo", "não devolveu uma árvore"), ("falha_commit-tree", "não consegui criar o commit de merge"),
                             ("falha_update-ref", "não consegui avançar melhoria/x")):
            with self.subTest(marca=marca):
                self.setUp()
                self.base_anda({"outro.md": "x\n"})
                antigo = self.git("rev-parse", "melhoria/x")
                (self.estado / marca).write_text("1")
                self.assert_parou_sem_trazer(self.fechar("p1", "--ref", "melhoria/x"), texto, antigo=antigo)

    def test_h4_worktree_suja_ou_ff_que_falha_para_sem_enviar(self):
        for marca, texto in (("", "tem mudança não commitada"), ("falha_ff", "não consegui avançar melhoria/r")):
            with self.subTest(marca=marca):
                self.setUp()
                self.renomeio_limpo()
                antigo, arvore = self.git("rev-parse", "melhoria/r"), self.tmp / "wt-r"
                self.git("worktree", "add", "-q", str(arvore), "melhoria/r")
                if marca:
                    (self.estado / marca).write_text("1")
                else:
                    (arvore / "rascunho").write_text("x\n")
                    self.git("add", "rascunho", cwd=arvore)
                self.assert_parou_sem_trazer(self.fechar("p1", "--ref", "melhoria/r"), texto, "melhoria/r", antigo)

    def test_h4_envio_recusado_para_sem_pr(self):
        self.base_anda({"outro.md": "x\n"})
        antigo = self.git("rev-parse", "melhoria/x")
        gancho = self.remoto / "hooks" / "pre-receive"
        gancho.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        gancho.chmod(0o755)
        self.assert_parou_sem_trazer(self.fechar("p1", "--ref", "melhoria/x"), "o envio do merge foi recusado")
        self.assertEqual(self.head_remoto("melhoria/x"), antigo)

    def test_h4_cadeia_recomecada_que_para_sai_com_o_codigo_dela(self):
        self.base_anda({"outro.md": "x\n"})
        (self.estado / "falha_apos_envio").write_text("1")
        self.assert_parou_sem_trazer(self.fechar("p1", "--ref", "melhoria/x"), "parou no passo 2: não consegui ler a branch melhoria/x")

    def test_h4_com_trazida_nao_traz_a_base_de_novo(self):
        self.base_anda({"outro.md": "x\n"})
        antigo = self.git("rev-parse", "melhoria/x")
        self.assert_segue_sem_trazer("melhoria/x", antigo, self.fechar("p1", "--ref", "melhoria/x", "--trazida", "--sem-limpar"))

    def test_e8_fora_de_melhoria_e_o_mesmo_nenhuma_branch_recebe_o_merge(self):
        self._arquivo_em_comum_sem_conflito("feature/z")

    def test_h4_base_que_mudou_codigo_traz_a_base(self):
        antigo = self.git("rev-parse", "melhoria/x")
        (self.proj / "bin").mkdir(exist_ok=True)
        self.base_anda({"bin/x": "da base\n"})
        self.assert_trouxe("melhoria/x", antigo, self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar"))
        self.assertEqual([c.split()[4] for c in self.chamadas() if c.startswith("forge-check pr")], ["refs/heads/melhoria/x"] * 2)

    def test_e8_com_conflito_para_sem_merge_sem_envio_e_sem_pr(self):
        self.base_anda({"b": "da base\n"})  # a branch também criou `b`, com outro conteúdo: conflito
        antigo = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("tem conflito", r.stderr)
        self.assertIn("git merge origin/develop", r.stderr)
        self.assertEqual((self.git("rev-parse", "melhoria/x"), self.head_remoto("melhoria/x")), (antigo, antigo))
        self.assertEqual(self.git("rev-list", "--merges", "-n", "1", "melhoria/x"), "")
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_e8_conflito_de_pasta_e_arquivo_sem_arquivo_em_comum_para(self):
        (self.proj / "d").mkdir()
        self.ramo_que_edita("melhoria/d", "d/x", "da branch\n")  # a base cria o arquivo `d`: conflito de pasta e arquivo
        antigo = self.git("rev-parse", "melhoria/d")
        self.base_anda({"d": "da base\n"})
        r = self.fechar("p1", "--ref", "melhoria/d")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("tem conflito", r.stderr)
        self.assertEqual((self.git("rev-parse", "melhoria/d"), self.head_remoto("melhoria/d")), (antigo, antigo))
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_e8_git_sem_merge_tree_ou_com_falha_para_no_2b(self):  # falha fechada: nunca vira "sem conflito"
        self.renomeio_limpo()
        (self.estado / "merge_tree_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/r")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 2b: não consegui calcular o merge", r.stderr)
        self.assertNotIn("sem conflito", r.stdout)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    # ---- CONFLITO-SEMANTICO-ANTES-DO-PR (0.43.2): a base anda durante os checks (passo 6a, antes do merge) ----
    def base_anda_nos_checks(self, arquivo, local=True):
        """Um commit na develop do servidor durante o `gh pr checks`; com `local`, a origin/develop desta cópia o acompanha
        (como depois de um `git fetch`); sem `local`, só o servidor anda (outra cópia envia)."""
        embrulho = self.tmp / "gh-nos-checks"
        embrulho.write_text('#!/usr/bin/env bash\nif [ "$1 $2" = "pr checks" ] && [ -f "$ESTADO/durante_checks" ]; then\n'
                            '  sh "$ESTADO/durante_checks" >&2; rm -f "$ESTADO/durante_checks"\nfi\nexec "$GH_REAL" "$@"\n', encoding="utf-8")
        embrulho.chmod(0o755)
        self.env.update(FORGE_GH=str(embrulho), GH_REAL=str(self.tmp / "gh"))
        copia = self.proj
        if not local:
            copia = self.tmp / "outra"
            self.git("clone", "-q", "-b", "develop", str(self.remoto), str(copia), cwd=self.tmp)
        pasta = os.path.dirname(arquivo) or "."
        (self.estado / "durante_checks").write_text(
            f'cd "{copia}" && git switch -q develop && mkdir -p "{pasta}" && echo novo > "{arquivo}" && git add -- "{arquivo}"'
            f' && git commit -q -m "feat: outro PR" && git push -q origin develop\n', encoding="utf-8")

    def test_6a_base_que_mudou_codigo_nos_checks_segue_sem_trazer_a_base(self):
        antigo = self.git("rev-parse", "melhoria/x")
        self.base_anda_nos_checks("bin/y")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("a develop andou durante os checks sem conflito com melhoria/x; não trago a base (E8)", r.stdout)
        self.assertEqual((self.git("rev-parse", "melhoria/x"), self.head_remoto("melhoria/x")), (antigo, antigo))
        self.assertEqual(len(self.merges()), 1)
        self.assertIn(antigo, self.merges()[0])

    def assert_parou_no_6a(self, r, texto):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6a", r.stderr)
        self.assertIn(texto, r.stderr)
        self.assertEqual(self.merges(), [])

    def test_6a_base_local_velha_busca_a_base_e_segue_sem_conflito(self):  # FECHAR-6A-DEVELOP-ANDOU
        antigo = self.git("rev-parse", "melhoria/x")
        self.base_anda_nos_checks("docs/nota.txt", local=False)
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("busco a develop (git fetch, só leitura) e confiro o merge com ela", r.stdout)
        self.assertIn("a develop andou durante os checks sem conflito com melhoria/x; não trago a base (E8)", r.stdout)
        self.assertEqual(self.git("rev-parse", "origin/develop"), self.head_remoto("develop"))
        self.assertEqual((self.git("rev-parse", "melhoria/x"), self.head_remoto("melhoria/x")), (antigo, antigo))
        self.assertEqual(len(self.merges()), 1)
        self.assertIn(antigo, self.merges()[0])

    def test_6a_base_local_velha_com_conflito_na_base_buscada_para(self):
        self.base_anda_nos_checks("b", local=False)  # a branch criou `b` com outro conteúdo
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assert_parou_no_6a(r, "o merge dela em melhoria/x tem conflito")
        self.assertIn("  b", r.stderr.splitlines())

    def test_6a_busca_que_traz_outra_base_alem_da_lida_para(self):
        # E75.6 (A2 da segurança): a base buscada tem de ser a lida no servidor (ls-remote); a que andou de novo não foi conferida
        antigo = self.git("rev-parse", "melhoria/x")
        self.base_anda_nos_checks("docs/nota.txt", local=False)
        outra = self.tmp / "outra"
        (self.estado / "antes_do_fetch").write_text(
            f'cd "{outra}" && echo mais > docs/mais.txt && git add -- docs/mais.txt && git commit -q -m "feat: mais um PR"'
            ' && git push -q origin develop\n', encoding="utf-8")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assert_parou_no_6a(r, "e origin/develop não a tem")
        self.assertTrue((self.estado / "antes_do_fetch.rodou").exists())
        self.assertEqual(self.git("rev-parse", "origin/develop"), self.head_remoto("develop"))
        self.assertEqual(self.head_remoto("melhoria/x"), antigo)

    def test_6a_busca_da_base_que_falha_para_e_pede_o_fetch(self):
        self.base_anda_nos_checks("docs/nota.txt", local=False)
        (self.estado / "falha_fetch_develop").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assert_parou_no_6a(r, "a busca dela falhou")
        self.assertIn("git fetch origin develop", r.stderr)

    def test_6a_base_que_conflita_nos_checks_para_sem_mesclar(self):
        antigo = self.git("rev-parse", "melhoria/x")
        self.base_anda_nos_checks("b")  # a branch criou `b` com outro conteúdo
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assert_parou_no_6a(r, "o merge dela em melhoria/x tem conflito")
        self.assertIn("  b", r.stderr.splitlines())
        self.assertEqual((self.git("rev-parse", "melhoria/x"), self.head_remoto("melhoria/x")), (antigo, antigo))

    def test_6a_falha_do_merge_tree_para(self):  # no 2b o head já contém a base: só o 6a chama o merge-tree
        self.base_anda_nos_checks("bin/y")
        (self.estado / "merge_tree_falha").write_text("")
        self.assert_parou_no_6a(self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar"), "não consegui calcular o merge")

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


    # ---- LOTE-FECHAR2 (volta 6): ramo de falha de cada guarda que o lote reescreveu ou que a QA achou sem teste ----
    def test_a1_pasta_do_log_que_nao_e_diretorio_e_recusada_com_a_mensagem_propria(self):
        # o mkdir -p falso diz "ok" para um arquivo comum; só a checagem -d && ! -L pode recusar (sem ela, o erro viria do cd, com outra mensagem)
        arquivo = self.tmp / "arquivo-no-lugar-da-pasta"
        arquivo.write_text("x\n")
        (self.tmp / "bin" / "mkdir").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        (self.tmp / "bin" / "mkdir").chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(arquivo))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("a pasta do log não é um diretório", r.stderr)
        self.assertEqual(arquivo.read_text(), "x\n")
        self.assertEqual(self.chamadas(), [])

    def test_a3_pr_merged_sem_commit_de_merge_vazio_ou_traco_nao_conta_como_sucesso(self):
        for nome, conteudo in (("merge_commit", ""), ("merge_commit_vazio", "1")):
            with self.subTest(caso=nome):
                for f in ("merge_commit", "merge_commit_vazio", "estado", "aberto"):
                    (self.estado / f).unlink(missing_ok=True)
                (self.estado / nome).write_text(conteudo)
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("consta MERGED sem commit de merge", r.stderr)
                self.assertNotIn("merge: ", r.stdout)
                self.assertEqual(self.git("branch", "--list", "melhoria/x"), "melhoria/x")  # a limpeza não chega a rodar

    def test_a4_a_mensagem_da_base_conta_os_commits_no_plural(self):
        self.base_anda({"outro.md": "x\n"})
        self.base_anda({"outro2.md": "y\n"})
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("a base andou 2 commits sem conflito com melhoria/x", r.stdout)



    # ---- FECHAR-1C-ANTES-DO-2B (v0478): o 1c confere a árvore do merge com a base, a que o 2b traria ----
    def conferidos_no_1c(self):
        return [l.split()[1] for l in (self.estado / "promover").read_text().splitlines()]

    def test_1c_base_andou_sem_conflito_confere_o_merge_da_base_com_o_head(self):
        antigo = self.git("rev-parse", "melhoria/x")
        self.base_anda({"outro.md": "x\n"})
        base_sha = self.git("rev-parse", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        primeiro = self.conferidos_no_1c()[0]
        self.assertEqual(self.git("rev-list", "--parents", "-n", "1", primeiro).split(), [primeiro, antigo, base_sha])
        self.assertEqual(self.git("rev-parse", f"{primeiro}^{{tree}}"), self.git("merge-tree", "--write-tree", antigo, base_sha))
        self.assertIn(f"1c: confiro a árvore do merge de origin/develop em melhoria/x ({primeiro[:12]}, merge-tree limpo).", r.stdout)

    def test_1c_branch_com_versao_velha_e_base_com_a_nova_passa_pelo_merge(self):
        # o defeito: a branch nasceu antes da release (versão velha na árvore dela); o 1c recusava a árvore da branch
        (self.tmp / "promover.py").write_text(
            "import json, subprocess, sys\n"
            "v = json.loads(subprocess.run(['git', 'show', sys.argv[2] + ':.claude-plugin/plugin.json'], capture_output=True, text=True).stdout)\n"
            "sys.exit(0 if v.get('version') == '0.2.0' else 1)\n", encoding="utf-8")
        self.base_anda({".claude-plugin/plugin.json": '{\n  "name": "forge",\n  "version": "0.2.0"\n}\n'})
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertNotIn("parou no passo 1c", r.stderr)

    def test_1c_que_recusa_diz_que_e_a_arvore_da_branch_e_nao_a_develop(self):
        antigo = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", PROMOVER_RC="1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(f"parou no passo 1c: a árvore de melhoria/x (head {antigo[:12]}) não é promovível", r.stderr)
        self.base_anda({"outro.md": "x\n"})
        r = self.fechar("p1", "--ref", "melhoria/x", PROMOVER_RC="1")
        self.assertIn("parou no passo 1c: a árvore do merge de origin/develop em melhoria/x (", r.stderr)
        self.assertEqual((self.criacoes(), self.merges()), ([], []))

    def test_1c_com_conflito_ou_falha_do_merge_confere_o_head(self):
        for marca, arquivos in (("", {"b": "da base\n"}), ("merge_tree_falha", {"outro.md": "x\n"}),
                                ("falha_commit-tree", {"outro.md": "x\n"})):
            with self.subTest(marca=marca or "conflito"):
                self.setUp()
                antigo = self.git("rev-parse", "melhoria/x")
                self.base_anda(arquivos)
                if marca:
                    (self.estado / marca).write_text("1")
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("parou no passo 2b", r.stderr)
                self.assertEqual(self.conferidos_no_1c(), [antigo])


if __name__ == "__main__":
    unittest.main()
