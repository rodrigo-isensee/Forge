"""F6, E5.5: `forge-check medida` e `forge-check escape` moram em bin/forge_medidas.py; os ramos de falha que os testes de ponta a ponta
(test_voltas.MedidaDoTopico, test_voltas.MedidaDaRelease e test_medidas_m14b.DefeitoEscapado) não alcançam."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
ESCAPE = ["escape", "registrar", "--pedido", "p", "--parecer-final", "docs/qa/p.md", "--achado-por", "uso", "--gravidade", "alto",
          "--controle-que-faltou", "qa", "--nota", "n"]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-medidas-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp / "home"), "LC_ALL": "C",
                    "GIT_CONFIG_NOSYSTEM": "1"}
        (self.tmp / "docs" / "kanban").mkdir(parents=True)
        (self.tmp / "KANBAN.md").write_text("## Em andamento\n", encoding="utf-8")

    def rodar(self, script, *args):
        r = subprocess.run([sys.executable, "-I", str(script), "--raiz", str(self.tmp), *args], capture_output=True, text=True,
                           env=self.env, cwd=self.tmp)
        self.assertNotIn("Traceback", r.stderr)  # a queda do script é falha do teste, não erro adiante
        return r.returncode, r.stdout, r.stderr


class RamosDeFalhaDoModuloMedidas(Base):
    AUSENTE = "forge-check: bin/forge_medidas.py ausente ao lado do forge-check; nada feito\n"

    def test_copia_avulsa_sem_o_modulo_sai_com_2_nos_tres_e_nada_grava(self):
        copia = self.tmp / "copia" / "bin"
        copia.mkdir(parents=True)
        (copia / "forge-check").write_bytes(FORGE_CHECK.read_bytes())
        for args in (("medida", "--pedido", "p", "--merge", "a" * 40), tuple(ESCAPE), ("escape", "resumo")):
            with self.subTest(args[0:2]):
                self.assertEqual(self.rodar(copia / "forge-check", *args)[:2], (2, self.AUSENTE))
        self.assertEqual(sorted(p.name for p in (self.tmp / "docs" / "kanban").iterdir()), [])

    def test_com_o_modulo_os_tres_rodam(self):
        cod, saida, erro = self.rodar(FORGE_CHECK, *ESCAPE)
        self.assertEqual(cod, 0, erro)
        self.assertRegex(saida, r"^\| \d{4}-\d{2}-\d{2} \d{2}:\d{2} \| p \| docs/qa/p\.md \| uso \| alto \| qa \| n \| nao-classificado \|\n$")
        cod, saida, erro = self.rodar(FORGE_CHECK, "escape", "resumo")
        self.assertEqual((cod, saida.splitlines()[-1]), (0, "escapes: total: escapes=1 pedidos_prontos=0 taxa=- dias=30"), erro)
        cod, saida, erro = self.rodar(FORGE_CHECK, "medida", "--pedido", "p", "--merge", "a" * 40)
        self.assertEqual((cod, saida, erro), (2, "", "medida: commit do --merge ausente no repositório; nada gravado\n"))


if __name__ == "__main__":
    unittest.main()
