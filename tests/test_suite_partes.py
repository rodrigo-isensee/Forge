"""SUITE-NO-CI: scripts/suite-partes.py roda uma parte da suíte (os afetados de um envio ou um terço da suíte no CI) sobre
o mecanismo do scripts/suite-paralela.py, sem perder teste.

A lógica pura é testada importando o script; o resto roda o script de verdade num repositório de brinquedo (cópia dos dois
scripts e dos módulos de apoio, com uma suíte mínima), com HOME temporário. Classe do defeito: uma parte (ou a soma das
partes) rodar menos do que o discover acha, e o CI dar verde sem a suíte inteira. Variantes: módulos pedidos, módulo que
falha, módulo inexistente, as três partes somadas, teste fora dos módulos da divisão, parte fora do intervalo e fora do CI,
e a fiação do ci.yml (partes por versão e agregadores com o nome do check exigido).
"""
import collections
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "suite-partes.py"
CI = RAIZ / ".github" / "workflows" / "ci.yml"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items()
                           if not k.startswith(("GIT_", "FORGE_SUITE_", "GITHUB_")) and k != "CI"})
ESPERA = re.compile(r"\$\{\{[^}]*outputs\.espera[^}]*\}\}$")  # E47.1/E47.6: sufixo da espera no nome do agregador

MODULO = '''import os, pathlib, unittest

class T(unittest.TestCase):
    def test_{nome}(self):
        (pathlib.Path(os.environ["MARCAS"]) / "{nome}").write_text("x")
        {corpo}
'''


def carregar():
    spec = importlib.util.spec_from_file_location("suite_partes", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Logica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = carregar()
        cls.sp = cls.f.carregar_paralela()

    def test_ler_parte(self):
        self.assertEqual(self.f.ler_parte("2/3"), (2, 3))
        for ruim in ("0/3", "4/3", "1/0", "a/3", "1/3/", "", "-1/3", "1 /3"):
            with self.subTest(ruim):
                with self.assertRaises(ValueError):
                    self.f.ler_parte(ruim)

    def test_fora_da_divisao_e_modulo_do_id(self):
        total = collections.Counter({"test_a.T.test_x": 1, "test_b.T.test_y": 2, "unittest.loader._FailedTest.test_c": 1})
        self.assertEqual(self.f.fora_da_divisao(total, ["test_a", "test_b"]), ["unittest.loader._FailedTest.test_c"])
        self.assertEqual(self.f.modulo_do_id("evals.test_p.T.x", {"evals.test_p", "test_p"}), "evals.test_p")



class Brinquedo(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        base = Path(self._t.name)
        self.dir, self.marcas, self.home = base / "repo", base / "marcas", base / "home"
        for pasta in (self.dir / "tests", self.dir / "scripts", self.marcas, self.home):
            pasta.mkdir(parents=True)
        for origem in ("scripts/suite-paralela.py", "scripts/suite-partes.py", "tests/guarda_git.py", "tests/ambiente_git.py"):
            (self.dir / origem).write_bytes((RAIZ / origem).read_bytes())
        for nome in ("a", "b", "c", "d", "e"):
            self.modulo(nome)
        (self.dir / ".gitignore").write_text("__pycache__/\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.dir, env=AMBIENTE, check=True, capture_output=True)

    def modulo(self, nome, corpo="pass"):
        (self.dir / "tests" / f"test_{nome}.py").write_text(MODULO.format(nome=nome, corpo=corpo))

    def roda(self, *args, ci=False):
        env = dict(AMBIENTE, MARCAS=str(self.marcas), HOME=str(self.home), **({"CI": "true"} if ci else {}))
        r = subprocess.run([sys.executable, "scripts/suite-partes.py", *args], cwd=self.dir, env=env,
                           capture_output=True, text=True, timeout=120)
        rodaram = {p.name for p in self.marcas.iterdir()}
        for p in self.marcas.iterdir():
            p.unlink()
        return r, rodaram

    def test_modulos_rodam_so_os_pedidos(self):
        r, rodaram = self.roda("--modulos", "test_a,test_c")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(rodaram, {"a", "c"})
        self.assertEqual(r.stdout.strip().splitlines()[-1], "OK")
        self.assertIn("afetados: 2 testes em 2 módulos", r.stderr)

    def test_modulo_que_falha_reprova(self):
        self.modulo("b", "self.fail('de propósito')")
        r, _ = self.roda("--modulos", "test_a,test_b")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertTrue(r.stdout.strip().splitlines()[-1].startswith("FAILED"))
        self.assertIn("suite-paralela: causa tipo=assercao id=test_b.", r.stderr)  # O7 (0.44.1): a causa tipada no dirigido

    def test_modulo_inexistente_ou_fora_do_padrao_e_uso_invalido(self):
        for pedido in ("test_zz", "os", "", "test_a,../x"):
            with self.subTest(pedido):
                r, rodaram = self.roda("--modulos", pedido)
                self.assertEqual((r.returncode, rodaram), (2, set()), r.stdout + r.stderr)

    def test_as_tres_partes_somam_a_suite_inteira_sem_repetir(self):
        vistos = []
        for k in (1, 2, 3):
            r, rodaram = self.roda("--parte", f"{k}/3", ci=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(rodaram)
            vistos += sorted(rodaram)
        self.assertEqual(sorted(vistos), ["a", "b", "c", "d", "e"])

    def pacote(self, nome="sub", modulo="escondido"):
        (self.dir / "tests" / nome).mkdir(exist_ok=True)
        (self.dir / "tests" / nome / "__init__.py").write_text("")
        (self.dir / "tests" / nome / f"test_{modulo}.py").write_text(MODULO.format(nome=modulo, corpo="pass"))
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", nome)

    def test_modulo_de_pacote_entra_na_divisao_e_nos_modulos_pedidos(self):  # tests/evals/ da 0.43.1
        self.pacote()
        vistos = []
        for k in (1, 2, 3):
            r, rodaram = self.roda("--parte", f"{k}/3", ci=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            vistos += sorted(rodaram)
        self.assertEqual(sorted(vistos), ["a", "b", "c", "d", "e", "escondido"])
        r, rodaram = self.roda("--modulos", "sub.test_escondido,test_a")
        self.assertEqual((r.returncode, rodaram), (0, {"a", "escondido"}), r.stdout + r.stderr)

    def test_nome_de_arquivo_repetido_num_pacote_reprova(self):  # o filho acha o módulo pelo nome do arquivo
        self.pacote(modulo="a")
        codigos = [self.roda("--parte", f"{k}/3", ci=True)[0].returncode for k in (1, 2, 3)]
        self.assertIn(1, codigos)  # a parte com test_a ou sub.test_a reprova
        self.assertEqual(set(codigos) - {0, 1}, set())
        r, rodaram = self.roda("--modulos", "test_a")
        self.assertEqual((r.returncode, rodaram), (1, set()), r.stdout + r.stderr)
        self.assertIn("nome de arquivo repetido", r.stderr)

    def test_falha_de_carga_fica_fora_da_divisao_e_reprova_toda_parte(self):
        (self.dir / "tests" / "test_quebrado.py").write_text("import modulo_que_nao_existe\n")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "quebrado")
        for k in (1, 2, 3):
            r, rodaram = self.roda("--parte", f"{k}/3", ci=True)
            self.assertEqual((r.returncode, rodaram), (1, set()), r.stdout + r.stderr)
            self.assertIn("fora dos módulos da divisão", r.stderr)

    def test_parte_fora_do_ci_ou_fora_do_intervalo_e_uso_invalido(self):
        self.assertEqual(self.roda("--parte", "1/3")[0].returncode, 2)
        for ruim in ("4/3", "0/3", "x"):
            with self.subTest(ruim):
                self.assertEqual(self.roda("--parte", ruim, ci=True)[0].returncode, 2)

    def test_sem_argumento_ou_opcao_desconhecida_e_uso_invalido(self):
        for args in ((), ("--todas",), ("--parte",)):
            with self.subTest(args):
                self.assertEqual(self.roda(*args)[0].returncode, 2)


class UnidadesSeparadas(unittest.TestCase):
    """A3 (review de correção da 0.43.1): a parte e os afetados abrem as unidades separadas nos pesos (`módulo.Classe`) em
    processos próprios, como o suite-paralela, e a divisão do CI pesa o módulo com as unidades dele."""

    setUp, git, modulo, roda = Brinquedo.setUp, Brinquedo.git, Brinquedo.modulo, Brinquedo.roda

    def test_unidade_separada_vai_a_outro_processo_sem_perder_teste(self):
        (self.dir / "tests" / "test_z.py").write_text(
            MODULO.format(nome="z", corpo="pass") + "\n\nclass U(unittest.TestCase):\n    def test_u(self):\n"
            "        (pathlib.Path(os.environ['MARCAS']) / 'u').write_text('x')\n")
        (self.dir / "tests" / "pesos-d4.json").write_text(json.dumps({"test_z": 1.0, "test_z.U": 5.0}))
        with unittest.mock.patch.dict(AMBIENTE, {"FORGE_SUITE_PROCS": "4"}):
            r, rodaram = self.roda("--modulos", "test_z")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(rodaram, {"z", "u"})
        self.assertIn("afetados: 2 testes em 1 módulos, 2 processos", r.stderr)


class PuladosDasPartes(unittest.TestCase):
    """T3: a parte verde grava os pulados em FORGE_SUITE_PULADOS; `--somar-pulados` soma as N contra `teto_pulados`."""

    setUp, git, modulo, roda = Brinquedo.setUp, Brinquedo.git, Brinquedo.modulo, Brinquedo.roda

    def partes(self, teto):
        (self.dir / "tests" / "config.json").write_text(json.dumps({"teto_pulados": teto}))
        self.modulo("b", 'self.skipTest("de propósito")')
        self.pasta = Path(self._t.name) / "pulados"
        for k in (1, 2, 3):
            env_extra = {"FORGE_SUITE_PULADOS": str(self.pasta / f"parte-{k}.json")}
            with unittest.mock.patch.dict(AMBIENTE, env_extra):
                r, _ = self.roda("--parte", f"{k}/3", ci=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_parte_grava_e_a_soma_no_teto_passa(self):
        self.partes(1)
        dados = [json.loads(p.read_text()) for p in sorted(self.pasta.glob("*.json"))]
        self.assertEqual(sorted(d["parte"] for d in dados), ["1/3", "2/3", "3/3"])
        self.assertEqual(sum(d["pulados"] for d in dados), 1)
        r, _ = self.roda("--somar-pulados", "3", str(self.pasta))
        self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (0, "OK (skipped=1)"), r.stderr)

    def test_soma_acima_do_teto_ou_teto_ilegivel_reprova(self):
        self.partes(0)
        r, _ = self.roda("--somar-pulados", "3", str(self.pasta))
        self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (1, "FAILED (skipped=1 acima do teto 0)"))
        self.assertIn("test_b.T.test_b", r.stderr)
        (self.dir / "tests" / "config.json").write_text('{"teto_pulados": "1"}')
        r, _ = self.roda("--somar-pulados", "3", str(self.pasta))
        self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (1, "FAILED (teto de pulados ilegível)"))

    def test_parte_faltando_repetida_ou_adulterada_reprova(self):
        self.partes(5)
        um = self.pasta / "parte-1.json"
        texto = um.read_text()
        casos = {"faltando": lambda: um.unlink(),
                 "repetida": lambda: (self.pasta / "outra.json").write_text(texto),
                 "outro N": lambda: um.write_text(texto.replace("1/3", "1/4")),
                 "contagem errada": lambda: um.write_text(json.dumps(dict(json.loads(texto), pulados=7))),
                 "ilegível": lambda: um.write_text("{quebrado")}
        for nome, estraga in casos.items():
            with self.subTest(nome):
                estraga()
                r, _ = self.roda("--somar-pulados", "3", str(self.pasta))
                self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (1, "FAILED (pulados das partes)"),
                                 r.stderr)
                (self.pasta / "outra.json").unlink(missing_ok=True)
                um.write_text(texto)
        for args in (("--somar-pulados", "0", str(self.pasta)), ("--somar-pulados", "x", str(self.pasta))):
            self.assertEqual(self.roda(*args)[0].returncode, 2)

    def test_parte_vermelha_nao_grava(self):
        self.modulo("a", "self.fail('de propósito')")
        pasta, codigos = Path(self._t.name) / "vermelha", {}
        for k in (1, 2, 3):
            with unittest.mock.patch.dict(AMBIENTE, {"FORGE_SUITE_PULADOS": str(pasta / f"parte-{k}.json")}):
                codigos[k] = self.roda("--parte", f"{k}/3", ci=True)[0].returncode
        self.assertEqual(sorted(codigos.values()), [0, 0, 1])
        for k, codigo in codigos.items():
            self.assertEqual((pasta / f"parte-{k}.json").exists(), codigo == 0, k)


class DivisaoPorUnidade(unittest.TestCase):
    """CI-RAPIDO (v047), S9: as partes dividem as UNIDADES do plano (módulo, módulo.Classe, módulo.Classe.teste), não só módulos,
    e a guarda de completude vale por ID. Classe do defeito: um ID fora de toda parte (a suíte inteira dar verde sem ele) ou
    em duas, ou uma parte vazia."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()
        cls.sp = cls.f.carregar_paralela()
        cls.pesos = {"test_a": 2.0, "test_a.K": 30.0, "test_a.K.test_x": 9.0, "test_b": 1.0}
        cls.total = collections.Counter({"test_a.T.test_p": 1, "test_a.K.test_q": 1, "test_a.K.test_x": 1,
                                         "test_b.T.test_y": 2})
        cls.nomes = ["test_a", "test_b"]

    def plano(self):
        return {"test_a": ("test_a", [0]), "test_a.K": ("test_a", [1]), "test_a.K.test_x": ("test_a", [2]),
                "test_b": ("test_b", None)}

    def test_unidade_do_id_e_a_chave_mais_longa_dos_pesos(self):
        casos = {"test_a.T.test_p": "test_a", "test_a.K.test_q": "test_a.K", "test_a.K.test_x": "test_a.K.test_x",
                 "test_b.T.test_y": "test_b"}
        for ident, unidade in casos.items():
            with self.subTest(ident):
                self.assertEqual(self.f.unidade_do_id(self.sp, ident, set(self.nomes), self.pesos), unidade)
        self.assertIsNone(self.f.unidade_do_id(self.sp, "unittest.loader._FailedTest.test_c", set(self.nomes), self.pesos))

    def test_esperado_por_unidade_reparte_o_discover_sem_perder_id(self):
        por = self.f.esperado_por_unidade(self.sp, self.total, self.nomes, self.pesos)
        self.assertEqual(set(por), set(self.plano()))
        self.assertEqual(sum(por.values(), collections.Counter()), self.total)
        self.assertEqual(por["test_b"], collections.Counter({"test_b.T.test_y": 2}))

    def test_completude_passa_com_a_particao_inteira(self):
        erros, _ = self.f.completude_da_divisao(self.sp, self.total, self.nomes, self.plano(),
                                                [["test_a", "test_b"], ["test_a.K", "test_a.K.test_x"]], self.pesos)
        self.assertEqual(erros, [])

    def test_completude_reprova_unidade_fora_de_toda_parte_ou_em_duas(self):  # remove um ID e exige vermelho
        for nome, partes in {"unidade fora": [["test_a", "test_b"], ["test_a.K"]],
                             "unidade em duas partes": [["test_a", "test_b"], ["test_a.K", "test_a.K.test_x", "test_b"]],
                             "nenhuma parte": []}.items():
            with self.subTest(nome):
                erros, _ = self.f.completude_da_divisao(self.sp, self.total, self.nomes, self.plano(), partes, self.pesos)
                self.assertIn("as partes não cobrem os IDs do discover uma vez cada", erros)

    def test_completude_reprova_id_sem_unidade_no_plano_e_unidade_sem_teste(self):
        plano = {k: v for k, v in self.plano().items() if k != "test_a.K"}
        erros, _ = self.f.completude_da_divisao(self.sp, self.total, self.nomes, plano, [["test_a", "test_b", "test_a.K.test_x"]],
                                                self.pesos)
        self.assertTrue(any("fora do plano: test_a.K" in e for e in erros), erros)
        com_sobra = dict(self.plano(), test_z=("test_z", None))
        erros, _ = self.f.completude_da_divisao(self.sp, self.total, self.nomes, com_sobra, [list(com_sobra)], self.pesos)
        self.assertTrue(any("do plano sem teste no discover: test_z" in e for e in erros), erros)

    def test_cinco_partes_dos_modulos_reais_cobrem_cada_unidade_uma_vez_e_equilibram(self):
        nomes = self.f.todos_os_modulos(self.sp)
        partes, plano, erros = self.f.dividir_por_unidade(self.sp, nomes, 5)
        self.assertEqual(erros, [])
        self.assertEqual(len(partes), 5)
        self.assertEqual(sorted(u for p in partes for u in p), sorted(plano))
        self.assertEqual(partes, self.f.dividir_por_unidade(self.sp, nomes, 5)[0], "a mesma árvore dá a mesma divisão")
        # o desequilíbrio previsto fica abaixo de 15% (a divisão por módulo dava 19% com pesos perfeitos)
        pesos = self.sp.ler_pesos()
        cargas = [sum(pesos.get(u, 1.0) for u in p) for p in partes]
        self.assertLess(max(cargas) / (sum(cargas) / 5), 1.15, cargas)
        # o módulo mais pesado deixa de ser um bloco só: suas unidades vão a mais de uma parte
        modulos_por_parte = [{plano[u][0] for u in p} for p in partes]
        self.assertGreater(sum("test_hooks" in m for m in modulos_por_parte), 1)

    def test_menos_unidades_que_partes_reprova(self):
        partes, plano, erros = self.f.dividir_por_unidade(self.sp, [], 5)
        self.assertEqual((partes, plano), ([], {}))
        self.assertEqual(erros, ["0 unidades não dão 5 partes não vazias"])


class Brinquedo5(unittest.TestCase):
    """A divisão por unidade rodando de verdade (repositório de brinquedo): as 5 partes juntas rodam todo teste uma vez e uma
    classe pesada vai a outra parte que o resto do módulo dela."""

    setUp, git, modulo, roda = Brinquedo.setUp, Brinquedo.git, Brinquedo.modulo, Brinquedo.roda

    def com_unidade_pesada(self):
        (self.dir / "tests" / "test_z.py").write_text(
            MODULO.format(nome="z", corpo="pass") + "\n\nclass U(unittest.TestCase):\n    def test_u(self):\n"
            "        (pathlib.Path(os.environ['MARCAS']) / 'u').write_text('x')\n")
        (self.dir / "tests" / "pesos-d4.json").write_text(json.dumps({"test_z": 1.0, "test_z.U": 50.0}))

    def test_as_cinco_partes_somam_a_suite_inteira_sem_repetir_e_separam_a_classe(self):
        self.com_unidade_pesada()
        vistos, onde = [], {}
        for k in (1, 2, 3, 4, 5):
            r, rodaram = self.roda("--parte", f"{k}/5", ci=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(rodaram, k)
            vistos += sorted(rodaram)
            onde.update({m: k for m in rodaram})
        self.assertEqual(sorted(vistos), ["a", "b", "c", "d", "e", "u", "z"])
        self.assertNotEqual(onde["u"], onde["z"])

    def test_mais_partes_que_unidades_reprova_toda_parte(self):
        for k in (1, 6):
            r, rodaram = self.roda("--parte", f"{k}/6", ci=True)
            self.assertEqual((r.returncode, rodaram), (1, set()), r.stdout + r.stderr)
            self.assertIn("não dão 6 partes", r.stderr)

    def test_parte_vermelha_anota_o_teste_que_caiu_e_a_verde_nao(self):  # a causa legível nas anotações do check run
        self.modulo("a", "self.fail('de propósito')")
        com_ci = {"GITHUB_ACTIONS": "true"}
        erros = {}
        with unittest.mock.patch.dict(AMBIENTE, com_ci):
            for k in (1, 2, 3, 4, 5):
                r, _ = self.roda("--parte", f"{k}/5", ci=True)
                erros[k] = (r.returncode, [l for l in r.stdout.splitlines() if l.startswith("::error")])
        vermelhas = [k for k, (rc, _) in erros.items() if rc == 1]
        self.assertEqual(len(vermelhas), 1, erros)
        (linha,) = erros[vermelhas[0]][1]
        self.assertTrue(linha.startswith(f"::error title=forge-suite parte {vermelhas[0]}/5::"), linha)
        self.assertRegex(linha, r"assercao test_a\.T\.test_a ")
        self.assertEqual([k for k, (rc, notas) in erros.items() if rc == 0 and notas], [])
        r, _ = self.roda("--parte", f"{vermelhas[0]}/5", ci=True)  # fora do Actions, só o log
        self.assertNotIn("::error", r.stdout)

    def test_parte_que_nao_divide_anota_o_erro_da_guarda(self):
        with unittest.mock.patch.dict(AMBIENTE, {"GITHUB_ACTIONS": "true"}):
            r, _ = self.roda("--parte", "1/6", ci=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        (linha,) = [l for l in r.stdout.splitlines() if l.startswith("::error")]
        self.assertIn("não dão 6 partes", linha)

    def test_erro_da_guarda_de_completude_reprova_a_parte_antes_de_rodar(self):  # a fiação da guarda por ID em por_parte
        codigo = ("import importlib.util, sys\n"
                  "spec = importlib.util.spec_from_file_location('sp', 'scripts/suite-partes.py')\n"
                  "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                  "m.completude_da_divisao = lambda *a, **k: (['id fora de toda parte (forçado)'], {})\n"
                  "sys.exit(m.main(['--parte', '1/5'], {'CI': '1'}))\n")
        env = dict(AMBIENTE, MARCAS=str(self.marcas), HOME=str(self.home))
        r = subprocess.run([sys.executable, "-c", codigo], cwd=self.dir, env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual((r.returncode, {p.name for p in self.marcas.iterdir()}), (1, set()), r.stdout + r.stderr)
        self.assertIn("id fora de toda parte (forçado)", r.stderr)
        self.assertEqual(r.stdout.strip().splitlines()[-1], "FAILED (divisão)")

    def test_modulo_que_tira_github_actions_no_import_nao_cala_as_anotacoes(self):
        """CI-ANOTACAO-CALADA (E137.2): o tests/test_catraca.py tira GITHUB_ACTIONS do os.environ no import, e o discover
        da divisão importa todos os módulos; a anotação de tempos (verde) e a de falha (vermelha) saem mesmo assim."""
        tira = "os.environ.pop('GITHUB_ACTIONS', None)\n"
        (self.dir / "tests" / "test_a.py").write_text(MODULO.format(nome="a", corpo="pass") + tira)
        self.modulo("b", "self.fail('de propósito')")
        saidas = {}
        with unittest.mock.patch.dict(AMBIENTE, {"GITHUB_ACTIONS": "true"}):
            for k in (1, 2, 3, 4, 5):
                r, _ = self.roda("--parte", f"{k}/5", ci=True)
                saidas[k] = (r.returncode, r.stdout)
        verdes = [s for rc, s in saidas.values() if rc == 0]
        vermelhas = [s for rc, s in saidas.values() if rc == 1]
        self.assertEqual((len(verdes), len(vermelhas)), (4, 1), saidas)
        self.assertTrue(all("::notice title=forge-tempos " in s for s in verdes), saidas)
        self.assertIn("::error title=forge-suite parte ", vermelhas[0])

    def test_anotacao_de_tempos_so_no_ci_e_so_com_a_parte_verde(self):
        com_ci = {"GITHUB_ACTIONS": "true"}
        with unittest.mock.patch.dict(AMBIENTE, com_ci):
            r, _ = self.roda("--parte", "1/5", ci=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        notas = [l for l in r.stdout.splitlines() if l.startswith("::notice title=forge-tempos 1/5 bloco 1/1::")]
        self.assertEqual(len(notas), 1, r.stdout)
        dado = json.loads(notas[0].split("::", 2)[2])
        self.assertEqual((dado["v"], dado["parte"], dado["bloco"]), (1, "1/5", [1, 1]))
        self.assertRegex(dado["python"], r"^3\.\d+$")
        self.assertTrue(dado["t"] and all(k.startswith("test_") and v >= 0 for k, v in dado["t"].items()), dado)
        self.assertEqual(r.stdout.strip().splitlines()[-1], "OK")
        r, _ = self.roda("--parte", "1/5", ci=True)  # sem GITHUB_ACTIONS: nenhuma anotação
        self.assertNotIn("::notice", r.stdout)
        self.modulo("a", "self.fail('de propósito')")
        vermelhas = []
        with unittest.mock.patch.dict(AMBIENTE, com_ci):
            for k in (1, 2, 3, 4, 5):
                r, _ = self.roda("--parte", f"{k}/5", ci=True)
                vermelhas.append((r.returncode, "::notice" in r.stdout))
        self.assertIn((1, False), vermelhas)
        self.assertEqual([v for v in vermelhas if v[0] == 1 and v[1]], [])  # perna vermelha nunca anota tempo


class AnotacaoDeTempos(unittest.TestCase):
    """S6: só nome de unidade no alfabeto seguro e segundos finitos saem em comando de workflow."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def test_uma_linha_notice_com_json_valido(self):
        (linha,) = self.f.anotacoes_de_tempos("2/5", "3.12", {"test_a": 1.234, "test_b.K": 0})
        self.assertTrue(linha.startswith("::notice title=forge-tempos 2/5 bloco 1/1::"))
        dado = json.loads(linha.split("::", 2)[2])
        self.assertEqual(dado, {"v": 1, "parte": "2/5", "python": "3.12", "bloco": [1, 1], "t": {"test_a": 1.2, "test_b.K": 0.0}})

    def test_nome_fora_do_alfabeto_valor_invalido_e_formato_ruim_ficam_de_fora(self):
        ruins = {"a::b": 1, "x\ny": 1, "com espaço": 1, "x%0A": 1, "": 1, "u" * 201: 1, "nan": float("nan"),
                 "inf": float("inf"), "neg": -1.0, "texto": "3", "bool": True, "ok": 2.0}
        (linha,) = self.f.anotacoes_de_tempos("1/5", "3.14", ruins)
        self.assertEqual(json.loads(linha.split("::", 2)[2])["t"], {"ok": 2.0})
        self.assertNotIn("\n", linha)
        for parte, python in (("0x/5", "3.12"), ("1/5", "x.12"), ("1/5/", "3.12"), ("1/5", "3.12;")):
            with self.subTest((parte, python)):
                self.assertEqual(self.f.anotacoes_de_tempos(parte, python, {"ok": 1}), [])
        self.assertEqual(self.f.anotacoes_de_tempos("1/5", "3.12", {}), [])
        self.assertEqual(self.f.anotacoes_de_tempos("1/5", "3.12", {"a::b": 1}), [])

    def test_muitas_unidades_viram_blocos_e_acima_do_limite_nenhuma(self):
        unidades = {f"test_modulo_{i:04d}.Classe.test_algo_{i:04d}": 1.0 for i in range(500)}
        linhas = self.f.anotacoes_de_tempos("1/5", "3.12", unidades)
        self.assertGreater(len(linhas), 1)
        juntos = {}
        for i, linha in enumerate(linhas, 1):
            dado = json.loads(linha.split("::", 2)[2])
            self.assertEqual(dado["bloco"], [i, len(linhas)])
            self.assertLessEqual(len(linha), self.f.LIMITE_DA_ANOTACAO + 400)
            juntos.update(dado["t"])
        self.assertEqual(juntos, unidades)
        enormes = {f"test_modulo_{i:06d}.Classe.test_algo_com_nome_longo_{i:06d}": 1.0 for i in range(6000)}
        self.assertEqual(self.f.anotacoes_de_tempos("1/5", "3.12", enormes), [])  # passaria de 8 anotações: não grava

    def test_escapar_dado(self):
        self.assertEqual(self.f.escapar_dado("a%b\r\nc"), "a%25b%0D%0Ac")


class AnotacaoDeFalha(unittest.TestCase):
    """A parte vermelha diz a causa nas anotações do check run (`::error`), sem depender do log: o tipo, o ID e o local de cada
    teste que caiu e os erros da guarda; só no Actions, uma linha só e nunca na parte verde."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    CAUSA = {"id": "test_a.T.test_x", "local": "tests/test_a.py:7", "tipo": "assercao", "obtido": "1", "esperado": "2"}

    def test_causa_vira_tipo_id_local_e_esperado_obtido(self):
        self.assertEqual(self.f.descricao_da_causa(self.CAUSA), "assercao test_a.T.test_x tests/test_a.py:7 (esperado 2, obtido 1)")
        self.assertEqual(self.f.descricao_da_causa({"id": "processo-1", "tipo": "sinal", "sinal": 9}), "sinal processo-1")
        self.assertEqual(self.f.descricao_da_causa({"tipo": "erro", "id": "t.T.x", "local": ""}), "erro t.T.x")

    def test_uma_linha_error_com_causas_e_erros_da_guarda(self):
        (linha,) = self.f.anotacao_de_falha("parte 1/5", [self.CAUSA], ["processo 2 saiu com 1"])
        self.assertTrue(linha.startswith("::error title=forge-suite parte 1/5::"), linha)
        self.assertIn("test_a.T.test_x", linha)
        self.assertIn("; processo 2 saiu com 1", linha)
        self.assertEqual(self.f.anotacao_de_falha("parte 1/5", None, ["so a guarda"])[0].split("::", 2)[2], "so a guarda")
        self.assertEqual(self.f.anotacao_de_falha("parte 1/5", [self.CAUSA], None)[0].count("::"), 2)

    def test_sem_causa_nem_erro_nao_anota(self):
        self.assertEqual(self.f.anotacao_de_falha("parte 1/5", [], []), [])
        self.assertEqual(self.f.anotacao_de_falha("parte 1/5", None, None), [])

    def test_titulo_fora_do_alfabeto_e_quebra_de_linha_nao_saem_no_comando(self):
        (linha,) = self.f.anotacao_de_falha("x::y\nz", [{"id": "a\nb::c%d", "tipo": "erro"}], [])
        self.assertNotIn("\n", linha)
        self.assertTrue(linha.startswith("::error title=forge-suite suite::"), linha)
        self.assertIn("a%0Ab::c%25d", linha)
        (linha,) = self.f.anotacao_de_falha(None, [self.CAUSA], [])
        self.assertTrue(linha.startswith("::error title=forge-suite suite::"), linha)

    def test_limites_de_causas_e_de_tamanho(self):
        causas = [{"id": f"test_m.T.test_{i:03d}", "tipo": "assercao"} for i in range(self.f.LIMITE_DE_CAUSAS + 10)]
        (linha,) = self.f.anotacao_de_falha("parte 1/5", causas, [])
        self.assertIn(f"test_{self.f.LIMITE_DE_CAUSAS - 1:03d}", linha)
        self.assertNotIn(f"test_{self.f.LIMITE_DE_CAUSAS:03d}", linha)
        (linha,) = self.f.anotacao_de_falha("parte 1/5", [], ["x" * (self.f.LIMITE_DA_ANOTACAO * 2)])
        self.assertLessEqual(len(linha.split("::", 2)[2]), self.f.LIMITE_DA_ANOTACAO)

    def test_emitir_so_no_actions(self):
        for ambiente, saiu in (({"GITHUB_ACTIONS": "true"}, True), ({}, False), ({"GITHUB_ACTIONS": "false"}, False),
                               ({"GITHUB_ACTIONS": "1"}, False)):
            with self.subTest(ambiente):
                with unittest.mock.patch.object(self.f.sys, "stdout", new_callable=io.StringIO) as saida:
                    self.f.emitir_falha(ambiente, "parte 1/5", [self.CAUSA], [])
                self.assertEqual(saida.getvalue().startswith("::error"), saiu)


class SomaDasCinco(unittest.TestCase):
    """S2 e A3: matriz reduzida (4 pernas) com `--somar-pulados 5` reprova no somatório, que é o que fecha a divergência de N."""

    setUp, git, modulo, roda = Brinquedo.setUp, Brinquedo.git, Brinquedo.modulo, Brinquedo.roda

    def escrever(self, pasta, partes, n=5):
        pasta.mkdir(parents=True, exist_ok=True)
        for k in partes:
            (pasta / f"parte-{k}.json").write_text(json.dumps({"parte": f"{k}/{n}", "pulados": 0, "pulados_ids": []}))

    def test_cinco_pernas_passam_quatro_ou_outro_n_reprovam(self):
        (self.dir / "tests" / "config.json").write_text(json.dumps({"teto_pulados": 1}))
        pasta = Path(self._t.name) / "p"
        self.escrever(pasta, (1, 2, 3, 4, 5))
        r, _ = self.roda("--somar-pulados", "5", str(pasta))
        self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (0, "OK"), r.stderr)
        for nome, partes, n_lido, n_pedido in (("matriz de 4", (1, 2, 3, 4), 5, "5"), ("N do arquivo diferente", (1, 2, 3, 4, 5), 4, "5"),
                                               ("N pedido diferente", (1, 2, 3, 4, 5), 5, "4")):
            with self.subTest(nome):
                outra = Path(self._t.name) / nome.replace(" ", "-")
                self.escrever(outra, partes, n_lido)
                r, _ = self.roda("--somar-pulados", n_pedido, str(outra))
                self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (1, "FAILED (pulados das partes)"), r.stderr)


class FiacaoDoCI(unittest.TestCase):
    """As partes por versão e os agregadores com o nome exato dos checks exigidos ("bateria", "bateria (python 3.14)")."""

    @classmethod
    def setUpClass(cls):
        cls.texto = CI.read_text(encoding="utf-8")
        cls.jobs = {}
        for bloco in re.split(r"(?m)^(?=  [a-z-]+:\n)", cls.texto.split("\njobs:\n", 1)[1]):
            achado = re.match(r"  ([a-z-]+):\n", bloco)
            if achado:
                cls.jobs[achado.group(1)] = bloco

    def job(self, nome):
        """O bloco do job; job ausente reprova por asserção (e não por KeyError), para o vermelho na base ter veredito."""
        self.assertIn(nome, self.jobs, f"o ci.yml não tem o job {nome}")
        return self.jobs[nome]

    def casar(self, padrao, bloco):
        """O trecho do bloco; sem ele a asserção reprova (e não o AttributeError de None.group)."""
        achado = re.search(padrao, bloco)
        self.assertIsNotNone(achado, f"sem {padrao!r} no bloco")
        return achado

    def nome(self, job):
        return self.casar(r"(?m)^    name: (.*)$", self.job(job)).group(1)

    def test_partes_por_versao_rodam_o_script_em_cinco(self):  # CI-RAPIDO: 5 partes por unidade (eram 3 por módulo)
        # F6 (v0481 E32.1): a suíte inteira roda uma vez, no 3.12; o 3.14 só tem instalação e fumaça no PR (diario.yml roda o resto)
        for job, versao in (("partes-doze", "3.12"), ("rapida-partes-doze", "3.12")):
            with self.subTest(job):
                bloco = self.job(job)
                self.assertIn("parte: [1, 2, 3, 4, 5]", bloco)
                self.assertIn(f'python-version: "{versao}"', bloco)
                self.assertIn('python3 scripts/suite-partes.py --parte "$PARTE/5"', bloco)
                self.assertIn("fail-fast: false", bloco)

    def test_agregadores_tem_o_nome_exigido_e_exigem_todas_as_partes(self):
        # E47.1: o agregador leva o sufixo da espera do parecer (vazio sem espera), que deixa o check exigido `bateria` pendente
        casos = {"agregador": ("bateria", {"bateria", "pareceres", "verificacoes", "partes-doze", "pulados-doze"}),
                 "bateria-python-tres-quatorze": ("bateria (python 3.14)", {"instalacao-quatorze"})}
        for job, (nome, necessarios) in casos.items():
            with self.subTest(job):
                bloco = self.job(job)
                self.assertEqual(ESPERA.sub("", self.nome(job)), nome)  # E47.6: o sufixo condicional da espera
                needs = self.casar(r"(?m)^    needs: \[(.*)\]$", bloco).group(1)
                self.assertEqual({n.strip() for n in needs.split(",")}, necessarios)
                # always(): necessário cancelado, pulado ou vermelho reprova o agregador (um pulado contaria como verde)
                self.assertRegex(bloco, r"(?m)^    if: always\(\) && ")
                for necessario in necessarios:
                    self.assertIn(f"${{{{ needs.{necessario}.result }}}}", bloco)
                self.assertEqual(bloco.count("= success ]"), len(necessarios))
                self.assertNotIn("uses:", bloco)  # o agregador não roda código da branch
        nomes = [self.nome(j) for j in self.jobs]
        self.assertEqual([ESPERA.sub("", n) for n in nomes].count("bateria"), 1)
        self.assertNotIn("bateria", nomes)
        self.assertTrue(self.nome("agregador").endswith("&& needs.pareceres.outputs.espera || '' }}"))
        self.assertEqual(nomes.count("bateria (python 3.14)"), 1)

    def test_cada_parte_publica_os_pulados_e_um_job_soma_contra_o_teto(self):  # T3
        for versao in ("doze",):
            with self.subTest(versao):
                parte = self.job(f"partes-{versao}")
                self.assertIn('FORGE_SUITE_PULADOS="$RUNNER_TEMP/pulados/parte-$PARTE.json"', parte)
                self.assertIn(f"name: pulados-{versao}-${{{{ matrix.parte }}}}", parte)
                self.assertIn("if-no-files-found: error", parte)
                soma = self.job(f"pulados-{versao}")
                self.assertRegex(soma, rf"(?m)^    needs: \[partes-{versao}, arvore\]$")
                self.assertNotIn(f"needs.partes-{versao}.outputs", soma)  # M2: a saída de job em matriz fica com a última perna
                self.assertIn(f"pattern: pulados-{versao}-*", soma)
                self.assertIn('python3 scripts/suite-partes.py --somar-pulados 5 "$RUNNER_TEMP/pulados"', soma)
                self.assertIn("persist-credentials: false", soma)

    def test_a_suite_inteira_so_roda_pelas_partes(self):  # SP4 e CI-RAPIDO: a develop também roda em partes
        for job, bloco in self.jobs.items():
            with self.subTest(job):
                self.assertNotIn("run: python3 scripts/suite-paralela.py", bloco)
                tem = "scripts/suite-partes.py --parte" in bloco
                self.assertEqual(tem, job in ("partes-doze", "rapida-partes-doze"))

    def test_rapidas_sao_a_prova_que_a_arvore_testada_le_com_o_preparo_das_partes(self):
        """SP4: o nome de cada agregador da develop é o JOBS_DE_PROVA de scripts/arvore-testada.py (test_arvore_testada
        confere o lado de lá); as pernas que ele exige rodam o mesmo preparo (env -a, histórico) das partes do PR."""
        nomes = {"3.12": "checagem rápida (push na develop)"}
        for job, perna, teto, versao in (("rapida", "rapida-partes-doze", "rapida-pulados-doze", "3.12"),):
            with self.subTest(job):
                self.assertEqual(self.nome(job), nomes[versao])
                bloco = self.job(perna)
                self.assertIn(f'python-version: "{versao}"', bloco)
                self.assertIn("fetch-depth: 0", bloco)
                self.assertIn("env -a x true", bloco)
                for j in (job, perna, teto):
                    self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/develop'"
                                  if j != job else "github.event_name == 'push' && github.ref == 'refs/heads/develop'",
                                  self.job(j))
                self.assertNotEqual(self.nome(perna), nomes[versao])  # o nome do agregador é só dele (len(com_nome) == 1)
                self.assertIn("parte ${{ matrix.parte }}/5", self.nome(perna))

    def test_agregador_da_develop_exige_as_cinco_pernas_e_o_teto_sem_rodar_codigo(self):  # CI-RAPIDO, S1 e A1
        for job, perna, teto in (("rapida", "rapida-partes-doze", "rapida-pulados-doze"),):
            with self.subTest(job):
                bloco = self.job(job)
                needs = self.casar(r"(?m)^    needs: \[(.*)\]$", bloco).group(1)
                self.assertEqual({n.strip() for n in needs.split(",")}, {"arvore-envio", perna, teto})
                self.assertRegex(bloco, r"(?m)^    if: always\(\) && github.event_name == 'push' && "
                                        r"github.ref == 'refs/heads/develop'$")
                # F6: sem a prova do PR, as duas pernas em success; com a prova (e o job dela em success), as duas puladas
                self.assertEqual(bloco.count("= success ]"), 3)
                self.assertIn('[ "$ARVORE" = success ] || exit 1', bloco)
                self.assertIn('[ "$PARTES" = skipped ] && [ "$PULADOS" = skipped ]', bloco)
                for necessario in ("arvore-envio", perna, teto):
                    self.assertIn(f"${{{{ needs.{necessario}.result }}}}", bloco)
                self.assertIn("${{ needs.arvore-envio.outputs.provada }}", bloco)
                self.assertNotIn("uses:", bloco)  # A1: o agregador só lê needs.*.result
                self.assertNotIn("scripts/", "\n".join(l for l in bloco.splitlines() if not l.lstrip().startswith("#")))
                self.assertIn("permissions:\n      contents: read", bloco)
                self.assertRegex(self.job(teto), rf"(?m)^    needs: \[arvore-envio, {perna}\]$")  # o teto só roda com as 5 pernas verdes
                self.assertIn('python3 scripts/suite-partes.py --somar-pulados 5 "$RUNNER_TEMP/pulados"', self.job(teto))
                self.assertIn("pattern: pulados-rapida-", self.job(teto))

    def test_f6_arvore_envio_so_le_a_prova_do_pr_e_as_pernas_da_develop_pulam_com_ela(self):
        """F6 (v0481 E32.9): o job da prova do PR roda só no push na develop, só com leitura, com o token num passo só e o script
        da develop (python -I); com `provada=true`, as 5 pernas e o teto de pulados ficam pulados (o job inteiro, sem gastar
        runner), e o agregador `rapida` (outro teste) aceita essa combinação; sem a prova, erro ou falha do job, elas rodam."""
        bloco = self.job("arvore-envio")
        self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/develop'\n", bloco)
        self.assertIn("permissions:\n      contents: read\n      actions: read", bloco)
        self.assertEqual(re.findall(r"(?m)^      (\w[\w-]*): (\w+)", bloco.split("    permissions:\n", 1)[1].split("    runs-on", 1)[0]),
                         [("contents", "read"), ("actions", "read"), ("pull-requests", "read")])
        self.assertEqual(bloco.count("GH_TOKEN: ${{ github.token }}"), 1)
        self.assertIn("persist-credentials: false", bloco)
        self.assertIn("python3 -I scripts/arvore-testada.py --do-pr", bloco)
        self.assertIn("provada: ${{ steps.prova.outputs.provada }}", bloco)
        self.assertIn("timeout-minutes: 5", bloco)
        for perna in ("rapida-partes-doze", "rapida-pulados-doze"):
            with self.subTest(perna):
                self.assertRegex(self.job(perna), r"(?m)^    needs: \[arvore-envio(, rapida-partes-doze)?\]$")
                self.assertIn("&& needs.arvore-envio.outputs.provada != 'true'\n", self.job(perna))
        self.assertNotIn("arvore-envio", self.job("partes-doze"))  # no PR a prova da develop é a do job `arvore`, outra
        efetivo = "\n".join(l for l in self.texto.replace(bloco, "").splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("--do-pr", efetivo)  # só o arvore-envio chama o modo do PR

    def test_pernas_da_develop_publicam_os_pulados_e_o_download_so_le_o_run_corrente(self):  # S5, A4
        for versao in ("doze",):
            with self.subTest(versao):
                perna, teto = self.job(f"rapida-partes-{versao}"), self.job(f"rapida-pulados-{versao}")
                self.assertIn('FORGE_SUITE_PULADOS="$RUNNER_TEMP/pulados/parte-$PARTE.json"', perna)
                self.assertIn(f"name: pulados-rapida-{versao}-${{{{ matrix.parte }}}}", perna)
                self.assertIn("if-no-files-found: error", perna)
                self.assertIn("retention-days: 1", perna)
                self.assertIn(f"pattern: pulados-rapida-{versao}-*", teto)
                efetivo = "\n".join(linha for linha in (perna + teto).splitlines() if not linha.lstrip().startswith("#"))
                for proibido in ("run-id", "github-token", "GH_TOKEN", "actions: read", "checks:"):
                    self.assertNotIn(proibido, efetivo)
                self.assertIn("persist-credentials: false", teto)

    def test_o_n_das_matrizes_e_o_mesmo_nos_tres_lugares(self):  # S2 e A3: 4 matrizes, --parte K/N e --somar-pulados N
        for versao in ("doze",):
            for matriz, soma in ((f"partes-{versao}", f"pulados-{versao}"),
                                 (f"rapida-partes-{versao}", f"rapida-pulados-{versao}")):
                with self.subTest(matriz):
                    lista = self.casar(r"(?m)^        parte: \[(.*)\]$", self.job(matriz)).group(1)
                    n = len(lista.split(","))
                    self.assertEqual([int(x) for x in lista.split(",")], list(range(1, n + 1)))
                    self.assertEqual(re.findall(r'--parte "\$PARTE/(\d+)"', self.job(matriz)), [str(n)])
                    self.assertEqual(re.findall(r"--somar-pulados (\d+) ", self.job(soma)), [str(n)])
                    self.assertIn(f"/{n})", self.nome(matriz))
                    self.assertEqual(n, 5)

    def test_f6_o_pr_roda_a_suite_uma_vez(self):
        """F6 (v0481 E32.1): sem job da suíte no 3.14 (nem no PR nem no envio); o e2e de instalação roda uma vez, no job da
        instalação do 3.14; os mutantes rodam no diario.yml, não no PR."""
        for job in self.jobs:
            self.assertNotIn("quatorze", job.replace("instalacao-quatorze", "").replace("bateria-python-tres-quatorze", ""))
        self.assertNotIn('python-version: "3.14"', "\n".join(b for j, b in self.jobs.items() if j != "instalacao-quatorze"))
        verificacoes = self.job("verificacoes")
        self.assertNotIn("e2e-instalacao", verificacoes)  # roda uma vez, no instalacao-quatorze
        self.assertIn("bash tests/e2e-instalacao.sh", self.job("instalacao-quatorze"))
        self.assertNotIn("forge-mutante", self.texto)  # os mutantes rodam no diario.yml, não no PR

    def test_f6_todo_workflow_tem_name_de_passo_entre_aspas_quando_tem_dois_pontos(self):
        """A1 do review e do devops (7cb7879): `name:` com `: ` num escalar simples invalida o YAML e o GitHub não cria o CI."""
        for arquivo in sorted((RAIZ / ".github" / "workflows").glob("*.yml")):
            for n, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
                valor = re.match(r"^\s*(?:- )?name:\s+(\S.*?)\s*$", linha)
                if valor and not valor.group(1).startswith(('"', "'")):
                    self.assertNotRegex(re.sub(r"\s#.*$", "", valor.group(1)), r": |:$", f"{arquivo.name}:{n}: {linha.strip()}")

    def test_f6_diario_roda_o_que_saiu_do_pr_na_develop_e_abre_o_cartao(self):
        """F6: o que saiu do PR (suíte no 3.14, e2e no 3.12, mutantes) roda uma vez por dia na develop, sem escrever no código;
        só o job `cartao` escreve, e só em issues."""
        diario = (RAIZ / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "17 5 * * *"', diario)
        self.assertNotIn("pull_request", diario)
        self.assertNotIn("continue-on-error", diario)
        self.assertIn("ref: develop", diario)
        self.assertEqual(diario.count("persist-credentials: false"), diario.count("actions/checkout@"))
        self.assertIn('python-version: "3.14"', diario)
        self.assertIn("bash tests/e2e-instalacao.sh", diario)
        self.assertIn("forge-mutante", diario)
        self.assertEqual(re.findall(r"(?m)^      (\w+): write", diario), ["issues"])
        cartao = diario[diario.index("\n  cartao:"):]
        self.assertIn("needs: [suite-quatorze, instalacao-doze, mutantes]", cartao)
        self.assertIn("if: always() && ", cartao)
        self.assertIn("gh issue create", cartao)
        self.assertNotIn("actions/checkout", cartao)

    def fatia_do_dia(self, pendentes, dia):
        """Roda, numa árvore descartável com 30 specs, o programa que o diario.yml usa para escolher a fatia do dia; devolve
        as linhas que ele imprime (a spec de índice dia%30 e, se houver pendentes dela, `--ids` com o resto)."""
        diario = (RAIZ / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
        inicio = diario.index("""<<'PY' > "$RUNNER_TEMP/fatia.txt"\n""") + len("""<<'PY' > "$RUNNER_TEMP/fatia.txt"\n""")
        programa = "\n".join(l[10:] for l in diario[inicio:diario.index("\n          PY\n")].splitlines())
        # o dia vai fixo ao programa (A16): ler date.today() aqui e no subprocesso discordaria na virada da meia-noite
        self.assertIn("datetime.date.today()", programa)
        programa = programa.replace("datetime.date.today()", f"datetime.date.fromordinal(datetime.date(2026, 1, 1).toordinal() + {dia - 1})")
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "tests" / "mutantes").mkdir(parents=True)
            (raiz / "tests" / "fixtures").mkdir()
            for n in range(30):
                (raiz / "tests" / "mutantes" / f"s{n:02d}.json").write_text(json.dumps(
                    {"pedido": "x", "mutantes": [{"id": "M1"}, {"id": "M2"}]}), encoding="utf-8")
            (raiz / "tests" / "fixtures" / "mutantes-pendentes.txt").write_text(pendentes, encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", "-c", programa], cwd=raiz, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.splitlines()

    def test_f6_diario_roda_uma_spec_por_chamada_sem_os_pendentes_conhecidos(self):
        """A3 e A4 do review (7cb7879): o forge-mutante recusa (rc 2) id repetido entre as specs de uma chamada, então a fatia vai
        uma spec por vez; os mutantes pendentes (a catraca de ConferirTodas) saem por --ids, e a issue avisa só quebra nova."""
        dia = 331  # 2026-11-27 (o dia do ano; 331 % 30 = 1)
        sobre = f"tests/mutantes/s{dia % 30:02d}.json"
        self.assertEqual(self.fatia_do_dia("", dia), [sobre])
        self.assertEqual(self.fatia_do_dia(f"# nota\n{sobre}: M1\ntests/mutantes/outra.json: M2\n", dia), [f"{sobre} --ids M2"])
        self.assertEqual(self.fatia_do_dia(f"{sobre}: M1\n{sobre}: M2\n", dia), [])
        diario = (RAIZ / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
        self.assertNotIn("por_pedido", diario)
        self.assertIn("python3 bin/forge-mutante $linha --processos 2", diario)

    @staticmethod
    def passo_do_diario(nome):
        """O `run` do passo `nome` do diario.yml (sem o recuo do YAML), como o GitHub o entrega ao bash."""
        diario = (RAIZ / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
        i = diario.index(f"      - name: {nome}")
        i = diario.index("        run: |\n", i) + len("        run: |\n")
        linhas = []
        for linha in diario[i:].splitlines():
            if linha.strip() and not linha.startswith("          "):
                break
            linhas.append(linha[10:])
        return "\n".join(linhas) + "\n"

    @staticmethod
    def jobs_do_diario():
        diario = (RAIZ / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
        blocos = re.split(r"(?m)^(?=  [a-z-]+:\n)", diario.split("\njobs:\n", 1)[1])
        return {re.match(r"  ([a-z-]+):\n", b).group(1): b for b in blocos if re.match(r"  ([a-z-]+):\n", b)}

    def rodar_passo(self, script, tmp, ambiente, caminho):
        """Roda o `run` de um passo no bash como o GitHub (`-e -o pipefail`), com PATH e RUNNER_TEMP controlados."""
        (tmp / "passo.sh").write_text(script, encoding="utf-8")
        (tmp / "rt").mkdir(exist_ok=True)
        env = {"PATH": f"{caminho}:/usr/bin:/bin", "HOME": str(tmp), "RUNNER_TEMP": str(tmp / "rt"),
               "GITHUB_STEP_SUMMARY": str(tmp / "resumo.md"), **ambiente}
        return subprocess.run(["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", str(tmp / "passo.sh")], cwd=tmp, env=env,
                              capture_output=True, text=True, timeout=60, check=False)

    def test_f6_diario_mutante_vivo_reprova_o_job_e_so_ele(self):
        """A1 do QA (cc91bc3): roda o passo dos mutantes com um `forge-mutante` falso; sem o `ruim=1` o job passaria com mutante
        vivo e a issue nunca abriria. Fatia com spec que passa: rc 0; spec que falha: rc 1."""
        for falha, rc in (("", 0), ("sim", 1)):
            with self.subTest(falha=falha), tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                (tmp / "bin").mkdir()
                (tmp / "bin" / "forge-mutante").write_text(
                    "import os, sys\nsys.exit(1 if os.environ.get('FALHA') else 0)\n", encoding="utf-8")
                (tmp / "tests" / "mutantes").mkdir(parents=True)
                for n in range(30):
                    (tmp / "tests" / "mutantes" / f"s{n:02d}.json").write_text(json.dumps(
                        {"pedido": "x", "mutantes": [{"id": "M1"}]}), encoding="utf-8")
                (tmp / "py").mkdir()
                (tmp / "py" / "python3").symlink_to(sys.executable)
                r = self.rodar_passo(self.passo_do_diario("Mutantes da fatia"), tmp, {"FALHA": falha}, str(tmp / "py"))
                self.assertEqual(r.returncode, rc, r.stdout + r.stderr)
                if falha:
                    self.assertIn("mutante vivo ou inválido em: tests/mutantes/s", r.stdout)

    def test_f6_diario_cada_job_le_a_develop_e_a_suite_tem_cinco_partes(self):
        """A1 do QA: `ref: develop` em cada checkout (sem ele o diário testaria a branch padrão), matriz de 5 partes casando com o
        `--parte "$PARTE/5"` e o rótulo `/5`, e cada job com `timeout-minutes`."""
        jobs = self.jobs_do_diario()
        self.assertEqual(sorted(jobs), ["cartao", "instalacao-doze", "mutantes", "suite-quatorze"])
        for nome in ("suite-quatorze", "instalacao-doze", "mutantes"):
            with self.subTest(nome):
                self.assertRegex(jobs[nome], r"actions/checkout@\S+ # \S+\n        with:\n          ref: develop\n")
                self.assertEqual(jobs[nome].count("ref: develop"), jobs[nome].count("actions/checkout@"))
        for nome, bloco in jobs.items():
            self.assertRegex(bloco, r"(?m)^    timeout-minutes: \d+$", nome)
        suite = jobs["suite-quatorze"]
        self.assertEqual(self.casar(r"(?m)^        parte: \[(.*)\]$", suite).group(1), "1, 2, 3, 4, 5")
        self.assertEqual(re.findall(r'--parte "\$PARTE/(\d+)"', suite), ["5"])
        self.assertIn("/5)", self.casar(r"(?m)^    name: (.*)$", suite).group(1))

    def test_f6_diario_cartao_comenta_na_issue_aberta_e_so_abre_se_nao_ha(self):
        """A2 do QA: roda o passo do cartão com um `gh` falso. Com issue aberta, comenta nela e não cria outra; sem, cria."""
        for aberta, esperado in (("42", ["issue list", "issue comment 42"]), ("", ["issue list", "issue create"])):
            with self.subTest(aberta=aberta), tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                (tmp / "fake").mkdir()
                gh = tmp / "fake" / "gh"
                gh.write_text('#!/bin/sh\necho "$1 $2 $3" >> "$LOG"\n[ "$2" = list ] && printf %s "$ABERTA"\nexit 0\n', encoding="utf-8")
                gh.chmod(0o755)
                amb = {"LOG": str(tmp / "log"), "ABERTA": aberta, "GH_TOKEN": "x", "REPO": "o/r", "RUN_URL": "u",
                       "SUITE": "failure", "INSTALACAO": "success", "MUTANTES": "success"}
                r = self.rodar_passo(self.passo_do_diario("Abre a issue"), tmp, amb, str(tmp / "fake"))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                chamadas = [l.strip() for l in (tmp / "log").read_text(encoding="utf-8").splitlines()]
                self.assertEqual([" ".join(c.split()[:3]) if c.startswith("issue comment") else " ".join(c.split()[:2])
                                  for c in chamadas], esperado)

    def test_f6_fumaca_do_python_3_14_roda_de_fato(self):
        """A2 do QA: o passo da fumaça do job `instalacao-quatorze` roda os dois testes, e nada de `run: true` no lugar."""
        bloco = self.job("instalacao-quatorze")
        i = bloco.index('      - name: "Fumaça no Python 3.14')
        passo = bloco[i:bloco.index("      - name:", i + 10)]
        self.assertIn("        run: python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.Referencias -v\n", passo)

    def test_partes_pulam_a_suite_so_com_a_arvore_provada(self):
        """SP4 e M2: um job prévio único tira a prova (F6: só a do Python 3.12); as 5 partes dependem dele e o
        preparo e a suíte só rodam sem a prova (falha fechada). A prova no passo de cada perna dava o `outputs` da última perna."""
        arvore = self.job("arvore")
        passo = arvore[arvore.index("        id: arvore\n"):]
        self.assertIn("          provada=false\n          if python3 scripts/arvore-testada.py --python 3.12; then provada=true; fi\n", passo)
        self.assertIn("      provada: ${{ steps.arvore.outputs.provada }}", arvore)
        self.assertIn("      actions: read", arvore)
        self.assertEqual(arvore.count("GH_TOKEN"), 1)
        for job in ("partes-doze",):
            with self.subTest(job):
                bloco = self.job(job)
                self.assertRegex(bloco, r"(?m)^    needs: \[arvore, bateria\]$")  # A18: os passos baratos antes da suíte
                self.assertNotIn("arvore-testada", bloco)
                self.assertNotIn("outputs:", bloco)
                for nome in ("      - name: env com -a", "      - name: Testes do Forge (parte)\n"):
                    i = bloco.index(nome)
                    self.assertEqual(bloco[i:].split("\n")[1], "        if: needs.arvore.outputs.provada != 'true'")
                self.assertNotIn("GH_TOKEN", bloco, "o token só no passo da árvore")
        release = (RAIZ / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        i = release.index("      - name: Testes antes de publicar\n")
        self.assertLess(release.index("        id: arvore\n"), i)
        self.assertEqual(release[i:].split("\n")[1], "        if: steps.arvore.outputs.provada != 'true'")


if __name__ == "__main__":
    unittest.main()
