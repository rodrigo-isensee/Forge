"""EST-M8: o pre-push roda só os testes afetados pelo mapa do `bin/forge-testes`; a suíte completa fica no CI do PR.

Cada teste roda o hook de verdade num repositório descartável com três suítes mínimas (`test_sugerir` e `test_forge`,
os módulos que o mapa dá a `bin/forge-sugerir`, e `test_a`, que o mapa não cita), cada uma deixando uma marca
`rodou-<nome>`, a cópia do `bin/forge-testes` e uma `origin/develop` local como base. Opção C do M8: módulo de teste
mudado no diff roda a suíte inteira, então o envio dirigido do brinquedo muda `bin/forge-sugerir`. Classe do defeito:
o portão rodar mais do que o afetado (ou, pior, menos do que o seguro). Variantes: caminho mapeado (só os módulos do
mapa), só módulo de teste mudado (suíte inteira e árvore verde), caminho sem mapa, sem base, sem a ferramenta, mais de
uma ref, árvore suja, HEAD diferente do enviado, falha no módulo afetado, falha em módulo não afetado, bloqueios de
conteúdo, e a prova de árvore verde (só a suíte completa anota).
"""
import os
import shutil
import subprocess
import sys
import tempfile
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


class PrePushAfetados(unittest.TestCase):
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
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), FORGE_TRAVA_ESPERA="20")
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

    def test_so_os_modulos_do_mapa_rodam_e_nao_anotam_a_arvore_verde(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)
        self.assertIn("rodando só os testes afetados", erro)
        self.assertFalse(self.verde.exists(), "só a suíte completa anota a prova de árvore verde")

    def test_so_modulo_de_teste_mudado_roda_a_suite_inteira_e_anota(self):  # opção C, item 6 do critério de fim
        self.commit("toca o teste a", tests__test_a_py=BOA.format("a") + "# x\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, TODAS)
        self.assertNotIn("rodando só os testes afetados", erro)
        self.assertTrue(self.verde.exists(), "a suíte inteira anota a árvore verde")

    def test_falha_em_modulo_nao_afetado_nao_barra_e_no_afetado_barra(self):
        self.commit("a quebra", tests__test_a_py=RUIM.format("a"))
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))  # a quebra já está na base
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.assertEqual(self.roda()[0], 0, "test_a, que o mapa não cita,, não roda")
        self.commit("ferramenta quebra o modulo afetado", bin__forge_sugerir="QUEBRA\n")
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("testes do Forge falharam", erro)

    def test_caminho_sem_mapa_roda_a_suite_inteira_e_anota(self):
        self.commit("novo", novo_txt="x\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, TODAS)
        self.assertTrue(self.verde.exists())

    def test_sem_a_base_origin_develop_roda_a_suite_inteira(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        self.assertEqual(self.roda()[1], TODAS)

    def test_sem_a_ferramenta_roda_a_suite_inteira(self):
        (self.repo / "bin" / "forge-testes").unlink()
        self.commit("sem ferramenta", tests__test_a_py=BOA.format("a") + "# x\n")
        self.assertEqual(self.roda()[1], TODAS)

    def test_arvore_suja_roda_a_suite_inteira(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        (self.repo / "sujo.txt").write_text("x")
        self.assertEqual(self.roda()[1], TODAS)

    def test_arvore_suja_com_arquivo_mapeado_nao_vira_envio_dirigido(self):  # QA A1: mutante da guarda de árvore limpa
        # O plano com o arquivo mapeado sujo é o mesmo dirigido (rodaria só os módulos do mapa); o que prova a guarda é o
        # caminho tomado: com a árvore suja o envio não é o dirigido e roda tudo.
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        (self.repo / "bin" / "forge-sugerir").write_text("x = 9\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, TODAS)
        self.assertNotIn("rodando só os testes afetados", erro)

    def test_ferramenta_que_e_link_roda_a_suite_inteira(self):  # QA A3: metade `! -L` da guarda
        (self.repo / "bin" / "forge-testes").unlink()
        (self.repo / "bin" / "forge-testes.real").write_text((RAIZ / "bin" / "forge-testes").read_text())
        os.symlink("forge-testes.real", self.repo / "bin" / "forge-testes")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "ferramenta vira link")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))  # o link já está na base
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.assertEqual(self.roda()[1], TODAS)

    def permissiva(self):
        """Uma cópia do forge-testes que manda tudo para `test_a` e não altera o mapa: o que um diff mal-intencionado faria."""
        texto = (RAIZ / "bin" / "forge-testes").read_text()
        texto = texto.replace("ALTERA_O_MAPA = {", "ALTERA_O_MAPA = set(); _NAO_USADO = {", 1)
        texto = texto.replace("MAPA = [\n", 'MAPA = [\n    (r".*", ("test_a",)),\n', 1)
        self.assertIn('(r".*", ("test_a",))', texto)
        return texto

    def test_diff_que_toca_o_filtro_o_mapa_ou_o_hook_roda_a_suite_inteira(self):  # seg A2
        (self.repo / "bin" / "forge-testes").write_text(self.permissiva())
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "filtro permissivo")
        base_pos_filtro = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/develop", base_pos_filtro)
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.assertEqual(self.roda()[1], {"rodou-a"}, "controle: o filtro permissivo manda tudo para test_a")
        casos = {"bin/forge-testes": self.permissiva() + "# y\n", "tests/config.json": "{}\n", ".githooks/pre-push": "#!/bin/sh\n"}
        for caminho, texto in casos.items():
            with self.subTest(caminho):
                self.git("reset", "-q", "--hard", base_pos_filtro)
                alvo = self.repo / caminho
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_text(texto)
                self.git("add", "-A")
                self.git("commit", "-q", "-m", f"toca {caminho}")
                self.assertEqual(self.roda()[1], TODAS)

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
        self.assertEqual(marcas, TODAS, "o json falso da branch não pode zerar os testes; bin/json.py não tem regra, o plano real é a suíte inteira")
        self.assertNotIn("rodando só os testes afetados", erro, "o plano falso não pode virar o envio dirigido")

    def test_modulo_falso_ja_na_base_nao_zera_a_execucao_dirigida(self):  # seg A1: o `-I` da execução, não só o do plano
        # O falso mente só na execução (sem `--listar`): fica na base, fora do diff, então o plano real é o dirigido.
        falso = "import sys\nif '--listar' not in sys.argv:\n    sys.exit(0)\n"
        self.commit("planta o json falso", bin__json_py=falso)
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)
        self.assertIn("rodando só os testes afetados", erro)

    def test_dirigido_so_vale_para_melhoria(self):  # review A2: o resto cai na suíte inteira
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        for destino in ("feature/x", "fix/x", "chore/x"):
            with self.subTest(destino):
                codigo, marcas, erro = self.roda(destino=destino)
                self.assertEqual(codigo, 0, erro)
                self.assertEqual(marcas, TODAS)
                self.assertNotIn("rodando só os testes afetados", erro)

    def test_ancora_e_a_base_comum_com_a_develop_nao_a_ponta_da_develop(self):  # QA A1: mutante `ancora="$base_dev"`
        # A develop andou depois que a branch saiu dela e agora tem um arquivo vigiado novo; o diff contra a ponta da
        # develop o mostraria como mudado pela branch. O diff contra a base comum não: o envio segue dirigido.
        self.git("switch", "-q", "-c", "dev", self.base)
        self.commit("a develop muda o mapa", tests__config_json="{}\n")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))
        self.git("switch", "-q", "melhoria/x")
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)
        self.assertIn("rodando só os testes afetados", erro)

    def test_commit_enviado_diferente_do_head_roda_a_suite_inteira(self):
        anterior = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        self.commit("toca a ferramenta de novo", bin__forge_sugerir="x = 3\n")
        self.assertEqual(self.roda(local=anterior)[1], TODAS)

    def test_varias_refs_rodam_a_suite_inteira(self):
        sha = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        entrada = (f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\nrefs/heads/y {sha} refs/heads/melhoria/y {ZERO}\n")
        self.assertEqual(self.roda(entrada=entrada)[1], TODAS)

    def test_ref_que_nao_e_branch_roda_a_suite_inteira(self):
        sha = self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        entrada = f"refs/tags/v1 {sha} refs/tags/v1 {ZERO}\n"
        self.assertEqual(self.roda(entrada=entrada)[1], TODAS)

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


class NaoRecuaDoHook(unittest.TestCase):
    """O texto do hook guarda a falha fechada que os testes acima exercitam."""

    def test_o_hook_cita_o_forge_testes_e_o_recuo_para_a_suite_inteira(self):
        texto = HOOK.read_text(encoding="utf-8")
        self.assertIn("bin/forge-testes", texto)
        self.assertIn("python3 scripts/suite-paralela.py", texto)  # o recuo continua a suíte inteira em paralelo
        self.assertIn("discover -s tests", texto)


if __name__ == "__main__":
    unittest.main()
