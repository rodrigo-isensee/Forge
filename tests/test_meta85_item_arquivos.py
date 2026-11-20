"""META85-ITEM-ATE-10-ARQUIVOS (v0478 E34.1): o `forge-check classe` recusa (rc 1) o item com mais de 10 arquivos no diff, pedindo o
corte antes de começar. Testes (com `tests/mutantes/`), fragmentos de `changelog.d/` e pareceres não contam; os módulos do portão em
`tests/` contam."""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from test_isencoes import FORGE_CHECK, Repo  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


def ambiente_limpo(home):
    """META85-FC-RESTOS A3: só o PATH, o TMPDIR e a HOME do teste, sem o ambiente herdado (GIT_*, FORGE_*, PYTHON*), e o git sem
    config global nem de sistema e sem manutenção automática."""
    base = {k: os.environ[k] for k in ("PATH", "TMPDIR") if k in os.environ}
    return sem_manutencao({**base, "HOME": str(home), "LANG": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})


def docs(n, pasta="docs/guias"):
    return {f"{pasta}/g{i}.md": f"# guia {i}\n" for i in range(n)}


class ItemAteDezArquivos(Repo):
    def classe(self, *args):
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.tmp), "classe", "--base", "develop", *args],
                           capture_output=True, text=True, timeout=60, env=ambiente_limpo(self.tmp / "home"))
        return r.returncode, r.stdout + r.stderr

    def test_dez_arquivos_passam(self):
        self.commitar(docs(10), "dez")
        rc, saida = self.classe()
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("item:", saida)

    def test_onze_arquivos_sao_recusados(self):
        self.commitar(docs(11), "onze")
        rc, saida = self.classe()
        self.assertEqual(rc, 1, saida)
        self.assertIn("item: 11 arquivos, teto 10: corte o item antes de começar", saida)

    def test_json_traz_a_contagem_e_recusa(self):
        self.commitar(docs(11), "onze")
        rc, saida = self.classe("--json")
        self.assertEqual(rc, 1, saida)
        dados = json.loads(saida)
        self.assertEqual((dados["arquivos_do_item"], dados["teto_de_arquivos"]), (11, 10))

    def test_testes_mutantes_changelog_e_pareceres_nao_contam(self):
        extras = {"tests/test_a.py": "x\n", "tests/test_b.py": "x\n", "tests/mutantes/p1.json": "{}\n", "changelog.d/x.md": "- x\n",
                  "docs/reviews/p1.md": "# r\n", "docs/qa/p1.md": "# q\n"}
        self.commitar({**docs(10), **extras}, "dez e os acompanhantes")
        rc, saida = self.classe("--json")
        self.assertEqual(rc, 0, saida)
        self.assertEqual(json.loads(saida).get("arquivos_do_item"), 10)  # .get: na base, falha (não dá erro)

    def test_modulo_do_portao_em_tests_conta_e_continua_barrado(self):
        self.commitar({**docs(10), "tests/catraca.py": "x = 1\n"}, "dez e a catraca")
        rc, saida = self.classe("--json")
        self.assertEqual(rc, 1, saida)
        self.assertEqual(json.loads(saida).get("arquivos_do_item"), 11)

    def test_base_ilegivel_nao_quebra_e_a_classe_vale_c(self):  # sem diff lido, a classe já exige todos os portões
        self.commitar(docs(11), "onze")
        rc, saida = self.classe("--base", "nao-existe")
        self.assertEqual(rc, 0, saida)
        self.assertIn("classe: C", saida)


if __name__ == "__main__":
    import unittest
    unittest.main()
