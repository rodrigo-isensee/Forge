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
        entrada = (f"refs/heads/x {um} refs/heads/melhoria/x {ZERO}\nrefs/heads/y {dois} refs/heads/melhoria/y {ZERO}\n")
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

    def test_shellcheck_so_dos_scripts_do_ci_alterados(self):
        if shutil.which("shellcheck") is None:
            self.skipTest("AVISO: shellcheck fora do PATH; o CI roda este passo")
        self.commit("script do ci com aviso", **{"scripts/validar-plugin.sh": "#!/bin/bash\necho $1\n"})
        self.reprova_sem_esperar("shellcheck reprovou (scripts/validar-plugin.sh)")


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
