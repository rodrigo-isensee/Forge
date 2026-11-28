"""Modelo de CI do projeto (E3.41, E3.74, R-CUSTO): suíte só em PR e nas branches do fluxo, um workflow só, detecção de só documento, um check "ci", concurrency."""
import itertools
import os
import re
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tests"))
from ambiente_git import sem_manutencao  # noqa: E402

MODELO = RAIZ / "templates" / "projeto" / ".github" / "workflows"


def ler(nome="ci.yml"):
    return (MODELO / nome).read_text(encoding="utf-8")


def linhas_de_codigo():
    return [l for l in ler().splitlines() if l.strip() and not l.lstrip().startswith("#")]


def script(passo):
    """Corpo do `run: |` do passo de nome `passo`, sem a indentação."""
    m = re.search(r"- name: %s\n(?:.*\n)*?        run: \|\n((?:          .*\n)+)" % re.escape(passo), ler())
    assert m, passo
    return "".join(l[10:] + "\n" for l in m.group(1).splitlines())


def ambiente_limpo(**extra):
    """Ambiente do subprocesso sem GIT_* nem BASH_ENV herdados (como tests/test_adotar.py)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "BASH_ENV"}
    env.update(extra)
    return sem_manutencao(env)


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True,
                          env=ambiente_limpo()).stdout.strip()


class SuitePesada(unittest.TestCase):
    def test_um_workflow_so_e_sem_filtro_de_caminho(self):
        self.assertEqual(sorted(p.name for p in MODELO.iterdir()), ["ci.yml"])
        self.assertNotIn("paths", ler().replace("paths-ignore", "paths"))
        self.assertNotIn("paths:", ler())

    def test_push_so_nas_branches_do_fluxo(self):
        self.assertIn("  push:\n    branches: [develop, homolog, main]\n", ler())

    def test_pull_request_dispara_a_suite(self):
        self.assertIn("  pull_request:\n    types: [opened, synchronize, reopened]\n", ler())

    def test_suite_pula_so_quando_a_deteccao_diz_documento(self):
        self.assertIn("    needs: [mudanca]\n    if: needs.mudanca.outputs.so_documento != 'true'\n", ler())

    def test_comando_vem_da_stack_sem_nome_de_ferramenta(self):
        self.assertIn("          {{COMANDO_PRONTO}}\n", ler())
        for termo in ("npm ", "pnpm", "pytest", "setup-node", "setup-python"):
            self.assertNotIn(termo, "\n".join(linhas_de_codigo()))


class Deteccao(unittest.TestCase):
    """Roda o script de detecção do modelo num repositório descartável."""

    def detectar(self, arquivos, base="ok", mover=()):
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q", "-b", "main")
            git(d, "config", "user.email", "t@t")
            git(d, "config", "user.name", "t")
            (Path(d) / "base.txt").write_text("a")
            for origem, _ in mover:
                (Path(d) / origem).parent.mkdir(parents=True, exist_ok=True)
                (Path(d) / origem).write_text("def f():\n    return 1\n")
            git(d, "add", "-A")
            git(d, "commit", "-qm", "base")
            b = git(d, "rev-parse", "HEAD")
            for origem, destino in mover:
                (Path(d) / destino).parent.mkdir(parents=True, exist_ok=True)
                git(d, "mv", origem, destino)
            for a in arquivos:
                p = Path(d) / a
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("x")
            git(d, "add", "-A")
            git(d, "commit", "-qm", "muda", "--allow-empty")
            cabeca = git(d, "rev-parse", "HEAD")
            saida = Path(d) / "saida"
            env = ambiente_limpo(GITHUB_OUTPUT=str(saida), CABECA=cabeca,
                       BASE={"ok": b, "vazia": "", "zeros": "0" * 40}[base])
            subprocess.run(["bash", "-c", script("Detecta mudança só de documento")], cwd=d, env=env, check=True)
            return saida.read_text().strip()

    def test_so_documento(self):
        self.assertEqual(self.detectar(["README.md", "docs/a/b.txt", "x/y.md"]), "so_documento=true")

    def test_codigo_ou_misto_roda_a_suite(self):
        self.assertEqual(self.detectar(["src/a.py"]), "so_documento=false")
        self.assertEqual(self.detectar(["README.md", "src/a.py"]), "so_documento=false")
        self.assertEqual(self.detectar(["docs.txt"]), "so_documento=false")

    def test_renomear_codigo_para_documento_roda_a_suite(self):
        # sondas S1 e S2 do parecer de segurança: a renomeação não esconde a origem
        self.assertEqual(self.detectar([], mover=[("src/app.py", "docs/app.py")]), "so_documento=false")
        self.assertEqual(self.detectar([], mover=[("src/app.py", "src/app.md")]), "so_documento=false")

    def test_deteccao_usa_no_renames(self):
        self.assertIn('git diff --no-renames --name-only "$BASE...$CABECA"', script("Detecta mudança só de documento"))

    def test_na_duvida_roda_a_suite(self):
        self.assertEqual(self.detectar(["README.md"], base="vazia"), "so_documento=false")
        self.assertEqual(self.detectar(["README.md"], base="zeros"), "so_documento=false")
        self.assertEqual(self.detectar([]), "so_documento=false")


class CheckObrigatorio(unittest.TestCase):
    def agregar(self, mudanca, so_documento, suite):
        env = ambiente_limpo(MUDANCA=mudanca, SO_DOCUMENTO=so_documento, SUITE=suite)
        return subprocess.run(["bash", "-c", script("Suíte verde ou só documento")], env=env).returncode == 0

    def test_ci_e_unico_e_roda_sempre(self):
        texto = ler()
        self.assertEqual(len(re.findall(r"^    name: ci$", texto, re.M)), 1)
        self.assertIn("    if: always()\n    needs: [mudanca, suite]\n", texto)

    def test_nunca_verde_sem_a_suite_num_pr_com_codigo(self):
        for mudanca, suite in itertools.product(("success", "failure", "cancelled", "skipped"), repeat=2):
            for so_doc in ("false", ""):
                esperado = mudanca == "success" and suite == "success"
                self.assertEqual(self.agregar(mudanca, so_doc, suite), esperado, (mudanca, so_doc, suite))

    def test_so_documento_aceita_suite_pulada_e_nada_mais(self):
        self.assertTrue(self.agregar("success", "true", "skipped"))
        for suite in ("success", "failure", "cancelled"):
            self.assertFalse(self.agregar("success", "true", suite))
        for mudanca in ("failure", "cancelled", "skipped"):
            self.assertFalse(self.agregar(mudanca, "true", "skipped"))


class Concorrencia(unittest.TestCase):
    def test_pr_pelo_numero_push_pela_ref_e_cancela_a_obsoleta(self):
        self.assertIn("  group: ci-${{ github.event.pull_request.number || github.ref }}\n  cancel-in-progress: true\n", ler())
        self.assertNotIn("head_ref", ler())


class Higiene(unittest.TestCase):
    def test_todo_job_tem_timeout_e_nenhuma_burla(self):
        texto = ler()
        jobs = len(re.findall(r"^    runs-on:", texto, re.M))
        self.assertEqual(len(re.findall(r"^    timeout-minutes: \d+$", texto, re.M)), jobs)
        for burla in ("continue-on-error", "[skip ci]", "pull_request_target"):
            self.assertNotIn(burla, texto)

    def test_acao_de_terceiros_fixada_por_sha(self):
        usos = re.findall(r"uses: (\S+)", ler())
        self.assertTrue(usos)
        for uso in usos:
            self.assertRegex(uso, r"@[0-9a-f]{40}$")

    def test_permissoes_minimas_e_nenhuma_interpolacao_em_run(self):
        texto = ler()
        self.assertIn("\npermissions:\n  contents: read\n", texto)
        self.assertEqual(texto.count("    permissions: {}\n"), 1)
        for corpo in re.findall(r"run: \|\n((?:          .*\n)+)", texto):
            self.assertNotIn("${{", corpo)


class Entrega(unittest.TestCase):
    def test_forge_init_copia_o_modelo_com_o_comando_da_stack(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([str(RAIZ / "bin" / "forge-init"), "--nome", "x", "--stack", "python", "--pronto", "make pronto",
                            "--sem-sandbox", d], check=True, capture_output=True, text=True, env=ambiente_limpo())
            fluxos = Path(d) / ".github" / "workflows"
            ci = (fluxos / "ci.yml").read_text(encoding="utf-8")
            self.assertIn("          make pronto\n", ci)
            self.assertNotIn("{{COMANDO_PRONTO}}", ci)
            self.assertFalse((fluxos / "ci-docs.yml").exists())
            # `${{ }}` é do GitHub Actions e fica; marcador do modelo (`{{X}}` sem `$`) não pode sobrar
            self.assertIn("${{", ci)
            self.assertIsNone(re.search(r"(?<!\$)\{\{", ci))

    def test_skill_aponta_para_o_modelo_e_explica_o_porque(self):
        pasta = RAIZ / "skills" / "ci-cd"
        self.assertIn("ci-de-projeto-privado.md", (pasta / "SKILL.md").read_text(encoding="utf-8"))
        skill = (pasta / "ci-de-projeto-privado.md").read_text(encoding="utf-8")
        self.assertIn("templates/projeto/.github/workflows/ci.yml", skill)
        self.assertIn("minutos", skill)
        self.assertIn("push de branch de trabalho", skill)
        self.assertIn("github.event.pull_request.number || github.ref", skill)
        self.assertNotIn("github.head_ref || github.ref_name", skill)
        self.assertIn("git diff --no-renames --name-only", skill)


if __name__ == "__main__":
    unittest.main()
