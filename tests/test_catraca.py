"""Testes da catraca (tests/catraca.py) em repositório git temporário: cada regra com um caso que passa e um que barra."""
import contextlib
import copy
import hashlib
import http.client
import importlib.util
import io
import json
import re
import os
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
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
SHA_TRECHO = hashlib.sha256(b"trecho1").hexdigest()


def hash_(forma, tipo="trecho", n=None):
    """Entrada de `termos_proibidos_hash` para uma forma fictícia."""
    return {"tipo": tipo, "n": n or len(forma.strip()), "sha256": hashlib.sha256(forma.strip().encode()).hexdigest()}


TESTE = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n    def test_b(self): pass\n"


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
        self.escreve("tests/catraca.py", "# presente na base\n")
        self.escreve(".github/workflows/ci.yml", "name: CI\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("tag", "base")
        self.git("checkout", "-q", "-b", "pr")

    def git(self, *args):
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
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
        self.repo.escreve("tests/catraca.py", "# nova\n")
        self.repo.escreve(".github/workflows/ci.yml", "name: CI com catraca\n")
        self.passa()


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
        self.repo.escreve("tests/catraca.py", "# nova\n")
        self.repo.commit()
        self.assertEqual(catraca.regra_protegidos(self.repo.dir, "base", "HEAD"), [])

    def test_rotulo_do_dono_nao_libera_o_ls_tree_que_falha(self):
        """Cada leitura do git que falha deixa a catraca vermelha mesmo com o rótulo do dono depois do push."""
        self.repo.escreve("tests/catraca.py", "# mudou\n")
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
        self.repo.escreve("tests/catraca.py", "# mudou\n")
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
    def parecer(self, tipo, ramo="pr", parecer="aprovado", pedido="ped"):
        self.repo.commit()
        commit = self.repo.git("rev-parse", "--short", "HEAD").strip()
        pasta = "reviews" if tipo == "review" else "qa"
        extra = "revisor: forge:tech-lead" if tipo == "review" else "qa: forge:qa-engineer"
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
    """O rótulo vale para o diff efetivo do PR no instante em que foi aplicado (sem pareceres e sem o que veio da base)."""

    def setUp(self):
        super().setUp()
        self.repo.escreve("tests/catraca.py", "# mudou no PR\n")  # protegido: só passa com o rótulo
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()

    def roda(self, execs=None, ramo=""):
        self.repo.commit()
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
                r = self.roda(ramo="melhoria/ped")
                self.assertEqual(r.returncode, 1, r.stdout)

    def test_parecer_de_outro_pedido_que_ja_existia_na_base_invalida(self):
        self.repo.git("checkout", "-q", "develop")
        self.repo.escreve("docs/reviews/antigo.md", "parecer original\n")
        self.repo.commit()
        self.repo.git("checkout", "-q", "pr")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "develop")
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("docs/reviews/antigo.md", "histórico reescrito\n")
        self.assertEqual(self.roda(ramo="melhoria/ped").returncode, 1)

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
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(catraca.main(["--raiz", str(self.repo.dir), "--base", "develop", "--pr", "7"]), esperado)

    def test_sem_ramo_parecer_novo_depois_do_rotulo_invalida(self):
        self.repo.escreve("docs/reviews/ped.md", "parecer\n")
        self.assertEqual(self.roda().returncode, 1)

    def test_nome_com_curinga_nao_vira_padrao_que_esconde_outros_pareceres(self):
        """O caminho ignorado vai literal ao git: `docs/reviews/*` tocado antes do rótulo não cobre `outro.md`."""
        self.repo.escreve("docs/reviews/*", "parecer de nome estranho\n")
        self.repo.commit()
        self.rotulado = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.escreve("docs/reviews/outro.md", "reescrito\n")
        self.assertEqual(self.roda().returncode, 1)

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
        for rel, texto in (("tests/catraca.py", "# mudou de novo\n"), ("scripts/novo.sh", "echo\n"), ("KANBAN.md", "x\n")):
            with self.subTest(rel=rel):
                self.repo.git("reset", "-q", "--hard", self.rotulado)
                self.repo.escreve(rel, texto)
                r = self.roda()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("R-CONFORMIDADE:", r.stdout)

    def test_mudanca_de_codigo_junto_com_merge_da_base_invalida(self):
        self.mescla_base()
        self.repo.escreve("scripts/novo.sh", "echo\n")
        self.assertEqual(self.roda().returncode, 1)

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


class RotuloDePrMesclado(Base):
    """S-16: na promoção, a violação "mudança em <arquivo>" fica coberta pelo rótulo do dono já posto num PR mesclado
    em base..head, se o arquivo tem o mesmo blob e modo do head rotulado; tudo o mais pede o rótulo (A1-A14 da segurança)."""

    def setUp(self):
        super().setUp()
        r = self.repo
        r.git("branch", "main", "base")
        r.git("checkout", "-q", "-b", "fonte", "base")  # head do PR #10 (develop -> homolog), rotulado pelo dono
        r.escreve(".github/workflows/ci.yml", "name: CI\non: push\n")
        r.escreve("tests/catraca.py", "# mudou no PR 10\n")
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
        for texto in ("# mudou no PR 10\n# e mais uma linha\n", "on: push\nname: CI\n"):
            with self.subTest(texto=texto):
                self.repo.git("reset", "-q", "--hard", self.m)
                rel = "tests/catraca.py" if texto.startswith("#") else ".github/workflows/ci.yml"
                self.depois_do_merge(rel, texto)
                self.pede()

    def test_a1_push_depois_do_rotulo_e_merge_pede(self):
        self.repo.git("checkout", "-q", "fonte")
        self.depois_do_merge("tests/catraca.py", "# mudou de novo depois do rótulo\n")
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
        self.depois_do_merge("hooks/parecer.py", "# veio sem rótulo\n")
        r = self.pede()
        self.assertIn("mudança em hooks/parecer.py", r.stdout)

    def test_a12_caso_8_custo_pede_sempre(self):
        self.depois_do_merge("scripts/x.sh", "export ANTHROPIC_API_KEY=1\n")
        r = self.pede()
        self.assertIn("R-CUSTO:", r.stdout)

    def test_violacao_sem_arquivo_continua_pedindo(self):
        """Decisão do dono (alcance A): chaves do tests/config.json e contagem de testes seguem pedindo o rótulo."""
        self.depois_do_merge("tests/test_x.py", "import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
        r = self.pede()
        self.assertIn("testes `test_*` caíram", r.stdout)

    def test_a13_pr_de_melhoria_para_a_develop_pede(self):
        for pr in ({"head": lado("melhoria/x"), "base": lado("develop")}, {"head": lado("homolog", "fork/r"), "base": lado("main")}):
            with self.subTest(pr=pr):
                self.pede(pr=pr)

    def test_caso_5_e_6_merge_fora_do_intervalo_ou_numero_forjado_pede(self):
        """O conteúdo volta ao rotulado em #10, mas o merge de #10 já está na base; a mensagem que cita #10 não basta."""
        self.repo.git("branch", "-f", "main", self.m)
        self.repo.git("checkout", "-q", "main")
        self.depois_do_merge("tests/catraca.py", "# outro conteúdo na main\n")
        self.repo.git("checkout", "-q", "homolog")
        self.repo.git("merge", "-q", "--no-ff", "--no-edit", "main")
        self.depois_do_merge("tests/catraca.py", "# mudou no PR 10\n", "volta ao rotulado (#10)")
        self.pede()
        self.repo.git("reset", "-q", "--hard", self.m)
        self.depois_do_merge("tests/catraca.py", "# conteúdo sem rótulo\n", "outra coisa (#10)")
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
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    return subprocess.run(["git", "-C", str(pasta), *args], check=True, capture_output=True, text=True, env=env).stdout


def _tem(pasta, sha):
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    return subprocess.run(["git", "-C", str(pasta), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True, env=env).returncode == 0


ROTULADO = "# mudou no PR 10\n"
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
        return ["--raiz", str(self.repo.dir), "--base", "homolog", "--head", "develop", "--mesclados", str(arq)]

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
        self.pull["merge_commit_sha"] = self.squash("# misturado com a develop\n")
        self.depois("tests/catraca.py", ROTULADO, "volta ao rotulado")
        self.pede()

    def test_b17_head_da_promocao_com_uma_linha_a_mais_pede(self):
        self.depois("tests/catraca.py", ROTULADO + "# uma linha a mais\n")
        self.pede()

    def test_b12_numero_forjado_no_assunto_pede(self):
        self.pull["merge_commit_sha"] = self.squash("# conteúdo sem rótulo\n", msg="outra coisa (#10)")
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
    def test_b8_merge_fora_da_cadeia_de_primeiro_pai_pede(self):
        self.repo.git("checkout", "-q", "-b", "lateral", "base")
        time.sleep(1.2)  # o M do pull não pode coincidir com o do setUp (mesmo conteúdo e segundo dariam o mesmo hash)
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
        self.repo.escreve("tests/catraca.py", "# mudou\n")
        self.repo.commit()
        arq = self.repo.dir.parent / (self.repo.dir.name + "-eventos.json")
        arq.write_text(json.dumps([rotulo()]), encoding="utf-8")
        self.addCleanup(arq.unlink, missing_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GITHUB_STEP_SUMMARY")}
        r = subprocess.run(["python3", str(AQUI / "catraca.py"), "--raiz", str(self.repo.dir), "--base", "base", "--eventos", str(arq),
                            "--ultimo-push", "2026-01-02T09:00:00Z"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("mudança em tests/catraca.py", r.stdout)


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
        """Economia de minutos: bateria num job, push na develop só com a checagem rápida, timeout em todo job."""
        for nome in ("ci.yml", "catraca.yml", "release.yml"):
            texto = self.texto(nome)
            jobs = len(re.findall(r"(?m)^  [a-z-]+:\n    (?:name|if|runs-on):", texto))
            self.assertEqual(texto.count("timeout-minutes:"), jobs, nome)
            self.assertNotIn("paths-ignore", texto.replace("`paths-ignore`", "").replace("nunca paths-ignore", ""), nome)
        ci = self.texto("ci.yml")
        self.assertIn("if: github.event_name != 'push' || github.ref != 'refs/heads/develop'", ci)  # bateria fora do push na develop
        self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/develop'", ci)
        self.assertRegex(ci, r"(?m)^  bateria:")
        self.assertIn("docs/(reviews|qa)/", ci)

    def test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde(self):
        """Review independente: renomeação, testes de pareceres, check forjado, cancelamento e promoção."""
        ci = self.texto("ci.yml")
        self.assertIn("git diff --name-only --no-renames", ci)  # renomear código para docs/reviews não pode esconder a origem
        self.assertNotIn("always()", ci)  # execução cancelada não gasta os minutos que o gate poupa
        self.assertNotIn("always()", self.texto("catraca.yml"))
        self.assertIn("!cancelled()", ci)
        self.assertIn('[ "$BASE_REF" = develop ]', ci)  # promoção para a homolog roda a bateria completa (R-FLUXO)
        self.assertIn('.app.slug == "github-actions"', ci)
        self.assertIn("sort_by(.started_at) | last", ci)
        leve = re.search(r"(?m)^      - name: Testes que leem pareceres.*?\n        run: (.*)$", ci, re.S)
        self.assertIsNotNone(leve, "commit só de parecer ainda roda os testes que leem docs/reviews e docs/qa")
        for classe in ("Neutralidade", "Referencias", "AntiDuplicacao"):
            self.assertIn("tests.test_forge." + classe, leve.group(1).splitlines()[0])
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


if __name__ == "__main__":
    unittest.main()
