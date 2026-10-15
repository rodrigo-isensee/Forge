"""Portão de pareceres (bin/forge-check, ADR 0004 item 3): o merge da base não desatualiza o parecer sem mudança
real da branch, mas qualquer linha adicionada ou removida pela branch, inclusive na resolução de um merge, sim."""
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

    def base_avanca(self, mexe_no_trecho=False):
        """A develop avança: linhas novas no topo de src.txt (desloca tudo) e entrada própria no changelog."""
        self.git("switch", "-q", "develop")
        corpo = CORPO.replace("linha 14\n", "linha 14 da base\n") if mexe_no_trecho else CORPO
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


if __name__ == "__main__":
    unittest.main()
