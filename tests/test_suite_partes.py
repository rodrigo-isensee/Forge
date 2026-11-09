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
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "suite-partes.py"
CI = RAIZ / ".github" / "workflows" / "ci.yml"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items()
                           if not k.startswith(("GIT_", "FORGE_SUITE_", "GITHUB_")) and k != "CI"})
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

    def test_esperado_e_fora_da_divisao_pelo_modulo_do_id(self):
        total = collections.Counter({"test_a.T.test_x": 1, "test_b.T.test_y": 2, "unittest.loader._FailedTest.test_c": 1})
        self.assertEqual(self.f.esperado_da_parte(total, ["test_b"]), collections.Counter({"test_b.T.test_y": 2}))
        self.assertEqual(self.f.fora_da_divisao(total, ["test_a", "test_b"]), ["unittest.loader._FailedTest.test_c"])
        pacote = collections.Counter({"evals.test_p.T.x": 1, "test_a.T.y": 1})
        self.assertEqual(self.f.esperado_da_parte(pacote, ["evals.test_p"]), collections.Counter({"evals.test_p.T.x": 1}))
        self.assertEqual(self.f.modulo_do_id("evals.test_p.T.x", {"evals.test_p", "test_p"}), "evals.test_p")

    def test_tres_partes_dos_modulos_reais_cobrem_tudo_uma_vez(self):
        nomes = self.sp.modulos()
        partes, erros = self.f.dividir(self.sp, nomes, 3)
        self.assertEqual(erros, [])
        self.assertEqual(len(partes), 3)
        self.assertEqual(sorted(m for p in partes for m in p), sorted(nomes))
        self.assertEqual(partes, self.f.dividir(self.sp, nomes, 3)[0], "a mesma árvore dá a mesma divisão")

    def test_menos_modulos_que_partes_reprova(self):
        self.assertTrue(self.f.dividir(self.sp, ["test_a"], 3)[1])


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

    def nome(self, job):
        return re.search(r"(?m)^    name: (.*)$", self.jobs[job]).group(1)

    def test_partes_por_versao_rodam_o_script_em_tres(self):
        for job, versao in (("partes-doze", "3.12"), ("partes-quatorze", "3.14")):
            with self.subTest(job):
                bloco = self.jobs[job]
                self.assertIn("parte: [1, 2, 3]", bloco)
                self.assertIn(f'python-version: "{versao}"', bloco)
                self.assertIn('python3 scripts/suite-partes.py --parte "$PARTE/3"', bloco)
                self.assertIn("fail-fast: false", bloco)

    def test_agregadores_tem_o_nome_exigido_e_exigem_todas_as_partes(self):
        casos = {"agregador": ("bateria", {"bateria", "partes-doze"}),
                 "bateria-python-tres-quatorze": ("bateria (python 3.14)", {"partes-quatorze", "instalacao-quatorze"})}
        for job, (nome, necessarios) in casos.items():
            with self.subTest(job):
                bloco = self.jobs[job]
                self.assertEqual(self.nome(job), nome)
                needs = re.search(r"(?m)^    needs: \[(.*)\]$", bloco).group(1)
                self.assertEqual({n.strip() for n in needs.split(",")}, necessarios)
                # always(): necessário cancelado, pulado ou vermelho reprova o agregador (um pulado contaria como verde)
                self.assertRegex(bloco, r"(?m)^    if: always\(\) && ")
                for necessario in necessarios:
                    self.assertIn(f"${{{{ needs.{necessario}.result }}}}", bloco)
                self.assertEqual(bloco.count("= success ]"), len(necessarios))
                self.assertNotIn("uses:", bloco)  # o agregador não roda código da branch
        nomes = [self.nome(j) for j in self.jobs]
        self.assertEqual(nomes.count("bateria"), 1)
        self.assertEqual(nomes.count("bateria (python 3.14)"), 1)

    def test_a_suite_inteira_so_roda_nas_partes_e_na_rapida(self):  # SP4: a rápida do 3.14 é a prova do 3.14
        for job, bloco in self.jobs.items():
            with self.subTest(job):
                tem = "run: python3 scripts/suite-paralela.py" in bloco
                self.assertEqual(tem, job in ("rapida", "rapida-quatorze"))

    def test_rapidas_sao_a_prova_que_a_arvore_testada_le_com_o_preparo_das_partes(self):
        """SP4: o nome de cada rápida é o JOBS_DE_PROVA do script; a prova roda o mesmo preparo (env -a, histórico) das partes."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("arvore_testada", RAIZ / "scripts" / "arvore-testada.py")
        at = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(at)
        for job, versao in (("rapida", "3.12"), ("rapida-quatorze", "3.14")):
            with self.subTest(job):
                bloco = self.jobs[job]
                self.assertEqual(self.nome(job), at.JOBS_DE_PROVA[versao])
                self.assertIn(f'python-version: "{versao}"', bloco)
                self.assertIn("fetch-depth: 0", bloco)
                self.assertIn("env -a x true", bloco)
                self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/develop'", bloco)

    def test_partes_pulam_a_suite_so_com_a_arvore_provada(self):
        """SP4: o passo da árvore vem antes do preparo e da suíte, e os dois só rodam sem a prova (falha fechada)."""
        for job in ("partes-doze", "partes-quatorze"):
            with self.subTest(job):
                bloco = self.jobs[job]
                arvore = bloco.index("        id: arvore\n")
                self.assertIn("if python3 scripts/arvore-testada.py; then provada=true; else provada=false; fi", bloco)
                self.assertIn("      actions: read", bloco)
                for passo in ("      - name: env com -a", "      - name: Testes do Forge (parte)\n"):
                    i = bloco.index(passo)
                    self.assertLess(arvore, i)
                    self.assertEqual(bloco[i:].split("\n")[1], "        if: steps.arvore.outputs.provada != 'true'")
                self.assertEqual(bloco.count("GH_TOKEN"), 1, "o token só no passo da árvore")
        release = (RAIZ / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        i = release.index("      - name: Testes antes de publicar\n")
        self.assertLess(release.index("        id: arvore\n"), i)
        self.assertEqual(release[i:].split("\n")[1], "        if: steps.arvore.outputs.provada != 'true'")


if __name__ == "__main__":
    unittest.main()
