"""FC-ENTREGA-GIT-FALHA-ABERTA (E3 da 0.33): a falha do git num passo do escopo reprova a `forge-check entrega` em toda etapa;
nunca vira "nada a conferir" nem tira arquivo de um filtro. Um `git` falso no PATH sai 128 só na N-ésima chamada que casa o padrão."""
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ambiente_limpo, git  # noqa: E402
from test_volta_por_delta import FORGE_CHECK, Repositorio, carregar_forge_check  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

GIT_FALSO = '#!/bin/sh\ncase "$*" in $PADRAO) n=$(cat "$CONTAGEM" 2>/dev/null || echo 0); n=$((n+1)); echo $n > "$CONTAGEM"; { [ "$n" = "$ORDEM" ] || [ "$ORDEM" = todas ]; } && exit 128;; esac\nexec "$O_GIT_DE_VERDADE" "$@"\n'
LINHA = "escopo: o git falhou ("
SEM_COMMIT = "escopo: sem commit (nada a conferir)"
TRES = "*--name-only*...*"  # diff `de...ate`
DOIS = "*--name-only*[!.]..[!.]*"  # diff `de..ate`


class FalhaDoGit(Repositorio):
    def setUp(self):
        super().setUp()
        self.pasta = self.tmp / "falso"
        self.pasta.mkdir()
        falso = self.pasta / "git"
        falso.write_text(GIT_FALSO, encoding="utf-8")
        falso.chmod(falso.stat().st_mode | stat.S_IXUSR)
        self.c1 = self.commitar({"a.txt": "1\n"}, "trabalho")
        self.gravar_pedido()

    def falhar(self, padrao, ordem, *args):
        return self.rodar(padrao, ordem, "entrega", str(self.pedido), "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base, *args)

    def rodar(self, padrao, ordem, *args):
        env = dict(ambiente_limpo(), HOME=str(self.home), PATH=f"{self.pasta}:{os.environ['PATH']}", PADRAO=padrao, ORDEM=str(ordem),
                   CONTAGEM=str(self.tmp / "contagem"), O_GIT_DE_VERDADE=shutil.which("git"))
        (self.tmp / "contagem").unlink(missing_ok=True)
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.repo), *args], env=env, capture_output=True, text=True)
        return r.returncode, r.stdout

    def reprova(self, padrao, ordem, *args, passo=None):
        rc, saida = self.falhar(padrao, ordem, *args)
        self.assertEqual(rc, 1, saida)
        self.assertTrue(any(l.startswith(LINHA + (passo or "")) and l.endswith("); o escopo não foi lido") for l in saida.splitlines()), saida)
        self.assertNotIn(SEM_COMMIT, saida)

    def integrar_a_base(self):
        """A develop anda e entra na branch por merge (dois pais); o `desde` é o commit já conferido."""
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar({"base.txt": "b\n"}, "a base anda")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("merge", "-q", "--no-ff", "-m", "integra a base", "develop", cwd=self.repo)
        self.gravar_pedido([self.c1])

    def squash(self):
        """O forge-fechar integrou por squash e apagou a ref: o head é o mergeCommit (um pai só), já na develop."""
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar({"outro.txt": "o\n"}, "outro PR já na develop")
        git("merge", "-q", "--squash", "melhoria/x", cwd=self.repo)
        git("commit", "-q", "-m", "squash", cwd=self.repo)
        git("branch", "-q", "-D", "melhoria/x", cwd=self.repo)
        return self.head()

    def test_diff_do_merge_integrado_falha_e_reprova(self):  # C-5/C-6: o 2º diff `..` é o do squash
        merge = self.squash()
        self.reprova(DOIS, 3, "--etapa", "merge-integracao", "--branch", merge, passo="diff do merge integrado")

    def test_falha_depois_de_um_filtro_saudavel_mostra_a_lista_inteira(self):  # C-3, exibição: o filtro que já rodou não esconde arquivo
        merge = self.squash()
        rc, saida = self.falhar(DOIS, 3, "--etapa", "merge-integracao", "--branch", merge)
        self.assertEqual(rc, 1, saida)
        self.assertIn("o git falhou (diff do merge integrado)", saida)
        self.assertIn('escopo: confira "a.txt"', saida)
        self.assertNotIn("integração da base", saida)  # o filtro que a lista não passou a ter não é anunciado

    def test_rev_list_dos_pais_do_head_do_cmd_entrega_tem_teste_proprio(self):  # a 1ª chamada homônima é a de `diferem_dos_dois_pais`
        for etapa in ("codigo", "review", "merge-integracao"):
            with self.subTest(etapa=etapa):
                self.reprova("*rev-list --parents -n 1*", 2, "--etapa", etapa, passo="rev-list dos pais do head")

    def test_passos_do_caminho_simples_em_toda_etapa(self):
        for etapa in ("codigo", "review", "merge-integracao"):
            for nome, padrao, ordem in (("diff da entrega", TRES, 1), ("rev-list dos pais do head", "*rev-list --parents -n 1*", 1),
                                        ("contagens do diff", "*--numstat*", 1)):
                with self.subTest(etapa=etapa, passo=nome):
                    self.reprova(padrao, ordem, "--etapa", etapa, passo=nome)

    def test_sem_base_na_entrega_e_falha_do_git(self):  # o `rev-parse` da base falha em todos os candidatos
        for etapa in ("codigo", "review", "merge-integracao"):
            with self.subTest(etapa=etapa):
                self.reprova("*--verify --quiet [!-]*", "todas", "--etapa", etapa, passo="base da entrega")

    def test_base_pedida_que_falha_nao_cai_para_as_bases(self):  # só o Base-sha falha no rev-parse; a develop segue lendo
        for etapa in ("codigo", "review", "merge-integracao"):
            with self.subTest(etapa=etapa):
                self.reprova(f"*--verify --quiet {self.base}*", "todas", "--etapa", etapa, passo="base da entrega")

    def test_base_pedida_que_falha_so_na_primeira_leitura_reprova(self):  # A6: a 2ª leitura acerta; a lista nunca sai de outra base com rc 0
        for etapa in ("codigo", "review", "merge-integracao"):
            with self.subTest(etapa=etapa):
                self.reprova(f"*--verify --quiet {self.base}*", 1, "--etapa", etapa, passo="diff da entrega")

    def test_so_o_diff_que_falha_nao_anuncia_a_base_ausente(self):  # AR-1: o rótulo "base da entrega" só vale com a base ilegível
        for etapa in ("codigo", "review", "merge-integracao"):
            with self.subTest(etapa=etapa):
                rc, saida = self.falhar(TRES, 1, "--etapa", etapa)
                self.assertEqual(rc, 1, saida)
                self.assertIn(LINHA + "diff da entrega)", saida)
                self.assertNotIn("base da entrega", saida)

    def test_rev_parse_do_objeto_que_falha_nos_dois_lados_nao_tira_o_arquivo(self):  # L08: "igual à base" exige código 0 nos dois
        merge = self.squash()
        rc, saida = self.falhar("*nunca-casa*", 1, "--etapa", "review", "--branch", merge)
        self.assertIn(SEM_COMMIT, saida)  # saudável: o squash já está na base, nada a conferir
        rc, saida = self.falhar("*rev-parse *:*", "todas", "--etapa", "review", "--branch", merge)
        self.assertNotIn(SEM_COMMIT, saida)
        self.assertIn('escopo: confira "a.txt"', saida)

    def test_passos_do_desde_em_toda_etapa(self):
        self.commitar({"b.txt": "2\n"}, "segunda delegação")
        self.gravar_pedido([self.c1])
        for etapa in ("codigo", "review"):
            for nome, padrao, ordem in (("diff da entrega", DOIS, 1), ("diff da entrega", TRES, 2),
                                        ("diff do que a branch já mudou até a conferida", TRES, 3)):
                with self.subTest(etapa=etapa, ordem=ordem):
                    self.reprova(padrao, ordem, "--desde", self.c1, "--etapa", etapa, passo=nome)

    def test_passos_do_merge_da_base_com_desde(self):
        self.integrar_a_base()
        for etapa in ("codigo", "review"):
            for nome, padrao, ordem in (("rev-list dos pais do head", "*rev-list --parents -n 1*", 1),
                                        ("rev-list dos commits próprios", "*rev-list*--not*", 1),
                                        ("diff contra um dos pais", DOIS, 2), ("diff contra um dos pais", DOIS, 3),
                                        ("diff contra um dos pais", "*--numstat*", 1),
                                        ("diff do que a branch já mudou até a conferida", TRES, 3)):
                with self.subTest(etapa=etapa, passo=nome, ordem=ordem):
                    self.reprova(padrao, ordem, "--desde", self.c1, "--etapa", etapa, passo=nome)

    def test_passos_do_primeiro_pai_sem_desde(self):
        self.integrar_a_base()
        self.commitar({"c.txt": "3\n"}, "trabalho depois do merge")
        for nome, padrao, ordem in (("rev-list do primeiro pai", "*rev-list --first-parent*", 1),
                                    ("diff do commit contra o primeiro pai", DOIS, 1),
                                    ("diff do merge da base", DOIS, 3),
                                    ("diff do merge da base", "*merge-base [!-]*", 1),
                                    ("diff do ancestral comum", DOIS, 4)):
            with self.subTest(passo=nome, ordem=ordem):
                self.reprova(padrao, ordem, "--etapa", "codigo", passo=nome)

    def test_filtro_e4_com_outro_passo_falho_nao_tira_arquivo(self):  # C-3: o que a base trouxe só sai da lista com o git inteiro saudável
        self.integrar_a_base()
        rc, saida = self.falhar("*nunca-casa*", 1, "--etapa", "merge-integracao")
        self.assertNotIn('escopo: confira "base.txt"', saida)
        rc, saida = self.falhar("*--numstat*", 1, "--etapa", "merge-integracao")
        self.assertIn("o git falhou (contagens do diff)", saida)
        self.assertIn('escopo: confira "base.txt"', saida)

    def test_merge_de_outra_coisa_nao_e_integracao_da_base(self):  # o conteúdo do outro pai não some do escopo
        git("switch", "-q", "-c", "outra", self.base, cwd=self.repo)
        self.commitar({"o.txt": "o\n"}, "outra coisa")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("merge", "-q", "--no-ff", "-m", "traz a outra coisa", "outra", cwd=self.repo)
        self.gravar_pedido([self.c1])
        rc, saida = self.falhar("*nunca-casa*", 1, "--desde", self.c1, "--etapa", "codigo")
        self.assertIn('escopo: confira "o.txt"', saida)

    def test_integracao_limpa_nao_le_o_primeiro_pai(self):  # com os dois pais lidos, o rev-list do primeiro pai nem roda
        self.integrar_a_base()
        rc, saida = self.falhar("*rev-list --first-parent*", "todas", "--desde", self.c1, "--etapa", "codigo")
        self.assertNotIn(LINHA, saida)

    def test_branch_cujo_git_falhou_fica_fora_da_sobreposicao(self):  # informativo: nunca entra como vazia
        git("switch", "-q", "-c", "melhoria/y", self.base, cwd=self.repo)
        self.commitar({"a.txt": "2\n"}, "mesmo arquivo")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        rc, saida = self.rodar("*nunca-casa*", 1, "sobreposicao", "--base", "develop")
        self.assertIn("a.txt", saida)
        rc, saida = self.rodar("*--name-only*...*", 1, "sobreposicao", "--base", "develop")
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("a.txt", saida)

    def test_filtro_que_falha_nao_tira_arquivo(self):
        self.integrar_a_base()  # a integração limpa não tem escopo próprio: com o git saudável, só o que a branch fez
        rc, saida = self.falhar("*--numstat*", 1, "--desde", self.c1, "--etapa", "codigo")
        self.assertEqual(rc, 1, saida)
        self.assertNotIn("integração da base", saida)  # o filtro não rodou: a lista sai inteira, com o que a falha deixou
        self.assertIn('escopo: confira "base.txt"', saida)

    def test_git_saudavel_nao_muda(self):
        for etapa in ("codigo", "review", "merge-integracao"):
            rc, saida = self.falhar("*nunca-casa*", 1, "--etapa", etapa)
            self.assertEqual(rc, 1 if etapa == "merge-integracao" else 0, saida)  # merge-integracao sem pareceres no head reprova; o git saudável não muda o resto
            self.assertNotIn(LINHA, saida)
            self.assertIn('escopo: confira "a.txt" +1 -0', saida)

    def test_sem_commit_so_com_todos_os_git_em_zero(self):
        git("reset", "-q", "--hard", self.base, cwd=self.repo)
        self.gravar_pedido()
        rc, saida = self.falhar("*nunca-casa*", 1, "--etapa", "review")
        self.assertEqual((rc, SEM_COMMIT in saida), (0, True), saida)
        self.reprova(TRES, 1, "--etapa", "review", passo="diff da entrega")

    def test_git_que_falha_exige_todos_os_portoes_sem_excecao(self):  # C-4: o `cmd_pr` e o hook `parecer` nunca exigem menos
        fc = carregar_forge_check()
        fc.arquivos_da_entrega = lambda *a, **k: None
        self.assertEqual(fc.gatilhos(self.repo, "p1"), (True, ["o git falhou: o diff da entrega não foi lido"]))
        self.assertEqual(fc.exigidos_do_pr(self.repo, "p1")[0], ["review", "qa", "revisao-devops", "revisao-seguranca"])


class DeltaGitFalha(Repositorio):
    """FC-DELTA-GIT-FALHA (0.43.2): no `delta` e no `parecer delta`, a falha do git sai com rc 2 e a linha `o delta não foi lido`;
    nunca `delta: nenhum` nem `nenhum arquivo do domínio mudou`, que aprovariam por engano. O mesmo `git` falso da `FalhaDoGit`."""
    FALHA = "o delta não foi lido"
    SEG = ("---\ntipo: revisao-seguranca\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
           "revisor: forge:security-engineer\ndata: 2026-11-08\n---\n# s\n")
    rodar = FalhaDoGit.rodar

    def setUp(self):
        super().setUp()
        self.pasta = self.tmp / "falso"
        self.pasta.mkdir()
        (self.pasta / "git").write_text(GIT_FALSO, encoding="utf-8")
        (self.pasta / "git").chmod(0o755)
        self.c1 = self.commitar({"a.txt": "1\n"}, "trabalho")
        self.commitar({"docs/security/p1.md": self.SEG.format(c=self.c1)}, "parecer")
        self.commitar({"a.txt": "2\n"}, "correção")

    def assert_falha(self, rc, saida):
        self.assertEqual(rc, 2, saida)
        self.assertIn(self.FALHA, saida)
        self.assertNotIn("nenhum", saida)

    def test_cada_passo_do_git_que_falha_da_rc_2(self):
        for padrao in (DOIS, "*--numstat*", "*-U0*", "*--first-parent*"):
            with self.subTest(padrao):
                self.assert_falha(*self.rodar(padrao, 1, "delta", self.c1))
        for padrao in (DOIS, "*--first-parent*", "*diff --no-ext-diff*"):
            with self.subTest(parecer=padrao):
                self.assert_falha(*self.rodar(padrao, 1, "parecer", "delta", "docs/security/p1.md"))

    def test_git_inexistente_da_rc_2(self):
        vazio = self.tmp / "sem-git"
        vazio.mkdir()
        for args in (("delta", self.c1), ("parecer", "delta", "docs/security/p1.md")):
            with self.subTest(args[0]):
                r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.repo), *args], capture_output=True, text=True,
                                   env=dict(ambiente_limpo(), HOME=str(self.home), PATH=str(vazio)))
                self.assert_falha(r.returncode, r.stdout)
                self.assertIn("FileNotFoundError", r.stdout)

    def test_ref_ruim_e_base_fora_da_lista_dao_rc_2(self):
        for args in (("delta", self.c1, "nao-existe"), ("delta", "nao-existe"), ("delta", self.c1, "--base", "melhoria/x"),
                     ("parecer", "delta", "docs/security/p1.md", "--ate", "nao-existe"),
                     ("parecer", "delta", "docs/security/p1.md", "--base", "melhoria/x")):
            with self.subTest(args):
                rc, saida = self.rodar("*nunca-casa*", 1, *args)
                self.assertEqual(rc, 2, saida)
                self.assertNotIn("nenhum", saida)

    def test_git_saudavel_nao_muda_o_delta(self):
        rc, saida = self.rodar("*nunca-casa*", 1, "delta", self.c1)
        self.assertEqual(rc, 0, saida)
        self.assertIn('delta: "a.txt" +1 -1', saida)
        self.assertNotIn(self.FALHA, saida)
