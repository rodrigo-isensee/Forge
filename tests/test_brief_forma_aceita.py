"""E7 BRIEF-FORMA-ACEITA (versao-035): o brief gerado de código traz as formas de commit e merge que os hooks aceitam, e cada
forma de commit da constante passa pelo hook `conformidade` (a oferta não envelhece em relação ao hook). Sem rede."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_etapa_do_brief import Base, ambiente_do_git, fc  # noqa: E402

HOOKS = Path(__file__).resolve().parent.parent / "hooks"
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; "
            "sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")


class FormasNoBrief(Base):
    def gerar(self, destino, *extra):
        return self.rodar("brief", "gerar", "--pedido", self.pedido, "--destino", f"forge:{destino}", *extra)

    def test_brief_de_codigo_traz_a_secao_com_cada_forma(self):
        rc, saida = self.gerar("dev-exemplo", "--cobre", "E1.1", "--branch", "melhoria/x")
        self.assertEqual(rc, 0, saida)
        self.assertIn("## Formas aceitas pelos hooks (copie, não reescreva)", saida)
        for _, comando in fc.FORMAS_DE_COMMIT:
            self.assertIn(comando, saida)
        self.assertNotIn("--is-ancestor", saida)  # brief de código não traz o merge (tests/test_volta_por_delta.py)

    def test_brief_de_review_nao_traz_a_secao(self):
        rc, saida = self.gerar("revisor-exemplo", "--cobre", "E1.2", "--etapa", "review", "--branch", "melhoria/x")
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("Formas aceitas pelos hooks", saida)

    def test_etapa_de_merge_traz_a_linha_do_merge_uma_vez(self):  # A2: o pq_de_merge já a traz
        with mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), mock.patch.object(fc, "estado_da_branch", return_value=([], [])):
            saida, rc, _ = fc.montar_brief(self.tmp, str(self.pedido), "forge:revisor-exemplo", "melhoria/x", "develop",
                                           etapa="merge-integracao", cobre="E1.5")
        self.assertEqual(rc, 0, saida)
        self.assertIn("## Formas aceitas pelos hooks", saida)
        self.assertEqual(saida.count("git merge-base --is-ancestor <mergeCommit> origin/develop"), 1, saida)

    def test_brief_gerado_e_preenchido_passa_na_forma_com_a_secao(self):  # A1: a seção não cai no Pronto quando
        rc, saida = self.gerar("dev-exemplo", "--cobre", "E1.1")
        self.assertEqual(rc, 0, saida)
        linhas = [linha for linha in saida.splitlines() if fc.PREENCHER not in linha]
        linhas[linhas.index("## Ler"):linhas.index("## Ler")] = ["## Objetivo", "Exemplo.", ""]
        pronto = next(i for i, linha in enumerate(linhas) if linha.startswith("## Pronto quando"))
        linhas.insert(pronto + 1, "- PQ-1 (cmd): `true` · espera: rc=0")
        texto = "\n".join(linhas) + "\n"
        self.assertIn("## Formas aceitas pelos hooks", texto)
        self.assertIn("git commit", texto)
        rc, conferido = self.conferir(texto)
        self.assertIn("forma: ok", conferido)
        self.assertNotIn("sem PQ que o conferente confira", conferido)


class FormasPassamNoHook(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-formas-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = sem_manutencao(dict(os.environ, HOME=str(self.tmp), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull))
        (self.tmp / ".forge").mkdir()
        (self.tmp / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")  # o hook só age dentro de um projeto do Forge
        subprocess.run(["git", "init", "-q", "-b", "melhoria/x", str(self.tmp)], check=True, env=self.env, timeout=60)

    def pelo_hook(self, comando):
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": comando},
                   "cwd": str(self.tmp), "agent_type": "forge:tech-lead", "session_id": "s"}
        limpo = {k: v for k, v in self.env.items() if not k.startswith("FORGE_")}
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / "conformidade.py")],
                              input=json.dumps(entrada), cwd=self.tmp, env=limpo, capture_output=True, text=True, timeout=120)

    def test_cada_forma_de_commit_passa_no_hook_conformidade_como_tech_lead(self):
        for nome, forma in fc.FORMAS_DE_COMMIT:
            r = self.pelo_hook(forma)
            with self.subTest(forma=nome):
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_o_teste_distingue_aceita_de_recusada(self):  # controle: o hook está de pé e recusa `--no-verify` (R-VERIFY)
        r = self.pelo_hook("git commit --no-verify -m 'x'")
        self.assertEqual(r.returncode, 2, r.stderr)


class EscritaDoDestino(Base):
    """VV-3 E1b-1: o `forge-check brief` confere cada caminho do Entregar pela resposta do hook `conformidade` ao destino,
    no ramo do `Branch:` (casos 1, 7, 8 e 10 do modelo de ameaças da 0.44)."""

    def caso(self, destino, caminho, branch="nenhuma", plugin=None):
        papel = destino.split(":", 1)[1]
        pedido = self.gravar("docs/pedidos/escrita.md", f"---\nid: escrita\n---\n# Pedido\n\n## Escopo\n- E1. X · `confirmado`\n\n"
                             f"## Etapas\n- E1.1 ({papel}): fazer X.\n")
        texto = (f"Agente destino: {destino}\n" + (f"Branch: {branch}\n" if branch else "") + "\n## Objetivo\nX.\n\n## Ler\n- o pedido.\n\n## Entregar\n"
                 f'- "E1.1 ({papel}): fazer X." (E1.1): com o `forge-check`, grave `{caminho}`.\n\n## Fora do escopo\n- nada.\n\n'
                 "## Decisões e restrições\n- nenhuma.\n\n## Pronto quando\n- PQ-1 (cmd): `true` · espera: rc=0\n\n## Relatório\nX.\n")
        if plugin is None:
            return self.rodar("brief", self.gravar("b.md", texto), "--pedido", pedido)
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR" and not k.startswith("FORGE_")}
        r = subprocess.run([sys.executable, "-I", str(plugin / "bin" / "forge-check"), "--raiz", str(self.tmp), "brief",
                            str(self.gravar("b.md", texto)), "--pedido", str(pedido)],
                           capture_output=True, text=True, env=dict(env, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout

    def test_caso_1_aq_gravando_brief_reprova_barrada(self):
        rc, saida = self.caso("forge-dev:aq", "docs/briefs/x.md")
        self.assertIn('escrita: barrada "docs/briefs/x.md" (', saida)
        self.assertNotEqual(rc, 0, saida)

    def test_caso_10_legitimos_saem_ok(self):
        for destino, caminho in (("forge-dev:aq", "docs/propostas/x.md"),
                                 ("forge:security-engineer", "~/.forge-contrib/docs/security/ameacas/versao-044.md"),
                                 ("forge:tech-lead", "bin/forge-check"), ("forge:qa-engineer", "docs/qa/escrita.md")):
            with self.subTest(destino=destino):
                rc, saida = self.caso(destino, caminho, "melhoria/x")
                self.assertIn(f'escrita: ok "{caminho}"', saida)
                self.assertEqual(rc, 0, saida)

    def test_o_branch_do_brief_decide_a_entrada_de_ramo(self):  # legítimo 3 no clone do Forge: melhoria/* passa; fora, barra
        self.gravar(".claude-plugin/plugin.json", '{"name": "forge"}')
        rc, saida = self.caso("forge:tech-lead", "tests/catraca.py", "melhoria/x")
        self.assertIn('escrita: ok "tests/catraca.py"', saida)
        env = ambiente_do_git()
        subprocess.run(["git", "init", "-q", "-b", "melhoria/x", str(self.tmp)], check=True, env=env, timeout=60)
        for branch in ("nenhuma", None):  # sem `Branch:`, o ramo é vazio: o do disco (melhoria/x) não vale
            rc, saida = self.caso("forge:tech-lead", "tests/catraca.py", branch)
            self.assertIn('escrita: barrada "tests/catraca.py" (', saida)
            self.assertNotEqual(rc, 0, saida)

    def test_caminho_com_marcador_sai_nao_verificavel_sem_reprovar(self):
        rc, saida = self.caso("forge-dev:aq", "<pasta>/x.md")
        self.assertIn('escrita: não verificável "<pasta>/x.md"', saida)
        self.assertNotIn("escrita: barrada", saida)
        self.assertEqual(rc, 0, saida)

    def test_caminho_acima_do_teto_sai_nao_verificavel_sem_reprovar(self):  # o quarto campo da E1a-2 (C-8)
        rc, saida = self.caso("forge-dev:aq", "docs/briefs/" + "x" * 4100)
        self.assertIn('escrita: não verificável "docs/briefs/xxx', saida)
        self.assertEqual(rc, 0, saida)

    def test_caso_7_politica_ilegivel_reprova_nao_conferida(self):
        plugin = self.tmp / "plugin"
        shutil.copytree(HOOKS, plugin / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        (plugin / "bin").mkdir()
        shutil.copy2(HOOKS.parent / "bin" / "forge-check", plugin / "bin" / "forge-check")
        (plugin / "hooks" / "conformidade.json").write_text("{", encoding="utf-8")
        rc, saida = self.caso("forge-dev:aq", "docs/propostas/x.md", plugin=plugin)
        self.assertIn('escrita: não conferida "docs/propostas/x.md" (', saida)
        self.assertNotIn("escrita: ok", saida)
        self.assertNotEqual(rc, 0, saida)
        (plugin / "hooks" / "conformidade.py").write_text("(", encoding="utf-8")  # o hook que nem importa também reprova
        rc, saida = self.caso("forge-dev:aq", "docs/propostas/x.md", plugin=plugin)
        self.assertIn('escrita: não conferida "docs/propostas/x.md" (hook ilegível: SyntaxError)', saida)
        self.assertNotEqual(rc, 0, saida)
        (plugin / "hooks" / "conformidade.py").write_text(  # a exceção da função também (T-5)
            'NAO_CONFERIDA, NAO_VERIFICAVEL, INVISIVEIS = "não conferida", "não verificável", frozenset()\n'
            "def escrita_barrada(*a):\n    raise RuntimeError\n", encoding="utf-8")
        rc, saida = self.caso("forge-dev:aq", "docs/propostas/x.md", plugin=plugin)
        self.assertIn('escrita: não conferida "docs/propostas/x.md" (erro interno (RuntimeError))', saida)
        self.assertNotEqual(rc, 0, saida)

    def test_caso_8_ambiente_nao_muda_a_saida(self):
        with mock.patch.dict(os.environ):
            for nome in ("CLAUDE_PROJECT_DIR", "FORGE_GUARDA_ABERTA"):
                os.environ.pop(nome, None)
            limpo = self.caso("forge-dev:aq", "docs/briefs/x.md")
        outro = self.tmp / "outro"
        outro.mkdir()
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(outro), "FORGE_GUARDA_ABERTA": "1"}):
            self.assertEqual(self.caso("forge-dev:aq", "docs/briefs/x.md"), limpo)
        self.assertIn("escrita: barrada", limpo[1])
        self.assertNotIn("aviso: escrita", limpo[1])  # T-4: a linha nunca entra na tupla de avisos

    def test_caso_4_prefixo_que_nao_decide_sai_nao_verificavel_contado(self):  # E1b-2, C-6
        rc, saida = self.caso("forge-dev:aq", "$HOME/.forge-contrib/docs/propostas/x.md docs/propostas/$X.md docs/propostas/y.md")
        self.assertIn('escrita: não verificável "$HOME/.forge-contrib/docs/propostas/x.md"', saida)
        self.assertIn('escrita: não verificável "docs/propostas/$X.md"\n', saida)  # sem motivo vazio
        self.assertIn("escrita: 2 não verificáveis\n", saida)
        self.assertEqual(rc, 0, saida)
        rc, saida = self.caso("forge-dev:aq", "docs/propostas/y.md")
        self.assertNotIn("não verificáveis", saida)

    def test_caso_5_prefixo_fixo_barrado_decide(self):  # E1b-2, C-6: o `$X` não esconde a pasta barrada à frente
        for caminho in ("docs/briefs/$X.md", "docs/briefs/*.md", "docs/briefs/x?.md", "docs/briefs/[ab].md", "docs/briefs/<n>.md",
                        "~/.forge-contrib/docs/briefs/${X}.md", "docs/briefs/sub/$X.md"):
            with self.subTest(caminho=caminho):
                rc, saida = self.caso("forge-dev:aq", caminho)
                self.assertIn(f'escrita: barrada "{caminho}" (', saida)
                self.assertNotIn("não verificáveis", saida)
                self.assertNotEqual(rc, 0, saida)

    def test_caso_6_invisivel_depois_da_marca_reprova_barrada(self):  # E1b-2, C-5: a marca não esconde o invisível (S1)
        for caminho in ("docs/propostas/$X\u202e.md", "docs/propostas/<n>\x00.md", "docs/propostas/*/\u202edm.x/sfeirb/.."):
            with self.subTest(caminho=caminho):
                rc, saida = self.caso("forge-dev:aq", caminho)
                visto = caminho.replace("\u202e", "\\u202e").replace("\x00", "\\u0000")
                self.assertIn(f'escrita: barrada "{visto}" (caractere invisível no caminho)', saida)
                self.assertNotIn("não verificáve", saida)
                self.assertNotEqual(rc, 0, saida)

    def test_caso_9_acima_de_64_caminhos_reprova(self):  # E1b-2, C-8: o excedente não é conferido e reprova
        rc, saida = self.caso("forge-dev:aq", " ".join(f"docs/propostas/x{i}.md" for i in range(64)))
        self.assertEqual(saida.count("escrita: ok"), 64)
        self.assertNotIn("além do teto", saida)
        self.assertEqual(rc, 0, saida)
        rc, saida = self.caso("forge-dev:aq", " ".join(f"docs/propostas/x{i}.md" for i in range(66)))
        self.assertEqual(saida.count("escrita: ok"), 64)
        self.assertIn("escrita: 2 caminhos além do teto de 64, não conferidos\n", saida)
        self.assertNotEqual(rc, 0, saida)


if __name__ == "__main__":
    unittest.main()
