"""Testes da lógica pura do scripts/ci-local (resumo, status, regra do pulado, leitura dos workflows), sem rede e sem git."""
import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

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

    def test_nenhum_job_e_opcional_e_so_actionlint_e_zizmor_sao_passos_opcionais(self):
        self.assertEqual(ci.NAO_OBRIGATORIOS, set())
        self.assertEqual(ci.FERRAMENTAS_OPCIONAIS, {"actionlint", "zizmor"})


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

    def test_if_com_escape_de_aspas_nao_executa_nada(self):
        """Regressão B1: `'\\'` fechava o literal na validação e abria código no eval."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            marca = Path(d) / "executou"
            carga = ("'\\' == ' and [x for x in ().__class__.__base__.__subclasses__() if x.__name__ == \"Popen\"][0]"
                     f"([\"touch\", \"{marca}\"]).wait() == 0 #'")
            self.assertFalse(ci.avaliar_se(carga, self.ctx))  # são dois literais diferentes comparados: nada é executado
            self.assertFalse(marca.exists())
            with self.assertRaises(ValueError):  # e a variante que sobra código fora de literal é recusada
                ci.avaliar_se("'a' == 'b' and __import__('os').system('touch " + str(marca) + "')", self.ctx)
            self.assertFalse(marca.exists())
            job = {"id": "j", "nome": "j", "se": "__import__('os').system('touch " + str(marca) + "')", "passos": [
                {"nome": "p", "se": "", "env": {}, "run": "true\n"}]}
            r = ci.rodar_job(job, self.ctx, Path(d), "b" * 40, Path(d))
            self.assertEqual((r["estado"], r["ausente"]), (ci.PULADO, True))
            self.assertIn("suporte", r["motivo"])
            self.assertFalse(marca.exists())

    def test_if_literal_com_aspa_dobrada_e_precedencia(self):
        ctx = {**self.ctx, "github.head_ref": "it's"}
        self.assertTrue(ci.avaliar_se("github.head_ref == 'it''s'", ctx))
        self.assertTrue(ci.avaliar_se("'a' == 'b' || 'a' == 'a' && 'c' != 'd'", ctx))
        self.assertFalse(ci.avaliar_se("('a' == 'b' || 'a' == 'a') && 'c' == 'd'", ctx))

    def test_if_malformado_e_recusado(self):
        for ruim in ("github.base_ref ==", "(github.base_ref == 'develop'", "'a' 'b'", "github.base_ref == 'x' )", "x"):
            with self.assertRaises(ValueError, msg=ruim):
                ci.avaliar_se(ruim, self.ctx)

    def test_expandir_troca_expressoes_conhecidas_e_apaga_desconhecidas(self):
        self.assertEqual(ci.expandir("${{ github.base_ref }}/${{ nada.disso }}", self.ctx), "develop/")


class LeituraDosWorkflowsTest(unittest.TestCase):
    def test_workflows_do_forge_listam_a_bateria_inteira(self):
        ids = []
        for arquivo in ci.WORKFLOWS:
            ids += [j["id"] for j in ci.ler_jobs((RAIZ / ".github" / "workflows" / arquivo).read_text(encoding="utf-8"))]
        esperados = {"rapida", "bateria", "catraca"}
        self.assertTrue(esperados <= set(ids), esperados - set(ids))

    def test_bateria_consolidada_mantem_os_passos_que_eram_jobs(self):
        (bateria,) = [j for j in ci.ler_jobs((RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
                      if j["id"] == "bateria"]
        comandos = "\n".join(p["run"] for p in bateria["passos"])
        for trecho in ("unittest discover", "shellcheck", "actionlint", "zizmor", "claude plugin validate", "e2e-instalacao",
                       "[Não publicado]", "Nada pula degrau", "verificar-contribuicao"):
            self.assertIn(trecho, comandos + "\n".join(p["nome"] for p in bateria["passos"]))

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


class AvisosTest(unittest.TestCase):
    def test_chaves_ignoradas_geram_aviso(self):
        texto = ("env:\n  A: 1\ndefaults:\n  run:\n    shell: sh\njobs:\n  j:\n    env:\n      X: 1\n    steps:\n"
                 "      - name: p\n        working-directory: sub\n        shell: sh\n        run: echo\n")
        avisos = " ".join(ci.avisos_do_workflow("w.yml", texto))
        for chave in ("env", "defaults", "working-directory", "shell"):
            self.assertIn(chave, avisos)

    def test_workflow_sem_chaves_ignoradas_nao_avisa(self):
        self.assertEqual(ci.avisos_do_workflow("w.yml", "jobs:\n  j:\n    steps:\n      - run: echo\n        env:\n          A: 1\n"), [])

    def test_head_pai_restante_gera_aviso(self):
        self.assertTrue(ci.avisos_do_script("git rev-parse HEAD~1"))
        self.assertFalse(ci.avisos_do_script("echo ok"))


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

    def passo(self, nome, run):
        return {"nome": nome, "se": "", "env": {}, "run": run}

    def test_actionlint_ausente_pula_so_o_passo_e_o_resto_do_job_roda(self):
        job = {"id": "j", "nome": "j", "se": "", "passos": [self.passo("lint", "actionlint -color\n"), self.passo("p", "true\n")]}
        original = ci.shutil.which
        ci.shutil.which = lambda _nome: None
        try:
            r = self.rodar(job)
        finally:
            ci.shutil.which = original
        self.assertEqual(r["estado"], ci.OK)

    def test_ferramenta_obrigatoria_ausente_continua_reprovando_com_actionlint_ausente(self):
        job = {"id": "j", "nome": "j", "se": "", "passos": [self.passo("lint", "actionlint\n"), self.passo("s", "shellcheck x\n")]}
        original = ci.shutil.which
        ci.shutil.which = lambda _nome: None
        try:
            r = self.rodar(job)
        finally:
            ci.shutil.which = original
        self.assertEqual((r["estado"], r["ausente"]), (ci.PULADO, True))
        self.assertIn("shellcheck", r["motivo"])

    def test_ferramenta_ausente_pula_como_ausencia(self):
        original = ci.shutil.which
        ci.shutil.which = lambda _nome: None
        try:
            r = self.rodar(self.job("shellcheck --version\n"))
        finally:
            ci.shutil.which = original
        self.assertEqual((r["estado"], r["ausente"], r["obrigatorio"]), (ci.PULADO, True, True))
        self.assertIn("shellcheck", r["motivo"])

    def test_sem_shell_nao_ha_pipefail_como_no_github(self):
        """Regressão B3: sem `shell:` o Actions roda `bash -e {0}`; `false | true` passa."""
        self.assertEqual(self.rodar(self.job("false | true\n"))["estado"], ci.OK)

    def test_shell_bash_declarado_ativa_pipefail(self):
        job = self.job("false | true\n")
        job["passos"][0]["shell"] = "bash"
        self.assertEqual(self.rodar(job)["estado"], ci.FALHOU)

    def test_leitor_guarda_o_shell_do_passo(self):
        (job,) = ci.ler_jobs("jobs:\n  j:\n    steps:\n      - name: p\n        shell: bash\n        run: echo\n")
        self.assertEqual(job["passos"][0]["shell"], "bash")

    def test_contexto_github_desconhecido_no_if_e_sem_suporte(self):
        with self.assertRaises(ValueError):
            ci.avaliar_se("github.nao_existe == ''", self.ctx)

    def test_if_aninhado_demais_e_sem_suporte_legivel(self):
        with self.assertRaises(ValueError) as c:
            ci.avaliar_se("(" * 5000 + "'a'" + ")" * 5000, self.ctx)
        self.assertIn("aninhada", str(c.exception))

    def test_token_so_chega_ao_passo_que_o_declara(self):
        ctx = ci.contexto_do_pr(PR, "b" * 40, "segredo")
        job = {"id": "j", "nome": "j", "se": "", "passos": [
            {"nome": "sem", "se": "", "env": {}, "run": '[ -z "${GITHUB_TOKEN-}" ]\n'},
            {"nome": "com", "se": "", "env": {"GITHUB_TOKEN": "${{ github.token }}"}, "run": '[ "$GITHUB_TOKEN" = segredo ]\n'}]}
        import tempfile
        old = ci.os.environ.get("GITHUB_TOKEN")
        ci.os.environ["GITHUB_TOKEN"] = "do-usuario"
        try:
            with tempfile.TemporaryDirectory() as d:
                self.assertEqual(ci.rodar_job(job, ctx, Path(d), "b" * 40, Path(d))["estado"], ci.OK)
        finally:
            if old is None:
                ci.os.environ.pop("GITHUB_TOKEN")
            else:
                ci.os.environ["GITHUB_TOKEN"] = old

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


class PortoesDeSegurancaTest(unittest.TestCase):
    """Regressões do review de segurança: A1 (fork), A2 (ambiente mínimo), C1 (symlink) e D (status autodeclarado)."""
    PR_BASE = {**PR, "state": "OPEN", "isCrossRepository": False, "headRepositoryOwner": {"login": "dona"}}

    def principal(self, pr, *args):
        """Roda main() com `gh` simulado; devolve (SystemExit ou None, comandos executados). O fetch falha de propósito."""
        chamadas = []

        def gh(*a):
            return {"pr": pr, "repo": {"nameWithOwner": "dona/repo"}}[a[0]]

        def rodar(args, **kw):
            chamadas.append(list(args))
            out = "/repo\n" if args[:2] == ["git", "rev-parse"] else ""
            return ci.subprocess.CompletedProcess(args, 1 if args[:2] == ["git", "fetch"] else 0, out, "")

        velho = (ci.gh_json, ci.rodar)
        ci.gh_json, ci.rodar = gh, rodar
        try:
            try:
                ci.main(["7", *args])
                erro = None
            except SystemExit as e:
                erro = e
        finally:
            ci.gh_json, ci.rodar = velho
        return erro, chamadas

    def test_pr_de_fork_e_recusado_antes_de_buscar_ou_criar_worktree(self):
        erro, chamadas = self.principal({**self.PR_BASE, "isCrossRepository": True, "headRepositoryOwner": {"login": "fulano"}})
        self.assertIn("fork", str(erro.code))
        self.assertFalse([c for c in chamadas if c[:2] in (["git", "fetch"], ["git", "worktree"])])

    def test_pr_de_fork_com_confiar_segue_e_avisa(self):
        erro, chamadas = self.principal({**self.PR_BASE, "isCrossRepository": True}, "--confiar")
        self.assertIn("buscar", str(erro.code))  # passou do portão e foi até o fetch
        self.assertTrue([c for c in chamadas if c[:2] == ["git", "fetch"]])

    def test_pr_do_mesmo_repositorio_segue_sem_confiar(self):
        erro, _ = self.principal(self.PR_BASE)
        self.assertIn("buscar", str(erro.code))

    def test_pedido_ao_gh_inclui_origem_da_cabeca(self):
        import inspect
        self.assertIn("isCrossRepository", inspect.getsource(ci.main))
        self.assertIn("headRepositoryOwner", inspect.getsource(ci.main))

    def test_passo_so_ve_ambiente_da_lista_branca(self):
        import tempfile
        nomes = {"FORGE_TESTE_CRED_TOKEN": "x", "FORGE_TESTE_PROXY_PASSWORD": "y", "LC_ALL": "C"}
        job = {"id": "j", "nome": "j", "se": "", "passos": [
            {"nome": "sem", "se": "", "env": {}, "run": 'env | grep -c "^FORGE_TESTE_" | grep -qx 0\n'},
            {"nome": "lc", "se": "", "env": {}, "run": '[ "$LC_ALL" = C ] && [ -n "$PATH" ]\n'},
            {"nome": "decl", "se": "", "env": {"FORGE_TESTE_DECLARADA": "v"}, "run": '[ "$FORGE_TESTE_DECLARADA" = v ]\n'}]}
        antigo = dict(ci.os.environ)
        ci.os.environ.update(nomes)
        try:
            with tempfile.TemporaryDirectory() as d:
                r = ci.rodar_job(job, ci.contexto_do_pr(PR, "b" * 40), Path(d), "b" * 40, Path(d))
        finally:
            ci.os.environ.clear()
            ci.os.environ.update(antigo)
        self.assertEqual(r["estado"], ci.OK, r)

    def test_ambiente_minimo_filtra_por_nome(self):
        env = ci.ambiente_minimo({"PATH": "/bin", "HOME": "/h", "LC_TIME": "C", "AWS_X": "1", "GITHUB_TOKEN": "t"})
        self.assertEqual(set(env), {"PATH", "HOME", "LC_TIME"})

    def test_workflow_symlink_conta_como_ausente(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "alvo.yml").write_text("jobs:\n", encoding="utf-8")
            (d / "ci.yml").symlink_to(d / "alvo.yml")
            (d / "ok.yml").write_text("jobs:\n", encoding="utf-8")
            self.assertIsNone(ci.ler_workflow(d / "ci.yml"))
            self.assertIsNone(ci.ler_workflow(d / "nao-existe.yml"))
            self.assertEqual(ci.ler_workflow(d / "ok.yml"), "jobs:\n")

    def test_publicar_recusa_pr_que_altera_a_propria_bateria(self):
        for arquivo in (".github/workflows/ci.yml", "tests/catraca.py"):
            with self.assertRaises(SystemExit) as c:
                ci.recusar_publicacao(["README.md", arquivo])
            self.assertIn("--publicar recusado", str(c.exception.code))
        ci.recusar_publicacao(["README.md", "tests/test_x.py", ".github/dependabot.yml"])

    def repo_com(self, d, antes, depois):
        """Repositório descartável: `antes` vira o commit base; `depois` (renomeações e edições) vira a cabeça."""
        import subprocess
        def git(*a):
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a],
                           cwd=d, check=True, capture_output=True, env=sem_manutencao())
        git("init", "-q")
        for nome in antes:
            (Path(d) / nome).parent.mkdir(parents=True, exist_ok=True)
            (Path(d) / nome).write_text("conteudo identico\n" * 20, encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, text=True, capture_output=True,
                              env=sem_manutencao()).stdout.strip()
        depois(git, Path(d))
        git("add", "-A")
        git("commit", "-q", "-m", "cabeca")
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, text=True, capture_output=True,
                              env=sem_manutencao()).stdout.strip()
        return base, sha

    def test_publicar_recusa_renomear_a_catraca(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            base, sha = self.repo_com(d, ["tests/catraca.py", "README.md"], lambda git, r: git("mv", "tests/catraca.py", "tests/outro.py"))
            alterados = ci.arquivos_alterados(d, base, sha)
            self.assertIn("tests/catraca.py", alterados)
            with self.assertRaises(SystemExit) as c:
                ci.recusar_publicacao(alterados)
            self.assertIn("--publicar recusado", str(c.exception.code))

    def test_publicar_recusa_se_o_git_diff_falha(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            base, _ = self.repo_com(d, ["README.md"], lambda git, r: (r / "x.txt").write_text("x"))
            with self.assertRaises(SystemExit) as c:
                ci.arquivos_alterados(d, base, "0" * 40)  # sha inexistente: o git diff falha
            self.assertIn("git diff", str(c.exception.code))

    def test_publicar_deixa_passar_pr_que_so_altera_o_readme(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            def mexe(git, r):
                (r / "README.md").write_text("outro texto\n", encoding="utf-8")
            base, sha = self.repo_com(d, ["README.md", "tests/catraca.py"], mexe)
            alterados = ci.arquivos_alterados(d, base, sha)
            self.assertEqual(alterados, ["README.md"])
            ci.recusar_publicacao(alterados)

    def test_publicar_recusa_no_fluxo_principal_antes_de_rodar_a_bateria(self):
        chamadas = []

        def rodar(args, **kw):
            chamadas.append(list(args))
            out = {"rev-parse": "/repo\n", "merge-base": "c" * 40 + "\n", "diff": ".github/workflows/ci.yml\0"}.get(args[1], "")
            return ci.subprocess.CompletedProcess(args, 0, out, "")

        velho = (ci.gh_json, ci.rodar)
        ci.gh_json = lambda *a: self.PR_BASE if a[0] == "pr" else {"nameWithOwner": "dona/repo"}
        ci.rodar = rodar
        try:
            with self.assertRaises(SystemExit) as c:
                ci.main(["7", "--publicar"])
        finally:
            ci.gh_json, ci.rodar = velho
        self.assertIn("--publicar recusado", str(c.exception.code))
        self.assertFalse([x for x in chamadas if x[:2] == ["git", "worktree"] or x[0] == "gh"])

    def test_ajuda_diz_que_o_status_e_autodeclarado(self):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            ci.main(["--help"])
        self.assertIn("AUTODECLARADO", buf.getvalue())
        self.assertIn("--confiar", buf.getvalue())


class SinalTest(unittest.TestCase):
    """INT e TERM num processo real: limpam a worktree e a pasta temporária, rc 128+sinal, sem traceback."""

    def setUp(self):
        import json
        import os
        import subprocess
        import tempfile
        self.os, self.subprocess = os, subprocess
        self.dir = Path(tempfile.mkdtemp(prefix="sinal."))
        self.addCleanup(__import__("shutil").rmtree, self.dir, True)
        origem, repo, binp, self.tmp = (self.dir / n for n in ("origem.git", "repo", "bin", "tmp"))
        for d in (binp, self.tmp):
            d.mkdir()
        git = lambda *a, cwd=repo: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True,
                                                  env=sem_manutencao({**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                                                                     "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}))
        self.git = git
        git("init", "-q", "--bare", str(origem), cwd=self.dir)
        git("init", "-q", "-b", "develop", str(repo), cwd=self.dir)
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / ".github" / "workflows" / "ci.yml").write_text(
            "name: CI\njobs:\n  lento:\n    name: lento\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - name: espera\n        run: |\n          echo comecou > \"$RUNNER_TEMP/../../comecou\"\n          sleep 120\n")
        git("add", "-A")
        git("commit", "-q", "-m", "x")
        git("remote", "add", "origin", str(origem))
        git("push", "-q", "origin", "develop")
        sha = git("rev-parse", "HEAD").stdout.strip()
        git("push", "-q", "origin", f"{sha}:refs/pull/7/head")
        pr = {"number": 7, "headRefOid": sha, "headRefName": "melhoria/x", "baseRefName": "develop", "body": "",
              "author": {"login": "a"}, "state": "OPEN", "isCrossRepository": False, "headRepositoryOwner": {"login": "a"}}
        gh = binp / "gh"
        gh.write_text(f"#!/bin/sh\ncase \"$1 $2\" in\n 'pr view') cat <<'J'\n{json.dumps(pr)}\nJ\n;;\n"
                      " 'repo view') echo '{\"nameWithOwner\": \"a/b\"}';;\n 'auth token') echo tok;;\nesac\n")
        gh.chmod(0o755)
        self.repo = repo
        self.env = {**os.environ, "PATH": f"{binp}:{os.environ['PATH']}", "TMPDIR": str(self.tmp)}

    def _interromper(self, sinal):
        p = self.subprocess.Popen([str(RAIZ / "scripts" / "ci-local"), "7"], cwd=self.repo, env=self.env,
                                  stdout=self.subprocess.PIPE, stderr=self.subprocess.STDOUT, text=True)
        import time
        marca = self.tmp / "comecou"
        for _ in range(300):
            if marca.exists() or any(self.tmp.glob("ci-local.*/**/comecou")) or p.poll() is not None:
                break
            time.sleep(0.1)
        time.sleep(0.5)
        self.assertIsNone(p.poll(), "o script terminou antes do sinal")
        p.send_signal(sinal)
        saida, _ = p.communicate(timeout=30)
        return p.returncode, saida

    def _confere(self, rc, saida, esperado):
        self.assertEqual(rc, esperado, saida)
        self.assertNotIn("Traceback", saida)
        self.assertIn("interrompido", saida)
        self.assertEqual(list(self.tmp.glob("ci-local.*")), [])
        self.assertNotIn("ci-local.", self.git("worktree", "list").stdout)

    def test_int_limpa_e_sai_130_sem_traceback(self):
        import signal
        self._confere(*self._interromper(signal.SIGINT), 130)

    def test_term_limpa_e_sai_143_sem_traceback(self):
        import signal
        self._confere(*self._interromper(signal.SIGTERM), 143)


if __name__ == "__main__":
    unittest.main()
