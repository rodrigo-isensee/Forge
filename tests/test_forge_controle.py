"""AE3.1 (v0478 E108.1): `salvar` de bin/forge_controle.py, o commit local da pasta de controle. Cada teste monta um
repositório temporário com HOME próprio (identidade do git sem o config de quem roda a suíte) e um remoto bare. Um teste por
guarda, com o ramo de falha: caminho fora da lista, link, segredo, arquivo grande ou não comum, hook ativo, trava, pasta que
não é a raiz e `GIT_DIR` herdado; e os ramos de sucesso: só a lista entra, mensagem fixa, nada muda sem mudança, nunca push."""
import fcntl
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_git_herdado  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "bin"))
import forge_controle as C  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        casa = self.tmp / "casa"
        casa.mkdir()
        (casa / ".gitconfig").write_text("[user]\n\tname = t\n\temail = t@t\n[init]\n\tdefaultBranch = principal\n")
        limpo = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        ambiente = mock.patch.dict(os.environ, limpo | {"HOME": str(casa), "XDG_CONFIG_HOME": str(casa)}, clear=True)
        ambiente.start()
        self.addCleanup(ambiente.stop)
        self.env = sem_git_herdado(GIT_CONFIG_NOSYSTEM="1")
        self.pasta = self.tmp / "controle"
        self.git("init", "-q", str(self.pasta), cwd=self.tmp)
        self.escrever("KANBAN.md", "quadro\n")
        self.escrever("docs/pedido.md", "pedido\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "inicio")
        self.remoto = self.tmp / "remoto.git"
        self.git("init", "-q", "--bare", str(self.remoto), cwd=self.tmp)
        remoto_sem_manutencao(self.remoto)
        self.git("remote", "add", "origin", str(self.remoto))
        self.git("push", "-q", "origin", "principal")
        self.inicio = self.head()

    def git(self, *args, cwd=None):
        r = subprocess.run(["git", *args], cwd=cwd or self.pasta, env=self.env, capture_output=True, text=True,
                           timeout=60, check=True)
        return r.stdout.strip()

    def escrever(self, nome, texto):
        arq = self.pasta / nome
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto)
        return arq

    def head(self):
        return self.git("rev-parse", "HEAD")

    def arquivos_do_ultimo(self):
        return sorted(self.git("show", "--name-only", "--format=", "HEAD").splitlines())

    def assert_sem_commit(self, resultado, estado):
        self.assertEqual(resultado[0], estado, resultado)
        self.assertEqual(self.head(), self.inicio)


class Salvar(Base):
    def test_so_os_caminhos_da_lista_entram_com_a_mensagem_fixa(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        self.escrever("docs/briefs/b.md", "brief\n")
        self.escrever("solto.log", "log\n")
        self.escrever("preparado.txt", "fora\n")
        self.git("add", "preparado.txt")
        estado, sha = C.salvar(self.pasta)
        self.assertEqual(estado, "salvo")
        self.assertEqual(sha, self.head())
        self.assertEqual(self.arquivos_do_ultimo(), ["KANBAN.md", "docs/briefs/b.md"])
        self.assertEqual(self.git("log", "-1", "--format=%s"), C.MENSAGEM)
        self.assertIn("preparado.txt", self.git("diff", "--cached", "--name-only"))

    def test_arquivo_apagado_entra_como_remocao(self):
        (self.pasta / "docs/pedido.md").unlink()
        self.assertEqual(C.salvar(self.pasta)[0], "salvo")
        self.assertEqual(self.git("ls-files", "docs"), "")

    def test_sem_mudanca_nao_faz_commit(self):
        self.escrever("solto.log", "log\n")
        self.assert_sem_commit(C.salvar(self.pasta), "nada")

    def test_nunca_faz_push(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        self.assertEqual(C.salvar(self.pasta)[0], "salvo")
        self.assertEqual(self.git("rev-parse", "principal", cwd=self.remoto), self.inicio)

    def test_git_dir_herdado_nao_desvia_o_commit(self):
        outro = self.tmp / "outro"
        self.git("init", "-q", str(outro), cwd=self.tmp)
        self.escrever("KANBAN.md", "quadro novo\n")
        with mock.patch.dict(os.environ, {"GIT_DIR": str(outro / ".git")}):
            self.assertEqual(C.salvar(self.pasta)[0], "salvo")
        self.assertNotEqual(self.head(), self.inicio)


class Recusas(Base):
    def test_link_para_fora_e_recusado_sem_commit_parcial(self):
        fora = self.tmp / "segredo.txt"
        fora.write_text("fora\n")
        self.escrever("KANBAN.md", "quadro novo\n")
        (self.pasta / "docs/link.md").symlink_to(fora)
        resultado = C.salvar(self.pasta)
        self.assert_sem_commit(resultado, "recusado")
        self.assertTrue(resultado[1].startswith("link: "), resultado)

    def test_pasta_que_e_link_e_recusada(self):
        alvo = self.tmp / "alvo"
        alvo.mkdir()
        (alvo / "a.md").write_text("a\n")
        (self.pasta / "docs/sub").symlink_to(alvo)
        resultado = C.salvar(self.pasta)
        self.assert_sem_commit(resultado, "recusado")
        self.assertTrue(resultado[1].startswith("link: "), resultado)

    def test_nome_de_segredo_e_recusado(self):
        self.escrever("docs/.env", "CHAVE=1\n")
        self.assert_sem_commit(C.salvar(self.pasta), "recusado")

    def test_arquivo_acima_do_teto_e_recusado(self):
        self.escrever("docs/grande.md", "x" * (C.TETO_DE_BYTES + 1))
        self.assert_sem_commit(C.salvar(self.pasta), "recusado")

    def test_arquivo_no_teto_entra(self):
        self.escrever("docs/grande.md", "x" * C.TETO_DE_BYTES)
        self.assertEqual(C.salvar(self.pasta)[0], "salvo")

    def test_repositorio_aninhado_nao_e_arquivo_comum(self):
        self.git("init", "-q", str(self.pasta / "docs/sub"), cwd=self.tmp)
        self.assert_sem_commit(C.salvar(self.pasta), "recusado")

    def test_caminho_fora_da_lista_e_recusado(self):
        self.assertEqual(C._recusa(self.pasta, "docsx/a.md"), "fora da lista")
        self.assertEqual(C._recusa(self.pasta, "KANBAN.md.bak"), "fora da lista")
        self.assertIsNone(C._recusa(self.pasta, "KANBAN.md"))


class Ambiente(Base):
    def test_hook_ativo_e_nao_verificavel_e_nao_roda(self):
        marca = self.tmp / "rodou"
        hook = self.pasta / ".git/hooks/pre-commit"
        hook.write_text(f"#!/bin/sh\ntouch '{marca}'\n")
        hook.chmod(0o755)
        self.escrever("KANBAN.md", "quadro novo\n")
        self.assert_sem_commit(C.salvar(self.pasta), "nao-verificavel")
        self.assertFalse(marca.exists())

    def test_hook_de_exemplo_nao_conta(self):
        hook = self.pasta / ".git/hooks/pre-commit.sample"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.escrever("KANBAN.md", "quadro novo\n")
        self.assertEqual(C.salvar(self.pasta)[0], "salvo")

    def test_sem_pasta_de_hooks_salva(self):
        shutil.rmtree(self.pasta / ".git/hooks", ignore_errors=True)
        self.escrever("KANBAN.md", "quadro novo\n")
        self.assertEqual(C.salvar(self.pasta)[0], "salvo")

    def test_hooks_path_configurado_e_nao_verificavel_e_fica_como_estava(self):
        self.git("config", "core.hooksPath", "ganchos")
        self.escrever("KANBAN.md", "quadro novo\n")
        self.assert_sem_commit(C.salvar(self.pasta), "nao-verificavel")
        self.assertEqual(self.git("config", "--get", "core.hooksPath"), "ganchos")

    def test_subpasta_nao_e_a_raiz(self):
        self.escrever("docs/novo.md", "n\n")
        self.assert_sem_commit(C.salvar(self.pasta / "docs"), "nao-verificavel")

    def test_segundo_salvar_ao_mesmo_tempo_sai_ocupado(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        trava = self.git("rev-parse", "--path-format=absolute", "--git-path", "forge-controle.lock")
        with open(trava, "a", encoding="utf-8") as arquivo:
            fcntl.flock(arquivo, fcntl.LOCK_EX)
            self.assert_sem_commit(C.salvar(self.pasta), "ocupado")
        self.assertEqual(C.salvar(self.pasta)[0], "salvo")


class Falhas(Base):
    """Ramo de falha de cada chamada do git: o git que falha num passo não deixa commit."""

    def falhar_em(self, marca):
        real = C._git

        def falso(pasta, *args):
            return (1, "falhou") if marca in args else real(pasta, *args)
        return mock.patch.object(C, "_git", falso)

    def test_falha_do_git_traz_a_mensagem_de_erro(self):
        cod, saida = C._git(self.pasta, "cat-file", "-e", "nao-existe")
        self.assertNotEqual(cod, 0)
        self.assertIn("nao-existe", saida)

    def test_git_ausente_e_nao_verificavel(self):
        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "vazio")}):
            self.assertEqual(C.salvar(self.pasta)[0], "nao-verificavel")

    def test_pasta_de_hooks_ilegivel_e_nao_verificavel(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        with self.falhar_em("hooks"):
            self.assert_sem_commit(C.salvar(self.pasta), "nao-verificavel")

    def test_trava_ilegivel_e_nao_verificavel(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        with self.falhar_em("forge-controle.lock"):
            self.assert_sem_commit(C.salvar(self.pasta), "nao-verificavel")

    def test_status_que_falha_e_erro(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        with self.falhar_em("status"):
            self.assert_sem_commit(C.salvar(self.pasta), "erro")

    def test_add_que_falha_e_erro(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        with self.falhar_em("add"):
            self.assert_sem_commit(C.salvar(self.pasta), "erro")

    def test_commit_que_falha_e_erro(self):
        self.escrever("KANBAN.md", "quadro novo\n")
        with self.falhar_em("commit"):
            self.assert_sem_commit(C.salvar(self.pasta), "erro")


if __name__ == "__main__":
    unittest.main()
