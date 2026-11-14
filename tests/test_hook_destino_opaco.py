"""A9 (E1.139, v047, CONFORMIDADE-A9-DESTINO-OPACO): as fixtures `opaco-semresto-*` do hook `conformidade`, sem as
outras: destino opaco sem resto (`cp config "$(echo .git)"`) recusa quando o texto que produz o valor cita o diretório do
git (U1), quando o hook não o lê (U2) e com origem de nome do git fora da lista positiva (U3); os legítimos seguem livres.
A10 (CONFORMIDADE-A10-OPERADOR-COLADO): as `opaco-colado-*`, operador colado no corpo do rev-parse e a liberação de link
do #512 só com corpo de um comando. Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de
`tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class HookDestinoOpaco(unittest.TestCase):
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

    def test_fixtures_opaco_sem_resto(self):
        self.rodar_prefixo("opaco-semresto", 59)

    def test_fixtures_opaco_colado(self):
        self.rodar_prefixo("opaco-colado", 15)

    def test_fixtures_opaco_d2b(self):  # E1.175: aspas e variável colada no corpo, `function f {` sem `()`
        self.rodar_prefixo("opaco-d2b", 11)


if __name__ == "__main__":
    unittest.main()
