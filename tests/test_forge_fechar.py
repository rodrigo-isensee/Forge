"""E3.45 (v0474): o passo 4 do `bin/forge-fechar` soma aos pares de CHECKS_EXIGIDOS os checks que o ruleset ou a proteção da develop exigem.

Reaproveita o ambiente de `test_fechar_checks_exigidos` (o `gh` falso com a sequência de leituras dos checks). O `gh api` falso devolve a
saída já filtrada pelo `--jq` (sem rede, R-CUSTO): `api_regras` e `api_protecao` no estado, uma linha por contexto; sem o arquivo, sai com 1,
como o 404 da branch sem regra.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar_checks_exigidos as exig  # noqa: E402

API = '''if [ "$1" = api ]; then  # a chamada já foi registrada no começo do gh falso
  [ "$3" = --jq ] || exit 64
  case "$2" in
    "repos/{owner}/{repo}/rules/branches/develop") f=api_regras ;;
    "repos/{owner}/{repo}/branches/develop/protection/required_status_checks") f=api_protecao ;;
    *) exit 64 ;;
  esac
  [ -f "$ESTADO/$f" ] || { echo '{"message":"Not Found"}'; exit 1; }
  cat "$ESTADO/$f"; exit 0
fi
'''
CASO = 'case "$1 $2" in\n'


class FecharExigidosDoDestino(unittest.TestCase):
    E = exig.FecharChecksExigidos
    tearDown, git, fechar, chamadas, leituras, para = E.tearDown, E.git, E.fechar, E.chamadas, E.leituras, E.para
    leituras_de_checks, sem_merge = E.leituras_de_checks, E.sem_merge

    def setUp(self):
        self.E.setUp(self)
        gh = self.tmp / "gh"
        texto = gh.read_text(encoding="utf-8")
        self.assertEqual(texto.count(CASO), 1)
        gh.write_text(texto.replace(CASO, API + CASO, 1), encoding="utf-8")

    def test_exigido_do_ruleset_ausente_para(self):
        (self.estado / "api_regras").write_text("lint\n")
        self.para(exig.OK, "lint", "ausente após 0s", "--espera", "0")

    def test_exigido_da_protecao_em_skipping_para(self):
        (self.estado / "api_protecao").write_text("lint\n")
        self.para([*exig.OK, "lint\tskipping\t0\turl"], "lint", "skipping")

    def test_exigido_do_ruleset_de_qualquer_workflow_em_pass_mescla(self):
        (self.estado / "api_regras").write_text("lint\n")
        self.leituras([*exig.OK, "lint\tpass\t1m\turl\tQualquer"])
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("exigidos em pass: CI/bateria CI/bateria (python 3.14) Catraca/catraca */lint)", r.stdout)
        chamadas = [c for c in self.chamadas() if c.startswith("gh api")]
        self.assertIn("gh api repos/{owner}/{repo}/rules/branches/develop --jq .[] | select(.type == \"required_status_checks\") | "
                      ".parameters.required_status_checks[].context", chamadas)

    def test_sem_regra_legivel_os_pares_continuam(self):  # o fallback: a leitura que falha não tira nenhum par
        self.para(["bateria\tskipping\t0\turl", *exig.OK[1:]], "bateria", "skipping")


if __name__ == "__main__":
    unittest.main()
