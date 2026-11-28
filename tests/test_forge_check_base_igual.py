"""E7 (0.45.6, E7.1): o arquivo que veio da base não desatualiza o parecer. No `forge-check pr` (`commit_vale` com `dominio`), no
`forge-check parecer delta` e na catraca `--modo pareceres` (que chama o `cmd_pr` com a base do servidor), sai o caminho cujo modo e
conteúdo no head são os da ponta da base e que a branch não tinha mudado no commit do parecer. O arquivo mudado pela branch, antes ou
depois do parecer (também o desfeito), segue desatualizando. A ref `origin/<base>` é forjável no cliente (A1 de docs/reviews/v0455.md):
a garantia é a catraca do CI, que recebe a base real."""
import ast
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
fc = SourceFileLoader("forge_check_base_igual", str(AQUI.parent / "bin" / "forge-check")).load_module()
_spec = importlib.util.spec_from_file_location("catraca_base_igual", AQUI / "catraca.py")
catraca = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(catraca)


class BaseIgual(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.git("init", "-q", "-b", "develop")
        self.escreve("bin/a", "a\n")
        self.escreve("bin/f", "f\n")
        self.commit("base")
        self.git("switch", "-q", "-c", "ramo")
        self.escreve("bin/a", "a da branch\n")
        self.parecer = self.commit("trabalho revisado")
        self.git("switch", "-q", "develop")
        self.escreve("bin/f", "f da develop\n")
        self.da_develop = self.commit("outro item na develop")
        self.git("switch", "-q", "ramo")

    def git(self, *args):
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        r = subprocess.run(["git", "-C", str(self.dir), "-c", "user.name=t", "-c", "user.email=t@t",
                            "-c", "commit.gpgsign=false", *args], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def escreve(self, nome, texto):
        (self.dir / nome).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / nome).write_text(texto)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def vale(self, base="develop"):
        return fc.commit_vale(self.dir, self.parecer, "HEAD", base, dominio="review")

    def parecer_no_ramo(self):
        self.escreve("docs/reviews/ramo.md", f"---\ntipo: review\ncontrato: 1\npedido: ramo\nbranch: ramo\ncommit: {self.parecer}\n"
                                             "parecer: aprovado\nrevisor: forge:tech-lead\ndata: 2026-11-10\n---\n# x\n")
        self.commit("parecer")

    def delta(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            rc = fc.cmd_parecer_delta(self.dir, "docs/reviews/ramo.md")
        return rc, saida.getvalue()

    def catraca(self):  # como no CI: a base é a ponta real da develop (o primeiro pai do merge do checkout)
        return " ".join(catraca.violacoes_de_pareceres(self.dir, self.da_develop, self.git("rev-parse", "HEAD"), "ramo", "develop"))

    def test_trazido_sem_merge_nao_desatualiza(self):  # cherry-pick da develop: o bin/f fica igual ao da ponta da base
        self.git("cherry-pick", self.da_develop)
        self.assertIsNone(self.vale())
        self.parecer_no_ramo()
        self.assertEqual([l for l in fc.cmd_pr(self.dir, "ramo", "HEAD", "develop") if "desatualizado" in l], [])

    def test_sem_dominio_segue_estrito(self):  # a conferência de entrega (sem `dominio`) não muda
        self.git("cherry-pick", self.da_develop)
        self.assertIn("desatualizado: bin/f mudou", fc.commit_vale(self.dir, self.parecer, "HEAD", "develop") or "")

    def test_mudado_pela_branch_desatualiza(self):
        self.escreve("bin/f", "f da branch\n")
        self.commit("mudança da branch depois do parecer")
        self.assertIn("desatualizado: bin/f mudou", self.vale() or "")

    def test_desfeito_pela_branch_desatualiza(self):  # a branch tinha mudado bin/a no parecer e o devolveu à base
        self.escreve("bin/a", "a\n")
        self.commit("desfaz")
        self.assertIn("desatualizado: bin/a mudou", self.vale() or "")

    def test_igual_a_base_com_outro_modo_desatualiza(self):
        self.git("cherry-pick", self.da_develop)
        (self.dir / "bin/f").chmod(0o755)
        self.commit("executável")
        self.assertIn("desatualizado: bin/f mudou", self.vale() or "")

    def test_ref_forjada_no_cliente_e_o_ci_reprova(self):  # A1 da v0455: a garantia é a base do servidor
        self.escreve("bin/f", "f da branch\n")
        self.commit("mudança da branch depois do parecer")
        self.parecer_no_ramo()
        forjada = self.git("commit-tree", self.git("rev-parse", "HEAD^{tree}"), "-p", self.da_develop, "-m", "forjada")
        self.git("update-ref", "refs/remotes/origin/develop", forjada)
        self.assertIsNone(self.vale("refs/remotes/origin/develop"))  # a forja esconde no cliente
        self.assertIn("desatualizado: bin/f mudou", self.catraca())

    def test_catraca_ignora_o_que_veio_da_base(self):  # segue pedindo o parecer de segurança (bin/ é classe C), não o review novo
        self.git("cherry-pick", self.da_develop)
        self.parecer_no_ramo()
        achadas = self.catraca()
        self.assertIn("revisao-seguranca: sem parecer", achadas)
        self.assertNotIn("desatualizado", achadas)

    def test_parecer_delta_separa_o_que_veio_da_base(self):
        self.git("cherry-pick", self.da_develop)
        self.escreve("bin/g", "g da branch\n")
        self.commit("arquivo novo da branch")
        self.parecer_no_ramo()
        rc, saida = self.delta()
        self.assertEqual(rc, 0, saida)
        self.assertIn('da base: "bin/f"', saida)
        self.assertIn('no dominio: "bin/g"', saida)
        self.assertNotIn('no dominio: "bin/f"', saida)

    def test_git_que_falha_nao_tira_nada(self):  # falha fechada
        self.git("cherry-pick", self.da_develop)
        self.assertEqual(fc.vindos_da_base(self.dir, "nao-existe", self.parecer, "HEAD", ["bin/f"]), set())
        with self.assertRaises(fc.ArvoreIlegivel):
            fc.entradas_da_arvore(self.dir, "nao-existe", ["bin/f"])

    def test_merge_base_que_falha_nao_e_ausencia(self):  # base órfã com a árvore do head: sem merge-base, o bin/g novo não sai
        self.escreve("bin/g", "g da branch\n")
        self.commit("arquivo novo da branch")
        orfa = self.git("commit-tree", self.git("rev-parse", "HEAD^{tree}"), "-m", "órfão")
        self.assertEqual(fc.vindos_da_base(self.dir, orfa, self.parecer, "HEAD", ["bin/g"]), set())


class JuncaoSemBase(unittest.TestCase):
    """E2.201 (v047): o `forge-check pr` sem `--base`, numa branch de trabalho, usa a develop; trazê-la por merge limpo não vence o
    parecer por arquivo que a branch não mudou (o .github/workflows/ci.yml do caso real); o que a branch mudou depois segue vencendo."""
    setUp, git, escreve, commit, parecer_no_ramo = (BaseIgual.setUp, BaseIgual.git, BaseIgual.escreve, BaseIgual.commit,
                                                    BaseIgual.parecer_no_ramo)

    def prepara(self, branch="ramo"):
        self.git("switch", "-q", "develop")
        self.escreve(".github/workflows/ci.yml", "on: push\n")
        self.commit("ci da develop")
        self.git("switch", "-q", "-C", branch, self.parecer)
        self.parecer_no_ramo()
        self.git("merge", "-q", "--no-edit", "develop")

    def desatualizados(self):
        return " ".join(l for l in fc.pr_da_cli(self.dir, "ramo", conferir=False) if "desatualizado" in l)

    def test_merge_limpo_da_develop_nao_vence(self):  # falha na base: ".github/workflows/ci.yml mudou depois do parecer"
        self.prepara()
        self.assertEqual(self.desatualizados(), "")

    def test_mudado_pela_branch_depois_do_parecer_vence(self):
        self.prepara()
        self.escreve("bin/a", "a mudado depois do parecer\n")
        self.commit("mudança da branch depois do parecer")
        self.assertIn("desatualizado: bin/a mudou", self.desatualizados())

    def test_branch_de_integracao_segue_o_diff_literal(self):  # na `main`, sem `--base`, a develop não vira base implícita
        self.prepara("main")
        self.assertIn("desatualizado: .github/workflows/ci.yml mudou", self.desatualizados())


class MergeQueDescartaABase(unittest.TestCase):
    """F3 (v0481 E30.4, segurança A2 de ae38993): o merge da base que a descarta (`-s ours`, conflito resolvido com o lado da branch)
    deixa o head igual ao do parecer nos arquivos da base; sem o merge simulado, o parecer seguia valendo e o PR desfaria a base."""
    setUp, git, escreve, commit = BaseIgual.setUp, BaseIgual.git, BaseIgual.escreve, BaseIgual.commit
    DOMINIOS = ("review", "revisao-seguranca")

    def motivos(self):
        return [fc.commit_vale(self.dir, self.parecer, "HEAD", "develop", dominio=d) for d in self.DOMINIOS]

    def test_merge_limpo_segue_valendo(self):  # o controle: a base trazida pelo merge de sempre
        self.git("merge", "-q", "--no-edit", "develop")
        self.assertEqual(self.motivos(), [None, None])

    def test_byte_a_mao_em_codigo_desatualiza_e_em_texto_nao(self):
        # sonda revisao-seguranca S1: sonda_merge_a_mao.py: merge da develop com byte à mão em bin/, README.md, tests/, docs/guia.md e com hooks/h voltado ao texto antigo · espera: código à mão desatualiza
        self.git("merge", "-q", "--no-commit", "develop")
        self.escreve("README.md", "texto à mão no merge\n")
        self.commit("merge com texto à mão")
        self.assertEqual(self.motivos(), [None, None])  # README.md é texto (EST-M4): não desatualiza
        self.escreve("bin/a", "a da branch e mais\n")
        self.commit("byte à mão em código")
        for motivo in self.motivos():
            self.assertIn("desatualizado: bin/a mudou depois do parecer", motivo or "")

    def test_merge_s_ours_desatualiza_review_e_seguranca(self):
        # sonda revisao-seguranca S2: base muda só hooks/h; autor faz `git merge -s ours develop` depois do parecer; commit_vale(base=develop) · espera: desatualizado (review e segurança)
        self.git("merge", "-q", "-s", "ours", "--no-edit", "develop")
        self.assertEqual(self.git("rev-parse", "HEAD^{tree}"), self.git("rev-parse", f"{self.parecer}^{{tree}}"))
        for motivo in self.motivos():
            self.assertIn("desatualizado: bin/f mudou depois do parecer", motivo or "")

    def test_conflito_resolvido_com_o_lado_da_branch_desatualiza(self):
        # sonda revisao-seguranca S3: branch e base mudam hooks/h (conflito) e a base muda c; conflito resolvido com `checkout --ours` · espera: desatualizado nos dois
        self.git("switch", "-q", "develop")
        self.escreve("bin/a", "a da develop\n")
        self.escreve("c", "c da develop\n")
        self.commit("develop muda bin/a (conflito) e c")
        self.git("switch", "-q", "ramo")
        self.git("merge", "-q", "-s", "recursive", "-X", "ours", "--no-edit", "develop")  # o conflito fica com o lado da branch
        self.assertEqual(self.git("show", "HEAD:bin/a"), "a da branch")
        for motivo in self.motivos():
            self.assertIn("desatualizado: bin/a mudou depois do parecer", motivo or "")

    def test_merge_simulado_que_falha_desatualiza(self):  # base ilegível: sem o merge simulado, nada se afirma
        self.assertTrue(fc.trouxe_a_base(self.dir, "nao-existe", self.parecer, self.parecer))
        self.assertIn("desatualizado: não comparei", fc.commit_vale(self.dir, self.parecer, self.parecer, "nao-existe") or "")
        self.assertIsNone(fc.commit_vale(self.dir, self.parecer, self.parecer, "develop"))  # sem trazer a base, igual vale


class NomeUnicoNoModulo(unittest.TestCase):
    """QA A2 da v0479-entrega-merges: uma 2.a definição de mesmo nome no `bin/forge-check` (o `vindos_da_base` do ENTREGA-MERGE-DA-DEVELOP)
    sobrepôs a do E7 e desligou o `commit_vale` e o `parecer delta` sem que nenhum mutante do conjunto a pegasse."""

    def test_nenhuma_funcao_ou_classe_definida_duas_vezes(self):
        arvore = ast.parse((AQUI.parent / "bin" / "forge-check").read_text(encoding="utf-8"))
        nomes = [n.name for n in arvore.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        self.assertGreater(len(nomes), 300)
        self.assertEqual(sorted({n for n in nomes if nomes.count(n) > 1}), [])


if __name__ == "__main__":
    unittest.main()
