"""E20.6 (pedido v046, A2 da segurança em docs/security/v046-pr-hook-prazo.md): escrita pelo Bash com `$(…)` ou variável
no caminho (`$(git rev-parse --git-common-dir)/forge/pr/a.json`, `d=<raiz>/.git; cp x $d/forge/…`) recusa quando o resto
cai num nome do diretório do git (.git/forge/, .git/config, .git/hooks/, .git/); os comandos de git comuns e as escritas
legítimas com `$(…)` ou variável seguem livres; na volta 1 (segurança E20.8), `git rev-parse --git-dir|--git-path` sem resto,
`${d%/}`, a crase sem aspas e `--target-directory=`; na volta 2 (E20.16), o corpo da substituição lido por palavras; na
volta 4 (E20.34), o curinga e as chaves na origem de link vinda de `git rev-parse`. As fixtures `gitcomum-*` do hook `conformidade`, sem as outras.
Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class HookGitComum(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_fixtures_gitcomum(self):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "conformidade").glob("gitcomum-*.json"))], 72,
                          "gitcomum-*")
        lados = {f.dados["esperado"]["codigo"] for f in fixtures}
        self.assertEqual(lados, {0, 2}, "o corpus tem os dois lados: o que passa e o que barra")
        casos = [(f"conformidade/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")


if __name__ == "__main__":
    unittest.main()
