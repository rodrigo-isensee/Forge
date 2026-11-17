"""E3.45 (v0474): o `forge-check pr` só aprova para merge com os checks do head concluídos e verdes e os exigidos do destino em pass.

Num projeto, um PR foi mesclado com o CI rodando e a integração ficou vermelha 74 min. Sem rede (R-CUSTO): o `gh` é a função
`gh_json` trocada por respostas simuladas, casadas pelo comando inteiro (nada de prefixo); o head e o "é o Forge" também são simulados.
"""
import contextlib
import io
import os
import shutil
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

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
    def rodar(self, checks=None, pr=None, regras=None, protecao=None, forge=False, previo=False, branch="melhoria/x", erro_checks=""):
        """`checks_do_head` com as respostas do `gh` por comando exato; comando sem resposta devolve (None, "") como o gh sem rede."""
        pr = {"number": 7, "state": "OPEN", "isDraft": False, "headRefOid": HEAD, "baseRefName": "develop"} if pr is None else pr
        respostas = {PR_VIEW: (pr, ""), PR_CHECKS: (checks, erro_checks), REGRAS: (regras, ""), PROTECAO: (protecao, "")}
        self.chamadas = []

        def gh_json(_raiz, *args):
            self.chamadas.append(args)
            return respostas.get(args, (None, ""))
        with mock.patch.object(fc, "gh_json", gh_json), mock.patch.object(fc, "sha_do_commit", lambda _r, _ref: HEAD), \
                mock.patch.object(fc, "e_o_forge", lambda _r: forge), contextlib.redirect_stderr(io.StringIO()):
            return fc.checks_do_head(Path("/nao-existe"), "refs/heads/melhoria/x", branch, previo)

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
        self.assertEqual(self.gh("echo 'x{'\n"), (None, ""))


class ParesIguaisAoFechar(unittest.TestCase):
    def test_os_pares_do_forge_sao_os_do_forge_fechar(self):
        texto = (RAIZ / "bin" / "forge-fechar").read_text(encoding="utf-8")
        linha = next(l for l in texto.splitlines() if l.startswith("readonly CHECKS_EXIGIDOS=("))
        self.assertEqual(linha, "readonly CHECKS_EXIGIDOS=(" + " ".join(f'"{p}"' for p in fc.CHECKS_EXIGIDOS_DO_FORGE) + ")")


if __name__ == "__main__":
    unittest.main()
