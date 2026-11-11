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

    def test_pesos_por_modulo_somam_as_unidades(self):
        partes = carregar()
        pesos = {"test_a": 1.0, "test_a.T": 5.0, "test_a.T.test_x": 2.0, "test_ab": 3.0, "evals.test_c.K": 4.0}
        self.assertEqual(partes.pesos_por_modulo(pesos, ["test_a", "test_ab", "evals.test_c", "test_z"]),
                         {"test_a": 8.0, "test_ab": 3.0, "evals.test_c": 4.0})

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
        casos = {"agregador": ("bateria", {"bateria", "verificacoes", "partes-doze", "pulados-doze"}),
                 "bateria-python-tres-quatorze": ("bateria (python 3.14)",
                                                  {"partes-quatorze", "pulados-quatorze", "instalacao-quatorze"})}
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

    def test_cada_parte_publica_os_pulados_e_um_job_soma_contra_o_teto(self):  # T3
        for versao in ("doze", "quatorze"):
            with self.subTest(versao):
                parte = self.jobs[f"partes-{versao}"]
                self.assertIn('FORGE_SUITE_PULADOS="$RUNNER_TEMP/pulados/parte-$PARTE.json"', parte)
                self.assertIn(f"name: pulados-{versao}-${{{{ matrix.parte }}}}", parte)
                self.assertIn("if-no-files-found: error", parte)
                soma = self.jobs[f"pulados-{versao}"]
                self.assertRegex(soma, rf"(?m)^    needs: \[partes-{versao}, arvore\]$")
                self.assertNotIn(f"needs.partes-{versao}.outputs", soma)  # M2: a saída de job em matriz fica com a última perna
                self.assertIn(f"pattern: pulados-{versao}-*", soma)
                self.assertIn('python3 scripts/suite-partes.py --somar-pulados 3 "$RUNNER_TEMP/pulados"', soma)
                self.assertIn("persist-credentials: false", soma)

    def test_a_suite_inteira_so_roda_nas_partes_e_na_rapida(self):  # SP4: a rápida do 3.14 é a prova do 3.14
        for job, bloco in self.jobs.items():
            with self.subTest(job):
                tem = "run: python3 scripts/suite-paralela.py" in bloco
                self.assertEqual(tem, job in ("rapida", "rapida-quatorze"))

    def test_rapidas_sao_a_prova_que_a_arvore_testada_le_com_o_preparo_das_partes(self):
        """SP4: o nome de cada rápida é o JOBS_DE_PROVA de scripts/arvore-testada.py (test_arvore_testada confere o lado de lá);
        a prova roda o mesmo preparo (env -a, histórico) das partes."""
        nomes = {"3.12": "checagem rápida (push na develop)", "3.14": "checagem rápida (push na develop, python 3.14)"}
        for job, versao in (("rapida", "3.12"), ("rapida-quatorze", "3.14")):
            with self.subTest(job):
                bloco = self.jobs[job]
                self.assertEqual(self.nome(job), nomes[versao])
                self.assertIn(f'python-version: "{versao}"', bloco)
                self.assertIn("fetch-depth: 0", bloco)
                self.assertIn("env -a x true", bloco)
                self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/develop'", bloco)

    def test_partes_pulam_a_suite_so_com_a_arvore_provada(self):
        """SP4 e M2: um job prévio único tira a prova (só com a dos dois Pythons); as 3 partes de cada versão dependem dele e o
        preparo e a suíte só rodam sem a prova (falha fechada). A prova no passo de cada perna dava o `outputs` da última perna."""
        arvore = self.jobs["arvore"]
        passo = arvore[arvore.index("        id: arvore\n"):]
        self.assertIn("          provada=false\n          if python3 scripts/arvore-testada.py --python 3.12 && "
                      "python3 scripts/arvore-testada.py --python 3.14; then provada=true; fi\n", passo)
        self.assertIn("      provada: ${{ steps.arvore.outputs.provada }}", arvore)
        self.assertIn("      actions: read", arvore)
        self.assertEqual(arvore.count("GH_TOKEN"), 1)
        for job in ("partes-doze", "partes-quatorze"):
            with self.subTest(job):
                bloco = self.jobs[job]
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
