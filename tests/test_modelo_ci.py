"""Modelo de CI do projeto (E3.41, R-CUSTO): suíte só em PR e nas branches do fluxo, sem rodar em documento, check leve, concurrency."""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "templates" / "projeto" / ".github" / "workflows"
DOC = '["**/*.md", "docs/**"]'


def ler(nome):
    return (MODELO / nome).read_text(encoding="utf-8")


def linhas_de_codigo(nome):
    return [l for l in ler(nome).splitlines() if l.strip() and not l.lstrip().startswith("#")]


class SuitePesada(unittest.TestCase):
    def test_push_so_nas_branches_do_fluxo(self):
        for nome in ("ci.yml", "ci-docs.yml"):
            self.assertIn("  push:\n    branches: [develop, homolog, main]\n", ler(nome), nome)

    def test_pull_request_dispara_a_suite(self):
        self.assertIn("  pull_request:\n    types: [opened, synchronize, reopened]\n", ler("ci.yml"))

    def test_so_documento_nao_roda_a_suite_e_o_par_cobre_a_mesma_lista(self):
        pesado, leve = ler("ci.yml"), ler("ci-docs.yml")
        self.assertEqual(pesado.count("paths-ignore: " + DOC), 2)
        self.assertEqual(leve.count("paths: " + DOC), 2)

    def test_comando_vem_da_stack_sem_nome_de_ferramenta(self):
        texto = ler("ci.yml")
        self.assertIn("          {{COMANDO_PRONTO}}\n", texto)
        for termo in ("npm ", "pnpm", "pytest", "setup-node", "setup-python"):
            self.assertNotIn(termo, "\n".join(linhas_de_codigo("ci.yml")))


class CheckObrigatorio(unittest.TestCase):
    def test_job_leve_tem_o_mesmo_nome_do_agregador(self):
        self.assertIn("  ci:\n    name: ci\n", ler("ci.yml"))
        self.assertIn("  ci:\n    name: ci\n", ler("ci-docs.yml"))

    def test_agregador_so_passa_com_suite_success(self):
        texto = ler("ci.yml")
        self.assertIn("    if: always()\n    needs: [suite]\n", texto)
        self.assertIn('run: test "$RESULTADO" = "success"', texto)
        self.assertIn("RESULTADO: ${{ needs.suite.result }}", texto)

    def test_job_leve_nao_gasta_suite(self):
        self.assertNotIn("checkout", ler("ci-docs.yml"))


class Concorrencia(unittest.TestCase):
    def test_push_e_pr_da_mesma_branch_dividem_o_grupo_e_cancelam(self):
        for nome, prefixo in (("ci.yml", "ci"), ("ci-docs.yml", "ci-docs")):
            texto = ler(nome)
            self.assertIn("  group: %s-${{ github.head_ref || github.ref_name }}\n  cancel-in-progress: true\n" % prefixo, texto, nome)


class Higiene(unittest.TestCase):
    def test_todo_job_tem_timeout_e_nenhuma_burla(self):
        for nome in ("ci.yml", "ci-docs.yml"):
            texto = ler(nome)
            jobs = len(re.findall(r"^    runs-on:", texto, re.M))
            self.assertEqual(len(re.findall(r"^    timeout-minutes: \d+$", texto, re.M)), jobs, nome)
            for burla in ("continue-on-error", "[skip ci]", "pull_request_target"):
                self.assertNotIn(burla, texto, nome)

    def test_acao_de_terceiros_fixada_por_sha(self):
        for nome in ("ci.yml", "ci-docs.yml"):
            for uso in re.findall(r"uses: (\S+)", ler(nome)):
                self.assertRegex(uso, r"@[0-9a-f]{40}$", nome)

    def test_permissoes_minimas(self):
        self.assertIn("\npermissions:\n  contents: read\n", ler("ci.yml"))
        self.assertIn("\npermissions: {}\n", ler("ci-docs.yml"))


class Entrega(unittest.TestCase):
    def test_forge_init_copia_o_modelo_com_o_comando_da_stack(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([str(RAIZ / "bin" / "forge-init"), "--nome", "x", "--stack", "python", "--pronto", "make pronto",
                            "--sem-sandbox", d], check=True, capture_output=True, text=True)
            ci = (Path(d) / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
            self.assertIn("          make pronto\n", ci)
            self.assertNotIn("{{COMANDO_PRONTO}}", ci)
            self.assertTrue((Path(d) / ".github" / "workflows" / "ci-docs.yml").is_file())

    def test_skill_aponta_para_o_modelo_e_explica_o_porque(self):
        skill = (RAIZ / "skills" / "ci-cd" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("templates/projeto/.github/workflows/ci.yml", skill)
        self.assertIn("minutos", skill)
        self.assertIn("push de branch de trabalho", skill)


if __name__ == "__main__":
    unittest.main()
