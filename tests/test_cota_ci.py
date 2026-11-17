"""`bin/forge-cota-ci` (E3.42, R-CUSTO): aviso de minutos do Actions acima de 80% da franquia; gh falso, sem rede."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gh_falso import com_gh_falso  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-cota-ci"


def rodar(resposta=None, *args, rc_gh=0, erro="HTTP 403: Resource not accessible"):
    """Roda a ferramenta com um `gh` falso que devolve `resposta` (JSON) ou falha com `erro`."""
    if resposta is None:
        script = f"echo '{erro}' >&2\nexit 1\n"
    else:
        script = f"echo '{json.dumps(resposta)}'\nexit {rc_gh}\n"
    env = com_gh_falso(script=script)
    env.pop("FORGE_COTA_CI_ENDPOINT", None)
    r = subprocess.run([sys.executable, "-I", str(FERRAMENTA), "--dono", "dono-x", *args], env=env, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


class CotaCi(unittest.TestCase):
    def test_abaixo_do_limite_diz_ok(self):
        rc, out, _ = rodar({"total_minutes_used": 1000, "included_minutes": 2000})
        self.assertEqual(rc, 0)
        self.assertIn("ok minutos do Actions no mês: 1000 de 2000 (50.0%)", out)

    def test_acima_de_80_avisa_com_rc_1(self):
        rc, out, _ = rodar({"total_minutes_used": 1700, "included_minutes": 2000})
        self.assertEqual(rc, 1)
        self.assertIn("AVISO", out)
        self.assertIn("85.0%", out)

    def test_exatamente_80_nao_avisa(self):
        rc, out, _ = rodar({"total_minutes_used": 1600, "included_minutes": 2000})
        self.assertEqual(rc, 0)
        self.assertNotIn("AVISO", out)

    def test_limite_configuravel(self):
        rc, _, _ = rodar({"total_minutes_used": 1000, "included_minutes": 2000}, "--limite", "40")
        self.assertEqual(rc, 1)

    def test_sem_permissao_diz_nao_verificavel_e_o_comando(self):
        rc, out, _ = rodar(None)
        self.assertEqual(rc, 0)
        self.assertIn("não verificável", out)
        self.assertIn("gh api /users/dono-x/settings/billing/actions", out)
        self.assertIn("HTTP 403", out)

    def test_resposta_sem_os_campos_nao_verifica(self):
        rc, out, _ = rodar({"outra": 1})
        self.assertEqual(rc, 0)
        self.assertIn("não verificável", out)

    def test_franquia_zero_nao_divide(self):
        rc, out, _ = rodar({"total_minutes_used": 10, "included_minutes": 0})
        self.assertEqual(rc, 0)
        self.assertIn("não verificável", out)

    def test_booleano_nao_vale_como_numero(self):
        rc, out, _ = rodar({"total_minutes_used": True, "included_minutes": 2})
        self.assertEqual(rc, 0)
        self.assertIn("não verificável", out)

    def test_limite_invalido_sai_2(self):
        rc, _, err = rodar({"total_minutes_used": 1, "included_minutes": 2}, "--limite", "x")
        self.assertEqual(rc, 2)
        self.assertIn("--limite", err)

    def test_opcao_desconhecida_sai_2(self):
        rc, _, _ = rodar({"total_minutes_used": 1, "included_minutes": 2}, "--foo")
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
