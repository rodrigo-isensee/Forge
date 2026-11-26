"""O índice das fixtures dos hooks (docs/hooks-fixtures.md) está em dia com o corpus de tests/hooks/ (Fase C) e, sem contagem
(HOOKS-FIXTURES-GERADA, E18.1), não conflita entre PRs que acrescentam fixtures; o detalhe sai só no `--detalhe`."""
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "indice-fixtures.py"
FIXTURE = '{"descricao": "caso", "esperado": {"codigo": 2}}\n'


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

    def test_lista_todo_hook_e_prefixo_do_corpus_sem_contagem(self):
        texto = (RAIZ / "docs" / "hooks-fixtures.md").read_text(encoding="utf-8")
        pastas = sorted(p for p in (RAIZ / "tests" / "hooks").iterdir() if p.is_dir() and any(p.glob("*.json")))
        self.assertGreaterEqual(len(pastas), 10, "o corpus tem pelo menos 10 hooks")
        for pasta in pastas:
            with self.subTest(hook=pasta.name):
                secao = texto.split(f"\n## `{pasta.name}`\n", 1)[1].split("\n## ", 1)[0]
                prefixos = sorted({c.stem.split("-", 1)[0] for c in pasta.glob("*.json")})
                self.assertEqual(re.findall(r"^- `(.+)-\*`$", secao, re.M), prefixos)
        self.assertNotRegex(texto, r"\d+ fixtures|\| ---: \|", "a contagem conflita entre PRs: só no --detalhe")

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
            texto = indice.detalhe(raiz)
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
            filtrado = indice.detalhe(Path(tmp), [re.compile(r"\bpnpm\b")])
            self.assertIn("| `a-*` | 2 | 2 | 0 | — | — | lançador no início |", filtrado)
            self.assertIn("| `b-*` | 1 | 1 | 0 | — | — | — |", filtrado)
            self.assertIn("| `c-*` | 1 | 1 | 0 | — | — | — |", filtrado)
            self.assertIn("| `c-*` | 1 | 1 | 0 | — | — | pnpm sem filtro |", indice.detalhe(Path(tmp), []))
            self.assertIn("| `c-*` | 1 | 1 | 0 | — | — | — |", indice.detalhe(Path(tmp)), "sem termos dados, os do config")

    def test_resumo_corta_a_lista(self):
        indice = carregar()
        self.assertEqual(indice.resumo({}), "—")
        self.assertEqual(indice.resumo({"b": 1, "a": 1, "c": 3, "d": 1, "e": 1}), "`c`, `a`, `b`, `d` e mais 1")

    def test_caso_novo_em_prefixo_existente_nao_muda_o_arquivo(self):
        indice = carregar()
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "tests" / "hooks" / "h"
            pasta.mkdir(parents=True)
            (pasta / "b-1.json").write_text(FIXTURE, encoding="utf-8")
            antes = indice.gerar(Path(tmp))
            (pasta / "b-2.json").write_text(FIXTURE, encoding="utf-8")
            self.assertEqual(indice.gerar(Path(tmp)), antes, "caso novo em prefixo que já existe não toca o arquivo")
            (pasta / "a-1.json").write_text(FIXTURE, encoding="utf-8")
            depois = indice.gerar(Path(tmp))
        self.assertEqual(depois.replace("- `a-*`\n", "", 1), antes, "prefixo novo é uma linha só")
        self.assertLess(depois.index("`a-*`"), depois.index("`b-*`"), "ordem alfabética, não pelo tamanho do grupo")

    def test_dois_prs_com_fixtures_diferentes_se_juntam_sem_conflito(self):
        """E18.1: dois ramos que acrescentam fixtures (no prefixo que já existe, em prefixo novo no mesmo hook e em hook
        novo), cada um com o índice regerado, juntam-se sem conflito, e o índice da junção está em dia."""
        git = shutil.which("git")
        self.assertIsNotNone(git, "o teste precisa do git")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            ambiente = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "LC_ALL": "C",
                        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "t",
                        "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

            def rodar(*args):
                r = subprocess.run(list(args), cwd=repo, env=ambiente, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{args}: {r.stdout}{r.stderr}")
                return r

            def acrescentar(fixtures, mensagem):
                for nome in fixtures:
                    (repo / "tests" / "hooks" / nome).parent.mkdir(parents=True, exist_ok=True)
                    (repo / "tests" / "hooks" / nome).write_text(FIXTURE, encoding="utf-8")
                rodar(sys.executable, "-I", "scripts/indice-fixtures.py")
                rodar(git, "add", "-A")
                rodar(git, "commit", "-q", "-m", mensagem)

            (repo / "scripts").mkdir(parents=True)
            (repo / "docs").mkdir()
            shutil.copy(SCRIPT, repo / "scripts" / "indice-fixtures.py")
            rodar(git, "init", "-q", "-b", "base")
            acrescentar(["h/c-1.json", "h/g-1.json", "h/m-1.json", "k/a-1.json"], "base")
            rodar(git, "switch", "-q", "-c", "pr1")
            acrescentar(["h/c-2.json", "h/e-1.json", "h/m-2.json", "j/a-1.json"], "pr1")
            rodar(git, "switch", "-q", "base")
            rodar(git, "switch", "-q", "-c", "pr2")
            acrescentar(["h/c-3.json", "h/i-1.json", "h/z-1.json", "k/a-2.json"], "pr2")
            self.assertEqual(rodar(git, "diff", "--name-only", "base", "pr2", "--", "docs").stdout, "docs/hooks-fixtures.md\n")
            rodar(git, "switch", "-q", "base")
            rodar(git, "merge", "-q", "--no-edit", "pr1")
            rodar(git, "merge", "-q", "--no-edit", "pr2")
            self.assertEqual(rodar(git, "status", "--porcelain").stdout, "", "junção sem conflito")
            self.assertIn("em dia", rodar(sys.executable, "-I", "scripts/indice-fixtures.py", "--conferir").stdout)
            texto = (repo / "docs" / "hooks-fixtures.md").read_text(encoding="utf-8")
        for linha in ("- `c-*`", "- `e-*`", "- `g-*`", "- `i-*`", "- `m-*`", "- `z-*`", "## `j`", "## `k`"):
            self.assertIn(linha, texto)

    def test_detalhe_imprime_sem_gravar(self):
        indice = carregar()
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(indice, "RAIZ", Path(tmp)), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as saida:
            pasta = Path(tmp) / "tests" / "hooks" / "h"
            pasta.mkdir(parents=True)
            (pasta / "a-b.json").write_text(FIXTURE, encoding="utf-8")
            self.assertEqual(indice.main(["--detalhe"]), 0)
            self.assertFalse((Path(tmp) / indice.INDICE).exists(), "--detalhe não grava")
            self.assertEqual(saida.getvalue(), indice.detalhe(Path(tmp)))
        self.assertIn("| `a-*` | 1 | 1 | 0 |", saida.getvalue())

    def test_conferir_da_rc_0_em_dia(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--conferir"], capture_output=True, text=True)
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
            self.assertEqual(indice.main(["--detalhe", "--conferir"]), 2, "opções juntas são recusadas")
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
