"""E31 (v0478, PROMOCAO-PR-RELEASE): a promoção por marca (`forge-fechar --promover <sha>`, com itens mesclados na develop depois da
marca) segue o caminho da promoção no `forge-check pr --base main|homolog`: sem a conferência E7 e sem o teto H1 de item. Uma branch de
trabalho com `--base main` segue item: conferência e H1 iguais. Repositório temporário com remoto bare."""
import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RepoComOrigem, carregar_forge_check, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

GRANDE = "".join(f"v{i} = {i}\n" for i in range(366))  # 366 linhas de código, como a 0.47.8
PR_ABERTO_SEM_TETO = ({"number": 7, "state": "OPEN", "body": "sem a linha do teto", "headRefOid": "x"}, None)


class PromocaoPorMarca(RepoComOrigem):
    CONFERIR = False  # o caso real: não há docs/pedidos/<pedido>.md nem conferida para a marca

    def setUp(self):
        super().setUp()
        base = git("rev-parse", "origin/develop", cwd=self.repo).stdout.strip()
        for destino in ("main", "homolog"):  # a main e a homolog na base: o diff da versão é o da marca
            git("push", "-q", "origin", f"{base}:refs/heads/{destino}", cwd=self.repo)
        git("fetch", "-q", "origin", cwd=self.repo)

    def marca_com_item_depois(self):
        """A marca da versão mesclada na develop, um item mesclado depois dela, e nenhuma branch apontando para a marca."""
        grande = self.commitar(self.repo, {"src/versao.py": GRANDE}, "versão")
        self.pareceres(grande)
        marca = self.head_da_branch()
        git("push", "-q", "origin", "melhoria/x:develop", cwd=self.repo)
        self.develop_anda({"src/y.txt": "y1 de outro item\ny2\ny3\ny4\ny5\ny6\ny7\ny8\n"})
        git("switch", "-q", "--detach", cwd=self.repo)
        git("branch", "-q", "-D", "melhoria/x", cwd=self.repo)
        self.assertNotEqual(git("rev-parse", "origin/develop", cwd=self.repo).stdout.strip(), marca)
        return marca

    def head_da_branch(self):
        return git("rev-parse", "melhoria/x", cwd=self.repo).stdout.strip()

    def fc(self):
        fc = carregar_forge_check()
        self.enterContext(contextlib.redirect_stderr(io.StringIO()))
        self.enterContext(mock.patch.object(fc, "RAIZES_DE_BRIEF", (self.home / ".forge-contrib",)))
        self.enterContext(mock.patch.object(fc, "checks_do_head", lambda *a, **k: []))
        self.enterContext(mock.patch.object(fc, "pr_da_branch", lambda *a, **k: PR_ABERTO_SEM_TETO))
        return fc

    def test_marca_com_item_depois_promove_sem_conferencia_e_sem_teto(self):  # o caso real da 0.47.8 (b407f8f7)
        marca = self.marca_com_item_depois()
        for base in ("main", "homolog"):
            with self.subTest(base):
                rc, saida, erro = self.pr("--base", base, ref=marca)
                self.assertEqual(rc, 0, saida + erro)
                self.assertIn(f"pr: promoção: o head é o da integração e a base é {base}", erro)
                self.assertNotIn("acima do teto", erro)
        self.assertEqual(self.fc().pr_da_cli(self.repo, "p1", ref=marca, base="main"), [])  # nem com o PR aberto sem o teto

    def test_item_comum_de_366_linhas_segue_medido_e_reprovado(self):
        grande = self.commitar(self.repo, {"src/versao.py": GRANDE}, "item grande")
        self.pareceres(grande)
        rc, saida, erro = self.pr("--base", "main")
        self.assertEqual(rc, 1, saida)
        self.assertIn('pr: conferência: sem o pedido de "p1"', saida)  # pedido inexistente segue reprovado
        self.assertIn("tamanho: 366 linhas de código, acima do teto de 150 por item", erro)
        self.assertNotIn("promoção", erro)
        violacoes = self.fc().pr_da_cli(self.repo, "p1", ref="melhoria/x", base="main")
        self.assertIn("pr: tamanho: 366 linhas de código acima do teto de 150 sem a linha", "\n".join(violacoes))

    def test_branch_mesclada_na_develop_nao_vira_promocao(self):  # o head da branch é o segundo pai do merge, não primeiro
        trabalho = self.head_da_branch()
        git("switch", "-q", "-c", "integra", "origin/develop", cwd=self.repo)
        self.commitar(self.repo, {"src/y.txt": "y1 de outro item\ny2\ny3\ny4\ny5\ny6\ny7\ny8\n"}, "outro item")
        git("merge", "-q", "--no-ff", "--no-edit", "melhoria/x", cwd=self.repo)
        git("push", "-q", "origin", "integra:develop", cwd=self.repo)
        git("fetch", "-q", "origin", cwd=self.repo)
        fc = self.fc()
        ponta = fc.ref_da_base(self.repo, "develop")
        self.assertTrue(fc.e_ancestral(self.repo, trabalho, ponta))
        self.assertFalse(fc.promocao(self.repo, trabalho, "main"))
        self.assertTrue(fc.promocao(self.repo, ponta, "main"))

    def test_sem_ponta_ou_com_o_git_falhando_nao_e_promocao(self):  # falha fechada: o caminho do item
        marca = self.marca_com_item_depois()
        fc = self.fc()
        ponta = fc.ref_da_base(self.repo, "develop")
        self.assertTrue(fc.foi_ponta_da_integracao(self.repo, marca, ponta))
        self.assertFalse(fc.foi_ponta_da_integracao(self.repo, marca, None))
        real = fc.git
        falho = lambda raiz, *args, **kw: (128, marca) if args[:1] == ("rev-list",) else real(raiz, *args, **kw)
        with mock.patch.object(fc, "git", falho):
            self.assertFalse(fc.foi_ponta_da_integracao(self.repo, marca, ponta))


if __name__ == "__main__":
    unittest.main()
