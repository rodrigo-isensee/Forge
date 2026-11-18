"""PP1 (E2.321): o patch `docs/devops/pp1-pre-push.patch` do `.githooks/pre-push`, provado à parte.

O `.githooks/pre-push` em vigor não muda neste pedido: o teste copia o hook para $TMPDIR, aplica o patch na cópia e prova cada
conserto, com o hook original falhando e o remendado passando (PRE-PUSH-TEXTO-TRAVA-FD, FILA-INTERVALO-ZERO,
PREPUSH-LEVE-COBERTURA-CATRACA, PREPUSH-INDICE-E-PULOS). Depois que o dono aplicar o patch, o hook em vigor já é o remendado e `git apply` do patch
recusa de novo: o teste então confere só o remendado e pula a comparação com o original.
"""
import os
import re
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
PATCH = RAIZ / "docs" / "devops" / "pp1-pre-push.patch"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})
ZERO = "0" * 40
SEGURA = "import fcntl, sys, time\nf = open(sys.argv[1], 'a')\nfcntl.flock(f, fcntl.LOCK_EX)\nprint('pronto', flush=True)\ntime.sleep(600)\n"
SUITE_VERDE = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n"


def aplicado(texto):
    return "PRE-PUSH-TEXTO-TRAVA-FD" in texto


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        raiz = Path(cls._tmp.name)
        orig, novo = raiz / "orig" / ".githooks", raiz / "novo" / ".githooks"
        for pasta in (orig, novo):
            pasta.mkdir(parents=True)
        texto = HOOK.read_text(encoding="utf-8")
        cls.em_vigor_remendado = aplicado(texto)
        if cls.em_vigor_remendado:  # o dono já aplicou: só o remendado existe
            shutil.copy2(HOOK, novo / "pre-push")
            cls.originais = []
        else:
            shutil.copy2(HOOK, orig / "pre-push")
            shutil.copy2(HOOK, novo / "pre-push")
            r = subprocess.run(["git", "apply", str(PATCH)], cwd=raiz / "novo", env=AMBIENTE, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            cls.originais = [orig / "pre-push"]
        cls.remendado = novo / "pre-push"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def hooks(self):
        """(rótulo, caminho, deve_ter_o_conserto): o original falha, o remendado passa."""
        return [("original", h, False) for h in self.originais] + [("remendado", self.remendado, True)]


class PatchAplica(Base):
    def test_patch_so_toca_o_pre_push_e_aplica_limpo_na_develop(self):
        texto = PATCH.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^diff --git (\S+) (\S+)$", texto, re.M), [("a/.githooks/pre-push", "b/.githooks/pre-push")])
        if not self.em_vigor_remendado:
            self.assertTrue(self.originais[0].exists())
        r = subprocess.run(["bash", "-n", str(self.remendado)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.access(self.remendado, os.X_OK), "o patch tem de manter o modo executável")


class TextoDaTravaPorFd(Base):
    """PRE-PUSH-TEXTO-TRAVA-FD: a leitura vale para o arquivo aberto no fd 9, não para o que o caminho aponta depois."""

    def funcao(self, hook):
        m = re.search(r"^texto_da_trava\(\) \{\n.*?^\}\n", hook.read_text(encoding="utf-8"), re.M | re.S)
        self.assertIsNotNone(m)
        return m.group(0)

    def le(self, hook, fd_aberto=True):
        with tempfile.TemporaryDirectory() as t:
            pasta = Path(t)
            (pasta / "aberta").write_text("pid 1 ns 2 desde dono-do-fd\n")
            (pasta / "desviada").write_text("TEXTO-DE-OUTRO-ARQUIVO\n")
            (pasta / "trava").symlink_to(pasta / "desviada")  # o caminho foi trocado depois da conferência
            abre = f'exec 9<"{pasta / "aberta"}"; ' if fd_aberto else ""
            script = f'trava="{pasta / "trava"}"; {self.funcao(hook)}\n{abre}texto_da_trava'
            r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=AMBIENTE)
            return r.returncode, r.stdout

    def test_le_o_arquivo_do_descritor_e_nao_o_do_caminho(self):
        for rotulo, hook, conserto in self.hooks():
            with self.subTest(rotulo):
                _, saida = self.le(hook)
                if conserto:
                    self.assertIn("dono-do-fd", saida)
                    self.assertNotIn("OUTRO-ARQUIVO", saida)
                else:
                    self.assertIn("OUTRO-ARQUIVO", saida, "sem o patch o caminho desviado é lido")

    def test_sem_descritor_o_texto_sai_vazio_e_sem_erro(self):
        codigo, saida = self.le(self.remendado, fd_aberto=False)
        self.assertEqual((codigo, saida), (0, ""))

    def test_continua_limitado_a_200_bytes_sem_controle(self):
        with tempfile.TemporaryDirectory() as t:
            trava = Path(t) / "trava"
            trava.write_bytes(b"\x1b]0;x\x07" + b"A" * 5000)
            script = f'trava="{trava}"; {self.funcao(self.remendado)}\nexec 9<"{trava}"; texto_da_trava'
            r = subprocess.run(["bash", "-c", script], capture_output=True, env=AMBIENTE)
        self.assertNotIn(b"\x1b", r.stdout)
        self.assertNotIn(b"\x07", r.stdout)
        self.assertLessEqual(len(r.stdout), 200)


class IntervaloDaFila(Base):
    """FILA-INTERVALO-ZERO: 0 imprimia a fila a cada 0,2 s; agora é recusado como o valor inválido."""

    def roda(self, hook, valor):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            (base / "run").mkdir()
            (base / "repo" / "tests").mkdir(parents=True)
            (base / "repo" / "tests" / "test_a.py").write_text(SUITE_VERDE)
            subprocess.run(["git", "init", "-q", str(base / "repo")], check=True, env=AMBIENTE)
            env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"), FORGE_TRAVA_ESPERA="5",
                       FORGE_FILA_INTERVALO=valor)
            r = subprocess.run([str(hook), "--suite"], cwd=base / "repo", env=env, capture_output=True, text=True, timeout=120)
            return r.returncode, r.stderr

    def test_zero_e_zeros_sao_recusados(self):
        for rotulo, hook, conserto in self.hooks():
            for valor in ("0", "00", "000"):
                with self.subTest(rotulo, valor=valor):
                    codigo, erro = self.roda(hook, valor)
                    if conserto:
                        self.assertEqual(codigo, 1, erro)
                        self.assertIn("FORGE_FILA_INTERVALO deve ser um número de segundos inteiro maior que zero", erro)
                        self.assertNotIn("pre-push: entrou", erro)  # recusado antes de entrar na fila
                    else:
                        self.assertEqual(codigo, 0, "sem o patch o 0 é aceito e a suíte roda")

    def test_zeros_a_esquerda_em_base_dez_sao_aceitos(self):
        """A1 do QA (mutante M3, `$((10#$intervalo))` -> `$((intervalo))`): "08" e "09" não são octal inválido."""
        for valor in ("08", "09", "010"):
            with self.subTest(valor=valor):
                codigo, erro = self.roda(self.remendado, valor)
                self.assertEqual(codigo, 0, erro)
                self.assertNotIn("maior que zero", erro)
                self.assertNotIn("value too great", erro)

    def test_conta_da_espera_usa_o_valor_decimal(self):
        """Com a trava presa, "08" entra na espera (a_cada_intervalo soma 8 s) e o envio é barrado só pelo tempo, sem erro de base."""
        for valor in ("08", "09"):
            with self.subTest(valor=valor), tempfile.TemporaryDirectory() as t:
                base = Path(t)
                (base / "run").mkdir()
                (base / "repo" / "tests").mkdir(parents=True)
                (base / "repo" / "tests" / "test_a.py").write_text(SUITE_VERDE)
                subprocess.run(["git", "init", "-q", str(base / "repo")], check=True, env=AMBIENTE)
                trava = base / "run" / f"forge-suite-{os.getuid()}.lock"
                dona = subprocess.Popen([sys.executable, "-I", "-c", SEGURA, str(trava)], stdout=subprocess.PIPE, text=True)
                self.addCleanup(lambda d=dona: (d.kill(), d.wait(), d.stdout.close()))
                self.assertEqual(dona.stdout.readline().strip(), "pronto")
                env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"), FORGE_TRAVA_ESPERA="2",
                           FORGE_FILA_INTERVALO=valor)
                r = subprocess.run([str(self.remendado), "--suite"], cwd=base / "repo", env=env, capture_output=True, text=True, timeout=120)
                self.assertEqual(r.returncode, 1, r.stderr)
                self.assertIn("a vez não chegou em 2 s", r.stderr)
                self.assertEqual(r.stderr.count("fila da suíte"), 1, r.stderr)  # só a linha da entrada: o próximo só em 8 ou 9 s
                self.assertNotIn("value too great", r.stderr)

    def test_invalido_segue_recusado_e_o_valor_bom_passa(self):
        for valor, esperado in (("1m", 1), ("-1", 1), ("", 1), ("1", 0), ("60", 0)):
            with self.subTest(valor=valor):
                codigo, erro = self.roda(self.remendado, valor)
                if valor == "":  # vazio cai no padrão da expansão ${...:-60}
                    esperado = 0
                self.assertEqual(codigo, esperado, erro)


class CoberturaDaCatraca(Base):
    """PREPUSH-LEVE-COBERTURA-CATRACA: o envio leve reprova condição mudada em Python de controle sem mutante declarado."""

    def repo(self, base):
        repo = base / "repo"
        (repo / "bin").mkdir(parents=True)
        (repo / "hooks").mkdir()
        (repo / "tests").mkdir()
        for nome in ("forge-mutante", "forge_apoio_testes.py", "forge-check"):  # o forge-mutante carrega o apoio; o filtro, o forge-check
            shutil.copy(RAIZ / "bin" / nome, repo / "bin" / nome)
        for nome in ("catraca.py", "neutralidade.py"):  # o filtro importa a catraca (a lista da classe C)
            shutil.copy(RAIZ / "tests" / nome, repo / "tests" / nome)
        (repo / "bin" / "x.py").write_text("def g(a, b):\n    if a:\n        return 1\n    return 0\n")
        (repo / "hooks" / "_comum.py").write_text("def h(a):\n    return a\n")
        (repo / "hooks" / "h.py").write_text("def f(a, b):\n    if a:\n        return 1\n    return 0\n")
        (repo / "tests" / "test_a.py").write_text(SUITE_VERDE)

        def git(*args):
            r = subprocess.run(["git", *args], cwd=repo, env=AMBIENTE, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r.stdout.strip()

        git("init", "-q", "-b", "melhoria/x")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "t")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        git("update-ref", "refs/remotes/origin/develop", "HEAD")
        return repo, git

    def roda(self, hook, mudanca):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            (base / "run").mkdir()
            repo, git = self.repo(base)
            for nome, texto in mudanca.items():
                (repo / nome).parent.mkdir(parents=True, exist_ok=True)
                (repo / nome).write_text(texto)
            git("add", "-A")
            git("commit", "-q", "-m", "muda")
            sha = git("rev-parse", "HEAD")
            env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"))
            r = subprocess.run([str(hook), "origin", "u"], cwd=repo, env=env, capture_output=True, text=True, timeout=120,
                               input=f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\n")
            return r.returncode, r.stderr

    def test_condicao_mudada_em_codigo_de_controle_sem_mutante_reprova(self):
        for rotulo, hook, conserto in self.hooks():
            with self.subTest(rotulo):
                codigo, erro = self.roda(hook, {"hooks/h.py": "def f(a, b):\n    if a and b:\n        return 1\n    return 0\n"})
                if conserto:
                    self.assertEqual(codigo, 1, erro)
                    self.assertIn("forge-mutante --cobertura reprovou", erro)
                    self.assertIn("sem mutante", erro)  # a análise rodou de verdade (não foi um erro da ferramenta)
                    self.assertNotIn("Traceback", erro)
                else:
                    self.assertEqual(codigo, 0, "sem o patch só o CI pega")

    def test_condicao_fora_de_hooks_tambem_reprova(self):
        codigo, erro = self.roda(self.remendado, {"bin/x.py": "def g(a, b):\n    if a or b:\n        return 1\n    return 0\n"})
        self.assertEqual(codigo, 1, erro)
        self.assertIn("sem mutante · bin/x.py", erro)

    def test_condicao_em_teste_nao_barra_porque_a_catraca_exclui_testes(self):
        """A1 do review: comentário em hooks/_comum.py e condição em tests/catraca.py; a catraca do CI aceita, o envio leve também."""
        catraca = (RAIZ / "tests" / "catraca.py").read_text(encoding="utf-8")
        mudanca = {"hooks/_comum.py": "# nota\ndef h(a):\n    return a\n", "tests/catraca.py": catraca + "\nif 1 and 2:\n    pass\n"}
        codigo, erro = self.roda(self.remendado, mudanca)
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("reprovou", erro)

    def test_so_a_falta_em_teste_com_falta_de_controle_ainda_reprova(self):
        catraca = (RAIZ / "tests" / "catraca.py").read_text(encoding="utf-8")
        mudanca = {"hooks/h.py": "def f(a, b):\n    if a and b:\n        return 1\n    return 0\n", "tests/catraca.py": catraca + "\nif 1 and 2:\n    pass\n"}
        codigo, erro = self.roda(self.remendado, mudanca)
        self.assertEqual(codigo, 1, erro)
        self.assertIn("sem mutante · hooks/h.py", erro)
        self.assertNotIn("tests/catraca.py", erro.split("pre-push: bin/forge-mutante")[0])

    def test_forge_check_que_e_link_nao_roda_a_checagem(self):
        """A2 da segurança: a guarda confere que o forge-check de bin não é link, como as vizinhas; com link, a checagem não roda."""
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            (base / "run").mkdir()
            repo, git = self.repo(base)
            nome = "forge-check"
            verificador = repo / "bin" / nome
            verificador.rename(repo / "bin" / "alvo-do-link")  # o link aponta para a cópia dentro do repo
            verificador.symlink_to("alvo-do-link")
            (repo / "hooks" / "h.py").write_text("def f(a, b):\n    if a and b:\n        return 1\n    return 0\n")
            git("add", "-A")
            git("commit", "-q", "-m", "muda")
            sha = git("rev-parse", "HEAD")
            env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"))
            r = subprocess.run([str(self.remendado), "origin", "u"], cwd=repo, env=env, capture_output=True, text=True, timeout=120,
                               input=f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("forge-mutante --cobertura", r.stderr)

    def test_saida_2_da_ferramenta_e_so_aviso(self):
        codigo, erro = self.roda(self.remendado, {"hooks/h.py": "def f(a, b):\n    return 1\n", "tests/mutantes/x.json": "{"})
        self.assertEqual(codigo, 0, erro)
        self.assertIn("aviso: bin/forge-mutante --cobertura não conferiu o delta (saída 2)", erro)

    def test_mudanca_sem_condicao_ou_fora_do_controle_passa(self):
        casos = {
            "sem condição": {"hooks/h.py": "def f(a, b):\n    if a:\n        return 2\n    return 0\n"},
            "fora do controle": {"docs.py": "if 1 and 2:\n    pass\n"},
        }
        for nome, mudanca in casos.items():
            with self.subTest(nome):
                codigo, erro = self.roda(self.remendado, mudanca)
                self.assertEqual(codigo, 0, erro)
                self.assertNotIn("forge-mutante --cobertura", erro)


class IndiceEPulos(Base):
    """PREPUSH-INDICE-E-PULOS: o envio leve confere o índice das fixtures e barra teste pulado novo em tests/."""

    FIXTURE = '{"descricao": "caso novo", "esperado": {"codigo": 2}}\n'

    def repo(self, base):
        repo = base / "repo"
        for pasta in ("scripts", "tests/hooks/h", "docs"):
            (repo / pasta).mkdir(parents=True)
        shutil.copy(RAIZ / "scripts" / "indice-fixtures.py", repo / "scripts" / "indice-fixtures.py")
        for nome in ("catraca.py", "neutralidade.py", "config.json"):
            shutil.copy(RAIZ / "tests" / nome, repo / "tests" / nome)
        (repo / "tests" / "hooks" / "h" / "a-1.json").write_text(self.FIXTURE)
        (repo / "tests" / "test_a.py").write_text(SUITE_VERDE)

        def git(*args):
            r = subprocess.run(["git", *args], cwd=repo, env=AMBIENTE, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r.stdout.strip()

        subprocess.run([sys.executable, "-I", "scripts/indice-fixtures.py"], cwd=repo, env=AMBIENTE, check=True, capture_output=True)
        git("init", "-q", "-b", "melhoria/x")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "t")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        git("update-ref", "refs/remotes/origin/develop", "HEAD")
        return repo, git

    def roda(self, hook, mudanca, regera=False):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            (base / "run").mkdir()
            repo, git = self.repo(base)
            for nome, texto in mudanca.items():
                (repo / nome).parent.mkdir(parents=True, exist_ok=True)
                (repo / nome).write_text(texto)
            if regera:
                subprocess.run([sys.executable, "-I", "scripts/indice-fixtures.py"], cwd=repo, env=AMBIENTE, check=True, capture_output=True)
            git("add", "-A")
            git("commit", "-q", "-m", "muda")
            sha = git("rev-parse", "HEAD")
            env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"))
            r = subprocess.run([str(hook), "origin", "u"], cwd=repo, env=env, capture_output=True, text=True, timeout=120,
                               input=f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\n")
            return r.returncode, r.stderr

    def test_fixture_nova_sem_regerar_o_indice_reprova(self):
        for rotulo, hook, conserto in self.hooks():
            with self.subTest(rotulo):
                codigo, erro = self.roda(hook, {"tests/hooks/h/b-1.json": self.FIXTURE})
                if conserto:
                    self.assertEqual(codigo, 1, erro)
                    self.assertIn("docs/hooks-fixtures.md: desatualizado", erro)
                    self.assertIn("docs/hooks-fixtures.md desatualizado (o CI reprova igual)", erro)
                else:
                    self.assertEqual(codigo, 0, "sem o patch só o CI pega")

    def test_fixture_nova_com_o_indice_regerado_passa(self):
        codigo, erro = self.roda(self.remendado, {"tests/hooks/h/b-1.json": self.FIXTURE}, regera=True)
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("hooks-fixtures", erro)

    def test_mudanca_fora_do_corpus_nao_roda_o_indice(self):
        codigo, erro = self.roda(self.remendado, {"docs/x.md": "x\n"})
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("hooks-fixtures", erro)

    def test_skip_novo_em_teste_reprova(self):
        pulado = SUITE_VERDE.replace("        pass\n", '        self.skipTest("depois")\n')
        for rotulo, hook, conserto in self.hooks():
            with self.subTest(rotulo):
                codigo, erro = self.roda(hook, {"tests/test_a.py": pulado})
                if conserto:
                    self.assertEqual(codigo, 1, erro)
                    self.assertIn("subiram de 0 para 1", erro)
                    self.assertIn("teste pulado novo em tests/", erro)
                else:
                    self.assertEqual(codigo, 0, "sem o patch só o CI pega")

    def test_decoradores_de_pulo_tambem_contam(self):
        for decorador in ("@unittest.skip('x')", "@unittest.skipIf(True, 'x')", "@unittest.skipUnless(False, 'x')", "@unittest.expectedFailure"):
            with self.subTest(decorador):
                texto = SUITE_VERDE.replace("    def test_a", f"    {decorador}\n    def test_a")
                codigo, erro = self.roda(self.remendado, {"tests/test_a.py": texto})
                self.assertEqual(codigo, 1, erro)

    def test_pulo_que_ja_existia_ou_so_citado_em_texto_ou_na_catraca_passa(self):
        casos = {
            "só citado em texto": {"tests/test_a.py": SUITE_VERDE + '\nNOTA = "usa skipTest e skipIf"\n'},
            "na catraca (a conta exclui)": {"tests/catraca.py": (RAIZ / "tests" / "catraca.py").read_text(encoding="utf-8") + "\nx = 1\n"},
            "fora de tests/": {"docs.py": "def t(s):\n    s.skipTest('x')\n"},
        }
        for nome, mudanca in casos.items():
            with self.subTest(nome):
                codigo, erro = self.roda(self.remendado, mudanca)
                self.assertEqual(codigo, 0, erro)
                self.assertNotIn("teste pulado", erro)


    def test_skip_novo_na_propria_catraca_nao_barra(self):
        """A2 do QA (mutante M11, soltar `a != "tests/catraca.py"`): a conta da catraca exclui a própria catraca."""
        catraca = (RAIZ / "tests" / "catraca.py").read_text(encoding="utf-8")
        texto = catraca + "\nimport unittest\nclass TX(unittest.TestCase):\n    def test_x(self):\n        self.skipTest('x')\n"
        codigo, erro = self.roda(self.remendado, {"tests/catraca.py": texto})
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("teste pulado", erro)

    def test_skip_novo_fora_de_tests_nao_barra(self):
        """A2 do QA (mutante M12, soltar `startswith("tests/")`): x.py com skip fora de tests/ não conta."""
        fora = SUITE_VERDE.replace("        pass\n", '        self.skipTest("depois")\n')
        mudanca = {"x.py": fora, "bin/y.py": fora, "tests/fora.txt": "x\n"}
        codigo, erro = self.roda(self.remendado, mudanca)
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("teste pulado", erro)
        codigo, erro = self.roda(self.remendado, {"x.py": fora, "tests/test_a.py": SUITE_VERDE.replace("        pass\n", '        self.skipTest("d")\n')})
        self.assertEqual(codigo, 1, erro)  # o mesmo envio com skip em tests/ continua barrado
        self.assertIn("subiram de 0 para 1", erro)  # e o x.py fora de tests/ não somou


if __name__ == "__main__":
    unittest.main()
