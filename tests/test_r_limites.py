"""AV5 (0.45.7, E1.1): R-MAIN, R-VERIFY, R-CUSTO, R-CONTRIB e R-COPIA são trechos de docs/regras/R-LIMITES.md; a citação `(R-<ID>)`
continua achando o texto, e ID inexistente continua "regra ausente"."""
import sys
import tempfile
import unittest
from unittest import mock
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
fc = SourceFileLoader("forge_check_r_limites", str(RAIZ / "bin" / "forge-check")).load_module()
sys.path.insert(0, str(RAIZ / "tests"))
from apoio_regra_id import ids  # noqa: E402


class CitacaoDeTrecho(unittest.TestCase):
    def ler(self, raiz, rid):
        """linhas_da_fonte que nunca levanta: exceção é falha do teste (a citação responde, não quebra)."""
        try:
            return fc.linhas_da_fonte(raiz, rid)
        except Exception as erro:  # noqa: BLE001 - qualquer exceção é o defeito que o teste acusa
            self.fail(f"linhas_da_fonte({rid}) levantou {erro!r}")

    def test_id_de_trecho_traz_so_o_trecho(self):
        linhas, motivo = self.ler(RAIZ, "R-MAIN")
        texto = "\n".join(linhas)
        self.assertIsNone(motivo)
        self.assertIn("é do usuário", texto)
        self.assertNotIn("--no-verify", texto)

    def test_regra_com_arquivo_proprio_vem_do_arquivo(self):
        linhas, motivo = self.ler(RAIZ, "R-QA")
        self.assertIsNone(motivo)
        self.assertIn("id: R-QA", linhas)

    def test_cada_id_juntado_tem_trecho(self):
        for id_ in ("R-MAIN", "R-VERIFY", "R-CUSTO", "R-CONTRIB", "R-COPIA"):
            with self.subTest(id_):
                linhas, motivo = self.ler(RAIZ, id_)
                self.assertIsNone(motivo)
                self.assertTrue(any(l.startswith("- ") for l in linhas))

    def test_id_inexistente_segue_ausente(self):
        self.assertEqual(self.ler(RAIZ, "R-XYZ"), (None, "regra ausente"))

    def test_sem_r_limites_o_trecho_e_ausente(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(fc, "PLUGIN", Path(tmp)):
            (Path(tmp) / "docs" / "regras").mkdir(parents=True)
            self.assertEqual(self.ler(Path(tmp), "R-MAIN"), (None, "regra ausente"))


class IdsDoApoio(unittest.TestCase):
    def test_ids_aceita_arquivo_proprio_e_trecho_e_recusa_inexistente(self):
        self.assertEqual(ids("(R-QA) (R-MAIN) (R-XYZ)"), {"R-QA", "R-MAIN"})


if __name__ == "__main__":
    unittest.main()
