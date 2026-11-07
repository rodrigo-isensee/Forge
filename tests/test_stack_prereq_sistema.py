"""Pacote da stack node-react: pré-requisitos de sistema do navegador de testes (cartão STACK-PREREQ-SISTEMA)."""
import re
import unittest
from pathlib import Path

PRONTO = Path(__file__).resolve().parent.parent / "stacks" / "node-react" / "pronto.md"


def secao(texto, titulo):
    achado = re.search(rf"^## {re.escape(titulo)}\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return achado.group(1) if achado else ""


class PreRequisitosDoSistema(unittest.TestCase):
    def setUp(self):
        self.corpo = secao(PRONTO.read_text(encoding="utf-8"), "Pré-requisitos do sistema")

    def test_secao_existe(self):
        self.assertTrue(self.corpo.strip(), "falta a seção '## Pré-requisitos do sistema' em pronto.md")

    def test_comando_de_instalacao_e_do_usuario(self):
        self.assertIn("npx playwright install --with-deps chromium", self.corpo)
        self.assertIn("sudo", self.corpo)
        self.assertIn("R-CONFORMIDADE", self.corpo)

    def test_pre_voo_so_leitura_antes_da_primeira_suite(self):
        self.assertIn("ldd", self.corpo)
        self.assertIn("PLAYWRIGHT_BROWSERS_PATH", self.corpo)
        self.assertIn("not found", self.corpo)
        self.assertIn("qa-engineer", self.corpo)
        self.assertIn("primeira suíte", self.corpo)

    def test_frase_para_pedir_ao_usuario(self):
        self.assertRegex(self.corpo, r"(?m)^> .*npx playwright install --with-deps chromium")


if __name__ == "__main__":
    unittest.main()


class MutacaoIncremental(unittest.TestCase):
    """M-4 (versao-041 E3a): o Stryker roda em modo incremental e a meta começa na primeira rodada."""

    def setUp(self):
        texto = secao(PRONTO.read_text(encoding="utf-8"), "Vermelho antes do verde, mutação e contrato")
        self.linha = next((l for l in texto.splitlines() if l.startswith("- Mutação")), "")

    def test_comando_do_stryker_e_incremental(self):
        self.assertIn("pnpm stryker run --incremental --mutate", self.linha)

    def test_meta_comeca_na_primeira_rodada_e_so_sobe(self):
        self.assertIn("começa pela pontuação da primeira rodada e só sobe", self.linha)
