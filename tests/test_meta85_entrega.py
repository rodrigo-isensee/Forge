"""META85-ENTREGA-COM-MUTANTES (v0478 E34.1): na etapa codigo com código no escopo, o `forge-check entrega` (forma antiga, o PQ do
autor) só passa com os logs da mutação (`--mutantes`) e do pronto (`--pronto`) da stack: `head=<sha40>` do head entregue na 1.ª
linha e `rc=0` na última. Sem código no escopo, ou fora da etapa codigo, nada muda."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ambiente_limpo  # noqa: E402
from test_volta_por_delta import FORGE_CHECK, Repositorio  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class ProvasDaEntrega(Repositorio):
    def setUp(self):
        super().setUp()
        self.gravar_pedido()

    def log(self, nome, texto):
        caminho = self.tmp / nome
        caminho.write_text(texto, encoding="utf-8")
        return caminho

    def verde(self, nome):
        return self.log(nome, f"head={self.head()}\nOK\nrc=0\n")

    def entregar(self, *provas, etapa="codigo"):
        return self.check("entrega", self.pedido, "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base,
                          "--etapa", etapa, *provas)

    def pendentes(self, saida):
        return [l for l in saida.splitlines() if l.startswith("pendente: entrega de código sem a prova de")]

    def test_codigo_com_as_duas_provas_verdes_passa(self):
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar("--mutantes", self.verde("m.log"), "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"prova: mutação verde no head {self.head()[:7]}", saida)
        self.assertIn(f"prova: pronto verde no head {self.head()[:7]}", saida)

    def test_codigo_sem_provas_reprova_as_duas(self):
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar()
        self.assertEqual(rc, 1, saida)
        self.assertEqual(len(self.pendentes(saida)), 2, saida)
        self.assertIn("(--mutantes <log>: sem log)", saida)
        self.assertIn("(--pronto <log>: sem log)", saida)

    def test_so_o_pronto_faltando_continua_barrado(self):
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar("--mutantes", self.verde("m.log"))
        self.assertEqual(rc, 1, saida)
        self.assertEqual(self.pendentes(saida), [l for l in self.pendentes(saida) if "de pronto" in l], saida)
        self.assertEqual(len(self.pendentes(saida)), 1, saida)

    def test_mutante_vivo_rc_1_reprova(self):
        self.commitar({"src/app.py": "x = 1\n"})
        vivo = self.log("m.log", f"head={self.head()}\nM1 sobreviveu\nrc=1\n")
        rc, saida = self.entregar("--mutantes", vivo, "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("(--mutantes <log>: a última linha não é rc=0)", saida)

    def test_log_de_outro_head_reprova(self):
        antigo = self.verde("m.log")  # o log do head anterior não prova o novo
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar("--mutantes", antigo, "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("(--mutantes <log>: a 1.ª linha não é o head entregue (head=<sha40>))", saida)

    def test_log_vazio_reprova(self):
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar("--mutantes", self.log("m.log", "\n\n"), "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("(--mutantes <log>: a 1.ª linha não é o head entregue", saida)

    def test_linhas_vazias_nas_pontas_nao_contam(self):
        self.commitar({"src/app.py": "x = 1\n"})
        com_brancos = self.log("m.log", f"\n  \nhead={self.head()}\nOK\nrc=0\n\n\n")
        rc, saida = self.entregar("--mutantes", com_brancos, "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 0, saida)

    def test_log_ausente_reprova(self):
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar("--mutantes", self.tmp / "nao-existe.log", "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("(--mutantes <log>: log ilegível)", saida)

    def test_log_acima_do_teto_reprova(self):
        self.commitar({"src/app.py": "x = 1\n"})
        grande = self.log("m.log", f"head={self.head()}\n" + "x" * (8 * 1024 * 1024) + "\nrc=0\n")
        rc, saida = self.entregar("--mutantes", grande, "--pronto", self.verde("p.log"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("(--mutantes <log>: log maior que o teto)", saida)

    def test_sem_codigo_no_escopo_nao_cobra(self):
        self.commitar({"docs/guia.md": "# guia\n", "tests/test_app.py": "x = 1\n"})
        rc, saida = self.entregar()
        self.assertEqual(rc, 0, saida)
        self.assertEqual(self.pendentes(saida), [], saida)

    def test_fora_da_etapa_codigo_nao_cobra(self):
        self.commitar({"src/app.py": "x = 1\n"})
        rc, saida = self.entregar(etapa="review")
        self.assertEqual(self.pendentes(saida), [], saida)

    def test_forma_nova_recusa_as_opcoes(self):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.repo), "entrega", "--pedido", "p1", "--branch", "melhoria/x",
                            "--etapa", "codigo", "--mutantes", "m.log"], env=dict(ambiente_limpo(), HOME=str(self.home)),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("--mutantes e --pronto", r.stderr)


if __name__ == "__main__":
    import unittest
    unittest.main()
