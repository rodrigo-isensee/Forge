"""INCIDENTE-HOOK-PARECER-CONTORNADO (0.47.8 E3.1): as fixtures `incidente-r-*` do hook `parecer` (tests/hooks/parecer/).

`gh pr ready`, `gh pr merge` e `gh pr create` fora de um repositório git, com `-R`/`--repo`, `GH_REPO=` ou a URL do PR,
passavam sem conferência (o hook só achava raiz pela pasta). Agora o hook confere no clone da sessão
(`CLAUDE_PROJECT_DIR`) que tem remoto desse repositório e recusa quando não o acha (falha fechada).
Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


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
        self.rodar("incidente-r-*.json", 11)


if __name__ == "__main__":
    unittest.main()
