"""I4: o merge do `bin/forge-fechar` exige `bateria`, `bateria (python 3.14)` e `catraca` em `pass` (lista positiva).

Reaproveita o ambiente de `test_fechar.Fechar` e a sequência de leituras dos checks de `test_fechar_espera_catraca` (o módulo, não a classe).
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402
import test_fechar_espera_catraca as seq  # noqa: E402

OK = ["bateria\tpass\t1m\turl", "bateria (python 3.14)\tpass\t1m\turl", "catraca\tpass\t5s\turl"]


class FecharChecksExigidos(unittest.TestCase):
    tearDown, git, fechar, chamadas = base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas
    setUp, leituras_de_checks, sem_merge, cat = (seq.FecharEsperaCatraca.setUp, seq.FecharEsperaCatraca.leituras_de_checks,
                                                 seq.FecharEsperaCatraca.sem_merge, seq.FecharEsperaCatraca.cat)

    def leituras(self, *blocos):
        (self.estado / "checks_seq").write_text("---\n".join("".join(f"{l}\n" for l in b) for b in blocos))

    def para(self, linhas, nome, estado, *extra, **env):
        self.leituras(linhas)
        r = self.fechar("p1", "--ref", "melhoria/x", *extra, **env)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(f"o check exigido {nome} não passou (estado: {estado})", r.stderr)
        self.assertTrue(self.sem_merge())

    def test_exigido_em_skipping_para_mesmo_com_o_nome_mais_longo_em_pass(self):
        self.para(["bateria\tskipping\t0\turl", *OK[1:]], "bateria", "skipping")

    def test_catraca_em_skipping_para(self):
        self.para([*OK[:2], "catraca\tskipping\t0\turl"], "catraca", "skipping")

    def test_duplicata_do_exigido_precisa_de_todas_em_pass(self):
        self.para([*OK, "bateria\tskipping\t0\turl"], "bateria", "skipping")

    def test_ausente_espera_e_para_no_fim_da_espera(self):
        self.para(OK[1:], "bateria", "ausente após 0s", "--espera", "0")

    def test_ausente_espera_e_mescla_quando_aparece_em_pass(self):
        self.leituras(OK[:2], OK)
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "600")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.leituras_de_checks(), 2)

    def test_variavel_do_ambiente_nao_muda_a_lista(self):
        self.para(["bateria\tskipping\t0\turl", *OK[1:]], "bateria", "skipping", CHECKS_EXIGIDOS="", FORGE_FECHAR_CHECKS="")

    def test_tudo_pass_e_nao_exigido_em_skipping_mescla(self):
        self.leituras([*OK, "checagem rápida (push na develop)\tskipping\t0\turl"])
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("checks verdes (exigidos em pass: bateria bateria (python 3.14) catraca).", r.stdout)

    def test_catraca_velha_do_rotulo_nao_conta_e_a_nova_em_pass_mescla(self):
        (self.estado / "rotulo_na_leitura").write_text("3\n")
        (self.estado / "texto").write_text(base.Fechar.ITEM_MARCADO)
        self.leituras([*OK[:2], self.cat("fail", 1)], [*OK[:2], self.cat("cancel", 1), self.cat("pass", 2)])
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "600")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_lista_vazia_por_edicao_para(self):
        texto = base.SCRIPT.read_text(encoding="utf-8")
        copia = self.tmp / "forge-fechar"
        copia.write_text(re.sub(r"(?m)^readonly CHECKS_EXIGIDOS=\(.*\)$", "readonly CHECKS_EXIGIDOS=()", texto), encoding="utf-8")
        self.assertNotEqual(copia.read_text(encoding="utf-8"), texto)
        r = base.subprocess.run(["bash", str(copia), "p1", "--ref", "melhoria/x"], cwd=self.proj, env=self.env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 1)
        self.assertIn("CHECKS_EXIGIDOS vazia", r.stderr)
        self.assertEqual(self.chamadas(), [])


if __name__ == "__main__":
    unittest.main()
