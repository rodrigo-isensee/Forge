"""`bin/forge-cota-ci` (E3.42, R-CUSTO): aviso de minutos do Actions acima de 80% da franquia; gh falso, sem rede."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from gh_falso import com_gh_falso  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-cota-ci"


def rodar(resposta=None, *args, rc_gh=0, erro="HTTP 403: Resource not accessible", script=None):
    """Roda a ferramenta com um `gh` falso que devolve `resposta` (JSON) ou falha com `erro`; `script` troca o gh inteiro."""
    if script is None:
        if resposta is None:
            script = f"echo '{erro}' >&2\nexit 1\n"
        else:
            script = f"echo '{json.dumps(resposta)}'\nexit {rc_gh}\n"
    env = com_gh_falso(script=script)
    env.pop("FORGE_COTA_CI_ENDPOINT", None)
    r = subprocess.run([sys.executable, "-I", str(FERRAMENTA), "--dono", "dono-x", *args], env=env, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def rodar_em(script, *args, origin=None, endpoint=None):
    """Roda num repositório descartável com `origin` dado (sem `--dono`, salvo em `args`); devolve (rc, saída, chamadas do gh)."""
    with tempfile.TemporaryDirectory() as d:
        log = Path(d) / "chamadas"
        env = com_gh_falso(script=f'echo "$*" >> {log}\n' + script)
        env.pop("FORGE_COTA_CI_ENDPOINT", None)
        if endpoint:
            env["FORGE_COTA_CI_ENDPOINT"] = endpoint
        subprocess.run(["git", "init", "-q", d], check=True, env=sem_manutencao())
        if origin:
            subprocess.run(["git", "-C", d, "remote", "add", "origin", origin], check=True, env=sem_manutencao())
        r = subprocess.run([sys.executable, "-I", str(FERRAMENTA), *args], env=env, cwd=d, capture_output=True, text=True)
        chamadas = log.read_text().splitlines() if log.exists() else []
        return r.returncode, r.stdout, chamadas


FALHA_403_E_404 = (
    'case "$2" in\n  /users/*) echo "HTTP 403: precisa do escopo user" >&2 ;;\n  *) echo "HTTP 404: Not Found" >&2 ;;\nesac\nexit 1\n'
)
OK_50 = 'echo \'{"total_minutes_used": 1, "included_minutes": 2}\'\n'


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

    def test_so_um_dos_campos_nao_verifica(self):
        for resposta in ({"total_minutes_used": 5}, {"included_minutes": 5}):
            rc, out, _ = rodar(resposta)
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
        rc, _, err = rodar({"total_minutes_used": 1, "included_minutes": 2}, "--foo")
        self.assertEqual(rc, 2)
        self.assertIn("uso:", err)

    def test_resposta_que_nao_e_objeto_nao_verifica(self):
        rc, out, _ = rodar(script="echo '[1, 2]'\n")
        self.assertEqual(rc, 0)
        self.assertIn("não verificável", out)
        self.assertIn("resposta inesperada", out)

    def test_falha_do_gh_sem_mensagem_diz_sem_resposta(self):
        rc, out, _ = rodar(script="exit 1\n")
        self.assertEqual(rc, 0)
        self.assertIn("(sem resposta | sem resposta)", out)

    def test_opcao_sem_valor_sai_2(self):
        for opcao in ("--dono", "--limite"):
            rc, _, err = rodar(None, opcao)
            self.assertEqual(rc, 2)
            self.assertIn("uso:", err)

    def test_resposta_que_nao_e_json_nao_verifica(self):
        rc, out, _ = rodar(script="echo 'oi'\n")
        self.assertEqual(rc, 0)
        self.assertIn("resposta não é JSON", out)

    def test_dono_desconhecido_sem_origin_pede_o_dono(self):
        rc, out, chamadas = rodar_em(OK_50)
        self.assertEqual(rc, 0)
        self.assertIn("dono do repositório desconhecido", out)
        self.assertIn("--dono", out)
        self.assertEqual(chamadas, [])

    def test_origin_fora_do_github_e_dono_desconhecido(self):
        rc, out, chamadas = rodar_em(OK_50, origin="https://gitlab.com/alguem/repo.git")
        self.assertEqual(rc, 0)
        self.assertIn("dono do repositório desconhecido", out)
        self.assertEqual(chamadas, [])

    def test_origin_do_github_da_o_dono(self):
        for url in ("https://github.com/alguem/repo.git", "git@github.com:alguem/repo.git"):
            rc, out, chamadas = rodar_em(OK_50, origin=url)
            self.assertEqual(rc, 0)
            self.assertIn("ok minutos", out)
            self.assertEqual(chamadas, ["api /users/alguem/settings/billing/actions"])

    def test_usuario_403_e_organizacao_404_mostra_os_dois_motivos(self):
        rc, out, chamadas = rodar_em(FALHA_403_E_404, "--dono", "dono-x")
        self.assertEqual(rc, 0)
        self.assertIn("HTTP 403: precisa do escopo user", out)
        self.assertIn("HTTP 404: Not Found", out)
        self.assertEqual(chamadas, ["api /users/dono-x/settings/billing/actions", "api /orgs/dono-x/settings/billing/actions"])

    def test_organizacao_responde_quando_o_usuario_nao(self):
        script = 'case "$2" in\n  /users/*) echo "HTTP 404" >&2; exit 1 ;;\nesac\n' + OK_50
        rc, out, _ = rodar_em(script, "--dono", "org-x")
        self.assertEqual(rc, 0)
        self.assertIn("ok minutos", out)

    def test_dono_fora_do_formato_de_login_nao_e_impresso_nem_consultado(self):
        for ruim in ("$(id)", "a b", "-x", "a" * 40, "a/b"):
            rc, out, chamadas = rodar_em(OK_50, "--dono", ruim)
            self.assertEqual(rc, 0, ruim)
            self.assertIn("formato de login", out)
            self.assertNotIn(ruim, out)
            self.assertEqual(chamadas, [])

    def test_origin_com_dono_fora_do_formato_nao_e_impresso(self):
        rc, out, chamadas = rodar_em(OK_50, origin="https://github.com/$(id)x/repo")
        self.assertIn("formato de login", out)
        self.assertNotIn("$(id)", out)
        self.assertEqual(chamadas, [])

    def test_dica_manda_para_a_tela_de_cobranca_e_nao_amplia_o_token(self):
        _, out, _ = rodar_em(FALHA_403_E_404, "--dono", "dono-x")
        self.assertIn("Settings > Billing", out)
        self.assertNotIn("auth refresh", out)
        self.assertNotIn("-s user", out)

    def test_a_chamada_e_so_gh_api_com_o_endpoint(self):
        _, _, chamadas = rodar_em(OK_50, "--dono", "dono-x")
        self.assertEqual(chamadas, ["api /users/dono-x/settings/billing/actions"])

    def test_endpoint_trocado_sem_dono_nao_imprime_users_vazio(self):
        _, out, chamadas = rodar_em(FALHA_403_E_404, endpoint="/teste/endpoint")
        self.assertEqual(chamadas, ["api /teste/endpoint"])
        self.assertNotIn("/users//", out)
        self.assertNotIn("/orgs//", out)
        self.assertIn("não verificável", out)

    def test_endpoint_trocado_responde(self):
        rc, out, chamadas = rodar_em(OK_50, endpoint="/teste/endpoint")
        self.assertEqual((rc, chamadas), (0, ["api /teste/endpoint"]))
        self.assertIn("ok minutos", out)


if __name__ == "__main__":
    unittest.main()
