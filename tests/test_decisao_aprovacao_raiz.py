"""BRIEF-DECISAO-POSTERIOR (E5 da versao-035): a aprovação do brief (P-N4) vale só com o pedido certo na coluna 2 (C-2) e é lida do
quadro da raiz do próprio brief, da `--raiz` e de ~/.forge-contrib, nessa ordem, sem cair na seguinte (C-4, C-5). Sem rede."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_decisao_aprovacao import ANTES, CABECALHO, FORGE_CHECK, PEDIDO, brief, linha  # noqa: E402

QUADRO = "docs/kanban/conferencias.md"


class AprovacaoNaRaizDoBrief(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-e5-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.contrib, self.clone = self.tmp / "home" / ".forge-contrib", self.tmp / "clone"  # A (pedido, brief) e B (o clone)
        self.clone.mkdir(parents=True)
        self.gravar(self.contrib, "docs/pedidos/exemplo.md", PEDIDO)

    def gravar(self, base, rel, texto):
        arq = base / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def conferir(self, *linhas, quadro_em=None, raiz=None):
        if linhas:
            self.gravar(quadro_em or self.contrib, QUADRO, CABECALHO + "".join(linhas))
        arq = self.gravar(self.contrib, "docs/briefs/exemplo-dev-exemplo-1.md", brief(ANTES))
        os.utime(arq, (t := time.mktime(time.strptime("2026-01-01 10:00:30", "%Y-%m-%d %H:%M:%S")), t))  # escrito às 10:00 (A1)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))}
        env["HOME"] = str(self.tmp / "home")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(raiz or self.contrib), "--raiz-pedidos", str(self.contrib),
                            "brief", str(arq), "--pedido", "exemplo"], capture_output=True, text=True, env=env, timeout=60)
        return r.returncode, r.stdout

    def assertAvisa(self, rc, saida):
        self.assertIn("decisões: decisão posterior à aprovação 2026-01-01 10:00:", saida)
        self.assertEqual(rc, 0, saida)

    def assertCobrada(self, rc, saida):
        self.assertIn('decisões: falta "DECISÃO DO DONO 2026-01-01 11:00', saida)
        self.assertNotIn("posterior à aprovação", saida)
        self.assertEqual(rc, 1, saida)

    def test_linha_aprovado_vale_so_com_o_pedido_na_coluna_2(self):
        self.assertAvisa(*self.conferir(linha("2026-01-01 10:00").replace("| exemplo |", "| EXEMPLO |")))
        for outro in ("outro", "exemplo-x", "exemplo.md"):
            with self.subTest(pedido=outro):
                self.assertCobrada(*self.conferir(linha("2026-01-01 10:00").replace("| exemplo |", f"| {outro} |")))


if __name__ == "__main__":
    unittest.main()
