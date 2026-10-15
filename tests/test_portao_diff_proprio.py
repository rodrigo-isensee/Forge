"""Portão de pareceres (bin/forge-check, ADR 0004 item 3): o merge da base não desatualiza o parecer sem mudança
real da branch, mas qualquer linha da branch a mais, a menos ou em outro lugar, inclusive na resolução de um merge,
sim (o HEAD tem de ser o patch do parecer aplicado sobre a base nova)."""
import os
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

AQUI = Path(__file__).resolve().parent
fc = SourceFileLoader("forge_check_portao", str(AQUI.parent / "bin" / "forge-check")).load_module()

CORPO = "".join(f"linha {i}\n" for i in range(1, 21))


class PortaoDiffProprio(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.git("init", "-q", "-b", "develop")
        self.escreve("src.txt", CORPO)
        self.escreve("CHANGELOG.md", "# Changelog\n\n## [Não publicado]\n\n## [1.0]\n")
        self.commit("base")
        self.git("switch", "-q", "-c", "ramo")

    def git(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        r = subprocess.run(["git", "-C", str(self.dir), "-c", "user.name=t", "-c", "user.email=t@t",
                            "-c", "commit.gpgsign=false", *args], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def escreve(self, nome, texto):
        (self.dir / nome).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / nome).write_text(texto)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def parecer_no_ramo(self):
        """A branch troca a linha 15 e ganha uma entrada no changelog; devolve o commit do parecer."""
        self.escreve("src.txt", CORPO.replace("linha 15\n", "linha 15 da branch\n"))
        self.escreve("CHANGELOG.md", "# Changelog\n\n## [Não publicado]\n- da branch\n\n## [1.0]\n")
        return self.commit("trabalho")

    def base_avanca(self, mexe_perto=False):
        """A develop avança: linhas novas no topo de src.txt (desloca tudo) e entrada própria no changelog; com
        `mexe_perto`, também altera a linha 12, a vizinha (a duas linhas) do trecho que a branch mexeu (a 15)."""
        self.git("switch", "-q", "develop")
        corpo = CORPO.replace("linha 13\n", "linha 13 da base\n") if mexe_perto else CORPO
        self.escreve("src.txt", "topo 1\ntopo 2\ntopo 3\n" + corpo)
        self.escreve("CHANGELOG.md", "# Changelog\n\n## [Não publicado]\n- da base\n\n## [1.0]\n")
        self.escreve("outro.txt", "novo\n")
        self.commit("base avança")
        self.git("switch", "-q", "ramo")

    CHANGELOG_DOS_DOIS = "# Changelog\n\n## [Não publicado]\n- da base\n- da branch\n\n## [1.0]\n"

    def vale(self, parecer, ate="HEAD"):
        return fc.commit_vale(self.dir, parecer, ate, "develop")

    def test_a_merge_da_base_que_desloca_linhas_nao_invalida(self):
        parecer = self.parecer_no_ramo()
        self.base_avanca()
        # conflito só no changelog: as duas entradas ficam
        r = subprocess.run(["git", "-C", str(self.dir), "-c", "user.name=t", "-c", "user.email=t@t",
                            "merge", "--no-edit", "develop"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.escreve("CHANGELOG.md", self.CHANGELOG_DOS_DOIS)
        self.commit("merge da base")
        self.assertIn("topo 1", (self.dir / "src.txt").read_text())
        self.assertIsNone(self.vale(parecer))

    def test_b_mudanca_de_conteudo_da_branch_cita_o_arquivo(self):
        parecer = self.parecer_no_ramo()
        self.base_avanca()
        self.git("merge", "-q", "--no-edit", "-X", "theirs", "develop")
        self.escreve("CHANGELOG.md", self.CHANGELOG_DOS_DOIS)
        self.escreve("src.txt", (self.dir / "src.txt").read_text().replace("linha 3\n", "linha 3 mudada\n"))
        self.commit("mudança depois do parecer")
        motivo = self.vale(parecer)
        self.assertIn("desatualizado: src.txt mudou", motivo)
        self.assertNotIn("outro.txt", motivo)

    def test_c_mudanca_so_na_resolucao_do_merge_invalida(self):
        parecer = self.parecer_no_ramo()
        self.base_avanca()
        self.git("merge", "--no-commit", "--no-edit", "-X", "theirs", "develop")
        self.escreve("CHANGELOG.md", self.CHANGELOG_DOS_DOIS)
        self.escreve("src.txt", (self.dir / "src.txt").read_text().replace("linha 3\n", "linha 3 maligna\n"))
        self.commit("merge com alteração escondida")
        self.assertIn("desatualizado: src.txt mudou", self.vale(parecer))

    def test_linha_removida_pela_branch_invalida(self):
        parecer = self.parecer_no_ramo()
        self.escreve("src.txt", (self.dir / "src.txt").read_text().replace("linha 3\n", ""))
        self.commit("remove")
        self.assertIn("desatualizado: src.txt", self.vale(parecer))

    def test_sem_base_continua_estrito(self):
        parecer = self.parecer_no_ramo()
        self.base_avanca()
        self.git("merge", "-q", "--no-edit", "-X", "theirs", "develop")
        self.assertIn("desatualizado:", fc.commit_vale(self.dir, parecer, "HEAD"))

    def test_mudanca_so_em_pareceres_vale(self):
        parecer = self.parecer_no_ramo()
        self.escreve("docs/reviews/x.md", "parecer\n")
        self.commit("parecer")
        self.assertIsNone(self.vale(parecer))

    def parecer_com_linha_repetida(self):
        """Base com `}` repetido; a branch insere `checa()` antes da chamada e recebe o parecer."""
        self.git("switch", "-q", "develop")
        self.escreve("f.txt", "def f():\n    x = 1\n    acao()\n    return x\n}\nfim\n}\n")
        self.commit("f na base")
        self.git("switch", "-q", "ramo")
        self.git("merge", "-q", "--no-edit", "develop")
        self.escreve("f.txt", "def f():\n    x = 1\n    checa()\n    acao()\n    return x\n}\nfim\n}\n")
        return self.commit("checa")

    def test_linha_movida_da_branch_invalida(self):
        parecer = self.parecer_com_linha_repetida()
        self.escreve("f.txt", "def f():\n    x = 1\n    acao()\n    checa()\n    return x\n}\nfim\n}\n")
        self.commit("move checa para depois de acao")
        self.assertIn("desatualizado: f.txt mudou", self.vale(parecer))

    def test_remover_copia_repetida_invalida(self):
        parecer = self.parecer_com_linha_repetida()
        self.escreve("f.txt", "def f():\n    x = 1\n    checa()\n    acao()\n    return x\n}\nfim\n")
        self.commit("tira o segundo }")
        self.assertIn("desatualizado: f.txt mudou", self.vale(parecer))

    def test_base_altera_a_linha_vizinha_sem_conflito_vale(self):
        parecer = self.parecer_no_ramo()
        self.base_avanca(mexe_perto=True)
        self.git("merge", "-q", "--no-edit", "-X", "theirs", "develop")
        self.escreve("CHANGELOG.md", self.CHANGELOG_DOS_DOIS)
        self.commit("changelog")
        texto = (self.dir / "src.txt").read_text()
        self.assertIn("linha 13 da base", texto)
        self.assertIn("linha 15 da branch", texto)
        self.assertIsNone(self.vale(parecer))

    def resolve_conflito_do_changelog(self, texto):
        parecer = self.parecer_no_ramo()
        self.base_avanca()
        self.git("merge", "--no-commit", "--no-edit", "-X", "theirs", "develop")
        self.escreve("CHANGELOG.md", texto)
        self.commit("merge")
        return self.vale(parecer)

    def test_conflito_no_changelog_resolvido_com_linha_a_mais_ou_a_menos_invalida(self):
        base = "# Changelog\n\n## [Não publicado]\n- da base\n"
        self.assertIn("desatualizado: CHANGELOG.md mudou",
                      self.resolve_conflito_do_changelog(base + "\n## [1.0]\n"))  # perdeu a entrada da branch

    def test_conflito_no_changelog_resolvido_com_linha_nova_invalida(self):
        self.assertIn("desatualizado: CHANGELOG.md mudou", self.resolve_conflito_do_changelog(
            self.CHANGELOG_DOS_DOIS.replace("- da branch\n", "- da branch\n- payload\n")))

    def test_conflito_no_changelog_com_a_entrada_em_outro_ponto_vale(self):
        """Caso real (teste-abertura-feita): a resolução pôs a entrada da branch antes da da base."""
        self.assertIsNone(self.resolve_conflito_do_changelog(
            "# Changelog\n\n## [Não publicado]\n- da branch\n- da base\n\n## [1.0]\n"))

    def test_conflito_em_arquivo_de_codigo_invalida_mesmo_com_as_mesmas_linhas(self):
        """Falha fechada: em conflito fora do CHANGELOG.md a posição não é conferida, então a linha movida passaria."""
        parecer = self.parecer_no_ramo()
        self.git("switch", "-q", "develop")
        self.escreve("src.txt", CORPO.replace("linha 15\n", "linha 15 da base\n"))
        self.commit("base mexe na mesma linha")
        self.git("switch", "-q", "ramo")
        self.git("merge", "--no-commit", "--no-edit", "-X", "ours", "develop")
        self.escreve("src.txt", CORPO.replace("linha 15\nlinha 16\n", "linha 16\nlinha 15 da branch\n"))
        self.commit("merge com a linha da branch uma posição abaixo")
        self.assertIn("desatualizado: src.txt mudou", self.vale(parecer))

    def test_conflito_so_no_changelog_com_as_mesmas_linhas_da_branch_vale(self):
        self.assertIsNone(self.resolve_conflito_do_changelog(self.CHANGELOG_DOS_DOIS))

    def esconde(self, separador):
        """Depois do parecer, uma linha da branch ganha `separador` + um falso cabeçalho git e um payload."""
        parecer = self.parecer_no_ramo()
        escondido = "linha 15 da branch" + separador + "index 0000..1111\n@@ -1 +1 @@\npayload"
        self.escreve("src.txt", CORPO.replace("linha 15\n", escondido + "\n"))
        self.commit("conteúdo escondido")
        return self.vale(parecer)

    def test_separadores_de_linha_do_python_nao_escondem_conteudo(self):
        for sep in ("\r", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"):
            with self.subTest(sep=repr(sep)):
                self.assertIn("desatualizado: src.txt mudou", self.esconde(sep))

    def test_caminho_com_b_barra_no_nome_sai_inteiro_na_mensagem(self):
        parecer = self.parecer_no_ramo()
        self.escreve("a b/c.txt", "novo\n")
        self.commit("arquivo com ' b/' no nome")
        self.assertIn("desatualizado: a b/c.txt mudou", self.vale(parecer))


if __name__ == "__main__":
    unittest.main()
