"""VALIDAR-YAML-DO-WORKFLOW (v048 E13.6): scripts/validar-yaml-workflow.py recusa o YAML que o GitHub recusa sem criar jobs
(#929: `: ` sem aspas num valor simples) e aceita os workflows do repositório."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "validar-yaml-workflow.py"
spec = importlib.util.spec_from_file_location("validar_yaml_workflow", SCRIPT)
vyw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vyw)

BOM = """name: x
on:
  push:
    branches: [develop]
    tags:
      - v1
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - name: "com: aspas"
        run: |
          echo "a: b"
          echo ok:
      - name: simples # comentario: livre
        if: github.event_name != 'push' || github.ref != 'refs/heads/develop'
      - uses: x/y@abc # v1.0: nota
        with:
          chave: 'it''s: ok'
"""


def defeitos(texto):
    return [msg for _, msg in vyw.validar(texto)]


class ValidarYaml(unittest.TestCase):
    def test_workflow_bom_passa(self):
        self.assertEqual(vyw.validar(BOM), [])

    def test_dois_pontos_sem_aspas_no_valor_e_recusado(self):
        ruim = BOM.replace('name: simples # comentario: livre', "name: Passo (nota: sem aspas)")
        erros = vyw.validar(ruim)
        self.assertEqual(len(erros), 1)
        self.assertIn("valor simples com `:`", erros[0][1])

    def test_valor_terminado_em_dois_pontos_e_recusado(self):
        self.assertTrue(defeitos("a:\n  - name: Passo:\n"))

    def test_tabulacao_na_indentacao_e_recusada(self):
        self.assertTrue(any("tabulação" in m for m in defeitos("a:\n\tb: 1\n")))

    def test_chave_repetida_no_mesmo_mapa_e_recusada(self):
        self.assertTrue(any("repetida" in m for m in defeitos("a:\n  b: 1\n  b: 2\n")))

    def test_mesma_chave_em_itens_diferentes_passa(self):
        self.assertEqual(defeitos("steps:\n  - name: a\n    run: x\n  - name: b\n    run: y\n"), [])

    def test_comentario_com_dois_pontos_nao_e_conferido(self):
        self.assertEqual(defeitos("# a: b: c\nx: 1\n"), [])

    def test_linha_em_branco_dentro_do_bloco_nao_encerra_o_corpo(self):
        self.assertEqual(defeitos("run: |\n  um\n\n  a: b: c\nnext: 1\n"), [])

    def test_linha_depois_do_bloco_volta_a_ser_conferida(self):
        self.assertTrue(defeitos("run: |\n  um\nname: a: b\n"))

    def test_corpo_de_bloco_nao_e_conferido(self):
        self.assertEqual(defeitos("run: >-\n  a: b: c\n\tz\nnext: 1\n"), [])

    def test_workflows_do_repositorio_passam(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=RAIZ, capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_cli_sai_1_com_defeito_e_nomeia_arquivo_e_linha(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "w.yml"
            arq.write_text("jobs:\n  a:\n    name: x: y\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), str(arq)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("w.yml:3:", r.stdout)

    def test_arquivo_ilegivel_sai_2(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "/nao/existe.yml"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
