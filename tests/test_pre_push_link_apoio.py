"""E13.1 do v0456 (decisão do dono, 2026-11-10 21:02): o `bin/forge-testes` carrega o `bin/forge_apoio_testes.py` da
pasta dele; com o apoio como link, a branch apontaria o plano dirigido para outro código. A função `afetados` do
pre-push recusa o plano dirigido quando o apoio é link e roda a suíte inteira (falha fechada); como arquivo comum, o
plano dirigido segue. Reusa o repositório de brinquedo de `test_pre_push_afetados`.
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_pre_push_afetados import AFETADOS, RAIZ, TODAS, Base  # noqa: E402


class PrePushLinkApoio(Base):
    def test_apoio_comum_segue_o_plano_dirigido(self):
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, AFETADOS)
        self.assertIn("rodando só os testes afetados", erro)

    def test_apoio_que_e_link_recusa_o_plano_e_roda_a_suite_inteira(self):
        apoio = self.repo / "bin" / "forge_apoio_testes.py"
        apoio.unlink()
        (self.repo / "bin" / "apoio_real.py").write_text((RAIZ / "bin" / "forge_apoio_testes.py").read_text())
        os.symlink("apoio_real.py", apoio)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "apoio vira link")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD"))  # o link já está na base
        self.commit("toca a ferramenta", bin__forge_sugerir="x = 2\n")
        codigo, marcas, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(marcas, TODAS)
        self.assertNotIn("rodando só os testes afetados", erro)


if __name__ == "__main__":
    unittest.main()
