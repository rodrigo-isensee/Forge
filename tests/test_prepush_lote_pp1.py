"""Lote PP1 (v0478 E94.1): os cinco consertos do `.githooks/pre-push` do Forge, provados pela proposta.

O hook é travado (só o dono grava): a correção mora no bloco `diff` de `docs/propostas/prepush-lote-pp1.md`. Cada teste
aplica esse bloco numa cópia temporária do hook e roda a cópia direto, num repositório descartável e com o ambiente
limpo; o hook de hoje é o mutante (falha onde o remendado passa). Com o patch já aplicado pelo dono, o hook em vigor é o
remendado e o teste confere só ele. Cartões: PRE-PUSH-TEXTO-TRAVA-FD, FILA-INTERVALO-ZERO, PREPUSH-LEVE-COBERTURA-CATRACA,
PREPUSH-INDICE-E-PULOS e PREPUSH-FORGE-AVISO-LISTA-VAZIA.
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
from ambiente_git import sem_git_herdado  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
PROPOSTA = RAIZ / "docs" / "propostas" / "prepush-lote-pp1.md"
# Só o que o hook precisa: nada de GIT_* nem FORGE_* de quem roda a suíte (AR-4); HOME e a pasta da trava vêm por teste.
AMBIENTE = sem_git_herdado({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C.UTF-8"},
                           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0",
                           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
ZERO = "0" * 40
SEGURA = "import fcntl, sys, time\nf = open(sys.argv[1], 'a')\nfcntl.flock(f, fcntl.LOCK_EX)\nprint('pronto', flush=True)\ntime.sleep(600)\n"
SUITE_VERDE = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n"


def diff_da_proposta():
    """O bloco ```diff da proposta (um só), o texto que o dono passa ao `git apply`."""
    linhas = PROPOSTA.read_text(encoding="utf-8").splitlines(keepends=True)
    inicio = linhas.index("```diff\n") + 1
    return "".join(linhas[inicio:linhas.index("```\n", inicio)])


def rodar(cmd, cwd, env=None, entrada=None, prazo=120):
    return subprocess.run(cmd, cwd=cwd, env=env or AMBIENTE, input=entrada, capture_output=True, text=True, timeout=prazo)


def fazenda(pasta, sem, falso=False):
    """Pasta de links para todo programa do PATH, menos `sem` (ou, com `falso`, `sem` vira um programa que sai com 2)."""
    pasta.mkdir()
    for d in AMBIENTE["PATH"].split(os.pathsep):
        if not os.path.isdir(d):
            continue
        for nome in os.listdir(d):
            alvo = os.path.join(d, nome)
            if nome != sem and not (pasta / nome).exists() and os.access(alvo, os.X_OK) and os.path.isfile(alvo):
                (pasta / nome).symlink_to(alvo)
    if falso:
        (pasta / sem).write_text("#!/bin/sh\nexit 2\n")
        (pasta / sem).chmod(0o755)
    return str(pasta)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="forge-lote-pp1-")
        raiz = Path(cls._tmp.name)
        for nome in ("orig", "novo"):
            (raiz / nome / ".githooks").mkdir(parents=True)
            shutil.copy2(HOOK, raiz / nome / ".githooks" / "pre-push")
        novo = raiz / "novo"
        rodar(["git", "init", "-q", str(novo)], raiz)
        patch = diff_da_proposta()
        if rodar(["git", "apply", "--check", "-"], novo, entrada=patch).returncode == 0:
            r = rodar(["git", "apply", "-"], novo, entrada=patch)
            assert r.returncode == 0, r.stderr
            cls.originais = [raiz / "orig" / ".githooks" / "pre-push"]
        else:  # o dono já aplicou: só o remendado existe
            r = rodar(["git", "apply", "-R", "--check", "-"], novo, entrada=patch)
            assert r.returncode == 0, f"o patch da proposta não aplica no hook nem já está nele: {r.stderr}"
            cls.originais = []
        cls.remendado = novo / ".githooks" / "pre-push"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def hooks(self):
        """(rótulo, caminho, deve_ter_o_conserto): o original falha, o remendado passa."""
        return [("original", h, False) for h in self.originais] + [("remendado", self.remendado, True)]

    def novo_repo(self, base, preparar):
        """Repositório descartável na branch melhoria/x, com origin/develop no commit base."""
        repo = base / "repo"
        repo.mkdir()
        preparar(repo)
        for args in (["init", "-q", "-b", "melhoria/x"], ["add", "-A"], ["commit", "-q", "-m", "base"],
                     ["update-ref", "refs/remotes/origin/develop", "HEAD"]):
            r = rodar(["git", *args], repo)
            self.assertEqual(r.returncode, 0, r.stderr)
        return repo

    def envia(self, hook, base, repo, mudanca, path=None, **extra):
        for nome, texto in mudanca.items():
            (repo / nome).parent.mkdir(parents=True, exist_ok=True)
            (repo / nome).write_text(texto)
        for args in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "muda"]):
            self.assertEqual(rodar(["git", *args], repo).returncode, 0)
        sha = rodar(["git", "rev-parse", "HEAD"], repo).stdout.strip()
        (base / "run").mkdir(exist_ok=True)
        env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"), TMPDIR=str(base), **extra)
        if path:
            env["PATH"] = path
        r = rodar([str(hook), "origin", "u"], repo, env, f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\n")
        return r.returncode, r.stderr


class PatchAplica(Base):
    def test_patch_so_toca_o_pre_push_e_o_remendado_e_shell_valido_e_executavel(self):
        self.assertEqual(re.findall(r"^diff --git (\S+) (\S+)$", diff_da_proposta(), re.M),
                         [("a/.githooks/pre-push", "b/.githooks/pre-push")])
        r = subprocess.run(["bash", "-n", str(self.remendado)], capture_output=True, text=True, env=AMBIENTE)
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
            r = subprocess.run(["bash", "-c", f'trava="{pasta / "trava"}"; {self.funcao(hook)}\n{abre}texto_da_trava'],
                               capture_output=True, text=True, env=AMBIENTE)
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
        self.assertEqual(self.le(self.remendado, fd_aberto=False), (0, ""))

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
    """FILA-INTERVALO-ZERO: 0 imprimia a fila a cada 0,2 s; agora é recusado como o valor inválido, lido em base 10."""

    def roda(self, hook, valor, espera="5", segura=False):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            (base / "run").mkdir()
            (base / "repo" / "tests").mkdir(parents=True)
            (base / "repo" / "tests" / "test_a.py").write_text(SUITE_VERDE)
            rodar(["git", "init", "-q", str(base / "repo")], base)
            if segura:
                dona = subprocess.Popen([sys.executable, "-I", "-c", SEGURA, str(base / "run" / f"forge-suite-{os.getuid()}.lock")],
                                        stdout=subprocess.PIPE, text=True, env=AMBIENTE)
                self.addCleanup(lambda d=dona: (d.kill(), d.wait(), d.stdout.close()))
                self.assertEqual(dona.stdout.readline().strip(), "pronto")
            env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(base / "run"), HOME=str(base / "home"), FORGE_TRAVA_ESPERA=espera,
                       FORGE_FILA_INTERVALO=valor)
            r = rodar([str(hook), "--suite"], base / "repo", env)
            return r.returncode, r.stderr

    def test_zero_e_zeros_sao_recusados_antes_da_fila(self):
        for rotulo, hook, conserto in self.hooks():
            for valor in ("0", "00", "000"):
                with self.subTest(rotulo, valor=valor):
                    codigo, erro = self.roda(hook, valor)
                    if conserto:
                        self.assertEqual(codigo, 1, erro)
                        self.assertIn("FORGE_FILA_INTERVALO deve ser um número de segundos inteiro maior que zero", erro)
                        self.assertNotIn("pre-push: entrou", erro)
                    else:
                        self.assertEqual(codigo, 0, "sem o patch o 0 é aceito e a suíte roda")

    def test_zeros_a_esquerda_em_base_dez_sao_aceitos(self):
        for valor in ("08", "09", "010"):
            with self.subTest(valor=valor):
                codigo, erro = self.roda(self.remendado, valor)
                self.assertEqual(codigo, 0, erro)
                self.assertNotIn("value too great", erro)

    def test_conta_da_espera_usa_o_valor_decimal(self):
        """Com a trava presa, "08" entra na espera (o próximo aviso só em 8 s) e o envio é barrado só pelo tempo."""
        codigo, erro = self.roda(self.remendado, "08", espera="2", segura=True)
        self.assertEqual(codigo, 1, erro)
        self.assertIn("a vez não chegou em 2 s", erro)
        self.assertEqual(erro.count("fila da suíte"), 1, erro)
        self.assertNotIn("value too great", erro)

    def test_invalido_segue_recusado_e_o_valor_bom_passa(self):
        for valor, esperado in (("1m", 1), ("-1", 1), ("", 0), ("1", 0), ("60", 0)):  # vazio cai no padrão de ${...:-60}
            with self.subTest(valor=valor):
                codigo, erro = self.roda(self.remendado, valor)
                self.assertEqual(codigo, esperado, erro)
                self.assertEqual("FORGE_FILA_INTERVALO deve ser um número de segundos inteiro" in erro, esperado == 1, erro)
                self.assertNotIn("error token", erro)  # recusado pelo case, antes da conta (sem erro do bash)


# O bin/forge-mutante não tem regra no MAPA do bin/forge-testes (só a convenção, que test_testes_tocados exige): o falso
# dele é gravado pelo mesmo nome da cópia, como no test_pre_push_patch. Mudar o forge-mutante roda este módulo só no CI.
MUTANTE = "forge-mutante"


class CoberturaDaCatraca(Base):
    """PREPUSH-LEVE-COBERTURA-CATRACA: o envio leve reprova condição mudada em Python de controle sem mutante declarado."""

    def preparar(self, repo):
        for pasta in ("bin", "hooks", "tests"):
            (repo / pasta).mkdir()
        for nome in (MUTANTE, "forge_apoio_testes.py", "forge-check"):
            shutil.copy(RAIZ / "bin" / nome, repo / "bin" / nome)
        for nome in ("catraca.py", "neutralidade.py"):
            shutil.copy(RAIZ / "tests" / nome, repo / "tests" / nome)
        (repo / "bin" / "x.py").write_text("def g(a, b):\n    if a:\n        return 1\n    return 0\n")
        (repo / "hooks" / "h.py").write_text("def f(a, b):\n    if a:\n        return 1\n    return 0\n")
        (repo / "tests" / "test_a.py").write_text(SUITE_VERDE)

    def roda(self, hook, mudanca, antes=None):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            repo = self.novo_repo(base, self.preparar)
            if antes:
                antes(repo)
            return self.envia(hook, base, repo, mudanca)

    def test_condicao_mudada_em_codigo_de_controle_sem_mutante_reprova(self):
        for rotulo, hook, conserto in self.hooks():
            with self.subTest(rotulo):
                codigo, erro = self.roda(hook, {"hooks/h.py": "def f(a, b):\n    if a and b:\n        return 1\n    return 0\n"})
                if conserto:
                    self.assertEqual(codigo, 1, erro)
                    self.assertIn("forge-mutante --cobertura reprovou", erro)
                    self.assertIn("sem mutante · hooks/h.py", erro)
                    self.assertNotIn("Traceback", erro)
                else:
                    self.assertEqual(codigo, 0, "sem o patch só o CI pega")

    def test_condicao_fora_de_hooks_tambem_reprova(self):
        codigo, erro = self.roda(self.remendado, {"bin/x.py": "def g(a, b):\n    if a or b:\n        return 1\n    return 0\n"})
        self.assertEqual(codigo, 1, erro)
        self.assertIn("sem mutante · bin/x.py", erro)

    def test_condicao_em_teste_nao_barra_porque_a_catraca_exclui_testes(self):
        catraca = (RAIZ / "tests" / "catraca.py").read_text(encoding="utf-8")
        codigo, erro = self.roda(self.remendado, {"tests/catraca.py": catraca + "\nif 1 and 2:\n    pass\n"})
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("reprovou", erro)

    def test_forge_check_que_e_link_nao_roda_a_checagem(self):
        def link(repo):
            (repo / "bin" / "forge-check").rename(repo / "bin" / "alvo-do-link")
            (repo / "bin" / "forge-check").symlink_to("alvo-do-link")
        codigo, erro = self.roda(self.remendado, {"hooks/h.py": "def f(a, b):\n    if a and b:\n        return 1\n    return 0\n"}, link)
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("forge-mutante --cobertura", erro)

    def test_saida_2_da_ferramenta_e_so_aviso(self):
        codigo, erro = self.roda(self.remendado, {"hooks/h.py": "def f(a, b):\n    return 1\n", "tests/mutantes/x.json": "{"})
        self.assertEqual(codigo, 0, erro)
        self.assertIn("aviso: bin/forge-mutante --cobertura não conferiu o delta (saída 2)", erro)

    def test_saida_fora_do_formato_ou_codigo_alto_da_ferramenta_e_so_aviso(self):
        """Um forge-mutante falso: falta sem `arquivo:linha` (o filtro sai com 2) ou saída 3; nos dois, aviso e rc 0."""
        for linha, saida in (("sem mutante sem arquivo", 1), ("sem mutante · hooks/h.py:2 · a", 3)):
            with self.subTest(saida=saida):
                falso = f"import sys\nprint({linha!r})\nsys.exit({saida})\n"
                codigo, erro = self.roda(self.remendado, {"hooks/h.py": "def f(a, b):\n    return 1\n", f"bin/{MUTANTE}": falso})
                self.assertEqual(codigo, 0, erro)
                self.assertIn(f"aviso: bin/forge-mutante --cobertura não conferiu o delta (saída {2 if saida == 1 else saida})", erro)

    def test_catraca_ilegivel_no_filtro_e_so_aviso(self):
        falso = "import sys\nprint('sem mutante · hooks/h.py:2 · a')\nsys.exit(1)\n"
        mudanca = {"hooks/h.py": "def f(a, b):\n    return 1\n", f"bin/{MUTANTE}": falso, "tests/catraca.py": "raise RuntimeError('x')\n"}
        codigo, erro = self.roda(self.remendado, mudanca)
        self.assertEqual(codigo, 0, erro)
        self.assertIn("aviso: bin/forge-mutante --cobertura não conferiu o delta (saída 2)", erro)

    def test_mudanca_sem_condicao_ou_sem_python_passa_sem_rodar(self):
        casos = {"sem condição": {"hooks/h.py": "def f(a, b):\n    if a:\n        return 2\n    return 0\n"},
                 "sem Python": {"docs/x.md": "x\n"}}
        for nome, mudanca in casos.items():
            with self.subTest(nome):
                codigo, erro = self.roda(self.remendado, mudanca)
                self.assertEqual(codigo, 0, erro)
                self.assertNotIn("forge-mutante --cobertura", erro)


class IndiceEPulos(Base):
    """PREPUSH-INDICE-E-PULOS: o envio leve confere o índice das fixtures e barra teste pulado novo em tests/."""

    FIXTURE = '{"descricao": "caso novo", "esperado": {"codigo": 2}}\n'

    def preparar(self, repo):
        for pasta in ("scripts", "tests/hooks/h", "docs"):
            (repo / pasta).mkdir(parents=True)
        shutil.copy(RAIZ / "scripts" / "indice-fixtures.py", repo / "scripts" / "indice-fixtures.py")
        for nome in ("catraca.py", "neutralidade.py", "config.json"):
            shutil.copy(RAIZ / "tests" / nome, repo / "tests" / nome)
        (repo / "tests" / "hooks" / "h" / "a-1.json").write_text(self.FIXTURE)
        (repo / "tests" / "test_a.py").write_text(SUITE_VERDE)
        self.regerar(repo)

    def regerar(self, repo):
        r = rodar([sys.executable, "-I", "scripts/indice-fixtures.py"], repo)
        self.assertEqual(r.returncode, 0, r.stderr)

    def roda(self, hook, mudanca, regera=False):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            repo = self.novo_repo(base, self.preparar)
            if regera:
                for nome, texto in mudanca.items():
                    (repo / nome).write_text(texto)
                self.regerar(repo)
            return self.envia(hook, base, repo, mudanca)

    def test_fixture_nova_sem_regerar_o_indice_reprova(self):
        for rotulo, hook, conserto in self.hooks():
            with self.subTest(rotulo):
                codigo, erro = self.roda(hook, {"tests/hooks/h/b-1.json": self.FIXTURE})
                if conserto:
                    self.assertEqual(codigo, 1, erro)
                    self.assertIn("docs/hooks-fixtures.md desatualizado (o CI reprova igual)", erro)
                else:
                    self.assertEqual(codigo, 0, "sem o patch só o CI pega")

    def test_fixture_nova_com_o_indice_regerado_passa(self):
        codigo, erro = self.roda(self.remendado, {"tests/hooks/h/b-1.json": self.FIXTURE}, regera=True)
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("hooks-fixtures", erro)

    def test_cada_caminho_do_corpus_dispara_o_indice(self):
        """Mexer no config ou no próprio índice também confere: índice adulterado reprova."""
        for nome in ("docs/hooks-fixtures.md", "tests/config.json"):
            with self.subTest(nome), tempfile.TemporaryDirectory() as t:
                base = Path(t)
                repo = self.novo_repo(base, self.preparar)
                (repo / "tests" / "hooks" / "h" / "b-1.json").write_text(self.FIXTURE)  # fixture fora do índice
                rodar(["git", "add", "-A"], repo)
                rodar(["git", "commit", "-q", "-m", "fixture"], repo)
                rodar(["git", "update-ref", "refs/remotes/origin/develop", "HEAD"], repo)
                texto = (repo / nome).read_text(encoding="utf-8")
                codigo, erro = self.envia(self.remendado, base, repo, {nome: texto + ("\n" if nome.endswith(".md") else " ")})
                self.assertEqual(codigo, 1, erro)
                self.assertIn("docs/hooks-fixtures.md desatualizado", erro)

    def test_indice_que_nao_roda_e_so_aviso(self):
        mudanca = {"scripts/indice-fixtures.py": "import sys\nsys.exit(2)\n", "tests/hooks/h/b-1.json": self.FIXTURE}
        codigo, erro = self.roda(self.remendado, mudanca)
        self.assertEqual(codigo, 0, erro)
        self.assertIn("aviso: scripts/indice-fixtures.py --conferir não conferiu o índice (saída 2)", erro)

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
        for decorador in ("@unittest.skip('x')", "@unittest.skipIf(True, 'x')", "@unittest.skipUnless(False, 'x')",
                          "@unittest.expectedFailure"):
            with self.subTest(decorador):
                texto = SUITE_VERDE.replace("    def test_a", f"    {decorador}\n    def test_a")
                self.assertEqual(self.roda(self.remendado, {"tests/test_a.py": texto})[0], 1)

    def test_pulo_so_citado_em_texto_ou_com_erro_de_sintaxe_nao_conta(self):
        casos = {"só citado em texto": {"tests/test_a.py": SUITE_VERDE + '\nNOTA = "usa skipTest e skipIf"\n'},
                 "teste ilegível": {"tests/test_b.py": "def f(:\n"}}
        for nome, mudanca in casos.items():
            with self.subTest(nome):
                _, erro = self.roda(self.remendado, mudanca)
                self.assertNotIn("teste pulado", erro)
                self.assertNotIn("contagem de testes pulados não rodou", erro)

    def test_skip_novo_na_propria_catraca_nao_barra(self):
        catraca = (RAIZ / "tests" / "catraca.py").read_text(encoding="utf-8")
        texto = catraca + "\nimport unittest\nclass TX(unittest.TestCase):\n    def test_x(self):\n        self.skipTest('x')\n"
        codigo, erro = self.roda(self.remendado, {"tests/catraca.py": texto})
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("teste pulado", erro)

    def test_skip_novo_fora_de_tests_nao_barra(self):
        fora = SUITE_VERDE.replace("        pass\n", '        self.skipTest("depois")\n')
        # um teste tocado (sem pulo) faz a conta rodar; o x.py e o bin/y.py com pulo, fora de tests/, não somam
        codigo, erro = self.roda(self.remendado, {"x.py": fora, "bin/y.py": fora, "tests/test_a.py": SUITE_VERDE + "# nota\n"})
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("teste pulado", erro)

    def test_catraca_ilegivel_e_so_aviso(self):
        pulado = SUITE_VERDE.replace("        pass\n", '        self.skipTest("depois")\n')
        codigo, erro = self.roda(self.remendado, {"tests/test_a.py": pulado, "tests/catraca.py": "raise RuntimeError(\"ilegível\")\n"})
        self.assertEqual(codigo, 0, erro)
        self.assertIn("aviso: a contagem de testes pulados não rodou (saída 2)", erro)


class ListaVazia(Base):
    """PREPUSH-FORGE-AVISO-LISTA-VAZIA: sem sort ou mktemp, ou com a lista vazia, o envio avisa; nunca libera a mais."""

    ERRO = {"bin/x.py": "def f(:\n"}
    FALHOU = "aviso: a lista de arquivos do envio falhou (mktemp, sort ou git)"
    VAZIA = "aviso: a lista de arquivos do envio veio vazia"

    def preparar(self, repo):
        (repo / "a.txt").write_text("x\n")

    def roda(self, hook, mudanca, sem=None, falso=False, base_dev=True):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            repo = self.novo_repo(base, self.preparar)
            if not base_dev:
                rodar(["git", "update-ref", "-d", "refs/remotes/origin/develop"], repo)
            path = fazenda(base / "bin", sem, falso) if sem else None
            return self.envia(hook, base, repo, mudanca, path)

    def test_sem_sort_ou_sem_mktemp_avisa_e_o_original_cala(self):
        for programa in ("sort", "mktemp"):
            for rotulo, hook, conserto in self.hooks():
                with self.subTest(rotulo, sem=programa):
                    codigo, erro = self.roda(hook, self.ERRO, sem=programa)
                    self.assertEqual(codigo, 0, erro)  # só avisa: o CI é o portão, como antes
                    self.assertEqual(self.FALHOU in erro, conserto, erro)
                    self.assertNotIn(self.VAZIA, erro)

    def test_sort_que_sai_com_erro_tambem_avisa(self):
        codigo, erro = self.roda(self.remendado, self.ERRO, sem="sort", falso=True)
        self.assertEqual(codigo, 0, erro)
        self.assertIn(self.FALHOU, erro)

    def test_lista_vazia_num_envio_de_codigo_avisa(self):
        codigo, erro = self.roda(self.remendado, {})
        self.assertEqual(codigo, 0, erro)
        self.assertIn(self.VAZIA, erro)
        self.assertNotIn(self.FALHOU, erro)

    def test_sem_a_base_nao_repete_o_aviso_da_varredura(self):
        codigo, erro = self.roda(self.remendado, {"b.txt": "y\n"}, base_dev=False)
        self.assertEqual(codigo, 0, erro)
        self.assertIn("sem refs/remotes/origin/develop", erro)
        self.assertNotIn(self.FALHOU, erro)
        self.assertNotIn(self.VAZIA, erro)

    def test_com_tudo_no_path_o_erro_de_sintaxe_segue_barrado_e_sem_aviso(self):
        codigo, erro = self.roda(self.remendado, self.ERRO)
        self.assertEqual(codigo, 1, erro)
        self.assertIn("erro de sintaxe Python em bin/x.py", erro)
        self.assertNotIn(self.FALHOU, erro)
        self.assertNotIn(self.VAZIA, erro)

    def test_lista_ilegivel_com_afetados_roda_a_suite_inteira(self):
        """Só aperta: com FORGE_PREPUSH_SUITE=afetados, a lista que falhou leva à suíte inteira, não a "nada a rodar"."""
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)

            def preparar(repo):
                (repo / "tests").mkdir()
                (repo / "tests" / "test_a.py").write_text(SUITE_VERDE)
            repo = self.novo_repo(base, preparar)
            codigo, erro = self.envia(self.remendado, base, repo, {"b.txt": "y\n"}, fazenda(base / "bin", "sort"),
                                      FORGE_PREPUSH_SUITE="afetados")
        self.assertEqual(codigo, 0, erro)
        self.assertIn(self.FALHOU, erro)
        self.assertRegex(erro, r"pre-push: fim \S+ rc 0 completa")


if __name__ == "__main__":
    unittest.main()
