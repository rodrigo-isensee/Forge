"""Testes da catraca (tests/catraca.py) em repositório git temporário: cada regra com um caso que passa e um que barra."""
import copy
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

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
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
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

    def test_termo_proibido_removido_barra_e_acrescimo_passa(self):
        self.repo.config(termos_proibidos=lambda t: t + ["Outro"])
        self.passa()
        self.repo.config(termos_proibidos=[])
        self.barra("Segredo1", "R-NEUTRO")

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
        self.repo.escreve("tests/test_y.py", TESTE)
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

    def test_claude_code_no_npm_nao_e_custo(self):
        self.repo.escreve("scripts/i.sh", "npm install -g @anthropic-ai/claude-code\n")
        self.passa()


class Protegidos(Base):
    def test_mudanca_em_arquivo_protegido_barra(self):
        for rel in (".github/workflows/ci.yml", ".github/rulesets/main.json", ".github/CODEOWNERS", "tests/catraca.py"):
            with self.subTest(rel):
                repo = Repo()
                self.addCleanup(repo.fecha)
                repo.escreve(rel, "mudou\n")
                repo.commit()
                self.assertTrue(any(v.startswith("R-CONFORMIDADE") and f"mudança em {rel}" in v for v in repo.violacoes()))

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
        antigo = {k: os.environ.pop(k, None) for k in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER")}
        try:
            self.assertEqual(catraca.eventos_do_github(), (None, None))
        finally:
            os.environ.update({k: v for k, v in antigo.items() if v is not None})


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


class TextoDoPr(unittest.TestCase):
    def test_preenchido_passa(self):
        corpo = "## Projeto de origem\nweb\n\n## Como medir\nmenos retrabalho\n\n## Checklist\n- [ ] x\n"
        self.assertEqual(catraca.violacoes_do_texto(corpo), [])

    def test_vazio_ou_so_comentario_barra(self):
        corpo = "## Projeto de origem\n<!-- tipo -->\n\n## Como medir\n\n## Checklist\n"
        achadas = catraca.violacoes_do_texto(corpo)
        self.assertEqual(len(achadas), 2)
        self.assertTrue(all(v.startswith("R-CONTRIB:") for v in achadas))

    def test_secao_ausente_e_corpo_nulo_barram(self):
        self.assertEqual(len(catraca.violacoes_do_texto(None)), 2)
        self.assertEqual(len(catraca.violacoes_do_texto("## Como medir\nx\n")), 1)


class Pareceres(Base):
    def parecer(self, tipo, ramo="pr", parecer="aprovado"):
        self.repo.escreve("bin/forge-check", (AQUI.parent / "bin" / "forge-check").read_text(encoding="utf-8"))
        self.repo.commit()
        commit = self.repo.git("rev-parse", "--short", "HEAD").strip()
        pasta = "reviews" if tipo == "review" else "qa"
        extra = "revisor: forge:tech-lead" if tipo == "review" else "qa: forge:qa-engineer"
        self.repo.escreve(f"docs/{pasta}/ped.md",
                          f"---\ntipo: {tipo}\ncontrato: 1\npedido: ped\nbranch: {ramo}\ncommit: {commit}\n"
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

    def test_parecer_reprovado_ou_de_outra_branch_barra(self):
        self.repo.escreve("scripts/novo.sh", "echo\n")
        self.parecer("review", parecer="ajustes")
        self.assertEqual(len(self.roda()), 1)
        self.parecer("review", ramo="outra")
        self.assertEqual(len(self.roda()), 1)


if __name__ == "__main__":
    unittest.main()
