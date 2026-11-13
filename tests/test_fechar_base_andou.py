"""N-FECHAR-a, A5 e E8 (0.45.6): passos 2b e 6a de `bin/forge-fechar`: a base que andou só para com conflito real e nunca é trazida.

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
case "$1 $2" in
  "ls-remote origin")
    # $ESTADO/ls_develop_falha: sem resposta do servidor para a develop (só ela)
    if [ -f "$ESTADO/ls_develop_falha" ] && [ "$3" = refs/heads/develop ]; then echo "fatal: unable to access" >&2; exit 128; fi
    # $ESTADO/ls_ref_falha: sem resposta do servidor para a branch da entrega (passo 2); $ESTADO/ls_ref_lixo: a coluna 1 não é sha
    if [ -f "$ESTADO/ls_ref_falha" ] && [ "$3" = refs/heads/melhoria/x ]; then echo "fatal: unable to access" >&2; exit 128; fi
    if [ -f "$ESTADO/ls_ref_lixo" ] && [ "$3" = refs/heads/melhoria/x ]; then printf '%s\t%s\n' "$(cat "$ESTADO/ls_ref_lixo")" "$3"; exit 0; fi ;;
  "merge-tree --write-tree")
    # $ESTADO/merge_tree_falha: o git não sabe `merge-tree --write-tree` (anterior ao 2.38) ou falha ao calcular
    if [ -f "$ESTADO/merge_tree_falha" ]; then echo "usage: git merge-tree" >&2; exit 129; fi ;;
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

    def test_c5_base_que_andou_sem_conflito_avisa_e_segue(self):
        self.base_anda({"outro.md": "x\n"})
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("a base andou 1 commit sem conflito com melhoria/x; não trago a base (E8)", r.stdout)
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
        self.assertIn("sem conflito avisa e segue, sem trazer a base (E8)", r.stdout)
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

    def test_e8_arquivo_em_comum_sem_conflito_segue_sem_trazer_a_base(self):
        self._arquivo_em_comum_sem_conflito("melhoria/r")

    def test_e8_fora_de_melhoria_e_o_mesmo_nenhuma_branch_recebe_o_merge(self):
        self._arquivo_em_comum_sem_conflito("feature/z")

    def test_e8_base_que_mudou_codigo_segue_sem_trazer_a_base(self):
        antigo = self.git("rev-parse", "melhoria/x")
        (self.proj / "bin").mkdir(exist_ok=True)
        self.base_anda({"bin/x": "da base\n"})
        self.assert_segue_sem_trazer("melhoria/x", antigo, self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar"))

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

    def test_6a_base_local_velha_para_e_pede_o_fetch(self):
        self.base_anda_nos_checks("docs/nota.txt", local=False)
        self.assert_parou_no_6a(self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar"), "git fetch origin develop")

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



if __name__ == "__main__":
    unittest.main()
