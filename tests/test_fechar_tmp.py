"""FECHAR-B-REC-REVIEW, item 1: os subtestes que chamam o preparo de `Fechar` de novo não deixam pastas `fechar-*` no TMPDIR.

Roda os dois testes de laço num processo filho com TMPDIR numa pasta própria e vazia, e só lê essa pasta.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
LACOS = (
    "test_fechar_pr_numero.PrPorNumero.test_saida_do_create_sem_numero_para_com_a_mensagem_do_pr_criado",
    "test_fechar_vars_vazias.VariaveisVazias.test_tmp2b_herdado_do_ambiente_nao_e_apagado_pelo_fim",
)


class SubtestesSemLixo(unittest.TestCase):
    def test_laco_com_preparo_repetido_nao_deixa_pasta_fechar_no_tmpdir(self):
        pasta = Path(tempfile.mkdtemp(prefix="fechar-tmp-"))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(pasta)])
        for teste in LACOS:
            with self.subTest(teste=teste):
                env = dict(os.environ, TMPDIR=str(pasta))
                r = subprocess.run([sys.executable, "-m", "unittest", teste], cwd=TESTES, env=env,
                                   capture_output=True, text=True, timeout=300)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(sorted(p.name for p in pasta.glob("fechar-*")), [])


if __name__ == "__main__":
    unittest.main()
