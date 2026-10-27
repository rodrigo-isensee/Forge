"""N-FECHAR-b, B2: a espera do rótulo vale para a execução da Catraca vista antes dele, não para a nova.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele. O `gh` falso
ganha aqui, só para estes testes, a sequência de leituras dos checks (`checks_seq`: blocos separados por "---"; cada leitura consome o
próximo e o último se repete, como execuções que mudam de estado).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

RUN = "https://github.com/o/r/actions/runs/{}/job/{}"
LEITURA = '    cat "$ESTADO/checks"; exit 0 ;;\n'
SEQUENCIA = '''    if [ -f "$ESTADO/checks_seq" ]; then
      n="$(( $(cat "$ESTADO/checks_n" 2>/dev/null || echo 0) + 1 ))"; echo "$n" > "$ESTADO/checks_n"
      awk -v n="$n" 'BEGIN {b = 1} /^---$/ {b++; next} {t[b] = t[b] $0 "\\n"; if (b > m) m = b} END {printf "%s", t[(n > m) ? m : n]}' "$ESTADO/checks_seq"
      exit 0
    fi
'''


class FecharEsperaCatraca(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas

    def setUp(self):
        base.Fechar.setUp(self)
        gh = self.tmp / "gh"
        texto = gh.read_text(encoding="utf-8")
        self.assertEqual(texto.count(LEITURA), 1)
        gh.write_text(texto.replace(LEITURA, SEQUENCIA + LEITURA), encoding="utf-8")

    def seq(self, *blocos):
        """Cada bloco é uma leitura dos checks (a última se repete); o rótulo aparece na 2ª leitura."""
        (self.estado / "checks_seq").write_text("---\n".join("".join(f"{l}\n" for l in b) for b in blocos))
        (self.estado / "rotulo_na_leitura").write_text("2\n")
        (self.estado / "texto").write_text(base.Fechar.ITEM_MARCADO)

    def leituras_de_checks(self):
        return sum(1 for c in self.chamadas() if c.startswith("gh pr checks"))

    def espera_rotulo(self, *extra, **env):
        return self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "600", *extra, **env)

    def cat(self, estado, run, job=9):
        return f"catraca\t{estado}\t5s\t{RUN.format(run, job)}"

    def sem_merge(self):
        return not any("pr merge" in c for c in self.chamadas())

    def test_catraca_nova_reprovada_para_na_hora_sem_esperar_a_tolerancia(self):
        self.seq([self.cat("fail", 1)], [self.cat("fail", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("a Catraca do rótulo reprovou (run 2)", r.stderr)
        self.assertEqual(self.leituras_de_checks(), 2)  # não espera 10 leituras
        self.assertTrue(self.sem_merge())

    def test_catraca_velha_cancelada_espera_a_nova_e_mescla_preso_ao_head(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "head").write_text(sha)
        self.seq(["bateria\tpass\t1m\turl", self.cat("fail", 1)], ["bateria\tpass\t1m\turl", self.cat("cancel", 1)],
                 ["bateria\tpass\t1m\turl", self.cat("pass", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.leituras_de_checks(), 3)
        self.assertTrue(any(f"--match-head-commit {sha}" in c for c in self.chamadas() if "pr merge" in c))

    def test_catraca_nova_cancelada_por_terceiro_para(self):
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.leituras_de_checks(), 2)
        self.assertTrue(self.sem_merge())

    def test_cancelada_com_link_fora_do_padrao_depois_do_rotulo_para_na_hora(self):
        self.seq([self.cat("fail", 1)], ["catraca\tcancel\t5s\turl"])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.leituras_de_checks(), 2)

    def test_velha_e_nova_na_mesma_leitura_so_passa_quando_a_nova_passa(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "head").write_text(sha)
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1), self.cat("pending", 2)],
                 [self.cat("cancel", 1), self.cat("pass", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.leituras_de_checks(), 3)

    def test_velha_e_nova_na_mesma_leitura_com_a_nova_vermelha_para(self):
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1), self.cat("fail", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("reprovou (run 2)", r.stderr)
        self.assertTrue(self.sem_merge())

    # ---- A2 do review: só `pass` libera o merge; a execução nova em `skipping` (ou outra conclusão) não ----
    def test_a2_velha_cancelada_e_nova_em_skipping_nao_libera_o_merge(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "head").write_text(sha)
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1), self.cat("skipping", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("run 2", r.stderr)
        self.assertIn("só pass libera o merge", r.stderr)
        self.assertEqual(self.leituras_de_checks(), 2)  # para na hora, sem esperar o prazo
        self.assertTrue(self.sem_merge())

    def test_a2_velha_vermelha_e_nova_em_skipping_nao_libera_o_merge(self):
        self.seq([self.cat("fail", 1)], [self.cat("fail", 1), self.cat("skipping", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertTrue(self.sem_merge())

    def test_a2_nova_com_conclusao_desconhecida_nao_libera_o_merge(self):
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1), self.cat("neutral", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertTrue(self.sem_merge())

    def test_a2_nova_em_skipping_depois_de_pendente_tambem_para(self):
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1), self.cat("pending", 2)],
                 [self.cat("cancel", 1), self.cat("skipping", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertEqual(self.leituras_de_checks(), 3)
        self.assertTrue(self.sem_merge())

    def test_velha_que_nunca_e_substituida_para_pelo_prazo_com_a_mensagem_do_rotulo(self):
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1)])
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "2", FORGE_FECHAR_INTERVALO="1")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("rótulo", r.stderr.splitlines()[-1])
        self.assertIn("run 1", r.stderr.splitlines()[-1])
        self.assertTrue(self.sem_merge())

    def test_com_a_nova_passando_outro_check_vermelho_para(self):
        self.seq([self.cat("fail", 1)], ["bateria\tfail\t1m\turl", self.cat("cancel", 1), self.cat("pass", 2)])
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(self.sem_merge())

    def test_rotulo_ja_aplicado_na_primeira_leitura_cancelada_para_e_fail_mantem_a_rede(self):
        (self.estado / "rotulos").write_text("afrouxa-regra\n")
        (self.estado / "checks").write_text(self.cat("cancel", 1) + "\n")
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.leituras_de_checks(), 1)
        (self.estado / "checks").write_text(self.cat("fail", 1) + "\n")
        r = self.espera_rotulo()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertGreater(self.leituras_de_checks(), 10)  # a rede de 10 leituras segue valendo

    # ---- LOTE-FECHAR2 (volta 6): só a execução da catraca com link válido conta como "vista antes do rótulo" ou "nova" ----
    def test_a2_check_de_outro_nome_com_run_novo_nao_faz_a_catraca_velha_virar_skipping(self):
        # a bateria com run 3 (pass) não é a catraca: sem o `continue`, ela contaria como execução nova e liberaria a velha (cancel, run 1)
        self.seq([self.cat("fail", 1)], [f"bateria\tpass\t1m\t{RUN.format(3, 3)}", self.cat("cancel", 1)])
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "2", FORGE_FECHAR_INTERVALO="1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("run 1", r.stderr.splitlines()[-1])
        self.assertTrue(self.sem_merge())

    def test_a2_catraca_com_link_fora_do_padrao_antes_do_rotulo_nao_entra_em_run_antes(self):
        # run `?` não é execução vista: sem o `continue`, o " ? " em run_antes faria a vermelha nova (run 3) parar na hora em vez de manter a rede
        self.seq(["catraca\tfail\t5s\turl"], [self.cat("fail", 3)])
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "4", FORGE_FECHAR_INTERVALO="1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertNotIn("reprovou (run 3)", r.stderr)
        self.assertGreater(self.leituras_de_checks(), 2)
        self.assertTrue(self.sem_merge())

    def test_o_script_nunca_reexecuta_a_catraca(self):
        self.seq([self.cat("fail", 1)], [self.cat("cancel", 1)], [self.cat("pass", 2)])
        self.espera_rotulo()
        self.assertFalse(any(("rerun" in c) or ("workflow run" in c) or ("-X POST" in c) for c in self.chamadas()))

    def test_o_codigo_do_script_nao_tem_reexecucao_nem_chamada_que_muda_estado(self):
        codigo = "\n".join(l for l in base.SCRIPT.read_text().splitlines() if not l.lstrip().startswith("#"))
        for proibido in ("run rerun", "workflow run", "-X POST", "--method"):
            self.assertNotIn(proibido, codigo)


if __name__ == "__main__":
    unittest.main()
