"""GIT-CONTROLE-CONFIG-DA-COPIA, corte GC1: o ponto único `bin/forge_git.py` (anexo E3.1, seções 2 e 3.1).

Cada vetor da seção 2 vira um teste com duas metades: o git cru (como o `git()` de hoje: só sem `GIT_*`) executa o
programa que a cópia aponta (o marcador aparece), e o `forge_git` não executa (marcador ausente, ou `Recusado`).
Tudo em repositórios descartáveis no `TMPDIR`, com HOME temporário e sem rede; nenhum hook real é chamado.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "bin"))
import forge_git  # noqa: E402

NEUTRA_REAL = forge_git.PASTA_NEUTRA  # antes do patch de cada teste

AMBIENTE_LIMPO = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C", "TMPDIR": tempfile.gettempdir()}


class Base(unittest.TestCase):
    """Uma cópia com main e lado (os dois mudam `f`, conflito) e uma origin nua local; `x` grava o marcador."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-git-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        home = self.tmp / "home"
        home.mkdir()
        (home / ".gitconfig").write_text("[user]\n\tname = t\n\temail = t@t\n", encoding="utf-8")
        self.env = {**AMBIENTE_LIMPO, "HOME": str(home)}
        patcher = mock.patch.dict(os.environ, self.env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        neutra = mock.patch.object(forge_git, "PASTA_NEUTRA", self.tmp / "neutra")
        neutra.start()
        self.addCleanup(neutra.stop)
        self.marca = self.tmp / "marca"
        self.x = self.tmp / "x"
        self.x.write_text(f'#!/bin/sh\necho "$0" >> "{self.marca}"\nexit 0\n', encoding="utf-8")
        self.x.chmod(0o755)
        self.origem = self.tmp / "origem.git"
        self.copia = self.tmp / "copia"
        self.cru("init", "-q", "--bare", "-b", "main", str(self.origem), pasta=self.tmp)
        self.cru("init", "-q", "-b", "main", str(self.copia), pasta=self.tmp)
        for passo in (("commit", "a"), ("switch", "-qc", "lado"), ("commit", "b"), ("switch", "-q", "main"),
                      ("commit", "c")):
            if passo[0] == "commit":
                (self.copia / "f").write_text(passo[1] + "\n", encoding="utf-8")
                self.cru("add", "f")
                self.cru("commit", "-qm", passo[1])
            else:
                self.cru(*passo)
        self.cru("remote", "add", "origin", str(self.origem))
        self.cru("push", "-q", "origin", "main", "lado")
        os.utime(self.copia / "f", (946684800, 946684800))  # índice sujo: o status relê o arquivo

    def cru(self, *args, pasta=None):
        """O git sem o ponto único (o `git()` de hoje), na cópia por padrão."""
        return subprocess.run(["git", *args], cwd=pasta or self.copia, env=self.env, capture_output=True,
                              text=True, timeout=20, stdin=subprocess.DEVNULL)

    def config(self, chave, valor):
        self.cru("config", chave, valor)

    def executou(self):
        achou = self.marca.exists()
        self.marca.unlink(missing_ok=True)
        return achou

    def vermelho_cru(self, *args):
        self.cru(*args)
        self.assertTrue(self.executou(), f"o vetor não executou cru com git {args}: a sonda não prova nada")

    def verde(self, *args):
        """O forge_git roda ou recusa; o marcador não aparece."""
        try:
            forge_git.git(self.copia, *args)
        except forge_git.Recusado:
            pass
        self.assertFalse(self.executou(), f"o forge_git executou o vetor com git {args}")


class Vetores(Base):
    def test_hook_plantado_post_index_change_e_pre_commit(self):
        for hook in ("post-index-change", "pre-commit", "post-commit"):
            (self.copia / ".git" / "hooks" / hook).symlink_to(self.x)
        self.vermelho_cru("status", "--porcelain")
        self.verde("status", "--porcelain")
        self.assertEqual(forge_git.git(self.copia, "commit", "-q", "--allow-empty", "-m", "v")[0], 0)
        self.assertFalse(self.executou())
        self.vermelho_cru("commit", "-q", "--allow-empty", "-m", "cru")

    def test_core_fsmonitor(self):
        self.config("core.fsmonitor", str(self.x))
        for args in (("status", "--porcelain"), ("ls-files", "-z"), ("diff-tree", "-r", "HEAD~1", "HEAD")):
            self.vermelho_cru(*args)
            self.verde(*args)
        with self.assertRaisesRegex(forge_git.Recusado, "fora da lista positiva"):
            forge_git.git(self.copia, "status")

    def test_uploadpack_com_origin_local(self):
        self.config("remote.origin.uploadpack", str(self.x))
        self.vermelho_cru("ls-remote", "origin")
        self.verde("ls-remote", "origin")
        self.verde("fetch", "origin")
        with self.assertRaisesRegex(forge_git.Recusado, "https"):
            forge_git.rede(str(self.origem), "ls-remote")
        self.assertFalse(self.executou())

    def test_insteadof_e_chave_por_protocolo(self):
        """`protocol.ext.allow=always` vence `protocol.allow=never`: só a chave por nome fecha o ext."""
        global_ = Path(self.env["HOME"]) / ".gitconfig"
        global_.write_text(global_.read_text(encoding="utf-8") + f'[protocol "ext"]\n\tallow = always\n'
                           f'[url "ext::sh -c {self.x}% #"]\n\tinsteadOf = https://exemplo.invalid/\n',
                           encoding="utf-8")
        self.vermelho_cru("ls-remote", "https://exemplo.invalid/a")
        self.vermelho_cru("-c", "protocol.allow=never", "ls-remote", "https://exemplo.invalid/a")
        rc, _ = forge_git.rede("https://exemplo.invalid/a", "ls-remote")
        self.assertNotEqual(rc, 0)
        self.assertFalse(self.executou())

    def test_credential_helper(self):
        """Sem servidor 401 no sandbox: o helper executa cru pelo `credential fill`; no forge_git, nenhum caminho."""
        self.config("credential.helper", f"!{self.x}")
        subprocess.run(["git", "credential", "fill"], cwd=self.copia, env=self.env, input="url=https://h/x\n\n",
                       capture_output=True, text=True, timeout=20)
        self.assertTrue(self.executou())
        for args in (("credential", "fill"), ("status",), ("ls-remote", "origin")):
            self.verde(*args)

    def test_core_sshcommand(self):
        self.config("core.sshCommand", str(self.x))
        self.config("remote.s.url", "ssh://h/r")
        self.vermelho_cru("ls-remote", "s")
        self.verde("ls-remote", "s")
        self.verde("status")
        with self.assertRaisesRegex(forge_git.Recusado, "https"):
            forge_git.rede("ssh://h/r", "ls-remote")

    def test_driver_por_info_attributes(self):
        (self.copia / ".git" / "info" / "attributes").write_text("* filter=y diff=y merge=y\n", encoding="utf-8")
        for chave in ("filter.y.clean", "diff.y.textconv", "merge.y.driver"):
            self.config(chave, str(self.x))
        for args in (("status", "--porcelain"), ("show", "HEAD"), ("hash-object", "f"), ("diff", "HEAD~1", "HEAD"),
                     ("diff",)):
            self.vermelho_cru(*args)
            self.verde(*args)
        self.vermelho_cru("merge-tree", "--write-tree", "main", "lado")
        rc, _ = forge_git.merge_tree(self.copia, "--write-tree", "main", "lado")
        self.assertEqual(rc, 1)  # conflito em f, resolvido sem o driver da cópia
        self.assertFalse(self.executou())

    def test_diff_external_e_assinatura(self):
        self.config("diff.external", str(self.x))
        self.vermelho_cru("diff", "HEAD~1", "HEAD")
        self.verde("show", "HEAD")
        self.verde("diff", "HEAD~1", "HEAD")
        falso = self.tmp / "assina"
        falso.write_text('#!/bin/sh\necho "[GNUPG:] SIG_CREATED " >&2\necho "-----BEGIN PGP SIGNATURE-----"\n'
                         'echo x\necho "-----END PGP SIGNATURE-----"\n', encoding="utf-8")
        falso.chmod(0o755)
        self.cru("-c", f"gpg.program={falso}", "commit", "-q", "--allow-empty", "-S", "-m", "s")
        self.config("log.showSignature", "true")
        self.config("gpg.program", str(self.x))
        self.vermelho_cru("log", "-1", "--format=%H")
        self.verde("log", "-1", "--format=%H")


class Recusas(Base):
    def test_subcomando_fora_da_lista_e_opcao_global(self):
        for args in (("push", "origin"), ("fetch", "origin"), ("-c", "core.fsmonitor=x", "status"), ()):
            with self.assertRaisesRegex(forge_git.Recusado, "fora da lista positiva"):
                forge_git.git(self.copia, *args)

    def test_subcomando_misto_so_na_leitura(self):
        for args in (("config", "core.x", "1"), ("branch", "-D", "lado"), ("remote", "add", "o", "x"),
                     ("worktree", "add", "w")):
            with self.assertRaisesRegex(forge_git.Recusado, "só a leitura"):
                forge_git.git(self.copia, *args)
        self.assertEqual(forge_git.git(self.copia, "branch", "--show-current"), (0, "main"))

    def test_opcao_que_reabre_programa(self):
        for args in (("show", "--textconv", "HEAD"), ("log", "--show-signature"), ("hash-object", "--path=f", "f"),
                     ("grep", "-O/bin/true", "-e", "a", "HEAD")):
            with self.assertRaisesRegex(forge_git.Recusado, "reabre"):
                forge_git.git(self.copia, *args)

    def test_pasta_que_nao_e_repositorio(self):
        with self.assertRaisesRegex(forge_git.Recusado, "não é repositório"):
            forge_git.git(self.tmp / "home", "status")

    def test_config_com_chave_fora_da_lista_recusa_e_uma_so_basta(self):
        self.config("core.hooksPath", ".githooks")
        self.config("core.editor", "vi")
        with self.assertRaisesRegex(forge_git.Recusado, "fora da lista positiva"):
            forge_git.git(self.copia, "status")

    def test_config_que_o_git_nao_le_recusa(self):
        """A config sumiu entre o rev-parse e a leitura (a janela de corrida): ler falha e a chamada recusa."""
        with mock.patch.object(forge_git, "_pasta_git", return_value=self.tmp / "sumiu"):
            self.assertFalse(forge_git.config_permitida(self.copia))
            with self.assertRaisesRegex(forge_git.Recusado, "fora da lista positiva"):
                forge_git.git(self.copia, "ls-files")

    def test_rede_so_ls_remote_e_fetch(self):
        with self.assertRaisesRegex(forge_git.Recusado, "ls-remote e fetch"):
            forge_git.rede("https://exemplo.invalid/a", "push")

    def test_merge_tree_com_revisao_que_nao_existe(self):
        self.assertEqual(forge_git.merge_tree(self.copia, "--write-tree", "main", "nao-existe"), (1, ""))


class Legitimos(Base):
    """A cópia como as de `wt/`: `core.hooksPath=.githooks` e `remote.origin.tagopt`; tudo passa."""

    def test_copia_limpa_passa_em_todos(self):
        self.config("core.hooksPath", ".githooks")
        self.config("remote.origin.tagopt", "--no-tags")
        g = forge_git.git
        self.assertEqual(g(self.copia, "status", "--porcelain")[0], 0)
        self.assertEqual(g(self.copia, "ls-files"), (0, "f"))
        self.assertEqual(g(self.copia, "show", "HEAD:f"), (0, "c"))
        self.assertEqual(g(self.copia, "config", "--get", "remote.origin.tagopt"), (0, "--no-tags"))
        self.assertIn("+c", g(self.copia, "diff", "HEAD~1", "HEAD")[1])
        self.assertEqual(g(self.copia, "hash-object", "-t", "tree", "/dev/null")[1],
                         "4b825dc642cb6eb9a060e54bf8d69288fbee4904")
        self.assertEqual(g(self.copia, "rev-parse", "--verify", "lado")[0], 0)
        self.assertEqual(g(self.copia, "cat-file", "--batch-check", entrada="HEAD\n")[0], 0)
        (self.copia / "g").write_text("g\n", encoding="utf-8")
        self.assertEqual(g(self.copia, "add", "g")[0], 0)
        self.assertEqual(g(self.copia, "commit", "-qm", "g")[0], 0)
        self.cru("switch", "-q", "-c", "lado2", "main~1")
        (self.copia / "h").write_text("h\n", encoding="utf-8")
        self.cru("add", "h")
        self.cru("commit", "-qm", "h")
        rc, arvore = forge_git.merge_tree(self.copia, "--write-tree", "main", "lado2")
        self.assertEqual((rc, len(arvore)), (0, 40))
        self.assertEqual(g(self.copia, "cat-file", "-t", arvore), (128, ""))  # a árvore do merge ficou no neutro

    def test_pasta_neutra_fora_do_tmpdir_do_agente(self):
        self.assertEqual(NEUTRA_REAL.parts[-3:], (".forge", "maquina", "neutro"))
        self.assertFalse(str(NEUTRA_REAL).startswith(tempfile.gettempdir()))


if __name__ == "__main__":
    unittest.main()
