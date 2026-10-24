"""N-FECHAR-b, B1: a parada do passo 4 diz se pedir o rótulo afrouxa-regra ajuda (só texto; a decisão não muda).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

RUN = "https://github.com/o/r/actions/runs/{}/job/{}"


class FecharAvisoRotulo(unittest.TestCase):
    setUp = base.Fechar.setUp
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas

    def checks(self, *linhas):
        (self.estado / "checks").write_text("".join(f"{l}\n" for l in linhas), encoding="utf-8")

    def avisos(self, r, trecho):
        return [l for l in r.stderr.splitlines() if trecho in l]

    def um_aviso(self, r, trecho):
        achadas = self.avisos(r, trecho)
        self.assertEqual(len(achadas), 1, f"esperava 1 aviso com {trecho!r}:\n{r.stderr}")
        return achadas[0]

    def test_so_catraca_vermelha_sugere_esperar_rotulo_depois_de_ler_o_motivo(self):
        self.checks(f"bateria\tpass\t1m\t{RUN.format(1, 2)}", f"catraca\tfail\t5s\t{RUN.format(3, 4)}")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr)
        linha = self.um_aviso(r, "pode estar pedindo o rótulo")
        self.assertIn("leia o motivo", linha)
        self.assertIn("rode com --esperar-rotulo", linha)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_outro_check_vermelho_diz_para_nao_pedir_o_rotulo(self):
        self.checks(f"bateria\tfail\t1m\t{RUN.format(1, 2)}", f"catraca\tfail\t5s\t{RUN.format(3, 4)}")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr)
        linha = self.um_aviso(r, "não peça o rótulo agora")
        self.assertIn("bateria", linha)
        self.assertIn("só depois peça o rótulo", linha)
        self.assertNotIn("--esperar-rotulo", linha)
        self.assertEqual(self.avisos(r, "pode estar pedindo o rótulo"), [])
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_o_nome_que_o_script_monta_na_frase_sai_sem_caractere_de_controle(self):
        self.checks("x\x1b[2Jy\tfail\t1m\turl")
        r = self.fechar("p1", "--ref", "melhoria/x")
        linha = self.um_aviso(r, "não peça o rótulo agora")
        self.assertIn("x[2Jy", linha)
        self.assertNotIn("\x1b", linha)

    def test_o_nome_sem_controle_c1_em_utf8_e_o_resto_do_texto_acentuado_fica(self):
        # U+0085 (NEL) e U+009B (CSI de 8 bits) são os C1 que um terminal interpreta; o filtro por byte (C0) não os pega
        self.checks("a\u009b[2Jb\u0085c\u0080d\u009fe-ação- \tfail\t1m\turl")
        r = self.fechar("p1", "--ref", "melhoria/x")
        linha = self.um_aviso(r, "não peça o rótulo agora")
        for c1 in ("\u0080", "\u0085", "\u009b", "\u009f"):
            self.assertNotIn(c1, linha)
        self.assertIn("a[2Jbcde-ação- ", linha)  # o NBSP (U+00A0) e as letras acentuadas ficam
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_com_a_espera_do_rotulo_a_frase_nao_manda_rodar_de_novo_com_ela(self):
        (self.estado / "rotulos").write_text("afrouxa-regra\n")
        self.checks(f"catraca\tcancel\t5s\t{RUN.format(3, 4)}")
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "60")
        self.assertEqual(r.returncode, 1, r.stderr)
        linha = self.um_aviso(r, "só a catraca está vermelha")
        self.assertNotIn("rode com --esperar-rotulo", linha)
        self.assertIn("leia o motivo", linha)

    def test_a_decisao_da_parada_nao_muda_check_vermelho_continua_sem_merge(self):
        self.checks(f"bateria\tfail\t1m\t{RUN.format(1, 2)}")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("parou no passo 4", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))


if __name__ == "__main__":
    unittest.main()
