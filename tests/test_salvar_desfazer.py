"""Primeiro uso (F2): `forge salvar` e `forge desfazer` em repositórios temporários, sem rede.

O remoto é um repositório bare local. HOME, configuração do git e PATH são do teste; o `gh` do PATH é falso
(nenhum destes comandos deve precisar dele).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="salvar-"))
        self.home = self.tmp / "home"
        bin_falso = self.tmp / "bin"
        bin_falso.mkdir()
        self.home.mkdir()
        (bin_falso / "gh").write_text('#!/usr/bin/env bash\necho "gh falso: $*" >&2\nexit 64\n', encoding="utf-8")
        (bin_falso / "gh").chmod(0o755)
        (self.home / "gitconfig").write_text(
            "[user]\n\tname = Pessoa Teste\n\temail = pessoa@exemplo.test\n[init]\n\tdefaultBranch = main\n",
            encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CLAUDE_PROJECT_DIR"}
        self.env.update(HOME=str(self.home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.home / "gitconfig"),
                        PATH=f"{bin_falso}:{os.environ['PATH']}")
        self.env = sem_manutencao(self.env)
        self.remoto = self.tmp / "remoto.git"
        self.proj = self.tmp / "proj"
        self.git("init", "-q", "--bare", str(self.remoto), cwd=self.tmp)
        remoto_sem_manutencao(self.remoto)
        self.git("clone", "-q", str(self.remoto), str(self.proj), cwd=self.tmp)
        self.escrever("README.md", "um\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: inicio")
        self.git("push", "-q", "origin", "main")
        self.git("branch", "develop")
        self.git("push", "-q", "origin", "develop")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, *args, cwd=None):
        r = subprocess.run(["git", *args], cwd=cwd or self.proj, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def escrever(self, nome, texto):
        (self.proj / nome).write_text(texto, encoding="utf-8")

    def forge(self, sub, *args, entrada="", cwd=None):
        return subprocess.run(["bash", str(RAIZ / "bin/forge"), sub, *args], input=entrada, env=self.env,
                              cwd=cwd or self.proj, capture_output=True, text=True, timeout=60)

    def saida(self, r):
        return r.stdout + r.stderr

    def ramo(self):
        return self.git("branch", "--show-current")

    def topo_remoto(self, ramo):
        return self.git("rev-parse", ramo, cwd=self.remoto)


class Salvar(Base):
    def test_em_develop_cria_ramo_de_trabalho_e_nao_mexe_nas_protegidas(self):
        antes = {r: self.topo_remoto(r) for r in ("main", "develop")}
        self.escrever("a.txt", "x\n")
        r = self.forge("salvar", "adiciona a")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertRegex(self.ramo(), r"^trabalho/\d{8}-\d{4}$")
        self.assertEqual(self.git("log", "-1", "--format=%s"), "adiciona a")
        self.assertEqual(self.topo_remoto(self.ramo()), self.git("rev-parse", "HEAD"))
        for ramo, topo in antes.items():
            self.assertEqual(self.topo_remoto(ramo), topo)

    def test_em_main_nunca_commita_na_main(self):
        topo = self.topo_remoto("main")
        self.escrever("a.txt", "x\n")
        r = self.forge("salvar", "adiciona a")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertNotEqual(self.ramo(), "main")
        self.assertEqual(self.git("rev-parse", "main"), topo)
        self.assertEqual(self.topo_remoto("main"), topo)

    def test_em_ramo_de_trabalho_continua_nele(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever("a.txt", "x\n")
        r = self.forge("salvar")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertEqual(self.ramo(), "feature/x")
        self.assertEqual(self.topo_remoto("feature/x"), self.git("rev-parse", "HEAD"))
        self.assertTrue(self.git("log", "-1", "--format=%s"))

    def test_sem_mudancas_diz_que_nao_ha_o_que_salvar(self):
        topo = self.git("rev-parse", "HEAD")
        r = self.forge("salvar", "nada")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertRegex(self.saida(r), r"(?i)nada.*salvar")
        self.assertEqual(self.git("rev-parse", "HEAD"), topo)
        self.assertEqual(self.ramo(), "main")

    def test_recusa_arquivo_de_segredo(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever(".env", "SENHA=1\n")
        r = self.forge("salvar", "oops")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(".env", self.saida(r))
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: inicio")

    def test_respeita_gitignore(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever(".gitignore", "lixo.txt\n")
        self.escrever("lixo.txt", "x\n")
        self.assertEqual(self.forge("salvar", "ignora").returncode, 0)
        self.assertNotIn("lixo.txt", self.git("ls-files"))

    def test_fora_de_repositorio_explica(self):
        r = self.forge("salvar", cwd=self.home)
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(r.stderr, r"(?i)não.*(projeto|repositório)")
        self.assertNotIn("fatal", r.stderr)

    def test_falha_no_envio_diz_que_o_trabalho_ficou_salvo_na_pasta(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.git("remote", "set-url", "origin", str(self.tmp / "nao-existe.git"))
        self.escrever("a.txt", "x\n")
        r = self.forge("salvar", "a")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)salvo.*pasta")
        self.assertEqual(self.git("log", "-1", "--format=%s"), "a")

    def conflito_em_andamento(self):
        """Deixa uma mesclagem parada por conflito em a.txt, na branch feature/x."""
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever("a.txt", "base\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "a base")
        self.git("checkout", "-q", "-b", "feature/y")
        self.escrever("a.txt", "y\n")
        self.git("commit", "-q", "-am", "a y")
        self.git("checkout", "-q", "feature/x")
        self.escrever("a.txt", "x\n")
        self.git("commit", "-q", "-am", "a x")
        r = subprocess.run(["git", "merge", "feature/y"], cwd=self.proj, env=self.env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)

    def test_envio_recusado_por_mudanca_no_github_nao_diz_rede_ou_permissao(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.git("push", "-q", "origin", "feature/x")
        outro = self.tmp / "outro"
        self.git("clone", "-q", "-b", "feature/x", str(self.remoto), str(outro), cwd=self.tmp)
        (outro / "o.txt").write_text("o\n", encoding="utf-8")
        self.git("add", "-A", cwd=outro)
        self.git("commit", "-q", "-m", "do outro", cwd=outro)
        self.git("push", "-q", "origin", "feature/x", cwd=outro)
        self.escrever("a.txt", "x\n")
        r = self.forge("salvar", "a")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)alguém|mudou")
        self.assertNotRegex(self.saida(r), r"(?i)rede ou permissão")
        self.assertRegex(self.saida(r), r"(?i)Jarvis")

    def test_recusa_com_mesclagem_em_andamento_sem_commitar_marcas(self):
        self.conflito_em_andamento()
        topo = self.git("rev-parse", "HEAD")
        r = self.forge("salvar", "tenta")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)conflito|mescla")
        self.assertNotIn("fatal", self.saida(r))
        self.assertEqual(self.git("rev-parse", "HEAD"), topo)

    def test_recusa_marcas_de_conflito_ja_resolvidas_no_indice(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever("a.txt", "<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> outro\n")
        r = self.forge("salvar", "tenta")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("a.txt", self.saida(r))
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: inicio")

    def test_recusa_segredo_ja_preparado_com_git_add(self):
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever(".env", "SENHA=1\n")
        self.git("add", "-f", ".env")
        self.escrever("b.txt", "b\n")
        r = self.forge("salvar", "oops")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(".env", self.saida(r))
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: inicio")


    def test_segredo_em_pasta_com_acento_e_espaco_e_recusado(self):  # BUG-F2-01
        (self.proj / "pasta ção").mkdir()
        (self.proj / "pasta ção/.env").write_text("K=1\n", encoding="utf-8")
        r = self.forge("salvar", "a")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("pasta ção/.env", self.saida(r))
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: inicio")

    def test_marca_de_conflito_em_pasta_com_acento_e_recusada(self):  # BUG-F2-01
        (self.proj / "configurações").mkdir()
        (self.proj / "configurações/a.txt").write_text("<<<<<<< HEAD\nx\n", encoding="utf-8")
        r = self.forge("salvar", "a")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("configurações/a.txt", self.saida(r))
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: inicio")

    def test_marca_de_conflito_em_arquivo_com_nome_iniciado_por_traco_e_recusada(self):  # BUG-F2-07
        self.escrever("-rf.txt", "<<<<<<< HEAD\nx\n")
        r = self.forge("salvar", "a")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("-rf.txt", self.saida(r))
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: inicio")

    def test_reenvia_o_que_ficou_salvo_em_ramo_sem_versao_remota(self):  # BUG-F2-02
        self.git("checkout", "-q", "-b", "feature/x")
        url = self.git("remote", "get-url", "origin")
        self.git("remote", "set-url", "origin", str(self.tmp / "nao-existe.git"))
        self.escrever("a.txt", "x\n")
        self.assertNotEqual(self.forge("salvar", "a").returncode, 0)
        self.git("remote", "set-url", "origin", url)
        r = self.forge("salvar")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertRegex(self.saida(r), r"(?i)enviei")
        self.assertEqual(self.topo_remoto("feature/x"), self.git("rev-parse", "HEAD"))

    def test_recusa_do_servidor_nao_diz_que_alguem_mudou_o_trabalho(self):  # F2-03
        hook = self.remoto / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\necho proibido >&2\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever("a.txt", "x\n")
        r = self.forge("salvar", "a")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)servidor|proteção|recus")
        self.assertNotRegex(self.saida(r), r"(?i)alguém mudou")
        self.assertRegex(self.saida(r), r"(?i)salvo.*pasta")


class Desfazer(Base):
    def setUp(self):
        super().setUp()
        self.git("checkout", "-q", "-b", "feature/x")
        self.escrever("b.txt", "bom\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "feat: adiciona b")
        self.git("push", "-q", "origin", "feature/x")

    def test_alteracoes_nao_salvas_vao_para_o_stash_so_com_confirmacao(self):
        self.escrever("README.md", "mudou\n")
        self.escrever("novo.txt", "n\n")
        r = self.forge("desfazer", entrada="n\n")
        self.assertIn("README.md", self.saida(r))
        self.assertTrue((self.proj / "novo.txt").exists(), "sem 'sim', nada muda")
        r = self.forge("desfazer", entrada="sim\n")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertIn("desfeito", self.git("stash", "list"))
        self.assertFalse((self.proj / "novo.txt").exists())

    def test_recuperar_traz_de_volta_o_que_foi_guardado(self):
        self.escrever("novo.txt", "n\n")
        self.assertEqual(self.forge("desfazer", entrada="sim\n").returncode, 0)
        r = self.forge("desfazer", "--recuperar", entrada="sim\n")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertEqual((self.proj / "novo.txt").read_text(encoding="utf-8"), "n\n")
        self.assertEqual(self.git("stash", "list"), "")

    def test_ultimo_commit_vira_revert_e_a_historia_so_cresce(self):
        antes = int(self.git("rev-list", "--count", "HEAD"))
        ruim = self.git("rev-parse", "HEAD")
        r = self.forge("desfazer", entrada="sim\n")
        self.assertEqual(r.returncode, 0, self.saida(r))
        self.assertIn("feat: adiciona b", self.saida(r))
        self.assertIn("b.txt", self.saida(r))
        self.assertEqual(int(self.git("rev-list", "--count", "HEAD")), antes + 1)
        self.assertFalse((self.proj / "b.txt").exists())
        self.assertEqual(self.git("merge-base", "--is-ancestor", ruim, "HEAD") or "", "")
        self.assertEqual(self.topo_remoto("feature/x"), self.git("rev-parse", "HEAD"))

    def test_sem_confirmacao_nao_desfaz(self):
        topo = self.git("rev-parse", "HEAD")
        for resposta in ("n\n", "\n", ""):
            with self.subTest(resposta=resposta):
                self.forge("desfazer", entrada=resposta)
                self.assertEqual(self.git("rev-parse", "HEAD"), topo)
                self.assertTrue((self.proj / "b.txt").exists())

    def test_recusa_commit_de_merge(self):
        self.git("checkout", "-q", "-b", "feature/y", "main")
        self.escrever("c.txt", "c\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "feat: c")
        self.git("merge", "-q", "--no-ff", "-m", "merge b", "feature/x")
        topo = self.git("rev-parse", "HEAD")
        r = self.forge("desfazer", entrada="sim\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)mescla")
        self.assertEqual(self.git("rev-parse", "HEAD"), topo)

    def test_recusa_com_mesclagem_em_andamento_sem_erro_cru(self):
        self.git("checkout", "-q", "-b", "feature/y", "main")
        self.escrever("b.txt", "outro\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "feat: b diferente")
        r = subprocess.run(["git", "merge", "feature/x"], cwd=self.proj, env=self.env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        r = self.forge("desfazer", entrada="sim\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)mescla")
        self.assertRegex(self.saida(r), r"(?i)Jarvis")
        self.assertNotIn("fatal", self.saida(r))
        self.assertNotIn("error:", self.saida(r))

    def test_recusa_nas_ramos_principais(self):
        for ramo in ("main", "develop"):
            with self.subTest(ramo=ramo):
                self.git("checkout", "-q", ramo)
                topo = self.git("rev-parse", "HEAD")
                r = self.forge("desfazer", entrada="sim\n")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(ramo, self.saida(r))
                self.assertEqual(self.git("rev-parse", "HEAD"), topo)

    def test_primeiro_commit_do_projeto_nao_e_desfeito(self):
        self.git("checkout", "-q", "--orphan", "solto")
        self.git("commit", "-q", "-m", "raiz", "--allow-empty")
        r = self.forge("desfazer", entrada="sim\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "1")

    def test_nada_a_desfazer_com_recuperar_vazio(self):
        r = self.forge("desfazer", "--recuperar", entrada="sim\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(self.saida(r), r"(?i)nada.*(recuperar|guardado)")

    def test_sem_commits_e_com_arquivo_novo_explica(self):  # F2-04
        vazio = self.tmp / "vazio"
        vazio.mkdir()
        self.git("init", "-q", cwd=vazio)
        (vazio / "n.txt").write_text("n\n", encoding="utf-8")
        r = self.forge("desfazer", entrada="sim\n", cwd=vazio)
        self.assertRegex(self.saida(r), r"(?i)ainda não há nenhum ponto salvo")
        self.assertTrue((vazio / "n.txt").exists())

    def test_recuperar_com_conflito_explica_em_portugues(self):  # F2-05
        self.escrever("b.txt", "guardado\n")
        self.assertEqual(self.forge("desfazer", entrada="sim\n").returncode, 0)
        self.escrever("b.txt", "outro\n")
        r = self.forge("desfazer", "--recuperar", entrada="sim\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotRegex(self.saida(r), r"(?i)error:|aborting|overwritten")
        self.assertNotIn("marcas de conflito", self.saida(r))
        self.assertRegex(self.saida(r), r"(?i)continua guardado")
        self.assertEqual((self.proj / "b.txt").read_text(encoding="utf-8"), "outro\n")
        self.assertIn("desfeito", self.git("stash", "list"))


class Garantias(unittest.TestCase):
    def test_scripts_nunca_usam_force_nem_reset_hard(self):
        for nome in ("forge-salvar", "forge-desfazer"):
            codigo = "\n".join(l for l in (RAIZ / "bin" / nome).read_text(encoding="utf-8").splitlines()
                               if not l.lstrip().startswith("#"))
            with self.subTest(script=nome):
                self.assertNotRegex(codigo, r"--force|--no-verify|reset\s+--hard|push\s+(-\w*f|\S*\s+\+)|clean\s+-f")

    def test_despachante_lista_salvar_e_desfazer(self):
        r = subprocess.run(["bash", str(RAIZ / "bin/forge")], capture_output=True, text=True)
        self.assertIn("salvar", r.stdout)
        self.assertIn("desfazer", r.stdout)


if __name__ == "__main__":
    unittest.main()
