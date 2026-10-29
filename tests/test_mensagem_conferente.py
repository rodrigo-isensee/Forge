"""T6 (T6T3-MENSAGEM): a mensagem ao conferente sai inteira do `forge-check brief mensagem`: a etapa vem do brief (E1) e a do modo
entrega também (E2). Raiz sintética do `Cenario`; biblioteca padrão, sem rede."""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ARQ, ID, Cenario  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

SHA_A, SHA_B, BASE_SHA = "a" * 40, "b" * 40, "c" * 40
SEM_WORKTREE = "--entrega exige --worktree <pasta absoluta existente> e não aceita --anterior, --ref nem --parecer"
SEM_CABECALHO = "--entrega exige `Etapa:`, `Branch:`, `Base:` e `Base-sha:` (40 hex) no cabeçalho do brief"
CABECALHO = f"Etapa: codigo   Cobre: E1.1\nBranch: melhoria/x   Base: develop   Base-sha: {BASE_SHA}\n"


class MensagemPelaEtapaDoBrief(Cenario):
    def setUp(self):
        super().setUp()
        self.completo = self.completo.replace("Agente destino: forge:dev-exemplo\n", "Agente destino: forge:dev-exemplo\n" + CABECALHO, 1)
        self.gravar(ARQ, self.completo)
        self.pasta = self.tmp / "wt"
        self.pasta.mkdir()

    def entrega(self, *extra, pedido_extra=""):
        self.gravar("docs/pedidos/pedido-sintetico.md", self.PEDIDO_CITANDO + "\n## Histórico\n" + pedido_extra)
        return self.mensagem("--entrega", *extra, etapa=None)

    def test_a_etapa_sai_da_linha_etapa_do_brief(self):
        rc, saida = self.mensagem(etapa=None)
        self.assertEqual(rc, 0, saida)
        self.assertIn("Etapa: codigo", saida.decode().splitlines()[1])
        self.assertEqual(self.mensagem(etapa="codigo")[0], 0)

    def test_etapa_diferente_da_do_brief_e_recusada_com_a_etapa_certa(self):
        rc, saida = self.mensagem(etapa="pr")
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), "brief mensagem: --etapa difere da `Etapa:` do brief; a etapa do brief é codigo")

    def test_entrega_traz_tudo_do_arquivo_e_o_desde_da_ultima_conferida(self):
        historico = f"- 2026-10-29 07:36: entrega conferida {SHA_A}\n- 2026-10-29 10:08: entrega conferida {SHA_B}\n"
        rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra=historico)
        self.assertEqual(rc, 0, saida)
        conteudo = (self.tmp / ARQ).read_bytes()
        esperado = ["modo: entrega", f"Pedido: {ID}", "Agente conferido: forge:dev-exemplo", f"Arquivo: {(self.tmp / ARQ).resolve()}",
                    f"Worktree: {self.pasta}", "Branch: melhoria/x", "Base: develop", f"Base-sha: {BASE_SHA}", f"Desde: {SHA_B}",
                    f"Brief-sha256: {hashlib.sha256(conteudo).hexdigest()}", "Etapa: codigo", "<<<BRIEF"]
        self.assertEqual(saida.decode().splitlines()[:12], esperado)
        self.assertTrue(saida.endswith(conteudo + b"\nBRIEF>>>\n"))

    def test_sem_conferida_no_historico_a_linha_desde_nao_sai(self):
        rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra="- 2026-10-29 07:36: aberto\n")
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("Desde:", saida.decode())

    def test_desde_e_a_linha_mais_recente_entre_conferida_e_base_do_dono(self):
        dono = f"- 2026-10-29 11:00: base do delta fixada pelo dono {SHA_B}\n"
        decisao = "DECISÃO DO DONO (2026-10-29): \"fixar a base\".\n"
        conferida = f"- 2026-10-29 07:36: entrega conferida {SHA_A}\n"
        casos = {"dono depois da conferida": (decisao + conferida + dono, SHA_B), "so a do dono": (decisao + dono, SHA_B),
                 "conferida depois do dono": (decisao + dono + conferida, SHA_A)}
        for nome, (historico, esperado) in casos.items():
            with self.subTest(nome):
                rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra=historico)
                self.assertEqual(rc, 0, saida)
                self.assertIn(f"Desde: {esperado}", saida.decode().splitlines())

    def recusa(self, motivo, *extra):
        rc, saida = self.entrega(*extra)
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), f"brief mensagem: {motivo}")

    def test_entrega_sem_worktree_e_recusada(self):
        self.recusa(SEM_WORKTREE)

    def test_entrega_com_worktree_relativo_e_recusada(self):
        self.recusa(SEM_WORKTREE, "--worktree", ".")

    def test_entrega_com_worktree_inexistente_e_recusada(self):
        self.recusa(SEM_WORKTREE, "--worktree", str(self.pasta / "nao-existe"))

    def test_entrega_com_ref_anterior_ou_parecer_e_recusada(self):
        for extra in (("--ref", "melhoria/x"), ("--anterior", ARQ), ("--parecer", "docs/reviews/x.md")):
            with self.subTest(extra=extra):
                self.recusa(SEM_WORKTREE, "--worktree", str(self.pasta), *extra)

    def test_entrega_com_controle_no_worktree_e_recusada_sem_imprimir_o_valor(self):
        rc, saida = self.entrega("--worktree", str(self.pasta) + "\x01")
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), "brief mensagem: o campo --worktree tem o caractere de controle ou de formato U+0001")

    def test_brief_sem_etapa_branch_base_ou_base_sha_recusa_a_entrega(self):
        for faltando in ("Etapa: codigo   ", "Branch: melhoria/x   ", "Base: develop   ", f"   Base-sha: {BASE_SHA}"):
            with self.subTest(faltando=faltando):
                self.gravar(ARQ, self.completo.replace(faltando, "", 1))
                self.recusa(SEM_CABECALHO, "--worktree", str(self.pasta))


if __name__ == "__main__":
    unittest.main()
