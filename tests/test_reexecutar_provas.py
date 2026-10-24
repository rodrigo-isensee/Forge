"""Arquivo de provas na branch (EST-030-L2, M15): formato do modelo e texto da regra que o descreve."""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DOCS = AQUI.parent / "docs"
LINHA_CMD = re.compile(r"^- PQ-(\d+) \(cmd\): `([^`]+)` · espera: (.+)$")


class ModeloDeProvas(unittest.TestCase):
    def test_modelo_traz_linhas_cmd_no_formato_da_regra(self):
        linhas = (DOCS / "provas" / "_modelo.md").read_text(encoding="utf-8").splitlines()
        cmd = [LINHA_CMD.match(l) for l in linhas if "(cmd)" in l and l.startswith("- PQ-")]
        self.assertEqual(len(cmd), 2)
        self.assertTrue(all(cmd))

    def test_regra_descreve_o_arquivo_a_lista_permitida_e_a_falha_fechada(self):
        regra = (DOCS / "regras" / "R-PROVA.md").read_text(encoding="utf-8")
        for trecho in ("docs/provas/<pedido>.md", "scripts/reexecutar-provas.py", "sem shell", "lista permitida",
                       "falha fechada", "pull_request_target"):
            self.assertIn(trecho, regra)


spec = importlib.util.spec_from_file_location("reexecutar_provas", AQUI.parent / "scripts" / "reexecutar-provas.py")
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)


class Lista(unittest.TestCase):
    def test_permitidos(self):
        for cmd in ("python3 -m unittest tests.test_x", "python3 -m unittest -v a.b c", "git rev-parse --verify HEAD",
                    "git diff --numstat abc...HEAD", "git ls-files -- docs"):
            self.assertIsNone(rp.comando_permitido(cmd.split()), cmd)

    def test_recusados_por_falha_fechada(self):
        for cmd in ("rm -rf x", "python3 -c print(1)", "python3 -m unittest discover -s tests", "python3 -m unittest",
                    "python3 -m http.server", "python3 scripts/x.py", "git push origin x", "git diff --output=x",
                    "git diff --no-index a b", "git log", "bash -c ls", "curl http://x", "python3 -m unittest a;b",
                    "git rev-parse $(id)"):
            self.assertIsNotNone(rp.comando_permitido(cmd.split()), cmd)


class Espera(unittest.TestCase):
    def test_cada_forma(self):
        casos = [("rc=0", "x\n", 0, None), ("rc=0", "", 1, "rc=0"), ("contém 'ab'", "xaby", 1, None),
                 ("contém 'zz'", "xaby", 0, "contém 'zz'"), ("igual 'ok'", "ok\n", 1, None), ("igual 'ok'", "ok2", 0, "igual 'ok'"),
                 ("linhas=2", "a\nb\n", 0, None), ("linhas=2", "a\n", 0, "linhas=2"), ("linhas>=2", "a\nb\nc", 0, None),
                 ("linhas>=2", "a", 0, "linhas>=2"), ("rc=0 e linhas=1", "a", 0, None), ("rc=0 e linhas=1", "a\nb", 0, "linhas=1")]
        for espera, saida, rc, esperado in casos:
            self.assertEqual(rp.avaliar(espera, saida, rc), esperado, (espera, saida, rc))

    def test_espera_ilegivel_falha_fechada(self):
        with self.assertRaises(rp.Falha):
            rp.avaliar("talvez", "x", 0)


class Execucao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / "docs" / "provas").mkdir(parents=True)
        (self.raiz / "t_ok.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): pass\n")
        (self.raiz / "t_ruim.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): self.fail('x')\n")

    def rodar(self, linhas, nome="p.md"):
        (self.raiz / "docs" / "provas" / nome).write_text("\n".join(linhas) + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(AQUI.parent / "scripts" / "reexecutar-provas.py"), "--raiz", str(self.raiz),
                            f"docs/provas/{nome}"], capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode, r.stdout + r.stderr

    def test_prova_que_confere_passa_e_so_cmd_conta(self):
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest t_ok` · espera: rc=0", "- PQ-2 (sha): abc", "texto"])
        self.assertEqual(rc, 0, saida)
        self.assertIn("1 prova(s) cmd", saida)

    def test_para_na_primeira_divergencia(self):
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest t_ruim` · espera: rc=0",
                                "- PQ-2 (cmd): `python3 -m unittest t_ok` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("PQ-1", saida)
        self.assertNotIn("ok docs/provas/p.md:2", saida)

    def test_comando_fora_da_lista_e_recusado_sem_executar(self):
        marca = self.raiz / "marca"
        rc, saida = self.rodar([f"- PQ-1 (cmd): `touch {marca}` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("recusado", saida)
        self.assertFalse(marca.exists())

    def test_sem_shell_o_metacaractere_nao_age(self):
        marca = self.raiz / "marca"
        rc, saida = self.rodar([f"- PQ-1 (cmd): `git rev-parse HEAD; touch {marca}` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertFalse(marca.exists())

    def test_linha_cmd_fora_do_formato_e_modelo_e_fora_de_provas_falham(self):
        self.assertEqual(self.rodar(["- PQ-1 (cmd): python3 -m unittest t_ok"])[0], 1)
        self.assertEqual(self.rodar(["- PQ-1 (cmd): `git rev-parse HEAD` · espera: talvez"])[0], 1)
        self.assertEqual(self.rodar(["- PQ-1 (cmd): `git rev-parse --verify HEAD` · espera: rc=0"], "_modelo.md")[0], 1)
        with self.assertRaises(rp.Falha):
            rp.reexecutar("../fora.md", self.raiz, 5)

    def test_ambiente_sem_segredo(self):
        original = os.environ.get("GITHUB_TOKEN")
        os.environ["GITHUB_TOKEN"] = "segredo"
        self.addCleanup(lambda: os.environ.pop("GITHUB_TOKEN") if original is None else os.environ.update(GITHUB_TOKEN=original))
        (self.raiz / "t_env.py").write_text("import os, unittest\nclass T(unittest.TestCase):\n    def test(self): assert 'GITHUB_TOKEN' not in os.environ\n")
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest t_env` · espera: rc=0"])
        self.assertEqual(rc, 0, saida)


class PassoDoCi(unittest.TestCase):
    CI = (AQUI.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    def passo(self):
        m = re.search(r"(?m)^      - name: Provas cmd do arquivo de provas.*?(?=^      - name: )", self.CI, re.S)
        self.assertIsNotNone(m)
        return m.group(0)

    def test_so_no_pull_request_sem_segredo_e_com_o_script_da_base(self):
        passo = self.passo()
        self.assertIn("github.event_name == 'pull_request'", passo)
        self.assertNotIn("pull_request_target", self.CI)
        self.assertNotIn("secrets.", passo)
        self.assertNotIn("GITHUB_TOKEN", passo)
        self.assertIn('git cat-file -e "$BASE:scripts/reexecutar-provas.py"', passo)
        self.assertIn('script="$RUNNER_TEMP/base/scripts/reexecutar-provas.py"', passo)

    def test_so_em_pr_para_a_develop_as_promocoes_ficam_fora(self):
        condicao = re.search(r"(?m)^        if: (.*)$", self.passo()).group(1)
        self.assertIn("github.event_name == 'pull_request'", condicao)
        self.assertIn("github.base_ref == 'develop'", condicao)

    def test_roda_no_sha_do_pr_sobre_o_arquivo_da_branch(self):
        passo = self.passo()
        self.assertIn('git worktree add --detach "$RUNNER_TEMP/pr" "$HEAD_SHA"', passo)
        self.assertIn("docs/provas/*.md", passo)
        self.assertIn('--raiz "$RUNNER_TEMP/pr"', passo)
        self.assertNotIn("${{", passo.split("run:")[1])  # entrada do evento só por env:, nunca no script

    def test_passo_vem_antes_da_suite(self):
        self.assertLess(self.CI.index("Provas cmd do arquivo de provas"), self.CI.index("- name: Testes do Forge\n        if: ${{ !cancelled() && steps"))


if __name__ == "__main__":
    unittest.main()
