"""Testes da lógica pura do scripts/ci-local (resumo, status, regra do pulado, leitura dos workflows), sem rede e sem git."""
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_loader = importlib.machinery.SourceFileLoader("ci_local", str(RAIZ / "scripts" / "ci-local"))
ci = importlib.util.module_from_spec(importlib.util.spec_from_loader("ci_local", _loader))
_loader.exec_module(ci)

PR = {"number": 7, "headRefOid": "a" * 40, "headRefName": "melhoria/x", "baseRefName": "develop",
      "body": "texto", "author": {"login": "dona"}}


class StatusTest(unittest.TestCase):
    def test_tudo_ok_e_success(self):
        rs = [ci.resultado("a", ci.OK), ci.resultado("b", ci.OK)]
        self.assertEqual(ci.status(rs), ("success", "2 ok / 0 falharam"))

    def test_job_que_falhou_e_failure(self):
        rs = [ci.resultado("a", ci.OK), ci.resultado("b", ci.FALHOU, "saiu com 1")]
        self.assertEqual(ci.status(rs), ("failure", "1 ok / 1 falharam"))

    def test_pulado_obrigatorio_por_ausencia_e_failure(self):
        rs = [ci.resultado("a", ci.OK), ci.resultado("plugin", ci.PULADO, "claude ausente", obrigatorio=True, ausente=True)]
        self.assertEqual(ci.status(rs), ("failure", "1 ok / 1 falharam"))

    def test_pulado_opcional_por_ausencia_nao_reprova(self):
        rs = [ci.resultado("a", ci.OK), ci.resultado("workflows", ci.PULADO, "sem actionlint", obrigatorio=False, ausente=True)]
        self.assertEqual(ci.status(rs), ("success", "1 ok / 0 falharam / 1 pulados"))

    def test_pulado_por_nao_se_aplicar_nao_reprova_mesmo_obrigatorio(self):
        rs = [ci.resultado("a", ci.OK), ci.resultado("pr-texto", ci.PULADO, "não se aplica", obrigatorio=True, ausente=False)]
        self.assertEqual(ci.status(rs)[0], "success")

    def test_workflows_e_o_unico_job_opcional(self):
        self.assertEqual(ci.NAO_OBRIGATORIOS, {"workflows"})


class ResumoTest(unittest.TestCase):
    def test_uma_linha_por_job_com_estado_e_motivo(self):
        rs = [ci.resultado("testes", ci.OK), ci.resultado("segredos", ci.FALHOU, "saiu com 1"),
              ci.resultado("plugin", ci.PULADO, "claude ausente", ausente=True),
              ci.resultado("pr-texto", ci.PULADO, "não se aplica")]
        linhas = ci.resumo(rs).splitlines()
        self.assertEqual(len(linhas), 4)
        self.assertIn("OK", linhas[0])
        self.assertIn("FALHOU (saiu com 1)", linhas[1])
        self.assertIn("PULADO (obrigatório: conta como falha) (claude ausente)", linhas[2])
        self.assertTrue(linhas[3].rstrip().endswith("PULADO (não se aplica)"))


class ExpressoesTest(unittest.TestCase):
    ctx = ci.contexto_do_pr(PR, "b" * 40)

    def test_if_vazio_vale(self):
        self.assertTrue(ci.avaliar_se("", self.ctx))

    def test_if_do_job_versao(self):
        se = "github.event_name == 'pull_request' && (github.base_ref == 'develop' || github.base_ref == 'main')"
        self.assertTrue(ci.avaliar_se(se, self.ctx))
        self.assertFalse(ci.avaliar_se(se, {**self.ctx, "github.base_ref": "homolog"}))

    def test_if_do_pr_texto_exclui_dependabot(self):
        se = "github.base_ref == 'develop' && github.event.pull_request.user.login != 'dependabot[bot]'"
        self.assertTrue(ci.avaliar_se(se, self.ctx))
        self.assertFalse(ci.avaliar_se(se, {**self.ctx, "github.event.pull_request.user.login": "dependabot[bot]"}))

    def test_if_fora_do_subconjunto_e_recusado(self):
        with self.assertRaises(ValueError):
            ci.avaliar_se("__import__('os').system('x') == 1", self.ctx)

    def test_expandir_troca_expressoes_conhecidas_e_apaga_desconhecidas(self):
        self.assertEqual(ci.expandir("${{ github.base_ref }}/${{ nada.disso }}", self.ctx), "develop/")


class LeituraDosWorkflowsTest(unittest.TestCase):
    def test_workflows_do_forge_listam_a_bateria_inteira(self):
        ids = []
        for arquivo in ci.WORKFLOWS:
            ids += [j["id"] for j in ci.ler_jobs((RAIZ / ".github" / "workflows" / arquivo).read_text(encoding="utf-8"))]
        esperados = {"testes", "shell", "workflows", "plugin", "instalacao", "versao", "fluxo", "segredos", "pareceres", "catraca", "pr-texto"}
        self.assertTrue(esperados <= set(ids), esperados - set(ids))

    def test_passo_com_bloco_env_e_if(self):
        texto = (
            "jobs:\n  j:\n    name: Meu job\n    if: github.base_ref == 'develop'\n    steps:\n"
            "      - uses: actions/checkout@abc\n        with:\n          fetch-depth: 0\n"
            "      - name: Passo\n        if: github.base_ref == 'main'\n        env:\n          BASE: ${{ github.base_ref }}\n"
            "        run: |\n          echo um\n\n          echo dois\n"
        )
        (job,) = ci.ler_jobs(texto)
        self.assertEqual((job["id"], job["nome"], job["se"]), ("j", "Meu job", "github.base_ref == 'develop'"))
        (passo,) = [p for p in job["passos"] if p["run"]]
        self.assertEqual(passo["run"], "echo um\n\necho dois\n")
        self.assertEqual(passo["env"], {"BASE": "${{ github.base_ref }}"})
        self.assertEqual(passo["se"], "github.base_ref == 'main'")


class RodarJobTest(unittest.TestCase):
    ctx = ci.contexto_do_pr(PR, "b" * 40)

    def job(self, run, se=""):
        return {"id": "j", "nome": "j", "se": se, "passos": [{"nome": "p", "se": "", "env": {}, "run": run}]}

    def rodar(self, job):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            return ci.rodar_job(job, self.ctx, Path(d), "b" * 40, Path(d))

    def test_passo_que_sai_com_zero_e_ok_e_com_erro_falha(self):
        self.assertEqual(self.rodar(self.job("true\n"))["estado"], ci.OK)
        self.assertEqual(self.rodar(self.job("false\n"))["estado"], ci.FALHOU)

    def test_if_falso_pula_sem_ser_ausencia(self):
        r = self.rodar(self.job("false\n", se="github.base_ref == 'main'"))
        self.assertEqual((r["estado"], r["ausente"]), (ci.PULADO, False))

    def test_ferramenta_ausente_pula_como_ausencia(self):
        original = ci.shutil.which
        ci.shutil.which = lambda _nome: None
        try:
            r = self.rodar(self.job("shellcheck --version\n"))
        finally:
            ci.shutil.which = original
        self.assertEqual((r["estado"], r["ausente"], r["obrigatorio"]), (ci.PULADO, True, True))
        self.assertIn("shellcheck", r["motivo"])

    def test_base_do_pr_substitui_o_primeiro_pai_do_merge(self):
        r = self.rodar(self.job('[ "$(git rev-parse HEAD^1)" = "' + "b" * 40 + '" ]\n'))
        self.assertEqual(r["estado"], ci.OK)

    def test_cada_job_tem_seu_runner_temp(self):
        """Regressão: dois jobs criavam `$RUNNER_TEMP/base` e o segundo falhava com 'already exists'."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for jid in ("a", "b"):
                job = {**self.job('mkdir "$RUNNER_TEMP/base"\n'), "id": jid}
                self.assertEqual(ci.rodar_job(job, self.ctx, Path(d), "b" * 40, Path(d))["estado"], ci.OK)


if __name__ == "__main__":
    unittest.main()
