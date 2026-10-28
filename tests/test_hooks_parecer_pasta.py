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


if __name__ == "__main__":
    unittest.main()
