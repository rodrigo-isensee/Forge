"""FILA-27 (0.45.7 E10.1): as fixtures `fila27-*` do hook `parecer` (tests/hooks/parecer/), sem as outras fixtures dos hooks.

A1: no clone do Forge, o manifesto vence o `hooks_desligados` mesmo com `.forge/versao` (`Hook.projeto`).
A2: no clone do Forge, a mutação GraphQL `markPullRequestReadyForReview` conta como `gh pr ready` (`pronto_por_graphql`).
Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class Fila27(unittest.TestCase):
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

    def test_a1_manifesto_vence_hooks_desligados_no_clone(self):
        self.rodar("fila27-a1-*.json", 3)

    def test_a1_hook_projeto_so_o_hook_do_clone_ignora_o_desligado(self):
        """`Hook.projeto` direto: com manifesto, `.forge/versao` e o hook desligado, só `clone_do_forge` devolve a raiz;
        sem manifesto, o desligado vale para os dois; fora de cópia de trabalho, None sem ler a config."""
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
        import _comum
        tmp = Path(self._pasta_temporaria())
        for manifesto in (True, False):
            raiz = tmp / f"proj-{manifesto}"
            (raiz / ".git").mkdir(parents=True)
            (raiz / ".forge").mkdir()
            (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
            (raiz / ".forge" / "config.json").write_text('{"hooks_desligados": ["parecer"]}', encoding="utf-8")
            if manifesto:
                (raiz / ".claude-plugin").mkdir()
                (raiz / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}', encoding="utf-8")
            with self.subTest(manifesto=manifesto):
                self.assertIsNone(_comum.Hook("parecer").projeto(raiz))
                self.assertEqual(_comum.Hook("parecer").projeto(raiz, clone_do_forge=True), raiz if manifesto else None)
                self.assertEqual(_comum.Hook("outro").projeto(raiz), raiz)
        (tmp / "solta").mkdir()
        try:
            achada = _comum.Hook("parecer").projeto(tmp / "solta")
        except Exception as erro:  # noqa: BLE001 - ler a config sem raiz é o defeito que o teste prova
            self.fail(f"fora de cópia de trabalho, Hook.projeto leu a config: {erro!r}")
        self.assertIsNone(achada)

    def test_a2_ready_por_graphql_no_clone(self):
        self.rodar("fila27-a2-*.json", 19)

    def test_a2_fifo_em_arroba_arq_recusa_sem_esperar(self):
        """A-F27-1: `-F query=@q` com `q` FIFO sem escritor recusa sem abrir para leitura bloqueante; aberto assim, o
        hook esperaria até o timeout do Claude Code (10 s), que libera a ação. O prazo de 9 s do teste é esse teto."""
        f = Fixture(FIXTURES / "parecer" / "fila27-a2-graphql-fifo-bloqueia.json")
        raiz, entrada = f.montar(Path(self._pasta_temporaria()), None)
        os.mkfifo(raiz / "q.graphql")
        r = test_hooks.rodar("parecer", entrada, raiz, prazo=test_hooks.PRAZO_DO_CLAUDE_CODE_S - 1)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("tirar o rascunho pela API", r.stderr)


if __name__ == "__main__":
    unittest.main()
