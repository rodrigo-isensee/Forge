"""scripts/gerar-derivados.py (proposta 1 da auditoria dos testes): o gerador único roda cada gerador que existe, diz o que
mudou e, no --conferir, não grava e sai 1 com derivado desatualizado. Os geradores aqui são falsos, numa raiz de brinquedo:
o teste confere o script, não os índices (esses têm os próprios testes)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "gerar-derivados.py"

# Gerador falso: grava o derivado com "novo"; no --conferir, rc 0 se o derivado já é "novo", senão 1. Registra o GIT_DIR
# que recebeu, e sai 3 se o arquivo `vermelho` existe na raiz.
FALSO = '''import os, sys
from pathlib import Path
raiz = Path(__file__).resolve().parent.parent
derivado = raiz / "docs" / DERIVADO
(raiz / "visto-git-dir").write_text(os.environ.get("GIT_DIR", "-"), encoding="utf-8")
if (raiz / "vermelho").exists():
    print("quebrou"); sys.exit(3)
if sys.argv[1:] == ["--conferir"]:
    sys.exit(0 if derivado.is_file() and derivado.read_text(encoding="utf-8") == "novo" else 1)
derivado.write_text("novo", encoding="utf-8")
'''


class GerarDerivados(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        (self.raiz / "scripts").mkdir()
        (self.raiz / "docs").mkdir()
        shutil.copy(SCRIPT, self.raiz / "scripts" / "gerar-derivados.py")
        for gerador, derivado in (("indice-forge.py", "indice-forge.md"), ("indice-fixtures.py", "hooks-fixtures.md")):
            (self.raiz / "scripts" / gerador).write_text(FALSO.replace("DERIVADO", repr(derivado)), encoding="utf-8")
            (self.raiz / "docs" / derivado).write_text("velho", encoding="utf-8")

    def rodar(self, *args, env=None):
        ambiente = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), **(env or {})}
        return subprocess.run([sys.executable, "-I", "scripts/gerar-derivados.py", *args], cwd=self.raiz, env=ambiente,
                              capture_output=True, text=True)

    def derivado(self, nome="indice-forge.md"):
        return (self.raiz / "docs" / nome).read_text(encoding="utf-8")

    def test_grava_e_diz_o_que_mudou(self):
        (self.raiz / "docs" / "hooks-fixtures.md").write_text("novo", encoding="utf-8")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.derivado(), "novo")
        self.assertIn("docs/indice-forge.md: mudou", r.stdout)
        self.assertIn("docs/hooks-fixtures.md: sem mudança", r.stdout)
        self.assertIn("rc=0", r.stdout)

    def test_conferir_nao_grava_e_sai_1_com_derivado_desatualizado(self):
        (self.raiz / "docs" / "hooks-fixtures.md").write_text("novo", encoding="utf-8")
        r = self.rodar("--conferir")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.derivado(), "velho")
        self.assertIn("docs/indice-forge.md: desatualizado", r.stdout)
        self.assertIn("docs/hooks-fixtures.md: em dia", r.stdout)

    def test_conferir_sai_0_com_tudo_em_dia(self):
        self.assertEqual(self.rodar().returncode, 0)
        r = self.rodar("--conferir")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.count(": em dia"), 2)

    def test_gerador_vermelho_sai_1_nos_dois_modos(self):
        (self.raiz / "vermelho").write_text("", encoding="utf-8")
        for args in ((), ("--conferir",)):
            with self.subTest(args=args):
                r = self.rodar(*args)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("gerador vermelho (rc=3): quebrou", r.stdout)

    def test_gerador_ausente_e_pulado_e_os_outros_rodam(self):
        (self.raiz / "scripts" / "indice-fixtures.py").unlink()
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ausente (scripts/indice-fixtures.py), pulado", r.stdout)
        self.assertEqual(self.derivado(), "novo")

    def test_uso_errado_sai_2_sem_rodar_gerador(self):
        for args in (("--gravar",), ("--conferir", "x")):
            with self.subTest(args=args):
                self.assertEqual(self.rodar(*args).returncode, 2)
        self.assertFalse((self.raiz / "visto-git-dir").exists())
        self.assertEqual(self.derivado(), "velho")

    def test_gerador_roda_sem_o_git_dir_de_quem_chamou(self):
        self.rodar(env={"GIT_DIR": str(self.raiz / "outro.git")})
        self.assertEqual((self.raiz / "visto-git-dir").read_text(encoding="utf-8"), "-")

    def test_diz_o_que_fica_fora(self):
        r = self.rodar("--conferir")
        self.assertIn("fora: pesos da suíte", r.stdout)
        self.assertIn("fora: mapa de testes", r.stdout)

    def test_todo_gerador_da_lista_existe_no_forge(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--conferir"], cwd=RAIZ,
                           env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")}, capture_output=True, text=True)
        self.assertNotIn("ausente", r.stdout)
        self.assertEqual(r.stdout.count("gerar-derivados: "), 5, r.stdout)


if __name__ == "__main__":
    unittest.main()
