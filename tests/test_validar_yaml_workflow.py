"""VALIDAR-YAML-DO-WORKFLOW (v048 E13.6): scripts/validar-yaml-workflow.py recusa o YAML que o GitHub recusa sem criar jobs
(#929: `: ` sem aspas num valor simples) e aceita os workflows do repositório."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
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

    def test_defeito_depois_de_linha_sem_par_continua_sendo_achado(self):
        self.assertTrue(any("valor simples" in m for m in defeitos("a:\n  - v1\n  - name: x: y\n")))

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

    def _arvore(self, d):
        """Árvore temporária com a cópia do script e .github/workflows/ vazio; devolve (script, pasta dos workflows)."""
        (Path(d) / "scripts").mkdir()
        shutil.copy(SCRIPT, Path(d) / "scripts" / SCRIPT.name)
        wf = Path(d) / ".github" / "workflows"
        wf.mkdir(parents=True)
        return Path(d) / "scripts" / SCRIPT.name, wf

    def _rodar(self, script, *args):
        return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, timeout=20)

    def test_linha_longa_de_espacos_e_linear(self):
        for n in (10000, 20000, 40000):
            t = time.perf_counter()
            vyw.validar("a: x" + " " * n + "y\n")
            self.assertLess(time.perf_counter() - t, 0.05, n)

    def test_link_para_arquivo_especial_sai_2(self):
        with tempfile.TemporaryDirectory() as d:
            script, wf = self._arvore(d)
            os.symlink("/dev/zero", wf / "zero.yml")
            r = self._rodar(script)
        self.assertEqual(r.returncode, 2)
        self.assertIn("não é arquivo regular", r.stderr)

    def test_link_para_fora_nao_ecoa_o_conteudo(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as fora:
            script, wf = self._arvore(d)
            (Path(fora) / "fora.txt").write_text("segredo: token: XYZ-fora-do-repo\n", encoding="utf-8")
            os.symlink(Path(fora) / "fora.txt", wf / "link.yml")
            r = self._rodar(script)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("XYZ-fora-do-repo", r.stdout + r.stderr)

    def test_arquivo_acima_de_1_mib_sai_2(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "grande.yml"
            arq.write_text("a: " + "x" * (1 << 20) + "\n", encoding="utf-8")
            r = self._rodar(SCRIPT, str(arq))
        self.assertEqual(r.returncode, 2)
        self.assertIn("1 MiB", r.stderr)

    def test_sem_workflow_nenhum_sai_2(self):
        with tempfile.TemporaryDirectory() as d:
            script, _ = self._arvore(d)
            r = self._rodar(script)
            shutil.rmtree(Path(d) / ".github")
            r2 = self._rodar(script)
        self.assertEqual((r.returncode, r2.returncode), (2, 2))
        self.assertIn("nenhum workflow", r.stderr)


if __name__ == "__main__":
    unittest.main()
