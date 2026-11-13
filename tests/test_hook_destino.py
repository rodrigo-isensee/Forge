"""mp1311 item 2 (destino real da escrita): o `conformidade` recusa pelo destino, não pelo texto que só cita um caminho
protegido. Os casos são os fixtures `destino-*` de tests/hooks/conformidade/: os `-libera` falham na base (falso positivo)
e os `-bloqueia` provam que a escrita real segue recusada; os `destino-aceita-*` são as formas do relato que já liberavam na
base (heredoc com apóstrofo, commit com heredoc e push, mutante com sed, laço da esperar-estado) e travam a regressão."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture, modulos_dos_hooks  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class HookDestino(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def lote(self, padrao, minimo_de_casos):
        fixtures = minimo([Fixture(p) for p in sorted(FIXTURES.glob(f"conformidade/{padrao}"))], minimo_de_casos, padrao)
        casos = [(f"{f.hook}/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(casos), "todo caso é verificado")

    def test_tmpdir_do_ambiente_no_marcador_so_de_caminho(self):
        """Texto que cita CLAUDE.md, .forge/versao ou docs/qa, com o destino no $TMPDIR do ambiente."""
        self.lote("destino-*tmpdir*.json", 7)

    def test_tmpdir_como_caminho(self):
        """As formas trocadas e as que voltam iguais (ação crítica, atribuição, $TMPDIR sem barra)."""
        _, conformidade, _ = modulos_dos_hooks()
        trocar = conformidade.tmpdir_como_caminho
        self.assertEqual(trocar('cat > "$TMPDIR/b" <<x'), 'cat > /tmp/b <<x')
        self.assertEqual(trocar('wc "$TMPDIR/a b"'), 'wc "/tmp/a b"')
        self.assertEqual(trocar("grep x > ${TMPDIR:-/tmp}/g ${TMPDIR}/h"), "grep x > /tmp/g /tmp/h")
        self.assertEqual(trocar('XDG_CACHE_HOME="$TMPDIR" gh pr checks 1'), "XDG_CACHE_HOME=/tmp gh pr checks 1")
        for igual in ('git push origin x > "$TMPDIR/l"', 'TMPDIR=.forge/; echo > "$TMPDIR/v"', 'cp a "$TMPDIR"',
                      'read TMPDIR; cat > "$TMPDIR/v"', '${TMPDIR:-.forge}/v'):
            with self.subTest(linha=igual):
                self.assertEqual(trocar(igual), igual)

    def test_prova_da_suite_pelo_destino(self):
        """CONFORMIDADE-PROVA-VARIAVEL-FP e o R-VERIFY de quem só lê: a volta ao texto da prova, com erro interno."""
        self.lote("destino-prova-*.json", 3)
        self.lote("destino-rverify-*.json", 4)

    def test_formas_do_relato_ja_aceitas(self):
        """Heredoc com apóstrofo, commit com heredoc e push na mesma chamada, mutante com sed e o laço da esperar-estado."""
        self.lote("destino-aceita-*.json", 4)


if __name__ == "__main__":
    unittest.main()
