"""BATERIA-SHELLCHECK-PREPUSH: o .githooks/pre-push passa no shellcheck da bateria (sem rede, R-CUSTO).

O CI roda `shellcheck` no hook; aqui o mesmo arquivo é conferido local quando o shellcheck existe, e por
leitura estrutural sempre: a forma `A && B || C` em fila_vivas (SC2015) e diretiva sem motivo não voltam.
"""
import re
import shutil
import subprocess
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"


def corpo_da_funcao(texto, nome):
    inicio = texto.index(f"{nome}() {{")
    fim = texto.index("\n}\n", inicio)
    return texto[inicio:fim]


class PrePushShellcheck(unittest.TestCase):
    def test_shellcheck_no_hook(self):
        if shutil.which("shellcheck") is None:
            self.skipTest("AVISO: shellcheck fora do PATH; o CI roda este passo")
        r = subprocess.run(["shellcheck", str(HOOK)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fila_vivas_sem_e_ou_continue(self):
        corpo = corpo_da_funcao(HOOK.read_text(encoding="utf-8"), "fila_vivas")
        self.assertIsNone(re.search(r"&&.*\|\|\s*continue", corpo),
                          "fila_vivas usa A && B || continue (SC2015); use `if ...; then continue; fi`")

    def test_diretiva_shellcheck_disable_tem_motivo(self):
        linhas = HOOK.read_text(encoding="utf-8").splitlines()
        achadas = 0
        for i, linha in enumerate(linhas):
            m = re.match(r"\s*#\s*shellcheck\s+disable=\S+(.*)$", linha)
            if not m:
                continue
            achadas += 1
            acima = linhas[i - 1].strip() if i else ""
            motivo_aqui = len(m.group(1).strip().lstrip("#").strip()) >= 10
            motivo_acima = acima.startswith("#") and "shellcheck" not in acima and len(acima) > 10
            self.assertTrue(motivo_aqui or motivo_acima, f"pre-push:{i + 1}: diretiva sem motivo")
        self.assertGreaterEqual(achadas, 1, "esperava a diretiva SC2317 de parar()")


if __name__ == "__main__":
    unittest.main()
