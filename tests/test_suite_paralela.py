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
import threading
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


EXTRA_DO_A = '\n    def test_a2(self):\n        marca("a2")\n\n\nclass U(unittest.TestCase):\n    def test_a3(self):\n        marca("a3")\n'


class Logica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = carregar()

    def test_testes_que_cairam_no_resumo_tem_teto_e_id_limpo(self):  # QA-1
        self.assertEqual(self.s.testes_que_cairam([None, {"caidos": []}, {}]), [])
        rels = [{"caidos": ["test_b.T.test_y", "test_a.T.test_x"]}, None, {"caidos": ["test_a.T.test_x", "x`y\nz" + "a" * 300]}]
        linhas = self.s.testes_que_cairam(rels)
        self.assertEqual(linhas[:4], ["", "#### Testes que caíram (3)", "- `test_a.T.test_x`", "- `test_b.T.test_y`"])
        self.assertEqual(linhas[4], "- `xyz" + "a" * 195 + "`")  # cortado em 200, depois sem crase nem quebra de linha
        self.assertEqual(self.s.LIMITE_CAIDOS, 30)  # A2 do review: o teto literal, não o valor da própria constante
        muitos = self.s.testes_que_cairam([{"caidos": [f"test_m.T.test_{i:03d}" for i in range(37)]}])
        self.assertEqual(len(muitos), 2 + 30 + 1)
        self.assertEqual(muitos[-1], "- e mais 7 (a lista inteira está no log do passo)")

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

    def test_chave_separada_tira_os_testes_do_modulo_para_unidade_propria(self):  # S-SUITE-RAPIDA
        ids = {"test_a": ["test_a.T.test_1", "test_a.T.test_2", "test_a.U.test_3", "test_b.Importada.test_x"],
               "test_c": ["test_c.T.test_1"]}
        pesos = {"test_a": 5, "test_a.T.test_2": 100, "test_a.U": 50, "test_a.Sumiu.test_9": 7, "test_c": 1}
        plano = self.s.planejar(["test_a", "test_c"], pesos, ids.__getitem__)
        self.assertEqual(plano, {"test_a": ("test_a", [0, 3]), "test_a.T.test_2": ("test_a", [1]),
                                 "test_a.U": ("test_a", [2]), "test_c": ("test_c", None)})
        # cada posição numa unidade só, e todas as posições do módulo cobertas
        posicoes = sorted(i for modulo, ps in plano.values() if modulo == "test_a" for i in ps)
        self.assertEqual(posicoes, [0, 1, 2, 3])
        self.assertEqual(self.s.unidade_do_teste("test_a.T.test_20", ["test_a.T.test_2"], "test_a"), "test_a")
        self.assertEqual(self.s.unidade_do_teste("test_a.T.test_2", ["test_a.T", "test_a.T.test_2"], "test_a"),
                         "test_a.T.test_2")
        # sem chave separada, o módulo não é aberto
        self.assertEqual(self.s.planejar(["test_c"], pesos, lambda nome: self.fail("abriu")), {"test_c": ("test_c", None)})

    def test_entrada_do_processo_leva_as_posicoes_so_da_unidade_aberta(self):  # S-SUITE-RAPIDA
        plano = {"test_a": ("test_a", [0]), "test_a.T.test_2": ("test_a", [1]), "test_c": ("test_c", None)}
        self.assertEqual(self.s.entrada_do_processo(["test_a.T.test_2", "test_c"], plano),
                         [{"unidade": "test_a.T.test_2", "modulo": "test_a", "posicoes": [1]}, "test_c"])

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


class CausaTipada(unittest.TestCase):
    """O7 (0.44.1): cada teste que cai ganha um tipo (timeout, teste de tempo, saída grande, asserção ou erro)."""

    @classmethod
    def setUpClass(cls):
        cls.s = carregar()

    def tb(self, final, local='  File "/x/tests/test_a.py", line 7, in test_a\n'):
        return "Traceback (most recent call last):\n" + local + final

    def test_tipos(self):
        casos = {
            "timeout": ("test_a.T.test_a", self.tb("subprocess.TimeoutExpired: Command 'x' timed out after 5 seconds\n")),
            "teste-de-tempo": ("test_a.T.test_prazo_vence", self.tb("AssertionError: 3 != 4\n")),
            "saida-grande": ("test_a.T.test_a", self.tb("AssertionError: " + "x" * 5000 + "\n")),
            "assercao": ("test_a.T.test_a", self.tb("AssertionError: 3 != 4\n")),
            "erro": ("test_a.T.test_a", self.tb("KeyError: 'k'\n")),
        }
        for tipo, (ident, texto) in casos.items():
            with self.subTest(tipo):
                self.assertEqual(self.s.causa_da_falha(ident, texto)["tipo"], tipo)

    def test_esperado_obtido_e_local_redigidos(self):
        causa = self.s.causa_da_falha("test_a.T.test_a", self.tb("AssertionError: 'senha: abc123' != 'sk-" + "b" * 24 + "'\n"))
        self.assertEqual(causa.get("local"), "tests/test_a.py:7")
        self.assertEqual(causa.get("obtido"), "'[redigido]")
        self.assertEqual(causa.get("esperado"), "'[redigido]'")
        sem_local = self.s.causa_da_falha("test_a.T.test_a", self.tb("ValueError: x\n", local=""))
        self.assertNotIn("local", sem_local)
        self.assertNotIn("esperado", sem_local)
        self.assertEqual(len(self.s.causa_da_falha("t", self.tb("AssertionError: " + "y" * 900 + " != 1\n"))["obtido"]),
                         self.s.TETO_DO_VALOR)


class TemposAoVivoLogica(unittest.TestCase):
    """O leitor do arquivo de tempos e o `esperar` (E23.27), sem subprocesso e sem depender de temporização."""

    @classmethod
    def setUpClass(cls):
        cls.s = carregar()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.pasta = Path(self._tmp.name)
        self.arquivo = self.pasta / "p1.saida.json.tempos"
        self.ao_vivo = self.s.TemposAoVivo(self.pasta, 1)

    def anexa(self, texto):
        with self.arquivo.open("a", encoding="utf-8") as f:
            f.write(texto)

    def atualiza(self):
        with mock.patch.object(sys, "stderr", io.StringIO()) as erro:
            self.ao_vivo.atualizar()
        return erro.getvalue()

    def test_linha_parcial_nao_abre_unidade_nem_avanca_a_posicao(self):
        self.anexa("inicio\tx\t1")  # sem \n: o filho ainda está escrevendo
        self.assertEqual(self.atualiza(), "")
        self.assertEqual((self.ao_vivo.posicao, self.ao_vivo.rodando()), ([0], []))
        self.anexa("00.5\n")
        self.atualiza()
        self.assertEqual([n for n, _, _ in self.ao_vivo.rodando()], ["x"])

    def test_inicio_abre_e_fim_fecha_e_imprime_uma_vez(self):
        self.anexa("inicio\tx\t100.5\n")
        self.assertEqual(self.atualiza(), "")
        self.assertEqual([(n, i) for n, _, i in self.ao_vivo.rodando()], [("x", 1)])
        self.anexa("fim\tx\t2.5\n")
        self.assertEqual(self.atualiza(), "suite-paralela: unidade x 2.5 s (processo 1)\n")
        self.assertEqual(self.ao_vivo.rodando(), [])
        self.assertEqual(self.atualiza(), "")  # nada novo: não repete a linha

    def test_posicao_avanca_por_linha_tratada(self):
        self.anexa("inicio\tx\t1.0\nfim\tx\t0.1\ninicio\ty\t2.0\n")
        impressas = []
        original = self.s.TemposAoVivo.informar
        def interrompe(texto):
            impressas.append(texto)
            raise KeyboardInterrupt  # o sinal chega no meio do laço, na impressão da primeira linha `fim`
        with mock.patch.object(self.s.TemposAoVivo, "informar", staticmethod(interrompe)):
            with self.assertRaises(KeyboardInterrupt):
                self.ao_vivo.atualizar()
        self.assertEqual(self.ao_vivo.posicao, [len("inicio\tx\t1.0\n")])  # a linha `fim` ainda não foi tratada até o fim
        with mock.patch.object(self.s.TemposAoVivo, "informar", staticmethod(original)):
            self.atualiza()
        self.assertEqual(self.ao_vivo.posicao, [len("inicio\tx\t1.0\nfim\tx\t0.1\ninicio\ty\t2.0\n")])
        self.assertEqual([n for n, _, _ in self.ao_vivo.rodando()], ["y"])

    def test_stderr_quebrado_nao_derruba_e_a_linha_sai_com_flush(self):
        class Quebrado:
            def write(self, _):
                raise BrokenPipeError

            flush = write

        self.anexa("inicio\tx\t1.0\nfim\tx\t0.1\ninicio\ty\t1.0\n")
        with mock.patch.object(sys, "stderr", Quebrado()):
            try:
                self.ao_vivo.atualizar()
                self.ao_vivo.imprimir_rodando()
            except OSError as erro:
                self.fail(f"stderr quebrado derrubou a suíte: {type(erro).__name__} escapou do informar")
        self.assertEqual([n for n, _, _ in self.ao_vivo.rodando()], ["y"])

        class Registra(io.StringIO):
            descargas = 0

            def flush(self):
                type(self).descargas += 1
                super().flush()

        with mock.patch.object(sys, "stderr", Registra()):
            self.s.TemposAoVivo.informar("a")
            self.s.TemposAoVivo.informar("b")
        self.assertEqual(Registra.descargas, 2)  # o flush de cada linha informada (QA A2)

    def test_esperar_atualiza_no_laco_e_uma_vez_depois_de_esperar_os_filhos(self):
        class Filho:
            def __init__(self):
                self.estados = [None, 0]

            def poll(self):
                return self.estados.pop(0) if len(self.estados) > 1 else self.estados[0]

            def wait(self):
                return 0

        class Leitor:
            chamadas = 0

            def atualizar(self):
                type(self).chamadas += 1

        with mock.patch.object(self.s.time, "sleep"):
            self.assertEqual(len(self.s.esperar([Filho()], self.s.time.monotonic(), Leitor())), 1)
            self.assertEqual(Leitor.chamadas, 3)  # a volta em que o filho ainda roda, a em que termina e a final
            self.assertEqual(len(self.s.esperar([Filho()], self.s.time.monotonic())), 1)  # sem leitor, sem erro


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
        (self.repo / "tests" / "config.json").write_text('{"teto_pulados": 0}')  # T3: no CI o teto é obrigatório
        for nome in ("a", "b", "c"):
            self.modulo(nome, modulo_de_teste(nome))
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "x")
        self.env = dict(AMBIENTE, MARCAS=str(self.marcas), TMPDIR=str(self.tmpdir), FORGE_SUITE_PROCS="3", FORGE_PREPUSH_SUITE="afetados",  # ENVIO-LEVE: o padrão do hook não roda teste
                        XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(base / "home"), FORGE_TRAVA_ESPERA="20")
        self.env.pop("FORGE_SUITE_TRAVA", None)
        self.env.pop("CI", None)
        self.env.pop("GITHUB_ACTIONS", None)
        self.env.pop("GITHUB_STEP_SUMMARY", None)
        # P11 da 0.43.1: o HOME deste processo também é o do brinquedo. `orquestrar_no_processo` e as funções do script
        # chamadas aqui leem `Path.home()`; com o HOME real, a suíte vermelha de brinquedo gravava `test_b.T.test_b` em
        # ~/.forge-contrib/suite-vermelha.jsonl, o registro das suítes vermelhas de verdade.
        home = mock.patch.dict(os.environ, {"HOME": self.env["HOME"]})
        home.start()
        self.addCleanup(home.stop)

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
        for linha in ("unidades mais lentas", "soma das unidades", "maior unidade", "desequilíbrio"):
            self.assertNotIn(linha, resumo)  # C-7: a medida da c2 só existe no resumo verde
        # QA-1: o resumo vermelho lista os testes que caíram, sem a mensagem da falha
        self.assertIn("#### Testes que caíram (1)\n- `test_b.T.test_b`\n", resumo)
        self.assertNotIn("de propósito", resumo)

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

    def test_pre_push_com_processo_morto_nao_anota_prova_nem_carimbo(self):  # versao-046 E2c/C-3 (MAQ-A2)
        # O OOM killer mata um processo da suíte: o envio reprova, sem a prova `.verde` do pre-push nem o carimbo K6.
        self.modulo("b", modulo_de_teste("b", "os.kill(os.getpid(), signal.SIGKILL)", "import signal\n"))
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "morto")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, env=AMBIENTE, capture_output=True,
                              text=True, check=True).stdout.strip()
        r = subprocess.run([str(self.repo / ".githooks" / "pre-push"), "origin", "u"], cwd=self.repo, env=self.env,
                           input=f"refs/heads/x {head} refs/heads/melhoria/x {'0' * 40}\n", capture_output=True,
                           text=True, timeout=120)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("morto pelo sinal 9", r.stderr)
        self.assertIn("testes do Forge falharam", r.stderr)
        self.assertFalse((self.run_dir / f"forge-suite-{os.getuid()}.verde").exists(), "suíte morta anotou a prova")
        self.assertFalse((self.repo / ".git" / "forge-suite-verde").exists(), "suíte morta gravou o carimbo")

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

    # ---- L32 (OK-3 e OK-13): o registro da suíte vermelha, fora do git ----
    def pasta_do_registro(self, existe=True):
        pasta = self.repo.parent / "home" / ".forge-contrib"
        if existe:
            pasta.mkdir(parents=True, mode=0o700)
        return pasta

    def vermelha(self, nome="b", mensagem="de propósito"):
        self.modulo(nome, modulo_de_teste(nome, f"self.fail({mensagem!r})"))
        return self.roda()

    def test_vermelha_grava_o_teste_que_caiu_a_carga_e_a_taxa_sem_a_mensagem(self):  # L32, C-32a, C-32b
        pasta = self.pasta_do_registro()
        codigo, saida, erro = self.vermelha(mensagem="segredo-da-mensagem")
        self.assertEqual(codigo, 1, saida + erro)
        arquivo = pasta / "suite-vermelha.jsonl"
        self.assertTrue(arquivo.exists(), "a suíte vermelha grava o registro")
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(linhas), 1, linhas)
        registro = json.loads(linhas[0])
        self.assertEqual(registro["testes"], [{"id": "test_b.T.test_b", "vezes": 1, "de": 1}])
        self.assertIn("carga", registro)
        self.assertNotIn("segredo-da-mensagem", arquivo.read_text(encoding="utf-8"))
        self.assertEqual(arquivo.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.roda()[0], 1)
        outra = json.loads(arquivo.read_text(encoding="utf-8").splitlines()[1])
        self.assertEqual(outra["testes"], [{"id": "test_b.T.test_b", "vezes": 2, "de": 2}])

    def test_causa_tipada_da_assercao_na_saida_e_no_registro(self):  # O7 (0.44.1): esperado, obtido e local, sem segredo
        pasta = self.pasta_do_registro()
        self.modulo("b", modulo_de_teste("b", "self.assertEqual('token=ghp_' + 'a' * 30, 'certo')"))
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 1, saida + erro)
        linha = next((l for l in erro.splitlines() if l.startswith("suite-paralela: causa ")), "")
        self.assertIn("tipo=assercao id=test_b.T.test_b local=tests/test_b.py:", linha)
        self.assertIn("esperado='certo'", linha)
        self.assertNotIn("ghp_", erro)
        registro = json.loads((pasta / "suite-vermelha.jsonl").read_text(encoding="utf-8"))
        causa = registro["causas"][0]
        self.assertEqual((causa["id"], causa["tipo"], causa["esperado"]), ("test_b.T.test_b", "assercao", "'certo'"))
        self.assertRegex(causa["local"], r"^tests/test_b\.py:\d+$")
        self.assertIn("[redigido]", causa["obtido"])
        self.assertNotIn("ghp_", json.dumps(registro))

    def test_processo_morto_sai_com_a_causa_sinal(self):  # O7
        self.pasta_do_registro()
        self.modulo("b", modulo_de_teste("b", "os.kill(os.getpid(), signal.SIGKILL)", "import signal\n"))
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("tipo=sinal id=processo", erro)
        self.assertIn(f"sinal={int(signal.SIGKILL)}", erro)

    def test_suite_verde_nao_grava_o_registro(self):  # L32
        pasta = self.pasta_do_registro()
        self.assertEqual(self.roda()[0], 0)
        self.assertFalse((pasta / "suite-vermelha.jsonl").exists())

    def test_sem_a_pasta_o_registro_nao_a_cria_e_o_veredito_e_o_mesmo(self):  # L32, T-32
        pasta = self.pasta_do_registro(existe=False)
        codigo, saida, _ = self.vermelha()
        self.assertEqual(codigo, 1)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED (failures=1"), saida)
        self.assertFalse(pasta.exists())
        self.assertNotIn("registro indisponível", self.vermelha("b")[2])  # a pasta ausente não é erro, só não há registro

    def test_no_ci_o_registro_nao_grava(self):  # L32: o runner não tem ~/.forge-contrib
        pasta = self.pasta_do_registro()
        self.modulo("b", modulo_de_teste("b", "self.fail('x')"))
        self.assertEqual(self.roda(GITHUB_ACTIONS="true")[0], 1)
        self.assertFalse((pasta / "suite-vermelha.jsonl").exists())

    def test_processo_morto_nao_impede_o_registro_dos_testes_que_cairam(self):  # L32: o relatório de quem morreu é None
        pasta = self.pasta_do_registro()
        self.modulo("b", modulo_de_teste("b", "os.kill(os.getpid(), signal.SIGKILL)", "import signal\n"))
        self.modulo("c", modulo_de_teste("c", "self.fail('x')"))
        self.assertEqual(self.roda()[0], 1)
        self.assertTrue((pasta / "suite-vermelha.jsonl").exists(), "o relatório que falta não derruba o registro")
        registro = json.loads((pasta / "suite-vermelha.jsonl").read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual([t["id"] for t in registro["testes"]], ["test_c.T.test_c"])

    def test_o_id_gravado_so_leva_caractere_imprimivel(self):  # L32, C-32b
        pasta = self.pasta_do_registro()
        extra = "setattr(T, 'test_b\\x1b[31m', lambda self: self.fail('x'))\n"
        self.modulo("b", modulo_de_teste("b", "pass") + extra)
        self.assertEqual(self.roda()[0], 1)
        texto = (pasta / "suite-vermelha.jsonl").read_text(encoding="utf-8")
        self.assertIn("test_b.T.test_b[31m", texto)
        self.assertNotIn("\x1b", texto)

    def test_orquestrar_no_processo_grava_o_registro_so_no_home_do_brinquedo(self):  # P11 da 0.43.1
        pasta = self.pasta_do_registro()
        self.modulo("b", modulo_de_teste("b", "self.fail('x')"))
        codigo, saida, erro = self.orquestrar_no_processo(self.script_do_brinquedo(), FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 1, saida + erro)
        self.assertEqual(Path.home(), pasta.parent)
        registro = json.loads((pasta / "suite-vermelha.jsonl").read_text(encoding="utf-8"))
        self.assertEqual([t["id"] for t in registro["testes"]], ["test_b.T.test_b"])

    def test_sem_a_leitura_da_memoria_o_registro_grava_nulo(self):  # L32: /proc/meminfo ilegível
        pasta = self.pasta_do_registro()
        script = self.script_do_brinquedo()
        relatorios = [{"caidos": ["test_b.T.test_b"]}, None]
        with mock.patch.dict(os.environ, {"HOME": str(pasta.parent), "GITHUB_ACTIONS": ""}):
            script.registrar_vermelha(relatorios, 1.5, None)
        self.assertTrue((pasta / "suite-vermelha.jsonl").exists(), "a memória ilegível não derruba o registro")
        registro = json.loads((pasta / "suite-vermelha.jsonl").read_text(encoding="utf-8"))
        self.assertEqual((registro["carga"], registro["memoria_gb"]), (1.5, None))

    def test_pasta_ou_arquivo_que_e_link_recusa_sem_gravar_e_sem_mudar_o_veredito(self):  # L32, C-32a, T-32
        alvo = self.repo.parent / "alvo"
        alvo.mkdir()
        pasta = self.pasta_do_registro(existe=False)
        pasta.parent.mkdir(parents=True)
        pasta.symlink_to(alvo)
        codigo, saida, _ = self.vermelha()
        self.assertEqual(codigo, 1)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED (failures=1"), saida)
        self.assertFalse((alvo / "suite-vermelha.jsonl").exists(), "a pasta que é link não recebe o registro")
        pasta.unlink()
        pasta.mkdir(mode=0o700)
        (pasta / "suite-vermelha.jsonl").symlink_to(alvo / "destino")
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertFalse((alvo / "destino").exists(), "o arquivo que é link não recebe o registro")
        self.assertIn("registro indisponível", erro)

    def test_pasta_gravavel_por_outros_recusa(self):  # L32, C-32a
        pasta = self.pasta_do_registro()
        pasta.chmod(0o777)
        self.assertEqual(self.vermelha()[0], 1)
        self.assertFalse((pasta / "suite-vermelha.jsonl").exists())

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

    # N-CI, item 55 d: a medida no resumo do CI (C-9, C-11, C-12); nada disso muda o veredito, a divisão nem o carimbo.

    def test_resumo_do_ci_traz_as_unidades_mais_lentas(self):
        self.modulo("b", modulo_de_teste("b", "time.sleep(0.6)", "import time\n"))
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 0, saida + erro)
        lentas = resumo.split("unidades mais lentas", 1)[1].splitlines()
        self.assertRegex(lentas[1], r"^- test_b: \d+\.\d s$")

    def test_resumo_do_ci_traz_soma_maior_unidade_e_desequilibrio(self):
        self.modulo("b", modulo_de_teste("b", "time.sleep(0.6)", "import time\n"))
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertRegex(resumo, r"- soma das unidades: \d+\.\d s; soma ÷ 3 processos: \d+\.\d s")
        self.assertRegex(resumo, r"- maior unidade: test_b \(\d+\.\d s\)")
        self.assertRegex(resumo, r"- desequilíbrio: \d+\.\d s \(\d+% da média dos processos\)")

    def test_resumo_do_ci_lista_os_modulos_sem_peso(self):
        (self.repo / "tests" / "pesos-d4.json").write_text('{"test_a": 1.0}\n')
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertIn("- sem peso em tests/pesos-d4.json: test_b, test_c\n", resumo)

    def test_resumo_limita_as_unidades_sem_peso(self):  # AB-6, C-11
        for i in range(27):
            self.modulo(f"n{i:02d}", modulo_de_teste(f"n{i:02d}"))
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 0, saida + erro)
        (sem_peso,) = [linha for linha in resumo.splitlines() if linha.startswith("- sem peso")]
        self.assertTrue(sem_peso.endswith(" e mais 10"), sem_peso)
        self.assertEqual(sem_peso.count("test_"), 20, sem_peso)
        lentas = resumo.split("unidades mais lentas", 1)[1].split("\n- soma", 1)[0]
        self.assertEqual(lentas.count("\n- test_"), 10)

    def test_grupo_do_ci_traz_as_unidades_do_processo(self):
        codigo, saida, erro = self.roda(GITHUB_ACTIONS="true")
        self.assertEqual(codigo, 0, saida + erro)
        grupos = [linha for linha in saida.splitlines() if linha.startswith("::group::")]
        self.assertEqual(len(grupos), 3)
        self.assertEqual(sorted(g.split(" (")[1] for g in grupos), ["test_a)", "test_b)", "test_c)"])
        self.assertTrue(all(g.startswith("::group::processo ") for g in grupos), grupos)

    def test_resumo_so_leva_nomes_e_numeros(self):  # AB-4, C-9
        corpo = ('print("::error::falso\\n::stop-commands::x\\n/etc/passwd\\nghp_" + "A" * 36); '
                 'import sys; print("::warning::falso", file=sys.stderr)')
        self.modulo("b", modulo_de_teste("b", corpo))
        codigo, saida, erro, resumo = self.resumo_do_ci()
        self.assertEqual(codigo, 0, saida + erro)
        for texto in ("::", "falso", "/etc", "ghp_", "AAAA"):
            self.assertNotIn(texto, resumo)

    def test_sem_github_step_summary_nada_e_escrito(self):
        codigo, saida, erro = self.roda()
        self.assertEqual(codigo, 0, saida + erro)
        self.assertNotIn("resumo indisponível", erro)
        self.assertFalse((self.repo.parent / "resumo.md").exists())

    def test_divisao_nao_depende_da_execucao_anterior(self):  # AB-7, C-12
        divisoes = []
        for demora in ("0", "0.5"):
            self.modulo("a", modulo_de_teste("a", "time.sleep(float(os.environ['DORME']))", "import time\n"))
            codigo, saida, erro = self.roda(DORME=demora, FORGE_SUITE_SEM_REUSO="1")
            self.assertEqual(codigo, 0, saida + erro)
            divisoes.append(sorted(linha.split("(", 1)[1] for linha in saida.splitlines() if linha.startswith("--- processo")))
        self.assertEqual(divisoes[0], divisoes[1])

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

    def test_modulo_com_chave_separada_divide_os_testes_entre_os_processos(self):  # S-SUITE-RAPIDA
        self.modulo("a", modulo_de_teste("a") + EXTRA_DO_A)
        (self.repo / "tests" / "pesos-d4.json").write_text(json.dumps(
            {"test_a": 1.0, "test_a.T.test_a2": 9.0, "test_a.U": 8.0, "test_b": 1.0, "test_c": 1.0}))
        codigo, saida, erro = self.roda(FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 0, saida + erro)
        self.assertIn("Ran 5 tests", saida)
        self.assertEqual(self.rodaram(), ["a", "a2", "a3", "b", "c"])  # cada teste uma vez só
        pids = {n.name.rsplit("-", 1)[0]: n.name.rsplit("-", 1)[1] for n in self.marcas.iterdir()}
        self.assertEqual(len({pids["a"], pids["a2"], pids["a3"]}), 3, "o módulo pesado se divide entre os processos")
        self.assertIn("test_a.T.test_a2", saida)
        # MEDIR grava o peso de cada unidade, inclusive as separadas
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "y")
        codigo, saida, erro = self.roda(FORGE_SUITE_MEDIR="1", FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 0, saida + erro)
        pesos = json.loads((self.repo / "tests" / "pesos-d4.json").read_text())
        self.assertEqual(sorted(pesos), ["test_a", "test_a.T.test_a2", "test_a.U", "test_b", "test_c"])

    def test_modulo_de_pacote_entra_pelo_nome_com_ponto(self):  # S-SUITE-RAPIDA: tests/<pacote>/ (ex.: tests/evals/)
        (self.repo / "tests" / "pac").mkdir()
        (self.repo / "tests" / "pac" / "__init__.py").write_text("")
        (self.repo / "tests" / "pac" / "test_p.py").write_text(modulo_de_teste("p"))
        (self.repo / "tests" / "solta").mkdir()  # sem __init__.py: o discover não entra, e a divisão também não
        (self.repo / "tests" / "solta" / "test_s.py").write_text(modulo_de_teste("s"))
        script = self.script_do_brinquedo()
        self.assertEqual(script.modulos(), ["pac.test_p", "test_a", "test_b", "test_c"])
        codigo, saida, erro = self.roda(FORGE_SUITE_SEM_REUSO="1", FORGE_SUITE_MEDIR="1")
        self.assertEqual(codigo, 0, saida + erro)
        self.assertIn("Ran 4 tests", saida)
        self.assertEqual(self.rodaram(), ["a", "b", "c", "p"])
        self.assertIn("pac.test_p", saida)
        pesos = json.loads((self.repo / "tests" / "pesos-d4.json").read_text())
        self.assertEqual(sorted(pesos), ["pac.test_p", "test_a", "test_b", "test_c"])

    def test_nome_de_arquivo_repetido_no_pacote_reprova_a_divisao(self):  # S-SUITE-RAPIDA
        (self.repo / "tests" / "pac").mkdir()
        (self.repo / "tests" / "pac" / "__init__.py").write_text("")
        (self.repo / "tests" / "pac" / "test_a.py").write_text(modulo_de_teste("a2"))
        codigo, saida, erro = self.roda(FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 1, saida + erro)
        self.assertIn("nome de arquivo repetido em tests/ e nos pacotes dela: pac.test_a, test_a", erro)
        self.assertEqual(saida.strip().splitlines()[-1], "FAILED (divisão)")
        self.assertEqual(self.rodaram(), [])

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
        saida, erro = self.termina(p)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("interrompida", erro)
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED"))
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        self.assertEqual(list(self.tmpdir.iterdir()), [])


    BLOQUEADO = MARCA + '''
import time
class T(unittest.TestCase):
    def test_b(self):
        marca("b")
        for _ in range(600):
            if (pathlib.Path(os.environ["MARCAS"]) / "liberar").exists():
                return
            time.sleep(0.1)
'''

    def sobe_com_b_bloqueado(self):
        self.modulo("b", self.BLOQUEADO)
        p = subprocess.Popen([sys.executable, str(self.repo / "scripts" / "suite-paralela.py")], cwd=self.repo,
                             env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: p.poll() is None and p.kill())
        return p

    def termina(self, p):
        """O que falta de stdout e stderr, lido dos próprios objetos: o `communicate` lê do descritor e perde o que o
        `readline` do `le_ate` já puxou para o buffer (a linha de test_c vinha junto da de test_a sob carga)."""
        temporizador = threading.Timer(30, p.kill)
        temporizador.start()
        try:
            saida, erro = p.stdout.read(), p.stderr.read()
            p.wait()
        finally:
            temporizador.cancel()
            p.stdout.close()
            p.stderr.close()
        return saida, erro

    def le_ate(self, p, trecho):
        """Lê o stderr ao vivo até a linha com `trecho`; devolve as linhas lidas (o módulo b segue bloqueado)."""
        linhas, fim = [], time.monotonic() + 30
        while time.monotonic() < fim:
            linha = p.stderr.readline()
            if not linha:
                break
            linhas.append(linha)
            if trecho in linha:
                return linhas
        self.fail(f"sem a linha {trecho!r} antes do fim: {linhas}")

    def test_linha_por_modulo_sai_antes_do_fim(self):  # E23.23
        p = self.sobe_com_b_bloqueado()
        linhas = self.le_ate(p, "unidade test_a ")
        self.assertIsNone(p.poll(), "a linha do test_a tem de sair com a suíte ainda rodando (test_b bloqueado)")
        self.assertRegex(linhas[-1], r"^suite-paralela: unidade test_a \d+\.\d s \(processo \d\)$")
        (self.marcas / "liberar").write_text("")
        saida, erro = self.termina(p)
        self.assertEqual(p.returncode, 0, saida + erro)
        self.assertEqual(saida.strip().splitlines()[-1], "OK")  # a saída final não mudou
        tudo = "".join(linhas) + erro
        for nome in ("test_a", "test_b", "test_c"):
            self.assertIn(f"suite-paralela: unidade {nome} ", tudo)

    def test_sigterm_deixa_o_resumo_de_quem_rodava(self):  # E23.23
        p = self.sobe_com_b_bloqueado()
        self.le_ate(p, "unidade test_a ")
        fim = time.monotonic() + 30
        while time.monotonic() < fim and not any(n.name.startswith("b-") for n in self.marcas.iterdir()):
            time.sleep(0.05)
        time.sleep(0.5)  # o `inicio` de test_b já está no arquivo de tempos; dá folga para a leitura marcar um tempo > 0
        p.send_signal(signal.SIGTERM)
        saida, erro = self.termina(p)
        self.assertNotEqual(p.returncode, 0)
        self.assertRegex(erro, r"suite-paralela: rodando test_b há \d+\.\d s \(processo \d\)")
        self.assertNotIn("rodando test_a", erro)  # o que terminou não entra no resumo de quem rodava
        self.assertTrue(saida.strip().splitlines()[-1].startswith("FAILED"))


class TetoDePulados(unittest.TestCase):
    """T3 (0.43.2): no CI, mais pulados que `teto_pulados` reprova; teto ilegível reprova; fora do CI só avisa."""

    setUp, roda, modulo, resumo_do_ci, git = (Brinquedo.setUp, Brinquedo.roda, Brinquedo.modulo, Brinquedo.resumo_do_ci,
                                              Brinquedo.git)

    def com_pulado(self, teto):
        corpo = 'with self.subTest("a|b`c::d\\x07"): self.skipTest("motivo-secreto")'
        self.modulo("b", modulo_de_teste("b", corpo))
        (self.repo / "tests" / "config.json").write_text(teto if isinstance(teto, str) else json.dumps(teto))

    def no_ci(self, teto, **extra):
        self.com_pulado(teto)
        return self.roda(GITHUB_ACTIONS="true", FORGE_SUITE_SEM_REUSO="1", **extra)

    def test_acima_do_teto_reprova_com_os_ids_neutros_no_resumo(self):
        self.com_pulado({"teto_pulados": 0})
        codigo, saida, erro, resumo = self.resumo_do_ci(GITHUB_ACTIONS="true", FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual(codigo, 1, saida + erro)
        self.assertEqual(saida.strip().splitlines()[-1], "FAILED (skipped=1 acima do teto 0)")
        (linha,) = [x for x in resumo.splitlines() if "pulados acima do teto" in x]
        self.assertIn("test_b.T.test_b", linha)
        for proibido in ("|", "`", "::", "\x07", "motivo-secreto"):
            self.assertNotIn(proibido, linha)

    def test_no_teto_passa_e_abaixo_avisa_que_pode_cair(self):
        codigo, saida, erro = self.no_ci({"teto_pulados": 1})
        self.assertEqual((codigo, saida.strip().splitlines()[-1]), (0, "OK (skipped=1)"), saida + erro)
        self.assertNotIn("pode cair", erro)
        codigo, saida, erro = self.no_ci({"teto_pulados": 3})
        self.assertEqual(codigo, 0, saida + erro)
        self.assertIn("o teto de pulados pode cair para 1", erro)

    def test_teto_ilegivel_reprova_no_ci(self):
        for teto in ({}, {"teto_pulados": "x"}, {"teto_pulados": True}, {"teto_pulados": None},
                     {"teto_pulados": 1.0}, {"teto_pulados": -1}, [1], "{quebrado"):
            with self.subTest(teto=teto):
                codigo, saida, erro = self.no_ci(teto)
                self.assertEqual(codigo, 1, saida + erro)
                self.assertEqual(saida.strip().splitlines()[-1], "FAILED (teto de pulados ilegível)")
        (self.repo / "tests" / "config.json").unlink()
        codigo, saida, _ = self.roda(GITHUB_ACTIONS="true", FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual((codigo, saida.strip().splitlines()[-1]), (1, "FAILED (teto de pulados ilegível)"))

    def test_fora_do_ci_so_avisa(self):
        self.com_pulado({"teto_pulados": 0})
        codigo, saida, erro = self.roda(FORGE_SUITE_SEM_REUSO="1")
        self.assertEqual((codigo, saida.strip().splitlines()[-1]), (0, "OK (skipped=1)"), saida + erro)
        self.assertIn("pulados 1 (teto 0; só reprova no CI)", erro)

    def test_estourado_nao_regrava_os_pesos(self):
        pesos = self.repo / "tests" / "pesos-d4.json"
        pesos.write_text("{}\n")
        codigo, saida, erro = self.no_ci({"teto_pulados": 0}, FORGE_SUITE_MEDIR="1")
        self.assertEqual(codigo, 1, saida + erro)
        self.assertEqual(pesos.read_text(), "{}\n")


if __name__ == "__main__":
    unittest.main()
