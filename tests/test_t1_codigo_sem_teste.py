"""T1 (decisão 20; 0.43.3): a entrega que muda código sem mudar nem acrescentar teste sai sinalizada no `forge-check pr` e no
`forge-check entrega --pedido`, nas classes N e C; a classe T fica isenta. A linha nunca reprova sozinha: o review confere a
justificativa do `## Sem teste` do PR. Sem rede."""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_selo_e_entrega import Repositorio, fc  # noqa: E402


class Classificacao(unittest.TestCase):
    def test_codigo_e_teste(self):
        for nome in ("bin/forge-check", "hooks/agentes.py", "src/app.ts", ".github/workflows/ci.yml", "tests/catraca.py",
                     "scripts/x.sh", "tests/guarda_git.py"):
            with self.subTest(nome=nome):
                self.assertTrue(fc.e_codigo(nome))
        for nome in ("README.md", "docs/a.py", "changelog.d/x.md", "tests/test_x.py", "src/a.test.ts", "tests/config.json",
                     "docs/reviews/p.md", "bin/LEIA.md", "package.json"):
            with self.subTest(nome=nome):
                self.assertFalse(fc.e_codigo(nome))
        self.assertTrue(fc.e_teste("tests/hooks/caso.json"))
        self.assertFalse(fc.e_teste("tests/config.json"))
        self.assertFalse(fc.e_teste("tests/catraca.py"))


class NaEntrega(Repositorio):
    """O `entrega --pedido` da etapa código: a linha `sem teste:` sai sem mudar o resultado."""

    def setUp(self):
        super().setUp()
        self.brief(arquivos="bin/app, docs/notas/, tests/")
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)

    def conferir(self):
        return self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", "--sem-gravar")

    def test_codigo_sem_teste_sinaliza_sem_reprovar(self):
        self.entregar()
        rc, saida = self.conferir()
        self.assertIn('sem teste: código mudado sem teste mudado ou novo (classe C): bin/app;', saida)
        self.assertIn("resultado: cumpriu", saida)
        self.assertEqual(rc, 0, saida)

    def test_teste_novo_cala_a_linha(self):
        self.gravar("tests/test_app.py", "def test_f():\n    assert True\n")
        self.entregar("tests/test_app.py")
        rc, saida = self.conferir()
        self.assertNotIn("sem teste:", saida)

    def test_teste_so_com_comentario_nao_conta(self):
        self.gravar("tests/test_app.py", "# só um comentário\n\n")
        self.entregar("tests/test_app.py")
        rc, saida = self.conferir()
        self.assertIn("sem teste:", saida)

    def test_classe_pela_funcao_da_frente_g(self):
        """O gancho: com `classe_da_entrega` presente, a T isenta e a N e a C aparecem no rótulo."""
        self.entregar()
        rev = f"{self.base}..HEAD"
        nomes = fc.nomes_do_intervalo(self.proj, self.base, "HEAD")
        for classe, espera in (("T", None), ("N", "classe N"), ("C", "classe C")):
            with self.subTest(classe=classe), mock.patch.object(fc, "classe_da_entrega", lambda *a, c=classe: (c, [], []), create=True):
                aviso = fc.aviso_de_codigo_sem_teste(self.proj, rev, nomes, fc.classe_para_o_t1(self.proj, "HEAD", "develop"))
                self.assertEqual(aviso if espera is None else espera in aviso, None if espera is None else True, aviso)

    def test_classe_que_falha_vale_n(self):
        def falha(*a):
            raise RuntimeError
        with mock.patch.object(fc, "classe_da_entrega", falha, create=True):
            self.assertEqual(fc.classe_para_o_t1(self.proj, "HEAD", "develop"), "N")


class NoPr(Repositorio):
    def test_pr_sinaliza_no_stderr(self):
        self.entregar()
        rc, saida = self.rodar("pr", "x", "--base", "develop")
        self.assertIn('pr: sem teste: código mudado sem teste mudado ou novo', saida)
        self.assertIn("): bin/app;", saida)


if __name__ == "__main__":
    unittest.main()
