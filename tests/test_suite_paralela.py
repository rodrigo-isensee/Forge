"""D4 (SUITE-PARALELA-D4): scripts/suite-paralela.py divide a suíte em processos sem perder teste.

A lógica pura (divisão, guarda de completude, número de processos) é testada importando o script; o resto roda o
script de verdade num repositório de brinquedo (cópia do script e dos módulos de apoio, com uma suíte mínima), para
não disparar a suíte do Forge de dentro dela. Casos de abuso AB-1 a AB-5 e AB-13 do modelo de ameaças.
"""
import collections
import contextlib
import importlib.util
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "suite-paralela.py"
# FORGE_SUITE_* (processos, medição, trava) da suíte que roda estes testes não vazam para a suíte de brinquedo.
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})


def carregar(caminho=SCRIPT, nome="suite_paralela"):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# Cada teste de brinquedo anota em $MARCAS (fora da árvore) quem rodou, com o TMPDIR e o nice do processo.
MARCA = '''import os, pathlib, unittest
def marca(nome):
    pasta = pathlib.Path(os.environ["MARCAS"])
    (pasta / f"{nome}-{os.getpid()}").write_text(
        f"{os.environ.get('TMPDIR', '')}\\n{os.nice(0)}\\n{os.getpgid(0)}\\n")
'''


def modulo_de_teste(nome, corpo="self.assertTrue(True)", extra=""):
    return MARCA + extra + f'''
class T(unittest.TestCase):
    def test_{nome}(self):
        marca("{nome}")
        {corpo}
'''


class Logica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = carregar()

    def test_repartir_cobre_todos_e_e_determinista(self):
        nomes = [f"test_{i}" for i in range(9)]
        pesos = {"test_0": 50, "test_1": 30, "test_2": 20, "test_3": 5, "test_4": 5, "test_5": 5}
        partes = self.s.repartir(nomes, pesos, 4)
        self.assertEqual(partes, self.s.repartir(list(reversed(nomes)), pesos, 4))
        self.assertEqual(sorted(m for p in partes for m in p), sorted(nomes))
        self.assertEqual(self.s.conferir_particao(nomes, partes), [])
        self.assertEqual(len(partes), 4)
        # o mais pesado fica sozinho (LPT; os sem peso valem a mediana, 12,5): 50 passa de tudo o que sobra dividido por 3
        self.assertIn(["test_0"], partes)

    def test_modulo_sem_peso_vale_a_mediana_e_entra(self):
        partes = self.s.repartir(["test_a", "test_b", "test_novo"], {"test_a": 10, "test_b": 2}, 2)
        self.assertIn("test_novo", [m for p in partes for m in p])
        self.assertEqual(self.s.repartir(["test_a"], {}, 4), [["test_a"]])  # sem pesos e com menos módulos que N

    def test_particao_errada_e_apontada(self):
        nomes = ["test_a", "test_b", "test_c"]
        self.assertIn("módulo fora da divisão: test_c", self.s.conferir_particao(nomes, [["test_a"], ["test_b"]]))
        self.assertIn("módulo em mais de um processo: test_a",
                      self.s.conferir_particao(nomes, [["test_a", "test_c"], ["test_a", "test_b"]]))
        self.assertIn("módulo desconhecido na divisão: test_x",
                      self.s.conferir_particao(nomes, [["test_a", "test_b", "test_c", "test_x"]]))

    def test_completude_compara_soma_e_uniao(self):
        esperado = collections.Counter({"a.T.t1": 1, "b.T.t1": 1, "v.Raiz.t": 2})
        self.assertEqual(self.s.conferir_completude(esperado, collections.Counter(esperado)), [])
        sem_b = collections.Counter({"a.T.t1": 1, "v.Raiz.t": 2})
        erros = self.s.conferir_completude(esperado, sem_b)
        self.assertTrue(any("soma diferente" in e for e in erros), erros)
        self.assertTrue(any("ausente" in e and "b.T.t1" in e for e in erros), erros)
        # mesma soma, outro teste: a união denuncia
        trocado = collections.Counter({"a.T.t1": 1, "x.T.t1": 1, "v.Raiz.t": 2})
        erros = self.s.conferir_completude(esperado, trocado)
        self.assertFalse(any("soma" in e for e in erros))
        self.assertTrue(any("ausente" in e for e in erros) and any("a mais" in e for e in erros), erros)
        # classe importada em dois módulos roda duas vezes, como no discover: uma só não basta
        erros = self.s.conferir_completude(esperado, collections.Counter({"a.T.t1": 1, "b.T.t1": 1, "v.Raiz.t": 1}))
        self.assertTrue(any("ausente" in e for e in erros), erros)

    def test_numero_de_processos(self):
        n = self.s.numero_de_processos
        self.assertEqual(n({}, 16, 1.0, 6.0, 8.0)[0], 4)
        self.assertEqual(n({}, 3, 0.1, 6.0, 8.0)[0], 3)
        self.assertEqual(n({}, 1, 0.1, 6.0, 8.0)[0], 1)
        self.assertEqual(n({}, None, None, None, None)[0], 1)
        self.assertEqual(n({}, 16, 13.0, 6.0, 8.0)[0], 2)  # load >= 0,8 x nproc
        self.assertEqual(n({}, 16, 1.0, 0.9, 8.0)[0], 2)  # memória no piso
        self.assertEqual(n({}, 16, None, None, None)[0], 4)  # sem medida, não é carga alta
        self.assertEqual(n({"FORGE_SUITE_PROCS": "3"}, 16, 1.0, 6.0, 8.0), (3, "FORGE_SUITE_PROCS"))
        for valor in ("5", "0", "x", "-1", "4.0"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                n({"FORGE_SUITE_PROCS": valor}, 16, 1.0, 6.0, 8.0)


class Brinquedo(unittest.TestCase):
    """O script de verdade num repositório de brinquedo."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.repo = base / "repo"
        self.marcas = base / "marcas"
        self.marcas.mkdir()
        self.tmpdir = base / "tmp"
        self.tmpdir.mkdir()
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "tests").mkdir()
        shutil.copy(SCRIPT, self.repo / "scripts" / "suite-paralela.py")
        (self.repo / ".githooks").mkdir()
        shutil.copy(RAIZ / ".githooks" / "pre-push", self.repo / ".githooks" / "pre-push")
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        for apoio in ("guarda_git.py", "ambiente_git.py"):
            shutil.copy(RAIZ / "tests" / apoio, self.repo / "tests" / apoio)
        (self.repo / ".gitignore").write_text("__pycache__/\n")
        for nome in ("a", "b", "c"):
            self.modulo(nome, modulo_de_teste(nome))
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "x")
        self.env = dict(AMBIENTE, MARCAS=str(self.marcas), TMPDIR=str(self.tmpdir), FORGE_SUITE_PROCS="3",
                        XDG_RUNTIME_DIR=str(self.run_dir), FORGE_TRAVA_ESPERA="20")
        self.env.pop("FORGE_SUITE_TRAVA", None)
        self.env.pop("CI", None)
        self.env.pop("GITHUB_ACTIONS", None)
        self.env.pop("GITHUB_STEP_SUMMARY", None)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, check=True, capture_output=True)

    def modulo(self, nome, texto):
        (self.repo / "tests" / f"test_{nome}.py").write_text(texto)

    def roda(self, **extra):
        r = subprocess.run([sys.executable, str(self.repo / "scripts" / "suite-paralela.py")], cwd=self.repo,
                           env=dict(self.env, **extra), capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout, r.stderr

    def rodaram(self):
        return sorted(p.name.rsplit("-", 1)[0] for p in self.marcas.iterdir())

    def script_do_brinquedo(self):
        return carregar(self.repo / "scripts" / "suite-paralela.py", "suite_paralela_brinquedo")

    def orquestrar_no_processo(self, script, **ambiente):
        """`script.orquestrar()` neste processo, sem o `GITHUB_STEP_SUMMARY` nem o `GITHUB_ACTIONS` do runner, para o
        brinquedo não escrever no resumo real do CI (N-CI, C-10); `ambiente` vale depois da limpeza."""
        saida, erro, cwd = io.StringIO(), io.StringIO(), os.getcwd()
        self.addCleanup(os.chdir, cwd)
        antes, modulos_antes = dict(os.environ), set(sys.modules)
        for chave in ("GITHUB_STEP_SUMMARY", "GITHUB_ACTIONS"):
            os.environ.pop(chave, None)
        os.environ.update(MARCAS=str(self.marcas), FORGE_SUITE_PROCS="2", **ambiente)
        try:
            with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
                codigo = script.orquestrar()
        finally:
            os.environ.clear()
            os.environ.update(antes)
            for nome in set(sys.modules) - modulos_antes:  # os test_a... do brinquedo não ficam para a próxima execução
                if nome.startswith("test_"):
                    del sys.modules[nome]
        return codigo, saida.getvalue(), erro.getvalue()

    def resumo_do_ci(self, **extra):
        """(código, saída, erro, texto do resumo) de uma execução com `GITHUB_STEP_SUMMARY` num arquivo do teste."""
        arquivo = self.repo.parent / "resumo.md"
        arquivo.unlink(missing_ok=True)
        codigo, saida, erro = self.roda(GITHUB_STEP_SUMMARY=str(arquivo), **extra)
        return codigo, saida, erro, (arquivo.read_text(encoding="utf-8") if arquivo.exists() else "")

    def test_tudo_verde_roda_cada_modulo_uma_vez(self):
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertEqual(saida.strip().splitlines()[-1], "OK")
        self.assertIn("Ran 3 tests", saida)
        self.assertIn("3 processos", saida)
        self.assertEqual(self.rodaram(), ["a", "b", "c"])

    def test_verde_grava_carimbo_e_a_segunda_chamada_reusa_sem_rodar(self):  # K6
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertEqual(len(self.rodaram()), 3)
        for marca in self.marcas.iterdir():
            marca.unlink()
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        linhas = saida.strip().splitlines()
        self.assertTrue(linhas[0].startswith("suite: reusa "), saida)
        self.assertEqual(linhas[-1], "OK")
        self.assertEqual(self.rodaram(), [])
        codigo, saida, erro = self.roda(FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 0, saida + erro)
        self.assertEqual(len(self.rodaram()), 3)

    def test_vermelho_nao_grava_carimbo(self):  # K6
        self.modulo("c", modulo_de_teste("c", "self.fail('x')"))
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "y")
        self.assertNotEqual(self.roda()[0], 0)
        for marca in self.marcas.iterdir():
            marca.unlink()
        self.assertNotEqual(self.roda()[0], 0)
        self.assertEqual(len(self.rodaram()), 3)

    def test_commit_no_meio_da_suite_nao_grava_carimbo(self):  # A2 da segurança
        corpo = ("import subprocess; open('novo.txt', 'w').write('x'); "
                 "[subprocess.run(c, check=True) for c in (['git', 'add', 'novo.txt'], "
                 "['git', '-c', 'user.email=t@example.com', '-c', 'user.name=t', 'commit', '-q', '-m', 'meio'])]")
        self.modulo("c", modulo_de_teste("c", corpo))
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "y")
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        for marca in self.marcas.iterdir():
            marca.unlink()
        self.git("reset", "-q", "--hard", "HEAD~1")  # volta à árvore que a suíte começou testando
        codigo, saida, erro = self.roda()
        self.assertNotIn("suite: reusa", saida)  # sem carimbo da árvore antiga, que não foi a testada inteira
        self.assertEqual(len(self.rodaram()), 3)

    def test_cada_processo_tem_tmpdir_proprio_nice_e_grupo_proprio(self):
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        linhas = [p.read_text().splitlines() for p in self.marcas.iterdir()]
        tmps = {linha[0] for linha in linhas}
        self.assertEqual(len(tmps), 3, tmps)
        for tmp in tmps:
            self.assertTrue(tmp.startswith(str(self.tmpdir) + os.sep), tmp)
            self.assertNotIn(f"forge-{os.getuid()}", Path(tmp).name)
            self.assertFalse(Path(tmp).exists(), "o TMPDIR do processo ficou para trás")
        self.assertEqual(list(self.tmpdir.iterdir()), [])
        self.assertTrue(all(int(linha[1]) >= min(19, os.nice(0) + 10) for linha in linhas), linhas)
        self.assertEqual(len({linha[2] for linha in linhas}), 3, "processos no mesmo grupo")
        self.assertNotIn(str(os.getpgid(0)), {linha[2] for linha in linhas})

    def test_modulo_novo_entra_sem_lista(self):  # AB-1
        self.modulo("novo", modulo_de_teste("novo"))
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertIn("novo", self.rodaram())
        self.assertIn("Ran 4 tests", saida)

    def test_guarda_reprova_quando_um_modulo_some(self):  # AB-2
        script = self.script_do_brinquedo()
        original = script.modulos
        script.modulos = lambda: [m for m in original() if m != "test_b"]
        codigo, saida, erro = self.orquestrar_no_processo(script)
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("ausente", erro)
        self.assertIn("test_b.T.test_b", erro)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED"))
        self.assertNotIn("b", self.rodaram())

    def test_resumo_comeca_pelo_veredito(self):  # AB-3, C-7
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertRegex(resumo.splitlines()[0], r"^### Suíte do Forge: OK\b")
        self.modulo("b", modulo_de_teste("b", 'self.fail("de propósito")'))
        codigo, saida, erro, resumo = self.resumo_do_ci(FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 1)
        self.assertRegex(resumo.splitlines()[0], r"^### Suíte do Forge: FAILED \(failures=1")
        self.assertIn("execução reprovada: não vale para o orçamento", resumo)
        self.assertNotIn("maior unidade", resumo)

    def test_resumo_com_processo_morto_nao_quebra_o_veredito(self):  # AB-1, C-8
        self.modulo("b", modulo_de_teste("b", "os.kill(os.getpid(), signal.SIGKILL)", "import signal\n"))
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("morto pelo sinal 9", erro)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED"))
        self.assertNotIn("resumo indisponível", erro)
        self.assertIn("- sem duração: test_b\n", resumo)

    def test_resumo_nao_muda_o_veredito(self):  # AB-2, C-6
        for corpo in ("self.assertTrue(True)", 'self.fail("de propósito")'):
            self.modulo("b", modulo_de_teste("b", corpo))
            referencia = self.roda(FORGE_SUITE_SEM_REUSO="1")
            pasta = self.repo.parent / "pasta"
            pasta.mkdir(exist_ok=True)
            com_erro_de_escrita = self.roda(FORGE_SUITE_SEM_REUSO="1", GITHUB_STEP_SUMMARY=str(pasta))
            self.assertEqual(com_erro_de_escrita[0], referencia[0])
            self.assertEqual(com_erro_de_escrita[1].strip().splitlines()[-1], referencia[1].strip().splitlines()[-1])
            self.assertIn("resumo indisponível", com_erro_de_escrita[2])
            script = self.script_do_brinquedo()
            script.montar_resumo = lambda *args: 1 / 0
            arquivo = self.repo.parent / "resumo.md"
            codigo, saida, erro = self.orquestrar_no_processo(script, GITHUB_STEP_SUMMARY=str(arquivo),
                                                              FORGE_SUITE_SEM_REUSO="1")
            self.assertEqual(codigo, referencia[0], saida + erro)
            self.assertEqual(saida.strip().splitlines()[-1], referencia[1].strip().splitlines()[-1])
            self.assertIn("resumo indisponível", erro)
            self.assertFalse(arquivo.exists())

    def test_orquestrar_no_processo_nao_escreve_no_resumo_real(self):  # AB-5, C-10
        sentinela = self.repo.parent / "sentinela.md"
        with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(sentinela), "GITHUB_ACTIONS": "true"}):
            codigo, saida, erro = self.orquestrar_no_processo(self.script_do_brinquedo())
            self.assertEqual(codigo, 0, saida + erro)
            self.assertEqual(os.environ["GITHUB_STEP_SUMMARY"], str(sentinela))  # o ambiente do teste volta como estava
        self.assertFalse(sentinela.exists())
        self.assertNotIn("::group::", saida)

    def test_um_processo_vermelho_reprova(self):  # AB-3
        self.modulo("b", modulo_de_teste("b", 'self.fail("de propósito")'))
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED (failures=1"), saida)
        self.assertIn("de propósito", saida)
        self.assertIn("processo", erro)
        # o processo que falhou aparece primeiro
        self.assertLess(saida.index("de propósito"), saida.index("processo 1:"))

    def test_processo_morto_por_sinal_reprova(self):  # AB-4
        self.modulo("b", modulo_de_teste("b", "os.kill(os.getpid(), signal.SIGKILL)", "import signal\n"))
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("morto pelo sinal 9", erro)
        self.assertIn("ausente", erro)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED"))

    def test_processo_com_zero_testes_reprova(self):  # AB-5
        for nome in ("b", "c"):
            (self.repo / "tests" / f"test_{nome}.py").unlink()
        self.modulo("vazio", "import unittest\n")
        codigo, saida, erro = self.roda(FORGE_SUITE_PROCS="2")
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("rodou zero testes", erro)

    def test_teste_que_escreve_na_arvore_reprova(self):  # AB-13
        self.modulo("b", modulo_de_teste("b", 'pathlib.Path("sujou").write_text("x")'))
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("árvore de trabalho mudou", erro)

    def segura_trava(self):
        trava = self.run_dir / f"forge-suite-{os.getuid()}.lock"
        p = subprocess.Popen([sys.executable, "-I", "-c", "import fcntl, sys, time\nf = open(sys.argv[1], 'a')\n"
                              "fcntl.flock(f, fcntl.LOCK_EX)\nprint('pronto', flush=True)\ntime.sleep(600)\n", str(trava)],
                             stdout=subprocess.PIPE, text=True)
        self.addCleanup(lambda: (p.kill(), p.wait(), p.stdout.close()))
        self.assertEqual(p.stdout.readline().strip(), "pronto")
        return trava

    def test_a_mao_espera_a_trava_do_pre_push(self):  # SUITE-FILA-JUSTA, AB-7
        self.segura_trava()
        codigo, saida, erro = self.roda(FORGE_TRAVA_ESPERA="1")
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("a vez não chegou", erro)
        self.assertEqual(self.rodaram(), [])

    def test_trava_informada_que_nao_esta_presa_e_recusada(self):
        trava = self.run_dir / "falsa.lock"
        trava.write_text(f"pid {os.getpid()} desde 00:00:00\n")
        codigo, saida, erro = self.roda(FORGE_SUITE_TRAVA=str(trava))
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("não está presa", erro)
        self.assertEqual(saida.strip().splitlines()[-1], "FAILED (trava)")
        self.assertEqual(self.rodaram(), [])

    def test_trava_presa_por_outro_processo_e_recusada(self):
        trava = self.segura_trava()
        trava.write_text("pid 1 desde 00:00:00\n")
        codigo, saida, erro = self.roda(FORGE_SUITE_TRAVA=str(trava))
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("não é do processo que chamou", erro)
        self.assertEqual(self.rodaram(), [])

    def test_parar_o_pre_push_encerra_os_processos_da_suite(self):  # PREPUSH-PKILL-ALHEIO, AB-6
        self.modulo("b", MARCA + '''
import time
class T(unittest.TestCase):
    def test_b(self):
        marca("b")
        for _ in range(600):
            time.sleep(0.1)
''')
        zero = "0" * 40
        hook = self.repo / ".githooks" / "pre-push"
        with tempfile.TemporaryFile("w+") as entrada:
            entrada.write(f"refs/heads/x {'1' * 40} refs/heads/melhoria/x {zero}\n")
            entrada.seek(0)
            p = subprocess.Popen([str(hook), "origin", "u"], cwd=self.repo, env=self.env, stdin=entrada,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: p.poll() is None and p.kill())
        fim = time.monotonic() + 30
        while time.monotonic() < fim and not any(n.name.startswith("b-") for n in self.marcas.iterdir()):
            time.sleep(0.05)
        (marca,) = [n for n in self.marcas.iterdir() if n.name.startswith("b-")]
        pid = int(marca.name.rsplit("-", 1)[1])
        p.send_signal(signal.SIGTERM)
        _, erro = p.communicate(timeout=30)
        self.assertEqual(p.returncode, 1, erro)
        self.assertIn("suíte interrompida", erro)
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        self.assertEqual(list(self.tmpdir.iterdir()), [])
        self.assertFalse((self.run_dir / f"forge-suite-{os.getuid()}.verde").exists())

    def test_procs_acima_do_teto_e_recusado(self):
        codigo, saida, erro = self.roda(FORGE_SUITE_PROCS="5")
        self.assertEqual(codigo, 1)
        self.assertIn("FORGE_SUITE_PROCS", erro)
        self.assertEqual(self.rodaram(), [])

    def test_medir_grava_pesos_so_dos_modulos_vivos(self):
        codigo, saida, erro = self.roda(FORGE_SUITE_MEDIR="1")
        self.assertEqual(codigo, 0, saida + erro)
        pesos = json.loads((self.repo / "tests" / "pesos-d4.json").read_text())
        self.assertEqual(sorted(pesos), ["test_a", "test_b", "test_c"])

    def test_sigterm_encerra_o_grupo_de_cada_processo(self):
        self.modulo("b", MARCA + '''
import time
class T(unittest.TestCase):
    def test_b(self):
        marca("b")
        for _ in range(600):
            if (pathlib.Path(os.environ["MARCAS"]) / "liberar").exists():
                return
            time.sleep(0.1)
''')
        p = subprocess.Popen([sys.executable, str(self.repo / "scripts" / "suite-paralela.py")], cwd=self.repo,
                             env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: p.poll() is None and p.kill())
        fim = time.monotonic() + 30
        while time.monotonic() < fim and not any(n.name.startswith("b-") for n in self.marcas.iterdir()):
            time.sleep(0.05)
        (marca,) = [n for n in self.marcas.iterdir() if n.name.startswith("b-")]
        pid = int(marca.name.rsplit("-", 1)[1])
        p.send_signal(signal.SIGTERM)
        saida, erro = p.communicate(timeout=30)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("interrompida", erro)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED"))
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        self.assertEqual(list(self.tmpdir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
