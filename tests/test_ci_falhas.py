"""v0475 (condição do #641): as guardas de scripts/falhas-no-resumo.py e de `pr_da_branch` que ficaram sem prova.

Obrigação: cada condição do leitor do registro da suíte (R-QA, mutante por condição) cai por um teste que a nomeia.
Variantes: texto de controle, limite do corte, nome de módulo sem classe, bloco sem separador antes, bloco no fim do
registro, linha com tab, traceback sem quadro, quadro fora do repositório, sem quadro, tetos exatos, arquivo ausente,
`main` com ambiente e raiz injetados, argumentos a mais e corpo nulo do PR.
"""
import importlib.machinery
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
SEP = "=" * 70
TRA = "-" * 70


def carregar(nome, rel, arquivo_py=True):
    caminho = str(RAIZ / rel)
    if arquivo_py:
        spec = importlib.util.spec_from_file_location(nome, caminho)
    else:
        spec = importlib.util.spec_from_loader(nome, importlib.machinery.SourceFileLoader(nome, caminho))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


f = carregar("falhas_ci", "scripts/falhas-no-resumo.py")
fc = carregar("forge_check_ci", "bin/forge-check", arquivo_py=False)


def achada(arquivo="tests/a.py", **extra):
    return {"teste": "m.C.t", "modulo": "m", "arquivo": arquivo, "linha": 3, "erro": "E", "tipo": "FAIL", **extra}


def bloco(*quadros, erro="ValueError: x", nome="FAIL: test_a (m.C.test_a)"):
    linhas = ["", SEP, nome, TRA, "Traceback (most recent call last):"]
    for caminho, linha in quadros:
        linhas += [f'  File "{caminho}", line {linha}, in t', "    x"]
    return "\n".join(linhas + ([erro] if erro else []) + [""]) + "\n"


class Texto(unittest.TestCase):
    def test_caractere_de_controle_vira_espaco(self):
        self.assertEqual(f.limpar("a\x1b[31mb"), "a [31mb")

    def test_corte_so_acima_do_teto(self):
        self.assertEqual(f.limpar("x" * 160), "x" * 160)
        cortado = f.limpar("x" * 161)
        self.assertEqual((len(cortado), cortado[-1]), (160, "…"))

    def test_modulo_do_id(self):
        self.assertEqual(f.modulo_do_id("t", "Classe.t"), "Classe.t")  # classe na primeira parte: sobra o completo
        self.assertEqual(f.modulo_do_id("x", "x"), "x")  # uma parte só: nada a tirar
        self.assertEqual(f.modulo_do_id("a", "m.b"), "m.b")  # o último nome não é o do teste: fica inteiro
        self.assertEqual(f.modulo_do_id("t", "m.t"), "m")
        self.assertEqual(f.modulo_do_id("t", "pkg.m.Classe.t"), "pkg.m")


class Blocos(unittest.TestCase):
    def test_cabecalho_na_primeira_linha_nao_e_bloco(self):
        self.assertEqual(f.blocos("FAIL: t (m.C)\nx\n" + SEP), [])

    def test_so_separador_de_igual_abre_bloco(self):
        self.assertEqual(f.blocos(TRA + "\nFAIL: t (m.C)\nx\n"), [])
        self.assertEqual(len(f.blocos(SEP + "\nFAIL: t (m.C)\nx\n")), 1)

    def test_bloco_que_vai_ate_o_fim_do_registro(self):
        (_, linhas), = f.blocos(SEP + "\nFAIL: t (m.C)\n" + TRA + "\nTraceback\nValueError: x")
        self.assertEqual(linhas[-1], "ValueError: x")

    def test_traco_dentro_do_bloco_nao_fecha_o_bloco(self):
        (_, linhas), = f.blocos(SEP + "\nFAIL: t (m.C)\n" + TRA + "\nTraceback\nValueError: x\n" + SEP)
        self.assertIn(TRA, linhas)


class ErroDoBloco(unittest.TestCase):
    def test_linha_em_branco_nao_conta_como_erro(self):
        self.assertEqual(f.erro_do_bloco(["  File x", "    y", "ValueError: a", "  extra", ""]), "ValueError: a")

    def test_linha_com_tab_e_recuada(self):
        self.assertEqual(f.erro_do_bloco(["\tcodigo", "ValueError: a"]), "ValueError: a")

    def test_traceback_sem_quadro_antes_da_excecao(self):
        self.assertEqual(f.erro_do_bloco(["Traceback (most recent call last):", "ValueError: boom"]), "ValueError: boom")


class Local(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.raiz = Path(self.t.name).resolve()
        for rel in ("pkg/tests/test_a.py", "pkg/mod.py", "scripts/y.py"):
            (self.raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.raiz / rel).write_text("x\n", encoding="utf-8")

    def falha(self, *quadros, **kw):
        (a,) = f.falhas(bloco(*[(self.raiz / q, n) for q, n in quadros], **kw), self.raiz)
        return a

    def test_quadro_fora_do_repositorio_e_ignorado(self):
        texto = bloco(("/etc/passwd", 9), (self.raiz / "scripts/y.py", 4))
        (b,) = f.falhas(texto, self.raiz)
        self.assertEqual((b["arquivo"], b["linha"]), ("scripts/y.py", 4))

    def test_pasta_tests_aninhada_vale_como_teste(self):
        a = self.falha(("pkg/tests/test_a.py", 2), ("pkg/mod.py", 7))
        self.assertEqual((a["arquivo"], a["linha"]), ("pkg/tests/test_a.py", 2))

    def test_so_quadro_do_repositorio_fora_dos_testes_serve(self):
        a = self.falha(("pkg/mod.py", 7))
        self.assertEqual((a["arquivo"], a["linha"]), ("pkg/mod.py", 7))

    def test_sem_quadro_nenhum_fica_sem_arquivo(self):
        a = self.falha()
        self.assertEqual((a["arquivo"], a["linha"]), (None, 0))

    def test_sem_excecao_o_erro_e_o_tipo(self):
        self.assertEqual(self.falha(("pkg/mod.py", 7), erro="")["erro"], "FAIL")

    def test_nome_que_termina_o_completo_sem_ponto_leva_o_nome(self):
        a = self.falha(("pkg/mod.py", 7), nome="FAIL: e (m.Classe)")
        self.assertEqual(a["teste"], "m.Classe.e")


class Resumo(unittest.TestCase):
    def test_registro_sem_testes(self):
        self.assertEqual(f.resumo("p", "", []), ["p: sem testes no registro"])

    def test_falha_sem_arquivo_mostra_interrogacao(self):
        linha = [x for x in f.resumo("p", "", [achada(arquivo=None)]) if x.startswith("| m.C.t")][0]
        self.assertIn("| ? |", linha)

    def test_no_teto_exato_nao_diz_e_mais(self):
        n = f.TETO_TABELA
        linhas = f.resumo("p", "", [achada(teste=f"m.C.t{i}") for i in range(n)])
        self.assertFalse([x for x in linhas if x.startswith("e mais")])
        mais = f.resumo("p", "", [achada(teste=f"m.C.t{i}") for i in range(n + 1)])
        self.assertIn("e mais 1 no registro do passo", mais)

    def test_anotacao_sem_arquivo_nao_leva_propriedades(self):
        self.assertEqual(f.anotacoes([achada(arquivo=None)]), ["::error::m.C.t: E"])

    def test_sobras_param_no_teto_e_aceitam_as_duas_causas(self):
        registro = "\n".join(["FAILED a"] * 8)
        self.assertEqual(len(f.resumo("p", registro, [])), 2 + f.TETO_SOBRAS)
        self.assertIn("falhou sem teste", f.resumo("p", "suite-partes: causa tipo=x\n", [])[0])


class Principal(unittest.TestCase):
    def test_main_usa_o_ambiente_e_a_raiz_injetados(self):
        with tempfile.TemporaryDirectory() as t:
            pasta = Path(t).resolve()
            (pasta / "tests").mkdir()
            (pasta / "tests/test_x.py").write_text("x\n", encoding="utf-8")
            (pasta / "reg.log").write_text(bloco((pasta / "tests/test_x.py", 1)), encoding="utf-8")
            destino = pasta / "resumo.md"
            with mock.patch("builtins.print") as imp:
                rc = f.main(["parte", str(pasta / "reg.log")], {"GITHUB_STEP_SUMMARY": str(destino)}, pasta)
            self.assertEqual(rc, 0)
            self.assertIn("1 teste(s) falharam", destino.read_text(encoding="utf-8"))
            self.assertIn("file=tests/test_x.py,line=1", imp.call_args_list[0].args[0])

    def test_argumento_a_mais_nao_reprova_e_so_avisa(self):
        r = subprocess.run(["python3", "-I", str(RAIZ / "scripts/falhas-no-resumo.py"), "a", "b", "c"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("uso:", r.stderr)


class CorpoDoPr(unittest.TestCase):
    def pr(self, dados):
        with mock.patch.object(fc.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(dados), "")):
            return fc.pr_da_branch(RAIZ, "melhoria/x", corpo=True)[0]

    def test_corpo_nulo_do_pr_vira_texto_vazio(self):
        base = {"number": 1, "state": "OPEN", "headRefOid": "a" * 40}
        self.assertEqual(self.pr({**base, "body": None})["body"], "")
        self.assertEqual(self.pr({**base, "body": "oi"})["body"], "oi")


if __name__ == "__main__":
    unittest.main()
