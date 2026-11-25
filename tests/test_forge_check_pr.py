"""E3.45 (v0474): o `forge-check pr` só aprova para merge com os checks do head concluídos e verdes e os exigidos do destino em pass.

Num projeto, um PR foi mesclado com o CI rodando e a integração ficou vermelha 74 min. Sem rede (R-CUSTO): o `gh` é a função
`gh_json` trocada por respostas simuladas, casadas pelo comando inteiro (nada de prefixo); o head e o "é o Forge" também são simulados.
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (o Repo roda git num repositório temporário)
from test_isencoes import Repo, git  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
fc = SourceFileLoader("forge_check_e345", str(RAIZ / "bin" / "forge-check")).load_module()

HEAD = "a" * 40
PR_VIEW = ("pr", "view", "melhoria/x", "--json", "number,state,isDraft,headRefOid,baseRefName")
PR_CHECKS = ("pr", "checks", "7", "--json", "name,bucket,workflow")
REGRAS = ("api", "repos/{owner}/{repo}/rules/branches/develop")
PROTECAO = ("api", "repos/{owner}/{repo}/branches/develop/protection/required_status_checks")
FORGE_OK = [{"name": "bateria", "bucket": "pass", "workflow": "CI"}, {"name": "bateria (python 3.14)", "bucket": "pass", "workflow": "CI"},
            {"name": "catraca", "bucket": "pass", "workflow": "Catraca"}]


def ck(nome, bucket, workflow="CI"):
    return {"name": nome, "bucket": bucket, "workflow": workflow}


class ChecksDoHead(unittest.TestCase):
    def rodar(self, checks=None, pr=None, regras=None, protecao=None, forge=False, previo=False, branch="melhoria/x", erro_checks="",
              erro_pr=None):
        """`checks_do_head` com as respostas do `gh` por comando exato; comando sem resposta devolve (None, "") como o gh sem rede.
        `erro_pr`: o `gh pr view` sem JSON e com este stderr. Guarda o stderr em `self.stderr` e as falhas de leitura do PR
        (CHECKS_NAO_CONFERIDOS) em `self.nao_conferidos`."""
        pr = {"number": 7, "state": "OPEN", "isDraft": False, "headRefOid": HEAD, "baseRefName": "develop"} if pr is None else pr
        respostas = {PR_VIEW: (pr, "") if erro_pr is None else (None, erro_pr), PR_CHECKS: (checks, erro_checks), REGRAS: (regras, ""),
                     PROTECAO: (protecao, "")}
        self.nao_conferidos, erro = [], io.StringIO()
        self.chamadas = []

        def gh_json(_raiz, *args):
            self.chamadas.append(args)
            return respostas.get(args, (None, ""))
        with mock.patch.object(fc, "gh_json", gh_json), mock.patch.object(fc, "sha_do_commit", lambda _r, _ref: HEAD), \
                mock.patch.object(fc, "e_o_forge", lambda _r: forge), mock.patch.object(fc, "CHECKS_NAO_CONFERIDOS", self.nao_conferidos), \
                contextlib.redirect_stderr(erro):
            saida = fc.checks_do_head(Path("/nao-existe"), "refs/heads/melhoria/x", branch, previo)
        self.stderr = erro.getvalue()
        return saida

    def reprova(self, saida, *trechos):
        self.assertEqual(len(saida), 1, saida)
        self.assertIn("não aprovado para merge (E3.45)", saida[0])
        for t in trechos:
            self.assertIn(t, saida[0])

    def test_projeto_tudo_verde_e_skipping_aprova(self):
        self.assertEqual(self.rodar([ck("testes", "pass"), ck("lint", "skipping")]), [])

    def test_pendente_reprova_com_a_lista(self):
        self.reprova(self.rodar([ck("testes", "pending"), ck("lint", "pass")]), "CI/testes (pending)")

    def test_vermelho_reprova(self):
        self.reprova(self.rodar([ck("testes", "fail")]), "CI/testes (fail)")

    def test_cancelado_reprova(self):
        self.reprova(self.rodar([ck("testes", "cancel")]), "CI/testes (cancel)")

    def test_exigido_do_ruleset_ausente_reprova(self):
        regras = [{"type": "pull_request"}, {"type": "required_status_checks",
                                              "parameters": {"required_status_checks": [{"context": "testes"}]}}]
        self.reprova(self.rodar([ck("lint", "pass")], regras=regras), "*/testes (exigido, ausente)")

    def test_so_a_regra_de_checks_exigidos_conta(self):
        regras = [{"type": "pull_request", "parameters": {"required_status_checks": [{"context": "outro"}]}}]
        self.assertEqual(self.rodar([ck("testes", "pass")], regras=regras), [])

    def test_resposta_de_404_nao_acrescenta(self):
        self.assertEqual(self.rodar([ck("testes", "pass")], regras={"message": "Not Found"}, protecao={"message": "Not Found"}), [])

    def test_exigido_da_protecao_em_skipping_reprova(self):
        self.reprova(self.rodar([ck("testes", "skipping")], protecao={"contexts": ["testes"]}), "*/testes (exigido, fora de pass)")

    def test_exigido_do_ruleset_de_qualquer_workflow_em_pass_aprova(self):
        self.assertEqual(self.rodar([ck("testes", "pass", "Outro")], protecao={"contexts": ["testes"]}), [])

    def test_sem_checks_no_projeto_aprova(self):
        self.assertEqual(self.rodar(None, erro_checks="no checks reported on the 'melhoria/x' branch"), [])

    def test_checks_nao_lidos_reprova(self):
        self.reprova(self.rodar(None, erro_checks="HTTP 502"), "PR #7 não lidos")

    def test_no_forge_sem_ruleset_vale_o_fallback(self):
        self.assertEqual(self.rodar(FORGE_OK, forge=True), [])
        self.reprova(self.rodar(FORGE_OK[1:], forge=True), "CI/bateria (exigido, ausente)")

    def test_no_projeto_o_fallback_do_forge_nao_vale(self):
        self.assertEqual(self.rodar([ck("testes", "pass")]), [])

    def test_no_forge_o_par_de_outro_workflow_nao_conta(self):  # C-6: o mesmo nome vindo de outro workflow
        self.reprova(self.rodar([ck("bateria", "pass", "Outro"), *FORGE_OK[1:]], forge=True), "CI/bateria (exigido, ausente)")

    def test_rascunho_nao_confere(self):
        pr = {"number": 7, "state": "OPEN", "isDraft": True, "headRefOid": HEAD, "baseRefName": "develop"}
        self.assertEqual(self.rodar([ck("testes", "pending")], pr=pr), [])

    def test_pr_mesclado_nao_confere(self):
        pr = {"number": 7, "state": "MERGED", "isDraft": False, "headRefOid": HEAD, "baseRefName": "develop"}
        self.assertEqual(self.rodar([ck("testes", "pending")], pr=pr), [])

    def test_outro_head_nao_confere(self):
        pr = {"number": 7, "state": "OPEN", "isDraft": False, "headRefOid": "b" * 40, "baseRefName": "develop"}
        self.assertEqual(self.rodar([ck("testes", "pending")], pr=pr), [])

    def test_previo_e_branch_do_fluxo_nao_consultam_o_gh(self):
        self.assertEqual(self.rodar([ck("testes", "pending")], previo=True), [])
        self.assertEqual(self.chamadas, [])
        self.assertEqual(self.rodar([ck("testes", "pending")], branch="develop"), [])
        self.assertEqual(self.chamadas, [])

    def test_pr_view_que_falha_avisa_e_marca_para_o_hook(self):  # A1 da segurança e do QA (E3.80): não aprova calado
        for erro in ("error connecting to api.github.com\n", "sem resposta em 10 s", "saída ilegível", ""):
            with self.subTest(erro=erro):
                self.assertEqual(self.rodar([ck("testes", "pending")], erro_pr=erro), [])
                self.assertEqual(len(self.nao_conferidos), 1, self.nao_conferidos)
                self.assertIn(f'PR de "melhoria/x" não lido (gh pr view: {erro.strip() or "saída vazia"}); ', self.nao_conferidos[0])
                self.assertIn(self.nao_conferidos[0], self.stderr)
                self.assertNotIn(PR_CHECKS, self.chamadas)

    def test_sem_pr_sem_remoto_do_github_ou_sem_gh_nao_marca(self):
        for erro in ('no pull requests found for branch "melhoria/x"\n', "no git remotes found\n",
                     "none of the git remotes configured for this repository point to a known GitHub host.\n",
                     "To get started with GitHub CLI, please run:  gh auth login\n", fc.GH_AUSENTE,
                     "gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:\n"):
            with self.subTest(erro=erro):
                self.assertEqual(self.rodar([ck("testes", "pending")], erro_pr=erro), [])
                self.assertEqual((self.nao_conferidos, self.stderr), ([], ""))

    def test_destino_fora_do_padrao_nao_vai_a_api(self):
        pr = {"number": 7, "state": "OPEN", "isDraft": False, "headRefOid": HEAD, "baseRefName": "dev#x"}
        self.assertEqual(self.rodar([ck("testes", "pass")], pr=pr), [])
        self.assertFalse([c for c in self.chamadas if c[0] == "api"], self.chamadas)


class GhJson(unittest.TestCase):
    """A leitura do `gh` por um falso no PATH (sh, sem rede): o JSON da saída, e o stderr quando não há saída."""
    def gh(self, script):
        pasta = Path(tempfile.mkdtemp(prefix="e345-gh-"))
        self.addCleanup(shutil.rmtree, pasta, ignore_errors=True)
        (pasta / "gh").write_text("#!/bin/sh\n" + script, encoding="utf-8")
        (pasta / "gh").chmod(0o755)
        with mock.patch.dict(os.environ, {"PATH": f"{pasta}{os.pathsep}{os.environ.get('PATH', '')}"}):
            return fc.gh_json(pasta, "pr", "checks", "7")

    def test_saida_json_vira_dado(self):
        self.assertEqual(self.gh("echo '[{\"name\": \"a\"}]'\n"), ([{"name": "a"}], ""))

    def test_sem_saida_devolve_o_stderr(self):
        self.assertEqual(self.gh("echo 'no checks reported' >&2\nexit 1\n"), (None, "no checks reported\n"))

    def test_saida_ilegivel_e_none(self):
        self.assertEqual(self.gh("echo 'x{'\n"), (None, "saída ilegível"))

    def test_sem_gh_e_teto_dizem_o_motivo(self):  # E3.80: o checks_do_head separa o gh ausente (sem PR a conferir) do teto (falha)
        for erro, esperado in ((FileNotFoundError(2, "x"), fc.GH_AUSENTE), (fc.subprocess.TimeoutExpired("gh", 10), "sem resposta em 10 s")):
            with self.subTest(esperado=esperado), mock.patch.object(fc.subprocess, "run", side_effect=erro):
                self.assertEqual(fc.gh_json(Path("/nao-existe"), "pr", "view", "x"), (None, esperado))


class GravarParaOHook(unittest.TestCase):
    """E3.80: o `executar` do `pr` com FORGE_FECHAR_PASSO_1=1 (o passo 1 do forge-fechar) não confere os checks e não grava o resultado;
    sem ela, o PR não lido grava reprovado para o hook do `gh pr merge`, com o rc do comando inalterado."""
    def executar(self, ambiente, nao_lido=False):
        gravados, pedidos = [], []

        def pr_da_cli(*_a, **k):
            pedidos.append(k)
            if nao_lido:
                fc.CHECKS_NAO_CONFERIDOS.append("pr: PR de melhoria/x não lido")
            return []
        a = fc.argparse.Namespace(cmd="pr", pedido="p1", ref="refs/heads/melhoria/x", base="origin/develop", previo=False, numero_pr=None)
        with mock.patch.dict(os.environ, ambiente), mock.patch.object(fc, "CHECKS_NAO_CONFERIDOS", []), \
                mock.patch.object(fc, "guarda_de_versao", lambda *_: None), mock.patch.object(fc, "migracao_pendente", lambda _r: []), \
                mock.patch.object(fc, "pedido_do_pr", lambda _r, p, _ref: p), mock.patch.object(fc, "uso_do_pr", lambda *_: None), \
                mock.patch.object(fc, "pr_da_cli", pr_da_cli), mock.patch.object(fc, "veredito_do_pr", lambda *_: "pr: veredito: aprovado"), \
                mock.patch.object(fc, "gravar_resultado_do_pr", lambda *args: gravados.append(args[-1])), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as erro:
            rc = fc.executar(a, Path("/nao-existe"))
        return rc, pedidos[0]["sem_checks"], gravados, erro.getvalue()

    def test_passo_1_do_fechar_nao_confere_nem_grava(self):
        rc, sem_checks, gravados, erro = self.executar({fc.SEM_CHECKS_DO_FECHAR: "1"})
        self.assertEqual((rc, sem_checks, gravados), (0, True, []))
        self.assertIn("checks do head não conferidos (FORGE_FECHAR_PASSO_1=1", erro)

    def test_sem_a_variavel_confere_e_o_pr_nao_lido_grava_reprovado(self):
        for valor in ("", "0", "sim"):
            with self.subTest(valor=valor):
                rc, sem_checks, gravados, _ = self.executar({fc.SEM_CHECKS_DO_FECHAR: valor}, nao_lido=True)
                self.assertEqual((rc, sem_checks, gravados), (0, False, [["pr: PR de melhoria/x não lido"]]))
        rc, _, gravados, _ = self.executar({fc.SEM_CHECKS_DO_FECHAR: ""})
        self.assertEqual((rc, gravados), (0, [[]]))


class ParesIguaisAoFechar(unittest.TestCase):
    def test_os_pares_do_forge_sao_os_do_forge_fechar(self):
        texto = (RAIZ / "bin" / "forge-fechar").read_text(encoding="utf-8")
        linha = next(l for l in texto.splitlines() if l.startswith("readonly CHECKS_EXIGIDOS=("))
        self.assertEqual(linha, "readonly CHECKS_EXIGIDOS=(" + " ".join(f'"{p}"' for p in fc.CHECKS_EXIGIDOS_DO_FORGE) + ")")



# ---- PARECER-SO-COM-CI-VERDE (v0478 E47.1) ------------------------------------------------------------------------------------------
# No Forge, o `forge-check pr` só conta o review e o QA aprovados com o CI verde no head ou com a prova da suíte no `commit:` do parecer
# (`- suíte: <sha40> rc=0 módulos=<...>`, cobrindo os módulos de teste do diff). O gh falso casa o comando inteiro, como o de cima.
FORGE = {".claude-plugin/plugin.json": json.dumps({"name": "forge"}) + "\n", "tests/test_velho.py": "x = 0\n"}
REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
          "revisor: forge:tech-lead\ndata: 2026-10-12\n---\n# Review\n\n## Achados\n{prova}")
PR_VIEW_CI = ("pr", "view", "melhoria/x", "--json", "number,headRefOid,baseRefName")


def gh_do_ci(head, checks, pr_ok=True):
    """O `gh_json` com o PR de melhoria/x no `head` e os `checks`; `pr_ok=False` imita o gh sem rede; o resto, sem resposta."""
    respostas = {PR_VIEW_CI: ({"number": 7, "headRefOid": head, "baseRefName": "develop"}, "") if pr_ok else (None, "error connecting"),
                 PR_CHECKS: (checks, "")}
    return lambda _raiz, *args: respostas.get(args, (None, "sem rede"))


class ProvaDaSuiteBase(Repo):
    def entregar(self):
        """Base do Forge; na branch, bin/forge-x, um teste no topo e um num pacote, e o tests/test_velho.py apagado: os módulos de
        teste do diff são {test_forge_x, evals.test_y} (o apagado não roda)."""
        git("switch", "-q", "develop", cwd=self.tmp)
        self.base = self.commitar(FORGE, "forge")
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        git("merge", "-q", "develop", cwd=self.tmp)
        git("rm", "-q", "tests/test_velho.py", cwd=self.tmp)
        return self.commitar({"bin/forge-x": "print(1)\n", "tests/test_forge_x.py": "x = 1\n", "tests/evals/test_y.py": "y = 1\n"}, "codigo")

    def falta(self, commit, prova, campos=None):
        texto = REVIEW.format(c=commit, prova=prova)
        return fc.falta_na_prova(self.tmp, self.base, {"commit": commit} if campos is None else campos, texto)


class ProvaDaSuite(ProvaDaSuiteBase):
    def test_prova_que_cobre_os_modulos_do_diff_vale(self):
        head = self.entregar()
        self.assertEqual(fc.modulos_tocados(self.tmp, self.base, head), {"test_forge_x", "evals.test_y"})
        self.assertIsNone(self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge_x,test_forge,evals.test_y\n"))
        self.assertIsNone(self.falta(head[:12], f"- suíte: {head} rc=0 módulos=evals.test_y,test_forge_x\n"))  # `commit:` curto

    def test_sem_linha_outro_sha_rc_ou_modulo_faltando_nao_vale(self):
        head = self.entregar()
        todos = "módulos=test_forge_x,evals.test_y\n"
        self.assertIn("sem a linha `- suíte:", self.falta(head, ""))
        self.assertIn("sem a linha", self.falta(head, f"- suíte: {self.base} rc=0 {todos}"))
        self.assertIn("sem a linha", self.falta(head, f"- suíte: {head} rc=1 {todos}"))
        self.assertIn("sem a linha", self.falta("", f"- suíte: {head} rc=0 {todos}"))  # `commit:` vazio é prefixo de tudo
        self.assertIn("sem a linha", self.falta(head, f"- suíte: {head} rc=0 {todos}", campos={}))  # parecer sem `commit:`
        self.assertIn("falta evals.test_y", self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge_x\n"))

    def test_diff_sem_modulo_de_teste_aceita_a_lista_rodada(self):
        git("switch", "-q", "develop", cwd=self.tmp)
        self.base = self.commitar(FORGE, "forge")
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        head = self.commitar({"src/so_producao.py": "y = 2\n"}, "codigo")
        self.assertEqual(fc.modulos_tocados(self.tmp, self.base, head), set())
        self.assertIsNone(self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge\n"))

    def test_base_ou_git_ilegivel_falha_fechado(self):
        head = self.entregar()
        git("branch", "None", "develop", cwd=self.tmp)  # sem base, nada se lê: nem a ref de nome `None`
        self.assertIsNone(fc.modulos_tocados(self.tmp, None, head))
        self.assertIsNone(fc.modulos_tocados(self.tmp, "nao-existe", head))
        self.base = "nao-existe"
        self.assertIn("não foram lidos", self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge_x,evals.test_y\n"))


class CiVerdeNoHead(ProvaDaSuiteBase):
    def verde(self, head, checks, pr_ok=True, ref_head=None):
        with mock.patch.object(fc, "gh_json", gh_do_ci(head, checks, pr_ok)):
            return fc.ci_verde_no_head(self.tmp, "melhoria/x", ref_head or head)

    def test_verde_so_com_o_mesmo_head_e_tudo_em_pass(self):
        head = self.entregar()
        self.assertTrue(self.verde(head, FORGE_OK))
        self.assertTrue(self.verde(head, FORGE_OK + [ck("x", "skipping", "W")]))

    def test_pendente_vermelho_ausente_outro_head_ou_sem_rede_nao_e_verde(self):
        head = self.entregar()
        self.assertFalse(self.verde(head, FORGE_OK + [ck("x", "pending", "W")]))
        self.assertFalse(self.verde(head, FORGE_OK[1:]))  # exigido ausente
        self.assertFalse(self.verde(head, []))  # nenhum check: CI que não rodou não é verde
        self.assertFalse(self.verde(head, None))  # checks ilegíveis
        self.assertFalse(self.verde(self.base, FORGE_OK, ref_head=head))  # o PR está em outro head
        self.assertFalse(self.verde(head, FORGE_OK, pr_ok=False))  # sem rede
        with mock.patch.object(fc, "gh_json", gh_do_ci(head, FORGE_OK)):  # o gh acharia um PR verde: a guarda vem antes
            self.assertFalse(fc.ci_verde_no_head(self.tmp, None, head))
        with mock.patch.object(fc, "gh_json", gh_do_ci(None, FORGE_OK)):
            self.assertFalse(fc.ci_verde_no_head(self.tmp, "melhoria/x", None))


class SuiteNoCmdPr(ProvaDaSuiteBase):
    def violacoes(self, prova, suite=False, verde=False, forge=True):
        head = self.entregar()
        if not forge:
            git("rm", "-q", ".claude-plugin/plugin.json", cwd=self.tmp)
            git("commit", "-q", "-m", "sem forge", cwd=self.tmp)
            head = git("rev-parse", "HEAD", cwd=self.tmp)
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head, prova=prova.format(h=head))}, "review")
        erro = io.StringIO()
        with mock.patch.object(fc, "ci_verde_no_head", return_value=verde) as ci, contextlib.redirect_stderr(erro):
            linhas = fc.cmd_pr(self.tmp, "p1", None, self.base, "melhoria/x", suite=suite)
        self.ci = ci
        return [l for l in linhas if "PARECER-SO-COM-CI-VERDE" in l], ci.call_count, erro.getvalue()

    def test_sem_prova_e_sem_ci_verde_reprova(self):
        linhas, chamadas, _ = self.violacoes("")
        self.assertEqual(len(linhas), 1, linhas)
        self.assertTrue(linhas[0].startswith("docs/reviews/p1.md: suíte: o parecer aprovado só conta com o CI verde"), linhas)
        self.assertEqual(chamadas, 1)
        self.ci.assert_called_once_with(self.tmp, "melhoria/x", git("rev-parse", "HEAD", cwd=self.tmp))  # o head da ref, não o `commit:`

    def test_ci_verde_basta(self):
        self.assertEqual(self.violacoes("", verde=True)[0], [])

    def test_prova_basta_sem_ler_o_gh(self):
        linhas, chamadas, _ = self.violacoes("- suíte: {h} rc=0 módulos=test_forge_x,evals.test_y\n")
        self.assertEqual((linhas, chamadas), ([], 0))  # a prova local dispensa a leitura do gh

    def test_adiar_so_avisa_sem_ler_o_gh(self):
        linhas, chamadas, erro = self.violacoes("", suite=True)
        self.assertEqual((linhas, chamadas), ([], 0))
        self.assertIn("aviso: docs/reviews/p1.md: suíte:", erro)

    def test_sem_suite_a_catraca_nada_muda(self):
        self.assertEqual(self.violacoes("", suite=None)[0], [])  # a catraca: o próprio CI

    def test_fora_do_forge_nada_muda(self):
        self.assertEqual(self.violacoes("", forge=False)[0], [])


class SuitePeloPrDaCli(ProvaDaSuiteBase):
    """O `pr_da_cli` (o `forge-check pr`, o `brief gerar` e o passo 1 do `forge-fechar`) liga a guarda; o `--previo` e o passo 1 só
    avisam; `conferir=False` (o escopo da merge-integracao) não a liga."""

    def linhas(self, **kw):
        head = self.entregar()
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head, prova="")}, "review")
        sem_gh = mock.patch.object(fc, "gh_json", return_value=(None, "no git remotes found"))
        with sem_gh, mock.patch.object(fc, "ci_verde_no_head", return_value=False), contextlib.redirect_stderr(io.StringIO()):
            saida = fc.pr_da_cli(self.tmp, "p1", base="develop", **kw)
        return [l for l in saida if "PARECER-SO-COM-CI-VERDE" in l]

    def test_o_pr_reprova(self):
        self.assertEqual(len(self.linhas()), 1)

    def test_previo_so_avisa(self):
        self.assertEqual(self.linhas(previo=True), [])

    def test_passo_1_do_fechar_so_avisa(self):
        self.assertEqual(self.linhas(sem_checks=True), [])

    def test_sem_conferir_nao_liga(self):
        self.assertEqual(self.linhas(conferir=False), [])


class SuiteNoBriefSemPr(ProvaDaSuiteBase):
    """A1 do review (E47.5, sonda S1): o `brief gerar` de `pr` e de merge roda antes de o PR nascer (passo 3 do `forge-fechar`); sem
    PR, o review aprovado sem a prova não trava o brief: só o aviso, como no `--previo`. O `pr` direto segue reprovando."""

    def rodar(self, chamada):
        head = self.entregar()
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head, prova="")}, "review")
        sem_pr = mock.patch.object(fc, "gh_json", return_value=(None, "no pull requests found for branch \"melhoria/x\""))
        erro = io.StringIO()
        with sem_pr, contextlib.redirect_stderr(erro):
            saida = chamada()
        return [l for l in saida if "PARECER-SO-COM-CI-VERDE" in l], erro.getvalue()

    def test_etapas_que_recusam_nao_travam_sem_pr(self):
        for etapa in fc.ETAPAS_QUE_RECUSAM:
            with self.subTest(etapa=etapa):
                self.setUp()
                linhas, erro = self.rodar(lambda: fc.pareceres_da_etapa(self.tmp, "p1", etapa, "melhoria/x", "develop"))
                self.assertEqual(linhas, [])
                self.assertIn("aviso: docs/reviews/p1.md: suíte:", erro)

    def test_o_pr_direto_sem_pr_segue_reprovando(self):
        linhas, _ = self.rodar(lambda: fc.pr_da_cli(self.tmp, "p1", base="develop"))
        self.assertEqual(len(linhas), 1, linhas)


class BaseDaEtapa(unittest.TestCase):
    """GUARDAS-SEM-MUTANTE-0.47.12 (v0478 E62.11): a etapa passa ao `pr` a base do brief lida do remoto (`origin/<base>`); sem base,
    nenhuma, e o `pr` escolhe a do fluxo."""

    def base_passada(self, base):
        with mock.patch.object(fc, "pr_da_cli", return_value=[]) as pr:
            fc.pareceres_da_etapa("raiz", "p1", "pr", "melhoria/x", base)
        return pr.call_args.kwargs["base"]

    def test_base_do_brief_vai_ao_pr_pelo_remoto(self):
        self.assertEqual(self.base_passada("homolog"), "origin/homolog")
        self.assertEqual(self.base_passada("origin/develop"), "origin/develop")

    def test_sem_base_o_pr_escolhe(self):
        self.assertIsNone(self.base_passada(None))


class EsqueletoComAProva(unittest.TestCase):
    def test_review_e_qa_trazem_a_linha_da_prova_para_preencher(self):
        for tipo in ("review", "qa"):
            with self.subTest(tipo=tipo):
                texto = fc.esqueleto_do_parecer(tipo, "p1", "melhoria/x", "a" * 40, "aprovado", "2026-01-01")
                self.assertIn(f"- suíte: {fc.PREENCHER} rc=0 módulos={fc.PREENCHER}\n", texto)
                self.assertIn(f"- ci: {fc.PREENCHER} verde\n", texto)  # PARECER-LE-O-CI


# ---- PARECER-LE-O-CI (G3, v0481 E8.1) -------------------------------------------------------------------------------------------------
# No Forge, o review e o QA aprovados trazem `- ci: <sha40 do commit:> verde` (o portão leu o CI do head em vez de rodar a bateria);
# sem ela, o `forge-check pr` recusa, também no `--previo` e no passo 1 do `forge-fechar` (o `adiar`), com o CI verde ou a prova.
CI_LIDO = "- ci: {h} verde\n"
PROVA_COMPLETA = "- suíte: {h} rc=0 módulos=test_forge_x,evals.test_y\n"


class LeuOCi(unittest.TestCase):
    H = "c" * 40

    def test_linha_do_sha_do_commit_vale(self):
        self.assertTrue(fc.leu_o_ci({"commit": self.H}, f"x\n- ci: {self.H} verde\n"))
        self.assertTrue(fc.leu_o_ci({"commit": self.H[:12]}, f"- ci: {self.H} verde \n"))  # `commit:` curto casa o prefixo

    def test_sem_linha_outro_sha_outro_estado_ou_commit_invalido_nao_vale(self):
        self.assertFalse(fc.leu_o_ci({"commit": self.H}, ""))
        self.assertFalse(fc.leu_o_ci({"commit": self.H}, f"- ci: {'d' * 40} verde\n"))  # CI de outro sha
        self.assertFalse(fc.leu_o_ci({"commit": self.H}, f"- ci: {self.H} vermelho\n"))
        self.assertFalse(fc.leu_o_ci({"commit": self.H}, f"- ci: {self.H} verde, falta o e2e\n"))
        self.assertFalse(fc.leu_o_ci({"commit": self.H}, f"texto - ci: {self.H} verde\n"))  # só no começo da linha
        self.assertFalse(fc.leu_o_ci({"commit": ""}, f"- ci: {self.H} verde\n"))  # `commit:` vazio é prefixo de tudo
        self.assertFalse(fc.leu_o_ci({}, f"- ci: {self.H} verde\n"))
        self.assertFalse(fc.leu_o_ci({"commit": "zz"}, "- ci: zz verde\n"))  # `commit:` fora da forma de sha


class LeOCiNoCmdPr(ProvaDaSuiteBase):
    def violacoes(self, prova, suite=False, verde=True, forge=True, marca="PARECER-LE-O-CI", regra=True):
        head = self.entregar()
        if regra:  # o `commit:` revisado já traz a regra no bin/forge-check (`cobra_a_linha_do_ci`)
            head = self.commitar({"bin/forge-check": "# PARECER-LE-O-CI\n"}, "regra")
        if not forge:
            git("rm", "-q", ".claude-plugin/plugin.json", cwd=self.tmp)
            git("commit", "-q", "-m", "sem forge", cwd=self.tmp)
            head = git("rev-parse", "HEAD", cwd=self.tmp)
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head, prova=prova.format(h=head, b=self.base))}, "review")
        with mock.patch.object(fc, "ci_verde_no_head", return_value=verde), contextlib.redirect_stderr(io.StringIO()):
            linhas = fc.cmd_pr(self.tmp, "p1", None, self.base, "melhoria/x", suite=suite)
        return [l for l in linhas if marca in l]

    def test_sem_a_linha_recusa_com_ci_verde_ou_com_a_prova(self):
        for prova in ("", PROVA_COMPLETA):
            with self.subTest(prova=prova):
                self.setUp()
                linhas = self.violacoes(prova)
                self.assertEqual(len(linhas), 1, linhas)
                self.assertTrue(linhas[0].startswith("docs/reviews/p1.md: ci: o parecer aprovado traz a linha `- ci:"), linhas)

    def test_sem_a_linha_recusa_tambem_no_adiar(self):
        for prova in ("", PROVA_COMPLETA):
            with self.subTest(prova=prova):
                self.setUp()
                self.assertEqual(len(self.violacoes(prova, suite=True)), 1)

    def test_linha_de_outro_sha_ou_vermelha_recusa(self):
        for linha in ("- ci: {b} verde\n", "- ci: {h} vermelho\n"):
            with self.subTest(linha=linha):
                self.setUp()
                self.assertEqual(len(self.violacoes(linha + PROVA_COMPLETA)), 1)

    def test_com_a_linha_e_ci_verde_passa(self):
        for prova in (CI_LIDO, CI_LIDO + PROVA_COMPLETA):
            with self.subTest(prova=prova):
                self.setUp()
                self.assertEqual(self.violacoes(prova, marca="(PARECER-"), [])  # nem a linha do CI nem a da suíte

    def test_a_linha_nao_dispensa_o_ci_verde_do_head(self):
        self.assertEqual(len(self.violacoes(CI_LIDO, verde=False, marca="PARECER-SO-COM-CI-VERDE")), 1)

    def test_sem_a_linha_e_sem_ci_verde_saem_as_duas(self):
        self.assertEqual(len(self.violacoes("", verde=False, marca="(PARECER-")), 2)

    def test_catraca_e_fora_do_forge_nada_muda(self):
        self.assertEqual(self.violacoes("", suite=None), [])  # a catraca: o próprio CI
        self.setUp()
        self.assertEqual(self.violacoes("", forge=False), [])

    # A3 do #893 (transição): o parecer cujo `commit:` é anterior à regra (as branches abertas) não é cobrado da linha, e a
    # PARECER-SO-COM-CI-VERDE segue inteira nele: nada que barrava antes deixa de barrar.
    def test_commit_anterior_a_regra_nao_cobra_a_linha(self):
        for suite in (False, True):
            with self.subTest(suite=suite):
                self.setUp()
                self.assertEqual(self.violacoes("", suite=suite, regra=False), [])

    def test_commit_anterior_a_regra_segue_com_o_ci_verde_do_head(self):
        self.assertEqual(len(self.violacoes("", verde=False, regra=False, marca="PARECER-SO-COM-CI-VERDE")), 1)

    def test_cobra_a_linha_com_commit_fora_da_forma_ou_erro_do_git(self):
        self.entregar()
        self.assertFalse(fc.cobra_a_linha_do_ci(self.tmp, {"commit": git("rev-parse", "HEAD", cwd=self.tmp)}))  # sem a regra
        self.assertTrue(fc.cobra_a_linha_do_ci(self.tmp, {"commit": "f" * 40}))  # sha que não existe: o git falha, cobra
        self.assertTrue(fc.cobra_a_linha_do_ci(self.tmp, {"commit": "--cached"}))  # não vira opção do git grep
        self.assertTrue(fc.cobra_a_linha_do_ci(self.tmp, {}))


# ---- G3.7 (v0481 E8.10): `- ci: <sha40 do commit:> verde via <sha40 do descendente>` ----------------------------------------------
# O envio de um parecer cancela o run do `Revisar-sha`; vale o run verde de um descendente cujo diff só toca as pastas dos pareceres.
PARECERES_SO = {"docs/reviews/p0.md": "r\n", "docs/qa/p0.md": "q\n", "docs/security/p0.md": "s\n"}


class LeOCiVia(ProvaDaSuiteBase):
    def preparar(self, depois=None):
        """O `commit:` revisado (com a regra) e um descendente que soma `depois` (por padrão, só pareceres)."""
        self.entregar()
        self.head = self.commitar({"bin/forge-check": "# PARECER-LE-O-CI\n"}, "regra")
        self.desc = self.commitar(PARECERES_SO if depois is None else depois, "pareceres")

    def vale(self, linha, commit=None):
        return fc.leu_o_ci_via(self.tmp, {"commit": self.head if commit is None else commit}, linha)

    def test_descendente_so_de_pareceres_vale(self):
        self.preparar()
        self.assertTrue(self.vale(f"x\n- ci: {self.head} verde via {self.desc}\n"))
        self.assertTrue(self.vale(f"- ci: {self.head} verde via {self.desc} \n", commit=self.head[:12]))  # `commit:` curto
        self.assertTrue(fc.so_pareceres_ate(self.tmp, self.head, self.head))  # o próprio sha: diff vazio

    def test_outro_caminho_no_diff_nao_vale(self):
        self.preparar({"docs/reviews/p0.md": "r\n", "bin/forge-x": "print(2)\n"})
        self.assertFalse(self.vale(f"- ci: {self.head} verde via {self.desc}\n"))

    def test_branco_no_inicio_do_caminho_nao_vale(self):
        # A1 do #895: o 1º caminho do `-z` não perde o espaço, o tab nem a quebra de linha iniciais (pasta fora das três)
        self.preparar()
        for nome in (" docs/reviews/x.py", "\tdocs/security/x.py", "\ndocs/qa/x.py"):
            with self.subTest(nome=nome):
                git("reset", "-q", "--hard", self.head, cwd=self.tmp)  # um caminho por vez, sobre o `commit:`
                desc = self.commitar({nome: "print(1)\n"}, "branco")
                self.assertFalse(fc.so_pareceres_ate(self.tmp, self.head, desc))

    def test_gitlink_fora_das_pastas_nao_some(self):
        # recomendado do QA no #895: `diff.ignoreSubmodules=all` na configuração não esconde o gitlink
        self.preparar()
        git("config", "diff.ignoreSubmodules", "all", cwd=self.tmp)
        git("update-index", "--add", "--cacheinfo", f"160000,{self.base},bin/sub", cwd=self.tmp)
        git("commit", "-q", "-m", "gitlink", cwd=self.tmp)
        self.assertFalse(fc.so_pareceres_ate(self.tmp, self.head, git("rev-parse", "HEAD", cwd=self.tmp)))

    def test_renomeacao_para_a_pasta_do_parecer_nao_vale(self):
        self.preparar()
        git("mv", "bin/forge-x", "docs/reviews/forge-x", cwd=self.tmp)
        git("commit", "-q", "-m", "mv", cwd=self.tmp)
        desc = git("rev-parse", "HEAD", cwd=self.tmp)
        self.assertFalse(self.vale(f"- ci: {self.head} verde via {desc}\n"))

    def test_nao_descendente_ou_sha_inexistente_nao_vale(self):
        self.preparar()
        # a mesma árvore do descendente sobre a base: o diff só toca pareceres, mas não descende do `commit:`
        irmao = git("commit-tree", f"{self.desc}^{{tree}}", "-p", self.base, "-m", "irmao", cwd=self.tmp)
        for via in (irmao, self.base, "f" * 40):
            with self.subTest(via=via):
                self.assertFalse(self.vale(f"- ci: {self.head} verde via {via}\n"))

    def test_outro_sha_outro_estado_ou_commit_invalido_nao_vale(self):
        self.preparar()
        self.assertFalse(self.vale(f"- ci: {self.desc} verde via {self.desc}\n"))  # o primeiro sha não é o `commit:`
        self.assertFalse(self.vale(f"- ci: {self.head} vermelho via {self.desc}\n"))
        self.assertFalse(self.vale(f"- ci: {self.head} verde via {self.desc}, falta o e2e\n"))
        self.assertFalse(self.vale(f"- ci: {self.head} verde via {self.desc}\n", commit=""))  # vazio é prefixo de tudo
        self.assertFalse(self.vale(f"- ci: {self.head} verde via {self.desc}\n", commit="zz"))
        self.assertFalse(fc.leu_o_ci_via(self.tmp, {}, f"- ci: {self.head} verde via {self.desc}\n"))  # parecer sem `commit:`

    def test_erro_do_git_diff_falha_fechado(self):
        self.preparar()
        real = fc.git

        def git_falso(raiz, *args, **kw):
            return (128, b"") if args[0] == "diff" else real(raiz, *args, **kw)
        with mock.patch.object(fc, "git", git_falso):
            self.assertFalse(fc.so_pareceres_ate(self.tmp, self.head, self.desc))

    def pr(self, linha):
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=self.head, prova=linha)}, "review")
        with mock.patch.object(fc, "ci_verde_no_head", return_value=True), contextlib.redirect_stderr(io.StringIO()):
            return [l for l in fc.cmd_pr(self.tmp, "p1", None, self.base, "melhoria/x", suite=False) if "PARECER-LE-O-CI" in l]

    def test_cmd_pr_aceita_o_via_so_de_pareceres(self):
        self.preparar()
        self.assertEqual(self.pr(f"- ci: {self.head} verde via {self.desc}\n"), [])

    def test_cmd_pr_recusa_o_via_que_nao_descende(self):
        self.preparar()  # código depois do `commit:` já deixa o parecer desatualizado; aqui, o `via` é a base (ancestral)
        linhas = self.pr(f"- ci: {self.head} verde via {self.base}\n")
        self.assertEqual(len(linhas), 1, linhas)
        self.assertIn("verde via", linhas[0])


if __name__ == "__main__":
    unittest.main()
