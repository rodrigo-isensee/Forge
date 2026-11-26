"""D2-PORTAO-ENTREGA-AUTOR (v0481 E11.1): o `forge-check pronto`, o portão de entrega do autor (bin/forge_pronto.py).

As checagens externas são as que já existem (forge-testes e as classes de neutralidade); aqui o teste prova o agregador com comandos
falsos, o teto e o corpo com o pr-texto falso, e o `cmd_pronto` de verdade num repositório descartável (base ausente, corpo ilegível,
corpo nenhum).
"""
import contextlib
import importlib.machinery
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "bin"))
import forge_pronto  # noqa: E402

sys.path.insert(0, str(RAIZ / "tests"))
from ambiente_git import sem_manutencao  # noqa: E402

PY = sys.executable
OK, FALHA = (PY, "-I", "-c", "pass"), (PY, "-I", "-c", "import sys; print('saida da falha'); sys.exit(3)")
SAI_2 = (PY, "-I", "-c", "import sys; sys.exit(2)")  # o passo sem veredito (o --afetados que não decide, o comando que não abre)
CORPO_COM_MOTIVO = "teto: excedido, 151 linhas, cortar mais quebra a suíte\n"
# gh falso: só o `gh pr view develop --json ...` com o nome exato da branch (checklist 12); outra chamada sai 3.
GH = '#!/bin/sh\n[ "$1 $2 $3" = "pr view develop" ] || exit 3\n'
SEM_PR = GH + 'echo "no pull requests found for branch" >&2\nexit 1\n'
COM_PR = GH + 'echo \'{"number": 7, "state": "%s", "headRefOid": "x", "body": "corpo do pr"}\'\n'
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "GH_", "GITHUB_"))})


def conferir(lista, falhas=(), corpo="", sem_corpo=None):
    saida, erro = io.StringIO(), io.StringIO()
    with mock.patch.object(forge_pronto, "tamanho_e_corpo", return_value=list(falhas)) as teto, \
            mock.patch.object(forge_pronto, "passos", return_value=[("dos passos", FALHA)]), \
            contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
        rc = forge_pronto.conferir(".", "origin/develop", "abc", 10, corpo, lista, sem_corpo=sem_corpo)
    return rc, saida.getvalue(), erro.getvalue(), teto


class Agregador(unittest.TestCase):
    def test_tudo_passa_sai_0(self):
        rc, saida, _, _ = conferir([("a", OK), ("b", OK)])
        self.assertEqual(rc, 0)
        self.assertIn("pronto: a: ok", saida)
        self.assertIn("pronto: tamanho e corpo do PR (10 linhas de código): ok", saida)
        self.assertIn("tudo passou", saida)

    def test_uma_checagem_reprovada_sai_1_e_mostra_a_saida(self):
        rc, saida, erro, _ = conferir([("a", OK), ("b", FALHA)])
        self.assertEqual(rc, 1)
        self.assertIn("pronto: b: reprovado (saída 3)", saida)
        self.assertIn("reprovado em b;", saida)
        self.assertIn("saida da falha", erro)

    def test_teto_ou_corpo_reprovado_sai_1(self):
        rc, saida, erro, _ = conferir([("a", OK)], ["falha do corpo"])
        self.assertEqual(rc, 1)
        self.assertIn("reprovado em tamanho e corpo do PR", saida)
        self.assertIn("pronto: tamanho e corpo do PR (10 linhas de código): reprovado", saida)
        self.assertIn("pronto: falha do corpo", erro)

    def test_passo_que_sai_2_fica_nao_verificavel_e_sai_2(self):
        rc, saida, _, _ = conferir([("a", OK), ("b", SAI_2)])
        self.assertEqual(rc, 2)
        self.assertIn("pronto: b: não verificável (saída 2)", saida)
        self.assertIn("pronto: não verificável em b;", saida)
        self.assertNotIn("tudo passou", saida)

    def test_reprovada_vence_o_nao_verificavel(self):
        rc, saida, _, _ = conferir([("a", SAI_2), ("b", FALHA)])
        self.assertEqual(rc, 1)
        self.assertIn("reprovado em b;", saida)

    def test_gh_em_erro_sem_corpo_sai_2_com_o_motivo(self):
        rc, saida, _, teto = conferir([("a", OK)], corpo=None, sem_corpo="gh sem rede ou sem acesso")
        self.assertEqual(rc, 2)
        self.assertIn("tamanho e corpo do PR: não verificável (gh sem rede ou sem acesso)", saida)
        self.assertIn("não verificável em tamanho e corpo do PR", saida)
        teto.assert_not_called()

    def test_motivo_com_corpo_dado_confere_o_corpo(self):
        rc, _, _, teto = conferir([("a", OK)], ["falha do corpo"], corpo="o corpo", sem_corpo="gh sem rede")
        self.assertEqual(rc, 1)
        teto.assert_called_once()

    def test_comando_que_nao_abre_sai_2(self):
        self.assertEqual(forge_pronto.rodar(".", ["/nao/existe/comando"])[0], 2)

    def test_passos_cobrem_as_checagens_do_cartao(self):
        lista = dict(forge_pronto.passos("origin/x"))
        self.assertEqual(list(lista), ["registros", "neutralidade", "texto", "testes"])
        self.assertIn("tests.test_forge.NeutralidadeDoNucleo", lista["neutralidade"])
        self.assertEqual(lista["testes"][-2:], ["--base", "origin/x"])


class TamanhoECorpo(unittest.TestCase):
    def falhas(self, total, corpo, rc=0):
        with mock.patch.object(forge_pronto, "rodar", return_value=(rc, "violação do pr-texto")) as rodar:
            return forge_pronto.tamanho_e_corpo(".", "abc", total, corpo), rodar

    def test_sem_corpo_reprova_sem_rodar_a_catraca(self):
        falhas, rodar = self.falhas(10, None)
        self.assertEqual(len(falhas), 1)
        self.assertIn("--corpo", falhas[0])
        rodar.assert_not_called()

    def test_acima_do_teto_sem_motivo_reprova(self):
        falhas, _ = self.falhas(151, "corpo")
        self.assertEqual(len(falhas), 1)
        self.assertIn("tamanho: 151 linhas", falhas[0])

    def test_acima_do_teto_com_motivo_e_no_teto_passam(self):
        self.assertEqual(self.falhas(151, CORPO_COM_MOTIVO)[0], [])
        self.assertEqual(self.falhas(150, "corpo")[0], [])

    def test_pr_texto_reprovado_reprova_com_o_corpo_no_ambiente(self):
        falhas, rodar = self.falhas(10, "corpo", rc=1)
        self.assertEqual(len(falhas), 1)
        self.assertIn("violação do pr-texto", falhas[0])
        self.assertEqual(rodar.call_args.args[2]["PR_BODY"], "corpo")


class CmdPronto(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.dir)])
        for args in (["init", "-q", "-b", "develop"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
                                                         "-m", "base"]):
            subprocess.run(["git", "-C", str(self.dir), *args], check=True, env=AMBIENTE)

    def pronto(self, *args, gh=SEM_PR):
        falsos = self.dir / "falsos"
        falsos.mkdir(exist_ok=True)
        (falsos / "gh").write_text(gh, encoding="utf-8")
        (falsos / "gh").chmod(0o755)
        env = dict(AMBIENTE, PATH=f"{falsos}{os.pathsep}{AMBIENTE.get('PATH', '')}")
        return subprocess.run([PY, "-I", str(RAIZ / "bin" / "forge-check"), "--raiz", str(self.dir), "pronto", *args],
                              capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, cwd=self.dir)

    def test_base_ausente_sai_2(self):
        r = self.pronto("--base", "nao-existe")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("não verificável", r.stderr)

    def test_corpo_ilegivel_sai_2(self):
        r = self.pronto("--base", "develop", "--corpo", str(self.dir / "sem-arquivo.md"))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("ilegível", r.stderr)

    def test_corpo_do_arquivo_chega_ao_portao(self):
        (self.dir / "corpo.md").write_text("o corpo", encoding="utf-8")
        r = self.pronto("--base", "develop", "--corpo", str(self.dir / "corpo.md"))
        self.assertIn("pronto: tamanho e corpo do PR (0 linhas de código)", r.stdout, r.stderr)
        self.assertNotIn("corpo do PR não conferido", r.stderr)

    def test_sem_corpo_e_sem_pr_reprova(self):
        r = self.pronto("--base", "develop")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("corpo do PR não conferido", r.stderr)

    def test_pr_aberto_da_o_corpo_e_fechado_nao(self):
        r = self.pronto("--base", "develop", gh=COM_PR % "OPEN")
        self.assertNotIn("corpo do PR não conferido", r.stderr)
        self.assertIn("pronto: tamanho e corpo do PR (0 linhas de código)", r.stdout, r.stderr)
        r = self.pronto("--base", "develop", gh=COM_PR % "CLOSED")
        self.assertIn("corpo do PR não conferido", r.stderr)

    def test_gh_em_erro_deixa_o_corpo_nao_verificavel(self):
        r = self.pronto("--base", "develop", gh=GH + 'echo "erro de rede" >&2\nexit 1\n')
        self.assertNotEqual(r.returncode, 0, r.stderr)  # os passos reprovam no repositório descartável; o rc 2 do corpo: Agregador
        self.assertIn("tamanho e corpo do PR: não verificável (gh sem rede ou sem acesso)", r.stdout)
        self.assertNotIn("corpo do PR não conferido", r.stderr)


# --- D2-NO-BRIEF e PR-TITULO-DO-BRIEF (v0481 E14.51) ---------------------------------------------------------------------
carregador = importlib.machinery.SourceFileLoader("forge_check_pronto_d2", str(RAIZ / "bin" / "forge-check"))
fc = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
carregador.exec_module(fc)
TITULO_DO_BRIEF = "E14.51 (tech-lead): [branch melhoria/x] D2-NO-BRIEF: o brief manda rodar o pronto"
TITULO_BOM = "feat(pronto): o brief manda rodar o D2 (v0481 E14.51)"
COM_TITULO = GH + 'case "$*" in *,title*) ;; *) exit 4 ;; esac\necho \'{"number": 7, "state": "OPEN", "headRefOid": "x", "body": "corpo", "title": "%s"}\'\n'


class TituloDoPr(unittest.TestCase):
    def falhas(self, titulo):
        with mock.patch.object(forge_pronto, "rodar", return_value=(0, "")):
            return forge_pronto.tamanho_e_corpo(".", "abc", 10, "corpo", titulo)

    def test_titulo_com_o_cabecalho_do_brief_reprova(self):
        for titulo in (TITULO_DO_BRIEF, "[branch melhoria/x] D2-NO-BRIEF", "  E3 (qa): o aceite"):
            with self.subTest(titulo=titulo):
                falhas = self.falhas(titulo)
                self.assertEqual(len(falhas), 1)
                self.assertIn("PR-TITULO-DO-BRIEF", falhas[0])

    def test_titulo_de_conventional_commits_e_sem_titulo_passam(self):
        for titulo in (TITULO_BOM, "fix(fechar): E3 (qa) citado no meio", None, ""):
            with self.subTest(titulo=titulo):
                self.assertEqual(self.falhas(titulo), [])


class TituloNoCmdPronto(unittest.TestCase):
    """O `cmd_pronto` lê o título do PR aberto pelo gh e o passa ao portão (sem herdar os testes do `CmdPronto`)."""
    setUp, pronto = CmdPronto.setUp, CmdPronto.pronto

    def test_pr_aberto_com_o_titulo_do_brief_reprova(self):
        r = self.pronto("--base", "develop", gh=COM_TITULO % TITULO_DO_BRIEF)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("título do PR é a linha da etapa do brief", r.stderr)
        r = self.pronto("--base", "develop", gh=COM_TITULO % TITULO_BOM)
        self.assertNotIn("PR-TITULO-DO-BRIEF", r.stderr)


class BaseVelha(unittest.TestCase):
    """PRONTO-BASE-VELHA: a branch nascida antes da última marca de versão da base recebe uma linha que manda trazer a base, em vez
    das checagens que listariam os fragmentos dos outros itens; a `origin/<ramo>` é buscada antes de comparar."""
    pronto = CmdPronto.pronto

    def git(self, pasta, *args):
        return subprocess.run(["git", "-C", str(pasta), *args], check=True, env=AMBIENTE, capture_output=True, text=True).stdout

    def versao(self, pasta, numero):
        (pasta / ".claude-plugin").mkdir(exist_ok=True)
        (pasta / ".claude-plugin" / "plugin.json").write_text('{"name": "forge", "version": "%s"}\n' % numero, encoding="utf-8")
        self.git(pasta, "add", ".claude-plugin")
        self.git(pasta, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", f"marca {numero}")

    def setUp(self):
        raiz = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(raiz)])
        self.origem, self.dir = raiz / "origem", raiz / "copia"
        self.git(raiz, "init", "-q", "-b", "develop", str(self.origem))
        self.versao(self.origem, "1.0.0")
        self.git(raiz, "clone", "-q", str(self.origem), str(self.dir))
        self.git(self.dir, "switch", "-q", "-c", "melhoria/x")
        self.versao(self.origem, "1.0.1")  # a marca entra na base depois que a branch nasceu; a cópia ainda não a buscou

    def test_marca_depois_do_nascimento_manda_trazer_a_base_sem_rodar_as_checagens(self):
        r = self.pronto("--base", "origin/develop")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("pronto: reprovado em base velha: a origin/develop tem a marca da 1.0.1 e a branch nasceu na 1.0.0; traga a base",
                      r.stdout)
        self.assertNotIn("pronto: registros", r.stdout)

    def test_com_a_base_trazida_nao_ha_linha_de_base_velha(self):
        self.git(self.dir, "fetch", "-q", "origin")
        self.git(self.dir, "merge", "-q", "--ff-only", "origin/develop")
        r = self.pronto("--base", "origin/develop")
        self.assertNotIn("base velha", r.stdout + r.stderr)
        self.assertIn("pronto: registros", r.stdout)

    def test_sem_versao_no_nascimento_nao_compara(self):  # fora do Forge, ou base que ganhou o manifesto depois: nada a dizer
        self.git(self.dir, "switch", "-q", "--orphan", "nascimento")
        self.git(self.dir, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "sem manifesto")
        self.git(self.dir, "switch", "-q", "-c", "com-manifesto")
        self.versao(self.dir, "1.0.0")
        self.git(self.dir, "switch", "-q", "nascimento")
        r = self.pronto("--base", "com-manifesto")
        self.assertNotIn("base velha", r.stdout)
        self.assertIn("pronto: registros", r.stdout)


class Resultado:
    def __init__(self, rc, saida="", erro=""):
        self.returncode, self.stdout, self.stderr = rc, saida, erro


class ProvaDoPronto(unittest.TestCase):
    """D2-NO-BRIEF: a conferência da entrega roda o pronto deste forge-check com `--raiz` na worktree; fora do rc 0 não cumpre."""
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.pasta)])
        (self.pasta / ".claude-plugin").mkdir()
        (self.pasta / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")

    def prova(self, resultado=None, so_leitura=False, pasta="padrão", erro=None, forge_no_head=False):
        rodar = mock.Mock(return_value=resultado, side_effect=erro)
        linhas = fc.prova_do_pronto(self.pasta if pasta == "padrão" else pasta, "develop", so_leitura, rodar, forge_no_head=forge_no_head)
        return linhas, rodar

    def test_rc_0_e_prova_sem_reprovar_com_o_pronto_da_worktree(self):
        linhas, rodar = self.prova(Resultado(0))
        self.assertEqual(linhas, [("prova: forge-check pronto rc 0 na worktree (D2)", False)])
        argv = rodar.call_args.args[0]
        self.assertEqual(argv[2:], ["--raiz", str(self.pasta), "pronto", "--base", "origin/develop"])
        self.assertEqual(rodar.call_args.kwargs["cwd"], self.pasta)

    def test_rc_1_e_rc_2_reprovam_com_a_ultima_linha(self):
        linhas, _ = self.prova(Resultado(1, "pronto: registros: reprovado (saída 1)\npronto: reprovado em registros; corrija\n",
                                         "o fim da saída do passo, no stderr\n"))
        self.assertEqual(linhas, [("pendente: D2 vermelho: forge-check pronto rc 1: pronto: reprovado em registros; corrija "
                                   "(D2-NO-BRIEF)", True)])
        linhas, _ = self.prova(Resultado(2, "", "pronto: não verificável: sem base\n"))
        self.assertTrue(linhas[0][1])
        self.assertIn("rc 2: pronto: não verificável: sem base", linhas[0][0])

    def test_pronto_que_nao_termina_reprova(self):
        linhas, _ = self.prova(erro=subprocess.TimeoutExpired("x", 1))
        self.assertTrue(linhas[0][1])
        self.assertIn("não terminou (TimeoutExpired)", linhas[0][0])

    def test_sem_worktree_com_o_head_no_forge_reprova_pedindo_worktree(self):
        """E14.81, sondas da revisão de segurança fe150b0 (a cópia do autor é clone, sem worktree no repositório de quem confere):
        S1 `python3 -I _sec75-v0481-d2nb-sonda.py <clone> (prova_do_pronto(None, "develop", False))`, espera reprovar;
        S2 `git -C /workspaces/Forge worktree list --porcelain, procurando melhoria/v0481-d2-no-brief`, sem a worktree da branch;
        S3 `comando_permitido(["bin/forge-check","pronto","--base","origin/develop"]) do scripts/reexecutar-provas.py`, fora da lista:
        a PQ do D2 não é cobrada por outra via, por isso a falta de worktree reprova aqui."""
        linhas, rodar = self.prova(Resultado(0), pasta=None, forge_no_head=True)
        rodar.assert_not_called()
        self.assertEqual(linhas, [("pendente: D2 sem worktree da branch para rodar o forge-check pronto (passe --worktree <cópia do "
                                   "autor>) (D2-NO-BRIEF)", True)])
        linhas, rodar = self.prova(Resultado(0), pasta=None, forge_no_head=True, so_leitura=True)
        rodar.assert_not_called()
        self.assertFalse(linhas[0][1])

    def test_so_leitura_sem_worktree_fora_do_forge_e_fora_do_forge_nao_rodam(self):
        (self.pasta / "fora").mkdir()
        for kw in ({"so_leitura": True}, {"so_leitura": True, "forge_no_head": True}, {"pasta": None},
                   {"pasta": self.pasta / "fora"}):
            with self.subTest(**{k: str(v) for k, v in kw.items()}):
                linhas, rodar = self.prova(Resultado(1), **kw)
                rodar.assert_not_called()
                self.assertFalse(linhas[0][1])
                self.assertIn("última linha do `forge-check pronto` no relatório do autor", linhas[0][0])


HEAD = "a" * 40
VERDES = [{"name": "bateria (python 3.14)", "bucket": "pass", "workflow": "CI"}, {"name": "shellcheck", "bucket": "skipping", "workflow": "CI"},
          {"name": "bateria", "bucket": "pending", "workflow": "CI"}, {"name": "bateria (pareceres)", "bucket": "fail", "workflow": "CI"},
          {"name": "catraca", "bucket": "fail", "workflow": "Catraca"}]


class ProvaDoCi(unittest.TestCase):
    """G3-ENTREGA-PELO-CI (v0481 E28.1): no Forge, a entrega prova o pronto pelo CI do PR concluído e verde no head exato, fora os
    CHECKS_FORA_DA_LINHA_DO_CI; o gh falso responde só ao `pr view <branch exata>` e ao `pr checks <número>` (checklist 12)."""
    def prova(self, heads=(HEAD, HEAD), checks=VERDES, exigidos=("CI/bateria (python 3.14)", "Catraca/catraca", "CI/bateria")):
        heads, chamadas = list(heads), []

        def gh_json(raiz, *args):
            chamadas.append(args)
            if args[:3] == ("pr", "view", "melhoria/x"):
                h = heads.pop(0)
                return ({"number": 9, "headRefOid": h, "baseRefName": "develop"}, "") if h else (None, "sem resposta em 10 s")
            if args[:3] == ("pr", "checks", "9"):
                return (checks, "") if checks is not None else (None, "erro de rede")
            return None, "chamada inesperada"
        with mock.patch.object(fc, "gh_json", gh_json), mock.patch.object(fc, "checks_exigidos", lambda raiz, destino: list(exigidos)):
            return fc.prova_do_ci(Path("."), "melhoria/x", HEAD), chamadas

    def test_ci_verde_no_head_prova_sem_os_checks_fora_da_linha(self):
        linhas, chamadas = self.prova()
        self.assertEqual(len(linhas), 1)
        self.assertFalse(linhas[0][1])
        self.assertTrue(linhas[0][0].startswith(f"prova: CI do PR #9 concluído e verde no head {HEAD[:12]} (2 checks, fora "), linhas)
        self.assertEqual([c[:2] for c in chamadas], [("pr", "view"), ("pr", "checks"), ("pr", "view")])

    def test_vermelho_e_pendente_reprovam_com_o_check(self):
        for bucket in ("fail", "pending"):
            with self.subTest(bucket=bucket):
                linhas, _ = self.prova(checks=[{"name": "bateria (python 3.14)", "bucket": bucket, "workflow": "CI"}], exigidos=())
                self.assertEqual(linhas, [(f"pendente: CI do PR #9 no head {HEAD[:12]} não concluído e verde: CI/bateria (python 3.14) "
                                           f"({bucket}) (G3-ENTREGA-PELO-CI)", True)])

    def test_exigido_ausente_e_nenhum_check_reprovam(self):
        linhas, _ = self.prova(checks=[{"name": "shellcheck", "bucket": "pass", "workflow": "CI"}])
        self.assertTrue(linhas[0][1])
        self.assertIn("CI/bateria (python 3.14) (exigido, ausente)", linhas[0][0])
        self.assertNotIn("Catraca/catraca", linhas[0][0])
        linhas, _ = self.prova(checks=[{"name": "catraca", "bucket": "pass", "workflow": "Catraca"}], exigidos=())
        self.assertEqual(linhas, [(f"pendente: CI do PR #9 no head {HEAD[:12]} não concluído e verde: nenhum check (G3-ENTREGA-PELO-CI)",
                                   True)])

    def test_head_diferente_reprova_sem_ler_os_checks(self):
        linhas, chamadas = self.prova(heads=("b" * 40,))
        self.assertEqual(linhas, [(f"pendente: o PR #9 está em bbbbbbbbbbbb, não no head entregue {HEAD[:12]}; envie o head e espere o "
                                   "CI (G3-ENTREGA-PELO-CI)", True)])
        self.assertEqual(len(chamadas), 1)

    def test_head_mudado_entre_as_leituras_reprova(self):
        for depois in ("b" * 40, None):
            with self.subTest(depois=depois):
                linhas, _ = self.prova(heads=(HEAD, depois))
                self.assertTrue(linhas[0][1])
                self.assertIn("não lidos (gh pr checks ou head mudado)", linhas[0][0])

    def test_sem_rede_nao_verificavel_reprova(self):
        linhas, _ = self.prova(heads=(None,))
        self.assertEqual(linhas, [("pendente: CI do GitHub não verificável (gh pr view: sem resposta em 10 s); a entrega só cumpre com o "
                                   "CI do PR verde no head (G3-ENTREGA-PELO-CI)", True)])
        linhas, _ = self.prova(checks=None)
        self.assertTrue(linhas[0][1])
        self.assertIn("checks do PR #9 no head", linhas[0][0])
