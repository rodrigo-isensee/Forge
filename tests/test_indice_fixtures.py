"""O índice das fixtures dos hooks (docs/hooks-fixtures.md) está em dia com o corpus de tests/hooks/ (Fase C)."""
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "indice-fixtures.py"


def carregar():
    spec = importlib.util.spec_from_file_location("indice_fixtures", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class IndiceDasFixtures(unittest.TestCase):
    def test_indice_esta_em_dia_com_o_corpus(self):
        indice = carregar()
        self.assertEqual((RAIZ / indice.INDICE).read_text(encoding="utf-8"), indice.gerar(),
                         "docs/hooks-fixtures.md desatualizado: rode scripts/indice-fixtures.py")

    def test_conta_todo_caso_do_corpus(self):
        texto = (RAIZ / "docs" / "hooks-fixtures.md").read_text(encoding="utf-8")
        total = len(list((RAIZ / "tests" / "hooks").glob("*/*.json")))
        self.assertIn(f"({total} fixtures)", texto)
        for pasta in sorted(p for p in (RAIZ / "tests" / "hooks").iterdir() if p.is_dir() and any(p.glob("*.json"))):
            with self.subTest(hook=pasta.name):
                self.assertIn(f"\n## `{pasta.name}`\n", texto)

    def test_grupos_contagens_regras_e_celula_segura(self):
        indice = carregar()
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            pasta = raiz / "tests" / "hooks" / "h"
            pasta.mkdir(parents=True)
            casos = {"ab-x-bloqueia": {"descricao": "CARTAO-1: a | b", "esperado": {"codigo": 2, "stderr": "R-MAIN: x; R-VERIFY"}},
                     "ab-y-libera": {"descricao": "livre", "esperado": {"codigo": 0}},
                     "cd-z": {"descricao": "z" * 200, "esperado": {"codigo": 2, "stderr": "sem regra"}}}
            for nome, dados in casos.items():
                (pasta / f"{nome}.json").write_text(json.dumps(dados), encoding="utf-8")
            texto = indice.gerar(raiz)
        self.assertIn("(3 fixtures)", texto)
        self.assertIn("| `h` | 3 | 2 | 1 | 2 |", texto)
        self.assertIn("| `ab-*` | 2 | 1 | 1 | `R-MAIN`, `R-VERIFY` | `CARTAO-1` | CARTAO-1: a \\| b |", texto)
        self.assertIn("| `cd-*` | 1 | 1 | 0 | — | — | " + "z" * 140 + "… |", texto)
        self.assertLess(texto.index("`ab-*`"), texto.index("`cd-*`"), "o grupo maior vem antes")

    def test_exemplo_sem_termo_de_stack(self):
        """ADR 0001: o índice é núcleo; o exemplo é a primeira descrição do grupo sem termo de stack do tests/config.json."""
        indice = carregar()
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "tests" / "hooks" / "h"
            pasta.mkdir(parents=True)
            casos = {"a-1": "usa pnpm exec", "a-2": "lançador no início", "b-1": "só pnpm", "c-1": "pnpm sem filtro"}
            for nome, descricao in casos.items():
                (pasta / f"{nome}.json").write_text(json.dumps({"descricao": descricao, "esperado": {"codigo": 2}}),
                                                    encoding="utf-8")
            filtrado = indice.gerar(Path(tmp), [re.compile(r"\bpnpm\b")])
            self.assertIn("| `a-*` | 2 | 2 | 0 | — | — | lançador no início |", filtrado)
            self.assertIn("| `b-*` | 1 | 1 | 0 | — | — | — |", filtrado)
            self.assertIn("| `c-*` | 1 | 1 | 0 | — | — | — |", filtrado)
            self.assertIn("| `c-*` | 1 | 1 | 0 | — | — | pnpm sem filtro |", indice.gerar(Path(tmp), []))
            self.assertIn("| `c-*` | 1 | 1 | 0 | — | — | — |", indice.gerar(Path(tmp)), "sem termos dados, os do config")

    def test_resumo_corta_a_lista(self):
        indice = carregar()
        self.assertEqual(indice.resumo({}), "—")
        self.assertEqual(indice.resumo({"b": 1, "a": 1, "c": 3, "d": 1, "e": 1}), "`c`, `a`, `b`, `d` e mais 1")

    def test_conferir_da_rc_0_em_dia(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--conferir"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("docs/hooks-fixtures.md: em dia", r.stdout)

    def test_main_grava_confere_e_recusa_opcao(self):
        indice = carregar()
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(indice, "RAIZ", Path(tmp)), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as saida, mock.patch("sys.stderr", new_callable=io.StringIO):
            (Path(tmp) / "docs").mkdir()
            pasta = Path(tmp) / "tests" / "hooks" / "h"
            pasta.mkdir(parents=True)
            (pasta / "a-b.json").write_text(json.dumps({"descricao": "x", "esperado": {"codigo": 0}}), encoding="utf-8")
            destino = Path(tmp) / indice.INDICE
            try:
                self.assertEqual(indice.main(["--conferir"]), 1, "sem o índice não está em dia")
            except OSError as erro:
                self.fail(f"--conferir sem o arquivo leu o que não existe: {erro}")
            self.assertFalse(destino.exists(), "--conferir não grava")
            self.assertEqual(indice.main(["--outra"]), 2)
            self.assertFalse(destino.exists(), "opção desconhecida não grava")
            self.assertEqual(indice.main([]), 0)
            self.assertEqual(destino.read_text(encoding="utf-8"), indice.gerar(Path(tmp)))
            self.assertEqual(indice.main(["--conferir"]), 0)
            destino.write_text("velho\n", encoding="utf-8")
            self.assertEqual(indice.main(["--conferir"]), 1)
        linhas = saida.getvalue().splitlines()
        self.assertEqual(linhas[0], "docs/hooks-fixtures.md: desatualizado; rode scripts/indice-fixtures.py")
        self.assertEqual(linhas[1:], ["docs/hooks-fixtures.md: gravado", "docs/hooks-fixtures.md: em dia",
                                      "docs/hooks-fixtures.md: desatualizado; rode scripts/indice-fixtures.py"])


if __name__ == "__main__":
    unittest.main()
