"""Piso de cobertura informativo (0.45.1): o coletor por linha de scripts/cobertura.py (versao-048 E3a-1a), a soma dos
acertos sobre o Python de bin/, hooks/ e scripts/ e o job do CI que só publica o número."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "cobertura.py"


def carregar():
    spec = importlib.util.spec_from_file_location("cobertura", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# E3a-1a: o coletor gerado roda por `exec` num `python -I`. argv: coletor (ou vazio), código antes, depois, raiz.
RODAR = """import sys
ns = {}
exec(sys.argv[2], ns)
if sys.argv[1]:
    exec(compile(open(sys.argv[1]).read(), "sitecustomize.py", "exec"), ns)
exec(sys.argv[3], ns)
sys.path.insert(0, sys.argv[4])
import alvo
print(alvo.f(10000))
"""
ALVO = "def f(n):\n    t = 0\n    for i in range(n):\n        t += i\n    return t\n\n\ndef nunca():\n    return 1\n"
CALLBACK_LEVANTA = "class R(dict):\n    def setdefault(self, *a):\n        raise RuntimeError('x')\n_acertos = R()"


@unittest.skipUnless(hasattr(sys, "monitoring"), "o coletor usa sys.monitoring (Python 3.12+)")
class ColetorDeCobertura(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.raiz, self.saida = self.tmp / "raiz", self.tmp / "sa'ida"  # C-3: aspa no caminho compila
        self.raiz.mkdir()
        self.saida.mkdir(mode=0o700)
        (self.raiz / "alvo.py").write_text(ALVO)
        (self.tmp / "rodar.py").write_text(RODAR)  # fora da raiz: não pode aparecer nos acertos
        self.cobertura = carregar()
        (self.tmp / "coletor.py").write_text(self.cobertura.texto_do_coletor(self.saida, self.raiz))

    def rodar(self, coletor=True, antes="", depois=""):
        r = subprocess.run([sys.executable, "-I", str(self.tmp / "rodar.py"), str(self.tmp / "coletor.py") if coletor else "",
                            antes, depois, str(self.raiz)], capture_output=True, text=True, timeout=60,
                           env={"PATH": "/usr/bin:/bin"})
        return r.returncode, r.stdout, r.stderr

    def acertos(self):
        return [json.loads(a.read_text()) for a in sorted(self.saida.iterdir())]

    def test_anota_cada_linha_da_raiz_uma_vez_em_arquivo_600(self):
        self.assertEqual(self.rodar(), self.rodar(coletor=False))
        (dados,) = self.acertos()
        self.assertEqual(dados["acertos"], {"alvo.py": [1, 2, 3, 4, 5, 8]})  # nunca() fica de fora; rodar.py também
        self.assertLess(dados["chamadas"], 10000)  # DISABLE: o laço de 10000 voltas conta uma vez por linha
        self.assertEqual((dados["ligado"], dados["falhas"]), (True, 0))
        self.assertEqual([a.stat().st_mode & 0o777 for a in self.saida.iterdir()], [0o600])

    def test_falha_no_coletor_nao_muda_o_processo_e_e_contada(self):
        quebra = "import sys\nsys.monitoring.set_events = None"  # a instalação do callback levanta
        for antes, depois in (("", CALLBACK_LEVANTA), (quebra, ""), ("", "_SAIDA = '/nao/existe'")):
            self.assertEqual(self.rodar(antes=antes, depois=depois), self.rodar(coletor=False), (antes, depois))
        self.assertEqual([a["falhas"] > 0 for a in self.acertos()], [True, True])  # sem a pasta, nada se grava

    def test_id_ocupado_nao_liga_e_nao_escreve_na_tela(self):
        ocupa = "import sys\nsys.monitoring.use_tool_id(sys.monitoring.COVERAGE_ID, 'outro')"
        self.assertEqual(self.rodar(antes=ocupa), self.rodar(coletor=False))
        (dados,) = self.acertos()
        self.assertEqual((dados["ligado"], dados["motivo"], dados["acertos"]), (False, "id de ferramenta ocupado", {}))

    def test_fork_grava_um_arquivo_por_processo(self):
        forca = "import os\nif os.fork():\n    os.wait()"
        self.assertEqual(self.rodar(depois=forca), (0, "49995000\n" * 2, ""))
        self.assertEqual(len(self.acertos()), 2)

    def test_caminho_com_quebra_de_linha_ou_nulo_e_recusado(self):
        for ruim in ("\n", "\r", "\0"):
            for saida, raiz in ((f"/tmp/a{ruim}b", self.raiz), (self.saida, f"/tmp/a{ruim}b")):
                with self.subTest(ruim=ruim, saida=saida), self.assertRaises(ValueError):
                    self.cobertura.texto_do_coletor(saida, raiz)


# Um arquivo com docstring de módulo, classe e função, laço, try, with e while: só o `except` não roda.
ALVO_COMPLETO = '''"""doc"""
import os


class C:
    """doc"""
    x = 1

    def m(self):
        """doc"""
        return self.x


def f(n):
    t = 0
    for i in range(n):
        if i % 2:
            t += i
        else:
            t -= 1
    try:
        t += 1
    except ValueError:
        t = 0
    with open(os.devnull) as a:
        a.read()
    while t > 10:
        t //= 2
    return t + C().m()


print(f(50))
'''


@unittest.skipUnless(hasattr(sys, "monitoring"), "o coletor usa sys.monitoring (Python 3.12+)")
class PisoInformativo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.raiz, self.site, self.saida = self.tmp / "raiz", self.tmp / "site", self.tmp / "saida"
        for pasta in ("bin", "hooks", "scripts", "tests", "bin/sub"):
            (self.raiz / pasta).mkdir(parents=True)
        self.site.mkdir()
        (self.raiz / "bin" / "alvo.py").write_text(ALVO_COMPLETO)
        (self.raiz / "bin" / "ferramenta").write_text("#!/usr/bin/env python3\nprint(1)\n")
        (self.raiz / "scripts" / "rodar.sh").write_text("#!/usr/bin/env bash\necho 1\n")
        (self.raiz / "scripts" / "rodar").write_text("#!/usr/bin/env bash\necho 1\n")  # sem extensão, shell
        (self.raiz / "scripts" / "notas.txt").write_text("#!/usr/bin/python3\n")  # extensão que não é .py
        (self.raiz / "bin" / "atalho.py").symlink_to(self.raiz / "bin" / "alvo.py")
        (self.raiz / "tests" / "test_x.py").write_text("x = 1\n")
        (self.raiz / "bin" / "sub" / "fundo.py").write_text("x = 1\n")
        (self.raiz / "hooks" / "nunca.py").write_text("x = 1\ny = 2\n")
        self.cobertura = carregar()

    def cli(self, *args, env=None):
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, timeout=60,
                           env=env if env is not None else {"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
        return r.returncode, r.stdout, r.stderr

    def test_mede_so_o_python_do_primeiro_nivel_de_bin_hooks_e_scripts(self):
        self.assertEqual(self.cobertura.arquivos_medidos(self.raiz), ["bin/alvo.py", "bin/ferramenta", "hooks/nunca.py"])

    def test_linha_executavel_e_o_comando_menos_a_docstring(self):
        self.assertEqual(sorted(self.sem_erro(self.cobertura.linhas_executaveis, ALVO_COMPLETO)),
                         [2, 5, 7, 9, 11, 14, 15, 16, 17, 18, 20, 21, 22, 24, 25, 26, 27, 28, 29, 32])

    def test_o_processo_filho_com_python_i_conta_pelo_sitecustomize(self):
        self.cobertura.instalar(self.site, self.saida, self.raiz)
        # o sitecustomize do `site` vale com -I; aqui o PYTHONPATH faz o papel do site-packages do job
        r = subprocess.run([sys.executable, str(self.raiz / "bin" / "alvo.py")], capture_output=True, text=True, timeout=60,
                           env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(self.site)})
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "10\n", ""))
        rel = self.cobertura.relatorio(self.saida, self.raiz)
        self.assertEqual(rel["por_arquivo"], {"bin/alvo.py": (19, 20), "bin/ferramenta": (0, 1), "hooks/nunca.py": (0, 2)})
        self.assertEqual((rel["cobertas"], rel["executaveis"], rel["processos"], rel["ligados"]), (19, 23, 1, 1))

    def test_relatorio_publica_o_numero_no_resumo_e_nao_reprova(self):
        self.saida.mkdir()
        (self.saida / "1-a.json").write_text(json.dumps({"ligado": True, "acertos": {"bin/alvo.py": [2, 5, 999]}}))
        (self.saida / "2-b.json").write_text("{quebrado")
        (self.saida / "3-c.json").write_text(json.dumps({"ligado": False, "acertos": {}}))
        rel = self.cobertura.relatorio(self.saida, self.raiz)
        self.assertEqual((rel["cobertas"], rel["executaveis"], rel["processos"], rel["ligados"]), (2, 23, 2, 1))
        resumo = self.tmp / "resumo.md"
        env = {"PATH": "/usr/bin:/bin", "GITHUB_STEP_SUMMARY": str(resumo)}
        r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import cobertura as c;"
                            "c.RAIZ = c.Path(sys.argv[2]); sys.exit(c.main(['relatorio', sys.argv[3]]))",
                            str(SCRIPT.parent), str(self.raiz), str(self.saida)], capture_output=True, text=True, timeout=60,
                           env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("cobertura informativa: 8.7% (2 de 23 linhas em 3 arquivos; 2 processos, 1 com o coletor ligado)", r.stdout)
        self.assertTrue(resumo.is_file(), "o número não foi ao resumo do job")
        texto = resumo.read_text(encoding="utf-8")
        self.assertIn("não reprova", texto)
        self.assertLess(texto.index("`bin/ferramenta`"), texto.index("`bin/alvo.py`"))  # do menos coberto ao mais

    def test_sem_acertos_o_numero_e_zero_e_sai_zero(self):
        self.saida.mkdir()
        codigo, saida, _ = self.cli("relatorio", self.saida)
        self.assertEqual(codigo, 0)
        self.assertRegex(saida, r"cobertura informativa: \d+\.\d% \(0 de \d+ linhas")

    def test_instalar_nao_sobrescreve_o_sitecustomize_de_outro_dono_nem_atalho(self):
        alheio = self.site / "sitecustomize.py"
        alheio.write_text("import algo\n")
        with self.assertRaises(ValueError):
            self.cobertura.instalar(self.site, self.saida, self.raiz)
        self.assertFalse(self.cobertura.remover(self.site))
        self.assertEqual(alheio.read_text(), "import algo\n")
        alheio.unlink()
        alheio.symlink_to(self.tmp / "fora.py")
        with self.assertRaises(ValueError):
            self.cobertura.instalar(self.site, self.saida, self.raiz)
        self.assertFalse((self.tmp / "fora.py").exists())

    def test_instalar_e_remover_o_proprio(self):
        destino = self.cobertura.instalar(self.site, self.saida, self.raiz)
        self.assertTrue(destino.read_text().startswith("# forge-cobertura\n"))
        self.assertEqual(self.saida.stat().st_mode & 0o777, 0o700)
        self.cobertura.instalar(self.site, self.saida, self.raiz)  # o próprio pode ser regravado
        self.assertTrue(self.cobertura.remover(self.site))
        self.assertFalse(destino.exists())

    def sem_erro(self, funcao, *args):
        """O piso só publica: entrada fora da forma nunca levanta (a exceção vira falha do teste, não erro)."""
        try:
            return funcao(*args)
        except Exception as erro:  # noqa: BLE001
            self.fail(f"{funcao.__name__} levantou {type(erro).__name__}: {erro}")

    def test_arquivo_de_acertos_fora_da_forma_nao_conta_nem_levanta(self):
        self.saida.mkdir()
        formas = ([1], {"acertos": [1]}, {"acertos": {"bin/alvo.py": 5}}, {"acertos": {"bin/alvo.py": [[2], "5", 7]}})
        for n, dados in enumerate(formas):
            (self.saida / f"{n}-x.json").write_text(json.dumps(dados))
        acertos, processos, ligados = self.sem_erro(self.cobertura.somar_acertos, self.saida)
        self.assertEqual((acertos, processos, ligados), ({"bin/alvo.py": {7}}, 2, 0))

    def test_tabela_e_numero_sem_linhas_executaveis(self):
        r = {"por_arquivo": {"a.py": (0, 0), "b.py": (1, 2)}, "cobertas": 0, "executaveis": 0, "processos": 0, "ligados": 0}
        linha, tabela = self.sem_erro(self.cobertura.texto_do_relatorio, r)
        self.assertIn("cobertura informativa: sem linhas (0 de 0", linha)
        self.assertLess(tabela.index("`b.py`"), tabela.index("`a.py`"))  # 50% antes do arquivo sem linhas
        self.assertIn("| `a.py` | sem linhas | 0/0 |", tabela)

    def test_raiz_padrao_e_a_do_forge(self):
        self.saida.mkdir()
        self.assertIn("hooks/conformidade.py", self.cobertura.relatorio(self.saida)["por_arquivo"])

    def test_linha_de_comando_instala_e_remove(self):
        destino = self.site / "sitecustomize.py"
        codigo, saida, _ = self.cli("instalar", self.site, self.saida)
        self.assertEqual((codigo, saida.strip()), (0, f"coletor em {destino}"))
        self.assertTrue(destino.read_text().startswith("# forge-cobertura\n"))
        self.assertEqual(self.cli("remover", self.site)[:2], (0, "coletor removido\n"))
        self.assertFalse(destino.exists())
        self.assertEqual(self.cli("remover", self.site)[:2], (0, "nada a remover\n"))

    def test_uso_errado_sai_dois(self):
        self.assertEqual(self.cli()[0], 2)
        self.assertEqual(self.cli("instalar", self.site)[0], 2)


class JobDoCI(unittest.TestCase):
    def test_job_de_cobertura_so_publica_e_nao_entra_no_check(self):
        texto = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        blocos = dict(re.findall(r"(?ms)^  ([a-z-]+):\n(.*?)(?=^  [a-z-]+:\n|\Z)", texto.partition("\njobs:\n")[2]))
        job = blocos["cobertura"]
        inicios = ("python3 scripts/cobertura.py", "python3 scripts/suite-paralela.py", "run: python3")
        comandos = [linha.strip() for linha in job.splitlines() if linha.strip().startswith(inicios)]
        self.assertEqual(len(comandos), 4, comandos)
        for comando in comandos:  # nenhum passo reprova
            self.assertRegex(comando, r'\|\| echo "[^"]+"$', comando)
        self.assertIn("    if: github.event_name == 'push' && github.ref == 'refs/heads/main'\n", job)
        for passo in ("cobertura.py instalar", "suite-paralela.py ||", "cobertura.py remover", "cobertura.py relatorio"):
            self.assertIn(passo, job)
        for nome, bloco in blocos.items():
            with self.subTest(job=nome):
                self.assertNotRegex(bloco, r"needs:.*\bcobertura\b")


if __name__ == "__main__":
    unittest.main()
