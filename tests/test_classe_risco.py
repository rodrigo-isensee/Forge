"""P5 da 0.43.1 (dono, 2026-11-08: rigor proporcional ao risco, decidido por ferramenta): `forge-check classe` classifica o diff da
branch em T (trivial), N (normal) ou C (controle), e o `forge-check pr` exige os pareceres da classe somados aos gatilhos de segurança e
de devops de hoje (a classe nunca exige menos que eles). Sem rede."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_isencoes import FORGE_CHECK, REVIEW, Repo, fc, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from apoio_conferida import gravar_conferida  # noqa: E402

M = fc.Mudanca
CATRACA = fc.carregar_catraca()


def sem_contagem(nomes):
    raise AssertionError(f"a contagem não devia rodar: {nomes}")


def classe(mudancas, contar=sem_contagem, catraca=CATRACA):
    return fc.classe_das_mudancas(mudancas, catraca, contar)[0]


class ClasseDasMudancas(unittest.TestCase):
    def test_controle_e_c(self):
        for nome in ("hooks/x.py", "bin/forge-novo", ".githooks/pre-push", ".github/workflows/ci.yml", "scripts/promover-homolog.py",
                     "docs/regras/R-X.md", "agents/x.md", "skills/a/SKILL.md", "tests/catraca.py", "tests/config.json",
                     "hooks/conformidade.json", "migrations/0001.sql", "Dockerfile", "templates/projeto/CLAUDE.md"):
            with self.subTest(nome=nome):
                self.assertEqual(classe([M("docs/x.md"), M(nome)]), "C")

    def test_config_do_claude_mcp_e_teste_de_controle_sao_c(self):  # EXT-B1: hoje sairiam N
        for nome in (".claude/settings.json", ".claude/hooks/x.sh", ".claude/agents/a.md", "app/.claude/settings.local.json", ".mcp.json",
                     "tests/test_hooks_x.py", "tests/catraca_apoio.py", "tests/test_oraculo_a.py", "tests/test_forge_check_y.py",
                     "tests/test_fechar_z.py", "tests/hooks/caso.json", "tests/test_pre_push_a.py", "tests/test_conformidade_b.py"):
            with self.subTest(nome=nome):
                self.assertEqual(classe([M(nome)]), "C")
        self.assertEqual(classe([M("tests/test_app.py")]), "T")  # teste comum segue T
        self.assertEqual(classe([M("docs/mcp.json.md")]), "T")

    def test_protegido_vem_da_lista_da_catraca(self):  # reaproveita PROTEGIDOS, sem cópia
        for nome in CATRACA.PROTEGIDOS:
            with self.subTest(nome=nome):
                self.assertEqual(classe([M(nome.rstrip("/") + ("/x" if nome.endswith("/") else ""))]), "C")

    def test_so_documentacao_comum_e_t_mesmo_grande_e_em_pasta_nova(self):
        self.assertEqual(classe([M("docs/guia/novo.md", novo_em_pasta_nova=True), M("README.md")]), "T")

    def test_so_testes_e_t(self):
        self.assertEqual(classe([M("tests/test_a.py"), M("tests/fixtures/x.json"), M("src/a_test.go"), M("web/b.spec.ts")]), "T")
        self.assertEqual(classe([M("tests/test_a.py"), M("docs/x.md")]), "T")

    def test_fronteira_das_20_linhas(self):
        self.assertEqual(classe([M("src/app.py")], lambda n: (20, False)), "T")
        self.assertEqual(classe([M("src/app.py")], lambda n: (21, False)), "N")

    def test_teste_mais_codigo_conta_as_linhas(self):
        mudancas = [M("tests/test_a.py"), M("src/app.py")]
        self.assertEqual(classe(mudancas, lambda n: (20, False)), "T")
        self.assertEqual(classe(mudancas, lambda n: (21, False)), "N")

    def test_conservador(self):
        self.assertEqual(classe([M("src/novo/a.py", novo_em_pasta_nova=True)]), "N")  # pasta que a base não tem
        self.assertEqual(classe([M("tests/novo/test_a.py", novo_em_pasta_nova=True)]), "N")
        self.assertEqual(classe([M("src/a.py", removido=True)]), "N")
        self.assertEqual(classe([M("src/link", modo_incomum=True)]), "N")
        self.assertEqual(classe([M("package.json")]), "N")  # gatilho de segurança (dependência)
        self.assertEqual(classe([M(".env.exemplo")]), "N")
        self.assertEqual(classe([M("src/a.png")], lambda n: (0, True)), "N")  # binário
        self.assertEqual(classe([M("src/a.py")], lambda n: None), "N")  # contagem ilegível
        self.assertEqual(classe([M(f"src/a{i}.py") for i in range(21)]), "N")  # mais de 20 arquivos: nem conta

    def test_falha_fechada(self):
        self.assertEqual(classe(None), "C")
        self.assertEqual(classe([M("docs/x.md")], catraca=None), "C")
        self.assertEqual(classe([]), "N")

    def test_pareceres_e_quadro_nao_contam(self):
        self.assertEqual(classe([M("docs/reviews/p1.md"), M("docs/qa/p1.md"), M("KANBAN.md"), M("src/a.py")], lambda n: (3, False)), "T")
        self.assertEqual(classe([M("docs/reviews/p1.md")]), "N")  # nada fora dos LIVRES: diff vazio

    def test_motivo_diz_os_arquivos_que_decidiram(self):
        c, motivos, arquivos = fc.classe_das_mudancas([M("docs/x.md"), M("hooks/a.py")], CATRACA, sem_contagem)
        self.assertEqual((c, arquivos), ("C", ["hooks/a.py"]))
        self.assertIn("hooks/a.py", motivos[0])


class PareceresDaClasse(unittest.TestCase):
    def test_mapeamento(self):
        self.assertEqual(fc.pareceres_exigidos("T", False, []), ["review"])
        self.assertEqual(fc.pareceres_exigidos("N", False, []), ["review", "qa"])
        self.assertEqual(fc.pareceres_exigidos("C", False, []), ["review", "qa", "revisao-seguranca"])
        self.assertEqual(fc.pareceres_exigidos("C", True, []), ["review", "qa", "revisao-devops", "revisao-seguranca"])

    def test_nunca_menos_que_os_gatilhos(self):
        for c in ("T", "N", "C"):
            with self.subTest(classe=c):
                exigidos = fc.pareceres_exigidos(c, True, ["dependência (travas ou manifesto): package.json"])
                self.assertIn("revisao-devops", exigidos)
                self.assertIn("revisao-seguranca", exigidos)
                self.assertIn("review", exigidos)

    def test_portoes(self):
        self.assertEqual(fc.portoes_da_classe("T", False), ["autor", ["review"], "CI"])
        self.assertEqual(fc.portoes_da_classe("N", False), ["autor", ["review", "qa"], "CI"])
        self.assertEqual(fc.portoes_da_classe("C", True), ["autor", ["review", "seguranca", "qa", "devops"], "CI"])


class ClasseNoRepositorio(Repo):
    def classe(self, *args):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "classe", "--base", "develop", "--json", *args],
                           capture_output=True, text=True, timeout=60, env=dict(os.environ, HOME=str(self.tmp / "home")))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def test_fronteira_20_21_linhas_contadas_pelo_git(self):
        self.commitar({"src/app.py": "v1\n" + "".join(f"l{i}\n" for i in range(20))}, "20 linhas")
        self.assertEqual(self.classe()["classe"], "T")
        self.commitar({"src/app.py": "v1\n" + "".join(f"l{i}\n" for i in range(21))}, "21 linhas")
        saida = self.classe()
        self.assertEqual((saida["classe"], saida["pareceres"]), ("N", ["review", "qa"]))
        self.assertEqual(saida["portoes"], ["autor", ["review", "qa"], "CI"])

    def test_docs_em_docs_regras_e_c(self):
        self.commitar({"docs/regras/R-X.md": "# x\n"}, "regra")
        saida = self.classe()
        self.assertEqual((saida["classe"], saida["arquivos"]), ("C", ["docs/regras/R-X.md"]))
        self.assertEqual(saida["pareceres"], ["review", "qa", "revisao-seguranca"])

    def test_teste_mais_codigo_grande_e_n(self):
        self.commitar({"tests/test_app.py": "ok\n", "src/app.py": "v1\n" + "".join(f"l{i}\n" for i in range(25))}, "teste e código")
        self.assertEqual(self.classe()["classe"], "N")

    def test_settings_do_claude_e_c(self):  # EXT-B1
        self.commitar({".claude/settings.json": "{}\n"}, "settings")
        saida = self.classe()
        self.assertEqual((saida["classe"], saida["arquivos"]), ("C", [".claude/settings.json"]))
        self.assertIn("configuração do Claude Code", saida["motivos"][0])

    def test_github_pede_devops(self):
        self.commitar({".github/workflows/ci.yml": "on: push\n"}, "ci")
        saida = self.classe()
        self.assertEqual(saida["classe"], "C")
        self.assertEqual(saida["portoes"], ["autor", ["review", "seguranca", "qa", "devops"], "CI"])

    def test_arquivo_novo_em_pasta_nova_nao_e_t(self):
        self.commitar({"lib/novo.py": "x\n"}, "pasta nova")
        self.assertEqual(self.classe()["classe"], "N")
        self.commitar({"src/outro.py": "x\n"}, "pasta conhecida")  # a lib/ ainda conta
        self.assertEqual(self.classe()["classe"], "N")

    def test_saida_em_texto(self):
        self.commitar({"docs/x.md": "# x\n"}, "doc")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "classe", "--base", "develop"],
                           capture_output=True, text=True, timeout=60, env=dict(os.environ, HOME=str(self.tmp / "home")))
        self.assertEqual(r.stdout.splitlines(), ["classe: T", "motivo: só documentação fora dos caminhos de controle",
                                                 "portoes: autor + review (mesmo head) + CI", "pareceres: review"])

    def test_head_inexistente_sai_2(self):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "classe", "--head", "nao-existe"],
                           capture_output=True, text=True, timeout=60, env=dict(os.environ, HOME=str(self.tmp / "home")))
        self.assertEqual(r.returncode, 2)


class PrPelaClasse(Repo):
    def pr(self):
        gravar_conferida(self.tmp / "home", self.tmp, "p1")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "pr", "p1", "--base", "develop"],
                           capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout, r.stderr

    def test_t_pede_so_o_review(self):
        self.entrega({"src/app.py": "v2\n"})
        rc, saida, erro = self.pr()
        self.assertEqual(rc, 0, saida)
        self.assertIn("exigidos review ·", saida)
        self.assertIn("pr: classe T", erro)

    def test_t_com_qa_reprovado_reprova(self):  # dispensar o QA não é ignorar um QA reprovado (como a catraca)
        head = self.commitar({"src/app.py": "v2\n"}, "entrega")
        qa = ("---\ntipo: qa\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: reprovado\nescopo: completo\n"
              "bugs_criticos: 1\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\ndata: 2026-10-12\n---\n# QA\n")
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head), "docs/qa/p1.md": qa.format(c=head)}, "pareceres")
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1, saida)
        self.assertIn("docs/qa/p1.md: parecer: o último parecer não é aprovado", saida)

    def test_n_pede_qa(self):
        self.entrega({"src/app.py": "".join(f"v{i}\n" for i in range(30))})
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1)
        self.assertIn("qa: sem parecer para o pedido `p1` (R-QA)", saida)
        self.assertNotIn("revisao-seguranca", saida)

    def test_c_pede_seguranca_mesmo_sem_gatilho(self):
        self.entrega({"bin/ferramenta": "x\n"})
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1)
        self.assertIn("revisao-seguranca: sem parecer para o pedido `p1` (classe C, sensível da catraca", saida)
        self.assertIn("qa: sem parecer", saida)

    def test_gatilho_de_seguranca_vale_na_classe_n(self):
        self.entrega({"package.json": "{}\n"})
        exigidos, gatilhos = fc.exigidos_do_pr(self.tmp, "p1", None, "develop")
        self.assertEqual(exigidos, ["review", "qa", "revisao-seguranca"])
        self.assertIn("dependência", gatilhos[0])

    def test_review_do_parecer_nao_muda_a_classe(self):  # o parecer commitado na branch (LIVRES) não conta linhas
        head = self.commitar({"src/app.py": "v2\n"}, "entrega")
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head) + "".join(f"linha {i}\n" for i in range(40))}, "review")
        self.assertEqual(fc.classe_da_entrega(self.tmp, None, "develop")[0], "T")


class HookSemPedido(Repo):
    """O hook `parecer` na branch sem pedido pede os mesmos pareceres do `forge-check pr` (classe + gatilhos), nunca menos."""

    def exigidos(self):
        import importlib.util
        hooks = str(Path(__file__).resolve().parent.parent / "hooks")
        if hooks not in sys.path:
            sys.path.insert(0, hooks)  # o `_comum` dos hooks, como o Claude Code os roda
        spec = importlib.util.spec_from_file_location("hook_parecer_classe", Path(__file__).resolve().parent.parent / "hooks" / "parecer.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo.exigidos_sem_pedido(fc, self.tmp, None, "develop")

    def test_t_so_review(self):
        self.entrega({"src/app.py": "v2\n"}, com_review=False)
        self.assertEqual(self.exigidos(), (["review"], "T"))

    def test_gatilho_de_seguranca_soma_na_classe_n(self):
        self.entrega({"package.json": "{}\n"}, com_review=False)
        self.assertEqual(self.exigidos(), (["review", "qa", "revisao-seguranca"], "N"))

    def test_c_pede_seguranca(self):
        self.entrega({"bin/ferramenta": "x\n"}, com_review=False)
        self.assertEqual(self.exigidos()[0], ["review", "qa", "revisao-seguranca"])


if __name__ == "__main__":
    unittest.main()
