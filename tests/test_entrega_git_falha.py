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
        env = dict(ambiente_limpo(), HOME=str(self.home), PATH=f"{self.pasta}:{os.environ['PATH']}", PADRAO=padrao, ORDEM=str(ordem),
                   CONTAGEM=str(self.tmp / "contagem"), O_GIT_DE_VERDADE=shutil.which("git"))
        (self.tmp / "contagem").unlink(missing_ok=True)
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.repo), "entrega", str(self.pedido), "--branch", "melhoria/x",
                            "--base", "develop", "--base-sha", self.base, *args], env=env, capture_output=True, text=True)
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
                                        ("diff contra um dos pais", "*--numstat*", 1)):
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
