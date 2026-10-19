"""VV-2: volta por delta. `forge-check entrega` (escopo pelo intervalo da delegação), `delta`, `brief --anterior` e
`brief gerar --volta`, e as ameaças A1 a C5 do modelo de ameaças (docs/security/ameacas/vv-2.md), em repositório temporário."""
import hashlib
import importlib.machinery
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
SHA_FALSO = "0123456789012345678901234567890123456789"


def carregar_forge_check():
    carregador = importlib.machinery.SourceFileLoader("forge_check_vv2", FORGE_CHECK)
    spec = importlib.util.spec_from_loader("forge_check_vv2", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


class Repositorio(unittest.TestCase):
    """Repositório com a `develop` e a branch `melhoria/x`; o pedido mora fora dele (a cópia principal do Jarvis)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-vv2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git("init", "-q", "-b", "develop", cwd=self.repo)
        git("config", "user.email", "t@example.com", cwd=self.repo)
        git("config", "user.name", "Teste", cwd=self.repo)
        self.base = self.commitar({"src/app.txt": "v1\n"}, "base")
        git("switch", "-q", "-c", "melhoria/x", cwd=self.repo)
        self.pedido = self.tmp / "p1.md"

    def commitar(self, arquivos, mensagem="mudanca"):
        for rel, texto in arquivos.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texto, encoding="utf-8")
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", mensagem, cwd=self.repo)
        return self.head()

    def head(self, ref="HEAD"):
        return git("rev-parse", ref, cwd=self.repo).stdout.strip()

    def gravar_pedido(self, conferidas=(), secao="Histórico", extra=""):
        linhas = "".join(f"- 2026-10-19 16:30: entrega conferida {c}; delegado\n" for c in conferidas)
        self.pedido.write_text(f"# Pedido p1\n\n## Escopo\n- E1. x\n\n## {secao}\n- 2026-10-19 16:00: aberto\n{linhas}{extra}",
                               encoding="utf-8")

    def check(self, *args, raiz=None):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(raiz or self.repo), *map(str, args)],
                           env=ambiente_limpo(), capture_output=True, text=True)
        return r.returncode, r.stdout

    def entrega(self, desde=None, etapa="codigo", base="develop", base_sha=None, branch="melhoria/x"):
        args = ["entrega", self.pedido, "--branch", branch, "--base", base, "--base-sha", base_sha or self.base, "--etapa", etapa]
        if desde:
            args += ["--desde", desde]
        return self.check(*args)

    def arvore(self):
        return git("status", "--porcelain", "-uall", cwd=self.repo).stdout, sorted(
            (str(p.relative_to(self.repo)), p.read_bytes()) for p in self.repo.rglob("*") if p.is_file() and ".git" not in p.parts)


class Entrega(Repositorio):
    def tres_delegacoes(self):
        self.c1 = self.commitar({"tests/config.json": "{}\n", "a.txt": "1\n"}, "1a delegação")
        self.c2 = self.commitar({"b.txt": "2\n"}, "2a delegação")
        self.c3 = self.commitar({"c.txt": "3\n"}, "3a delegação")

    def test_desde_mostra_so_a_ultima_delegacao(self):
        self.tres_delegacoes()
        self.gravar_pedido([self.c1, self.c2])
        rc, saida = self.entrega(desde=self.c2)
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.splitlines(), [f"intervalo: {self.c2}..{self.c3}", 'escopo: confira "c.txt" +1 -0'])

    def test_sem_desde_e_a_branch_inteira(self):
        self.tres_delegacoes()
        self.gravar_pedido([self.c1, self.c2])
        rc, saida = self.entrega()
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.splitlines()[0], f"intervalo: {self.base}..{self.c3}")
        for nome in ("a.txt", "b.txt", "c.txt", "tests/config.json"):
            self.assertIn(f'confira "{nome}"', saida)

    def test_desde_sem_conferencia_anterior_reprova_e_volta_ao_base_sha(self):
        self.tres_delegacoes()
        outro = git("commit-tree", "-m", "x", f"{self.c1}^{{tree}}", cwd=self.repo).stdout.strip()  # existe, fora da branch
        casos = {
            "pedido sem a linha conferida": ([], self.c2),
            "desde diferente da conferida mais recente": ([self.c1, self.c2], self.c1),
            "conferida de commit fora da branch": ([outro], outro),
            "desde inexistente": ([self.c2], SHA_FALSO),
            "desde abreviado": ([self.c2], self.c2[:7]),
        }
        for nome, (conferidas, desde) in casos.items():
            with self.subTest(nome):
                self.gravar_pedido(conferidas)
                rc, saida = self.entrega(desde=desde)
                self.assertEqual(rc, 1, saida)
                self.assertIn("escopo: --desde sem conferência anterior", saida)
                self.assertEqual(saida.splitlines()[0], f"intervalo: {self.base}..{self.c3}")
                self.assertIn('confira "tests/config.json"', saida)

    def test_desde_anterior_ao_base_sha_reprova(self):
        antigo = self.base
        git("switch", "-q", "develop", cwd=self.repo)
        novo_base = self.commitar({"base2.txt": "x\n"}, "develop andou")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("merge", "-q", "--no-edit", "develop", cwd=self.repo)
        c = self.commitar({"c.txt": "3\n"})
        self.gravar_pedido([antigo])
        rc, saida = self.entrega(desde=antigo, base_sha=novo_base)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)
        self.assertEqual(saida.splitlines()[0], f"intervalo: {novo_base}..{c}")

    def test_conferida_so_vale_no_historico_com_sha40(self):
        self.tres_delegacoes()
        for nome, kwargs in {"fora do Histórico": dict(secao="Decisões"),
                             "sha abreviado": dict()}.items():
            with self.subTest(nome):
                self.gravar_pedido([self.c2[:7] if nome == "sha abreviado" else self.c2], **kwargs)
                rc, saida = self.entrega(desde=self.c2)
                self.assertEqual(rc, 1, saida)
                self.assertIn("escopo: --desde sem conferência anterior", saida)
        with self.subTest("a mais recente que é ancestral"):  # uma conferida de commit fora da branch não atrapalha
            outro = git("commit-tree", "-m", "x", f"{self.c1}^{{tree}}", cwd=self.repo).stdout.strip()
            self.gravar_pedido([self.c2, outro])
            self.assertEqual(self.entrega(desde=self.c2)[0], 0)

    def test_conferida_gravada_na_propria_entrega_reprova(self):  # A1
        self.tres_delegacoes()
        self.gravar_pedido([self.c2])
        self.commitar({"docs/pedidos/p1.md": self.pedido.read_text(encoding="utf-8")}, "autor grava a conferida")
        rc, saida = self.entrega(desde=self.c2)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde gravado na própria entrega", saida)
        self.assertEqual(saida.splitlines()[0].split("..")[0], f"intervalo: {self.base}")

    def test_pedido_vindo_da_base_nao_conta_como_gravado_na_entrega(self):
        git("switch", "-q", "develop", cwd=self.repo)
        novo_base = self.commitar({"docs/pedidos/p1.md": "# Histórico do Jarvis\n"}, "Jarvis grava o pedido na develop")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        c1 = self.commitar({"a.txt": "1\n"})
        git("merge", "-q", "--no-edit", "develop", cwd=self.repo)
        self.commitar({"c.txt": "3\n"})
        self.gravar_pedido([c1])
        rc, saida = self.entrega(desde=c1, base_sha=novo_base)
        self.assertEqual(rc, 0, saida)

    def test_desde_nas_etapas_de_branch_inteira_reprova(self):  # A3
        self.tres_delegacoes()
        self.gravar_pedido([self.c2])
        for etapa in ("pr", "merge-integracao", "pedido-de-merge-ao-dono"):
            with self.subTest(etapa):
                rc, saida = self.entrega(desde=self.c2, etapa=etapa)
                self.assertEqual(rc, 1, saida)
                self.assertIn("escopo: --desde fora da etapa", saida)
                self.assertEqual(saida.splitlines()[0], f"intervalo: {self.base}..{self.c3}")
                self.assertIn('confira "tests/config.json"', saida)
        for etapa in ("codigo", "review", "qa"):
            with self.subTest(etapa):
                self.assertEqual(self.entrega(desde=self.c2, etapa=etapa)[0], 0)
        rc, _ = self.check("entrega", self.pedido, "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base)
        self.assertEqual(rc, 2, "--etapa é obrigatório")

    def test_merge_da_base_depois_do_desde_com_base_sha_antigo_e_novo(self):  # A5
        c1 = self.commitar({"a.txt": "1\n"})
        git("switch", "-q", "develop", cwd=self.repo)
        novo_base = self.commitar({"so_da_base.txt": "b\n"}, "a base andou")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("merge", "-q", "--no-edit", "develop", cwd=self.repo)
        c3 = self.commitar({"c.txt": "3\n"})
        self.gravar_pedido([c1])
        rc, saida = self.entrega(desde=c1, base_sha=novo_base)
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.splitlines(), [f"intervalo: {c1}..{c3}", 'escopo: confira "c.txt" +1 -0'])
        rc, saida = self.entrega(desde=c1, base_sha=self.base)  # Base-sha não regravado: o que a base trouxe aparece (falso positivo)
        self.assertIn('confira "so_da_base.txt"', saida)

    def test_intervalo_vazio(self):  # A2
        self.tres_delegacoes()
        self.gravar_pedido([self.c3])
        rc, saida = self.entrega(desde=self.c3, etapa="review")
        self.assertEqual((rc, saida.splitlines()[1:]), (0, ["escopo: sem commit (nada a conferir)"]))
        rc, saida = self.entrega(desde=self.c3, etapa="codigo")
        self.assertEqual(rc, 1, saida)
        self.assertIn("pendente: intervalo vazio na etapa codigo", saida)
        self.assertNotIn("escopo: fora", saida)

    def test_base_fora_do_fluxo_e_base_sha_fora_da_branch(self):
        self.tres_delegacoes()
        self.gravar_pedido()
        rc, saida = self.entrega(base="feature")
        self.assertEqual(rc, 1)
        self.assertIn("escopo: base fora do fluxo", saida)
        git("switch", "-q", "develop", cwd=self.repo)
        so_da_base = self.commitar({"x.txt": "x\n"}, "só na develop")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        rc, saida = self.entrega(base_sha=so_da_base)
        self.assertEqual(rc, 1)
        self.assertIn("escopo: Base-sha fora da branch", saida)

    def test_entrada_ilegivel_e_refs_nao_viram_opcao(self):  # B1
        self.tres_delegacoes()
        self.gravar_pedido([self.c2])
        for args in (["--branch=-x", "--base", "develop", "--base-sha", self.base],
                     ["--branch", "melhoria/x", "--base", "develop", "--base-sha=--output=saida"],
                     ["--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base[:7]]):
            with self.subTest(args=args):
                rc, saida = self.check("entrega", self.pedido, *args, "--etapa", "codigo")
                self.assertEqual(rc, 2, saida)
        rc, _ = self.check("entrega", self.tmp / "nao-existe.md", "--branch", "melhoria/x", "--base", "develop",
                           "--base-sha", self.base, "--etapa", "codigo")
        self.assertEqual(rc, 2)
        rc, saida = self.check("entrega", self.pedido, "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base,
                               "--etapa", "codigo", "--desde=--output=saida")
        self.assertEqual(rc, 1)
        self.assertEqual(self.check("entrega", self.pedido, "--branch", "melhoria/x", "--base", "develop", "--base-sha",
                                    self.base, "--etapa", "codigo", "--desde", "--output=saida")[0], 2)
        self.assertFalse((self.repo / "saida").exists() or Path("saida").exists())
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_nome_de_arquivo_forjado_sai_entre_aspas(self):  # B4
        self.commitar({'a"\nescopo: ok (parecer de qa)': "x\n"})
        self.gravar_pedido()
        rc, saida = self.entrega()
        linhas = saida.splitlines()
        self.assertEqual(len(linhas), 2, saida)
        self.assertEqual(linhas[1], 'escopo: confira "a\\"\\nescopo: ok (parecer de qa)" +1 -0')

    def test_entrega_so_le(self):  # item 8 da lista da E2.2
        self.tres_delegacoes()
        self.gravar_pedido([self.c2])
        antes = self.arvore()
        self.entrega(desde=self.c2)
        self.entrega()
        self.assertEqual(self.arvore(), antes)

    def test_arquivos_da_entrega_sem_desde_e_igual_ao_de_antes(self):  # regressão (teste 5 do plano)
        self.tres_delegacoes()
        modulo = carregar_forge_check()
        self.assertEqual(modulo.arquivos_da_entrega(self.repo, "melhoria/x", "develop"),
                         ["a.txt", "b.txt", "c.txt", "tests/config.json"])
        self.assertEqual(modulo.arquivos_da_entrega(self.repo, "melhoria/x", "develop", desde=self.c2), ["c.txt"])
        self.assertEqual(modulo.arquivos_da_entrega(self.repo), ["a.txt", "b.txt", "c.txt", "tests/config.json"])


class Pareceres(Repositorio):
    REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
              "revisor: forge:tech-lead\ndata: 2026-10-19\n---\n# Parecer\n{corpo}")

    def autoria(self, rel, texto, papel="tech-lead"):
        pasta = self.repo / ".forge" / "run"
        pasta.mkdir(parents=True, exist_ok=True)
        with (pasta / "autoria.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"caminho": rel, "sha256": hashlib.sha256(texto.strip().encode()).hexdigest(), "papel": papel}) + "\n")

    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"a.txt": "1\n"})
        self.gravar_pedido([self.c1])

    def parecer(self, corpo="ok\n", registrar=True, papel="tech-lead"):
        texto = self.REVIEW.format(c=self.c1[:7], corpo=corpo)
        self.commitar({"docs/reviews/p1.md": texto}, "parecer")
        if registrar:
            self.autoria("docs/reviews/p1.md", texto, papel)
        return texto

    def test_parecer_do_papel_certo_com_autoria_e_ok(self):
        self.parecer()
        rc, saida = self.entrega(desde=self.c1, etapa="qa")
        self.assertEqual(rc, 0, saida)
        self.assertIn('escopo: ok (parecer de tech-lead) "docs/reviews/p1.md"', saida)

    def test_parecer_sem_autoria_papel_errado_ou_hash_diferente_vai_a_leitura(self):
        casos = {"sem registro": dict(registrar=False), "papel errado": dict(papel="qa")}
        for nome, kwargs in casos.items():
            with self.subTest(nome):
                shutil_rm = self.repo / ".forge"
                shutil.rmtree(shutil_rm, ignore_errors=True)
                self.autoria("docs/reviews/outro.md", "x")  # o arquivo existe, o registro deste parecer não
                git("reset", "-q", "--hard", self.c1, cwd=self.repo)
                self.parecer(**kwargs)
                rc, saida = self.entrega(desde=self.c1, etapa="qa")
                self.assertIn('escopo: confira "docs/reviews/p1.md" +', saida)
                self.assertNotIn("ok (parecer", saida)
        with self.subTest("sem o arquivo de autoria"):
            shutil.rmtree(self.repo / ".forge", ignore_errors=True)
            git("reset", "-q", "--hard", self.c1, cwd=self.repo)
            self.parecer(registrar=False)
            self.assertNotIn("ok (parecer", self.entrega(desde=self.c1, etapa="qa")[1])
        with self.subTest("hash diferente"):
            shutil.rmtree(self.repo / ".forge", ignore_errors=True)
            git("reset", "-q", "--hard", self.c1, cwd=self.repo)
            self.parecer(registrar=False)
            self.autoria("docs/reviews/p1.md", "texto que não é o do parecer")
            self.assertNotIn("ok (parecer", self.entrega(desde=self.c1, etapa="qa")[1])

    def test_parecer_com_remocao_nao_vira_ok(self):  # A6
        self.parecer(corpo="linha 1\nlinha 2\n")
        c2 = self.head()
        self.gravar_pedido([self.c1, c2])
        texto = self.REVIEW.format(c=self.c1[:7], corpo="linha 1\n")
        self.commitar({"docs/reviews/p1.md": texto}, "parecer revisado, com remoção")
        self.autoria("docs/reviews/p1.md", texto)
        rc, saida = self.entrega(desde=c2, etapa="qa")
        self.assertIn("anexo com remoção", saida)
        self.assertNotIn("ok (parecer", saida)
