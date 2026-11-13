"""PRE-ENVIO-RAPIDO (mp1311, diretriz 23 com a DECISÃO DO DONO de 13/11 17:31): o `brief gerar` do Forge cobra do autor as PQs de
pré-envio (descrição do PR pela catraca, o mapa de testes e os testes de tamanho de texto e, só quando o Entregar declara código, os testes afetados); os briefs de
parecer só aprovam com o CI do head todo verde quando há PR. E o `forge-testes --texto` roda os testes de tamanho de texto num comando só.
Sem rede: o `gh` e o pre-push não rodam; a decisão é lida no brief montado."""
import importlib.machinery
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent


def carregar(nome, rel):
    carregador = importlib.machinery.SourceFileLoader(nome, str(RAIZ / rel))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(nome, carregador))
    carregador.exec_module(modulo)
    return modulo


fc = carregar("forge_check_pre_envio", "bin/forge-check")
ft = carregar("forge_testes_pre_envio", "bin/forge-testes")

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO

## Escopo
- E1. Fazer o recurso X · `confirmado`

## Etapas
- E1.1 (dev-exemplo): o recurso X em bin/forge-x e tests/test_x.py.
- E1.2 (dev-exemplo): o guia do recurso X em docs/guia.md.
- E1.3 (dev-exemplo): junção com a develop do recurso em bin/forge-x e PR em rascunho.
- E1.4 (revisor-exemplo): review do recurso X.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""

CATRACA = "python3 tests/catraca.py --modo pr-texto"
TEXTO = "`python3 -m unittest tests.test_testes_tocados tests.test_forge.Orcamento tests.test_jarvis_nucleo tests.test_metricas_texto " \
        "tests.test_orcamento_instrucao`"
AFETADOS = "`FORGE_PREPUSH_SUITE=afetados .githooks/pre-push`"


class Gerar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-pre-envio-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        (self.tmp / "docs" / "pedidos" / "exemplo.md").write_text(PEDIDO, encoding="utf-8")

    def gerar(self, etapa, cobre, forge=True, destino="forge:dev-exemplo", pr=({}, None)):
        with mock.patch.object(fc, "e_o_forge", return_value=forge), mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), \
                mock.patch.object(fc, "estado_da_branch", return_value=([], [])), mock.patch.object(fc, "pr_da_branch", return_value=pr), \
                mock.patch.object(fc, "base_sha_real", return_value="b" * 40), redirect_stderr(io.StringIO()):
            saida, rc, erros = fc.montar_brief(self.tmp, "exemplo", destino, "melhoria/x", "develop", etapa=etapa, cobre=cobre)
        self.assertEqual(rc, 0, erros)
        return saida

    def test_codigo_traz_descricao_texto_e_testes_afetados(self):
        saida = self.gerar("codigo", "E1.1")
        for trecho in (CATRACA, TEXTO, AFETADOS):
            self.assertIn(trecho, saida)
        self.assertLess(saida.index(TEXTO), saida.index("forge-check entrega"))  # antes do PQ do autor que o selo numera
        self.assertNotIn("sem PR para a branch", saida)  # a linha do CI é só do parecer

    def test_so_texto_fica_sem_os_testes_afetados(self):
        saida = self.gerar("codigo", "E1.2")
        self.assertIn(CATRACA, saida)
        self.assertIn(TEXTO, saida)
        self.assertNotIn(AFETADOS, saida)

    def test_juncao_fica_sem_os_testes_afetados(self):
        saida = self.gerar("pr", "E1.3")
        self.assertIn(CATRACA, saida)
        self.assertIn(TEXTO, saida)
        self.assertNotIn(AFETADOS, saida)

    def test_fora_do_forge_nao_cobra_o_pre_envio_da_fabrica(self):
        saida = self.gerar("codigo", "E1.1", forge=False)
        for trecho in (CATRACA, TEXTO, AFETADOS):
            self.assertNotIn(trecho, saida)

    def test_parecer_nao_leva_o_pre_envio_do_autor(self):
        saida = self.gerar("review", "E1.4", destino="forge:revisor-exemplo")
        self.assertNotIn(TEXTO, saida)

    def test_parecer_com_pr_so_aprova_com_o_ci_do_head_verde(self):
        saida = self.gerar("review", "E1.4", destino="forge:revisor-exemplo", pr=({"number": 7, "state": "OPEN", "head": "a" * 40}, None))
        self.assertIn("`gh pr checks 7` · espera: rc=0 · aprova só com o CI do head todo verde, e2e incluso", saida)

    def test_parecer_sem_pr_diz_que_a_suite_fica_para_o_ci(self):
        saida = self.gerar("qa", "E1.4", destino="forge:revisor-exemplo")
        self.assertIn("sem PR para a branch: a suíte inteira fica para o CI do PR", saida)
        self.assertNotIn("gh pr checks", saida)

    def test_parecer_sem_gh_mantem_a_regra(self):
        saida = self.gerar("seguranca", "E1.4", destino="forge:revisor-exemplo", pr=(None, "sem gh"))
        self.assertIn("aprova só com o CI do head todo verde, e2e incluso (`gh pr checks <n>`), quando houver PR", saida)


class Texto(unittest.TestCase):
    def test_a_lista_do_brief_e_a_do_modo_de_texto(self):
        self.assertEqual(fc.TESTES_DE_TEXTO, ft.TESTES_DE_TEXTO)

    def rodar(self, *args, codigo=0):
        self.addCleanup(os.chdir, os.getcwd())  # o `main` vai para a raiz do repositório
        with mock.patch.object(ft, "git", return_value=f"{RAIZ}\n"), mock.patch.object(ft, "anotar"), \
                mock.patch.object(ft.subprocess, "run", return_value=mock.Mock(returncode=codigo)) as run, redirect_stdout(io.StringIO()) as saida:
            rc = ft.main(list(args))
        return rc, run, saida.getvalue()

    def test_roda_os_testes_de_texto_num_comando_so_com_rc_e_resumo(self):
        rc, run, saida = self.rodar("--texto", codigo=1)
        self.assertEqual(rc, 1)
        run.assert_called_once_with([sys.executable, "-m", "unittest", "-q", "tests.test_testes_tocados", "tests.test_forge.Orcamento",
                                     "tests.test_jarvis_nucleo", "tests.test_metricas_texto", "tests.test_orcamento_instrucao"])
        self.assertEqual(len(saida.splitlines()), 1)
        self.assertRegex(saida, r"^forge-testes: texto rc=1 em \d+ s \(tests\.test_testes_tocados, ")

    def test_texto_nao_combina_com_outra_opcao(self):
        for extra in (["--completa"], ["--afetados"], ["--listar"], ["bin/forge-check"], ["-k", "x"]):
            with self.subTest(extra=extra):
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as erro:
                    self.rodar("--texto", *extra)
                self.assertEqual(erro.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
