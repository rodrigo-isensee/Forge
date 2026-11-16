"""PR-HOOK-RAPIDO (E2.117, v047): o hook `parecer` decide o `gh pr ready` (3 s) e o `gh pr merge` (8 s) no prazo com a máquina carregada.

1. O resultado que o `forge-check pr` gravou (PR-HOOK-PRAZO) vale também como atalho no `gh pr ready` e no `gh pr merge`, preso ao head
   e à base: o aprovado do mesmo head libera sem refazer a checagem; o reprovado recusa; head ou base diferente roda a conferência de
   hoje (falha fechada), e o prazo vencido nela diz o comando que grava o resultado.
2. O `forge-check` lê os documentos de uma `ref` em lote (`textos_da_arvore`: um `ls-tree` e um `cat-file --batch`), no lugar de um
   `git show` por arquivo (medido: 3029 chamadas git e 18,6 s antes; 299 e 3,8 s depois, no mesmo `forge-check pr`).

Os testes que provam "só lê" rodam o hook com o `cmd_pr` e o `pedidos_da_branch` trocados por uma saída 97 (`REFEZ`)."""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import git  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture, modulos_dos_hooks, montar_proc, rodar  # noqa: E402
import test_pr_hook_prazo  # noqa: E402 - o módulo, não a classe: a classe importada rodaria de novo aqui
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

READY = FIXTURES / "parecer" / "forge-clone-pr-ready-com-parecer-libera.json"
COMANDOS = {"ready": "gh pr ready feature/x --repo rodrigo-isensee/Forge",
            "merge": "gh pr merge feature/x --repo rodrigo-isensee/Forge --merge"}


class AtalhoDoReadyEDoMerge(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    hook_so_lendo = test_pr_hook_prazo.PrHookPrazo.hook_so_lendo
    hook_lento = test_pr_hook_prazo.PrHookPrazo.hook_lento

    def montar(self, acao, com_resultado=True):
        """O clone do Forge com review e QA aprovados de feature/x (pedido p1, base develop) e a entrada `gh pr <acao>`."""
        dados = json.loads(READY.read_text(encoding="utf-8"))
        self.assertNotIn("resultado_do_pr", dados)
        if com_resultado:
            dados["resultado_do_pr"] = {"pedido": "p1", "base": "develop"}
        dados["entrada"]["tool_input"]["command"] = COMANDOS[acao]
        self.tmp = self._pasta_temporaria()
        f = Fixture(self.tmp / "parecer" / "caso.json", dados)
        raiz, self.entrada = f.montar(self.tmp, os.getpid())
        f.executar_passos(raiz, None)
        return raiz

    def hook(self, raiz):
        return rodar("parecer", self.entrada, raiz, montar_proc(self._pasta_temporaria(), None), {})

    def test_aprovado_do_mesmo_head_libera_so_lendo_no_prazo(self):
        _comum = modulos_dos_hooks()[0]
        for acao in COMANDOS:
            with self.subTest(acao):
                r, segundos = self.hook_so_lendo(self.montar(acao))
                self.assertEqual((r.returncode, r.stderr), (0, ""), "libera sem refazer a checagem (97 = refez)")
                self.assertLess(segundos, _comum.PRAZO_DA_DECISAO_S, "a decisão só lendo cabe no prazo de 3 s")

    def test_reprovado_do_mesmo_head_recusa_so_lendo(self):
        fc = modulos_dos_hooks()[0].forge_check()
        for acao in COMANDOS:
            with self.subTest(acao):
                raiz = self.montar(acao, com_resultado=False)
                fc.gravar_resultado_do_pr(raiz, "p1", None, "develop", ["docs/qa/p1.md: parecer: reprovado (R-QA)"])
                r, _ = self.hook_so_lendo(raiz)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("R-REVIEW: ", r.stderr)
                self.assertIn("forge-check pr p1 reprovou o head", r.stderr)

    def test_head_diferente_roda_de_novo(self):
        """O aprovado de outro head não vale: o hook refaz a conferência (97), nunca libera pelo resultado velho."""
        for acao in COMANDOS:
            with self.subTest(acao):
                raiz = self.montar(acao)
                git("commit", "-q", "--allow-empty", "-m", "outro head", cwd=raiz)
                r, _ = self.hook_so_lendo(raiz)
                self.assertEqual(r.returncode, test_pr_hook_prazo.REFEZ, r.stderr)

    def test_base_diferente_roda_de_novo(self):
        fc = modulos_dos_hooks()[0].forge_check()
        for acao in COMANDOS:
            with self.subTest(acao):
                raiz = self.montar(acao, com_resultado=False)
                fc.gravar_resultado_do_pr(raiz, "p1", None, None, [])  # o modo estrito, sem base: o PR pede a develop
                r, _ = self.hook_so_lendo(raiz)
                self.assertEqual(r.returncode, test_pr_hook_prazo.REFEZ, r.stderr)

    def test_head_diferente_com_prazo_vencido_recusa_e_diz_o_comando(self):
        for acao in COMANDOS:
            with self.subTest(acao):
                raiz = self.montar(acao)
                git("commit", "-q", "--allow-empty", "-m", "outro head", cwd=raiz)
                r = self.hook_lento(raiz)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("R-REVIEW: o hook não decidiu", r.stderr)
                self.assertIn("Corrigir: rode antes forge-check pr", r.stderr)

    def test_sem_resultado_e_sem_violacao_a_conferencia_de_hoje_libera(self):
        """O atalho não exige o resultado gravado (só o `gh pr create` o exige): sem ele, decide a conferência de hoje, como antes."""
        for acao in COMANDOS:
            with self.subTest(acao):
                r = self.hook(self.montar(acao, com_resultado=False))
                self.assertEqual((r.returncode, r.stderr), (0, ""))


class DocumentosEmLote(unittest.TestCase):
    """`textos_da_arvore`: o mesmo texto do `git show` por arquivo, em duas chamadas git por pasta."""
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria

    def setUp(self):
        self.fc = modulos_dos_hooks()[0].forge_check()
        self.fc.textos_da_arvore.cache_clear()
        self.raiz = self._pasta_temporaria() / "repo"
        self.raiz.mkdir()
        git("init", "-q", "-b", "develop", cwd=self.raiz)
        git("config", "user.email", "t@t", cwd=self.raiz)
        git("config", "user.name", "t", cwd=self.raiz)
        reviews = self.raiz / "docs" / "reviews"
        (reviews / "sub.md").mkdir(parents=True)
        (reviews / "sub.md" / "dentro.md").write_text("---\nna subpasta\n", encoding="utf-8")
        (reviews / "a.md").write_bytes(b"  ---\r\ntipo: review\r\n\r\n")
        (reviews / "b.md").write_text("---\nb\n\n", encoding="utf-8")
        (reviews / "nota.txt").write_text("não é md\n", encoding="utf-8")
        (self.raiz / "docs" / "qa").mkdir()
        (self.raiz / "docs" / "qa" / "leia.txt").write_text("sem md\n", encoding="utf-8")
        (self.raiz / "docs" / "devops").mkdir()
        (self.raiz / "docs" / "devops" / "u.md").write_text("---\nu\n", encoding="utf-8")
        git("add", "-A", cwd=self.raiz)
        git("commit", "-q", "-m", "docs", cwd=self.raiz)

    def contando(self):
        """(lista das chamadas, falso de `git` que as anota e chama o de verdade)."""
        chamadas, real = [], self.fc.git

        def falso(raiz, *args, **kw):
            chamadas.append(args[0])
            return real(raiz, *args, **kw)
        return chamadas, falso

    def test_mesmo_texto_do_git_show(self):
        arvore = self.fc.git(self.raiz, "rev-parse", "HEAD:docs/reviews")[1]
        textos = self.fc.textos_da_arvore(str(self.raiz), arvore)
        self.assertEqual(sorted(textos), ["a.md", "b.md"], "só os .md que são arquivo da pasta")
        for nome, texto in textos.items():
            with self.subTest(nome):
                self.assertEqual(texto, self.fc.git(self.raiz, "show", f"HEAD:docs/reviews/{nome}")[1])

    def test_documentos_da_ref_iguais_aos_do_disco(self):
        self.assertEqual(list(self.fc.documentos(self.raiz, "review", "HEAD")),
                         [("docs/reviews/a.md", "---\ntipo: review"), ("docs/reviews/b.md", "---\nb")])

    def test_chamadas_git_por_pasta(self):
        """Pasta com .md: rev-parse, ls-tree e cat-file; sem .md: sem o cat-file; ausente (docs/architecture/features): só o rev-parse."""
        for tipo, esperado, n in (("review", ["rev-parse", "ls-tree", "cat-file"], 2), ("qa", ["rev-parse", "ls-tree"], 0),
                                  ("plano-tecnico", ["rev-parse"], 0)):
            with self.subTest(tipo):
                chamadas, falso = self.contando()
                with mock.patch.object(self.fc, "git", falso):
                    self.assertEqual(len(list(self.fc.documentos(self.raiz, tipo, "HEAD"))), n)
                self.assertEqual(chamadas, esperado)
        chamadas, falso = self.contando()
        with mock.patch.object(self.fc, "git", falso):
            self.assertEqual(len(list(self.fc.documentos(self.raiz, "review", "HEAD"))), 2)
        self.assertEqual(chamadas, ["rev-parse"], "a mesma árvore sai do cache")

    def test_lote_fora_do_pedido_nao_le_nada(self):
        """Objeto ausente, cabeçalho de outro objeto ou saída truncada: {} (falha fechada), nunca um texto parcial."""
        real = self.fc.git
        arvore = real(self.raiz, "rev-parse", "HEAD:docs/devops")[1]  # um .md só: o defeito no 1.o objeto não cai no 2.o
        primeiro = real(self.raiz, "rev-parse", "HEAD:docs/devops/u.md")[1].encode()
        for nome, lote in (("ausente", b"%s missing\n" % primeiro), ("vazio", b""),
                           ("truncado", b"%s blob 12" % primeiro), ("outro", b"%s blob 1\nx\n" % (b"0" * 40))):
            with self.subTest(nome):
                self.fc.textos_da_arvore.cache_clear()
                falso = lambda r, *a, **kw: (0, lote) if a[0] == "cat-file" else real(r, *a, **kw)  # noqa: E731
                with mock.patch.object(self.fc, "git", falso):
                    self.assertEqual(self.fc.textos_da_arvore(str(self.raiz), arvore), {})


if __name__ == "__main__":
    unittest.main()
