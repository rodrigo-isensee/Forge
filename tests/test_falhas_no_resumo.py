"""E2.270 (v047): scripts/falhas-no-resumo.py põe as falhas da suíte no resumo do GitHub e em anotações `::error`.

Classe do defeito: o CI vermelho sem o nome e o local dos testes que falharam no resumo, ou o leitor do registro virando
vetor (o registro é texto de teste, não confiável: comando de workflow e Markdown injetados) ou reprovando no lugar da suíte.
Variantes: falha, erro, subteste, erro em setUpClass, verde com contagem, tetos, registro ausente, injeção, e a fiação do
ci.yml (um passo em cada job que roda a suíte, sem mudar `permissions`).
"""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "falhas-no-resumo.py"
CI = RAIZ / ".github" / "workflows" / "ci.yml"
CODIGO = '''import unittest

class Classe(unittest.TestCase):
    def test_soma(self):
        self.assertEqual(1 + 1, 3, "soma errada")

    def test_erro(self):
        raise ValueError("estourou\\nsegunda linha")

    def test_sub(self):
        for caso in ("a", "b"):
            with self.subTest(caso=caso):
                self.assertTrue(caso == "a")

    def test_ok(self):
        pass

class Quebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raise RuntimeError("sem preparo")

    def test_nunca(self):
        pass
'''


def carregar():
    spec = importlib.util.spec_from_file_location("falhas_no_resumo", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def registro_real(pasta):
    """Roda um módulo de teste de verdade e devolve (registro, raiz): a saída do `unittest` com as falhas."""
    (pasta / "tests").mkdir()
    (pasta / "tests" / "test_brinquedo.py").write_text(CODIGO, encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_brinquedo"], cwd=pasta, capture_output=True, text=True)
    assert r.returncode != 0
    return r.stderr


class Leitor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = carregar()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.tmp.name).resolve()
        cls.registro = registro_real(cls.raiz)
        cls.achadas = cls.f.falhas(cls.registro, cls.raiz)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def por_teste(self, trecho):
        (a,) = [x for x in self.achadas if trecho in x["teste"]]
        return a

    def test_acha_falha_erro_subteste_e_setupclass(self):
        nomes = sorted(a["teste"] for a in self.achadas)
        self.assertEqual(len(nomes), 4, nomes)
        for esperado in ("tests.test_brinquedo.Classe.test_soma", "tests.test_brinquedo.Classe.test_erro",
                         "tests.test_brinquedo.Classe.test_sub (caso='b')", "tests.test_brinquedo.Quebra.setUpClass"):
            self.assertIn(esperado, nomes)

    def test_modulo_arquivo_e_linha_do_quadro_dos_testes(self):
        a = self.por_teste("test_soma")
        self.assertEqual((a["modulo"], a["arquivo"], a["linha"]), ("tests.test_brinquedo", "tests/test_brinquedo.py", 5))
        self.assertEqual(self.por_teste("test_erro")["linha"], 8)
        self.assertEqual(self.por_teste("Quebra")["modulo"], "tests.test_brinquedo")

    def test_primeira_linha_do_erro_e_a_da_excecao_nunca_o_diff(self):
        self.assertEqual(self.por_teste("test_soma")["erro"], "AssertionError: 2 != 3 : soma errada")
        self.assertEqual(self.por_teste("test_erro")["erro"], "ValueError: estourou")
        self.assertEqual(self.por_teste("Quebra")["erro"], "RuntimeError: sem preparo")

    def test_anotacao_por_falha_com_arquivo_e_linha(self):
        notas = self.f.anotacoes(self.achadas)
        self.assertEqual(len(notas), 4)
        self.assertIn("::error file=tests/test_brinquedo.py,line=5::tests.test_brinquedo.Classe.test_soma: "
                      "AssertionError: 2 != 3 : soma errada", notas)

    def test_resumo_tem_tabela_curta(self):
        linhas = self.f.resumo("suíte (python 3.12, parte 1/3)", self.registro, self.achadas)
        self.assertIn("| Teste | Módulo | Linha | Erro |", linhas)
        self.assertIn("| tests.test_brinquedo.Classe.test_soma | tests.test_brinquedo | tests/test_brinquedo.py:5 | "
                      "AssertionError: 2 != 3 : soma errada |", linhas)
        self.assertIn("4 teste(s) falharam", linhas[0])

    def test_formato_do_python_311_classe_sem_metodo(self):
        texto = ("\n" + "=" * 70 + "\nFAIL: test_a (tests.test_x.Classe)\n" + "-" * 70 + "\nTraceback (most recent call last):\n"
                 f'  File "{self.raiz}/tests/test_brinquedo.py", line 5, in test_a\n    x\nAssertionError: ruim\n')
        (a,) = self.f.falhas(texto, self.raiz)
        self.assertEqual((a["teste"], a["modulo"], a["arquivo"], a["linha"]), ("tests.test_x.Classe.test_a", "tests.test_x",
                                                                             "tests/test_brinquedo.py", 5))

    def test_verde_e_uma_linha_com_a_contagem_somada_dos_processos(self):
        registro = "x\n\nRan 120 tests\n\nOK\n\nRan 30 tests\n\nOK (skipped=2)\n"
        self.assertEqual(self.f.resumo("parte 1/3", registro, []), ["parte 1/3: 150 testes, sem falhas"])
        self.assertEqual(self.f.resumo("p", "Ran 7 tests in 0.1s\n\nOK\n", []), ["p: 7 testes, sem falhas"])

    def test_falha_sem_teste_identificado_mostra_o_veredito(self):
        linhas = self.f.resumo("p", "suite-paralela: causa tipo=x id=y\nFAILED (divisão)\n", [])
        self.assertIn("falhou sem teste identificado", linhas[0])
        self.assertEqual(len(linhas), 4)

    def test_tetos_da_tabela_e_das_anotacoes(self):
        muitas = [{"teste": f"m.C.t{i}", "modulo": "m", "arquivo": "tests/a.py", "linha": i, "erro": "E", "tipo": "FAIL"}
                  for i in range(40)]
        linhas = self.f.resumo("p", "", muitas)
        self.assertEqual(len([x for x in linhas if x.startswith("| m.C.")]), self.f.TETO_TABELA)
        self.assertIn(f"e mais {40 - self.f.TETO_TABELA} no registro do passo", linhas)
        self.assertEqual(len(self.f.anotacoes(muitas)), self.f.TETO_ANOTACOES)

    def test_texto_do_registro_nao_vira_comando_nem_tabela_nem_segredo(self):
        mau = {"teste": "m.C.t", "modulo": "m", "arquivo": "tests/a,b::c.py", "linha": 3, "tipo": "FAIL",
               "erro": "x\r\n::add-mask::y %0A | <b>`z` ghp_" + "a" * 30 + " token=abc"}
        (nota,) = self.f.anotacoes([mau])
        self.assertNotIn("\n", nota)
        self.assertNotIn("\r", nota)
        self.assertEqual(nota.count("::"), 2, nota)  # o do comando e o do fim das propriedades
        self.assertNotIn("a" * 30, nota)
        self.assertNotIn("token=abc", nota)
        self.assertIn("file=tests/a%2Cb%3A%3Ac.py,line=3", nota)
        linha = [x for x in self.f.resumo("p|q", "", [mau]) if x.startswith("| m.C.t")][0]
        self.assertEqual(len(re.findall(r"(?<!\\)\|", linha)), 5, linha)  # só as barras da tabela
        self.assertIn("&lt;b&gt;", linha)
        self.assertEqual(self.f.escapar_dado("a\nb\r%"), "a%0Ab%0D%25")
        self.assertNotIn("`", linha)

    def test_quadro_fora_do_repositorio_ou_com_ponto_ponto_fica_sem_arquivo(self):
        for caminho in ("/etc/passwd", f"{self.raiz}/../fora.py", "tests/nao_existe.py", "tests/../tests/test_brinquedo.py"):
            with self.subTest(caminho):
                self.assertIsNone(self.f.relativo(caminho, self.raiz))
        self.assertEqual(self.f.relativo("tests/test_brinquedo.py", self.raiz), "tests/test_brinquedo.py")

    def test_o_local_e_o_ultimo_quadro_dos_testes_mesmo_com_quadro_do_repositorio_depois(self):
        texto = ("\n" + "=" * 70 + "\nFAIL: test_a (tests.test_falhas_no_resumo.Leitor.test_a)\n" + "-" * 70 + "\nTraceback (most recent call last):\n"
                 f'  File "{RAIZ}/tests/test_falhas_no_resumo.py", line 7, in test_a\n    x\n'
                 f'  File "{RAIZ}/scripts/falhas-no-resumo.py", line 10, in falhas\n    y\nValueError: ruim\n')
        (a,) = self.f.falhas(texto, RAIZ)
        self.assertEqual((a["arquivo"], a["linha"]), ("tests/test_falhas_no_resumo.py", 7))

    def test_o_mesmo_bloco_duas_vezes_conta_uma_vez(self):
        self.assertEqual(len(self.f.falhas(self.registro + self.registro, self.raiz)), 4)


class Execucao(unittest.TestCase):
    def rodar(self, argumentos, registro=None, resumo=True):
        with tempfile.TemporaryDirectory() as t:
            pasta = Path(t)
            ambiente = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}
            destino = pasta / "resumo.md"
            if resumo:
                ambiente["GITHUB_STEP_SUMMARY"] = str(destino)
            argumentos = [str(pasta / a) if a == "registro.log" else a for a in argumentos]
            if registro is not None:
                (pasta / "registro.log").write_text(registro, encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(SCRIPT), *argumentos], cwd=RAIZ, env=ambiente,
                               capture_output=True, text=True)
            return r, destino.read_text(encoding="utf-8") if destino.exists() else ""

    def test_falha_escreve_no_resumo_anota_e_sai_com_zero(self):
        with tempfile.TemporaryDirectory() as t:
            registro = registro_real(Path(t))
        r, resumo = self.rodar(["parte", "registro.log"], registro)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("### parte: 4 teste(s) falharam", resumo)
        self.assertEqual(len(re.findall(r"(?m)^::error", r.stdout)), 4)

    def test_verde_so_a_linha_da_contagem(self):
        r, resumo = self.rodar(["parte", "registro.log"], "Ran 5 tests\n\nOK\n")
        self.assertEqual((r.returncode, r.stdout, resumo), (0, "", "parte: 5 testes, sem falhas\n"))

    def test_registro_ausente_ou_argumento_errado_nao_reprova(self):
        r, resumo = self.rodar(["parte", "registro.log"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("sem registro da suíte", resumo)
        r, _ = self.rodar([])
        self.assertEqual(r.returncode, 0)

    def test_sem_variavel_do_resumo_escreve_na_saida_padrao(self):
        r, _ = self.rodar(["parte", "registro.log"], "Ran 1 test\n\nOK\n", resumo=False)
        self.assertEqual((r.returncode, r.stdout), (0, "parte: 1 testes, sem falhas\n"))


class Fiacao(unittest.TestCase):
    """O ci.yml: cada job que roda a suíte guarda o registro e chama o leitor; as permissões ficam como estão."""

    @classmethod
    def setUpClass(cls):
        texto = CI.read_text(encoding="utf-8")
        cls.texto = texto
        cls.jobs = {m.group(1): m.group(0) for m in re.finditer(r"(?ms)^  ([a-z][\w-]*):\n.*?(?=^  [a-z][\w-]*:\n|\Z)", texto)}

    def test_jobs_que_rodam_a_suite_chamam_o_leitor_depois_do_teste(self):
        # PR: a suíte roda em 3 partes por versão (a develop roda a inteira em "rapida", sem registro por parte)
        casos = {j: "Testes do Forge (parte)" for j in ("partes-doze", "partes-quatorze")}
        for job, passo in casos.items():
            with self.subTest(job):
                bloco = self.jobs[job]
                i = bloco.index(f"      - name: {passo}")
                resto = bloco[i:]
                self.assertIn("set -o pipefail", resto.split("      - name: ")[1])
                self.assertIn('tee "$RUNNER_TEMP/suite.log"', resto.split("      - name: ")[1])
                seguinte = resto.split("      - name: ")[2]
                self.assertTrue(seguinte.startswith("Falhas no resumo"), seguinte[:60])
                self.assertIn('python3 -I scripts/falhas-no-resumo.py "$ROTULO" "$RUNNER_TEMP/suite.log"', seguinte)
                self.assertRegex(seguinte, r"(?m)^        if: \$\{\{ !cancelled\(\)")

    def test_leitor_nao_muda_permissoes_nem_afrouxa_o_ci(self):
        self.assertEqual(self.texto.count("scripts/falhas-no-resumo.py"), 2)
        for passo in re.findall(r"(?ms)^      - name: Falhas no resumo.*?(?=^      - |^  [a-z]|\Z)", self.texto):
            self.assertNotIn("GH_TOKEN", passo)
            self.assertNotIn("secrets.", passo)
            self.assertNotIn("permissions", passo)
        self.assertNotIn("continue-on-error", self.texto)
        self.assertNotIn("write", re.sub(r"(?m)^\s*#.*$", "", self.texto).replace("writes", ""))  # nenhuma permissão de escrita

    def test_partes_sem_ou_com_pipefail_mantem_o_codigo_de_saida_da_suite(self):
        with tempfile.TemporaryDirectory() as t:
            r = subprocess.run(["bash", "-e", "-c", 'set -o pipefail; false 2>&1 | tee "$1/x.log"; echo nao', "_", t],
                               capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (1, ""))


if __name__ == "__main__":
    unittest.main()
