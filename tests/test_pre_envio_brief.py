"""PRE-ENVIO-RAPIDO (mp1311, diretriz 23 com a DECISÃO DO DONO de 13/11 17:31): o `brief gerar` do Forge cobra do autor as PQs de
pré-envio (descrição do PR pela catraca, o mapa de testes e os testes de tamanho de texto e, só quando o Entregar declara código, os testes afetados); os briefs de
parecer só aprovam com o CI do head todo verde quando há PR. E o `forge-testes --texto` roda os testes de tamanho de texto num comando só.
Sem rede: o `gh` e o pre-push não rodam; a decisão é lida no brief montado."""
import importlib.machinery
import importlib.util
import io
import os
import re
import shutil
import subprocess
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
ACHADOS = "`python3 -m unittest tests.test_forge_mutante.ConferirTodas`"


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
        for trecho in (CATRACA, TEXTO, AFETADOS, ACHADOS):
            self.assertIn(trecho, saida)
        self.assertLess(saida.index(TEXTO), saida.index("forge-check entrega"))  # antes do PQ do autor que o selo numera
        self.assertNotIn("sem PR para a branch", saida)  # a linha do CI é só do parecer

    def test_so_texto_fica_sem_os_testes_afetados(self):
        saida = self.gerar("codigo", "E1.2")
        self.assertIn(CATRACA, saida)
        self.assertIn(TEXTO, saida)
        self.assertNotIn(AFETADOS, saida)
        self.assertNotIn(ACHADOS, saida)  # H3 (a): a autoverificação do AR-12 só com código no Entregar

    def test_juncao_fica_sem_os_testes_afetados(self):
        saida = self.gerar("pr", "E1.3")
        self.assertIn(CATRACA, saida)
        self.assertIn(TEXTO, saida)
        self.assertNotIn(AFETADOS, saida)

    def test_fora_do_forge_nao_cobra_o_pre_envio_da_fabrica(self):
        saida = self.gerar("codigo", "E1.1", forge=False)
        for trecho in (CATRACA, TEXTO, AFETADOS):
            self.assertNotIn(trecho, saida)

    def test_codigo_do_forge_prova_pelo_ci_sem_o_d2_e_fora_do_forge_nao(self):  # G3-ENTREGA-PELO-CI (v0481 E28.6)
        saida = self.gerar("codigo", "E1.1")
        self.assertIn(fc.PQ_DO_CI, saida)
        self.assertIn("a prova do pronto é o CI do PR no head", saida)
        for d2 in ("pronto --base origin/develop", "D2 (D2-NO-BRIEF)", "-d2"):
            self.assertNotIn(d2, saida)
        afetados = next(l for l in saida.splitlines() if AFETADOS in l)
        self.assertIn("rode só os testes afetados para se guiar; a prova é o CI do PR no head", afetados)
        self.assertNotIn(fc.PQ_DO_CI, self.gerar("codigo", "E1.1", forge=False))

    def test_parecer_nao_leva_o_pre_envio_do_autor(self):
        saida = self.gerar("review", "E1.4", destino="forge:revisor-exemplo")
        self.assertNotIn(TEXTO, saida)

    def test_parecer_com_pr_so_aprova_com_o_ci_do_head_verde(self):
        saida = self.gerar("review", "E1.4", destino="forge:revisor-exemplo", pr=({"number": 7, "state": "OPEN", "head": "a" * 40}, None))
        self.assertIn("`gh pr checks 7` · espera: rc=0 · aprova só com o CI do head todo verde, e2e incluso", saida)

    def test_parecer_sem_pr_diz_que_a_suite_fica_para_o_ci(self):
        saida = self.gerar("seguranca", "E1.4", destino="forge:revisor-exemplo")  # a segurança fica fora do G3 (PARECER-LE-O-CI)
        self.assertIn("sem PR para a branch: a suíte inteira fica para o CI do PR", saida)
        self.assertNotIn("gh pr checks", saida)

    def test_parecer_sem_gh_mantem_a_regra(self):
        saida = self.gerar("seguranca", "E1.4", destino="forge:revisor-exemplo", pr=(None, "sem gh"))
        self.assertIn("aprova só com o CI do head todo verde, e2e incluso (`gh pr checks <n>`), quando houver PR", saida)


class LeOCiNoBrief(unittest.TestCase):
    """PARECER-LE-O-CI (G3, v0481 E8.1): o brief de review e de QA manda ler o CI do head e gravar a linha `- ci:`, sem rodar a
    bateria; sem PR, não há aprovação. O da segurança e o do autor seguem como antes."""
    COM_PR = ({"number": 7, "state": "OPEN", "head": "a" * 40}, None)
    setUp, gerar = Gerar.setUp, Gerar.gerar  # o mesmo pedido e o mesmo gh falso, sem herdar os testes do `Gerar`

    def test_review_e_qa_leem_o_ci_com_e_sem_gh(self):
        for etapa in fc.PORTOES_QUE_LEEM_O_CI:
            for pr in (self.COM_PR, (None, "sem gh")):
                with self.subTest(etapa=etapa, pr=pr):
                    saida = self.gerar(etapa, "E1.4", destino="forge:revisor-exemplo", pr=pr)
                    self.assertIn(fc.LINHA_LE_O_CI, saida)
                    self.assertIn("`- ci: <sha40 do Revisar-sha> verde`", saida)
                    self.assertIn("não rode a suíte inteira", saida)

    def test_review_e_qa_sem_pr_nao_aprovam(self):
        for etapa in fc.PORTOES_QUE_LEEM_O_CI:
            with self.subTest(etapa=etapa):
                saida = self.gerar(etapa, "E1.4", destino="forge:revisor-exemplo")
                self.assertIn(fc.SEM_PR_NO_PORTAO, saida)
                self.assertNotIn("o parecer cita o PQ do autor e não afirma CI verde", saida)

    def test_seguranca_e_autor_sem_a_linha(self):
        self.assertNotIn(fc.LINHA_LE_O_CI, self.gerar("seguranca", "E1.4", destino="forge:revisor-exemplo", pr=self.COM_PR))
        self.assertNotIn(fc.LINHA_LE_O_CI, self.gerar("codigo", "E1.1", pr=self.COM_PR))
        self.assertNotIn(fc.SEM_PR_NO_PORTAO, self.gerar("seguranca", "E1.4", destino="forge:revisor-exemplo"))


class QaLeOCiSemEsperarAConferencia(unittest.TestCase):
    """G3-ENTREGA-PELO-CI (v0481 E28.6, F2 parte 3): o brief do QA manda ler o CI do head sem esperar a conferência da entrega, e o
    pré-voo do portão (`pr --previo`) avisa a conferência que falta em vez de reprovar; o `pr` sem `--previo` segue exigindo-a."""
    FALTA = "docs/pedidos/p.md: conferência: nenhuma linha cobre o head"
    setUp, gerar = Gerar.setUp, Gerar.gerar

    def test_o_brief_do_qa_nao_espera_a_conferencia(self):
        saida = self.gerar("qa", "E1.4", destino="forge:revisor-exemplo", pr=LeOCiNoBrief.COM_PR)
        self.assertIn("o CI do head basta, sem esperar a conferência da entrega (G3-ENTREGA-PELO-CI)", saida)

    def conferencia(self, previo, linhas):
        erro = io.StringIO()
        with mock.patch.object(fc, "linhas_da_conferencia", return_value=linhas), redirect_stderr(erro):
            return fc.conferencia_do_head(self.tmp, "p", ref="melhoria/x", branch="melhoria/x", previo=previo), erro.getvalue()

    def test_no_previo_a_conferencia_que_falta_so_avisa(self):
        saida, erro = self.conferencia(True, [self.FALTA])
        self.assertEqual(saida, [])
        self.assertIn(f"aviso: {self.FALTA}; o pré-voo segue (--previo, G3-ENTREGA-PELO-CI)", erro)

    def test_fora_do_previo_a_conferencia_que_falta_reprova(self):
        self.assertEqual(self.conferencia(False, [self.FALTA]), ([self.FALTA], ""))
        self.assertEqual(self.conferencia(True, []), ([], ""))

    def test_o_pr_passa_o_previo_a_conferencia_com_e_sem_base(self):
        vazio = mock.Mock(return_value=[])
        for base in (None, "develop"):
            for previo in (False, True):
                with self.subTest(base=base, previo=previo), mock.patch.multiple(
                        fc, cmd_pr=vazio, tamanho_do_pr=vazio, checks_do_head=vazio, aviso_t1_do_pr=vazio, avisar_classe=vazio,
                        isencoes_da_entrega=mock.Mock(return_value=False), promocao=mock.Mock(return_value=False),
                        base_sem_flag_do_pr=mock.Mock(return_value=None), base_do_delta=mock.Mock(return_value=("origin/develop", None)),
                        linhas_da_conferencia=mock.Mock(return_value=[self.FALTA])), redirect_stderr(io.StringIO()):
                    saida = fc.pr_da_cli(self.tmp, "p", ref="melhoria/x", base=base, branch="melhoria/x", previo=previo)
                    self.assertEqual(saida, [] if previo else [self.FALTA])


class ChecksForaDaLinhaDoCi(unittest.TestCase):
    """A1 do #893: no `Revisar-sha`, `bateria (pareceres)`, `bateria` e `catraca` ficam vermelhos por construção (esperam o parecer
    ou o rótulo). A constante `CHECKS_FORA_DA_LINHA_DO_CI` é a fonte única: o brief, o esqueleto do parecer e as duas skills citam
    cada um; e cada um é um job de verdade dos workflows, para a lista não divergir do CI."""
    setUp, gerar = Gerar.setUp, Gerar.gerar

    def citados(self, texto, onde):
        self.assertEqual(len(fc.CHECKS_FORA_DA_LINHA_DO_CI), 3)
        for check in fc.CHECKS_FORA_DA_LINHA_DO_CI:
            with self.subTest(onde=onde, check=check):
                self.assertIn(f"`{check}`", texto)

    def test_o_brief_de_review_e_qa_cita_os_checks(self):
        for etapa in fc.PORTOES_QUE_LEEM_O_CI:
            linha = [l for l in self.gerar(etapa, "E1.4", destino="forge:revisor-exemplo", pr=LeOCiNoBrief.COM_PR).splitlines()
                     if l.startswith("- G3 (PARECER-LE-O-CI)")]
            self.assertEqual(len(linha), 1, etapa)
            self.citados(linha[0], f"brief {etapa}")

    def test_o_esqueleto_do_parecer_cita_os_checks(self):
        for tipo in fc.PORTOES_QUE_LEEM_O_CI:
            texto = fc.esqueleto_do_parecer(tipo, "p1", "melhoria/x", "a" * 40, "aprovado", "2026-01-01")
            nota = [l for l in texto.splitlines() if "a linha `- ci:` vale" in l]
            self.assertEqual(len(nota), 1, tipo)
            self.citados(nota[0], f"esqueleto {tipo}")

    def test_as_skills_citam_os_checks(self):
        for skill in ("engineering-practices", "qa-testing"):
            linhas = [l for l in (RAIZ / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").splitlines() if "PARECER-LE-O-CI" in l]
            self.assertEqual(len(linhas), 1, skill)
            self.citados(linhas[0], skill)

    def test_brief_esqueleto_e_skills_citam_a_forma_via(self):
        """G3.7 (v0481 E8.10): o run do `Revisar-sha` cancelado pelo envio de outro parecer; vale o do descendente só de pareceres."""
        textos = {"brief": fc.LINHA_LE_O_CI, "esqueleto": fc.NOTA_NO_ESQUELETO}
        textos.update({s: [l for l in (RAIZ / "skills" / s / "SKILL.md").read_text(encoding="utf-8").splitlines()
                           if "PARECER-LE-O-CI" in l][0] for s in ("engineering-practices", "qa-testing")})
        for onde, texto in textos.items():
            with self.subTest(onde=onde):
                self.assertIn("verde via <sha40 do descendente", texto)

    def test_cada_check_e_um_job_dos_workflows(self):
        ESPERA = re.compile(r"\$\{\{[^}]*outputs\.espera[^}]*\}\}$")  # E47.6: o sufixo é condicional
        nomes = set()
        for yml in (RAIZ / ".github" / "workflows").glob("*.yml"):
            nomes |= {ESPERA.sub("", l.split("name:", 1)[1].split("#")[0].strip()) for l in yml.read_text(encoding="utf-8").splitlines()
                      if l.startswith("    name:")}  # E47.1: o sufixo da espera é vazio sem espera; o check é o nome sem ele
        self.assertGreater(len(nomes), 10)
        self.assertLessEqual(set(fc.CHECKS_FORA_DA_LINHA_DO_CI), nomes)


DESATUALIZADO = ("docs/reviews/exemplo.md: commit: desatualizado: bin/forge-x mudou depois de aaaaaaa; peça novo parecer; o que mudou no "
                 "domínio: forge-check parecer delta docs/reviews/exemplo.md (R-REVIEW)")
REPROVADO = "docs/qa/exemplo.md: parecer: o último parecer não é aprovado (R-QA)"
LER_DO_DELTA = "- revalidação (H3, R-REVIEW): leia só `forge-check parecer delta docs/reviews/exemplo.md`"


class PortaoNaBranch(unittest.TestCase):
    """H3 (c): o brief de portão liga a revalidação ao `parecer delta` do parecer da branch e avisa quando o portão não precisa de agente."""

    def portao(self, etapa, linhas, exigidos=("review", "qa"), existe=True, branch="melhoria/x", base="develop"):
        with mock.patch.object(fc, "sha_do_commit", return_value="a" * 40 if existe else None), \
                mock.patch.object(fc, "pr_da_cli", return_value=list(linhas)) as pr, \
                mock.patch.object(fc, "base_do_delta", return_value=("refs/remotes/origin/develop", None)), \
                mock.patch.object(fc, "exigidos_do_pr", return_value=(list(exigidos), [])):
            return fc.portao_na_branch(RAIZ, "exemplo", etapa, branch, base), pr

    def test_parecer_desatualizado_no_dominio_le_so_o_delta(self):
        (ler, aviso), pr = self.portao("review", [DESATUALIZADO, REPROVADO])
        self.assertIsNotNone(ler)
        self.assertTrue(ler.startswith(LER_DO_DELTA), ler)
        self.assertIsNone(aviso)
        pr.assert_called_once_with(RAIZ, "exemplo", ref="melhoria/x", base="origin/develop")

    def test_parecer_reprovado_revalida_pelo_delta_do_proprio_tipo(self):
        (ler, aviso), _ = self.portao("qa", [DESATUALIZADO, REPROVADO])
        self.assertIsNotNone(ler)
        self.assertIn("`forge-check parecer delta docs/qa/exemplo.md`", ler)
        self.assertIsNone(aviso)
        (ler, _), _ = self.portao("seguranca", [DESATUALIZADO, REPROVADO], exigidos=("review", "qa", "revisao-seguranca"))
        self.assertIsNone(ler)  # o delta de outro portão não vale para este

    def test_parecer_exigido_aprovado_e_em_dia_avisa_que_nao_precisa_de_agente(self):
        (ler, aviso), _ = self.portao("review", [REPROVADO])
        self.assertIsNone(ler)
        self.assertEqual(aviso, "o parecer de review da branch está aprovado e em dia no head (`forge-check pr`): a etapa review "
                                "não precisa de agente (H3)")

    def test_portao_que_a_classe_nao_exige_avisa_sem_tirar_o_reprovado(self):  # H8: a classe decide; nenhum portão sai dela
        (ler, aviso), _ = self.portao("qa", [], exigidos=("review",))
        self.assertIsNone(ler)
        self.assertEqual(aviso, "a classe da entrega não exige o parecer de qa (`forge-check classe`): a etapa qa não precisa de agente (H8)")
        nao_aprova = "docs/qa/exemplo.md: parecer: o último parecer não é aprovado; o tipo não é exigido pela classe, mas o reprovado vale (R-QA)"
        ler, aviso = self.portao("qa", [nao_aprova], exigidos=("review",))[0]  # dispensar não é ignorar o reprovado: revalida pelo delta
        self.assertIn("`forge-check parecer delta docs/qa/exemplo.md`", ler)
        self.assertIsNone(aviso)
        with mock.patch.object(fc, "sha_do_commit", return_value="a" * 40), mock.patch.object(fc, "pr_da_cli", return_value=[]), \
                mock.patch.object(fc, "base_do_delta", return_value=("refs/remotes/origin/develop", None)), \
                mock.patch.object(fc, "exigidos_do_pr", return_value=(["review"], [])) as exigidos:
            fc.portao_na_branch(RAIZ, "exemplo", "qa", "melhoria/x", "origin/develop")
        exigidos.assert_called_once_with(RAIZ, "exemplo", "melhoria/x", "refs/remotes/origin/develop")

    def test_parecer_ausente_ou_com_outra_violacao_nao_avisa(self):
        for linha in ("docs/reviews: review: sem parecer para o pedido `exemplo` (R-REVIEW)",
                      "docs/reviews/exemplo.md: autoria: sem registro (R-REVIEW)"):
            with self.subTest(linha=linha):
                self.assertEqual(self.portao("review", [linha])[0], (None, None))

    def test_base_fora_do_fluxo_nao_avisa_nem_le_o_pr(self):  # review A1 e segurança A1: a recusa de uso não é parecer em dia
        for base in ("devlop", "origin/nada"):
            with self.subTest(base=base):
                resultado, pr = self.portao("review", [], base=base)
                self.assertEqual(resultado, (None, None))
                pr.assert_not_called()

    def test_linha_de_erro_ou_fora_das_pastas_de_parecer_nao_avisa(self):  # segurança A2: aviso só sem linha desconhecida
        for linha in ("pr: --base devlop: use develop, homolog, main (ou origin/<uma delas>); a base é lida de origin/<base>",
                      "docs/pedidos: parecer conferido ilegível"):
            with self.subTest(linha=linha):
                self.assertEqual(self.portao("review", [REPROVADO, linha])[0], (None, None))
                self.assertEqual(self.portao("qa", [linha], exigidos=("review",))[0], (None, None))

    def test_brief_gerar_recusa_base_fora_do_fluxo(self):  # a CLI aceita só as bases do fluxo, como a juncao
        tmp = Path(tempfile.mkdtemp(prefix="forge-portao-base-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp)}
        r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), "brief", "gerar", "--pedido", "exemplo",
                            "--base", "devlop"], capture_output=True, text=True, env=env, cwd=tmp)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("invalid choice: 'devlop'", r.stderr)

    def test_fora_do_portao_ou_sem_a_branch_nao_le_o_pr(self):
        for etapa, existe, branch in (("codigo", True, "melhoria/x"), ("pr", True, "melhoria/x"), ("review", False, "melhoria/x"),
                                      ("review", True, None)):
            with self.subTest(etapa=etapa, existe=existe, branch=branch):
                resultado, pr = self.portao(etapa, [DESATUALIZADO], existe=existe, branch=branch)
                self.assertEqual(resultado, (None, None))
                pr.assert_not_called()

    def test_o_brief_do_portao_traz_a_linha_no_ler_e_o_aviso_no_stderr(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-portao-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "docs" / "pedidos").mkdir(parents=True)
        (tmp / "docs" / "pedidos" / "exemplo.md").write_text(PEDIDO, encoding="utf-8")
        for retorno, no_ler, no_stderr in (((LER_DO_DELTA, None), True, False), ((None, "em dia (H3)"), False, True)):
            # create=True: na base sem portao_na_branch o patch não erra e o teste falha pela asserção (QA A1, veredito do vermelho)
            with mock.patch.object(fc, "e_o_forge", return_value=True), \
                    mock.patch.object(fc, "estado_da_branch", return_value=([], [])), mock.patch.object(fc, "pr_da_branch", return_value=({}, None)), \
                    mock.patch.object(fc, "base_sha_real", return_value="b" * 40), \
                    mock.patch.object(fc, "portao_na_branch", return_value=retorno, create=True), redirect_stderr(io.StringIO()) as err:
                saida, rc, _ = fc.montar_brief(tmp, "exemplo", "forge:revisor-exemplo", "melhoria/x", "develop", etapa="review", cobre="E1.4")
            self.assertEqual(rc, 0, retorno)
            ler = saida.split("\n## Ler\n", 1)[1].split("\n## Decisões", 1)[0]
            self.assertEqual(LER_DO_DELTA in ler, no_ler)
            self.assertEqual(err.getvalue().count("brief gerar: aviso: em dia (H3)"), 1 if no_stderr else 0)
            self.assertNotIn("aviso: None", err.getvalue())


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
        try:
            rc, run, saida = self.rodar("--texto", codigo=1)
        except SystemExit as erro:  # sem a opção, o argparse sai; o teste falha por asserção, não por erro (R-QA)
            self.fail(f"--texto não existe: o argparse saiu com {erro.code}")
        self.assertEqual(rc, 1)
        run.assert_called_once_with([sys.executable, "-m", "unittest", "-q", "tests.test_testes_tocados", "tests.test_forge.Orcamento",
                                     "tests.test_jarvis_nucleo", "tests.test_metricas_texto", "tests.test_orcamento_instrucao"])
        self.assertEqual(len(saida.splitlines()), 1)
        self.assertRegex(saida, r"^forge-testes: texto rc=1 em \d+ s \(tests\.test_testes_tocados, ")

    def test_texto_nao_combina_com_outra_opcao(self):
        for extra in (["--completa"], ["--afetados"], ["--listar"], ["bin/forge-check"], ["-k", "x"], ["--vermelho"], ["--modulos", "test_x"],
                      ["--prazo", "5"]):
            with self.subTest(extra=extra):
                with redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as erro:
                    self.rodar("--texto", *extra)
                self.assertEqual(erro.exception.code, 2)
                self.assertIn("--texto não combina com outras opções", err.getvalue())  # a guarda do --texto, não outra recusa do parser


if __name__ == "__main__":
    unittest.main()
