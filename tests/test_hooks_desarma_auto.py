"""HOOK-DISABLE-AUTO (v048 E13.2): as fixtures `pr-merge-desarma-auto-*` do hook `parecer` (tests/hooks/parecer/).

O desarme do merge automático (`--disable-auto` no merge do `gh pr`) não mescla nada: o parecer o deixa passar sem
`forge-check pr` verde. A forma que o hook não lê como o gh (`=true` sozinha, valor de outra opção, `=false`,
`--admin`, `--auto`, grupo de opções curtas, depois de `--`) segue como merge. Roda a mesma máquina do
`tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class DesarmaAuto(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def rodar(self, padrao, total, codigo):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob(padrao))], total, padrao)
        self.assertEqual({f.dados["esperado"]["codigo"] for f in fixtures}, {codigo}, padrao)
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_desarme_passa_sem_parecer(self):
        self.rodar("pr-merge-desarma-auto-*-libera.json", 2, 0)

    def test_forma_duvidosa_segue_como_merge(self):
        self.rodar("pr-merge-desarma-auto-*-bloqueia.json", 7, 2)


if __name__ == "__main__":
    unittest.main()
