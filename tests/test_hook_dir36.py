"""E3.39 (v0474, diretriz 36, R-CONTRIB): projeto nunca mexe no Forge, só sugere. As fixtures `dir36-*` (branch, commit,
worktree e PR no Forge vindos de sessão de projeto; o próprio projeto e a sessão do Forge seguem livres) e as `contrib-*`
do hook `conformidade`, sem as outras. Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de
`tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class HookDir36(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def rodar_prefixo(self, prefixo, piso):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "conformidade").glob(f"{prefixo}-*.json"))], piso,
                          f"{prefixo}-*")
        lados = {f.dados["esperado"]["codigo"] for f in fixtures}
        self.assertEqual(lados, {0, 2}, "o corpus tem os dois lados: o que passa e o que barra")
        casos = [(f"conformidade/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_fixtures_dir36(self):
        self.rodar_prefixo("dir36", 18)

    def test_fixtures_contrib(self):
        self.rodar_prefixo("contrib", 140)


if __name__ == "__main__":
    unittest.main()
