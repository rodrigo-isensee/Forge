"""AV5 (0.45.7, E1.1): R-MAIN, R-VERIFY, R-CUSTO, R-CONTRIB e R-COPIA são trechos de docs/regras/R-LIMITES.md; a citação `(R-<ID>)`
continua achando o texto, e ID inexistente continua "regra ausente"."""
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
fc = SourceFileLoader("forge_check_r_limites", str(RAIZ / "bin" / "forge-check")).load_module()


class CitacaoDeTrecho(unittest.TestCase):
    def test_id_de_trecho_traz_so_o_trecho(self):
        linhas, motivo = fc.linhas_da_fonte(RAIZ, "R-MAIN")
        texto = "\n".join(linhas)
        self.assertIsNone(motivo)
        self.assertIn("é do usuário", texto)
        self.assertNotIn("--no-verify", texto)

    def test_cada_id_juntado_tem_trecho(self):
        for id_ in ("R-MAIN", "R-VERIFY", "R-CUSTO", "R-CONTRIB", "R-COPIA"):
            with self.subTest(id_):
                linhas, motivo = fc.linhas_da_fonte(RAIZ, id_)
                self.assertIsNone(motivo)
                self.assertTrue(any(l.startswith("- ") for l in linhas))

    def test_id_inexistente_segue_ausente(self):
        self.assertEqual(fc.linhas_da_fonte(RAIZ, "R-XYZ"), (None, "regra ausente"))


if __name__ == "__main__":
    unittest.main()
