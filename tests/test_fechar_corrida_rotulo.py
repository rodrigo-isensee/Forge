"""FECHAR-B-REC-REVIEW, item 3 (C4, opção B' do modelo de ameaças): a execução da Catraca só vira velha com o rótulo ausente depois de vista.

Uma execução vista antes do rótulo é só candidata; uma leitura do rótulo posterior à leitura dos checks em que ela apareceu decide: rótulo
ausente promove as candidatas a "velhas" (`run_antes`), rótulo presente as descarta. Nunca libera o merge sem a execução nova em `pass`.
Reaproveita o ambiente de `test_fechar_espera_catraca` (`gh` falso com a sequência de leituras dos checks) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
import test_fechar_espera_catraca as espera  # noqa: E402

BATERIA = "bateria\tpass\t1m\turl"


class CorridaDoRotulo(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    setUp = espera.FecharEsperaCatraca.setUp
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    leituras_de_checks = espera.FecharEsperaCatraca.leituras_de_checks
    cat = espera.FecharEsperaCatraca.cat
    sem_merge = espera.FecharEsperaCatraca.sem_merge

    def seq(self, rotulo_na_leitura, *blocos):
        """Blocos de checks como em `FecharEsperaCatraca.seq`; o rótulo aparece a partir da N-ésima leitura dele (as leituras são contadas pelo `gh`)."""
        (self.estado / "checks_seq").write_text("---\n".join("".join(f"{l}\n" for l in b) for b in blocos))
        (self.estado / "rotulo_na_leitura").write_text(f"{rotulo_na_leitura}\n")
        (self.estado / "texto").write_text(base.Fechar.ITEM_MARCADO)

    def espera_rotulo(self, espera_s="3"):
        return self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", espera_s)

    def test_corrida_com_a_nova_reprovando_para_na_hora(self):  # AB-C4-1
        # o dono aplica o rótulo logo depois da leitura dele na volta 2: os checks dessa volta já trazem a execução nova (run 2)
        self.seq(4, [self.cat("fail", 1)], [self.cat("fail", 1), self.cat("fail", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("a Catraca do rótulo reprovou (run 2)", r.stderr)
        self.assertNotIn("só a execução velha", r.stderr)
        self.assertEqual(self.leituras_de_checks(), 3)
        self.assertTrue(self.sem_merge())

    def test_corrida_com_a_nova_passando_mescla_preso_ao_head(self):  # AB-C4-2
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "head").write_text(sha)
        self.seq(4, [self.cat("fail", 1)], [self.cat("fail", 1), self.cat("pending", 2)],
                 [BATERIA, self.cat("cancel", 1), self.cat("pass", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(any(f"--match-head-commit {sha}" in c for c in self.chamadas() if "pr merge" in c))

    def test_descartada_em_fail_sem_velha_nunca_mescla(self):  # AB-C4-6
        # o rótulo aparece na leitura posterior da primeira volta: a execução 2 foi vista na janela de dúvida e é descartada
        self.seq(2, [self.cat("fail", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertNotIn("só a execução velha", r.stderr)
        self.assertTrue(self.sem_merge())

    def test_leitura_posterior_do_rotulo_que_falha_conta_como_ausente_e_nunca_mescla(self):  # AB-C4-4
        (self.estado / "falha_leitura").write_text("")  # toda leitura do rótulo falha (3 tentativas por leitura)
        self.seq(2, [self.cat("fail", 1)])
        r = self.espera_rotulo("2")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("o dono ainda não o aplicou", r.stderr)
        self.assertTrue(self.sem_merge())

    def test_a_leitura_nova_so_le(self):  # C4-5
        texto = base.SCRIPT.read_text()
        for escreve in ("run rerun", "workflow run", "-X POST", "--method"):
            self.assertNotIn(escreve, texto)


if __name__ == "__main__":
    unittest.main()
