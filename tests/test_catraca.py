"""Testes da catraca (tests/catraca.py) em repositório git temporário: cada regra com um caso que passa e um que barra."""
import ast
import contextlib
import copy
import datetime
import hashlib
import http.client
import importlib.util
import io
import itertools
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
_EM_CI = os.environ.pop("GITHUB_ACTIONS", None)  # a suíte roda como execução local; os testes de CI definem a variável


def tearDownModule():
    if _EM_CI is not None:
        os.environ["GITHUB_ACTIONS"] = _EM_CI
spec = importlib.util.spec_from_file_location("catraca", AQUI / "catraca.py")
catraca = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catraca)

CONFIG = {
    "dono": "dona",
    "neutralidade_nucleo": {"pastas": ["agents"], "ignorar": [], "termos": ["\\bReact\\b"], "excecoes": {}},
    "limite_linhas": {"agente": 10},
    "termos_proibidos": ["Segredo1"],
    "anti_duplicacao": {"palavras": 12, "pastas": ["docs"], "excecoes": []},
    "invariantes": {"docs/regra.md": ["nunca sem teste"]},
    "custo_permitido": {},
}
HOOKS = {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "python3", "args": ["a.py"]},
                                                                  {"type": "command", "command": "python3", "args": ["b.py"]}]}]}}
_RELOGIO_DAS_FIXTURES = itertools.count()  # só cresce: cada chamada de `ambiente_de_git` vale um segundo a mais


def ambiente_de_git():
    """Ambiente de todo `git` que cria commit nas fixtures. Ordem: tira o `GIT_*` herdado (um hook exporta `GIT_DIR`, que
    levaria o commit ao repositório real), deixa a manutenção desligada e só então fixa as datas: a data inicial é fixa
    e o contador sobe um segundo por chamada, então o mesmo conteúdo não repete o SHA (b8) e a ordem do `git log` fica
    a cronológica, sem depender do relógio."""
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    data = datetime.datetime(2025, 6, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=next(_RELOGIO_DAS_FIXTURES))
    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = data.strftime("%Y-%m-%dT%H:%M:%SZ")
    return env


SHA_TRECHO = hashlib.sha256(b"trecho1").hexdigest()


def hash_(forma, tipo="trecho", n=None):
    """Entrada de `termos_proibidos_hash` para uma forma fictícia."""
    return {"tipo": tipo, "n": n or len(forma.strip()), "sha256": hashlib.sha256(forma.strip().encode()).hexdigest()}


TESTE = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n    def test_b(self): pass\n"


class AmbienteDeGitDasFixtures(unittest.TestCase):
    """FIXTURE-DATA-GIT: toda fixture que cria commit usa datas fixas e crescentes, nunca o relógio nem o `GIT_*` herdado."""

    def test_traz_as_duas_datas_iguais_e_crescentes(self):
        a, b = ambiente_de_git(), ambiente_de_git()
        self.assertEqual(a["GIT_AUTHOR_DATE"], a["GIT_COMMITTER_DATE"])
        self.assertEqual(b["GIT_AUTHOR_DATE"], b["GIT_COMMITTER_DATE"])
        self.assertLess(a["GIT_AUTHOR_DATE"], b["GIT_AUTHOR_DATE"])  # ISO 8601 em UTC: a ordem de texto é a cronológica
        self.assertTrue(a["GIT_AUTHOR_DATE"].startswith("2025-"))

    def test_nao_devolve_o_git_herdado_do_processo(self):
        herdado = {"GIT_DIR": "/nao/existe", "GIT_WORK_TREE": "/nao/existe", "GIT_INDEX_FILE": "/nao/existe", "GIT_AUTHOR_DATE": "1 +0000"}
        with mock.patch.dict(os.environ, herdado):
            env = ambiente_de_git()
        for chave in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            self.assertNotIn(chave, env)
        self.assertNotEqual(env["GIT_AUTHOR_DATE"], "1 +0000")
        self.assertEqual(env["GIT_CONFIG_COUNT"], "3")  # a manutenção segue desligada

    def test_commit_da_fixture_nao_depende_do_relogio(self):
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.escreve("a.txt", "a\n")
        repo.commit()
        data = repo.git("log", "-1", "--format=%aI").strip()
        self.assertTrue(data.startswith("2025-"), data)


class Repo:
    """Repositório temporário com um commit `base` (tag) e a branch `pr` por cima."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.git("init", "-q", "-b", "develop")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "Teste")
        self.escreve("tests/config.json", json.dumps(CONFIG))
        self.escreve("hooks/hooks.json", json.dumps(HOOKS))
        self.escreve("tests/test_x.py", TESTE)
        self.escreve("tests/hooks/p/um.json", "{}")
        self.escreve("tests/hooks/p/dois.json", "{}")
        self.escreve("tests/catraca.py", "x = 'presente na base'\n")
        self.escreve(".github/workflows/ci.yml", "name: CI\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("tag", "base")
        self.git("checkout", "-q", "-b", "pr")

    def git(self, *args):
        env = ambiente_de_git()
        return subprocess.run(["git", "-C", str(self.dir), *args], check=True, capture_output=True, text=True, env=env).stdout

    def escreve(self, rel, texto):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")

    def config(self, **mudancas):
        cfg = copy.deepcopy(CONFIG)
        for chave, valor in mudancas.items():
            cfg[chave] = valor(cfg[chave]) if callable(valor) else valor
        self.escreve("tests/config.json", json.dumps(cfg))

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "pr")

    def violacoes(self):
        return catraca.violacoes_das_regras(self.dir, "base", "HEAD")

    def fecha(self):
        self.tmp.cleanup()


class Base(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.fecha)

    def barra(self, trecho, rid=None):
        self.repo.commit()
        achadas = self.repo.violacoes()
        self.assertTrue(any(trecho in v for v in achadas), achadas)
        if rid:
            self.assertTrue(any(v.startswith(rid + ":") and trecho in v for v in achadas), achadas)
        for v in achadas:  # formato único de mensagem
            self.assertRegex(v, r"^R-[A-Z]+: .+\. Por quê: .+\. Corrigir: .+ \(.+\)$")

    def passa(self):
        self.repo.commit()
        self.assertEqual(self.repo.violacoes(), [])


class RegrasDeConfig(Base):
    def test_sem_mudanca_passa(self):
        self.passa()

    def test_invariante_removido_barra_e_acrescimo_passa(self):
        self.repo.config(invariantes=lambda i: {**i, "docs/nova.md": ["x"]})
        self.passa()
        self.repo.config(invariantes=lambda i: {"docs/regra.md": []})
        self.barra("nunca sem teste", "R-CONFORMIDADE")

    def test_invariante_alterado_barra(self):
        self.repo.config(invariantes=lambda i: {"docs/regra.md": ["nunca sem testes"]})
        self.barra("nunca sem teste")

    def test_termo_proibido_em_claro_removido_barra_sem_mostrar_o_texto(self):
        self.repo.config(termos_proibidos=lambda t: t + ["Outro"])
        self.passa()
        self.repo.config(termos_proibidos=[])
        self.barra("termo nº 1 (sha256 ", "R-NEUTRO")
        self.assertFalse(any("Segredo1" in v or "segredo1" in v for v in self.repo.violacoes()))

    def test_remover_hash_barra_e_acrescimo_passa(self):
        self.repo.escreve("tests/config.json", json.dumps({**CONFIG, "termos_proibidos_hash": [hash_("zebra"), hash_("trecho1")]}))
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "hash")
        self.repo.git("tag", "-f", "base")
        base = [hash_("zebra"), hash_("trecho1")]
        self.repo.config(termos_proibidos_hash=base + [hash_("novo", "palavra")])
        self.passa()
        self.repo.config(termos_proibidos_hash=base[:1])
        self.barra(f"termo nº 2 (sha256 {SHA_TRECHO[:8]}…)", "R-NEUTRO")
        self.assertFalse(any("trecho1" in v for v in self.repo.violacoes()))

    def test_transicao_do_claro_para_hash_completa_passa(self):
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=[hash_("segredo1", "trecho")])
        self.passa()

    def test_transicao_incompleta_barra(self):
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=[hash_("outra", "trecho")])
        self.barra("sem cobertura em termos_proibidos_hash", "R-NEUTRO")
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=[hash_("segredo1", "palavra")])
        self.barra("sem cobertura")

    def test_transicao_de_palavra_par_e_classe(self):
        base = {**CONFIG, "termos_proibidos": ["\\bAlfa[12]\\b", "Beta ?Gama"]}
        self.repo.escreve("tests/config.json", json.dumps(base))
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "claro")
        self.repo.git("tag", "-f", "base")
        completo = [hash_("alfa1", "palavra"), hash_("alfa2", "palavra"), hash_("betagama", "trecho"), hash_("betagama", "par", [4, 4])]
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=completo)
        self.passa()
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=completo[1:])
        self.barra("termo nº 1 (sha256 ", "R-NEUTRO")
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=completo[:3])
        self.barra("termo nº 2 (sha256 ")

    def test_regex_complexa_na_transicao_barra(self):
        self.repo.escreve("tests/config.json", json.dumps({**CONFIG, "termos_proibidos": ["Zeta(a|b)"]}))
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "regex")
        self.repo.git("tag", "-f", "base")
        self.repo.config(termos_proibidos=[], termos_proibidos_hash=[hash_("zetaa", "trecho"), hash_("zetab", "trecho")])
        self.barra("termo nº 1 (sha256 ")

    def test_termo_de_neutralidade_removido_ou_mudado_barra(self):
        self.repo.config(neutralidade_nucleo=lambda n: {**n, "termos": ["\\bReact\\b", "\\bVue\\b"]})
        self.passa()
        self.repo.config(neutralidade_nucleo=lambda n: {**n, "termos": ["\\bReact\\s"]})
        self.barra("termo de neutralidade", "R-NEUTRO")

    def test_limite_de_linhas(self):
        self.repo.config(limite_linhas={"agente": 9})
        self.passa()
        self.repo.config(limite_linhas={"agente": 11})
        self.barra("limite_linhas.agente", "R-CONFORMIDADE")

    def test_excecao_nova_de_neutralidade(self):
        self.repo.config(neutralidade_nucleo=lambda n: {**n, "excecoes": {"agents/a.md": ["\\bReact\\b"]}})
        self.barra("exceção nova de neutralidade", "R-NEUTRO")

    def test_excecao_nova_de_anti_duplicacao(self):
        self.repo.config(anti_duplicacao=lambda a: {**a, "excecoes": ["um trecho qualquer"]})
        self.barra("anti-duplicação", "R-CONFORMIDADE")

    def test_dono_mudou(self):
        self.repo.config(dono="outra")
        self.barra("`dono`", "R-CONTRIB")

    def test_dono_novo_na_introducao_passa(self):
        cfg = copy.deepcopy(CONFIG)
        del cfg["dono"]
        self.repo.escreve("tests/config.json", json.dumps(cfg))
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "sem dono")
        self.repo.git("tag", "-f", "base")
        self.repo.config()
        self.passa()

    def test_permissao_de_custo_nova_barra(self):
        self.repo.config(custo_permitido={"bin/x": ["chave-de-api"]})
        self.barra("permissão nova", "R-CUSTO")


class ArquivosDeRegras(Base):
    """QA BUG-02: apagar ou renomear arquivo com invariantes (ou de docs/regras/) barra."""

    def prepara(self):
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.escreve("docs/regra.md", "nunca sem teste\n")
        repo.escreve("docs/regras/R-X.md", "regra\n")
        repo.git("add", "-A")
        repo.git("commit", "-q", "-m", "regras")
        repo.git("tag", "-f", "base")
        return repo

    def test_apagar_ou_mover_barra(self):
        for rel in ("docs/regra.md", "docs/regras/R-X.md"):
            for como in ("mv", "rm"):
                with self.subTest(rel=rel, como=como):
                    repo = self.prepara()
                    repo.git(como, rel, *(["novo.md"] if como == "mv" else []))
                    repo.commit()
                    self.assertTrue(any(f"arquivo de regra apagado ou movido: {rel}" in v for v in repo.violacoes()), repo.violacoes())

    def test_editar_o_arquivo_passa(self):
        repo = self.prepara()
        repo.escreve("docs/regras/R-X.md", "regra melhor\n")
        repo.commit()
        self.assertEqual(repo.violacoes(), [])

    def test_remover_chave_de_limite_ou_de_palavras_barra(self):
        self.repo.config(limite_linhas=lambda d: {})
        self.barra("limite_linhas.agente removido")
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.config(anti_duplicacao=lambda d: {k: x for k, x in d.items() if k != "palavras"})
        repo.commit()
        self.assertTrue(any("anti_duplicacao.palavras removido" in v for v in repo.violacoes()))


class Hooks(Base):
    def test_hook_removido_barra_e_novo_passa(self):
        novo = copy.deepcopy(HOOKS)
        novo["hooks"]["PreToolUse"][0]["hooks"].append({"type": "command", "command": "python3", "args": ["c.py"]})
        self.repo.escreve("hooks/hooks.json", json.dumps(novo))
        self.passa()
        antigo = copy.deepcopy(HOOKS)
        del antigo["hooks"]["PreToolUse"][0]["hooks"][1]
        self.repo.escreve("hooks/hooks.json", json.dumps(antigo))
        self.barra("b.py", "R-CONFORMIDADE")

    def test_arquivo_de_hooks_apagado_barra(self):
        (self.repo.dir / "hooks/hooks.json").unlink()
        self.barra("hook removido")


class Testes(Base):
    def test_testes_novos_passam_e_queda_barra(self):
        self.repo.escreve("tests/test_y.py", TESTE.replace("pass", "self.assertTrue(True)"))
        self.passa()
        self.repo.escreve("tests/test_x.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
        self.repo.escreve("tests/test_y.py", "")
        self.barra("`test_*` caíram de 2 para 1", "R-CONFORMIDADE")

    def test_mover_teste_entre_arquivos_passa(self):
        self.repo.escreve("tests/test_x.py", "")
        self.repo.escreve("tests/test_y.py", TESTE)
        self.passa()

    def test_fixture_removida_barra(self):
        (self.repo.dir / "tests/hooks/p/dois.json").unlink()
        self.barra("fixtures de tests/hooks caíram de 2 para 1")

    def test_fixture_nova_passa(self):
        self.repo.escreve("tests/hooks/p/tres.json", "{}")
        self.passa()


class TestesEnfraquecidos(Base):
    """Review 4: esvaziar, pular ou tirar asserção de teste existente barra, mesmo com a contagem de `def test_*` igual."""

    def com_asserts(self):
        self.repo.escreve("tests/test_y.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n"
                          "        self.assertEqual(1, 1)\n        assert True\n")
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "com asserções")
        self.repo.git("tag", "-f", "base")

    def test_remover_assert_barra(self):
        self.com_asserts()
        self.repo.escreve("tests/test_y.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertEqual(1, 1)\n")
        self.barra("asserções em tests/ caíram de 2 para 1", "R-CONFORMIDADE")

    def test_esvaziar_o_teste_barra(self):
        self.com_asserts()
        self.repo.escreve("tests/test_y.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n")
        self.repo.commit()
        achadas = self.repo.violacoes()
        self.assertTrue(any("asserções em tests/ caíram" in v for v in achadas), achadas)
        self.assertTrue(any("testes vazios" in v for v in achadas), achadas)

    def test_acrescentar_skip_ou_expected_failure_barra(self):
        for dec in ("@unittest.skip('x')", "@unittest.skipIf(True, 'x')", "@unittest.expectedFailure"):
            with self.subTest(dec):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve("tests/test_x.py", TESTE.replace("    def test_a", f"    {dec}\n    def test_a"))
                repo.commit()
                self.assertTrue(any("skip/skipIf/skipUnless/expectedFailure" in v for v in repo.violacoes()), dec)
        self.repo.escreve("tests/test_x.py", TESTE.replace("def test_a(self): pass", "def test_a(self):\n        self.skipTest('x')"))
        self.barra("subiram de 0 para 1")

    def test_acrescentar_asserts_e_testes_com_corpo_passa(self):
        self.repo.escreve("tests/test_y.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertTrue(True)\n")
        self.passa()

    def test_catraca_py_fica_fora_da_contagem(self):
        self.repo.escreve("tests/catraca.py", "assert True\n")
        self.repo.commit()
        self.assertFalse(any("asserções" in v for v in self.repo.violacoes()))


class ControlesEnfraquecidos(Base):
    """MAQ-I7a: a força conta por módulo de controle; ilegível, grande demais ou renomeado conta zero."""
    HOOKS_PY = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertTrue(1)\n        assert 2\n"

    def com_controle(self, nome="tests/test_hooks.py"):
        self.repo.escreve(nome, self.HOOKS_PY)
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "com controle")
        self.repo.git("tag", "-f", "base")

    def sem_traceback(self, funcao, *args):
        try:
            return funcao(*args)
        except Exception as e:  # a catraca que morre por um arquivo falha aqui por asserção, não por erro
            self.fail(f"a catraca morreu: {e!r}")

    def test_assercao_movida_para_modulo_comum_barra_mesmo_com_o_total_igual(self):
        self.com_controle()
        self.repo.escreve("tests/test_hooks.py", self.HOOKS_PY.replace("        assert 2\n", ""))
        self.repo.escreve("tests/test_forge.py", "def f():\n    assert 2\n")
        self.barra("módulo de controle tests/test_hooks.py enfraqueceu", "R-CONFORMIDADE")
        self.assertFalse(any("asserções em tests/ caíram" in v for v in self.repo.violacoes()))

    def test_cada_familia_de_controle_conta_por_modulo(self):
        for nome in ("tests/test_hooks_volta_x.py", "tests/test_pre_push_y.py", "tests/test_suite_partes.py",
                     "tests/test_testes_tocados.py", "tests/test_catraca_z.py"):
            with self.subTest(nome):
                self.repo.git("reset", "-q", "--hard", "base")
                self.com_controle(nome)
                self.repo.escreve(nome, self.HOOKS_PY.replace("        assert 2\n", ""))
                self.repo.escreve("tests/test_y.py", "def f():\n    assert 2\n")
                self.barra(f"módulo de controle {nome} enfraqueceu")

    def test_fora_das_familias_nao_e_controle(self):
        for nome in ("tests/test_forge.py", "tests/evals/test_hooks.py", "tests/hooks_test.py", "tests/test_hooks.txt"):
            self.assertFalse(catraca.eh_controle(nome), nome)

    def test_controle_renomeado_ou_apagado_barra(self):
        self.com_controle()
        self.repo.git("mv", "tests/test_hooks.py", "tests/hooks_t.py")
        self.barra("tests/test_hooks.py enfraqueceu")

    def test_controle_ilegivel_ou_grande_demais_barra_sem_derrubar_a_catraca(self):
        self.com_controle()
        casos = {"parêntese a mais": self.HOOKS_PY + ")\n", "10 mil parênteses": self.HOOKS_PY + "x = " + "(" * 10000 + ")" * 10000 + "\n",
                 "aninhamento fundo": self.HOOKS_PY + "x = " + "-" * 200000 + "1\n", "UTF-8 inválido": None,
                 "acima de 2 MB": self.HOOKS_PY + "#" * catraca.TETO_DO_MODULO + "\n"}
        queda = "tests/test_hooks.py enfraqueceu: (asserções, pulos, vazios) de (2, 0, 0) para (0, 0, 0)"
        for nome, texto in casos.items():
            with self.subTest(nome):
                (self.repo.dir / "tests/test_hooks.py").write_bytes(texto.encode() if texto else self.HOOKS_PY.encode() + b"# \xff\n")
                self.repo.commit()
                self.assertIn(queda, "".join(self.sem_traceback(catraca.regra_controles_enfraquecidos, self.repo.dir, "base", "HEAD")))
        self.repo.escreve("tests/test_hooks.py", casos["parêntese a mais"])
        self.repo.commit()
        self.assertIn(queda, "".join(self.sem_traceback(self.repo.violacoes)))  # a catraca inteira não morre

    def test_pulo_ou_teste_vazio_levado_para_o_controle_barra(self):
        for nome, texto in (("skip", "import unittest\nclass T(unittest.TestCase):\n    @unittest.skip('x')\n    def test_a(self):\n        assert 1\n"),
                            ("vazio", TESTE)):
            with self.subTest(nome):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve("tests/test_hooks.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        assert 1\n")
                repo.commit()
                repo.git("tag", "-f", "base")
                repo.escreve("tests/test_hooks.py", texto)
                repo.commit()
                self.assertTrue(any("tests/test_hooks.py enfraqueceu" in v for v in repo.violacoes()), nome)

    def test_corpus_de_legitimos_passa(self):
        self.com_controle()
        self.repo.escreve("tests/test_y.py", "def f():\n    assert 1\n")
        self.repo.escreve("tests/test_hooks.py", self.HOOKS_PY.replace("assertTrue(1)", "assertEqual(1, 1)") + "        assert 3\n")
        self.repo.escreve("tests/test_catraca.py", "def f():\n    assert 1\n")
        self.passa()

    def test_git_que_falha_ao_ler_o_controle_falha_fechada(self):
        self.com_controle()
        real = catraca.git

        def falso(raiz, *a):
            return (128, "") if a[0] == "show" and a[-1].endswith(":tests/test_hooks.py") else real(raiz, *a)
        self.repo.commit()
        with mock.patch.object(catraca, "git", falso):
            achadas = self.sem_traceback(catraca.violacoes_das_regras, self.repo.dir, "base", "HEAD")
        self.assertTrue(any(catraca.NAO_LIBERAVEL in v and "tests/test_hooks.py" in v for v in achadas), achadas)

    def test_piora_no_controle_depois_do_rotulo_derruba_o_rotulo(self):
        """P9: os déficits por módulo de controle entram na conta do rótulo preso ao conteúdo."""
        self.com_controle()
        self.repo.escreve("tests/test_hooks.py", self.HOOKS_PY.replace("        assert 2\n", ""))
        self.repo.escreve("tests/test_y.py", "def f():\n    assert 2\n")
        self.repo.commit()
        rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("tests/test_hooks.py", self.HOOKS_PY.replace("        assert 2\n", "").replace("self.assertTrue(1)", "pass"))
        self.repo.escreve("tests/test_y.py", "def f():\n    assert 2\n    assert 1\n")
        self.repo.commit()
        self.assertFalse(catraca.protegidos_como_no_rotulo(self.repo.dir, "base", rotulado, "HEAD"))
        self.assertTrue(catraca.protegidos_como_no_rotulo(self.repo.dir, "base", rotulado, rotulado))


class TestesNoCi(Base):
    """MAQ-I7b com T4, uma regra só: o teste que sai do discover, o arquivo de teste que nenhum comando do CI roda, a classe
    citada num `run:` que some e a exceção nova em `testes_fora_do_ci` barram. Tudo pela árvore do git e por AST."""
    QUEDA = "módulos de teste que o `discover` da suíte vê caíram de 1 para 0"
    sem_traceback = ControlesEnfraquecidos.sem_traceback

    def move(self, destino, extra=None):
        (self.repo.dir / destino).parent.mkdir(parents=True, exist_ok=True)
        (self.repo.dir / "tests/test_x.py").rename(self.repo.dir / destino)
        if extra:
            self.repo.escreve(extra, "")

    def nova_base(self):
        self.repo.commit()
        self.repo.git("tag", "-f", "base")

    def test_modulo_fora_do_alcance_do_discover_barra(self):
        for destino, extra in (("tests/test-x.py", None), ("tests/x.py", None), ("tests/Test_x.py", None), ("tests/test_x_py", None),
                               ("tests/sub/test_x.py", None), ("tests/pa-c/test_x.py", "tests/pa-c/__init__.py")):
            with self.subTest(destino):
                self.repo.git("reset", "-q", "--hard", "base")  # no começo: o caso que falha não contamina o seguinte
                self.repo.git("clean", "-qfd", "tests")
                self.move(destino, extra)
                self.barra(self.QUEDA, "R-CONFORMIDADE")

    def test_init_apagado_tira_o_pacote_do_discover(self):
        self.repo.escreve("tests/pac/__init__.py", "")
        self.repo.escreve("tests/pac/test_p.py", TESTE)
        self.nova_base()
        (self.repo.dir / "tests/pac/__init__.py").unlink()
        self.barra("módulos de teste que o `discover` da suíte vê caíram de 2 para 1")
        self.assertTrue(any("nenhum comando do CI roda: tests/pac/test_p.py" in v for v in self.repo.violacoes()))

    def test_corpus_de_legitimos_passa(self):
        self.move("tests/pac/testx.py", "tests/pac/__init__.py")
        self.repo.escreve("tests/pac/testx.py", TESTE + "#" * catraca.TETO_DO_MODULO + "\n")  # o teto vale só para módulo de controle
        self.passa()
        self.repo.escreve("tests/test_novo.py", TESTE.replace("pass", "assert 1"))
        self.passa()

    def test_rename_compensado_por_modulo_novo_barra(self):
        """S1 da segurança g2: tests/test_x.py vira tests/x.py e tests/test_z.py novo repõe a contagem; os totais não caem."""
        self.move("tests/x.py")
        self.repo.escreve("tests/test_z.py", TESTE)
        self.barra("testes `test_*` em tests/ fora do alcance do `discover` subiram de 0 para 2", "R-CONFORMIDADE")

    def test_legitimos_nao_sobem_os_testes_fora_do_discover(self):
        cheio = TESTE.replace("pass", "assert 1")  # sem `pass`: a regra dos testes vazios não entra no caso
        casos = {"módulo novo": lambda: self.repo.escreve("tests/test_novo.py", cheio),
                 "rename de test_a.py para test_b.py": lambda: self.move("tests/test_b.py"),
                 "asserção nova": lambda: self.repo.escreve("tests/test_x.py", cheio),
                 "corpus em tests/hooks/": lambda: self.repo.escreve("tests/hooks/caso.py", cheio),
                 "ajudante sem teste": lambda: self.repo.escreve("tests/ajuda.py", "def f():\n    return 1\n"),
                 "pacote novo com __init__.py": lambda: (self.repo.escreve("tests/evals/__init__.py", ""),
                                                         self.repo.escreve("tests/evals/test_e.py", cheio))}
        for nome, muda in casos.items():
            with self.subTest(nome):
                self.repo.git("reset", "-q", "--hard", "base")
                self.repo.git("clean", "-qfd", "tests")
                muda()
                self.passa()

    def test_modulo_ilegivel_ou_controle_grande_demais_derruba_os_testes_sem_traceback(self):
        self.repo.escreve("tests/test_hooks.py", TESTE)
        self.nova_base()
        casos = {"parêntese a mais": ("tests/test_x.py", TESTE.encode() + b")\n"), "UTF-8 inválido": ("tests/test_x.py", TESTE.encode() + b"# \xff\n"),
                 "aninhamento fundo": ("tests/test_x.py", TESTE.encode() + b"x = " + b"-" * 200000 + b"1\n"),
                 "controle acima de 2 MB": ("tests/test_hooks.py", TESTE.encode() + b"#" * catraca.TETO_DO_MODULO + b"\n")}
        for nome, (arq, texto) in casos.items():
            with self.subTest(nome):
                self.repo.git("reset", "-q", "--hard", "base")
                (self.repo.dir / arq).write_bytes(texto)
                self.repo.commit()
                achadas = self.sem_traceback(catraca.regra_testes_no_ci, self.repo.dir, "base", "HEAD", {})
                self.assertIn("testes `test_*` que o `discover` da suíte vê caíram de 4 para 2", "".join(achadas))

    def test_git_que_falha_ao_ler_o_modulo_falha_fechada(self):
        real = catraca.git

        def falso(raiz, *a):
            return (128, "") if a[0] == "show" and a[-1] == "HEAD:tests/test_x.py" else real(raiz, *a)
        self.repo.commit()
        with mock.patch.object(catraca, "git", falso):
            achadas = self.sem_traceback(catraca.violacoes_das_regras, self.repo.dir, "base", "HEAD")
        self.assertTrue(any(catraca.NAO_LIBERAVEL in v and "tests/test_x.py" in v for v in achadas), achadas)

    # T4: arquivo de teste que nenhum comando do CI roda.
    SOLTOS = ["tests/b_test.py", "tests/c.test.ts", "tests/sub/test_s.py", "tests/web/a.spec.js", "tests/x.sh"]

    def fora(self, achadas):
        return sorted(v.split("nenhum comando do CI roda: ", 1)[1].split(". Por quê", 1)[0] for v in achadas if "nenhum comando do CI roda" in v)

    def test_arquivo_de_teste_que_nenhum_comando_roda_barra(self):
        for a in self.SOLTOS:
            self.repo.escreve(a, "")
        self.repo.commit()
        self.assertEqual(self.fora(self.repo.violacoes()), self.SOLTOS)

    def test_run_com_o_caminho_inteiro_ou_excecao_da_base_bastam(self):
        self.repo.config(testes_fora_do_ci={"tests/sub/test_s.py": "roda à mão: precisa de rede real"})
        self.nova_base()
        for a in self.SOLTOS:
            self.repo.escreve(a, "")
        self.repo.escreve(".github/workflows/ci.yml", "jobs:\n  t:\n    steps:\n      - run: bash tests/x.sh\n      - run: |\n"
                          "          node tests/web/a.spec.js tests/c.test.ts\n          python3 tests/b_test.py\n      - name: y\n        run: echo\n")
        self.repo.commit()
        achadas = [v for v in self.repo.violacoes() if not v.startswith("R-CONFORMIDADE: mudança em .github")]
        self.assertEqual(self.fora(achadas), [])

    def test_nome_sem_o_caminho_comentario_fim_do_bloco_ou_motivo_invalido_nao_bastam(self):
        soltos = ["tests/sub/test_s.py", "tests/u.sh", "tests/v.sh", "tests/w.sh", "tests/x.sh", "tests/y.sh", "tests/z.sh"]
        self.repo.config(testes_fora_do_ci={"tests/sub/test_s.py": "curto", "tests/u.sh": "\u200b" * 25, "tests/w.sh": list("x" * 25)})
        self.nova_base()
        for a in soltos:
            self.repo.escreve(a, "")
        self.repo.escreve(".github/workflows/ci.yml", "      - run: bash x.sh; bash outro/tests/x.sh tests/x.sh.bak; echo ok # tests/y.sh\n"
                          "      - run: |\n          # bash tests/z.sh\n          true\n        env: tests/v.sh\n")
        self.repo.commit()
        self.assertEqual(self.fora(self.repo.violacoes()), soltos)

    def test_comando_do_ci_que_deixa_de_rodar_o_arquivo_barra(self):
        self.repo.escreve("tests/e2e.sh", "")
        self.repo.escreve(".github/workflows/ci.yml", "      - run: bash tests/e2e.sh\n")
        self.nova_base()
        self.repo.escreve(".github/workflows/ci.yml", "      - run: echo nada\n")
        self.barra("nenhum comando do CI roda: tests/e2e.sh")

    def test_arquivo_ja_fora_na_base_nao_barra_de_novo(self):
        self.repo.escreve("tests/velho.sh", "")
        self.nova_base()
        self.repo.escreve("tests/velho.sh", "echo mudou\n")
        self.passa()

    def test_excecao_nova_no_head_barra_e_nao_libera_o_arquivo(self):
        self.repo.config(testes_fora_do_ci={"tests/x.sh": "roda à mão: precisa de rede real"})
        self.repo.escreve("tests/x.sh", "")
        self.repo.commit()
        achadas = self.repo.violacoes()
        self.assertTrue(any("exceção nova em `testes_fora_do_ci`: tests/x.sh" in v for v in achadas), achadas)
        self.assertEqual(self.fora(achadas), ["tests/x.sh"])

    def test_classe_citada_num_run_que_some_barra(self):
        self.repo.escreve("tests/test_m0.py", "import unittest\nclass Existe(unittest.TestCase):\n    def test_a(self):\n        assert 1\n")
        self.repo.escreve("tests/evals/__init__.py", "")
        self.repo.escreve("tests/evals/test_e.py", "import unittest\nclass E(unittest.TestCase):\n    def test_a(self):\n        assert 1\n")
        self.repo.escreve(".github/workflows/ci.yml", "      - run: python3 -m unittest tests.test_m0.Existe.test_a tests.evals.test_e.E\n")
        self.nova_base()
        self.assertEqual(catraca.classes_citadas_ausentes(self.repo.dir, "base"), set())
        self.repo.escreve("tests/test_m0.py", "import unittest\nclass Outra(unittest.TestCase):\n    def test_a(self):\n        assert 1\n")
        self.barra("classe citada num `run:` do CI não existe: tests.test_m0.Existe", "R-CONFORMIDADE")

    def test_bate_com_os_modulos_da_suite_paralela(self):
        """A mesma lista que `modulos()` de scripts/suite-paralela.py (e o discover que scripts/suite-partes.py divide) dá."""
        spec_suite = importlib.util.spec_from_file_location("suite_paralela_i7", AQUI.parent / "scripts" / "suite-paralela.py")
        suite = importlib.util.module_from_spec(spec_suite)
        spec_suite.loader.exec_module(suite)
        for nome in ("testy.py", "test-z.py", "Test_w.py", "x.py", "test_v.txt", "pac/__init__.py", "pac/test_p.py", "sem/test_q.py"):
            self.repo.escreve(f"tests/{nome}", TESTE)
        self.repo.commit()
        for raiz in (AQUI.parent, self.repo.dir):
            with self.subTest(str(raiz)), mock.patch.object(suite, "RAIZ", raiz):
                self.assertEqual(sorted(catraca.modulos_descobriveis(raiz, "HEAD")),
                                 sorted(f"tests/{m.replace('.', '/')}.py" for m in suite.modulos()))
        self.assertGreater(len(suite.modulos()), 100)

    def test_arvore_do_forge_roda_todo_teste_no_ci(self):
        """Na árvore real: nenhum arquivo de teste fora do CI e nenhuma classe citada ausente."""
        cfg = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(catraca.testes_fora_do_ci(AQUI.parent, "HEAD", catraca._excecoes_do_ci(cfg)), [])
        self.assertTrue([c for r in catraca.runs_dos_workflows(AQUI.parent, "HEAD") for c in catraca.CLASSE_CITADA.findall(r)])
        self.assertEqual(catraca.classes_citadas_ausentes(AQUI.parent, "HEAD"), set())

    def test_funcoes_do_i7_so_leem_pelo_git_e_pelo_ast(self):
        """As funções do I7 e da T4, e as do arquivo que elas chamam, não importam nem executam nada do head."""
        funcoes = {n.name: n for n in ast.parse((AQUI / "catraca.py").read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)}
        proibidos = {"importlib", "__import__", "exec", "eval", "compile", "runpy", "TestLoader", "discover", "SourceFileLoader",
                     "import_module", "system", "popen", "execv", "execvp", "spawnv", "run_path", "run_module", "loadTestsFromName"}
        pendentes, vistas = ["regra_controles_enfraquecidos", "regra_testes_no_ci", "deficits_do_ci"], set()
        while pendentes:
            nome = pendentes.pop()
            vistas.add(nome)
            for n in ast.walk(funcoes[nome]):
                palavra = n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else None
                self.assertNotIn(palavra, proibidos, f"{nome} usa {palavra}")
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and catraca._nome(n.func.value) == "subprocess":
                    self.assertEqual(ast.literal_eval(n.args[0].elts[0]), "git", nome)
                if palavra in funcoes and palavra not in vistas:
                    pendentes.append(palavra)
        self.assertLessEqual({"git", "ler", "listar", "modulos_descobriveis", "_forca_das_arvores", "testes_fora_do_ci"}, vistas)

    def test_saida_do_ci_depois_do_rotulo_derruba_o_rotulo(self):
        """P9: arquivo de teste novo fora do CI depois do rótulo entra na conta do rótulo preso ao conteúdo."""
        self.repo.escreve("tests/a.sh", "")
        self.repo.commit()
        rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("tests/b.sh", "")
        self.repo.commit()
        self.assertFalse(catraca.protegidos_como_no_rotulo(self.repo.dir, "base", rotulado, "HEAD"))


class TetoDePulados(Base):
    """T3: `teto_pulados` de tests/config.json só cai; sair, virar outro tipo ou subir barra."""

    def com_teto(self, teto):
        self.repo.config(teto_pulados=teto)
        self.repo.commit()
        self.repo.git("tag", "-f", "base")

    def test_teto_que_sobe_barra_e_que_cai_passa(self):
        self.com_teto(1)
        self.repo.config(teto_pulados=2)
        self.barra("`teto_pulados` subiu de 1 para 2", "R-CONFORMIDADE")
        self.repo.config(teto_pulados=0)
        self.passa()

    def test_teto_que_sai_ou_vira_outro_tipo_barra(self):
        self.com_teto(1)
        for teto in (None, "1", True, 1.0, -1, [1]):
            with self.subTest(teto=teto):
                cfg = copy.deepcopy(CONFIG)
                if teto is not None:
                    cfg["teto_pulados"] = teto
                self.repo.escreve("tests/config.json", json.dumps(cfg))
                self.barra("`teto_pulados` saiu de tests/config.json ou não é inteiro >= 0")

    def test_sem_teto_na_base_nada_a_conferir(self):
        self.repo.config(teto_pulados=5)
        self.passa()
        self.assertEqual(catraca.regra_teto_pulados(None, {}), [])

    def test_o_forge_tem_teto(self):
        teto = json.loads((AQUI / "config.json").read_text(encoding="utf-8")).get("teto_pulados")
        self.assertIs(type(teto), int)
        self.assertGreaterEqual(teto, 0)


class GuardasDosHooks(Base):
    """MUTANTES-SPEC-HOOKS: condição mudada ou apagada em hooks/*.py sem mutante declarado numa spec do diff barra."""
    HOOK = "def decide(valor):\n    if valor > 10:\n        return 'bloqueia'\n    return 'passa'\n"

    def setUp(self):
        super().setUp()
        self.repo.escreve("hooks/x.py", self.HOOK)
        self.repo.commit()
        self.repo.git("tag", "-f", "base")

    def spec(self, mutantes, isentas=None, nome="tests/mutantes/p.json"):
        dados = {"pedido": "p", "mutantes": mutantes} | ({"isentas": isentas} if isentas else {})
        self.repo.escreve(nome, json.dumps(dados))

    def mutante(self, de="if valor > 11:", para="if valor >= 11:"):
        return {"id": "M1", "guarda": "limite do bloqueio", "arquivo": "hooks/x.py", "de": de, "para": para,
                "testes": ["tests.test_x.T.test_a"]}

    def test_guarda_mudada_sem_spec_barra(self):
        self.repo.escreve("hooks/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.barra("guarda de hooks/x.py mudada sem mutante declarado: sem mutante · hooks/x.py:2", "R-QA")

    def test_guarda_mudada_com_mutante_na_spec_do_diff_passa(self):
        self.repo.escreve("hooks/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.spec([self.mutante()])
        self.passa()

    def test_spec_que_ja_estava_na_base_nao_vale(self):
        self.spec([self.mutante()])
        self.repo.commit()
        self.repo.git("tag", "-f", "base")
        self.repo.escreve("hooks/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.barra("sem mutante · hooks/x.py:2")

    def test_mutante_de_outro_arquivo_ou_que_nao_cobre_a_condicao_barra(self):
        self.repo.escreve("hooks/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.repo.escreve("hooks/y.py", "Y = 1\n")
        self.spec([self.mutante() | {"arquivo": "hooks/y.py", "de": "Y = 1", "para": "Y = 2"}])
        self.barra("sem mutante · hooks/x.py:2")

    def test_guarda_apagada_barra_e_isenta_com_motivo_passa(self):
        self.repo.escreve("hooks/x.py", "def decide(valor):\n    return 'passa'\n")
        self.barra("apagada · hooks/x.py:2(base)")
        self.spec([self.mutante() | {"de": "return 'passa'", "para": "return 'bloqueia'"}],
                  [{"arquivo": "hooks/x.py", "trecho": "valor > 10", "motivo": "a guarda saiu com o comportamento que ela protegia"}])
        self.repo.commit()
        self.assertFalse(any(v.startswith("R-QA:") for v in self.repo.violacoes()), self.repo.violacoes())

    def test_mudanca_sem_guarda_e_arquivo_que_nao_e_python_passam(self):
        self.repo.escreve("hooks/x.py", self.HOOK.replace("'bloqueia'", "'bloqueia agora'"))
        self.repo.escreve("hooks/dados.json", "{\"if\": 1}\n")
        self.passa()

    def test_guarda_fora_do_controle_nao_entra_na_regra(self):
        self.repo.escreve("exemplos/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.repo.escreve("tests/test_hooks_x.py", self.HOOK.replace("valor > 10", "valor > 11"))  # teste não pede mutante
        self.passa()

    def test_guarda_em_codigo_de_controle_fora_de_hooks_entra_na_regra(self):  # a classe C do forge-check classe
        self.repo.escreve("scripts/x.py", self.HOOK)
        self.repo.escreve("bin/forge-y", "#!/usr/bin/env python3\n" + self.HOOK)
        self.repo.escreve("bin/forge-z", "#!/usr/bin/env bash\nif [ 1 -gt 10 ]; then :; fi\n")
        self.repo.commit()
        self.repo.git("tag", "-f", "base")
        self.repo.escreve("scripts/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.repo.escreve("bin/forge-y", "#!/usr/bin/env python3\n" + self.HOOK.replace("valor > 10", "valor > 12"))
        self.repo.escreve("bin/forge-z", "#!/usr/bin/env bash\nif [ 1 -gt 11 ]; then :; fi\n")
        self.barra("guarda de scripts/x.py mudada sem mutante declarado", "R-QA")
        self.barra("guarda de bin/forge-y mudada sem mutante declarado", "R-QA")
        self.repo.commit()
        self.assertFalse(any("bin/forge-z" in v for v in self.repo.violacoes()), self.repo.violacoes())

    def test_spec_invalida_barra(self):
        self.repo.escreve("hooks/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.repo.escreve("tests/mutantes/p.json", "{quebrado")
        self.barra("spec de mutantes inválida: tests/mutantes/p.json", "R-QA")
        self.spec([self.mutante() | {"testes": []}])
        self.barra("spec de mutantes inválida: tests/mutantes/p.json")

    def test_hook_ilegivel_barra_sem_derrubar_a_catraca(self):
        self.repo.escreve("hooks/x.py", self.HOOK + "if (:\n")
        self.repo.commit()
        achadas = ControlesEnfraquecidos.sem_traceback(self, self.repo.violacoes)
        self.assertTrue(any("não consegui analisar as guardas de hooks/x.py" in v for v in achadas), achadas)

    def test_forge_mutante_que_nao_carrega_barra(self):
        self.repo.escreve("hooks/x.py", self.HOOK.replace("valor > 10", "valor > 11"))
        self.spec([self.mutante()])
        self.repo.commit()
        with mock.patch.object(catraca, "forge_mutante", side_effect=OSError("sumiu")):
            achadas = self.repo.violacoes()
        self.assertTrue(any("não consegui carregar bin/forge-mutante" in v for v in achadas), achadas)

    def test_muitas_faltas_mostram_as_primeiras_e_a_contagem(self):
        corpo = "".join(f"    if valor > {i}:\n        return {i}\n" for i in range(20, 28))
        self.repo.escreve("hooks/x.py", self.HOOK.replace("    return 'passa'\n", corpo + "    return 'passa'\n"))
        self.repo.commit()
        (achada,) = [v for v in self.repo.violacoes() if v.startswith("R-QA:")]
        self.assertIn("e mais 3", achada)


class Custo(Base):
    def test_github_token_passa(self):
        self.repo.escreve(".github/workflows/ci.yml", "env:\n  T: ${{ secrets.GITHUB_TOKEN }}\n")
        self.passa_exceto_protegido()

    def passa_exceto_protegido(self):
        self.repo.commit()
        self.assertEqual([v for v in self.repo.violacoes() if v.startswith("R-CUSTO")], [])

    def test_segredo_diferente_barra(self):
        self.repo.escreve(".github/workflows/ci.yml", "env:\n  T: ${{ secrets.OUTRO }}\n")
        self.barra("segredo-do-workflow em .github/workflows/ci.yml:2", "R-CUSTO")

    def test_padroes_pagos_barram_em_cada_pasta(self):
        for rel, texto, nome in (("hooks/h.py", "x = 'ANTHROPIC_API_KEY'\n", "chave-de-api"),
                                 ("bin/f", "claude plugin eval .\n", "claude-plugin-eval"),
                                 ("scripts/s.sh", "claude -p 'oi'\n", "claude-print"),
                                 (".github/x.yml", "url: https://api.anthropic.com/v1\n", "url-de-api-paga")):
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, texto)
                repo.commit()
                self.assertTrue(any(v.startswith("R-CUSTO") and nome in v for v in repo.violacoes()))

    def test_lista_de_permissao_libera_so_o_padrao_do_arquivo(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.config(custo_permitido={"bin/f": ["claude-plugin-eval"]})
        self.repo.escreve("bin/f", "claude plugin eval .\n")
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "permite")
        self.repo.git("tag", "-f", "base")
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("reset", "-q", "--hard", "develop")
        self.repo.escreve("bin/g", "claude plugin eval .\n")
        self.barra("bin/g")
        self.assertFalse(any("bin/f" in v for v in self.repo.violacoes()))

    def test_segredo_sem_distincao_de_maiusculas_e_em_expressoes(self):
        """Review 5: GitHub Expressions não diferenciam maiúsculas; tojson(secrets) e secrets[...] também são segredo."""
        for trecho in ("${{ tojson(secrets) }}", "${{ secrets['X'] }}", "${{ SECRETS.FOO }}", "${{ toJSON(Secrets) }}", "secrets: inherit"):
            with self.subTest(trecho):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(".github/workflows/x.yml", f"run: echo {trecho}\n")
                repo.commit()
                self.assertTrue(any(v.startswith("R-CUSTO:") for v in repo.violacoes()), trecho)
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.escreve(".github/pull_request_template.md", "claude PLUGIN eval\nanthropic_api_key\n")
        repo.escreve("scripts/x.sh", "claude PLUGIN eval\n")
        repo.commit()
        self.assertTrue(any("claude-plugin-eval em scripts/x.sh" in v for v in repo.violacoes()))

    def test_claude_code_no_npm_nao_e_custo(self):
        self.repo.escreve("scripts/i.sh", "npm install -g @anthropic-ai/claude-code\n")
        self.passa()


class Protegidos(Base):
    def test_mudanca_em_arquivo_protegido_barra(self):
        for rel in (".github/workflows/ci.yml", ".github/rulesets/main.json", ".github/CODEOWNERS", "tests/catraca.py", "scripts/conferir-release.py"):
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, "mudou\n")
                repo.commit()
                self.assertTrue(any(v.startswith("R-CONFORMIDADE") and f"mudança em {rel}" in v for v in repo.violacoes()))

    def test_mover_ou_apagar_arquivo_protegido_barra(self):
        """QA BUG-01: mover (desligar o CI) ou apagar conta como mudança do caminho antigo."""
        for rel in (".github/workflows/ci.yml", "tests/catraca.py"):
            for como in ("mv", "rm"):
                with self.subTest(rel=rel, como=como):
                    repo = Repo()
                    self.addCleanup(repo.fecha)
                    repo.git(como, rel, *(["desligado.txt"] if como == "mv" else []))
                    repo.commit()
                    self.assertTrue(any(f"mudança em {rel}" in v for v in repo.violacoes()), repo.violacoes())

    def test_detector_de_neutralidade_e_protegido(self):
        """Review termos-hash 1: enfraquecer `normalizar` ou `termos_achados` sem rótulo barra."""
        self.repo.escreve("tests/neutralidade.py", "def normalizar(t):\n    return t\n")
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "detector")
        self.repo.git("tag", "-f", "base")
        self.repo.escreve("tests/neutralidade.py", "def normalizar(t):\n    return t.lower()\n")
        self.barra("mudança em tests/neutralidade.py", "R-CONFORMIDADE")

    def test_githooks_e_dependabot_sao_protegidos(self):
        for rel in (".githooks/pre-push", ".github/dependabot.yml"):
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, "mudou\n")
                repo.commit()
                self.assertTrue(any(f"mudança em {rel}" in v for v in repo.violacoes()))

    def altera_protegido(self, rel, base, depois, modo=None):
        """Repositório novo com `base` em `rel` na base do PR e `depois` no head; devolve as violações de `regra_protegidos`."""
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.git("checkout", "-q", "develop")
        repo.escreve(rel, base)
        repo.git("add", "-A")
        repo.git("commit", "-q", "--allow-empty", "-m", "base com o arquivo")
        repo.git("tag", "-f", "base")
        repo.git("checkout", "-q", "pr")
        repo.git("reset", "-q", "--hard", "develop")
        repo.escreve(rel, depois)
        if modo:
            os.chmod(repo.dir / rel, modo)
        repo.commit()
        return catraca.regra_protegidos(repo.dir, "base", "HEAD")

    CHECAGEM = "def checa(x):\n    if x:\n        return 1\n    return 0\n"

    def test_m9_s1_arvore_igual_passa_sem_rotulo(self):
        casos = {
            "diff só de comentário": self.CHECAGEM + "# nota\n",
            "linha em branco": "\n" + self.CHECAGEM,
            "comentário dentro da função": self.CHECAGEM.replace("    if x:", "    # só 1 ou 0\n    if x:"),
            "espaço e quebra de linha": self.CHECAGEM.replace("return 1", "return  1  "),
        }
        for nome, depois in casos.items():
            with self.subTest(nome):
                self.assertEqual(self.altera_protegido("hooks/_comum.py", self.CHECAGEM, depois), [])

    def test_m9_s1_docstring_conta_como_codigo(self):
        self.assertEqual(len(self.altera_protegido("hooks/_comum.py", self.CHECAGEM, self.CHECAGEM.replace("    if x:", '    """doc"""\n    if x:'))), 1)

    def test_m9_s1_le_os_bytes_e_o_cookie_de_codificacao_muda_a_arvore(self):
        base = "x = 'á'\n"
        self.assertEqual(len(self.altera_protegido("hooks/_comum.py", base, "# coding: latin-1\n" + base)), 1)

    def test_m9_s2_item_novo_em_constante_monotonica_passa_sem_rotulo(self):
        fonte = (AQUI / "catraca.py").read_text(encoding="utf-8")
        self.assertIn("MONOTONICAS = (", fonte)
        casos = {
            "item novo em PROTEGIDOS": fonte.replace('"scripts/conferir-release.py")', '"scripts/conferir-release.py", "hooks/conformidade.json")', 1),
            "item novo em SENSIVEIS": fonte.replace('SENSIVEIS = ("hooks/",', 'SENSIVEIS = ("lib/", "hooks/",', 1),
            "item novo em PASTAS_CUSTO": fonte.replace('PASTAS_CUSTO = ("hooks/",', 'PASTAS_CUSTO = ("docs/provas/", "hooks/",', 1),
            "chave nova em CUSTO": fonte.replace('CUSTO = {\n', 'CUSTO = {\n    "outra-url": r"api\\.exemplo\\.com",\n', 1),
        }
        for nome, depois in casos.items():
            with self.subTest(nome):
                self.assertNotEqual(depois, fonte)
                self.assertEqual(self.altera_protegido("tests/catraca.py", fonte, depois), [])

    def test_m9_s2_so_vale_para_a_lista_da_base_e_sem_reatribuicao_nem_outro_no(self):
        fonte = (AQUI / "catraca.py").read_text(encoding="utf-8")
        item = '"scripts/conferir-release.py")'
        casos = {
            "reatribuição de PROTEGIDOS": fonte + "\nPROTEGIDOS = ()\n",
            "reatribuição que soma": fonte + "\nPARECERES = PARECERES + ('docs/',)\n",
            "item tirado de PROTEGIDOS": fonte.replace('"hooks/parecer.py", ', "", 1),
            "item novo em PARECERES (afrouxa)": fonte.replace('PARECERES = ("docs/reviews/",', 'PARECERES = ("docs/", "docs/reviews/",', 1),
            "item que não é literal": fonte.replace(item, '*PARECERES, ' + item, 1),
            "chave repetida em CUSTO troca o valor": fonte.replace('CUSTO = {\n', 'CUSTO = {\n    "chave-de-api": r"NUNCA",\n', 1),
            "item novo e outro nó mudado": fonte.replace(item, '"x/", ' + item, 1).replace("ROTULO = ", "ROTULO0 = ", 1),
        }
        for nome, depois in casos.items():
            with self.subTest(nome):
                self.assertNotEqual(depois, fonte)
                self.assertEqual(len(self.altera_protegido("tests/catraca.py", fonte, depois)), 1)

    def test_m9_s2_sem_lista_na_base_nao_vale(self):
        base = 'PROTEGIDOS = ("a/",)\n'
        self.assertEqual(len(self.altera_protegido("tests/catraca.py", base, 'PROTEGIDOS = ("a/", "b/")\n')), 1)

    def test_m9_so_python_de_texto_e_classificado(self):
        self.assertEqual(len(self.altera_protegido("hooks/_comum.py", "x = 1\n", "x = 1\n\x00")), 1)

    def test_m9_casos_de_abuso_do_modelo_de_ameacas_pedem_o_rotulo(self):
        """L3-1 a L3-10 e L3-13 (est-030-ameacas-l2-l3.md): cada um é só acréscimo e afrouxa; nenhum passa sem o rótulo."""
        c = self.CHECAGEM
        py = "hooks/_comum.py"
        casos = {
            "L3-1 return novo no começo da checagem": (py, c, c.replace("    if x:", "    return 0\n    if x:")),
            "L3-1 sys.exit novo": (py, c, "import sys\n" + c.replace("    if x:", "    sys.exit(0)\n    if x:")),
            "L3-2 redefinição no fim": (py, c, c + "def checa(*a): return 0\n"),
            "L3-3 reatribuição de constante": ("tests/catraca.py", "PARECERES = ('docs/reviews/',)\n", "PARECERES = ('docs/reviews/',)\nPARECERES = PARECERES + ('docs/',)\n"),
            "L3-5 try/except que engole": (py, c, c.replace("    return 0\n", "    return 0\n\n\ndef g(x):\n    try:\n        return checa(x)\n    except Exception:\n        pass\n")),
            "L3-6 porta dos fundos por condição": (py, c, c.replace("    if x:", "    if os.environ.get('X'):\n        return 0\n    if x:")),
            "L3-7 continue-on-error": (".github/workflows/ci.yml", "jobs:\n  a:\n    steps:\n      - run: x\n", "jobs:\n  a:\n    steps:\n      - run: x\n        continue-on-error: true\n"),
            "L3-7 paths-ignore": (".github/workflows/catraca.yml", "on:\n  pull_request:\n", "on:\n  pull_request:\n    paths-ignore: ['**']\n"),
            "L3-9 CODEOWNERS": (".github/CODEOWNERS", "* @dona\n", "* @dona\n/tests/ @outro\n"),
            "L3-10 exit 0 no pre-push": (".githooks/pre-push", "#!/bin/sh\necho x\n", "#!/bin/sh\nexit 0\necho x\n"),
        }
        for nome, (rel, base, depois) in casos.items():
            with self.subTest(nome):
                self.assertEqual(len(self.altera_protegido(rel, base, depois)), 1)

    def test_m9_l3_4_item_novo_em_linha_nova_de_lista_de_isencao_pede_o_rotulo(self):
        """L3-4: o diff não sabe o sentido de um item novo; fora de `MONOTONICAS` (PARECERES, REESCRITA) ele afrouxa e pede o rótulo."""
        for nome in ("PARECERES", "REESCRITA"):
            with self.subTest(nome):
                base = f'MONOTONICAS = ("PROTEGIDOS",)\n{nome} = (\n    "a/",\n    "b/",\n)\n'
                depois = f'MONOTONICAS = ("PROTEGIDOS",)\n{nome} = (\n    "a/",\n    "b/",\n    "docs/",\n)\n'
                self.assertEqual(len(self.altera_protegido("tests/catraca.py", base, depois)), 1)

    def test_m9_l3_8_arquivo_novo_em_caminho_protegido_pede_o_rotulo(self):
        """L3-8: workflow novo com `pull_request_target` e ruleset novo com `bypass_actors` são acréscimo puro e pedem o rótulo."""
        casos = {
            ".github/workflows/novo.yml": "on:\n  pull_request_target:\njobs:\n  a:\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: ${{ github.event.pull_request.head.sha }}\n",
            ".github/rulesets/novo.json": '{"bypass_actors": [{"actor_id": 1, "actor_type": "Team", "bypass_mode": "always"}]}\n',
        }
        for rel, texto in casos.items():
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, texto)
                repo.commit()
                self.assertEqual(len(catraca.regra_protegidos(repo.dir, "base", "HEAD")), 1)

    def test_m9_l3_13_diff_que_a_contagem_le_errado_conta_como_alteracao(self):
        """L3-13: binário (`-\\t-` no numstat), `.gitattributes` com `-diff`, troca de modo, de link simbólico e de submódulo, sem linha apagada: cada um pede o rótulo."""
        py = "hooks/_comum.py"
        c = self.CHECAGEM
        self.assertEqual(len(self.altera_protegido(py, c, c + "\x00\xff")), 1, "binário")
        self.assertEqual(len(self.altera_protegido("bin/forge-check", "#!/usr/bin/env python3\n" + c, "#!/usr/bin/env python3\n" + c, modo=0o755)), 1, "troca de modo")

        def forma(nome, muda):
            repo = Repo()
            self.addCleanup(repo.fecha)
            repo.git("checkout", "-q", "develop")
            repo.escreve(py, c)
            repo.git("add", "-A")
            repo.git("commit", "-q", "-m", "base com o arquivo")
            repo.git("tag", "-f", "base")
            repo.git("checkout", "-q", "pr")
            repo.git("reset", "-q", "--hard", "develop")
            muda(repo)
            repo.commit()
            self.assertEqual(len(catraca.regra_protegidos(repo.dir, "base", "HEAD")), 1, nome)

        def gitattributes(repo):
            repo.escreve(".gitattributes", f"{py} -diff\n")
            repo.escreve(py, c.replace("return 0", "return 2"))

        def link(repo):
            (repo.dir / py).unlink()
            (repo.dir / py).symlink_to("outro.py")

        def submodulo(repo):
            repo.git("rm", "-q", "--cached", py)
            (repo.dir / py).unlink()
            repo.git("update-index", "--add", "--cacheinfo", "160000", "1" * 40, py)

        forma(".gitattributes -diff", gitattributes)
        forma("link simbólico", link)
        forma("submódulo", submodulo)

    def test_m9_pragma_de_ferramenta_em_comentario_pede_o_rotulo(self):
        """Um pragma desliga uma checagem de ferramenta: não é 'sem efeito' e pede o rótulo, mesmo com a árvore igual."""
        for pragma in ("# noqa", "# nosec", "# type: ignore", "# pylint: disable=all", "# fmt: off", "# pragma: no cover"):
            with self.subTest(pragma):
                self.assertEqual(len(self.altera_protegido("hooks/_comum.py", self.CHECAGEM, self.CHECAGEM.replace("return 1", f"return 1  {pragma}"))), 1)
        self.assertEqual(len(self.altera_protegido("bin/forge-check", "#!/usr/bin/env python3\n" + self.CHECAGEM, "#!/usr/bin/env python3\n" + self.CHECAGEM + "# noqa\n")), 1)
        self.assertEqual(self.altera_protegido("hooks/_comum.py", self.CHECAGEM, self.CHECAGEM + "# nota\n"), [])

    def test_m9_funcao_de_topo_nova_pede_o_rotulo(self):
        self.assertEqual(len(self.altera_protegido("hooks/_comum.py", self.CHECAGEM, self.CHECAGEM + "\n\ndef auxiliar(y):\n    return y + 1\n")), 1)

    def test_m9_script_python_sem_extensao_conta_pelo_shebang(self):
        base = "#!/usr/bin/env python3\n" + self.CHECAGEM
        self.assertEqual(self.altera_protegido("bin/forge-check", base, base + "# nota\n"), [])

    def shebang(self, antes, depois, rel="bin/forge-check"):
        """Classe "linha com efeito que a S1 não compara": a `#!` escolhe o interpretador e as opções; trocá-la pede o rótulo."""
        return len(self.altera_protegido(rel, antes + self.CHECAGEM, depois + self.CHECAGEM))

    def test_m9_shebang_trocado_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env python3\n", "#!/bin/true python3\n"), 1)

    def test_m9_shebang_com_env_s_e_sh_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env python3\n", "#!/usr/bin/env -S sh -c 'exit 0' python3\n"), 1)

    def test_m9_shebang_sem_a_opcao_i_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env -S python3 -I\n", "#!/usr/bin/env -S python3\n"), 1)

    def test_m9_shebang_com_a_opcao_o_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env python3\n", "#!/usr/bin/env -S python3 -O\n"), 1)

    def test_m9_shebang_com_env_s_python3_u_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env python3\n", "#!/usr/bin/env -S python3 -u\n"), 1)

    def test_m9_shebang_com_fim_de_linha_diferente_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env python3\n", "#!/usr/bin/env python3\r\n"), 1)

    def test_m9_shebang_acrescentado_em_py_pede_o_rotulo(self):
        self.assertEqual(self.shebang("", "#!/bin/true python3\n", "hooks/_comum.py"), 1)

    def test_m9_shebang_removido_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/usr/bin/env python3\n", ""), 1)

    def test_m9_arquivo_so_python_de_um_lado_pede_o_rotulo(self):
        self.assertEqual(self.shebang("#!/bin/sh\n", "#!/usr/bin/env python3\n"), 1)
        self.assertEqual(self.shebang("", "#!/usr/bin/env python3\n"), 1)

    def test_m9_shebang_igual_com_comentario_novo_passa_sem_rotulo(self):
        self.assertEqual(len(self.altera_protegido("bin/forge-check", "#!/usr/bin/env -S python3 -I\n" + self.CHECAGEM, "#!/usr/bin/env -S python3 -I\n# nota\n" + self.CHECAGEM)), 0)

    def test_m9_s2_so_vale_em_tests_catraca_py_mesmo_que_outro_py_declare_a_lista(self):
        base = 'MONOTONICAS = ("PROTEGIDOS",)\nPROTEGIDOS = ("a/",)\n'
        self.assertEqual(len(self.altera_protegido("hooks/_comum.py", base, base.replace('("a/",)', '("a/", "b/")'))), 1)

    def test_m9_s2_renomear_constante_monotonica_pede_o_rotulo(self):
        fonte = (AQUI / "catraca.py").read_text(encoding="utf-8")
        depois = fonte.replace('PASTAS_CUSTO = ("hooks/",', 'PASTAS_RENOMEADA = ("docs/provas/", "hooks/",', 1)
        self.assertNotEqual(depois, fonte)
        self.assertEqual(len(self.altera_protegido("tests/catraca.py", fonte, depois)), 1)

    def test_m9_remocao_alteracao_e_o_que_nao_sabe_classificar_seguem_pedindo_o_rotulo(self):
        casos = {
            "linha alterada": (self.CHECAGEM, self.CHECAGEM.replace("return 0", "return 2")),
            "linha removida": (self.CHECAGEM, self.CHECAGEM.replace("    return 0\n", "")),
            "acréscimo que muda o programa": (self.CHECAGEM, self.CHECAGEM + "checa = lambda x: 0\n"),
            "pragma que desliga a checagem": (self.CHECAGEM, self.CHECAGEM + "x = 1  # noqa\n"),
            "Python que não compila": (self.CHECAGEM, self.CHECAGEM + "def (\n"),
        }
        for nome, (base, depois) in casos.items():
            with self.subTest(nome):
                self.assertEqual(len(self.altera_protegido("hooks/_comum.py", base, depois)), 1)

    def test_m9_acrescimo_em_outra_linguagem_ou_arquivo_novo_continua_pedindo_o_rotulo(self):
        """Só Python é classificado; workflow, shell e JSON de política seguem pedindo o rótulo mesmo só acrescentando linhas."""
        for rel, base in ((".github/workflows/ci.yml", "name: CI\n"), (".githooks/pre-push", "#!/bin/sh\nexit 0\n"), (".github/CODEOWNERS", "* @dona\n")):
            with self.subTest(rel):
                self.assertEqual(len(self.altera_protegido(rel, base, base + "# nota\n")), 1)
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.escreve("scripts/conferir-release.py", "# novo\n")
        repo.commit()
        self.assertEqual(len(catraca.regra_protegidos(repo.dir, "base", "HEAD")), 1)

    def test_m9_acrescimo_que_afrouxa_pendente_do_modelo_de_ameacas_continua_pedindo_o_rotulo(self):
        """PENDENTE (modelo de ameaças do L3): um `return` novo no começo de uma função de checagem é só acréscimo de linha,
        mas desliga a checagem. A regra não o separa de um acréscimo inocente pelo diff; ela o barra por mudar o AST, e a
        decisão de uma regra mais fina é do dono. Este teste fixa o comportamento seguro: pede o rótulo."""
        depois = self.CHECAGEM.replace("    if x:", "    return 0\n    if x:")
        self.assertEqual(len(self.altera_protegido("hooks/_comum.py", self.CHECAGEM, depois)), 1)

    def test_m9_modo_do_arquivo_mudado_continua_pedindo_o_rotulo(self):
        base = "#!/usr/bin/env python3\n" + self.CHECAGEM
        self.assertEqual(len(self.altera_protegido("bin/forge-check", base, base + "# nota\n", modo=0o755)), 1)

    def test_m9_forma_compilada_continua_pedindo_o_rotulo_mesmo_so_acrescentando(self):
        """`regra_compilados` não usa a classificação: bytecode e extensão nativa não têm 'linha acrescentada'."""
        self.repo.escreve("pacote/x.so", "# so texto\n")
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "x.so")
        self.repo.git("tag", "-f", "base")
        self.repo.escreve("pacote/x.so", "# so texto\n# mais\n")
        self.repo.commit()
        self.assertEqual(len(catraca.regra_compilados(self.repo.dir, "base", "HEAD")), 1)

    def test_regra_de_release_e_protegida(self):
        self.repo.escreve("scripts/conferir-release.py", "mudou\n")
        self.barra("mudança em scripts/conferir-release.py", "R-CONFORMIDADE")

    def test_git_diff_com_erro_vira_violacao(self):
        """Falha fechada: base inexistente faz o `git diff` falhar, e a lista vazia não pode virar 'nada mudou'."""
        achadas = catraca.violacoes_das_regras(self.repo.dir, "ref-que-nao-existe", "HEAD")
        self.assertEqual(len(achadas), 1, achadas)
        self.assertRegex(achadas[0], r"^R-CONFORMIDADE: não consegui listar os arquivos alterados entre ref-que-nao-existe e HEAD .+\. Por quê: .+\. Corrigir: .+ \(.+\)$")

    def test_base_inexistente_deixa_a_catraca_vermelha_mesmo_com_rotulo(self):
        eventos = self.repo.dir / "eventos.json"
        eventos.write_text(json.dumps([{"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": "dona"}, "created_at": "2026-01-02T10:00:00Z"}]), encoding="utf-8")
        argv = ["--raiz", str(self.repo.dir), "--base", "ref-que-nao-existe", "--eventos", str(eventos), "--ultimo-push", "2026-01-01T10:00:00Z"]
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(argv)
        self.assertEqual(rc, 1)
        self.assertIn("não consegui listar os arquivos alterados", saida.getvalue())

    def test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera(self):
        """Decisão técnica do pedido: com a base legível (dono definido) e o rótulo do dono depois do push, o erro do
        `git diff` continua vermelho; só a guarda `SEM_LISTA in x` da catraca impede o rótulo de liberar."""
        eventos = self.repo.dir / "eventos.json"
        eventos.write_text(json.dumps([{"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": "dona"}, "created_at": "2026-01-02T10:00:00Z"}]), encoding="utf-8")
        argv = ["--raiz", str(self.repo.dir), "--base", "base", "--eventos", str(eventos), "--ultimo-push", "2026-01-02T09:00:00Z"]

        def diff_que_falha(raiz, base, head):
            raise catraca.ErroDeDiff(catraca.msg_diff(base, head))
        with mock.patch.object(catraca, "alterados", diff_que_falha), contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(argv)
        self.assertEqual(rc, 1, saida.getvalue())
        self.assertIn("não consegui listar os arquivos alterados", saida.getvalue())
        self.assertNotIn("liberada", saida.getvalue())

    def test_alterados_levanta_quando_o_git_diff_falha(self):
        with self.assertRaises(catraca.ErroDeDiff):
            catraca.alterados(self.repo.dir, "ref-que-nao-existe", "HEAD")

    def test_outros_arquivos_passam(self):
        self.repo.escreve(".github/pull_request_template.md", "x\n")
        self.passa()

    def test_introducao_da_catraca_e_ignorada(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.git("rm", "-q", "tests/catraca.py")
        self.repo.git("commit", "-q", "-m", "sem catraca")
        self.repo.git("tag", "-f", "base")
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("reset", "-q", "--hard", "develop")
        self.repo.escreve("tests/catraca.py", "x = 'nova'\n")
        self.repo.escreve(".github/workflows/ci.yml", "name: CI com catraca\n")
        self.passa()


class CorpusDosAfrouxamentosReais(unittest.TestCase):
    """E2 do EST-030-L3: os 11 PRs rotulados `afrouxa-regra` que a linha de base (`forge-check afrouxamentos`) mediu como afrouxamento real
    seguem pedindo o rótulo depois da M9. Cada fixture em `tests/fixtures/afrouxamentos/` guarda, do diff real do PR, só os arquivos
    (texto antes e depois) que fazem a catraca achar o afrouxamento; sem rede."""
    PRS = (109, 125, 161, 195, 200, 204, 209, 218, 236, 253, 281)

    def monta(self, arquivos):
        repo = Repo()
        self.addCleanup(repo.fecha)
        repo.git("checkout", "-q", "--orphan", "corpus")
        repo.git("rm", "-rfq", "--ignore-unmatch", ".")
        for lado in ("base", "head"):
            for rel, textos in arquivos.items():
                caminho = repo.dir / rel
                if textos[lado] is None:
                    caminho.unlink(missing_ok=True)
                else:
                    repo.escreve(rel, textos[lado])
            repo.git("add", "-A")
            repo.git("commit", "-q", "--allow-empty", "-m", lado)
            repo.git("tag", "-f", "corpus-" + lado)
        return repo.dir

    def test_cada_afrouxamento_real_segue_pedindo_o_rotulo(self):
        pasta = AQUI / "fixtures" / "afrouxamentos"
        self.assertEqual(sorted(int(f.stem) for f in pasta.glob("*.json")), list(self.PRS))
        for n in self.PRS:
            with self.subTest(pr=n):
                fixture = json.loads((pasta / f"{n}.json").read_text(encoding="utf-8"))
                self.assertEqual(fixture["pr"], n)
                achadas = catraca.violacoes_das_regras(self.monta(fixture["arquivos"]), "corpus-base", "corpus-head")
                de_conteudo = [v for v in achadas if catraca.arquivo_da_violacao(v) is None]
                self.assertTrue(de_conteudo, achadas)
                self.assertTrue(all(v.startswith("R-CONFORMIDADE:") for v in de_conteudo), de_conteudo)


class FalhaFechadaDoGit(Base):
    """Item 1 do N-CAT1: erro do git nunca vale como "ausente" nem como lista vazia, em qualquer ordem das regras."""

    def git_que_falha(self, quando, erro=None):
        """Substituto de `catraca.git`: com `quando(args)` verdadeiro, falha (rc 128 ou a exceção `erro`); senão, o git de verdade."""
        real = catraca.git

        def falso(raiz, *args):
            if quando(args):
                if erro:
                    raise erro
                return 128, ""
            return real(raiz, *args)
        return falso

    def argv(self, *extra, eventos=True):
        a = ["--raiz", str(self.repo.dir), "--base", "base", *extra]
        if eventos:
            arq = self.repo.dir.parent / (self.repo.dir.name + "-falha-git-eventos.json")
            if not arq.exists():
                arq.write_text(json.dumps([{"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": "dona"},
                                            "created_at": "2026-01-02T10:00:00Z"}]), encoding="utf-8")
                self.addCleanup(arq.unlink)
            a += ["--eventos", str(arq), "--ultimo-push", "2026-01-02T09:00:00Z"]
        return a

    def roda(self, argv, git_falho):
        with mock.patch.object(catraca, "git", git_falho), contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(argv)
        return rc, saida.getvalue()

    def ls_tree_do_head(self, args):
        return "ls-tree" in args and "HEAD" in args

    def ls_tree_da_catraca_na_base(self, args):
        return "ls-tree" in args and "tests/catraca.py" in args

    def test_listar_levanta_quando_o_ls_tree_falha(self):
        with mock.patch.object(catraca, "git", self.git_que_falha(lambda a: "ls-tree" in a)):
            with self.assertRaises(catraca.ErroDeGit):
                catraca.listar(self.repo.dir, "HEAD", "tests")

    def test_ls_tree_do_head_que_falha_nao_esconde_o_custo(self):
        self.repo.escreve("scripts/x.sh", "claude -p oi\n")
        self.repo.commit()
        with mock.patch.object(catraca, "git", self.git_que_falha(self.ls_tree_do_head)):
            with self.assertRaises(catraca.ErroDeGit):
                catraca.regra_custo(self.repo.dir, "HEAD", {})
            achadas = self.repo.violacoes()
        self.assertTrue(any(catraca.NAO_LIBERAVEL in v and v.startswith("R-CONFORMIDADE:") for v in achadas), achadas)

    def test_ls_tree_da_base_que_falha_nao_zera_a_contagem_de_testes(self):
        self.repo.git("rm", "-q", "tests/test_x.py")
        self.repo.commit()
        base = self.repo.git("rev-parse", "base").strip()
        falho = self.git_que_falha(lambda a: "ls-tree" in a and base in a)
        with mock.patch.object(catraca, "git", falho):
            with self.assertRaises(catraca.ErroDeGit):
                catraca.contar_testes(self.repo.dir, base)
            with self.assertRaises(catraca.ErroDeGit):
                catraca.forca_dos_testes(self.repo.dir, base)

    def test_regra_protegidos_sozinha_falha_fechada(self):
        """Sem depender de `regra_arquivos_de_regras` rodar antes: base inexistente e erro do `ls-tree` da base levantam."""
        self.repo.escreve("hooks/_comum.py", "mudou\n")
        self.repo.commit()
        with self.assertRaises(catraca.ErroDeGit):
            catraca.regra_protegidos(self.repo.dir, "ref-que-nao-existe", "HEAD")
        with mock.patch.object(catraca, "git", self.git_que_falha(self.ls_tree_da_catraca_na_base)):
            with self.assertRaises(catraca.ErroDeGit):
                catraca.regra_protegidos(self.repo.dir, "base", "HEAD")

    def test_introducao_real_da_catraca_continua_sem_violacao(self):
        self.repo.git("rm", "-q", "tests/catraca.py")
        self.repo.git("commit", "-q", "-m", "sem catraca")
        self.repo.git("tag", "-f", "base")
        self.repo.escreve("tests/catraca.py", "x = 'nova'\n")
        self.repo.commit()
        self.assertEqual(catraca.regra_protegidos(self.repo.dir, "base", "HEAD"), [])

    def test_rotulo_do_dono_nao_libera_o_ls_tree_que_falha(self):
        """Cada leitura do git que falha deixa a catraca vermelha mesmo com o rótulo do dono depois do push."""
        self.repo.escreve("tests/catraca.py", "x = 'mudou'\n")
        self.repo.commit()
        for nome, quando in (("ls-tree do head", self.ls_tree_do_head), ("ls-tree da catraca na base", self.ls_tree_da_catraca_na_base)):
            with self.subTest(nome):
                rc, saida = self.roda(self.argv(), self.git_que_falha(quando))
                self.assertEqual(rc, 1, saida)
                self.assertIn(catraca.NAO_LIBERAVEL, saida)
                self.assertNotIn("liberada", saida)

    def test_estouro_de_prazo_do_git_vira_uma_linha_e_rc_1(self):
        self.repo.escreve("scripts/x.sh", "echo\n")
        self.repo.commit()
        estouro = subprocess.TimeoutExpired(["git"], 60)
        casos = (("regras", self.argv(eventos=False)),
                 ("pareceres", ["--modo", "pareceres", "--raiz", str(self.repo.dir), "--base", "base", "--ramo", "pr", "--base-ref", "develop"]))
        for modo, argv in casos:
            with self.subTest(modo):
                rc, saida = self.roda(argv, self.git_que_falha(lambda a: a[0] == "diff", estouro))
                self.assertEqual(rc, 1, saida)
                linhas = [l for l in saida.splitlines() if l.strip()]
                self.assertEqual(len(linhas), 1, saida)
                self.assertRegex(linhas[0], r"^R-CONFORMIDADE: .+\. Por quê: .+\. Corrigir: .+ \(.+\)$")
                self.assertIn("TimeoutExpired", linhas[0])

    def test_rotulo_do_dono_nao_libera_o_estouro_de_prazo(self):
        self.repo.escreve("tests/catraca.py", "x = 'mudou'\n")
        self.repo.commit()
        rc, saida = self.roda(self.argv(), self.git_que_falha(lambda a: a[0] == "diff", subprocess.TimeoutExpired(["git"], 60)))
        self.assertEqual(rc, 1, saida)
        self.assertNotIn("liberada", saida)


class Rotulo(unittest.TestCase):
    def evento(self, quem, quando, tipo="labeled", rotulo=catraca.ROTULO):
        return {"event": tipo, "label": {"name": rotulo}, "actor": {"login": quem}, "created_at": quando}

    def test_dono_depois_do_push_libera(self):
        self.assertTrue(catraca.rotulo_liberado([self.evento("dona", "2026-01-02T10:00:00Z")], "dona", "2026-01-02T09:00:00Z"))

    def test_dono_antes_do_push_nao_libera(self):
        self.assertFalse(catraca.rotulo_liberado([self.evento("dona", "2026-01-02T08:00:00Z")], "dona", "2026-01-02T09:00:00Z"))

    def test_outra_pessoa_nao_libera(self):
        self.assertFalse(catraca.rotulo_liberado([self.evento("intrusa", "2026-01-02T10:00:00Z")], "dona", "2026-01-02T09:00:00Z"))

    def test_rotulo_removido_depois_nao_libera(self):
        eventos = [self.evento("dona", "2026-01-02T10:00:00Z"), self.evento("dona", "2026-01-02T11:00:00Z", "unlabeled")]
        self.assertFalse(catraca.rotulo_liberado(eventos, "dona", "2026-01-02T09:00:00Z"))

    def test_outro_rotulo_e_sem_eventos_nao_liberam(self):
        self.assertFalse(catraca.rotulo_liberado([self.evento("dona", "2026-01-02T10:00:00Z", rotulo="bug")], "dona", "2026-01-02T09:00:00Z"))
        self.assertFalse(catraca.rotulo_liberado([], "dona", "2026-01-02T09:00:00Z"))

    def test_sem_token_trata_como_sem_rotulo(self):
        antigo = {k: os.environ.pop(k, None) for k in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER", "HEAD_SHA")}
        try:
            self.assertEqual(catraca.eventos_do_github(), (None, None))
        finally:
            os.environ.update({k: v for k, v in antigo.items() if v is not None})


class InstanteDoServidor(unittest.TestCase):
    """Review 1: o "último push" vem do servidor (execuções do head), nunca da data do commit."""

    def setUp(self):
        self.antigo = dict(os.environ)
        os.environ.update({"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PR_NUMBER": "7", "HEAD_SHA": "abc"})
        self.original = catraca.api
        self.addCleanup(lambda: setattr(catraca, "api", self.original))
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(self.antigo)))

    def api_falsa(self, execucoes):
        eventos = [{"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": "dona"}, "created_at": "2026-01-02T10:00:00Z"}]

        def falsa(caminho, token, chave=None):
            if "/actions/runs" in caminho:
                self.assertEqual(chave, "workflow_runs")
                self.assertIn("head_sha=abc", caminho)
                return execucoes
            if "/commits" in caminho:  # a data do commit não pode ser consultada
                return [{"commit": {"committer": {"date": "2026-01-02T08:00:00Z"}}}]
            return eventos
        catraca.api = falsa

    def test_usa_a_execucao_mais_antiga_do_head(self):
        self.api_falsa([{"head_sha": "abc", "created_at": "2026-01-02T11:00:00Z"}, {"head_sha": "abc", "created_at": "2026-01-02T09:30:00Z"}])
        eventos, push = catraca.eventos_do_github()
        self.assertEqual(push, "2026-01-02T09:30:00Z")
        self.assertTrue(catraca.rotulo_liberado(eventos, "dona", push))

    def test_commit_com_data_antiga_mas_push_depois_do_rotulo_nao_libera(self):
        self.api_falsa([{"head_sha": "abc", "created_at": "2026-01-02T10:30:00Z"}])
        eventos, push = catraca.eventos_do_github()
        self.assertEqual(push, "2026-01-02T10:30:00Z")
        self.assertFalse(catraca.rotulo_liberado(eventos, "dona", push))

    def test_sem_execucao_do_head_ou_sem_head_sha_trata_como_sem_rotulo(self):
        self.api_falsa([])
        self.assertEqual(catraca.eventos_do_github()[1], None)
        self.api_falsa([{"head_sha": "outro", "created_at": "2026-01-02T09:00:00Z"}])
        self.assertEqual(catraca.eventos_do_github()[1], None)
        del os.environ["HEAD_SHA"]
        self.assertEqual(catraca.eventos_do_github(), (None, None))

    def test_falha_da_api_trata_como_sem_rotulo(self):
        def falha(*a, **k):
            raise OSError("sem rede")
        catraca.api = falha
        self.assertEqual(catraca.eventos_do_github(), (None, None))


class PoliticaDeConformidade(Base):
    """hooks/conformidade.json: lista branca: só acrescentar entrada válida em `caminhos` passa; todo o resto acusa R-CONFORMIDADE."""

    POLITICA = {
        "papeis": {"tech-lead": ["forge:tech-lead"], "doc": ["forge:software-architect"]},
        "sem_agent_type": "jarvis",
        "papel_padrao": "dev",
        "acoes": {"merge_integracao": ["tech-lead"], "instalar_pacote": ["dev"]},
        "caminhos": [
            {"caminho": ".claude/", "quem": [], "motivo": "x"},
            {"caminho": "docs/regras/", "quem": ["tech-lead"], "so_forge": True, "branch": "melhoria/", "motivo": "y"},
        ],
        "pacotes": {"npm": {"adicionam": ["install", "add"], "congelados": ["ci"]}},
    }

    def setUp(self):
        super().setUp()
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve("hooks/conformidade.json", json.dumps(self.POLITICA))
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "politica")
        self.repo.git("tag", "-f", "base")
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("reset", "-q", "--hard", "develop")

    def muda(self, f):
        pol = copy.deepcopy(self.POLITICA)
        f(pol)
        self.repo.escreve("hooks/conformidade.json", json.dumps(pol))
        self.repo.commit()
        return [v for v in self.repo.violacoes() if "conformidade.json" in v]

    def test_sem_mudanca_nao_acusa(self):
        self.assertEqual(self.muda(lambda p: None), [])

    def test_remover_entrada_de_caminhos_acusa(self):
        v = self.muda(lambda p: p["caminhos"].pop(0))
        self.assertEqual(len(v), 1)
        self.assertIn("R-CONFORMIDADE:", v[0])
        self.assertIn(".claude/", v[0])

    def test_ampliar_quem_acusa(self):
        v = self.muda(lambda p: p["caminhos"][1]["quem"].append("doc"))
        self.assertEqual(len(v), 1)
        self.assertIn("doc", v[0])

    def test_quem_de_vazio_para_lista_acusa(self):
        self.assertEqual(len(self.muda(lambda p: p["caminhos"][0].update(quem=["jarvis"]))), 1)

    def test_remover_branch_acusa(self):
        v = self.muda(lambda p: p["caminhos"][1].pop("branch"))
        self.assertEqual(len(v), 1)
        self.assertIn("docs/regras/", v[0])

    def test_alterar_branch_ou_remover_so_forge_acusa(self):
        self.assertEqual(len(self.muda(lambda p: p["caminhos"][1].update(branch="feature/"))), 1)
        self.assertEqual(len(self.muda(lambda p: p["caminhos"][1].pop("so_forge"))), 1)

    def test_acao_ganha_papel_ou_some_acusa(self):
        self.assertEqual(len(self.muda(lambda p: p["acoes"]["merge_integracao"].append("dev"))), 1)
        self.assertEqual(len(self.muda(lambda p: p["acoes"].pop("merge_integracao"))), 1)

    def test_papel_ganha_agent_type_ou_padrao_muda_acusa(self):
        self.assertEqual(len(self.muda(lambda p: p["papeis"]["tech-lead"].append("forge:dev"))), 1)
        self.assertEqual(len(self.muda(lambda p: p.update(papel_padrao="tech-lead"))), 1)

    def test_bloqueio_de_pacote_removido_acusa(self):
        self.assertEqual(len(self.muda(lambda p: p["pacotes"]["npm"]["adicionam"].remove("add"))), 1)

    def acusa(self, f, trecho=None):
        v = self.muda(f)
        self.assertEqual(len(v), 1, v)
        self.assertIn("R-CONFORMIDADE:", v[0])
        if trecho:
            self.assertIn(trecho, v[0])

    def nova(self, **campos):
        return lambda p: p["caminhos"].append({"caminho": "novo/", "quem": ["tech-lead"], "motivo": "z", **campos})

    def test_acrescentar_entrada_legitima_nao_acusa(self):
        self.assertEqual(self.muda(lambda p: p["caminhos"].append({"caminho": "novo/", "quem": [], "motivo": "z"})), [])
        self.assertEqual(self.muda(self.nova(so_forge=True, branch="melhoria/")), [])

    def test_entrada_nova_com_dev_ou_papel_inexistente_acusa(self):
        self.acusa(self.nova(quem=["dev"]), "dev")
        self.acusa(self.nova(quem=["fantasma"]), "fantasma")
        self.acusa(lambda p: p["caminhos"].append({"caminho": "novo/", "motivo": "z"}), "quem")

    def test_entrada_nova_sem_motivo_ou_com_campo_fora_do_esquema_acusa(self):
        self.acusa(lambda p: p["caminhos"].insert(0, {"caminho": "novo/", "quem": []}), "motivo")
        self.acusa(self.nova(motivo=""), "motivo")
        self.acusa(self.nova(motivo=3), "motivo")
        self.acusa(self.nova(branch=7), "branch")
        self.acusa(self.nova(branch=""), "branch")
        self.acusa(self.nova(so_forge="sim"), "so_forge")
        self.acusa(self.nova(extra=1), "extra")

    def test_entrada_nova_com_caminho_igual_ou_prefixo_de_existente_acusa(self):
        self.acusa(lambda p: p["caminhos"].append({"caminho": "docs/regras/", "quem": [], "motivo": "z"}), "docs/regras/")
        self.acusa(lambda p: p["caminhos"].append({"caminho": "docs/", "quem": [], "motivo": "z"}), "docs/")
        self.assertEqual(self.muda(lambda p: p["caminhos"].append({"caminho": "docs/regras/x", "quem": [], "motivo": "z"})), [])

    def test_entrada_nova_junto_de_outra_mudanca_acusa(self):
        def f(p):
            p["caminhos"].append({"caminho": "novo/", "quem": [], "motivo": "z"})
            p["acoes"]["merge_integracao"] = []
        self.acusa(f)

    def test_so_forge_acrescentado_acusa(self):
        self.acusa(lambda p: p["caminhos"][0].update(so_forge=True), ".claude/")

    def test_restringir_tambem_acusa(self):
        """Lista branca: só acrescentar entrada passa; apertar `quem` ou `acoes` também pede o rótulo."""
        self.acusa(lambda p: p["caminhos"][1].update(quem=[]))
        self.acusa(lambda p: p["acoes"].update(merge_integracao=[]))

    def test_listas_de_instalacao_congelada_ampliadas_acusam(self):
        self.acusa(lambda p: p.update(flags_congeladas=["--save"]), "flags_congeladas")
        self.acusa(lambda p: p["pacotes"]["npm"]["congelados"].append("install"), "pacotes")
        self.acusa(lambda p: p["pacotes"]["npm"].update(flags_congeladas=["--save"]), "pacotes")
        self.acusa(lambda p: p["pacotes"]["npm"].update(so_arquivo=["-r"]), "pacotes")

    def test_mudar_papeis_acusa(self):
        self.acusa(lambda p: p["papeis"]["tech-lead"].clear())
        self.acusa(lambda p: p["papeis"].pop("tech-lead"))
        self.acusa(lambda p: p["papeis"].update(dev=["forge:qa-engineer"]))
        self.acusa(lambda p: p.update(sem_agent_type="dev"))

    def test_quebra_de_esquema_acusa(self):
        self.acusa(lambda p: p.update(papeis_x=p.pop("papeis")))
        self.acusa(lambda p: p["caminhos"][0].pop("quem"))
        self.acusa(lambda p: p.pop("pacotes"))
        self.acusa(lambda p: p.update(caminhos={}))

    def test_json_invalido_ou_nao_objeto_acusa(self):
        for texto in ("{invalido", "[]", "null"):
            with self.subTest(texto):
                self.repo.git("reset", "-q", "--hard", "base")
                self.repo.escreve("hooks/conformidade.json", texto)
                self.repo.commit()
                v = [x for x in self.repo.violacoes() if "conformidade.json" in x]
                self.assertEqual(len(v), 1, v)

    def test_arquivo_removido_ou_movido_acusa(self):
        self.repo.git("mv", "hooks/conformidade.json", "hooks/outra.json")
        self.repo.commit()
        self.assertTrue([x for x in self.repo.violacoes() if "conformidade.json" in x])

    def test_hook_conformidade_e_protegido(self):
        self.assertIn("hooks/conformidade.py", catraca.PROTEGIDOS)
        self.repo.escreve("hooks/conformidade.py", "x = 1\n")
        self.repo.commit()
        self.assertTrue(any("mudança em hooks/conformidade.py" in v for v in self.repo.violacoes()))

    def test_hooks_e_validador_que_decidem_o_bloqueio_sao_protegidos(self):
        """Review #57: `parecer.py` (e_clone_do_forge), `_comum.py` (falhar_fechado, executar) e o `forge-check`
        (validade do parecer que o hook `parecer` e o modo `pareceres` consultam) decidem o bloqueio."""
        for rel in ("hooks/parecer.py", "hooks/_comum.py", "bin/forge-check"):
            with self.subTest(rel):
                self.assertIn(rel, catraca.PROTEGIDOS)
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, "x = 1\n")
                repo.commit()
                self.assertTrue(any(f"mudança em {rel}" in v for v in repo.violacoes()), repo.violacoes())

    def test_politica_ausente_na_base_nao_acusa(self):
        self.repo.git("rm", "-q", "hooks/conformidade.json")
        self.repo.git("commit", "-q", "-m", "tira")
        self.repo.git("tag", "-f", "base", "HEAD")
        self.repo.escreve("hooks/conformidade.json", json.dumps(self.POLITICA))
        self.repo.commit()
        self.assertEqual([v for v in self.repo.violacoes() if "conformidade.json" in v], [])

    def roda(self, eventos):
        pol = copy.deepcopy(self.POLITICA)
        pol["caminhos"].pop(0)
        self.repo.escreve("hooks/conformidade.json", json.dumps(pol))
        self.repo.commit()
        arq = self.repo.dir.parent / (self.repo.dir.name + "-eventos.json")
        arq.write_text(json.dumps(eventos), encoding="utf-8")
        self.addCleanup(arq.unlink, missing_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY")}
        return subprocess.run(["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "base", "--eventos", str(arq),
                               "--ultimo-push", "2026-01-02T09:00:00Z"], capture_output=True, text=True, env=env)

    def evento(self, quem):
        return {"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": quem}, "created_at": "2026-01-02T10:00:00Z"}

    def test_sem_rotulo_sai_1_e_rotulo_do_dono_libera(self):
        self.assertEqual(self.roda([]).returncode, 1)
        self.assertEqual(self.roda([self.evento("dona")]).returncode, 0)


class LinhaDeComando(Base):
    """A saída e o código de saída do script, com e sem o rótulo."""

    def roda(self, eventos=None, push="2026-01-02T09:00:00Z"):
        self.repo.config(dono="outra")
        self.repo.commit()
        args = ["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "base"]
        if eventos is not None:
            arq = self.repo.dir.parent / (self.repo.dir.name + "-eventos.json")
            arq.write_text(json.dumps(eventos), encoding="utf-8")
            self.addCleanup(arq.unlink)
            args += ["--eventos", str(arq), "--ultimo-push", push]
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY")}
        return subprocess.run(args, capture_output=True, text=True, env=env)

    def evento(self, quem):
        return {"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": quem}, "created_at": "2026-01-02T10:00:00Z"}

    def test_sem_rotulo_sai_1(self):
        r = self.roda()
        self.assertEqual(r.returncode, 1)
        self.assertIn("R-CONTRIB:", r.stdout)

    def test_rotulo_do_dono_da_base_depois_do_push_sai_0(self):
        self.assertEqual(self.roda([self.evento("dona")]).returncode, 0)

    def test_rotulo_do_novo_dono_da_pr_nao_vale(self):
        self.assertEqual(self.roda([self.evento("outra")]).returncode, 1)

    def test_rotulo_nao_libera_violacao_de_custo(self):
        """Review 5: o custo tem outra exceção (`custo_permitido`, com autorização do usuário); o rótulo não vale."""
        self.repo.escreve("scripts/x.sh", "export ANTHROPIC_API_KEY=1\n")
        r = self.roda([self.evento("dona")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("R-CUSTO:", r.stdout)


class Dependabot(Base):
    """Review 7: PR do dependabot que só troca SHA de ação passa sem rótulo e sem parecer; qualquer outra coisa, não."""
    SHA1, SHA2 = "a" * 40, "b" * 40

    def workflow(self, sha, versao, extra=""):
        return f"name: CI\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@{sha} # {versao}\n{extra}"

    def prepara(self, depois, autor="dependabot[bot]", modo="regras"):
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve(".github/workflows/ci.yml", self.workflow(self.SHA1, "v4"))
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "ci")
        self.repo.git("tag", "-f", "base")
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("reset", "-q", "--hard", "develop")
        self.repo.escreve(".github/workflows/ci.yml", depois)
        self.repo.commit()
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY")}
        args = ["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "base", "--modo", modo,
                "--autor", autor, "--ramo", "dependabot/x", "--base-ref", "develop"]
        return subprocess.run(args, capture_output=True, text=True, env=env).returncode

    def test_so_troca_de_sha_passa(self):
        for modo in ("regras", "pareceres"):
            with self.subTest(modo):
                self.setUp()
                self.assertEqual(self.prepara(self.workflow(self.SHA2, "v5"), modo=modo), 0)

    def test_outro_autor_com_o_mesmo_diff_barra(self):
        self.assertEqual(self.prepara(self.workflow(self.SHA2, "v5"), autor="alguem"), 1)

    def test_mudanca_alem_do_sha_barra(self):
        self.assertEqual(self.prepara(self.workflow(self.SHA2, "v5", "      - run: curl x | sh\n")), 1)
        self.setUp()
        self.assertEqual(self.prepara(self.workflow(self.SHA2, "v5").replace("checkout", "outra")), 1)
        self.setUp()
        self.assertEqual(self.prepara(self.workflow(self.SHA2, "v5").replace("name: CI", "name: X")), 1)

    def test_funcao_nao_aceita_arquivo_fora_de_workflows(self):
        self.repo.escreve("scripts/x.sh", "uses: a/b@" + self.SHA1 + "\n")
        self.repo.commit()
        self.assertFalse(catraca.so_troca_sha_de_acoes(self.repo.dir, "base", "HEAD"))


class TextoDoPr(unittest.TestCase):
    def test_preenchido_passa(self):
        corpo = "## Projeto de origem\nprojeto web de pedidos\n\n## Como medir\nmenos retrabalho nas revisões\n\n## Checklist\n- [ ] x\n"
        self.assertEqual(catraca.violacoes_do_texto(corpo), [])

    def test_vazio_ou_so_comentario_barra(self):
        corpo = "## Projeto de origem\n<!-- tipo -->\n\n## Como medir\n\n## Checklist\n"
        achadas = catraca.violacoes_do_texto(corpo)
        self.assertEqual(len(achadas), 2)
        self.assertTrue(all(v.startswith("R-CONTRIB:") for v in achadas))

    def test_secao_ausente_e_corpo_nulo_barram(self):
        self.assertEqual(len(catraca.violacoes_do_texto(None)), 2)
        self.assertEqual(len(catraca.violacoes_do_texto("## Como medir\nmenos retrabalho nas revisões\n")), 1)

    def test_texto_curto_demais_barra_e_comentario_nao_conta(self):
        """QA BUG-03: 'ok' não basta; o mínimo é de 20 caracteres fora de comentários HTML."""
        for texto in ("ok", "x" * 19, "<!-- " + "x" * 40 + " -->curto"):
            with self.subTest(texto=texto[:12]):
                corpo = f"## Projeto de origem\nprojeto web de pedidos\n\n## Como medir\n{texto}\n"
                self.assertEqual(len(catraca.violacoes_do_texto(corpo)), 1)
        corpo = "## Projeto de origem\n" + "x" * 20 + "\n\n## Como medir\n" + "y" * 20 + "\n"
        self.assertEqual(catraca.violacoes_do_texto(corpo), [])


class Pareceres(Base):
    def parecer(self, tipo, ramo="pr", parecer="aprovado", pedido="ped", commit=None):
        self.repo.commit()
        commit = commit or self.repo.git("rev-parse", "--short", "HEAD").strip()
        pasta = {"review": "reviews", "revisao-seguranca": "security"}.get(tipo, "qa")
        extra = "qa: forge:qa-engineer" if tipo == "qa" else "revisor: forge:tech-lead"
        self.repo.escreve(f"docs/{pasta}/{pedido}.md",
                          f"---\ntipo: {tipo}\ncontrato: 1\npedido: {pedido}\nbranch: {ramo}\ncommit: {commit}\n"
                          f"parecer: {parecer}\n{extra}\ndata: 2026-01-01\n---\n# parecer\n")

    def roda(self, base_ref="develop"):
        self.repo.commit()
        return catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", "pr", base_ref)

    def test_pr_que_nao_toca_codigo_sensivel_passa(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.assertEqual(self.roda(), [])

    def test_toca_hooks_sem_parecer_barra(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        achadas = self.roda()
        self.assertEqual(len(achadas), 1)
        self.assertTrue(achadas[0].startswith("R-REVIEW:"))

    def test_toca_hooks_com_review_aprovado_passa_na_develop_e_exige_qa_na_homolog(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commit=self.repo.git("rev-parse", "--short", "HEAD").strip())  # P5: classe C; AQ-5: o sha do código
        self.assertEqual(self.roda("develop"), [])
        self.assertEqual(len(self.roda("homolog")), 1)

    def test_promocao_fica_fora_do_job(self):
        """Review 2: develop -> homolog e homolog -> main não exigem parecer novo (foi exigido na entrada na develop)."""
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.repo.commit()
        for ramo, base_ref in (("develop", "homolog"), ("homolog", "main")):
            with self.subTest(ramo=ramo):
                self.assertEqual(catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", ramo, base_ref), [])
        for ramo, base_ref in (("melhoria/x", "homolog"), ("develop", "main"), ("melhoria/x", "develop")):
            with self.subTest(ramo=ramo, base_ref=base_ref):
                self.assertEqual(len(catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", ramo, base_ref)), 1)

    def test_usa_o_forge_check_do_proprio_script(self):
        """Review 13: uma fonte só para ler os pareceres (ADR 0002)."""
        fc = catraca.forge_check()
        self.assertTrue(callable(fc.pedidos_da_branch) and callable(fc.cmd_pr))
        self.assertFalse(hasattr(catraca, "pedidos_da_branch"))

    def test_parecer_reprovado_ou_de_outra_branch_barra(self):
        self.repo.escreve("scripts/novo.sh", "echo\n")
        self.parecer("review", parecer="ajustes")
        self.assertEqual(len(self.roda()), 1)
        self.parecer("review", ramo="outra")
        self.assertEqual(len(self.roda()), 1)

    def test_um_pedido_reprovado_barra_mesmo_com_outro_aprovado(self):
        """Proposta anti-alucinação, seção 9, item 4: o primeiro pedido aprovado não pode aprovar a branch inteira.
        Os dois nomes cobrem as duas ordens (o forge-check devolve os pedidos em ordem alfabética)."""
        for aprovado, reprovado in (("a-ok", "b-ruim"), ("b-ok", "a-ruim")):
            with self.subTest(aprovado=aprovado):
                self.setUp()
                self.repo.escreve("hooks/novo.py", "x = 1\n")
                self.parecer("review", pedido=reprovado, parecer="reprovado")
                self.parecer("review", pedido=aprovado)
                achadas = self.roda()
                self.assertEqual(len(achadas), 1)
                self.assertIn(f"docs/reviews/{reprovado}.md", achadas[0])

    def test_dois_pedidos_aprovados_passam(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review", pedido="a")
        self.parecer("review", pedido="b")
        self.parecer("revisao-seguranca", pedido="a")  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.parecer("revisao-seguranca", pedido="b")
        self.assertEqual(self.roda(), [])

    # --- O parecer sobrevive a merge da base e a commit de parecer (diff efetivo, ADR 0004 item 3) ---
    def mescla_base(self, rel="scripts/da-base.sh"):
        """A base (`develop`) ganha um commit depois do parecer e ele é mesclado na branch do PR."""
        self.repo.commit()
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve(rel, "echo base\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")

    def roda_sobre_develop(self):
        self.repo.commit()
        return catraca.violacoes_de_pareceres(self.repo.dir, "develop", "HEAD", "pr", "develop")

    def test_merge_da_base_depois_do_parecer_mantem_o_parecer(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commit=self.repo.git("rev-parse", "--short", "HEAD").strip())  # P5: classe C; AQ-5: o sha do código
        self.mescla_base()
        self.assertEqual(self.roda_sobre_develop(), [])

    def test_mudanca_de_codigo_depois_do_merge_da_base_invalida_o_parecer(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.mescla_base()
        self.repo.escreve("hooks/novo.py", "x = 2\n")
        achadas = self.roda_sobre_develop()
        self.assertEqual(len(achadas), 1)
        self.assertIn("desatualizado", achadas[0])

    def test_veredito_trocado_no_parecer_depois_do_merge_continua_conferido(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.mescla_base()
        texto = (self.repo.dir / "docs/reviews/ped.md").read_text(encoding="utf-8")
        self.repo.escreve("docs/reviews/ped.md", texto.replace("parecer: aprovado", "parecer: reprovado"))
        achadas = self.roda_sobre_develop()
        self.assertEqual(len(achadas), 1)
        self.assertIn("não é aprovado", achadas[0])

    def test_sem_base_o_merge_da_base_continua_invalidando(self):
        """`forge-check pr` sem `--base` mantém a regra estrita (diff direto entre o commit e o head)."""
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.mescla_base()
        self.repo.commit()
        fc = catraca.forge_check()
        self.assertTrue(any("desatualizado" in l for l in fc.cmd_pr(self.repo.dir, "ped")))
        self.assertFalse(any("desatualizado" in l for l in fc.cmd_pr(self.repo.dir, "ped", None, "develop")))


class ParecerReprovadoBarraSempre(Base):
    """Item 5 do N-CAT1: o último parecer de cada tipo dos pedidos da branch barra se não aprova, com ou sem arquivo sensível,
    com o tipo exigido ou não e na entrada da `develop` também (promoção fica de fora)."""

    PASTAS = {"review": "reviews", "qa": "qa", "revisao-seguranca": "security", "revisao-devops": "devops"}

    def parecer(self, tipo, parecer="aprovado", ramo="pr", pedido="ped", data="2026-01-01", arquivo=None, commita=True, commit=None):
        if commita:
            self.repo.commit()
        commit = commit or self.repo.git("rev-parse", "--short", "HEAD").strip()
        pasta = self.PASTAS[tipo]
        extra = "qa: forge:qa-engineer\nescopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0" if tipo == "qa" else "revisor: forge:tech-lead"
        self.repo.escreve(f"docs/{pasta}/{arquivo or pedido}.md",
                          f"---\ntipo: {tipo}\ncontrato: 1\npedido: {pedido}\nbranch: {ramo}\ncommit: {commit}\n"
                          f"parecer: {parecer}\n{extra}\ndata: {data}\n---\n# parecer\n")

    def roda(self, base_ref="develop", ramo="pr"):
        self.repo.commit()
        return catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", ramo, base_ref)

    def test_review_reprovado_barra_pr_que_nao_toca_arquivo_sensivel(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review", "reprovado")
        achadas = self.roda()
        self.assertEqual(len(achadas), 1, achadas)
        self.assertRegex(achadas[0], r"^R-REVIEW: .+docs/reviews/ped\.md.+\. Por quê: .+\. Corrigir: .+ \(.+\)$")

    def test_review_reprovado_barra_em_agents_e_skills(self):
        for rel in ("agents/x.md", "skills/x/SKILL.md"):
            with self.subTest(rel):
                self.setUp()
                self.repo.escreve(rel, "x\n")
                self.parecer("review", "reprovado")
                self.assertEqual(len(self.roda()), 1)

    def test_seguranca_reprovada_barra_mesmo_sem_gatilho_no_diff(self):
        self.repo.escreve("docs/x.md", "x\n")  # P5 (0.43.1): scripts/ virou classe C (pede segurança); o diff sem gatilho é o de documentação
        self.parecer("review")
        self.parecer("qa", commita=False)
        self.parecer("revisao-seguranca", "reprovado", commita=False)
        achadas = self.roda()
        self.assertEqual(len(achadas), 1, achadas)
        self.assertRegex(achadas[0], r"^R-SEGURANCA: .+docs/security/ped\.md")

    def test_devops_reprovado_barra_mesmo_sem_infra_no_diff(self):
        self.repo.escreve("docs/x.md", "x\n")  # P5 (0.43.1): scripts/ virou classe C (pede segurança); o diff sem infra é o de documentação
        self.parecer("review")
        self.parecer("revisao-devops", "reprovado", commita=False)
        achadas = self.roda()
        self.assertEqual(len(achadas), 1, achadas)
        self.assertIn("docs/devops/ped.md", achadas[0])

    def test_qa_reprovado_barra_na_entrada_da_develop(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commita=False)  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.parecer("qa", "reprovado", commita=False)
        achadas = self.roda("develop")
        self.assertEqual(len(achadas), 1, achadas)
        self.assertRegex(achadas[0], r"^R-QA: .+docs/qa/ped\.md")

    def test_valor_fora_do_contrato_barra(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review", "ajustes")
        self.assertEqual(len(self.roda()), 1)

    def test_riscos_aceitos_so_passa_com_o_aceite_do_usuario(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", "riscos-aceitos", commit="abc1234", commita=False)
        achadas = self.roda()
        self.assertEqual(len(achadas), 1, achadas)
        self.assertIn("docs/security/ped.md", achadas[0])
        self.repo.escreve("docs/security/aceites/ped.md", "---\npedido: ped\naceite: sim\ncommit: abc1234\n---\n")
        self.assertEqual(self.roda(), [])

    def test_sensivel_com_review_reprovado_continua_com_uma_violacao_so(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review", "reprovado")
        achadas = self.roda()
        self.assertEqual(len(achadas), 1, achadas)
        self.assertIn("docs/reviews/ped.md", achadas[0])

    def test_nao_regressao_parecer_mais_novo_aprovado_substitui_o_reprovado(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review", "reprovado", arquivo="ped-v1", data="2026-01-01")
        self.parecer("review", "aprovado", arquivo="ped-v2", data="2026-01-02", commita=False)
        self.assertEqual(self.roda(), [])

    def test_nao_regressao_parecer_regravado_no_mesmo_arquivo(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review", "reprovado")
        self.repo.commit()
        self.parecer("review", "aprovado", commita=False)
        self.assertEqual(self.roda(), [])

    def test_nao_regressao_parecer_de_outra_branch_nao_barra(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review", "reprovado", ramo="outra")
        self.assertEqual(self.roda(), [])

    def test_e11_parecer_da_branch_do_pr_vence_o_de_outra_branch_no_desempate(self):
        """Caso do #437: mesmo pedido e data; o parecer de outra branch (sha sumido no squash) vence por caminho, e o da branch vale."""
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commita=False)  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.parecer("review", ramo="outra", arquivo="zz-outra", commit="deadbee", commita=False)
        self.assertEqual(self.roda(), [])

    def test_e11_reprovado_da_propria_branch_barra_com_aprovado_de_outra_vencendo(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review", "reprovado")
        self.parecer("review", ramo="outra", arquivo="zz-outra", commita=False)
        achadas = self.roda()
        self.assertEqual(len(achadas), 1, achadas)
        self.assertIn("docs/reviews/ped.md", achadas[0])

    def test_e11_tipo_exigido_so_em_outra_branch_falha_fechado(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("qa", ramo="outra", commita=False)
        achadas = self.roda("homolog")
        self.assertEqual(len(achadas), 1, achadas)
        self.assertIn('sem parecer da branch "pr" para o pedido `ped`', achadas[0])

    def test_fork_com_o_nome_de_branch_ja_mesclada_nao_herda_o_parecer(self):
        """A1: parecer aprovado com `branch: pr` cobre o PR do próprio repositório, mas não o de um fork com o mesmo nome de branch."""
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commita=False)  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.assertEqual(self.roda(), [])
        for head in ("fulano/Forge", ""):  # fork e head.repo nulo (fork apagado)
            with self.subTest(head=head):
                achadas = catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", "pr", "develop", head, "dono/Forge")
                self.assertEqual(len(achadas), 1, achadas)
                self.assertIn("R-REVIEW", achadas[0])
                self.assertIn("dono/Forge", achadas[0])

    def test_fork_recusa_ate_sem_arquivo_sensivel_e_nas_promocoes(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.repo.commit()
        for ramo, base_ref in (("pr", "develop"), ("develop", "homolog"), ("homolog", "main")):
            with self.subTest(ramo=ramo):
                achadas = catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", ramo, base_ref, "fulano/Forge", "dono/Forge")
                self.assertEqual(len(achadas), 1, achadas)

    def test_em_ci_sem_base_repo_falha_fechado_e_fora_do_ci_libera(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commita=False)  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.repo.commit()
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            for head in ("", "dono/Forge"):
                with self.subTest(head=head):
                    achadas = catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", "pr", "develop", head, "")
                    self.assertEqual(len(achadas), 1, achadas)
            self.assertEqual(catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", "pr", "develop", "dono/Forge", "dono/Forge"), [])
        self.assertEqual(catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", "pr", "develop", "", ""), [])

    def test_workflow_declara_head_repo_e_base_repo_no_passo_de_pareceres(self):
        texto = (AQUI.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        (passo,) = [p for p in re.split(r"\n      - name: ", texto) if "--modo pareceres" in p]
        passo = re.split(r"\n\n  [a-z-]+:\n", passo, maxsplit=1)[0]  # o passo é o último do job: o corte evita ler o job seguinte
        env = passo.split("        env:\n", 1)[1].split("        run:", 1)[0]
        self.assertIn("HEAD_REPO: ${{ github.event.pull_request.head.repo.full_name }}", env)
        self.assertIn("BASE_REPO: ${{ github.repository }}", env)
        self.assertNotIn("${{", passo.split("        run:", 1)[1])

    def test_mesmo_repositorio_ou_sem_env_nao_muda_o_resultado(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commita=False)  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.repo.commit()
        for head, base in (("dono/Forge", "dono/Forge"), ("", "")):
            with self.subTest(head=head):
                self.assertEqual(catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", "pr", "develop", head, base), [])

    def test_cli_le_o_repositorio_do_head_por_env_e_recusa_o_fork(self):
        self.repo.escreve("hooks/novo.py", "x = 1\n")
        self.parecer("review")
        self.parecer("revisao-seguranca", commita=False)  # P5 (0.43.1): hooks/ é classe C, que pede também o de segurança
        self.repo.commit()
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "GITHUB_ACTIONS", "HEAD_REPO", "BASE_REPO")}
        argv = ["python3", str(AQUI / "catraca.py"), "--modo", "pareceres", "--raiz", str(self.repo.dir), "--base", "base",
                "--ramo", "pr", "--base-ref", "develop"]
        ok = subprocess.run(argv, capture_output=True, text=True, env={**env, "HEAD_REPO": "dono/Forge", "BASE_REPO": "dono/Forge"})
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        fork = subprocess.run(argv, capture_output=True, text=True, env={**env, "HEAD_REPO": "fulano/Forge", "BASE_REPO": "dono/Forge"})
        self.assertEqual(fork.returncode, 1, fork.stdout + fork.stderr)

    def test_nao_regressao_promocao_nao_le_parecer(self):
        self.repo.escreve("docs/x.md", "x\n")
        self.parecer("review", "reprovado")
        self.repo.commit()
        for ramo, base_ref in (("develop", "homolog"), ("homolog", "main")):
            with self.subTest(ramo=ramo):
                self.assertEqual(catraca.violacoes_de_pareceres(self.repo.dir, "base", "HEAD", ramo, base_ref), [])

    def test_nao_regressao_sem_parecer_e_sem_arquivo_sensivel_passa(self):
        """A exigência de parecer não cresce: só o reprovado que já existe barra."""
        self.repo.escreve("docs/x.md", "x\n")
        self.assertEqual(self.roda(), [])


def execucao(sha, quando, numero=7, evento="pull_request"):
    return {"event": evento, "head_sha": sha, "created_at": quando, "pull_requests": [{"number": numero}]}


def rotulo(quem="dona", quando="2026-01-02T10:00:00Z", tipo="labeled"):
    return {"event": tipo, "label": {"name": catraca.ROTULO}, "actor": {"login": quem}, "created_at": quando}


class CommitDoRotulo(unittest.TestCase):
    """O head do PR quando o dono aplicou o rótulo, pelas execuções do Actions (instante do servidor); senão None."""

    def test_head_vigente_e_a_ultima_execucao_antes_do_rotulo(self):
        execs = [execucao("a", "2026-01-02T08:00:00Z"), execucao("b", "2026-01-02T09:00:00Z"), execucao("b", "2026-01-02T10:00:03Z"),
                 execucao("c", "2026-01-02T11:00:00Z")]
        self.assertEqual(catraca.commit_do_rotulo([rotulo()], execs, "7", "dona"), "b")

    def test_execucao_de_outro_pr_ou_de_outro_evento_nao_conta(self):
        execs = [execucao("b", "2026-01-02T09:00:00Z"), execucao("x", "2026-01-02T09:30:00Z", numero=8),
                 execucao("y", "2026-01-02T09:40:00Z", evento="push"), execucao("b", "2026-01-02T10:00:03Z")]
        self.assertEqual(catraca.commit_do_rotulo([rotulo()], execs, 7, "dona"), "b")

    def test_sem_execucao_do_mesmo_head_depois_do_rotulo_falha_fechado(self):
        """Head sem execução no instante do rótulo ([skip ci], workflow desligado): a atribuição seria de um head anterior."""
        execs = [execucao("a", "2026-01-02T09:00:00Z"), execucao("c", "2026-01-02T10:00:03Z")]
        self.assertIsNone(catraca.commit_do_rotulo([rotulo()], execs, 7, "dona"))

    def test_force_push_depois_do_head_vigente_falha_fechado(self):
        execs = [execucao("b", "2026-01-02T09:00:00Z"), execucao("b", "2026-01-02T10:00:03Z")]
        forca = {"event": "head_ref_force_pushed", "created_at": "2026-01-02T09:30:00Z"}
        self.assertIsNone(catraca.commit_do_rotulo([rotulo(), forca], execs, 7, "dona"))

    def test_rotulo_de_outra_pessoa_removido_ou_ausente_nao_vale(self):
        execs = [execucao("b", "2026-01-02T09:00:00Z"), execucao("b", "2026-01-02T10:00:03Z")]
        self.assertIsNone(catraca.commit_do_rotulo([rotulo("intrusa")], execs, 7, "dona"))
        self.assertIsNone(catraca.commit_do_rotulo([rotulo(), rotulo(quando="2026-01-02T10:01:00Z", tipo="unlabeled")], execs, 7, "dona"))
        self.assertIsNone(catraca.commit_do_rotulo([], execs, 7, "dona"))
        self.assertIsNone(catraca.commit_do_rotulo([rotulo()], execs, 7, None))
        self.assertIsNone(catraca.commit_do_rotulo([rotulo()], [], 7, "dona"))


class RotuloSobreviveAoConteudo(Base):
    """O rótulo vale para o diff efetivo do PR no instante em que foi aplicado (sem pareceres e sem o que veio da base). Desde a
    0.43.1 (P9) vale também com os arquivos protegidos iguais aos do rótulo: os testes do diff efetivo rodam com `so_diff=True`, que
    desliga esse caminho e deixa só o do diff efetivo (o que sobra quando a base também mexeu no arquivo protegido)."""

    def setUp(self):
        super().setUp()
        self.repo.escreve("tests/catraca.py", "x = 'mudou no PR'\n")  # protegido: só passa com o rótulo
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()

    def roda(self, execs=None, ramo="", so_diff=False):
        self.repo.commit()
        if so_diff:
            return self.roda_aqui(execs, ramo)
        entrada = tempfile.TemporaryDirectory()
        self.addCleanup(entrada.cleanup)
        pasta = Path(entrada.name)
        (pasta / "eventos.json").write_text(json.dumps([rotulo()]), encoding="utf-8")
        execs = execs if execs is not None else [execucao(self.rotulado, "2026-01-02T09:00:00Z"), execucao(self.rotulado, "2026-01-02T10:00:03Z")]
        (pasta / "execucoes.json").write_text(json.dumps(execs), encoding="utf-8")
        args = ["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "develop",
                "--eventos", str(pasta / "eventos.json"), "--ultimo-push", "2026-01-02T11:00:00Z",
                "--execucoes", str(pasta / "execucoes.json"), "--pr", "7", f"--ramo={ramo}"]
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "HEAD_REF")}
        return subprocess.run(args, capture_output=True, text=True, env=env)

    def roda_aqui(self, execs=None, ramo=""):
        """A catraca no mesmo processo, só com o caminho do diff efetivo (`protegidos_como_no_rotulo` falso)."""
        pasta = Path(tempfile.mkdtemp(dir=self.repo.dir.parent))
        self.addCleanup(shutil.rmtree, pasta, True)
        (pasta / "eventos.json").write_text(json.dumps([rotulo()]), encoding="utf-8")
        execs = execs if execs is not None else [execucao(self.rotulado, "2026-01-02T09:00:00Z"), execucao(self.rotulado, "2026-01-02T10:00:03Z")]
        (pasta / "execucoes.json").write_text(json.dumps(execs), encoding="utf-8")
        argv = ["--raiz", str(self.repo.dir), "--base", "develop", "--eventos", str(pasta / "eventos.json"), "--ultimo-push", "2026-01-02T11:00:00Z",
                "--execucoes", str(pasta / "execucoes.json"), "--pr", "7", f"--ramo={ramo}"]
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "HEAD_REF")}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(catraca, "protegidos_como_no_rotulo", return_value=False), \
                contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(argv)
        return SimpleNamespace(returncode=rc, stdout=saida.getvalue())

    def mescla_base(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve("docs/da-base.md", "veio da base\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")

    def test_merge_da_base_depois_do_rotulo_mantem_o_rotulo(self):
        self.mescla_base()
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("liberada", r.stdout)

    def test_commit_so_de_parecer_mantem_o_rotulo(self):
        """Parecer cujo nome é o da branch (o pedido desta branch) muda depois do rótulo sem invalidá-lo."""
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        self.repo.escreve("docs/qa/ped.md", "parecer\n")
        self.assertEqual(self.roda(ramo="melhoria/ped").returncode, 0)

    def test_parecer_de_outro_pedido_depois_do_rotulo_invalida(self):
        """Review #65, desvio 1: só os pareceres dos pedidos desta branch ficam fora da comparação."""
        for rel in ("docs/reviews/outro.md", "docs/qa/outro.md", "docs/reviews/ped-x.md"):
            with self.subTest(rel=rel):
                self.repo.git("reset", "-q", "--hard", self.rotulado)
                self.repo.escreve(rel, "reescrito depois do rótulo\n")
                r = self.roda(ramo="melhoria/ped", so_diff=True)
                self.assertEqual(r.returncode, 1, r.stdout)

    def test_parecer_de_outro_pedido_que_ja_existia_na_base_invalida(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve("docs/reviews/antigo.md", "parecer original\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("docs/reviews/antigo.md", "histórico reescrito\n")
        self.assertEqual(self.roda(ramo="melhoria/ped", so_diff=True).returncode, 1)

    def test_parecer_que_o_pr_ja_tocava_antes_do_rotulo_pode_mudar(self):
        self.repo.escreve("docs/reviews/tocado.md", "parecer de autor\n")
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("docs/reviews/tocado.md", "parecer independente\n")
        self.assertEqual(self.roda().returncode, 0)

    def test_sem_ramo_na_linha_de_comando_usa_a_branch_do_pr_pela_api(self):
        """No CI o `catraca.yml` não passa a branch: ela vem do PR pela API (gratuita, só leitura)."""
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        self.repo.commit()
        execs = [execucao(self.rotulado, "2026-01-02T09:00:00Z"), execucao(self.rotulado, "2026-01-02T10:00:03Z")]
        originais = {n: getattr(catraca, n, None) for n in ("eventos_do_github", "execucoes_do_pr", "ramo_do_pr")}
        self.addCleanup(lambda: [setattr(catraca, n, f) for n, f in originais.items()])
        catraca.eventos_do_github = lambda: ([rotulo()], "2026-01-02T11:00:00Z")
        catraca.execucoes_do_pr = lambda: execs
        for ramo, esperado in (("melhoria/ped", 0), ("", 1)):
            with self.subTest(ramo=ramo):
                catraca.ramo_do_pr = lambda ramo=ramo: ramo
                antigo = dict(os.environ)
                self.addCleanup(lambda: (os.environ.clear(), os.environ.update(antigo)))
                for k in ("HEAD_REF", "GITHUB_STEP_SUMMARY"):
                    os.environ.pop(k, None)
                with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(catraca, "protegidos_como_no_rotulo", return_value=False):
                    self.assertEqual(catraca.main(["--raiz", str(self.repo.dir), "--base", "develop", "--pr", "7"]), esperado)

    def test_sem_ramo_parecer_novo_depois_do_rotulo_invalida(self):
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        self.assertEqual(self.roda(so_diff=True).returncode, 1)

    def test_nome_com_curinga_nao_vira_padrao_que_esconde_outros_pareceres(self):
        """O caminho ignorado vai literal ao git: `docs/reviews/*` tocado antes do rótulo não cobre `outro.md`."""
        self.repo.escreve("docs/reviews/*", "parecer de nome estranho\n")
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("docs/reviews/outro.md", "reescrito\n")
        self.assertEqual(self.roda(so_diff=True).returncode, 1)

    def test_violacao_nova_vinda_da_base_invalida(self):
        """Review #65, desvio 2: a base passa a proteger um arquivo que o patch do PR já apagava."""
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve("docs/nova.md", "regra nova\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")
        self.repo.git("rm", "-q", "docs/nova.md")
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.git("checkout", "-q", "develop")
        self.repo.config(invariantes={"docs/regra.md": ["nunca sem teste"], "docs/nova.md": ["regra nova"]})
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")
        r = self.roda()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("docs/nova.md", r.stdout)

    def test_mesma_violacao_com_numero_diferente_depois_da_base_mantem_o_rotulo(self):
        """O texto é comparado sem os números: a contagem de testes muda com a base, a violação é a mesma."""
        self.repo.escreve("tests/test_x.py", TESTE.replace("    def test_b(self): pass\n", ""))
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve("tests/test_z.py", "import unittest\nclass T(unittest.TestCase):\n    def test_z(self):\n        self.assertTrue(1)\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_mudanca_de_codigo_depois_do_rotulo_invalida(self):
        for rel, texto in (("tests/catraca.py", "x = 'mudou de novo'\n"), ("scripts/novo.sh", "echo\n"), ("KANBAN.md", "x\n")):
            with self.subTest(rel=rel):
                self.repo.git("reset", "-q", "--hard", self.rotulado)
                self.repo.escreve(rel, texto)
                r = self.roda(so_diff=True)
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("R-CONFORMIDADE:", r.stdout)

    def test_mudanca_de_codigo_junto_com_merge_da_base_invalida(self):
        self.mescla_base()
        self.repo.escreve("scripts/novo.sh", "echo\n")
        self.assertEqual(self.roda(so_diff=True).returncode, 1)

    def test_sem_execucoes_ou_commit_desconhecido_falha_fechado(self):
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        self.assertEqual(self.roda([]).returncode, 1)
        fantasma = "0" * 40
        self.assertEqual(self.roda([execucao(fantasma, "2026-01-02T09:00:00Z"), execucao(fantasma, "2026-01-02T10:00:03Z")]).returncode, 1)

    def test_git_diff_falho_no_head_rotulado_nao_libera_pelo_conteudo(self):
        """O `git diff` falha só ao listar os pareceres do head rotulado: o rótulo por conteúdo não vale, rc 1."""
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        self.repo.commit()
        pasta = Path(tempfile.mkdtemp(dir=self.repo.dir.parent))
        self.addCleanup(lambda: [f.unlink() for f in pasta.iterdir()] and pasta.rmdir())
        (pasta / "eventos.json").write_text(json.dumps([rotulo()]), encoding="utf-8")
        (pasta / "execucoes.json").write_text(json.dumps([execucao(self.rotulado, "2026-01-02T09:00:00Z"), execucao(self.rotulado, "2026-01-02T10:00:03Z")]), encoding="utf-8")
        argv = ["--raiz", str(self.repo.dir), "--base", "develop", "--eventos", str(pasta / "eventos.json"), "--ultimo-push", "2026-01-02T11:00:00Z",
                "--execucoes", str(pasta / "execucoes.json"), "--pr", "7", "--ramo=melhoria/ped"]
        original = catraca.alterados

        def falha_no_rotulado(raiz, base, head):
            if head == self.rotulado:
                raise catraca.ErroDeDiff(catraca.msg_diff(base, head))
            return original(raiz, base, head)
        with contextlib.redirect_stdout(io.StringIO()) as controle:
            self.assertEqual(catraca.main(argv), 0, controle.getvalue())  # com o git funcionando, o rótulo vale
        with mock.patch.object(catraca, "alterados", falha_no_rotulado), contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(argv)
        self.assertEqual(rc, 1, saida.getvalue())
        self.assertIn("não consegui listar os arquivos alterados", saida.getvalue())

    def test_rotulo_nao_libera_custo_nem_pelo_conteudo(self):
        self.repo.git("reset", "-q", "--hard", "base")
        self.repo.escreve("scripts/x.sh", "export ANTHROPIC_API_KEY=1\n")
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        r = self.roda()
        self.assertEqual(r.returncode, 1)
        self.assertIn("R-CUSTO:", r.stdout)


    # --- P9 (0.43.1, PARECER-CONTEUDO): o rótulo fica preso aos arquivos protegidos ---
    def test_p9_push_sem_arquivo_protegido_mantem_o_rotulo(self):
        for rel, texto in (("scripts/novo.sh", "echo\n"), ("KANBAN.md", "x\n"), ("docs/reviews/outro.md", "reescrito\n"),
                           ("src/app.py", "x = 1\n"), ("tests/test_novo.py", "import unittest\nclass T(unittest.TestCase):\n"
                                                                         "    def test_n(self):\n        self.assertTrue(1)\n")):
            with self.subTest(rel=rel):
                self.repo.git("reset", "-q", "--hard", self.rotulado)
                self.repo.escreve(rel, texto)
                r = self.roda()
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertIn("arquivos protegidos ou diff efetivo iguais", r.stdout)

    def test_p9_push_que_muda_arquivo_protegido_derruba_o_rotulo(self):
        for rel, texto in (("tests/catraca.py", "x = 'mudou de novo'\n"), (".github/workflows/ci.yml", "name: outro\n"),
                           ("bin/forge-check", "#!/bin/sh\n"), ("hooks/x.cpython-312.pyc", "\0")):
            with self.subTest(rel=rel):
                self.repo.git("reset", "-q", "--hard", self.rotulado)
                self.repo.escreve(rel, texto)
                r = self.roda()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("R-CONFORMIDADE:", r.stdout)

    def test_p9_protegido_que_volta_ao_da_base_nao_derruba(self):
        """O arquivo que o PR deixa de mudar não pede mais o rótulo: a violação restante é a do rotulado (ou nenhuma)."""
        self.repo.escreve(".github/workflows/ci.yml", "name: mudou no PR\n")
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve(".github/workflows/ci.yml", "name: CI\n")
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_p9_merge_da_base_que_muda_outro_protegido_mantem(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve(".github/workflows/ci.yml", "name: CI da base\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_p9_testes_que_pioram_mais_depois_do_rotulo_derrubam(self):
        """A mesma violação (testes caíram) com número maior: a chave é a mesma, a piora não."""
        self.repo.escreve("tests/test_x.py", TESTE.replace("    def test_b(self): pass\n", ""))
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("tests/test_y.py", "import unittest\nclass T(unittest.TestCase):\n    def test_y(self):\n        self.assertTrue(1)\n")
        self.assertEqual(self.roda().returncode, 0)  # teste novo: não piora
        self.repo.git("reset", "-q", "--hard", self.rotulado)
        self.repo.escreve("tests/test_x.py", "import unittest\n")
        r = self.roda()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("caíram", r.stdout)

    def test_p9_git_que_falha_no_blob_nao_libera(self):
        self.repo.escreve("src/app.py", "x = 1\n")
        self.repo.commit()
        with mock.patch.object(catraca, "blob_e_modo", side_effect=catraca.ErroDeGit("falha do git simulada")), \
                mock.patch.object(catraca, "forge_check", side_effect=AssertionError("não chega ao diff efetivo")):
            with self.assertRaises(catraca.ErroDeGit):
                catraca.protegidos_como_no_rotulo(self.repo.dir, "develop", self.rotulado, "HEAD")


class RespostaCortadaEPaginacaoSemTeto(Base):
    """Item 3 do N-CAT1: `IncompleteRead` e páginas demais na API valem como sem rótulo, com uma linha, e nunca por rastro de pilha."""

    ENV = {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PR_NUMBER": "7", "HEAD_SHA": "abc"}

    def setUp(self):
        super().setUp()
        patch = mock.patch.dict(os.environ, self.ENV)
        patch.start()
        self.addCleanup(patch.stop)

    def corta(self, *a, **k):
        raise http.client.IncompleteRead(b"x")

    def test_resposta_cortada_vale_como_sem_dado_nas_tres_funcoes(self):
        with mock.patch.object(catraca, "requisicao", self.corta), contextlib.redirect_stdout(io.StringIO()) as saida:
            with self.subTest("eventos_do_github"):
                self.assertEqual(catraca.eventos_do_github(), (None, None))
            with self.subTest("ramo_do_pr"):
                self.assertEqual(catraca.ramo_do_pr(), "")
            with self.subTest("execucoes_do_pr"):
                with mock.patch.object(catraca, "ramo_do_pr", lambda: "melhoria/x"):
                    self.assertIsNone(catraca.execucoes_do_pr())
        self.assertEqual(saida.getvalue().count("vale como sem rótulo."), 3, saida.getvalue())

    def test_main_com_a_api_cortada_deixa_uma_linha_e_rc_1(self):
        self.repo.escreve("tests/catraca.py", "x = 'mudou'\n")
        self.repo.commit()
        with mock.patch.object(catraca, "requisicao", self.corta), contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(["--raiz", str(self.repo.dir), "--base", "base"])
        self.assertEqual(rc, 1, saida.getvalue())
        avisos = [l for l in saida.getvalue().splitlines() if l.startswith("catraca: ") and l.endswith("vale como sem rótulo.")]
        self.assertEqual(len(avisos), 1, saida.getvalue())
        self.assertIn("mudança em tests/catraca.py", saida.getvalue())

    def paginas(self, cheias):
        """`requisicao` falsa: `cheias` páginas de 100 itens e depois uma curta; anota as páginas pedidas."""
        pedidas = []

        def falsa(caminho, token):
            pagina = int(caminho.rsplit("page=", 1)[1])
            pedidas.append(pagina)
            lote = [{"created_at": "2026-01-02T09:00:00Z", "head_sha": "abc"}] * (100 if pagina <= cheias else 1)
            return {"workflow_runs": lote} if "runs" in caminho else lote
        return falsa, pedidas

    def test_api_acima_do_teto_de_paginas_e_none(self):
        falsa, pedidas = self.paginas(catraca.TETO_PAGINAS + 1)
        with mock.patch.object(catraca, "requisicao", falsa):
            self.assertIsNone(catraca.api("/x", "t"))
            self.assertEqual(pedidas, list(range(1, catraca.TETO_PAGINAS + 1)))
            self.assertIsNone(catraca.api("/runs", "t", "workflow_runs"))

    def test_api_no_teto_ou_abaixo_devolve_tudo(self):
        falsa, pedidas = self.paginas(catraca.TETO_PAGINAS - 1)
        with mock.patch.object(catraca, "requisicao", falsa):
            self.assertEqual(len(catraca.api("/x", "t")), 100 * (catraca.TETO_PAGINAS - 1) + 1)

    def test_paginas_demais_valem_como_sem_rotulo_nas_funcoes_que_usam_a_api(self):
        falsa, _ = self.paginas(catraca.TETO_PAGINAS + 1)
        with mock.patch.object(catraca, "requisicao", falsa), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(catraca.eventos_do_github(), (None, None))
            with mock.patch.object(catraca, "ramo_do_pr", lambda: "melhoria/x"):
                self.assertIsNone(catraca.execucoes_do_pr())


class ExecucoesDoPr(unittest.TestCase):
    """Execuções do PR pela API (gratuita, só leitura): `pull_request` da branch do PR; sem dados ou com falha, None."""

    def setUp(self):
        self.antigo = dict(os.environ)
        os.environ.update({"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PR_NUMBER": "7"})
        self.originais = (catraca.api, catraca.api_objeto)
        self.addCleanup(lambda: (setattr(catraca, "api", self.originais[0]), setattr(catraca, "api_objeto", self.originais[1])))
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(self.antigo)))

    def test_consulta_as_execucoes_pull_request_da_branch_do_pr(self):
        chamadas = []
        catraca.api_objeto = lambda caminho, token: chamadas.append(caminho) or {"head": {"ref": "melhoria/a b"}}
        catraca.api = lambda caminho, token, chave=None: chamadas.append((caminho, chave)) or [execucao("b", "2026-01-02T09:00:00Z")]
        self.assertEqual(catraca.execucoes_do_pr(), [execucao("b", "2026-01-02T09:00:00Z")])
        self.assertEqual(chamadas[0], "/repos/o/r/pulls/7")
        self.assertEqual(chamadas[1], ("/repos/o/r/actions/runs?event=pull_request&branch=melhoria%2Fa%20b", "workflow_runs"))

    def test_ramo_do_pr_vem_da_api_e_falha_vira_vazio(self):
        catraca.api_objeto = lambda caminho, token: {"head": {"ref": "melhoria/ped"}} if caminho == "/repos/o/r/pulls/7" else {}
        self.assertEqual(catraca.ramo_do_pr(), "melhoria/ped")
        catraca.api_objeto = lambda caminho, token: {"head": {}}
        self.assertEqual(catraca.ramo_do_pr(), "")
        del os.environ["GITHUB_TOKEN"]
        self.assertEqual(catraca.ramo_do_pr(), "")

    def test_sem_token_ou_com_falha_da_api_e_none(self):
        def falha(*a, **k):
            raise OSError("sem rede")
        catraca.api_objeto = falha
        self.assertIsNone(catraca.execucoes_do_pr())
        del os.environ["GITHUB_TOKEN"]
        self.assertIsNone(catraca.execucoes_do_pr())


REPO_GH = "o/r"


def lado(ref, repo=REPO_GH):
    return {"ref": ref, "repo": {"full_name": repo}}


def corrida(sha, quando, ramo="develop", repo=REPO_GH, evento="pull_request"):
    """Execução do Actions como a API devolve para PR já fechado: `pull_requests` vazio."""
    return {"event": evento, "head_sha": sha, "head_branch": ramo, "created_at": quando, "pull_requests": [],
            "head_repository": {"full_name": repo}}


# Uma linha por forma de violação de chave (tests/catraca.py, `regras_de_config` e `regra_termos_proibidos`):
# (forma, ajuste da base, mudança do head sobre ela, texto da regra).
CHAVES_DO_CONFIG = (
    ("invariante removido", None, lambda c: c.update(invariantes={}), "invariante removido de docs/regra.md"),
    ("termos_proibidos_hash removido", lambda c: c.update(termos_proibidos_hash=[hash_("Forma1")]),
     lambda c: c.update(termos_proibidos_hash=[]), "removido ou alterado em termos_proibidos_hash"),
    ("termos_proibidos sem cobertura", None, lambda c: c.update(termos_proibidos=[]), "sem cobertura em termos_proibidos_hash"),
    ("neutralidade: termo removido", None, lambda c: c["neutralidade_nucleo"].update(termos=[]), "termo de neutralidade removido"),
    ("neutralidade: pasta removida", None, lambda c: c["neutralidade_nucleo"].update(pastas=[]), "pasta saiu da checagem de neutralidade"),
    ("neutralidade: pasta ignorada", None, lambda c: c["neutralidade_nucleo"].update(ignorar=["docs"]), "nova pasta ignorada pela neutralidade"),
    ("neutralidade: exceção nova", None, lambda c: c["neutralidade_nucleo"].update(excecoes={"agents/a.md": ["x"]}),
     "exceção nova de neutralidade"),
    ("anti-duplicação: exceção nova", None, lambda c: c["anti_duplicacao"].update(excecoes=["trecho"]), "exceção nova de anti-duplicação"),
    ("anti-duplicação: palavras removido", None, lambda c: c["anti_duplicacao"].pop("palavras"), "anti_duplicacao.palavras removido"),
    ("anti-duplicação: palavras subiu", None, lambda c: c["anti_duplicacao"].update(palavras=13), "anti-duplicação exige mais palavras iguais"),
    ("anti-duplicação: pasta removida", None, lambda c: c["anti_duplicacao"].update(pastas=[]), "pasta saiu da anti-duplicação"),
    ("limite_linhas removido", None, lambda c: c.update(limite_linhas={}), "limite_linhas.agente removido"),
    ("limite_linhas subiu", None, lambda c: c["limite_linhas"].update(agente=20), "limite_linhas.agente subiu de 10 para 20"),
    ("dono trocado", None, lambda c: c.update(dono="outro"), "a chave `dono` mudou"),
    ("custo_permitido novo", None, lambda c: c.update(custo_permitido={"scripts/x.sh": ["y"]}), "permissão nova de custo em scripts/x.sh"),
)


class RotuloDePrMesclado(Base):
    """S-16: na promoção, a violação "mudança em <arquivo>" fica coberta pelo rótulo do dono já posto num PR mesclado
    em base..head, se o arquivo tem o mesmo blob e modo do head rotulado; tudo o mais pede o rótulo (A1-A14 da segurança)."""

    def setUp(self):
        super().setUp()
        r = self.repo
        r.git("branch", "main", "base")
        r.git("checkout", "-q", "-b", "fonte", "base")  # head do PR #10 (develop -> homolog), rotulado pelo dono
        r.escreve(".github/workflows/ci.yml", "name: CI\non: push\n")
        r.escreve("tests/catraca.py", "x = 'mudou no PR 10'\n")
        r.commit()
        self.s = r.git("rev-parse", "HEAD").strip()
        r.git("checkout", "-q", "-b", "homolog", "base")
        r.git("merge", "-q", "--no-ff", "-m", "Merge pull request #10 from o/develop", "fonte")
        self.m = r.git("rev-parse", "HEAD").strip()
        self.pull = {"number": 10, "created_at": "2026-01-02T08:00:00Z", "merged_at": "2026-01-02T10:30:00Z",
                     "merge_commit_sha": self.m, "base": lado("homolog"), "head": lado("develop")}
        self.eventos = [rotulo()]
        self.execs = [corrida(self.s, "2026-01-02T09:00:00Z"), corrida(self.s, "2026-01-02T10:00:03Z")]
        self.pr = {"head": lado("homolog"), "base": lado("main")}

    def roda(self, **troca):
        dados = {"repo": REPO_GH, "pr": self.pr, "pulls": {"10": self.pull}, "eventos": {"10": self.eventos},
                 "execucoes": {"10": self.execs}}
        dados.update(troca)
        arq = self.repo.dir.parent / (self.repo.dir.name + "-mesclados.json")
        arq.write_text(json.dumps(dados), encoding="utf-8")
        self.addCleanup(arq.unlink, missing_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "HEAD_REF")}
        return subprocess.run(["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "main", "--head", "homolog",
                               "--mesclados", str(arq)], capture_output=True, text=True, env=env)

    def pede(self, **troca):
        r = self.roda(**troca)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("mudança em", r.stdout)
        return r

    def depois_do_merge(self, rel, texto, msg="pr"):
        self.repo.escreve(rel, texto)
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", msg)

    def test_a14_conteudo_identico_ao_rotulado_e_mesclado_passa(self):
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("mesmo conteúdo já rotulado no PR mesclado #10", r.stdout)

    def test_merge_commit_com_ancestralidade_nao_busca_nada(self):
        """O caminho do merge commit segue como era: o substituto do squash (e o fetch) só entra quando a ancestralidade falha."""
        chamadas = []
        real = catraca.git
        with mock.patch.object(catraca, "git", lambda raiz, *a: chamadas.append(a) or real(raiz, *a)):
            fonte = catraca.FonteJson({"repo": REPO_GH, "pr": self.pr, "pulls": {"10": self.pull}, "eventos": {"10": self.eventos},
                                       "execucoes": {"10": self.execs}})
            viol = catraca.violacoes_das_regras(self.repo.dir, "main", "homolog")
            self.assertEqual(catraca.liberado_por_pr_mesclado(self.repo.dir, "main", "homolog", viol, fonte, "dona"), ["10"])
        self.assertFalse([a for a in chamadas if "fetch" in a])

    def test_branch_apagada_depois_do_merge_nao_invalida(self):
        """O `head_ref_deleted` do fechamento vem depois do merge: o que foi mesclado não muda."""
        self.eventos = [rotulo(), {"event": "head_ref_deleted", "created_at": "2026-01-02T10:31:00Z"}]
        self.assertEqual(self.roda().returncode, 0)

    def test_arquivo_alterado_depois_pede(self):
        """Casos 2, A6 e A7: uma linha a mais ou o trecho movido no mesmo arquivo mudam o blob."""
        for texto in ("x = 'mudou no PR 10'\ny = 1\n", "on: push\nname: CI\n"):
            with self.subTest(texto=texto):
                self.repo.git("reset", "-q", "--hard", self.m)
                rel = "tests/catraca.py" if texto.startswith("x") else ".github/workflows/ci.yml"
                self.depois_do_merge(rel, texto)
                self.pede()

    def test_a1_push_depois_do_rotulo_e_merge_pede(self):
        self.repo.git("checkout", "-q", "fonte")
        self.depois_do_merge("tests/catraca.py", "x = 'mudou de novo depois do rótulo'\n")
        s2 = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.git("checkout", "-q", "homolog")
        self.repo.git("reset", "-q", "--hard", "base")
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #10 from o/develop", "fonte")
        self.pull["merge_commit_sha"] = self.repo.git("rev-parse", "HEAD").strip()
        self.execs.append(corrida(s2, "2026-01-02T10:10:00Z"))
        self.pede()

    def test_a2_caso_3_pr_nao_mesclado_pede(self):
        self.pull["merged_at"] = None
        self.pede()

    def test_a3_caso_4_rotulo_de_outra_conta_por_app_ou_removido_pede(self):
        app = dict(rotulo(), performed_via_github_app={"slug": "x"})
        for eventos in ([rotulo("intrusa")], [app], [rotulo(), rotulo(quando="2026-01-02T11:00:00Z", tipo="unlabeled")], []):
            with self.subTest(eventos=eventos):
                self.eventos = eventos
                self.pede()

    def test_a5_pr_contra_outra_base_ou_de_fork_pede(self):
        for chave, valor in (("base", lado("outra")), ("base", lado("homolog", "fork/r")), ("head", lado("develop", "fork/r"))):
            with self.subTest(chave=chave, valor=valor):
                pull = dict(self.pull, **{chave: valor})
                self.pede(pulls={"10": pull})

    def test_a8_renomear_o_arquivo_rotulado_pede(self):
        self.repo.git("mv", ".github/workflows/ci.yml", ".github/workflows/ci2.yml")
        self.repo.git("commit", "-q", "-m", "renomeia")
        self.pede()

    def test_modo_link_simbolico_e_submodulo_pedem(self):
        self.repo.git("update-index", "--chmod=+x", "tests/catraca.py")
        self.repo.git("commit", "-q", "-m", "modo")
        self.pede()
        self.assertIsNone(catraca.entrada_da_arvore(self.repo.dir, "base", "tests"))  # pasta
        self.repo.git("reset", "-q", "--hard", self.m)
        os.symlink("alvo", self.repo.dir / "link")
        sub = "160000,{},sub".format("1" * 40)
        self.repo.git("update-index", "--add", "--cacheinfo", sub)
        self.repo.git("add", "link")
        self.repo.git("commit", "-q", "-m", "link e submódulo")
        self.assertIsNone(catraca.entrada_da_arvore(self.repo.dir, "HEAD", "link"))
        self.assertIsNone(catraca.entrada_da_arvore(self.repo.dir, "HEAD", "sub"))
        self.assertIsNotNone(catraca.entrada_da_arvore(self.repo.dir, "HEAD", "tests/catraca.py"))
        self.assertFalse(catraca.mesmo_arquivo(self.repo.dir, "HEAD", "HEAD", "link"))

    def test_a9_caso_9_falha_da_api_ou_sem_execucoes_pede(self):
        self.pede(pulls={})
        self.pede(eventos={})
        self.pede(execucoes={})
        self.execs = []
        self.pede()

    def test_execucao_de_fork_de_outra_branch_ou_fora_da_vida_do_pr_nao_conta(self):
        for execs in ([corrida(self.s, "2026-01-02T09:00:00Z", repo="fork/r"), corrida(self.s, "2026-01-02T10:00:03Z", repo="fork/r")],
                      [corrida(self.s, "2026-01-02T09:00:00Z", ramo="outra"), corrida(self.s, "2026-01-02T10:00:03Z", ramo="outra")],
                      [corrida(self.s, "2026-01-02T07:00:00Z"), corrida(self.s, "2026-01-02T10:40:00Z")]):
            with self.subTest(execs=execs):
                self.execs = execs
                self.pede()

    def test_force_push_antes_do_merge_pede(self):
        self.eventos = [rotulo(), {"event": "head_ref_force_pushed", "created_at": "2026-01-02T10:05:00Z"}]
        self.pede()

    def test_a10_sha_rotulado_ausente_no_git_local_pede(self):
        fantasma = "0" * 40
        self.execs = [corrida(fantasma, "2026-01-02T09:00:00Z"), corrida(fantasma, "2026-01-02T10:00:03Z")]
        self.pede()

    def test_a11_caso_7_um_arquivo_coberto_e_outro_nao_pede(self):
        self.depois_do_merge("hooks/parecer.py", "x = 'veio sem rótulo'\n")
        r = self.pede()
        self.assertIn("mudança em hooks/parecer.py", r.stdout)

    def test_a12_caso_8_custo_pede_sempre(self):
        self.depois_do_merge("scripts/x.sh", "export ANTHROPIC_API_KEY=1\n")
        r = self.pede()
        self.assertIn("R-CUSTO:", r.stdout)

    def test_violacao_sem_arquivo_continua_pedindo(self):
        """Decisão do dono (alcance A): a contagem de testes segue pedindo o rótulo (as chaves do config: o teste abaixo)."""
        self.depois_do_merge("tests/test_x.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
        r = self.pede()
        self.assertIn("testes `test_*` caíram", r.stdout)

    def refaz_o_pr_10_com_config(self, na_base, no_head):
        """Refaz o PR #10 (rotulado e mesclado) com o `tests/config.json` alterado pelo head: `na_base` ajusta a base (a `main`),
        `no_head` a mudança que o PR traz. O arquivo de regra e o workflow seguem mudados no PR, como no `setUp`."""
        r, cfg = self.repo, copy.deepcopy(CONFIG)
        r.git("checkout", "-q", "-B", "base2", "base")
        if na_base:
            na_base(cfg)
            r.escreve("tests/config.json", json.dumps(cfg))
            r.git("add", "-A")
            r.git("commit", "-q", "-m", "base com a chave")
        r.git("branch", "-f", "main", "base2")
        r.git("checkout", "-q", "-B", "fonte", "base2")
        no_head(cfg)
        r.escreve("tests/config.json", json.dumps(cfg))
        r.escreve(".github/workflows/ci.yml", "name: CI\non: push\n")
        r.escreve("tests/catraca.py", "x = 'mudou no PR 10'\n")
        r.commit()
        self.s = r.git("rev-parse", "HEAD").strip()
        r.git("checkout", "-q", "-B", "homolog", "base2")
        r.git("merge", "-q", "--no-ff", "-m", "Merge pull request #10 from o/develop", "fonte")
        self.pull["merge_commit_sha"] = self.m = r.git("rev-parse", "HEAD").strip()
        self.execs = [corrida(self.s, "2026-01-02T09:00:00Z"), corrida(self.s, "2026-01-02T10:00:03Z")]

    def test_rotulo_de_pr_mesclado_nao_cobre_nenhuma_chave_do_config(self):
        """S16-TESTE-CHAVES: a mudança de chave dentro do PR #10 rotulado e mesclado, junto da "mudança em <arquivo>" que ele
        cobre, segue pedindo o rótulo: só a violação que nomeia arquivo é liberada pelo PR mesclado. As 15 formas de violação
        de `regras_de_config` e `regra_termos_proibidos`; a guarda de completude está no teste seguinte."""
        for forma, na_base, no_head, texto in CHAVES_DO_CONFIG:
            with self.subTest(forma=forma):
                self.refaz_o_pr_10_com_config(na_base, no_head)
                r = self.pede()
                self.assertIn(texto, r.stdout)
                self.assertNotIn("liberada(s)", r.stdout)

    def test_toda_forma_de_violacao_de_chave_tem_um_caso(self):
        """Guarda de completude: cada chamada a `msg(` de `regras_de_config` e de `regra_termos_proibidos` é uma forma de violação
        de chave. Regra nova sem caso em CHAVES_DO_CONFIG deixa este teste vermelho."""
        arvore = ast.parse((AQUI / "catraca.py").read_text(encoding="utf-8"))
        formas = sum(1 for f in ast.walk(arvore) if isinstance(f, ast.FunctionDef) and f.name in ("regras_de_config", "regra_termos_proibidos")
                     for c in ast.walk(f) if isinstance(c, ast.Call) and getattr(c.func, "id", None) == "msg")
        self.assertGreaterEqual(formas, 15)
        self.assertEqual(formas, len(CHAVES_DO_CONFIG))
        self.assertEqual(len({c[0] for c in CHAVES_DO_CONFIG}), len(CHAVES_DO_CONFIG), "forma repetida na tabela")

    def test_a13_pr_de_melhoria_para_a_develop_pede(self):
        for pr in ({"head": lado("melhoria/x"), "base": lado("develop")}, {"head": lado("homolog", "fork/r"), "base": lado("main")}):
            with self.subTest(pr=pr):
                self.pede(pr=pr)

    def test_caso_5_e_6_merge_fora_do_intervalo_ou_numero_forjado_pede(self):
        """O conteúdo volta ao rotulado em #10, mas o merge de #10 já está na base; a mensagem que cita #10 não basta."""
        self.repo.git("branch", "-f", "main", self.m)
        self.repo.git("checkout", "-q", "main")
        self.depois_do_merge("tests/catraca.py", "x = 'outro conteúdo na main'\n")
        self.repo.git("checkout", "-q", "homolog")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "main")
        self.depois_do_merge("tests/catraca.py", "x = 'mudou no PR 10'\n", "volta ao rotulado (#10)")
        self.pede()
        self.repo.git("reset", "-q", "--hard", self.m)
        self.depois_do_merge("tests/catraca.py", "x = 'conteúdo sem rótulo'\n", "outra coisa (#10)")
        self.pede()

    def test_sem_transitividade_pr_mesclado_sem_o_proprio_rotulo_pede(self):
        """#10 passou sem rótulo (ex.: por este mesmo caminho); só o rótulo do dono no próprio PR vale."""
        self.eventos = [{"event": "merged", "actor": {"login": "dona"}, "created_at": "2026-01-02T10:30:00Z"}]
        self.pede()

    def test_sem_fonte_ou_sem_dono_nao_libera(self):
        viol = catraca.violacoes_das_regras(self.repo.dir, "main", "homolog")
        self.assertIsNone(catraca.liberado_por_pr_mesclado(self.repo.dir, "main", "homolog", viol, None, "dona"))
        fonte = catraca.FonteJson({"repo": REPO_GH, "pr": self.pr, "pulls": {"10": self.pull}, "eventos": {"10": self.eventos},
                                   "execucoes": {"10": self.execs}})
        self.assertIsNone(catraca.liberado_por_pr_mesclado(self.repo.dir, "main", "homolog", viol, fonte, None))
        self.assertEqual(catraca.liberado_por_pr_mesclado(self.repo.dir, "main", "homolog", viol, fonte, "dona"), ["10"])

    def test_limite_de_candidatos(self):
        for i in range(catraca.LIMITE_CANDIDATOS + 5):
            self.depois_do_merge(".github/workflows/x.yml", f"v{i}\n", f"x (#{100 + i})")
        intervalo, numeros = catraca.candidatos_mesclados(self.repo.dir, "main", "homolog", {".github/workflows/x.yml"})
        self.assertEqual(len(numeros), catraca.LIMITE_CANDIDATOS)
        self.assertEqual(numeros[0], str(100 + catraca.LIMITE_CANDIDATOS + 4))  # do mais novo ao mais antigo
        self.assertIn(self.m, intervalo)
        self.assertEqual(catraca.candidatos_mesclados(self.repo.dir, "main", "homolog", {"docs/nada.md"})[1], [])

    def test_arquivo_da_violacao_so_reconhece_a_mensagem_exata(self):
        v = catraca.msg_protegido("tests/catraca.py")
        self.assertEqual(catraca.arquivo_da_violacao(v), "tests/catraca.py")
        self.assertIsNone(catraca.arquivo_da_violacao(v.replace("Por quê: workflows", "Por quê: outro")))
        self.assertIsNone(catraca.arquivo_da_violacao("R-CONFORMIDADE: testes `test_*` caíram de 2 para 1. Por quê: x. Corrigir: y (z)"))


def _g(pasta, *args):
    env = ambiente_de_git()
    return subprocess.run(["git", "-C", str(pasta), *args], check=True, capture_output=True, text=True, env=env).stdout


def _tem(pasta, sha):
    env = ambiente_de_git()
    return subprocess.run(["git", "-C", str(pasta), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True, env=env).returncode == 0


ROTULADO = "x = 'mudou no PR 10'\n"
WORKFLOW = "name: CI\non: push\n"


class RotuloDePrSquash(Base):
    """S-16-PROMOCAO-DEVELOP: na promoção develop -> homolog os PRs entram por squash (o head rotulado S nunca é ancestral do merge M)
    e S só existe em `refs/pull/<n>/head` do origin. Casos de abuso B1-B17 do modelo de ameaças (mitigações M1-M7)."""

    def setUp(self):
        super().setUp()
        r = self.repo
        r.git("branch", "homolog", "base")
        r.git("checkout", "-q", "develop")
        self.bare = tempfile.TemporaryDirectory()
        self.clone = tempfile.TemporaryDirectory()
        self.addCleanup(self.bare.cleanup)
        self.addCleanup(self.clone.cleanup)
        _g(self.bare.name, "init", "-q", "--bare", "-b", "develop")
        remoto_sem_manutencao(self.bare.name)
        r.git("remote", "add", "origin", self.bare.name)
        _g(r.dir, "clone", "-q", str(r.dir), self.clone.name)
        _g(self.clone.name, "config", "user.email", "t@example.com")
        _g(self.clone.name, "config", "user.name", "Teste")
        _g(self.clone.name, "checkout", "-q", "-b", "melhoria/x")
        self.s = self.commita_na_fonte(ROTULADO, "feat: do PR 10")
        self.final = self.s
        self.publica(self.s)
        self.m = self.squash(ROTULADO)
        self.pull = {"number": 10, "created_at": "2026-01-02T08:00:00Z", "merged_at": "2026-01-02T10:30:00Z", "merge_commit_sha": self.m,
                     "base": lado("develop"), "head": dict(lado("melhoria/x"), sha=self.final)}
        self.eventos = [rotulo()]
        self.execs = [corrida(self.s, "2026-01-02T09:00:00Z", ramo="melhoria/x"), corrida(self.s, "2026-01-02T10:00:03Z", ramo="melhoria/x")]
        self.pr = {"head": lado("develop"), "base": lado("homolog")}
        self.args = []
        self.head = "develop"

    def commita_na_fonte(self, texto, msg):
        (Path(self.clone.name) / "tests").mkdir(exist_ok=True)
        (Path(self.clone.name) / "tests/catraca.py").write_text(texto, encoding="utf-8")
        (Path(self.clone.name) / ".github/workflows").mkdir(parents=True, exist_ok=True)
        (Path(self.clone.name) / ".github/workflows/ci.yml").write_text(WORKFLOW, encoding="utf-8")
        _g(self.clone.name, "add", "-A")
        _g(self.clone.name, "commit", "-q", "--allow-empty", "-m", msg)
        return _g(self.clone.name, "rev-parse", "HEAD").strip()

    def publica(self, sha, ref="refs/pull/10/head"):
        _g(self.clone.name, "push", "-q", "-f", self.bare.name, f"{sha}:{ref}")

    def squash(self, texto, msg="feat(x): mudança (#10)", workflow=WORKFLOW):
        """M: um commit só sobre a base da develop, sem S como ancestral."""
        self.repo.git("checkout", "-q", "develop")
        self.repo.git("reset", "-q", "--hard", "base")
        self.repo.escreve("tests/catraca.py", texto)
        self.repo.escreve(".github/workflows/ci.yml", workflow)
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", msg)
        return self.repo.git("rev-parse", "HEAD").strip()

    def depois(self, rel, texto, msg="outra coisa"):
        self.repo.escreve(rel, texto)
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", msg)

    def dados(self, **troca):
        self.pull["head"]["sha"] = self.final
        d = {"repo": REPO_GH, "pr": self.pr, "pulls": {"10": self.pull}, "eventos": {"10": self.eventos}, "execucoes": {"10": self.execs}}
        d.update(troca)
        arq = self.repo.dir.parent / (self.repo.dir.name + "-squash.json")
        arq.write_text(json.dumps(d), encoding="utf-8")
        self.addCleanup(arq.unlink, missing_ok=True)
        return ["--raiz", str(self.repo.dir), "--base", "homolog", "--head", self.head, "--mesclados", str(arq)]

    def roda(self, **troca):
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "HEAD_REF")}
        return subprocess.run(["python3", str(AQUI / "catraca.py"), *self.dados(**troca)], capture_output=True, text=True, env=env)

    def pede(self, **troca):
        r = self.roda(**troca)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("mudança em", r.stdout)
        return r

    # --- caminho feliz -------------------------------------------------------------------------------------
    def test_b1_squash_rotulado_busca_o_head_e_passa(self):
        self.assertFalse(_tem(self.repo.dir, self.s))  # S só existe no origin, em refs/pull/10/head
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("mesmo conteúdo já rotulado no PR mesclado #10", r.stdout)
        self.assertTrue(_tem(self.repo.dir, self.s))
        self.assertEqual(self.repo.git("rev-parse", "refs/catraca/pull/10").strip(), self.s)

    def test_b1_head_com_varios_commits_no_pr_passa(self):
        """S é um commit do meio: o head final é posterior, mas o conteúdo rotulado é o que o squash gravou."""
        self.final = self.commita_na_fonte(ROTULADO, "so o parecer mudou")
        self.publica(self.final)
        self.assertEqual(self.roda().returncode, 0)

    # --- a promoção como o CI a roda: head no merge de teste do PR (refs/pull/<n>/merge) -----------------------
    def merge_de_teste(self):
        """O head que o CI entrega à catraca: o merge de teste do PR, com a base (homolog) como primeiro pai e a develop como segundo."""
        arvore = self.repo.git("rev-parse", "develop^{tree}").strip()
        return self.repo.git("commit-tree", arvore, "-p", "homolog", "-p", "develop", "-m", "Merge de teste").strip()

    def segundo_pr(self, arquivo, texto):
        """PR 11, rotulado e mesclado por squash depois do PR 10, mudando um outro arquivo protegido (forma das promoções #310 e #317)."""
        _g(self.clone.name, "checkout", "-q", "-b", "melhoria/y", "origin/develop")
        (Path(self.clone.name) / arquivo).parent.mkdir(parents=True, exist_ok=True)
        (Path(self.clone.name) / arquivo).write_text(texto, encoding="utf-8")
        _g(self.clone.name, "add", "-A")
        _g(self.clone.name, "commit", "-q", "-m", "feat: do PR 11")
        s = _g(self.clone.name, "rev-parse", "HEAD").strip()
        self.publica(s, "refs/pull/11/head")
        self.depois(arquivo, texto, "feat(y): outra mudança (#11)")
        pull = {"number": 11, "created_at": "2026-01-02T11:00:00Z", "merged_at": "2026-01-02T12:30:00Z",
                "merge_commit_sha": self.repo.git("rev-parse", "HEAD").strip(), "base": lado("develop"), "head": dict(lado("melhoria/y"), sha=s)}
        execs = [corrida(s, "2026-01-02T11:30:00Z", ramo="melhoria/y"), corrida(s, "2026-01-02T12:00:03Z", ramo="melhoria/y")]
        return pull, [rotulo(quando="2026-01-02T12:00:00Z")], execs

    def test_promocoes_310_e_317_com_head_no_merge_de_teste_passam(self):
        """#310 e #317: dois PRs da develop, cada um rotulado e mesclado por squash, cada um com um arquivo protegido idêntico ao do
        head rotulado; o CI passa o merge de teste como head, e a cadeia de primeiro pai de base..head era só esse merge."""
        pull, eventos, execs = self.segundo_pr("hooks/conformidade.py", "x = 'mudou no PR 11'\n")
        self.head = self.merge_de_teste()
        r = self.roda(pulls={"10": self.pull, "11": pull}, eventos={"10": self.eventos, "11": eventos}, execucoes={"10": self.execs, "11": execs})
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("mesmo conteúdo já rotulado no PR mesclado #11, #10", r.stdout)

    def test_merge_de_teste_com_merge_fora_da_cadeia_de_primeiro_pai_da_develop_pede(self):
        """O segundo pai do merge de teste é a ponta da develop: o M fora da cadeia de primeiro pai dela segue pedindo o rótulo."""
        self.test_b8_merge_fora_da_cadeia_de_primeiro_pai_pede()
        self.head = self.merge_de_teste()
        self.pede()

    # --- o motivo quando a conferência não libera (antes ela voltava calada) ---------------------------------
    def motivo(self, r):
        linhas = [l for l in r.stdout.splitlines() if l.startswith("catraca: a conferência do PR mesclado não liberou")]
        self.assertEqual(len(linhas), 1, r.stdout)
        self.assertTrue(linhas[0].endswith("vale como sem rótulo."), linhas[0])
        return linhas[0]

    def test_promocao_que_nao_libera_diz_o_motivo_de_cada_pr(self):
        casos = (
            (lambda: setattr(self, "eventos", [rotulo("intrusa")]), "#10: o último evento do rótulo `afrouxa-regra` não é `labeled` pelo dono"),
            (lambda: self.pull.update(merged_at=None), "#10: não foi mesclado ou o merge não está em base..head"),
            (lambda: setattr(self, "execs", []), "#10: sem o head do instante do rótulo"),
        )
        for prepara, esperado in casos:
            with self.subTest(esperado=esperado):
                self.setUp()
                prepara()
                linha = self.motivo(self.pede())
                self.assertIn(esperado, linha)
                self.assertIn("mesma violação para: .github/workflows/ci.yml, tests/catraca.py", linha)
        self.setUp()
        self.depois("tests/catraca.py", ROTULADO + "y = 1\n")  # #10 cobre o ci.yml, não o arquivo mudado depois do merge
        self.assertIn("mesma violação para: tests/catraca.py)", self.motivo(self.pede()))

    def test_merge_fora_da_cadeia_diz_o_motivo(self):
        self.test_b8_merge_fora_da_cadeia_de_primeiro_pai_pede()
        self.assertIn("não é squash na cadeia de primeiro pai de homolog..", self.motivo(self.pede()))

    def test_sem_pr_citado_e_violacao_sem_arquivo_dizem_o_motivo(self):
        self.repo.git("commit", "-q", "--amend", "-m", "feat(x): mudança sem número")
        self.assertIn("nenhum commit de base..head que toca esses arquivos cita um PR", self.motivo(self.pede()))
        self.setUp()
        self.depois("tests/test_x.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
        self.assertIn("há violação que não é \"mudança em <arquivo>\"", self.motivo(self.pede()))

    def test_fora_da_promocao_nao_fala_da_conferencia(self):
        self.pr = {"head": lado("melhoria/x"), "base": lado("develop")}
        self.assertNotIn("conferência do PR mesclado", self.pede().stdout)

    # --- conteúdo alterado pede o rótulo --------------------------------------------------------------------
    def test_b2_push_depois_do_rotulo_pede(self):
        self.final = self.commita_na_fonte("# empurrado depois do rótulo\n", "push depois")
        self.publica(self.final)
        self.m = self.squash("# empurrado depois do rótulo\n")
        self.pull["merge_commit_sha"] = self.m
        self.execs.append(corrida(self.final, "2026-01-02T10:10:00Z", ramo="melhoria/x"))
        self.pede()

    def test_b3_merge_com_conteudo_diferente_do_rotulado_pede_mesmo_se_o_head_volta_ao_rotulado(self):
        """Só `mesmo_arquivo(M, S)` pega: M gravou outra coisa e um commit posterior (sem PR) devolveu o conteúdo rotulado."""
        self.pull["merge_commit_sha"] = self.squash("x = 'misturado com a develop'\n")
        self.depois("tests/catraca.py", ROTULADO, "volta ao rotulado")
        self.pede()

    def test_b17_head_da_promocao_com_uma_linha_a_mais_pede(self):
        self.depois("tests/catraca.py", ROTULADO + "y = 1\n")
        self.pede()

    def test_b12_numero_forjado_no_assunto_pede(self):
        self.pull["merge_commit_sha"] = self.squash("x = 'conteúdo sem rótulo'\n", msg="outra coisa (#10)")
        self.pede()

    # --- o ref buscado -------------------------------------------------------------------------------------
    def test_b4_ref_do_remoto_diferente_do_head_da_api_pede(self):
        outro = self.commita_na_fonte(ROTULADO, "outro commit com o mesmo conteúdo")
        self.publica(outro)  # refs/pull/10/head aponta para `outro`; a API diz que o head é `self.final`
        self.pede()

    def test_b5_head_rotulado_ausente_depois_do_fetch_pede(self):
        fantasma = "0" * 40
        self.execs = [corrida(fantasma, "2026-01-02T09:00:00Z", ramo="melhoria/x"), corrida(fantasma, "2026-01-02T10:00:03Z", ramo="melhoria/x")]
        self.pede()

    def test_b6_fetch_que_falha_pede_com_mensagem(self):
        self.repo.git("remote", "remove", "origin")
        r = self.pede()
        self.assertIn("não consegui buscar refs/pull/10/head", r.stdout)
        self.assertNotIn("Traceback", r.stderr)

    def test_b6_fetch_que_estoura_o_prazo_pede_sem_traceback(self):
        real = catraca.git

        def estoura(raiz, *a):
            if "fetch" in a:
                raise subprocess.TimeoutExpired("git", 60)
            return real(raiz, *a)
        saida = io.StringIO()
        antigo = dict(os.environ)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(antigo)))
        for k in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "HEAD_REF"):
            os.environ.pop(k, None)
        with mock.patch.object(catraca, "git", estoura), contextlib.redirect_stdout(saida):
            rc = catraca.main(self.dados())
        self.assertEqual(rc, 1, saida.getvalue())
        self.assertIn("TimeoutExpired", saida.getvalue())
        self.assertIn("mudança em", saida.getvalue())

    def test_b7_head_rotulado_que_nao_e_ancestral_do_head_final_pede(self):
        """Execução de outra branch de mesmo nome: S tem o mesmo blob, mas não é do histórico do head da API."""
        _g(self.clone.name, "checkout", "-q", "--orphan", "outra")
        outro_s = self.commita_na_fonte(ROTULADO, "outro histórico")
        _g(self.clone.name, "push", "-q", "-f", self.bare.name, f"{outro_s}:refs/heads/outra")
        self.repo.git("fetch", "-q", "origin", "refs/heads/outra:refs/heads/outra")  # S local: o fetch do PR só traz o head final
        self.execs = [corrida(outro_s, "2026-01-02T09:00:00Z", ramo="melhoria/x"), corrida(outro_s, "2026-01-02T10:00:03Z", ramo="melhoria/x")]
        self.assertTrue(_tem(self.repo.dir, outro_s))
        self.pede()

    def test_b14_o_fetch_nao_escreve_em_refs_existentes(self):
        self.repo.git("update-ref", "refs/remotes/origin/develop", "base")
        self.repo.git("tag", "v1", "base")
        antes = self.repo.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes", "refs/tags")
        self.assertEqual(self.roda().returncode, 0)
        depois = self.repo.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes", "refs/tags")
        self.assertEqual(depois, antes)
        self.assertFalse((self.repo.dir / ".git" / "FETCH_HEAD").exists())

    def test_m1_fetch_so_com_a_refspec_explicita_do_pr(self):
        fetches = []
        real = catraca.git
        antigo = dict(os.environ)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(antigo)))
        with mock.patch.object(catraca, "git", lambda raiz, *a: (fetches.append(a) if "fetch" in a else None) or real(raiz, *a)), \
                contextlib.redirect_stdout(io.StringIO()):
            catraca.main(self.dados())
        self.assertEqual(len(fetches), 1, fetches)
        a = fetches[0]
        self.assertEqual(a[a.index("fetch"):], ("fetch", "--no-tags", "--no-recurse-submodules", "--no-write-fetch-head", "origin",
                                                "refs/pull/10/head:refs/catraca/pull/10"))

    def test_sem_head_sha_da_api_pede(self):
        for sha in (None, "", "abc", 7):
            with self.subTest(sha=sha):
                self.final = sha
                self.pede()

    # --- a prova do squash só vale para squash --------------------------------------------------------------
    def test_dois_squash_do_mesmo_conteudo_sem_espera_dao_shas_diferentes(self):
        self.assertNotEqual(self.squash(ROTULADO), self.m)

    def test_b8_merge_fora_da_cadeia_de_primeiro_pai_pede(self):
        self.repo.git("checkout", "-q", "-b", "lateral", "base")
        m = self.pull["merge_commit_sha"] = self.squash(ROTULADO)  # M do pull, na `develop`
        self.assertNotEqual(m, self.m)
        self.repo.git("branch", "-f", "lateral", m)
        self.repo.git("checkout", "-q", "develop")
        self.repo.git("reset", "-q", "--hard", "base")
        self.depois("docs/outra.md", "outra\n")
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge lateral", "lateral")
        self.assertIn(m, self.repo.git("rev-list", "homolog..develop").split())
        self.assertNotIn(m, self.repo.git("rev-list", "--first-parent", "homolog..develop").split())
        self.pede()

    def test_b9_merge_com_dois_pais_e_s_fora_da_ancestralidade_pede(self):
        self.repo.git("checkout", "-q", "-b", "lado", "base")
        self.depois("tests/catraca.py", ROTULADO)
        self.depois(".github/workflows/ci.yml", WORKFLOW)
        self.repo.git("checkout", "-q", "develop")
        self.repo.git("reset", "-q", "--hard", "base")
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #10 from o/melhoria/x", "lado")
        self.pull["merge_commit_sha"] = self.repo.git("rev-parse", "HEAD").strip()
        self.assertEqual(len(self.repo.git("rev-list", "--parents", "-n", "1", "HEAD").split()), 3)
        self.pede()

    # --- os filtros da S-16 seguem como eram ---------------------------------------------------------------
    def test_b10_fork_ou_outra_base_com_squash_pede(self):
        for chave, valor in (("base", lado("outra")), ("base", lado("develop", "fork/r")), ("head", dict(lado("melhoria/x", "fork/r"), sha=self.s))):
            with self.subTest(chave=chave):
                self.pede(pulls={"10": dict(self.pull, **{chave: valor})})

    def test_b11_pr_fechado_sem_merge_pede(self):
        self.pull["merged_at"] = None
        self.pede()

    def test_b13_force_push_entre_o_rotulo_e_o_merge_pede(self):
        self.eventos = [rotulo(), {"event": "head_ref_force_pushed", "created_at": "2026-01-02T10:05:00Z"}]
        self.pede()

    def test_b15_violacao_sem_arquivo_e_custo_pedem_sempre(self):
        self.depois("tests/test_x.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
        self.assertIn("testes `test_*` caíram", self.pede().stdout)
        self.repo.git("reset", "-q", "--hard", self.m)
        self.depois("scripts/x.sh", "export ANTHROPIC_API_KEY=1\n")
        self.assertIn("R-CUSTO:", self.pede().stdout)

    def test_b16_rotulo_de_outra_conta_ou_por_app_ou_sem_dono_pede(self):
        app = dict(rotulo(), performed_via_github_app={"slug": "x"})
        for eventos in ([rotulo("intrusa")], [app], [rotulo(), rotulo(quando="2026-01-02T11:00:00Z", tipo="unlabeled")]):
            with self.subTest(eventos=eventos):
                self.eventos = eventos
                self.pede()
        fonte = catraca.FonteJson({"repo": REPO_GH, "pr": self.pr, "pulls": {"10": self.pull}, "eventos": {"10": self.eventos},
                                   "execucoes": {"10": self.execs}})
        viol = catraca.violacoes_das_regras(self.repo.dir, "homolog", "develop")
        self.assertIsNone(catraca.liberado_por_pr_mesclado(self.repo.dir, "homolog", "develop", viol, fonte, None))


class DonoSoDaBase(Base):
    """S-16 E4: o dono vem só do tests/config.json da base; sem ele, nenhum rótulo vale (o head é do autor)."""

    def test_base_sem_config_falha_fechado_mesmo_com_dono_no_head(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.git("rm", "-q", "tests/config.json")
        self.repo.git("commit", "-q", "-m", "sem config")
        self.repo.git("tag", "-f", "base")
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("reset", "-q", "--hard", "develop")
        self.repo.escreve("tests/config.json", json.dumps(CONFIG))  # o head traz `dono: dona`
        self.repo.escreve("tests/catraca.py", "x = 'mudou'\n")
        self.repo.commit()
        arq = self.repo.dir.parent / (self.repo.dir.name + "-eventos.json")
        arq.write_text(json.dumps([rotulo()]), encoding="utf-8")
        self.addCleanup(arq.unlink, missing_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY")}
        r = subprocess.run(["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "base", "--eventos", str(arq),
                            "--ultimo-push", "2026-01-02T09:00:00Z"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("mudança em tests/catraca.py", r.stdout)


class PrazoTotalDaApi(Base):
    """Item 4 do N-CAT1: um prazo total para as chamadas à API, num relógio monotônico; estourou, vale como sem rótulo."""

    ENV = {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PR_NUMBER": "11", "HEAD_SHA": "abc"}

    def setUp(self):
        super().setUp()
        patch = mock.patch.dict(os.environ, self.ENV)
        patch.start()
        self.addCleanup(patch.stop)
        self.agora = 0.0
        for alvo, valor in (("relogio", lambda: self.agora), ("urlopen", self.urlopen)):
            patch = mock.patch.object(catraca if alvo == "relogio" else catraca.urllib.request, alvo, valor)
            patch.start()
            self.addCleanup(patch.stop)
        self.chamadas, self.salto, self.resposta = [], 0.0, []
        catraca.PRAZO.reiniciar()
        self.addCleanup(catraca.PRAZO.reiniciar)

    def urlopen(self, req, timeout=None):
        self.chamadas.append((req.full_url, timeout))
        self.agora += self.salto
        corpo = json.dumps(self.resposta(req.full_url) if callable(self.resposta) else self.resposta).encode()
        return contextlib.nullcontext(io.BytesIO(corpo))

    def test_o_prazo_total_cabe_na_metade_do_timeout_do_job(self):
        """Se o N-CI baixar o `timeout-minutes` do job `catraca`, a suíte acusa."""
        yml = (AQUI.parent / ".github" / "workflows" / "catraca.yml").read_text(encoding="utf-8")
        job = re.search(r"^  catraca:\n(.*?)(?=^  \S|\Z)", yml, re.M | re.S).group(1)
        minutos = int(re.search(r"^    timeout-minutes: (\d+)\s*$", job, re.M).group(1))
        self.assertLessEqual(catraca.PRAZO_TOTAL_DA_API, minutos * 60 / 2)
        self.assertGreater(catraca.PRAZO_TOTAL_DA_API, 0)

    def test_a_excecao_do_prazo_e_oserror(self):
        """Assim as capturas que já existem a tratam como sem rótulo."""
        self.assertTrue(issubclass(catraca.PrazoDaApiEsgotado, OSError))

    def test_prazo_esgotado_nao_chama_a_rede_e_a_fonte_devolve_none(self):
        self.salto = 150.0
        fonte = catraca.FonteGithub("t", "o/r", "11")
        self.assertEqual(fonte.pull(1), [])
        self.assertEqual(fonte.pull(2), [])
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            self.assertIsNone(fonte.pull(3))
            self.assertIsNone(fonte.pull(4))
        self.assertEqual(len(self.chamadas), 2, self.chamadas)
        self.assertEqual(saida.getvalue().count("prazo da API esgotado; vale como sem rótulo."), 1, saida.getvalue())

    def test_o_prazo_de_cada_chamada_e_o_menor_entre_30_e_o_que_resta(self):
        catraca.requisicao("/a", "t")
        self.agora = catraca.PRAZO_TOTAL_DA_API - 12.5
        catraca.requisicao("/b", "t")
        self.assertEqual([t for _, t in self.chamadas], [30, 12.5])

    def test_o_relogio_comeca_na_primeira_chamada(self):
        self.agora = 1000.0
        catraca.requisicao("/a", "t")
        self.agora = 1000.0 + catraca.PRAZO_TOTAL_DA_API - 1
        catraca.requisicao("/b", "t")
        self.assertEqual(len(self.chamadas), 2)

    def test_promocao_com_o_prazo_esgotado_para_de_consultar_e_deixa_rc_1(self):
        """O caminho da S-16 (um PR candidato por commit citado) não pode consumir os 10 minutos do job."""
        self.repo.git("branch", "main", "base")
        self.repo.git("checkout", "-q", "-b", "homolog", "base")
        for n in range(21, 31):
            self.repo.escreve("tests/catraca.py", f"x = 'mudou {n}'\n")
            self.repo.git("add", "-A")
            self.repo.git("commit", "-q", "-m", f"fix: mudança (#{n})")
        pr = {"head": {"ref": "develop", "repo": {"full_name": "o/r"}}, "base": {"ref": "homolog", "repo": {"full_name": "o/r"}}}
        self.resposta = lambda url: pr if url.endswith("/pulls/11") else ({"workflow_runs": []} if "runs" in url else [])
        self.salto = 100.0
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(["--raiz", str(self.repo.dir), "--base", "main", "--head", "homolog"])
        self.assertEqual(rc, 1, saida.getvalue())
        self.assertIn("mudança em tests/catraca.py", saida.getvalue())
        self.assertEqual(len(self.chamadas), 3, self.chamadas)
        self.assertEqual(saida.getvalue().count("prazo da API esgotado; vale como sem rótulo."), 1, saida.getvalue())


class FonteDoGithub(unittest.TestCase):
    """S-16: as consultas dos PRs mesclados (só leitura, gratuitas) e a falha fechada sem token, com erro ou além do teto."""

    def setUp(self):
        self.antigo = dict(os.environ)
        self.original = catraca.requisicao
        self.addCleanup(lambda: setattr(catraca, "requisicao", self.original))
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(self.antigo)))

    def test_sem_token_repositorio_ou_numero_e_none(self):
        for k in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER"):
            os.environ.update({"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PR_NUMBER": "7"})
            del os.environ[k]
            self.assertIsNone(catraca.fonte_do_github(), k)

    def test_consultas_e_teto_de_paginas(self):
        chamadas = []
        catraca.requisicao = lambda caminho, token: chamadas.append(caminho) or ({"workflow_runs": []} if "runs" in caminho else [])
        f = catraca.FonteGithub("t", "o/r", "7")
        pull = {"created_at": "2026-01-02T08:00:00Z", "merged_at": "2026-01-02T10:30:00Z", "head": {"ref": "melhoria/a"}}
        self.assertEqual(f.eventos(10), [])
        self.assertEqual(f.execucoes(10, pull), [])
        self.assertEqual(chamadas, ["/repos/o/r/issues/10/events?per_page=100&page=1",
                                    "/repos/o/r/actions/runs?event=pull_request&branch=melhoria%2Fa"
                                    "&created=2026-01-02T08%3A00%3A00Z..2026-01-02T10%3A30%3A00Z&per_page=100&page=1"])
        catraca.requisicao = lambda caminho, token: [{}] * 100
        self.assertIsNone(f.eventos(10))  # lista além do teto não decide nada
        self.assertIsNone(catraca.api_com_teto("/x", "t", teto=5))

    def test_falha_da_api_e_none(self):
        def falha(*a, **k):
            raise OSError("limite de taxa")
        catraca.requisicao = falha
        f = catraca.FonteGithub("t", "o/r", "7")
        self.assertIsNone(f.pull(10))
        self.assertIsNone(f.pr_atual())
        self.assertIsNone(f.eventos(10))
        self.assertIsNone(f.execucoes(10, {"created_at": "a", "merged_at": "b", "head": {"ref": "x"}}))

    def test_resposta_cortada_da_api_e_none(self):
        """M5: `http.client.IncompleteRead` não é `OSError`; sem captura sairia por traceback."""
        def corta(*a, **k):
            raise http.client.IncompleteRead(b"")
        catraca.requisicao = corta
        self.assertIsNone(catraca.FonteGithub("t", "o/r", "7").pull(10))


class Workflows(unittest.TestCase):
    """Reviews 3, 6, 9, 10 e 14: o que os workflows prometem, conferido no texto (sem rede)."""
    RAIZ = AQUI.parent / ".github"

    def texto(self, nome):
        return (self.RAIZ / "workflows" / nome).read_text(encoding="utf-8")

    def test_rotulo_e_edicao_so_disparam_a_catraca(self):
        ci, ct = self.texto("ci.yml"), self.texto("catraca.yml")
        self.assertIn("types: [opened, synchronize, reopened]", ci)
        for evento in ("labeled", "unlabeled", "edited"):
            self.assertNotIn(evento, ci.split("jobs:")[0].replace("rótulo e edição", ""))
            self.assertIn(evento, ct.split("jobs:")[0])
        self.assertRegex(ct, r"(?m)^  catraca:")
        self.assertIn("--modo pr-texto", ct)  # o texto do PR é um passo do job catraca (um job só: o GitHub cobra por minuto cheio)
        self.assertNotRegex(ct, r"(?m)^  pr-texto:")
        self.assertNotRegex(ci, r"(?m)^  (catraca|pr-texto):")

    def test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore(self):
        """Economia de minutos: passos da bateria num job, push na develop só com a checagem rápida, timeout em todo job."""
        for nome in ("ci.yml", "catraca.yml", "release.yml"):
            texto = self.texto(nome)
            jobs = len(re.findall(r"(?m)^  [a-z-]+:\n    (?:name|if|runs-on):", texto))
            self.assertEqual(texto.count("timeout-minutes:"), jobs, nome)
            self.assertNotIn("paths-ignore", texto.replace("`paths-ignore`", "").replace("nunca paths-ignore", ""), nome)
        ci = self.texto("ci.yml")
        self.assertIn("if: github.event_name != 'push' || github.ref != 'refs/heads/develop'", ci)  # bateria fora do push na develop
        self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/develop'", ci)
        self.assertRegex(ci, r"(?m)^  bateria:")
        self.assertIn("docs/(reviews|qa|security|devops|ux)/", ci)
        # Teto de tempo (ci-suite-no-teto; SUITE-NO-CI): as duas checagens rápidas (3.12 e 3.14, SP4) 30 min (CI-TEMPO-314: medido 13-20 min, a 3.14 batia nos 20); cada parte da suíte (3.12 e 3.14) 20 min;
        # instalação no 3.14 15 min; o teto de pulados de cada versão (T3, 0.43.2) 5 min; passos da bateria 20 min; verificações longas (shellcheck, Provas, e2e; #493) 20 min; os dois agregadores 5 min;
        # o job de pareceres (v047 E1.18, J9) 5 min; o job prévio da árvore (M2, 0.43.4), antes das partes, 5 min.
        self.assertEqual(re.findall(r"timeout-minutes: (\d+)", ci), ["30", "30", "45", "5", "20", "20", "15", "5", "5", "5", "20", "5", "20", "5"])

    def test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde(self):
        """Review independente: renomeação, testes de pareceres, check forjado, cancelamento e promoção."""
        ci = self.texto("ci.yml")
        self.assertIn("git diff --name-only --no-renames", ci)  # renomear código para docs/reviews não pode esconder a origem
        # Execução cancelada não gasta os minutos que o gate poupa: always() só no if dos dois agregadores (SUITE-NO-CI),
        # que não fazem checkout e só conferem o resultado dos jobs necessários (cancelado ou pulado reprova).
        agregadores = "    if: always() && (github.event_name != 'push' || github.ref != 'refs/heads/develop')\n"
        self.assertEqual(ci.count("always()"), ci.count(agregadores) + ci.count("always():"), "always() fora do if de agregador")
        self.assertEqual(ci.count(agregadores), 2)
        self.assertNotIn("always()", self.texto("catraca.yml"))
        self.assertIn("!cancelled()", ci)
        self.assertIn('[ "$BASE_REF" = develop ]', ci)  # promoção para a homolog roda a bateria completa (R-FLUXO)
        self.assertIn('.app.slug == "github-actions"', ci)
        self.assertIn("sort_by(.started_at) | last", ci)
        leve = re.search(r"(?m)^      - name: Testes que leem pareceres.*?\n        run: (.*)$", ci, re.S)
        self.assertIsNotNone(leve, "commit só de parecer ainda roda os testes que leem docs/reviews e docs/qa")
        for classe in ("Neutralidade", "Referencias", "AntiDuplicacao", "NeutralidadeDoNucleo"):  # a última varre docs/security e docs/devops
            self.assertIn("tests.test_forge." + classe + " ", leve.group(1).splitlines()[0] + " ")
        self.assertIn("steps.gate.outputs.pesada != 'true'", ci)

    def test_checkout_sem_credencial_e_sem_pull_request_target(self):
        for nome in ("ci.yml", "catraca.yml"):
            texto = self.texto(nome)
            self.assertNotIn("pull_request_target", texto)
            self.assertEqual(texto.count("actions/checkout@"), texto.count("persist-credentials: false"), nome)

    def test_catraca_e_pareceres_usam_a_base_do_merge_e_o_script_da_base(self):
        for nome, trecho in (("ci.yml", "--modo pareceres"), ("catraca.yml", 'python3 "$script" --base')):
            texto = self.texto(nome)
            self.assertIn("BASE=$(git rev-parse HEAD^1)", texto)
            self.assertIn('git cat-file -e "$BASE:tests/catraca.py"', texto)
            self.assertIn('script="$RUNNER_TEMP/base/tests/catraca.py"', texto)
            self.assertIn(trecho, texto)
        self.assertNotIn("base.sha", self.texto("catraca.yml"))
        self.assertIn('--ramo="$HEAD_REF"', self.texto("ci.yml"))
        self.assertIn("HEAD_SHA:", self.texto("catraca.yml"))

    def test_dependabot_vai_para_a_develop(self):
        self.assertIn("target-branch: develop", (self.RAIZ / "dependabot.yml").read_text(encoding="utf-8"))


class GateDoCi(unittest.TestCase):
    """VEL-P6-GATE: o passo Gate do ci.yml executado de verdade (bash -e, como o GitHub), num repositório temporário,
    com um gh falso que só dá a bateria verde para o commit anterior exato."""

    def setUp(self):
        ci = (Workflows.RAIZ / "workflows" / "ci.yml").read_text(encoding="utf-8")
        bloco = re.search(r"(?m)^        id: gate\n.*?^        run: \|\n((?:          [^\n]*\n|\n)+)", ci, re.S)
        self.assertIsNotNone(bloco, "passo Gate do ci.yml não achado")
        self.script = textwrap.dedent(bloco.group(1))
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "bin").mkdir()
        gh = self.tmp / "bin" / "gh"
        gh.write_text('#!/bin/sh\n[ "$1 $2" = "api repos/o/r/commits/$ANTES/check-runs?per_page=100" ] && [ -n "$VERDE" ]'
                      ' && { echo 1; exit 0; }\necho 0\n', encoding="utf-8")
        gh.chmod(0o755)
        self.repo = self.tmp / "r"
        self.env = sem_manutencao({"PATH": f"{self.tmp / 'bin'}:/usr/bin:/bin", "HOME": str(self.tmp),
                                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C"})
        self.repo.mkdir()
        self.git("init", "-q")
        self.versao = 0
        self.commit(["README.md"])

    def git(self, *args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.repo,
                              env=self.env, check=True, capture_output=True, text=True, timeout=30).stdout.strip()

    def commit(self, arquivos):
        self.versao += 1
        for rel in arquivos:
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / rel).write_text(f"{rel} {self.versao}\n", encoding="utf-8")
            self.git("add", "--", rel)
        self.git("commit", "-qm", "c")
        return self.git("rev-parse", "HEAD")

    def pesada(self, arquivos, verde=True):
        antes = self.git("rev-parse", "HEAD")
        depois = self.commit(arquivos)
        saida = self.tmp / "saida"
        env = dict(self.env, EVENTO="pull_request", BASE_REF="develop", ACAO="synchronize", ANTES=antes, HEAD_SHA=depois,
                   REPO="o/r", GITHUB_OUTPUT=str(saida), GITHUB_STEP_SUMMARY=os.devnull, **({"VERDE": "1"} if verde else {}))
        subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", self.script], cwd=self.repo, env=env, check=True,
                       capture_output=True, text=True, timeout=30)
        return saida.read_text(encoding="utf-8").splitlines()[-1]

    def test_so_parecer_de_seguranca_devops_ou_ux_com_bateria_verde_pula(self):
        for pasta in ("reviews", "qa", "security", "devops", "ux"):
            with self.subTest(pasta=pasta):
                self.assertEqual(self.pesada([f"docs/{pasta}/p1.md"]), "pesada=false")

    def test_parecer_misturado_com_codigo_nao_pula(self):
        for outro in ("bin/forge-check", "docs/regras/R-X.md", "docs/uxx/p1.md", "vendor/docs/ux/p1.md"):
            with self.subTest(outro=outro):
                self.assertEqual(self.pesada(["docs/security/p1.md", outro]), "pesada=true")

    def test_sem_bateria_verde_no_commit_anterior_nao_pula(self):
        for pasta in ("security", "devops", "ux"):
            with self.subTest(pasta=pasta):
                self.assertEqual(self.pesada([f"docs/{pasta}/p1.md"], verde=False), "pesada=true")

    def test_modelo_e_ameacas_e_aceites_nao_sao_parecer(self):
        for rel in ("docs/security/_modelo.md", "docs/ux/_modelo.md", "docs/reviews/_modelo.md",
                    "docs/security/ameacas/p1.md", "docs/security/aceites/p1.md"):
            with self.subTest(rel=rel):
                self.assertEqual(self.pesada([rel]), "pesada=true")


class FormaCompiladaDosControles(Base):
    """Item 6 do N-CAT1 (K10-CAT): a forma compilada (`__pycache__/`, `.pyc`, `.pyo`, `.pyd`, `.so`) troca o fonte sem o fonte
    mudar; por isso, em qualquer pasta, pede o rótulo do dono como qualquer arquivo protegido."""

    COMPILADOS = ("hooks/__pycache__/_comum.cpython-312.pyc", "hooks/_comum.cpython-312-x86_64-linux-gnu.so", "hooks/_comum.abi3.so",
                  "hooks/conformidade.abi3.so", "tests/__pycache__/neutralidade.cpython-312.pyc", "bin/__pycache__/x.pyc",
                  "hooks/agentes.pyd", "hooks/sub/x.pyo", "__pycache__/x.txt", "x.pyc")

    def test_forma_compilada_pede_o_rotulo(self):
        for rel in self.COMPILADOS:
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, "binario\n")
                repo.commit()
                achadas = repo.violacoes()
                self.assertEqual(len(achadas), 1, achadas)
                self.assertTrue(achadas[0].startswith("R-CONFORMIDADE: ") and f"mudança em {rel}" in achadas[0], achadas)

    def test_prefixo_ja_protegido_nao_conta_duas_vezes(self):
        self.repo.escreve("hooks/_comum.pyc", "binario\n")
        self.repo.commit()
        self.assertEqual(len(self.repo.violacoes()), 1, self.repo.violacoes())

    def test_apagar_ou_mover_a_forma_compilada_tambem_pede(self):
        self.repo.escreve("hooks/__pycache__/x.pyc", "binario\n")
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "tinha")
        self.repo.git("tag", "-f", "base")
        self.repo.git("rm", "-q", "hooks/__pycache__/x.pyc")
        self.barra("mudança em hooks/__pycache__/x.pyc", "R-CONFORMIDADE")

    def test_o_rotulo_do_dono_libera_como_a_qualquer_protegido(self):
        self.repo.escreve("hooks/__pycache__/_comum.cpython-312.pyc", "binario\n")
        self.repo.commit()
        eventos = self.repo.dir.parent / (self.repo.dir.name + "-compilado-eventos.json")
        eventos.write_text(json.dumps([{"event": "labeled", "label": {"name": catraca.ROTULO}, "actor": {"login": "dona"},
                                        "created_at": "2026-01-02T10:00:00Z"}]), encoding="utf-8")
        self.addCleanup(eventos.unlink)
        argv = ["--raiz", str(self.repo.dir), "--base", "base", "--eventos", str(eventos), "--ultimo-push", "2026-01-02T09:00:00Z"]
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            self.assertEqual(catraca.main(argv), 0, saida.getvalue())
            self.assertEqual(catraca.main(argv[:4]), 1)

    def test_ancora_e_extensao_nao_pegam_nome_parecido(self):
        for rel in ("docs/notas.so.md", "src/pycache/x.txt", "src/__pycache__x/y.txt", "docs/x.pyc.md"):
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, "texto\n")
                repo.commit()
                self.assertEqual(repo.violacoes(), [])

    def test_nenhum_arquivo_versionado_da_arvore_real_tem_forma_compilada(self):
        """Medido: 0 (M3). A catraca só vê o que o PR muda; isto pega o que já está na árvore."""
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        r = subprocess.run(["git", "-C", str(AQUI.parent), "ls-files"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        arquivos = r.stdout.splitlines()
        self.assertGreater(len(arquivos), 100)
        self.assertEqual([a for a in arquivos if catraca.FORMA_COMPILADA.search(a)], [])


if __name__ == "__main__":
    unittest.main()


class ExcecaoDoAcrescimoNaAdr(unittest.TestCase):
    def test_adr_0008_registra_a_excecao_da_m9_e_o_que_continua_pedindo(self):
        texto = (AQUI.parent / catraca.ADR).read_text(encoding="utf-8")
        self.assertIn("**Exceção estreita da M9", texto)
        trecho = texto[texto.index("**Exceção estreita da M9"):]
        trecho = trecho[:trecho.index("\n")]
        for esperado in ("S1: a árvore de sintaxe é igual", "S2:", "MONOTONICAS", "falha fechada", "função de topo nova", "linha removida ou alterada", "outra linguagem",
                         "um `return` novo no começo de uma função de checagem", "modelo de ameaças", "decisão do dono",
                         "tests/fixtures/afrouxamentos/", "A forma compilada não entra", "a linha `#!` não é comentário"):
            self.assertIn(esperado, trecho)


class RotuladosDaLeva(Base):
    """ACELERA-P3 (c), E2-1: `rotulados_da_leva` lista os PRs rotulados da leva com a decisão declarada (C-3 a C-6, 0.40)."""

    def setUp(self):
        super().setUp()
        self.repo.git("checkout", "-q", "develop")
        self.pulls, self.eventos = {}, {}

    def mescla(self, n, corpo="", eventos=(rotulo(),), assunto="Merge pull request #{} from o/x", **pull):
        self.repo.git("commit", "-q", "--allow-empty", "-m", assunto.format(n))
        sha = self.repo.git("rev-parse", "HEAD").strip()
        self.pulls[str(n)] = {"merged_at": "2026-01-02T10:30:00Z", "merge_commit_sha": sha, "body": corpo, "base": lado("develop"), "head": lado(f"x{n}"), **pull}
        self.eventos[str(n)] = list(eventos)
        return sha

    def lista(self, base="base", dono="dona"):
        fonte = catraca.FonteJson({"repo": REPO_GH, "pr": {"head": lado("develop"), "base": lado("homolog")}, "pulls": self.pulls, "eventos": self.eventos})
        return catraca.rotulados_da_leva(self.repo.dir, base, "develop", fonte, dono)

    def test_com_e_sem_linha_de_decisao_e_sem_rotulo(self):
        self.mescla(10, "x\n<!--\nRótulo: DECISÃO DO DONO falsa -->\n  Rótulo: DECISÃO DO DONO (2026-11-06): \"A\"\nRótulo: DECISÃO DO DONO 2")
        self.mescla(11, None)
        self.mescla(12, eventos=())
        linhas = self.lista()
        self.assertIn("confere só o rótulo do dono; a decisão é a que o autor declarou", linhas[0])
        self.assertIn('rotulados: #10 · rótulo do dono · decisão declarada no corpo: `Rótulo: DECISÃO DO DONO (2026-11-06): "A"`', linhas)
        self.assertIn("rotulados: #11 · rótulo do dono · sem linha de decisão no corpo", linhas)
        self.assertFalse([l for l in linhas if "#12" in l], linhas)

    def test_fora_da_leva_nao_sai(self):
        self.mescla(20, merge_commit_sha="0" * 40)
        self.mescla(21, base=lado("main"))
        self.mescla(22, head=lado("x", "f/r"))
        self.mescla(23, base=lado("develop", "f/r"))
        self.mescla(24, merged_at=None)
        self.mescla(25)
        self.assertEqual([l for l in self.lista() if "#2" in l], ["rotulados: #25 · rótulo do dono · sem linha de decisão no corpo"])

    def test_rotulo_de_outro_ator_de_app_ou_retirado_nao_e_do_dono(self):
        self.mescla(30, eventos=[rotulo("outro")])
        self.mescla(31, eventos=[{**rotulo(), "performed_via_github_app": {"slug": "app"}}])
        self.mescla(32, eventos=[rotulo(), rotulo(quando="2026-01-02T11:00:00Z", tipo="unlabeled")])
        self.assertEqual([l for l in self.lista() if "#3" in l], [f"rotulados: #{n} · rótulo não é do dono" for n in (32, 31, 30)])

    def test_limite_de_candidatos_diz_incompleta(self):
        for n in range(100, 100 + catraca.LIMITE_CANDIDATOS):
            self.mescla(n)
        self.assertFalse([l for l in self.lista() if "incompleta" in l])
        self.mescla(500)
        linhas = self.lista()
        self.assertTrue([l for l in linhas if l.startswith("rotulados: incompleta (limite)")], linhas)
        self.assertNotIn("rotulados: #100 · rótulo do dono · sem linha de decisão no corpo", linhas)  # o mais antigo fica de fora

    def test_commits_sem_numero_sao_contados_com_o_sha7(self):
        shas = [self.mescla(n, assunto="push direto") for n in (40, 41)]
        self.mescla(42)
        self.assertIn(f"rotulados: commits de primeiro pai sem #n em base..head: 2 {shas[1][:7]} {shas[0][:7]}", self.lista())

    def test_corpo_com_link_imagem_html_e_barra_sai_em_codigo_inline(self):
        self.mescla(50, "Rótulo: DECISÃO DO DONO [x](https://e.vil) ![](https://e.vil/p.png) <b>x</b> | y`z ｜w")
        linha = [l for l in self.lista() if "#50" in l][0]
        self.assertTrue(linha.endswith("corpo: `Rótulo: DECISÃO DO DONO [x](https://e.vil) ![](https://e.vil/p.png) <b>x</b>  yz w`"), linha)

    def test_corpo_com_comando_de_workflow_e_controle_sai_numa_linha_limpa(self):
        self.mescla(60, "Rótulo: DECISÃO DO DONO a\u202e:\u200b:add-mask:::x\ue000\n::stop-commands::y")
        self.mescla(61, "Rótulo: DECISÃO DO DONO " + "z" * 300)
        linhas = self.lista()
        self.assertIn("rotulados: #60 · rótulo do dono · decisão declarada no corpo: `Rótulo: DECISÃO DO DONO a:add-mask:x`", linhas)
        self.assertIn(f"corpo: `{('Rótulo: DECISÃO DO DONO ' + 'z' * 300)[:200]}`", [l for l in linhas if "#61" in l][0])
        self.assertFalse([l for l in linhas if "::" in l or "\u202e" in l], linhas)

    def test_falha_da_api_do_git_ou_sem_dono_diz_incompleta(self):
        self.mescla(70)
        self.mescla(71)
        del self.pulls["70"]
        self.eventos["71"] = {}
        linhas = self.lista()
        self.assertIn("rotulados: incompleta (a API não devolveu o #70)", linhas)
        self.assertIn("rotulados: incompleta (a API não devolveu os eventos do #71)", linhas)
        self.assertEqual(self.lista(base="nao-existe")[1:], ["rotulados: incompleta (git)"])
        for sem_pr_ou_dono in (self.lista(dono=""), catraca.rotulados_da_leva(self.repo.dir, "base", "develop", None, "dona")):
            self.assertEqual(sem_pr_ou_dono[1:], ["rotulados: incompleta (sem o PR atual ou o dono)"])

    # --- E2-2: a ligação em `main` (só informa, C-1, C-2) e o modo local `rotulados` (C-7) ------------------
    def roda(self, *extra, pr=None, env=None):
        """`catraca.main` no PR `pr` (padrão: develop -> homolog) com a fonte em `self.arq`; devolve (rc, stdout, resumo)."""
        self.arq, resumo = (self.repo.dir.parent / f"{self.repo.dir.name}-{nome}" for nome in ("mesclados.json", "resumo.md"))
        self.arq.write_text(json.dumps({"repo": REPO_GH, "pr": pr or {"head": lado("develop"), "base": lado("homolog")},
                                        "pulls": self.pulls, "eventos": self.eventos}), encoding="utf-8")
        resumo.write_text("", encoding="utf-8")
        self.addCleanup(lambda: [f.unlink(missing_ok=True) for f in (self.arq, resumo)])
        limpo = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER", "HEAD_REF")}
        argv = ["--raiz", str(self.repo.dir), "--base", "base", "--head", "develop", *(extra or ("--mesclados", str(self.arq)))]
        with mock.patch.dict(os.environ, {**limpo, "GITHUB_STEP_SUMMARY": str(resumo), **(env or {})}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()) as saida:
            rc = catraca.main(argv)
        return rc, saida.getvalue(), resumo.read_text(encoding="utf-8")

    def test_a_lista_so_informa_rc_e_saida_iguais_com_e_sem_ela(self):
        """C-1 e caso de abuso 3: com a lista, sem ela e com KeyError no 2.º PR, o rc e a saída são os mesmos, menos `rotulados:`."""
        self.mescla(80, 'Rótulo: DECISÃO DO DONO (2026-11-06): "A"')
        self.mescla(81)
        for rc_esperado in (0, 1):
            if rc_esperado:  # invariante removido, sem rótulo: rc 1
                self.repo.config(invariantes={"docs/regra.md": []})
                self.repo.commit()
            com = self.roda()
            with mock.patch.object(catraca, "lista_de_rotulados", return_value=[]):
                sem = self.roda()
            with mock.patch.object(catraca.FonteJson, "eventos", side_effect=[self.eventos["81"], KeyError("80")]):
                falha = self.roda()
            self.assertIn('rotulados: #80 · rótulo do dono · decisão declarada no corpo: `Rótulo: DECISÃO DO DONO (2026-11-06): "A"`', com[1])
            self.assertIn("\n- rotulados: #81 · rótulo do dono · sem linha de decisão no corpo\n", com[2])
            self.assertIn("rotulados: incompleta (KeyError)", falha[1].splitlines())
            self.assertNotIn("rotulados", sem[1] + sem[2])
            for rc, saida, resumo in (com, sem, falha):
                self.assertEqual(rc, rc_esperado, saida)
                self.assertEqual([l for l in saida.splitlines() if not l.startswith("rotulados:")], sem[1].splitlines())
                self.assertEqual(resumo.split("### rotulados")[0], sem[2])

    def test_fora_de_promocao_nada_e_listado(self):
        self.mescla(85)
        for pr in ({"head": lado("x"), "base": lado("develop")}, {"head": lado("develop", "f/r"), "base": lado("homolog")}):
            rc, saida, resumo = self.roda(pr=pr)
            self.assertEqual((rc, "rotulados" in saida + resumo), (0, False), saida)
            self.assertIn("rotulados: o PR não é promoção", self.roda("--modo", "rotulados", "--mesclados", str(self.arq), pr=pr)[1])
        self.assertEqual(self.roda("--pr", "7")[1], "")  # sem a fonte da API (sem token): nada

    def test_prazo_esgotado_na_liberacao_diz_incompleta_sem_nova_chamada(self):
        """Caso de abuso 8 (C-2): com a fonte da API e o prazo esgotado na liberação, a lista não chama a API de novo."""
        self.repo.config(invariantes={"docs/regra.md": []})
        self.repo.commit()
        for fonte in ((), ("--mesclados", str(self.repo.dir.parent / f"{self.repo.dir.name}-mesclados.json"))):  # da API e em JSON
            with mock.patch.object(catraca, "relogio", side_effect=itertools.chain([0], itertools.repeat(10 ** 6))), \
                    mock.patch("urllib.request.urlopen") as rede:
                rc, saida, _ = self.roda("--pr", "7", *fonte, env={"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": REPO_GH, "PR_NUMBER": "7", "HEAD_SHA": "a" * 40})
            self.assertEqual((rc, rede.call_count, saida.count("prazo da API esgotado")), (1, 0, 1), saida)
            self.assertIn("rotulados: incompleta (prazo)", saida.splitlines())

    def test_modo_local_so_le_sem_fetch_nem_ref(self):
        """Caso de abuso 7 (C-7): o modo `rotulados`, num clone com `git` registrador, só lê."""
        self.mescla(95, 'Rótulo: DECISÃO DO DONO (2026-11-06): "A"')
        self.roda()  # grava a fonte em `self.arq`
        pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, pasta)
        (pasta / "git").write_text(f'#!/bin/sh\necho "$*" >> {pasta}/registro\nexec {shutil.which("git")} "$@"\n', encoding="utf-8")
        (pasta / "git").chmod(0o755)
        r = subprocess.run([sys.executable, "-I", str(AQUI / "catraca.py"), "--modo", "rotulados", "--raiz", str(self.repo.dir), "--base", "base",
                            "--head", "develop", "--mesclados", str(self.arq)], capture_output=True, text=True, env={"PATH": f"{pasta}:/usr/bin:/bin"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("rotulados: #95 · rótulo do dono · decisão declarada no corpo", r.stdout)
        registro = (pasta / "registro").read_text(encoding="utf-8")
        self.assertIn("log --first-parent", registro)
        self.assertNotRegex(registro, r"\b(fetch|update-ref|tag|branch)\b")

    def test_modo_local_pede_token_repositorio_e_pr_e_nunca_imprime_o_token(self):
        for env, pr in (({"GITHUB_REPOSITORY": REPO_GH}, "7"), ({"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r;x"}, "7"),
                        ({"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": REPO_GH}, "7²")):
            self.assertEqual(self.roda("--modo", "rotulados", "--pr", pr, env=env)[0], 2)
        with mock.patch("urllib.request.urlopen", side_effect=RuntimeError("tok-s3")) as rede:
            rc, saida, resumo = self.roda("--modo", "rotulados", "--pr", "7", env={"GITHUB_TOKEN": "tok-s3", "GITHUB_REPOSITORY": REPO_GH})
            regras = self.roda("--pr", "7", env={"GITHUB_TOKEN": "tok-s3", "GITHUB_REPOSITORY": REPO_GH, "PR_NUMBER": "7"})  # fonte da API
        self.assertEqual(regras[:2], (0, "rotulados: incompleta (RuntimeError)\n"))
        self.assertEqual(rc, 0, saida)
        self.assertIn("rotulados: incompleta (RuntimeError)", saida)
        self.assertNotIn("tok-s3", saida + resumo)
        self.assertEqual((rede.call_args.args[0].get_method(), rede.call_args.args[0].full_url), ("GET", "https://api.github.com/repos/o/r/pulls/7"))
