"""SUITE-NO-CI (decisão do dono, 2026-11-08, que substitui a M8): o pre-push roda as checagens baratas antes da trava e
depois só os testes afetados (`bin/forge-testes --afetados`), para qualquer branch e para várias refs; a suíte inteira
roda no CI do PR e, local, só com FORGE_PREPUSH_SUITE=1.

Cada teste roda o hook de verdade num repositório descartável com três suítes mínimas (`test_sugerir` e `test_forge`,
os módulos que o mapa dá a `bin/forge-sugerir`, e `test_a`, que o mapa não cita), cada uma deixando uma marca
`rodou-<nome>`, a cópia do `bin/forge-testes` e uma `origin/develop` local como base. Classe do defeito: o portão rodar
mais do que o afetado (a suíte inteira local) ou menos do que o seguro (um leitor do caminho fora do plano), e a
checagem barata só falhar depois da fila. Variantes: caminho mapeado, módulo de teste mudado, caminho sem mapa (com e
sem leitor), sem base e sem a ferramenta (a suíte inteira, falha fechada), árvore suja, HEAD diferente do enviado, várias
refs, tag, branch fora de melhoria/*, falha no afetado e no não afetado, opt-in da suíte inteira, módulo falso em bin/,
checagens baratas (sintaxe e changelog) antes da trava, bloqueios de conteúdo, e a prova de árvore verde (só a suíte
completa anota).
"""
import os
import shutil
import subprocess
import hashlib
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})
AMBIENTE["FORGE_PREPUSH_SUITE"] = "afetados"  # ENVIO-LEVE: o padrão do hook não roda teste; estes testes exercitam o plano dos afetados
ZERO = "0" * 40
BOA = "import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_a(self):\n        pathlib.Path('rodou-{}').write_text('sim')\n"
RUIM = BOA + "        self.fail('de proposito')\n"
# Os módulos do mapa leem a ferramenta que o diff muda: `QUEBRA` nela derruba o módulo afetado.
LE_A_FERRAMENTA = BOA + "        self.assertNotIn('QUEBRA', pathlib.Path('bin/forge-sugerir').read_text())\n"
TODAS = {"rodou-a", "rodou-sugerir", "rodou-forge"}
AFETADOS = {"rodou-sugerir", "rodou-forge"}


class Base(unittest.TestCase):
    """O repositório de brinquedo e o hook de verdade."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        self.repo = base / "repo"
        (self.repo / "tests").mkdir(parents=True)
        (self.repo / "bin").mkdir()
        shutil.copy(RAIZ / "bin" / "forge-testes", self.repo / "bin" / "forge-testes")
        shutil.copy(RAIZ / "bin" / "forge_apoio_testes.py", self.repo / "bin" / "forge_apoio_testes.py")  # FILA-31 F1: o script o carrega da pasta dele
        self.git("init", "-q", "-b", "melhoria/x")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(base / "home"), FORGE_TRAVA_ESPERA="20")
        (self.repo / ".gitignore").write_text("rodou-*\n__pycache__/\n/.forge\n")
        self.base = self.commit("base", tests__test_a_py=BOA.format("a"), bin__forge_sugerir="x = 1\n",
                                tests__test_sugerir_py=LE_A_FERRAMENTA.format("sugerir"),
                                tests__test_forge_py=BOA.format("forge"))
        self.git("update-ref", "refs/remotes/origin/develop", self.base)
        self.verde = self.run_dir / f"forge-suite-{os.getuid()}.verde"

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            alvo = self.repo / nome.replace("_py", ".py").replace("__", "/").replace("forge_sugerir", "forge-sugerir")
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def roda(self, local=None, remoto=ZERO, destino="melhoria/x", entrada=None):
        for p in self.repo.glob("rodou-*"):
            p.unlink()
        local = local or self.git("rev-parse", "HEAD")
        entrada = entrada if entrada is not None else f"refs/heads/x {local} refs/heads/{destino} {remoto}\n"
        r = subprocess.run([str(HOOK), "origin", "u"], cwd=self.repo, env=self.env, input=entrada,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, {p.name for p in self.repo.glob("rodou-*")}, r.stderr

class PrePushAfetados(Base):
    def test_so_os_modulos_do_mapa_rodam_e_nao_anotam_a_arvore_verde(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)
        self.assertIn("rodando só os testes afetados", erro)
        self.assertFalse(self.verde.exists(), "só a suíte completa anota a prova de árvore verde")

    def test_modulo_de_teste_mudado_roda_ele_e_nao_a_suite_inteira(self):
        self.commit("toca o teste sugerir", tests__test_sugerir_py=LE_A_FERRAMENTA.format("sugerir") + "# x\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, {"rodou-sugerir"})
        self.assertIn("rodando só os testes afetados", erro)
        self.assertFalse(self.verde.exists())

    def test_falha_em_modulo_nao_afetado_nao_barra_e_no_afetado_barra(self):
        self.commit("a quebra", tests__test_a_py=RUIM.format("a"))
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))  # a quebra já está na base
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.assertEqual(self.roda()[0], 0, "test_a, que o mapa não cita, não roda")
        self.commit("ferramenta quebra o modulo afetado", bin__forge_sugerir="QUEBRA\n")
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("testes do Forge falharam", erro)

    def test_caminho_sem_mapa_e_sem_leitor_nao_roda_teste_e_avisa(self):
        self.commit("novo", novo_txt="x\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, set())
        self.assertIn("nenhum teste afetado", erro)
        self.assertFalse(self.verde.exists())

    def test_caminho_sem_mapa_roda_o_teste_que_o_cita(self):  # na dúvida, o módulo entra
        self.commit("leitor", tests__test_a_py=BOA.format("a") + "        pathlib.Path('dados/tabela.csv')\n")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("dado novo", **{"dados/tabela.csv": "a,b\n"})
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, {"rodou-a"})

    def test_sem_a_base_origin_develop_roda_a_suite_inteira(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        self.assertEqual(self.roda()[1], TODAS)

    def test_sem_a_ferramenta_roda_a_suite_inteira(self):
        (self.repo / "bin" / "forge-testes").unlink()
        self.commit("sem ferramenta", tests__test_a_py=BOA.format("a") + "# x\n")
        self.assertEqual(self.roda()[1], TODAS)

    def test_ferramenta_que_e_link_roda_a_suite_inteira(self):  # QA A3: metade `! -L` da guarda
        (self.repo / "bin" / "forge-testes").unlink()
        (self.repo / "bin" / "forge-testes.real").write_text((RAIZ / "bin" / "forge-testes").read_text())
        os.symlink("forge-testes.real", self.repo / "bin" / "forge-testes")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "ferramenta vira link")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))  # o link já está na base
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.assertEqual(self.roda()[1], TODAS)

    def test_arvore_suja_entra_no_plano(self):  # os testes rodam na árvore de trabalho: o que ela muda é afetado
        self.commit("novo", novo_txt="x\n")
        (self.repo / "bin" / "forge-sugerir").write_text("x = 9\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)

    def test_arquivo_novo_nao_versionado_entra_no_plano(self):
        self.commit("novo", novo_txt="x\n")
        (self.repo / "tests" / "test_novo.py").write_text(BOA.format("novo"))
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertIn("rodou-novo", marcas)

    def test_diff_que_toca_o_hook_roda_quem_cita_o_hook(self):  # EXERCITAM: .githooks leva quem cita pre-push
        self.commit("leitor do hook", tests__test_a_py=BOA.format("a") + "# lê .githooks/pre-push\n")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("toca o hook", **{".githooks/pre-push": "#!/bin/sh\nexit 0\n"})
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, {"rodou-a"})

    def test_base_e_a_ref_remota_mesmo_com_branch_local_de_mesmo_nome(self):  # seg A3
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.git("update-ref", "refs/heads/origin/develop", self.git("rev-parse", "HEAD"))  # `origin/develop` curto aponta para cá
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS, "a base é refs/remotes/origin/develop, não a branch local ambígua")

    def test_modulo_falso_em_bin_nao_decide_o_plano_nem_a_execucao(self):  # seg A1: Python do hook com `-I`
        falso = "import sys\nprint('forge-testes: dirigido (falso)')\nsys.exit(0)\n"
        self.commit("toca a ferramenta e planta um json falso", bin__forge_sugerir="x = 2\n", bin__json_py=falso)
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS, "o json falso da branch não pode zerar os testes nem mudar o plano")
        self.assertIn("rodando só os testes afetados", erro)

    def test_modulo_falso_ja_na_base_nao_zera_a_execucao_dirigida(self):  # seg A1: o `-I` da execução, não só o do plano
        falso = "import sys\nif '--listar' not in sys.argv:\n    sys.exit(0)\n"
        self.commit("planta o json falso", bin__json_py=falso)
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)
        self.assertIn("rodando só os testes afetados", erro)

    def test_afetados_valem_para_qualquer_branch(self):  # antes, só melhoria/*
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        for destino in ("feature/x", "fix/x", "chore/x"):
            with self.subTest(destino):
                codigo, marcas, erro = self.roda(destino=destino)
                self.assertEqual(codigo, 0, erro)
                self.assertEqual(marcas, AFETADOS)
                self.assertIn("rodando só os testes afetados", erro)

    def test_ancora_e_a_base_comum_com_a_develop_nao_a_ponta_da_develop(self):  # QA A1: mutante `ancora="$base_dev"`
        # A develop andou depois que a branch saiu dela; o diff contra a ponta da develop mostraria o test_a como mudado
        # pela branch. Contra a base comum, não: só os afetados da branch rodam.
        self.git("switch", "-q", "-c", "dev", self.base)
        (self.repo / "tests" / "test_a.py").write_text(BOA.format("a") + "# develop\n")
        self.commit("a develop muda o test_a")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.git("switch", "-q", "melhoria/x")
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)

    def test_commit_enviado_diferente_do_head_entra_no_plano_junto_do_head(self):
        anterior = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.commit("novo", novo_txt="x\n")
        self.assertEqual(self.roda(local=anterior)[1], AFETADOS)

    def test_varias_refs_rodam_a_uniao_dos_afetados(self):
        um = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.git("switch", "-q", "-c", "y", self.base)
        dois = self.commit("leitor", tests__test_a_py=BOA.format("a") + "# y\n")
        self.git("switch", "-q", "melhoria/x")
        entrada = (f"refs/heads/x {um} refs/heads/melhoria/x {ZERO}\nrefs/tags/y {dois} refs/tags/y {ZERO}\n")  # PREPUSH-REFS: uma branch por envio
        codigo, marcas, erro = self.roda(entrada=entrada)
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, TODAS, "a união: o mapa da ferramenta e o módulo de teste mudado na outra ref")
        self.assertIn("rodando só os testes afetados", erro)

    def test_tag_roda_os_afetados(self):
        sha = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.assertEqual(self.roda(entrada=f"refs/tags/v1 {sha} refs/tags/v1 {ZERO}\n")[1], AFETADOS)

    def test_so_remocao_nao_roda_teste(self):
        codigo, marcas, erro = self.roda(entrada=f"(delete) {ZERO} refs/heads/melhoria/velha {self.base}\n")
        self.assertEqual((codigo, marcas), (0, set()), erro)
        self.assertIn("suíte não roda", erro)

    def test_suite_inteira_local_so_com_opt_in(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.env["FORGE_PREPUSH_SUITE"] = "1"
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, TODAS)
        self.assertTrue(self.verde.exists(), "a suíte inteira anota a árvore verde")
        self.env["FORGE_PREPUSH_SUITE"] = "sim"
        codigo, marcas, erro = self.roda()
        self.assertEqual((codigo, marcas), (1, set()))
        self.assertIn("FORGE_PREPUSH_SUITE vale 0", erro)

    def test_bloqueios_de_conteudo_valem_antes_do_filtro(self):
        sha = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        for destino in ("main", "homolog", "develop"):
            with self.subTest(destino):
                codigo, marcas, erro = self.roda(local=sha, destino=destino)
                self.assertEqual(codigo, 1)
                self.assertEqual(marcas, set())
                self.assertIn("bloqueado", erro)
        # histórico reescrito: o remoto tem um commit que o enviado não contém
        self.git("switch", "-q", "-c", "outro", self.base)
        divergente = self.commit("diverge", tests__test_a_py=BOA.format("a") + "# z\n")
        codigo, marcas, erro = self.roda(local=divergente, remoto=sha)
        self.assertEqual(codigo, 1)
        self.assertEqual(marcas, set())
        self.assertIn("não fast-forward", erro)


class ChecagensBaratasAntesDaTrava(Base):
    """PREPUSH-BARATAS: sintaxe, shellcheck e changelog reprovam em segundos, sem entrar na fila nem esperar a trava."""

    def setUp(self):
        super().setUp()
        self.trava = self.run_dir / f"forge-suite-{os.getuid()}.lock"

    def segura_a_trava(self):
        self.trava.touch()
        segurador = subprocess.Popen(["flock", str(self.trava), "sleep", "60"])
        self.addCleanup(segurador.wait)
        self.addCleanup(segurador.terminate)
        for _ in range(100):
            if subprocess.run(["flock", "-n", str(self.trava), "true"]).returncode != 0:
                return
            time.sleep(0.05)
        self.fail("o flock de fora não segurou a trava")

    def reprova_sem_esperar(self, trecho):
        self.segura_a_trava()
        inicio = time.monotonic()
        codigo, marcas, erro = self.roda()
        self.assertEqual((codigo, marcas), (1, set()), erro)
        self.assertIn(trecho, erro)
        self.assertIn("checagens baratas reprovadas", erro)
        self.assertNotIn("pre-push: entrou", erro, "a checagem barata não pode esperar a trava")
        self.assertLess(time.monotonic() - inicio, 15)

    def test_sintaxe_python_reprova_antes_da_trava(self):
        self.commit("quebra", bin__forge_sugerir="x = 2\n", bin__util_py="def f(:\n")
        self.reprova_sem_esperar("erro de sintaxe Python em bin/util.py")

    def test_sintaxe_python_de_script_sem_extensao_pela_primeira_linha(self):
        self.commit("quebra", bin__forge_sugerir="#!/usr/bin/env python3\ndef f(:\n")
        self.reprova_sem_esperar("erro de sintaxe Python em bin/forge-sugerir")

    def test_sintaxe_shell_reprova_antes_da_trava(self):
        self.commit("quebra", bin__forge_sugerir="x = 2\n", **{"scripts/x.sh": "if then\n"})
        self.reprova_sem_esperar("erro de sintaxe shell em scripts/x.sh")

    def test_changelog_com_outro_nome_reprova_antes_da_trava(self):  # o FragmentoTemONomeDaBranch que caía aos 20 min
        shutil.copy(RAIZ / "bin" / "forge-changelog", self.repo / "bin" / "forge-changelog")
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "plugin.json").write_text('{"version": "1.0.0"}\n')
        (self.repo / "CHANGELOG.md").write_text("# Changelog\n\n## [Não publicado]\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "changelog")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("fragmento errado", bin__forge_sugerir="x = 2\n", **{"changelog.d/outro.md": "### Alterado\n- y\n"})
        self.reprova_sem_esperar("CHANGELOG-BRANCH")
        self.git("mv", "changelog.d/outro.md", "changelog.d/x.md")
        self.git("commit", "-q", "-m", "nome certo")
        self.trava.unlink()
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertLess(erro.index("checagens baratas ok"), erro.index("pre-push: entrou"), "barata antes da fila")

    def test_shellcheck_so_dos_scripts_alterados_e_pelo_shebang(self):  # COBERTURA-P6: também o script fora da antiga lista
        if shutil.which("shellcheck") is None:
            self.skipTest("AVISO: shellcheck fora do PATH; o CI roda este passo")
        for arquivo, texto in (("scripts/validar-plugin.sh", "#!/bin/bash\necho $1\n"), ("bin/forge-novo", "#!/usr/bin/env bash\necho $1\n")):
            with self.subTest(arquivo=arquivo):
                self.setUp()  # um repositório novo por caso
                self.commit("script com aviso", **{arquivo: texto})
                self.reprova_sem_esperar(f"shellcheck reprovou ({arquivo})")


class ShellcheckPeloShebang(unittest.TestCase):
    """COBERTURA-P6: o passo shellcheck do CI escolhe os arquivos pelo shebang, com a mesma regra do pre-push."""

    def lista_do_ci(self):
        """Roda o `run:` do passo shellcheck do ci.yml na raiz, com um shellcheck falso que só imprime os arquivos."""
        sys.path.insert(0, str(RAIZ / "tests"))
        from test_ci_local import ci  # noqa: E402  (o leitor de jobs do scripts/ci-local)
        texto = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        (passo,) = [p for j in ci.ler_jobs(texto) for p in j["passos"] if p["nome"].startswith("shellcheck")]
        falso = Path(tempfile.mkdtemp(prefix="shellcheck-falso-"))
        self.addCleanup(shutil.rmtree, falso)
        (falso / "shellcheck").write_text('#!/bin/sh\n[ "$1" = -- ] && shift\nprintf "%s\\n" "$@" > "$SAIDA"\n')
        (falso / "shellcheck").chmod(0o755)
        saida = falso / "saida"
        r = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", passo["run"]], cwd=RAIZ, capture_output=True, text=True,
                           env=dict(os.environ, PATH=f"{falso}:{os.environ['PATH']}", SAIDA=str(saida)))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return saida.read_text().splitlines()

    def test_pega_o_forge_fechar_e_os_pre_push_sem_python(self):
        lista = self.lista_do_ci()
        for nome in ("bin/forge-fechar", ".githooks/pre-push", "templates/projeto/.githooks/pre-push", "bin/forge-init",
                     "tests/e2e-instalacao.sh", "scripts/validar-plugin.sh"):
            self.assertIn(nome, lista)
        self.assertNotIn("bin/forge-check", lista)  # python pelo shebang
        self.assertFalse([n for n in lista if n.endswith(".py")])

    def test_a_mesma_regra_do_pre_push(self):
        texto = HOOK.read_text(encoding="utf-8")
        self.assertNotIn("SHELLCHECK_DO_CI", texto)
        regra = "'#!'*bash*|'#!'*/sh|'#!'*' sh'"
        self.assertIn(regra, texto)
        self.assertIn(regra, (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))


def isca_de_caminho(nome):
    """SENTINELA-CAMINHO-LOCAL: caminho pessoal montado aqui, para o literal nunca estar no fonte (o CI o barraria)."""
    return "/" + "home" + "/" + nome + "/"


class NeutralidadeECaminhoCedo(Base):
    """PARECER-NEUTRALIDADE-CEDO e SENTINELA-CAMINHO-LOCAL (0.43.3): as checagens baratas rodam a neutralidade e o
    scripts/verificar-contribuicao.sh nos arquivos tocados, em segundos e antes da fila e da trava."""
    segura_a_trava = ChecagensBaratasAntesDaTrava.segura_a_trava
    reprova_sem_esperar = ChecagensBaratasAntesDaTrava.reprova_sem_esperar

    def setUp(self):
        super().setUp()
        self.trava = self.run_dir / f"forge-suite-{os.getuid()}.lock"

    def com_neutralidade(self, **muda):
        """tests/config.json com um termo de stack (Zebrinha) e um termo de projeto por hash (zebra), e o detector real."""
        cfg = {"termos_proibidos_hash": [{"tipo": "palavra", "n": 5, "sha256": hashlib.sha256(b"zebra").hexdigest()}],
               "neutralidade_nucleo": {"pastas": ["docs", "bin"], "ignorar": ["docs/qa/"], "termos": [r"\bZebrinha\b"],
                                       "excecoes": {"docs/ok.md": [r"\bZebrinha\b"]}}}
        cfg["neutralidade_nucleo"].update(muda)
        (self.repo / "tests" / "config.json").write_text(json.dumps(cfg))
        shutil.copy(RAIZ / "tests" / "neutralidade.py", self.repo / "tests" / "neutralidade.py")

    def test_stack_no_nucleo_reprova_antes_da_trava(self):
        self.com_neutralidade()
        self.commit("stack", **{"docs/x.md": "use Zebrinha aqui\n"})
        self.reprova_sem_esperar("docs/x.md: stack no núcleo (\\bZebrinha\\b)")

    def test_termo_de_projeto_reprova_sem_imprimir_o_termo(self):
        self.com_neutralidade()
        self.commit("projeto", **{"docs/y.md": "a Zebra do cliente\n"})
        self.reprova_sem_esperar("docs/y.md: termo de projeto")
        _, _, erro = self.roda()
        self.assertNotIn("zebra", erro.lower())

    def test_excecao_pasta_ignorada_e_arquivo_fora_do_nucleo_passam(self):
        self.com_neutralidade()
        self.commit("ok", **{"docs/ok.md": "Zebrinha\n", "docs/qa/r.md": "Zebrinha\n", "outro/z.md": "Zebrinha zebra\n"})
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("neutralidade reprovada", erro)

    def test_so_os_arquivos_tocados_sao_lidos(self):  # o arquivo velho com o termo fica para o CI, que roda as classes inteiras
        self.com_neutralidade()
        self.commit("velho", **{"docs/velho.md": "Zebrinha\n"})
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("novo", **{"docs/novo.md": "nada\n"})
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)

    def test_caminho_pessoal_no_delta_reprova_pelo_script_da_arvore_sem_imprimir_o_caminho(self):
        isca = isca_de_caminho("fulano")
        (self.repo / "scripts").mkdir()
        shutil.copy(RAIZ / "scripts" / "verificar-contribuicao.sh", self.repo / "scripts" / "verificar-contribuicao.sh")
        self.commit("pessoal", **{"docs/p.md": f"veja {isca}notas\n"})  # a base não tem o script: só a checagem barata o roda
        self.reprova_sem_esperar("docs/p.md:1: caminho pessoal")
        _, _, erro = self.roda()
        self.assertIn("scripts/verificar-contribuicao.sh reprovou o delta", erro)
        self.assertNotIn(isca, erro)

    def test_caminho_pessoal_marcado_como_exemplo_passa(self):
        (self.repo / "scripts").mkdir()
        shutil.copy(RAIZ / "scripts" / "verificar-contribuicao.sh", self.repo / "scripts" / "verificar-contribuicao.sh")
        self.commit("exemplo", **{"docs/e.md": f"veja {isca_de_caminho('fulano')}notas forge:exemplo\n"})
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)


class NaoRecuaDoHook(unittest.TestCase):
    """O texto do hook guarda a falha fechada que os testes acima exercitam."""

    def test_o_hook_cita_o_forge_testes_e_o_recuo_para_a_suite_inteira(self):
        texto = HOOK.read_text(encoding="utf-8")
        self.assertIn("bin/forge-testes", texto)
        self.assertIn("python3 scripts/suite-paralela.py", texto)  # o recuo continua a suíte inteira em paralelo
        self.assertIn("discover -s tests", texto)
        for trecho in ("FORGE_ENTRADA=suite FORGE_SUITE_TRAVA", "FORGE_ENTRADA=push python3 -I", "FORGE_ENTRADA=push FORGE_SUITE_TRAVA"):
            self.assertIn(trecho, texto)  # MAQ-A7: a linha do testes.log diz quem lançou
        self.assertIn('FORGE_PREPUSH_SUITE:-0', texto)  # SUITE-NO-CI: a suíte inteira local só com opt-in
        self.assertIn("--afetados", texto)
        # PREPUSH-BARATAS: as checagens baratas vêm antes da fila e da trava no texto do hook.
        self.assertLess(texto.index("\n  checagens_baratas || "), texto.index('echo "pre-push: entrou'))


if __name__ == "__main__":
    unittest.main()
