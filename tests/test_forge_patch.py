"""bin/forge-patch preparar (ARQUIVO-TRAVADO-APROVA-COM-COMANDO, C1): confere o patch e a cópia em modo seco, grava a
ficha com `x` e imprime o comando do dono; qualquer conferência que falha sai com 1 e não grava ficha.

A pasta pessoal e a cópia vigente se trocam no processo (`casa`, `vigente`), nunca pelo ambiente (seção 4 do desenho);
o teste da linha de comando roda em subprocesso com `python3 -I` e ambiente limpo."""
import hashlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "bin"))
import forge_patch
from ambiente_git import sem_manutencao

PEDIDO = "p-forge-patch-teste"
VIGENTE = forge_patch.vigente  # a função real, antes da troca do setUp


def diff(velho, novo, nome):
    """Diff unificado de um arquivo de texto, no formato do git."""
    linhas = [f"diff --git a/{nome} b/{nome}\n", f"--- a/{nome}\n", f"+++ b/{nome}\n", "@@ -1 +1 @@\n", f"-{velho}\n", f"+{novo}\n"]
    return "".join(linhas)


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home = Path(t.name).resolve() / "home"
        self.patches = self.home / ".forge-contrib" / "patches"
        self.patches.mkdir(parents=True)
        self.env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.home),
                                   "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "LC_ALL": "C"})
        for alvo, valor in (("casa", lambda: self.home), ("vigente", lambda: True)):
            p = mock.patch.object(forge_patch, alvo, valor)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.dict(os.environ, self.env, clear=True)
        p.start()
        self.addCleanup(p.stop)
        self.copia = self.repo(self.home / ".forge-contrib" / "wt" / "c1")

    def git(self, cwd, *a):
        return subprocess.run(["git", *a], cwd=cwd, env=self.env, capture_output=True, text=True, check=True)

    def repo(self, pasta, ramo="melhoria/x"):
        pasta.mkdir(parents=True)
        self.git(pasta, "init", "-q", "-b", ramo)
        for nome, texto in ((".githooks/pre-push", "velho\n"), (".githooks/outro", "velho\n"), ("README.md", "velho\n"),
                            ("docs/reviews/r.md", "velho\n"), (f"docs/pedidos/{PEDIDO}.md", "# pedido\n")):
            (pasta / nome).parent.mkdir(parents=True, exist_ok=True)
            (pasta / nome).write_text(texto)
        self.git(pasta, "add", "-A")
        self.git(pasta, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "i")
        return pasta

    def preparar(self, patch=None, ident="p1", arquivos=(".githooks/pre-push",), copia=None, motivo="trava nova", pedido=PEDIDO):
        if patch is not None:
            (self.patches / f"{ident}.patch").write_text(patch) if isinstance(patch, str) else None
        saida, erro = io.StringIO(), io.StringIO()
        argv = ["preparar", ident, "--copia", str(copia or self.copia), "--pedido", pedido, "--motivo", motivo, "--arquivos", *arquivos]
        with redirect_stdout(saida), redirect_stderr(erro):
            rc = forge_patch.main(argv)
        return rc, saida.getvalue(), erro.getvalue()

    def recusa(self, *a, contem="", **k):
        rc, saida, erro = self.preparar(*a, **k)
        self.assertEqual(rc, 1, saida + erro)
        self.assertIn(contem, erro)
        self.assertEqual(saida, "")
        self.assertEqual(sorted(p.name for p in self.patches.glob("*.ficha")), [], "recusa não grava ficha")
        return erro


class Grava(Base):
    def test_patch_protegido_grava_a_ficha_e_imprime_o_comando_com_o_sha256(self):
        patch = diff("velho", "novo", ".githooks/pre-push")
        rc, saida, erro = self.preparar(patch)
        self.assertEqual(rc, 0, erro)
        ficha = (self.patches / "p1.ficha").read_bytes()
        cabeca, corpo = ficha.split(b"\n\n", 1)
        self.assertEqual(corpo, patch.encode())
        head = self.git(self.copia, "rev-parse", "HEAD").stdout.strip()
        for linha in ("Id: p1", f"Pedido: {PEDIDO}", f"Copia: {self.copia}", "Ramo: melhoria/x", f"Head: {head}",
                      "Arquivos: .githooks/pre-push", "Motivo: trava nova"):
            self.assertIn(linha, cabeca.decode().splitlines())
        esperado = f"python3 -I {forge_patch.AQUI / 'forge-patch'} aplicar {self.patches / 'p1.ficha'} {hashlib.sha256(ficha).hexdigest()}"
        self.assertEqual(saida.strip(), esperado)
        self.assertEqual(self.git(self.copia, "status", "--porcelain").stdout, "", "o preparar não aplica nada")

    def test_ficha_existente_nao_e_sobrescrita(self):
        (self.patches / "p1.ficha").write_bytes(b"antiga")
        rc, saida, erro = self.preparar(diff("velho", "novo", ".githooks/pre-push"))
        self.assertEqual((rc, saida), (1, ""))
        self.assertIn("File exists", erro)
        self.assertEqual((self.patches / "p1.ficha").read_bytes(), b"antiga")


class Ficha(Base):
    def test_id_torto_recusa(self):
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), ident="P_1", contem="id fora")

    def test_patch_por_link_recusa(self):
        (self.patches / "alvo").write_text(diff("velho", "novo", ".githooks/pre-push"))
        (self.patches / "p1.patch").symlink_to(self.patches / "alvo")
        self.recusa(contem="link")

    def test_patch_acima_de_256_kib_recusa(self):
        self.recusa(diff("velho", "n" * (256 * 1024), ".githooks/pre-push"), contem="patch ausente, link ou acima")

    def test_ficha_inteira_acima_do_teto_recusa(self):
        corpo = diff("velho", "novo", ".githooks/pre-push")
        self.recusa(corpo + "\n" * (forge_patch.TETO_DA_FICHA - len(corpo)), contem="ficha acima")

    def test_motivo_vazio_ou_pedido_sem_arquivo_recusa(self):
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), motivo="  ", contem="motivo vazio")
        self.recusa(pedido="p-que-nao-existe-em-lugar-nenhum", contem="pedido sem")

    def test_fora_da_copia_vigente_nao_imprime_o_comando(self):
        with mock.patch.object(forge_patch, "vigente", lambda: False):
            self.recusa(diff("velho", "novo", ".githooks/pre-push"), contem="cópia vigente")

    def test_vigente_e_so_o_cache_de_plugins_ou_o_clone_do_jarvis_forge(self):
        with mock.patch.object(forge_patch, "vigente", VIGENTE):
            for pasta, esperado in ((self.home / ".claude" / "plugins" / "forge" / "bin", True),
                                    (self.home / ".local" / "share" / "forge" / "vigente" / "bin", True),
                                    (self.home / ".forge-contrib" / "wt" / "c1" / "bin", False)):
                with mock.patch.object(forge_patch, "AQUI", pasta):
                    self.assertIs(forge_patch.vigente(), esperado, pasta)


class Patch(Base):
    def test_arquivo_fora_da_lista_recusa(self):
        self.recusa(diff("velho", "novo", ".githooks/pre-push") + diff("velho", "novo", ".githooks/outro"), contem="exatamente")

    def test_arquivo_livre_recusa(self):
        self.recusa(diff("velho", "novo", "README.md"), arquivos=("README.md",), contem="arquivo livre")

    def test_parecer_e_pedido_nunca_vao_por_patch(self):
        self.recusa(diff("velho", "novo", "docs/reviews/r.md"), arquivos=("docs/reviews/r.md",), contem="nunca vai")
        self.recusa(diff("# pedido", "x", f"docs/pedidos/{PEDIDO}.md"), arquivos=(f"docs/pedidos/{PEDIDO}.md",), contem="nunca vai")

    def test_renomeacao_recusa(self):
        patch = "diff --git a/.githooks/outro b/.githooks/novo\nsimilarity index 100%\nrename from .githooks/outro\nrename to .githooks/novo\n"
        self.recusa(patch, arquivos=(".githooks/novo",), contem="renomeação")

    def test_mudanca_de_modo_recusa(self):
        self.recusa("diff --git a/.githooks/pre-push b/.githooks/pre-push\nold mode 100644\nnew mode 100755\n", contem="mudança de modo")
        patch = diff("velho", "novo", ".githooks/pre-push").replace("--- a/", "old mode 100644\nnew mode 100755\n--- a/", 1)
        self.recusa(patch, contem="mudança de modo")

    def test_link_simbolico_novo_recusa(self):
        patch = ("diff --git a/.githooks/lnk b/.githooks/lnk\nnew file mode 120000\n--- /dev/null\n+++ b/.githooks/lnk\n"
                 "@@ -0,0 +1 @@\n+pre-push\n\\ No newline at end of file\n")
        self.recusa(patch, arquivos=(".githooks/lnk",), contem="link")

    def test_binario_recusa(self):
        (self.copia / ".githooks" / "b").write_bytes(b"\0\1\2")  # o diff binário sai do próprio git, que o aplica
        self.git(self.copia, "add", ".githooks/b")
        patch = self.git(self.copia, "diff", "--cached", "--binary").stdout
        self.git(self.copia, "rm", "-q", "--cached", ".githooks/b")
        (self.copia / ".githooks" / "b").unlink()
        self.assertIn("GIT binary patch", patch)
        self.recusa(patch, arquivos=(".githooks/b",), contem="binário")

    def test_patch_que_nao_aplica_recusa(self):
        self.recusa(diff("outro texto", "novo", ".githooks/pre-push"), contem="não aplica")

    def test_arquivo_novo_protegido_passa(self):
        patch = "diff --git a/.githooks/novo b/.githooks/novo\nnew file mode 100755\n--- /dev/null\n+++ b/.githooks/novo\n@@ -0,0 +1 @@\n+x\n"
        rc, _, erro = self.preparar(patch, arquivos=(".githooks/novo",))
        self.assertEqual(rc, 0, erro)

    def test_caminho_travado_com_curinga_recusa(self):
        for nome in (".githooks/a*b", ".githooks/a[1]"):
            with self.subTest(nome=nome):
                patch = f"diff --git a/{nome} b/{nome}\nnew file mode 100644\n--- /dev/null\n+++ b/{nome}\n@@ -0,0 +1 @@\n+x\n"
                self.recusa(patch, arquivos=(nome,), contem="nunca vai")


class Copia(Base):
    def test_copia_fora_das_raizes_recusa(self):
        fora = self.repo(self.home / "fora")
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), copia=fora, contem="fora das raízes")

    def test_copia_por_link_recusa(self):
        link = self.home / ".forge-contrib" / "wt" / "link"
        link.symlink_to(self.copia)
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), copia=link, contem="por link")

    def test_subpasta_de_outro_repositorio_recusa(self):
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), copia=self.copia / "docs", contem="não é a raiz")

    def test_sessao_registrada_vira_raiz_e_a_torta_nao_derruba_as_outras(self):
        outra = self.repo(self.home / "projeto")
        maquina = self.home / ".forge" / "maquina"
        maquina.mkdir(parents=True)
        (maquina / "projetos-ativos.json").write_text('{"sessoes": {"t": {"pasta": 5}, "s": {"pasta": "%s"}}}' % outra)
        rc, _, erro = self.preparar(diff("velho", "novo", ".githooks/pre-push"), copia=outra)
        self.assertEqual(rc, 0, erro)

    def test_ramo_de_integracao_recusa(self):
        for ramo in ("develop", "main"):
            with self.subTest(ramo=ramo):
                self.git(self.copia, "switch", "-q", "-c", ramo)
                self.recusa(diff("velho", "novo", ".githooks/pre-push"), contem="ramo protegido")
                self.git(self.copia, "switch", "-q", "melhoria/x")
        self.git(self.copia, "switch", "-q", "--detach")
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), contem="HEAD solto: ''")

    def test_arvore_suja_recusa(self):
        (self.copia / "README.md").write_text("mudou\n")
        self.recusa(diff("velho", "novo", ".githooks/pre-push"), contem="árvore ou índice")


class LinhaDeComando(unittest.TestCase):
    def test_rodado_fora_da_copia_vigente_sai_1_sem_imprimir_comando(self):
        with tempfile.TemporaryDirectory() as t:
            env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": t, "LC_ALL": "C"})
            r = subprocess.run([sys.executable, "-I", str(AQUI.parent / "bin" / "forge-patch"), "preparar", "p1", "--copia", t,
                                "--pedido", PEDIDO, "--motivo", "m", "--arquivos", "a"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, "")
        self.assertIn("cópia vigente", r.stderr)


if __name__ == "__main__":
    unittest.main()
