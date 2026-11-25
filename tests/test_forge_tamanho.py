"""H1-TETO-DE-TAMANHO-POR-ITEM e PEDIDO-TETO-BRIEF (v0474 E2.13): o `forge-check pr` e o `brief gerar` avisam do item acima de 150
linhas de código (testes e documentação não contam; decisão do dono 17/11 11:15); o `pr` só reprova quando o PR aberto não traz
`teto: excedido, <n> linhas, <motivo>` no corpo. O `brief gerar` avisa do pedido com mais de 50 etapas e do brief perto do teto de
caracteres. Sem rede: o `gh` é um falso no PATH e o `origin` é um repositório nu local."""
import contextlib
import functools
import io
import json
import os
import subprocess
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from test_selo_e_entrega import FORGE_CHECK, PEDIDO, RAIZ, Repositorio, fc  # noqa: E402



@functools.lru_cache(maxsize=None)
def tam():
    """bin/forge_tamanho.py carregado sob demanda: sem ele (a base), cada teste falha sozinho e o `--vermelho` tem veredito."""
    return SourceFileLoader("forge_tamanho_teste", str(RAIZ / "bin" / "forge_tamanho.py")).load_module()


class Funcoes(unittest.TestCase):
    def test_so_codigo_conta_e_binario_fica_fora(self):
        contagens = {"bin/app": ("100", "51"), "tests/test_app.py": ("900", "0"), "docs/a.md": ("500", "5"),
                     "changelog.d/x.md": ("3", "0"), "bin/imagem": ("-", "-")}
        self.assertEqual(tam().linhas_de_codigo(contagens, fc.e_codigo), 151)

    def test_borda_do_teto_de_linhas(self):
        self.assertIsNone(tam().aviso_de_linhas(150))
        self.assertIn("tamanho: 151 linhas de código, acima do teto de 150", tam().aviso_de_linhas(151))
        self.assertIn("`teto: excedido, 151 linhas, <motivo>`", tam().aviso_de_linhas(151))

    def test_motivo_no_corpo(self):
        for corpo in ("teto: excedido, 180 linhas, a guarda e o teste não ficam verdes separados",
                      "texto\n- teto: excedido, 180 linhas, o corte quebra a suíte\nmais", "  * teto: excedido, 9 linhas,  x"):
            with self.subTest(corpo=corpo):
                self.assertTrue(tam().tem_motivo(corpo))
        for corpo in (None, "", "teto: excedido, 180 linhas, ", "teto: excedido, 180 linhas,", "teto excedido, 180 linhas, x",
                      "o teto: excedido, 180 linhas, x", "teto: excedido, muitas linhas, x"):
            with self.subTest(corpo=corpo):
                self.assertFalse(tam().tem_motivo(corpo))

    def test_falta_de_motivo(self):
        self.assertIsNone(tam().falta_de_motivo(150, "", 7))
        self.assertIsNone(tam().falta_de_motivo(151, "teto: excedido, 151 linhas, a suíte quebra", 7))
        self.assertIn("no corpo do PR #7", tam().falta_de_motivo(151, "sem a linha", 7))

    def test_numero_do_motivo_cobre_o_total(self):
        self.assertIsNotNone(tam().falta_de_motivo(160, "teto: excedido, 9 linhas, ok", 7))
        self.assertIsNotNone(tam().falta_de_motivo(400, "teto: excedido, 151 linhas, o item cresceu", 7))
        self.assertIsNone(tam().falta_de_motivo(160, "teto: excedido, 9 linhas, velho\nteto: excedido, 200 linhas, novo", 7))
        self.assertIsNone(tam().falta_de_motivo(160, "teto: excedido, 160 linhas, a suíte quebra", 7))

    def test_borda_das_etapas(self):
        self.assertIsNone(tam().aviso_de_etapas(50))
        self.assertIn("o pedido tem 51 etapas", tam().aviso_de_etapas(51))

    def test_borda_dos_caracteres(self):
        self.assertIsNone(tam().aviso_de_caracteres(7999, 10000))
        self.assertIsNotNone(tam().aviso_de_caracteres(8000, 10000))  # a base (90%) falha aqui por asserção, não por erro (QA A3)
        self.assertIn("o brief tem 8000 caracteres, perto do teto de 10000", tam().aviso_de_caracteres(8000, 10000))
        self.assertIn("pedido de continuação", tam().aviso_de_caracteres(10500, 10000))


GH_FALSO = """#!/bin/sh
echo "$*" >> "{log}"
printf '%s' '{saida}'
printf '%s' '{erro}' >&2
exit {rc}
"""


class ComRepositorio(Repositorio):
    """O `pr` e o `brief gerar` de ponta a ponta, com `python3 -I` e o ambiente limpo; o `gh` é o falso de `bin/gh`."""

    def setUp(self):
        super().setUp()
        self.falsos = self.tmp / "falsos"
        self.falsos.mkdir()
        self.log_gh = self.tmp / "gh.log"
        self.env = sem_manutencao({"PATH": f"{self.falsos}:{os.environ.get('PATH', '/usr/bin:/bin')}", "HOME": str(self.home),
                                   "LANG": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        self.gh(rc=1, erro="no pull requests found for branch")

    def gh(self, saida="", rc=0, erro=""):
        arq = self.falsos / "gh"
        arq.write_text(GH_FALSO.format(log=self.log_gh, saida=saida, erro=erro, rc=rc), encoding="utf-8")
        arq.chmod(0o755)

    def pr_aberto(self, corpo, estado="OPEN"):
        self.gh(saida=json.dumps({"number": 7, "state": estado, "headRefOid": "a" * 40, "body": corpo}))

    def item(self, linhas_de_codigo):
        """A branch com `linhas_de_codigo` linhas novas em bin/app e muitas em teste e documentação, que não contam."""
        self.gravar("bin/app", "x\n" + "".join(f"l{i}\n" for i in range(linhas_de_codigo)))
        self.gravar("tests/test_app.py", "".join(f"# t{i}\n" for i in range(400)))
        self.gravar("docs/notas/a.md", "".join(f"n{i}\n" for i in range(400)))
        self.git("add", "bin/app", "tests", "docs/notas")
        return self.commit("feat: item")

    def rodar3(self, *args):
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.proj), *map(str, args)], capture_output=True,
                           text=True, env=self.env, timeout=300)
        self.assertNotIn("Traceback", r.stderr)
        return r.returncode, r.stdout, r.stderr

    def tamanho(self, previo=False, base="develop", branch="melhoria/x", ref=None):
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), mock.patch.dict(os.environ, {"PATH": self.env["PATH"]}):  # o `gh` falso também em processo
            saida = fc.tamanho_do_pr(self.proj, ref, base, branch, previo)
        return saida, erro.getvalue()


class NoPr(ComRepositorio):
    def test_pr_aberto_sem_motivo_reprova(self):
        self.item(151)
        self.pr_aberto("## Objetivo\nsem a linha do teto\n")
        _, saida, erro = self.rodar3("pr", "x", "--base", "develop")
        self.assertIn("pr: tamanho: 151 linhas de código, acima do teto de 150", erro)
        self.assertIn("pr: tamanho: 151 linhas de código acima do teto de 150 sem a linha `teto: excedido, 151 linhas, <motivo>` "
                      "no corpo do PR #7", saida)
        self.assertIn("pr view melhoria/x --json number,state,headRefOid,body", self.log_gh.read_text(encoding="utf-8"))

    def test_pr_aberto_com_motivo_so_avisa(self):
        self.item(151)
        self.pr_aberto("## Objetivo\n- teto: excedido, 151 linhas, a guarda e o teste não ficam verdes separados\n")
        _, saida, erro = self.rodar3("pr", "x", "--base", "develop")
        self.assertIn("pr: tamanho: 151 linhas de código", erro)
        self.assertNotIn("tamanho", saida)

    def test_no_teto_nada(self):
        self.item(150)
        self.pr_aberto("sem a linha")
        _, saida, erro = self.rodar3("pr", "x", "--base", "develop")
        self.assertNotIn("tamanho", saida + erro)
        gh = self.log_gh.read_text(encoding="utf-8") if self.log_gh.exists() else ""  # E3.45: os checks do head leem o PR sem o corpo
        self.assertNotIn(",body", gh)

    def test_sem_pr_so_avisa(self):
        self.item(151)
        saida, erro = self.tamanho()
        self.assertEqual(saida, [])
        self.assertIn("pr: tamanho: 151 linhas de código", erro)
        self.assertNotIn("não verificável", erro)

    def test_pr_fechado_ou_mesclado_nao_reprova(self):
        self.item(151)
        for estado in ("CLOSED", "MERGED"):
            with self.subTest(estado=estado):
                self.pr_aberto("sem a linha do teto", estado)
                saida, erro = self.tamanho()
                self.assertEqual(saida, [])
                self.assertIn("pr: tamanho: 151 linhas de código", erro)
        self.pr_aberto("sem a linha do teto")
        self.assertIn("no corpo do PR #7", self.tamanho()[0][0])

    def test_ref_diferente_do_head_mede_a_ref(self):
        sha = self.item(151)
        self.git("rm", "-q", "bin/app")
        self.commit("revert: tira o item")
        self.pr_aberto("sem a linha do teto")
        self.assertEqual(self.tamanho(), ([], ""))
        saida, erro = self.tamanho(ref=sha)
        self.assertIn("pr: tamanho: 151 linhas de código", erro)
        self.assertIn("no corpo do PR #7", saida[0])

    def test_motivo_presente_devolve_lista_vazia(self):
        self.item(151)
        self.pr_aberto("teto: excedido, 151 linhas, a suíte quebra")
        self.assertEqual(self.tamanho()[0], [])

    def test_gh_sem_rede_avisa_nao_verificavel(self):
        self.item(151)
        self.gh(rc=1, erro="could not resolve host")
        saida, erro = self.tamanho()
        self.assertEqual(saida, [])
        self.assertIn("pr: tamanho: corpo do PR não verificável (gh sem rede ou sem acesso)", erro)

    def test_previo_e_base_do_fluxo_nao_chamam_o_gh(self):
        self.item(151)
        self.pr_aberto("sem a linha")
        for kwargs in ({"previo": True}, {"branch": "develop"}, {"branch": None}):
            with self.subTest(**{k: str(v) for k, v in kwargs.items()}):
                saida, erro = self.tamanho(**kwargs)
                self.assertEqual(saida, [])
                self.assertIn("pr: tamanho: 151 linhas", erro)
        self.assertFalse(self.log_gh.exists())

    def test_base_que_nao_le_nao_fala(self):
        self.item(151)
        self.assertEqual(self.tamanho(base="homolog"), ([], ""))

    def test_numstat_que_falha_nao_confere(self):
        self.item(151)
        with mock.patch.object(fc, "contagens_do_intervalo", lambda *a, **k: None):
            saida, erro = self.tamanho()
        self.assertEqual((saida, erro), ([], "pr: tamanho: não conferido: o git não leu o diff --numstat (H1)\n"))


def pedido_com(etapas):
    linhas = "".join(f"- E1.{i} (node-backend): {texto}\n" for i, texto in enumerate(etapas, 1))
    return PEDIDO.replace("- E1.1 (node-backend): implementação do recurso X.\n- E1.2 (tech-lead): review do recurso X.\n", linhas)


class NoBriefGerar(ComRepositorio):
    def gerar(self, *extra):
        return self.rodar3("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:node-backend", "--cobre", "E1.1",
                           "--etapa", "codigo", *extra)

    def test_pedido_com_mais_de_50_etapas_avisa(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_com(["etapa curta"] * 51))
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertIn("brief gerar: aviso: o pedido tem 51 etapas, acima de cerca de 50 (H1)", erro)
        self.assertNotIn("caracteres", erro)

    def test_50_etapas_nao_avisa(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_com(["etapa curta"] * 50))
        rc, _, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertNotIn("etapas, acima", erro)

    def test_brief_perto_do_teto_de_caracteres_avisa(self):
        self.gravar("docs/pedidos/exemplo.md", pedido_com(["texto longo " * 900]))  # E3.48: a coberta vai inteira ao Entregar
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertGreaterEqual(len(saida), 8000)
        self.assertIn(f"brief gerar: aviso: o brief tem {len(saida)} caracteres, perto do teto de 10000", erro)

    def test_brief_curto_nao_avisa(self):
        rc, saida, erro = self.gerar()
        self.assertEqual(rc, 0, erro)
        self.assertLess(len(saida), 8000)
        self.assertNotIn("caracteres, perto", erro)

    def test_brief_da_branch_acima_do_teto_avisa(self):
        self.item(151)
        rc, _, erro = self.gerar("--branch", "melhoria/x")
        self.assertEqual(rc, 0, erro)
        self.assertIn("pr: tamanho: 151 linhas de código, acima do teto de 150", erro)


class CorpoDoPr(unittest.TestCase):
    def pr(self, dados):
        with mock.patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(dados), "")):
            return fc.pr_da_branch(RAIZ, "melhoria/x", corpo=True)[0]

    def test_corpo_nulo_do_pr_vira_texto_vazio(self):
        base = {"number": 1, "state": "OPEN", "headRefOid": "a" * 40}
        self.assertEqual(self.pr({**base, "body": None})["body"], "")
        self.assertEqual(self.pr({**base, "body": "oi"})["body"], "oi")


if __name__ == "__main__":
    unittest.main()
