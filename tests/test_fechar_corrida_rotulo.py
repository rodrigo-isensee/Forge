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

    def rotulo_lido(self, quando):
        """O rótulo em cada leitura dele: n ausente, s presente, f falha (a última se repete). O invólucro responde só `--json labels`; o resto vai ao `gh` falso."""
        falso = self.tmp / "gh"
        falso.rename(self.tmp / "gh-base")
        (self.estado / "rotulo_quando").write_text(quando)
        falso.write_text('#!/usr/bin/env bash\ncase "$*" in *"--json labels"*)\n'
                         '  n=$(( $(cat "$ESTADO/rotulo_lidas" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$ESTADO/rotulo_lidas"\n'
                         '  set -- $(cat "$ESTADO/rotulo_quando"); [ "$n" -le "$#" ] || n=$#; eval "r=\\${$n}"\n'
                         '  case "$r" in f) exit 1 ;; s) echo afrouxa-regra ;; esac; exit 0 ;;\nesac\n'
                         f'exec "{self.tmp / "gh-base"}" "$@"\n')
        falso.chmod(0o755)

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

    def test_so_a_leitura_posterior_falha_e_o_rotulo_presente_depois_segue_velha_e_nunca_mescla(self):  # AB-C4-4 (C4-2)
        # a execução 1 é vista sem o rótulo; só a leitura posterior falha (conta como ausente: a promove a velha); na volta 2 o rótulo está presente
        self.seq(99, [self.cat("fail", 1)])
        self.rotulo_lido("n f f f s")
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("só a execução velha da Catraca (run 1)", r.stderr)
        self.assertTrue(self.sem_merge())

    def test_rotulo_retirado_na_espera_nao_deixa_candidata_descartada_virar_velha(self):  # AB-C4-7 (C4-3)
        # volta 1: rótulo ausente e depois presente (a execução 1 é descartada); volta 2: retirado, a execução 2 passa; volta 3: presente e a 1 reprova
        pendente = "bateria\tpending\t1m\turl"
        self.seq(99, [self.cat("fail", 1)], [pendente, self.cat("pass", 2)], [pendente, self.cat("fail", 1)])
        self.rotulo_lido("n s n n s")
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("a Catraca do rótulo reprovou (run 1)", r.stderr)
        self.assertNotIn("só a execução velha", r.stderr)
        self.assertTrue(self.sem_merge())

    def test_a_leitura_nova_so_le(self):  # C4-5
        texto = base.SCRIPT.read_text()
        for escreve in ("run rerun", "workflow run", "-X POST", "--method"):
            self.assertNotIn(escreve, texto)


if __name__ == "__main__":
    unittest.main()
