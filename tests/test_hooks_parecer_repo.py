"""0.47.8 E3.1: as fixtures `incidente-r-*` e `leitura-api-*` do hook `parecer` (tests/hooks/parecer/).

INCIDENTE-HOOK-PARECER-CONTORNADO: `gh pr ready`, `gh pr merge` e `gh pr create` fora de um repositório git, com
`-R`/`--repo`, `GH_REPO=` ou a URL do PR, passavam sem conferência (o hook só achava raiz pela pasta). Agora o hook confere
no clone da sessão (`CLAUDE_PROJECT_DIR`) que tem remoto desse repositório e recusa quando não o acha (falha fechada).
GH-API-LEITURA-UNICA: a leitura dos arquivos do `gh api` (`hooks/_gh_api.py`) lê o mesmo arquivo que o gh ou recusa:
`~` no começo do caminho, curinga e o `@` de `--input=@arq` (que é parte do nome).
Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
import _gh_api  # noqa: E402


class ParecerForaDoRepo(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def rodar(self, padrao, total):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob(padrao))], total, padrao)
        lados = {f.dados["esperado"]["codigo"] for f in fixtures}
        self.assertEqual(lados, {0, 2}, "o corpus tem os dois lados: o que passa e o que barra")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao(self):
        self.rodar("incidente-r-*.json", 38)

    def test_leitura_dos_arquivos_do_gh_api(self):
        self.rodar("leitura-api-*.json", 9)

    def test_graphql_fora_do_clone_e_arquivo_trocado_na_linha(self):
        """GRAPHQL-FORA-DO-CLONE e GH-API-ARQUIVO-TROCADO (A3 e A4 da E3.4): o graphql não usa a pasta, e a linha com
        outro comando pode trocar o arquivo da consulta depois da leitura do hook."""
        self.rodar("graphql-*.json", 6)


class LeituraDoGhApi(unittest.TestCase):
    """`textos_do_gh_api` direto: o arquivo lido é o que o gh lê."""

    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.pasta)
        for nome, texto in (("q", "consulta"), ("query=@q", "nome com =@")):
            with open(os.path.join(self.pasta, nome), "w", encoding="utf-8") as f:
                f.write(texto)

    def test_campo_longo_com_igual_le_o_arquivo_depois_do_arroba(self):
        """`--field=query=@q`: o gh lê `q`; antes, o hook procurava `query=@q` e recusava o que o gh aceita."""
        textos, legivel = _gh_api.textos_do_gh_api(["graphql", "--field=query=@q"], self.pasta)
        self.assertTrue(legivel)
        self.assertIn("consulta", textos)

    def test_pasta_desconhecida_com_relativo_e_ilegivel(self):
        self.assertFalse(_gh_api.textos_do_gh_api(["graphql", "-F", "query=@q"], None)[1])
        self.assertTrue(_gh_api.textos_do_gh_api(["graphql", "-F", "query=@q"], self.pasta)[1])


if __name__ == "__main__":
    unittest.main()
