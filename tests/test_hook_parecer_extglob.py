"""HOOK-HEREDOC-EXTGLOB-E-CAIXA (v0478 E70.1): o alvo de redireção do heredoc de dado no hook `parecer` recusa o curinga
estendido (`bin/@(ls)`, `bin/+(ls)`, `bin/!(cat)`) e compara o nome com casefold (`bin/LS` num disco sem caixa).

Roda só as fixtures `heredoc-dado-alvo-extglob-*` e `heredoc-dado-alvo-caixa-*`, pela máquina do `tests/test_hooks.py`
(o hook roda como processo, com a entrada do Claude Code), para os mutantes de `tests/mutantes/` rodarem rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class AlvoDoHeredocDeDado(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def _rodar(self, padrao, minimo_de_fixtures):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob(padrao))], minimo_de_fixtures, padrao)
        self.assertEqual({f.dados["esperado"]["codigo"] for f in fixtures}, {2}, "todas recusam (ramo de falha)")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_curinga_estendido_no_alvo_recusa(self):
        """`@(`, `+(` e `!(` no alvo: com extglob o bash grava o nome de um programa da chamada; o corpo não é dado."""
        self._rodar("heredoc-dado-alvo-extglob-*.json", 3)

    def test_nome_do_alvo_sem_caixa_recusa(self):
        """`bin/LS` com `ls` na chamada: num disco sem caixa é o mesmo arquivo; o corpo não é dado."""
        self._rodar("heredoc-dado-alvo-caixa-*.json", 1)


if __name__ == "__main__":
    unittest.main()
