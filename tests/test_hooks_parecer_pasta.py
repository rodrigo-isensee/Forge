"""HK3-PARECER, PR A (E1 e E3): o corpus `pasta-*` do hook `parecer` (tests/hooks/parecer/), sem as outras fixtures dos hooks.

A pasta em que o git roda é a que o bash e o git calculam (`cd` no nível de cima da linha, `-C` repetido e relativo ao
anterior, `~`), só com caminho literal; o que o hook não resolve (variável, crase, `$( )`, `cd` em subshell, pipeline,
segundo plano ou condicional) recusa o merge e o pull, seja qual for a branch da sessão. As
fixtures marcam com `passa-` o que o hook deixa passar e com `barra-` o que ele recusa (docs/security/hk3-parecer-ameacas.md,
linhas P e B). Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class PastaDoGit(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_corpus_pasta_passa_e_barra(self):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob("pasta-*.json"))], 50, "fixtures pasta-*")
        passam = [f for f in fixtures if f.dados["esperado"]["codigo"] == 0]
        self.assertTrue(10 <= len(passam) < len(fixtures), "o corpus tem os dois lados: o que passa e o que barra")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_corpus_texto_passa_e_barra(self):
        """HK3-PARECER, PR B (E2): a palavra crítica só no texto (heredoc lido, argumento de leitor, merge-base, sh -c que só
        lê ou espera) passa; executar merge, pull ou gh pr em heredoc, sh -c ou eval segue barrado (`texto-*`)."""
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob("texto-*.json"))], 30, "fixtures texto-*")
        passam = [f for f in fixtures if f.dados["esperado"]["codigo"] == 0]
        self.assertTrue(10 <= len(passam) < len(fixtures), "o corpus tem os dois lados: o que passa e o que barra")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_corpus_atualiza_passa_e_barra(self):
        """PARECER-BARRA-FETCH: na branch de trabalho com parecer reprovado, o autor da volta se atualiza (fetch, merge
        --ff-only, pull --ff-only); na develop, a mesma branch reprovada segue barrada (`atualiza-*`)."""
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob("atualiza-*.json"))], 5, "atualiza-*")
        lados = {(f.caminho.stem.split("-")[1], f.dados["esperado"]["codigo"]) for f in fixtures}
        self.assertEqual(lados, {("passa", 0), ("barra", 2)}, "os dois lados, e o nome diz o esperado")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_corpus_heredoc_interpretador_libera_e_bloqueia(self):
        """HOOK-CONTRIB-HEREDOC-FP e HOOK-REVIEW-HEREDOC-TIMEOUT: o corpo de heredoc que só o Python lê, sem comando de PR
        lançado, não é comando nem marca a chamada, e o que o sh roda passa sozinho pela gramática; o gh pr, o merge e o
        pull executados seguem recusados (`heredoc-interpretador-*`)."""
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob("heredoc-interpretador-*.json"))], 35,
                          "heredoc-interpretador-*")
        lados = {(f.caminho.stem.rsplit("-", 1)[1], f.dados["esperado"]["codigo"]) for f in fixtures}
        self.assertEqual(lados, {("libera", 0), ("bloqueia", 2)}, "os dois lados, e o nome diz o esperado")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")


if __name__ == "__main__":
    unittest.main()
