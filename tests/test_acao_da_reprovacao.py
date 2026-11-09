"""O1 (0.44.1): ação fixa por classe de reprovação no `bin/forge-check`. As classes de forma (forma, base, citação, etapa) a
ferramenta corrige sem rodada do Jarvis; a mesma classe reprovada N vezes no mesmo brief vai ao dono."""
import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402

REPROVADO = ["conferencia", "registrar", "--pedido", "xpto", "--brief", "xpto-tech-lead-1", "--modo", "brief",
             "--resultado", "reprovado", "--merito", "s"]


def carregar():
    carregador = importlib.machinery.SourceFileLoader("forge_check_o1", FORGE_CHECK)
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader("forge_check_o1", carregador))
    carregador.exec_module(modulo)
    return modulo


class Catalogo(unittest.TestCase):
    def test_toda_classe_do_catalogo_tem_acao_e_as_de_forma_sao_da_ferramenta(self):
        fc = carregar()
        self.assertEqual(sorted(fc.ACAO_DA_CLASSE), sorted(fc.CLASSES_DE_FALHA))
        for classe, (quem, acao) in fc.ACAO_DA_CLASSE.items():
            with self.subTest(classe):
                self.assertIn(quem, ("ferramenta", "jarvis", "destino", "dono"))
                self.assertGreater(len(acao), 8)
        self.assertEqual(sorted(c for c, (q, _) in fc.ACAO_DA_CLASSE.items() if q == "ferramenta"),
                         ["base", "forma"])
        self.assertGreaterEqual(fc.LIMIAR_AO_DONO, 2)


class Registrar(Raiz):
    def setUp(self):
        super().setUp()
        self.gravar("KANBAN.md", "# Quadro\n")

    def registrar(self, classe, rodada="1", modo="brief", tardio=()):
        args = list(REPROVADO) + ["--classe", classe, "--rodada", rodada]
        args[args.index("--modo") + 1] = modo
        return self.rodar(*args, *tardio)

    def acao(self, linhas):
        return [l for l in linhas if l.startswith("ação: ")]

    def test_classe_de_forma_roda_a_ferramenta_sem_rodada_do_jarvis(self):
        for classe, comando in (("base", "brief selar --sem-selar"), ("forma", "brief mensagem")):
            with self.subTest(classe):
                self.gravar("docs/kanban/conferencias.md", "")
                cod, linhas, erro = self.registrar(classe)
                self.assertEqual(cod, 0, erro)
                acao = self.acao(linhas)
                self.assertEqual(len(acao), 1, linhas)
                self.assertTrue(acao[0].startswith(f"ação: ferramenta: forge-check {comando} --pedido xpto --arquivo "
                                                   "docs/briefs/xpto-tech-lead-1.md -> rc 2 "), acao)

    def test_etapa_e_citacao_sao_do_jarvis(self):
        """B2 (review da 0.44.1): etapa e citação não rodam a ferramenta (o `brief selar` gravaria o selo)."""
        for classe in ("etapa", "citacao"):
            with self.subTest(classe):
                self.gravar("docs/kanban/conferencias.md", "")
                cod, linhas, _ = self.registrar(classe)
                self.assertEqual(cod, 0)
                self.assertEqual(self.acao(linhas), ["ação: jarvis: " + carregar().ACAO_DA_CLASSE[classe][1]])

    def test_outra_classe_traz_a_acao_fixa_de_quem_corrige(self):
        cod, linhas, _ = self.registrar("escopo")
        self.assertEqual(cod, 0)
        self.assertEqual(self.acao(linhas), ["ação: jarvis: " + carregar().ACAO_DA_CLASSE["escopo"][1]])

    def test_no_modo_entrega_a_classe_de_forma_nao_roda_o_brief(self):
        cod, linhas, _ = self.registrar("base", modo="entrega")
        self.assertEqual(cod, 0)
        self.assertEqual(self.acao(linhas), ["ação: jarvis: " + carregar().CLASSES_DE_FALHA["base"]])

    def test_a_mesma_classe_reprovada_n_vezes_no_brief_vai_ao_dono(self):
        fc = carregar()
        for n in range(1, fc.LIMIAR_AO_DONO + 1):
            cod, linhas, erro = self.registrar("base", rodada=str(n), tardio=("--tardio", "nao") if n > 1 else ())
            self.assertEqual(cod, 0, erro)
        acao = self.acao(linhas)
        self.assertEqual(len(acao), 1, linhas)
        self.assertTrue(acao[0].startswith(f"ação: ao dono: base reprovou {fc.LIMIAR_AO_DONO} vezes o brief xpto-tech-lead-1"), acao)
        cod, linhas, _ = self.registrar("escopo", rodada=str(fc.LIMIAR_AO_DONO + 1), tardio=("--tardio", "nao"))
        self.assertTrue(self.acao(linhas)[0].startswith("ação: jarvis: "), "outra classe conta à parte")


if __name__ == "__main__":
    unittest.main()
