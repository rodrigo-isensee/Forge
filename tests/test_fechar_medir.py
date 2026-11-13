"""FECHAR-MEDIR-DO-LOG (E1.11): o `--medir` de `bin/forge-fechar` lê a linha ORCAMENTO-TEMPO do log do CI, não texto livre.

Fonte: o número da execução (`gh run view <n> --log`, pelo dublê) ou o log salvo num arquivo. A linha vale só no formato
`FORMATO_DO_ORCAMENTO` de `tests/test_hooks.py`; ausente ou fora dele, o script para antes do passo 1, com o quê, o porquê e
como destravar. Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos), sem rede.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

LINHA = "ORCAMENTO-TEMPO teste=tests.test_hooks.Hooks.t medido=1.23s limite=3s medida=cpu forma=um por linha"
OUTRA = "ORCAMENTO-TEMPO teste=tests.test_hooks.Hooks.u medido=0.50s limite=2.5s medida=parede forma=x"
# Como o `gh run view --log` devolve: job, passo e hora antes do texto; a primeira traz o `unittest -v` na mesma linha.
LOG_GH = (f"bateria\tTestes\t2026-11-11T00:00:01.0000000Z test_t (tests.test_hooks.Hooks.t) ... {LINHA}\n"
          "bateria\tTestes\t2026-11-11T00:00:02.0000000Z ok\n"
          f"bateria\tTestes\t2026-11-11T00:00:03.0000000Z {OUTRA}\r\n")
# Dublê do `gh run view`: confere a forma exata (só leitura, `--log`) e devolve $ESTADO/log_run; o resto vai ao `gh` falso de sempre.
GH_RUN = r'''#!/usr/bin/env bash
if [ "$1 $2" = "run view" ]; then
  echo "gh $*" >> "$REGISTRO"
  [ "$#" = 4 ] && [ "$4" = --log ] && [[ "$3" =~ ^[0-9]+$ ]] || exit 64
  [ -f "$ESTADO/log_run" ] || { echo "HTTP 404" >&2; exit 1; }
  cat "$ESTADO/log_run"; exit 0
fi
exec "$GH_BASE" "$@"
'''


class FecharMedir(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas

    def setUp(self):
        base.Fechar.setUp(self)
        gh = self.tmp / "gh-run"
        gh.write_text(GH_RUN, encoding="utf-8")
        gh.chmod(0o755)
        self.env.update(GH_BASE=self.env["FORGE_GH"], FORGE_GH=str(gh))

    def parada_antes_do_passo_1(self, r, *trechos):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        for trecho in trechos:
            self.assertIn(trecho, r.stderr)
        self.assertFalse([c for c in self.chamadas() if not c.startswith("gh run view")])  # nem forge-check, nem PR

    def corpo_do_pr(self):
        texto = self.registro.read_text()
        self.assertIn("gh pr create", texto)
        return texto[texto.index("## Como medir"):texto.index("## Checklist")]

    def test_numero_da_execucao_le_o_log_do_ci_e_vai_ao_corpo(self):
        (self.estado / "log_run").write_text(LOG_GH)
        r = self.fechar("p1", "--ref", "melhoria/x", "--medir", "4242")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("gh run view 4242 --log", self.chamadas())
        self.assertEqual(self.corpo_do_pr(), f"## Como medir\n{LINHA}\n{OUTRA}\n\n")
        self.assertIn(f"medida: {LINHA}\nmedida: {OUTRA}\n", r.stdout)

    def test_arquivo_do_log_vale_sem_chamar_o_gh(self):
        arquivo = self.tmp / "ci.log"
        arquivo.write_text(f"{LINHA}\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--medir", str(arquivo))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh run")])
        self.assertEqual(self.corpo_do_pr(), f"## Como medir\n{LINHA}\n\n")

    def test_sem_medir_o_corpo_segue_com_o_texto_padrao(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.corpo_do_pr(), "## Como medir\nVer a seção de medição do pedido p1.\n\n")
        self.assertNotIn("medida:", r.stdout)

    def test_linha_ausente_para_antes_do_passo_1(self):
        (self.estado / "log_run").write_text("bateria\tTestes\t2026-11-11T00:00:01Z Ran 10 tests\nOK\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--medir", "4242")
        self.parada_antes_do_passo_1(r, "não tem linha ORCAMENTO-TEMPO", "sem ela não há medida", "gh run list --branch melhoria/x")

    def test_linha_fora_do_formato_para_antes_do_passo_1(self):
        for ruim in ("ORCAMENTO-TEMPO teste=t medido=nan limite=3s medida=cpu forma=x",
                     "ORCAMENTO-TEMPO teste=t medido=1.2s limite=3s medida=cpu forma=x",
                     "ORCAMENTO-TEMPO teste=t medido=1.23s limite=3s medida=relogio forma=x",
                     "ORCAMENTO-TEMPO teste=t medido=1.23s limite=3s medida=cpu forma="):
            with self.subTest(ruim=ruim):
                self.registro.write_text("")
                (self.estado / "log_run").write_text(f"{LINHA}\n{ruim}\n")
                r = self.fechar("p1", "--ref", "melhoria/x", "--medir", "4242")
                self.parada_antes_do_passo_1(r, "fora do formato", ruim, "corrija quem a imprime")

    def test_texto_livre_e_recusado_com_o_motivo(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--medir", "tempo do teste caiu")
        self.parada_antes_do_passo_1(r, "não é número de execução do CI nem arquivo legível", "não texto livre")
        self.assertEqual(self.chamadas(), [])

    def test_leitura_do_log_que_falha_para_antes_do_passo_1(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--medir", "4242")  # sem $ESTADO/log_run: o dublê falha como o 404
        self.parada_antes_do_passo_1(r, "não consegui ler o log da execução 4242")
        self.assertEqual(self.chamadas().count("gh run view 4242 --log"), 3)  # leitura: repete até 3 vezes

    def test_dry_run_nao_chama_o_gh(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--medir", "4242", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.chamadas(), [])
        self.assertIn("medida: (lida no passo real:", r.stdout)


if __name__ == "__main__":
    unittest.main()
