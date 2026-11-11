"""0.45.6 E1.1 (AV4(c)): a fatia por portão do `forge-check metricas` (review, QA, segurança, CI, revalidação): tempo e voltas por
versão, `medido`, `estimado` ou `nao-medido`, nunca zero por dado ausente; as demais linhas seguem como estavam."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FIXTURE = RAIZ / "tests" / "fixtures" / "metricas-portoes"


def metricas(pedido, raiz, *extra):
    r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), "--raiz", str(raiz), "metricas", *(["--pedido", pedido] if pedido else []),
                        "--fuso=-03:00", "--agora", "2026-11-03T00:00", *extra], capture_output=True, text=True, env=sem_manutencao())
    return r.returncode, [l for l in r.stdout.splitlines() if l.startswith("metricas: fatia ")], r.stdout


class FatiaPorPortao(unittest.TestCase):
    def test_cada_portao_tem_minutos_voltas_e_origem(self):
        """Dois pedidos da mesma versão (o segundo sem dado de portão): o que falta num não vira zero na soma."""
        rc, linhas, _ = metricas(None, FIXTURE)
        self.assertEqual(rc, 0)
        self.assertEqual(linhas, [
            "metricas: fatia versao 9.9.9 portao review minutos=50 voltas=1 tempo=medido",
            "metricas: fatia versao 9.9.9 portao qa minutos=20 voltas=0 tempo=estimado",
            "metricas: fatia versao 9.9.9 portao seguranca minutos=60 voltas=0 tempo=medido",
            "metricas: fatia versao 9.9.9 portao ci minutos=nao-medido voltas=0 tempo=nao-medido",
            "metricas: fatia versao 9.9.9 portao revalidacao minutos=20 voltas=2 tempo=medido",
        ])

    def test_sem_dado_nao_vira_zero(self):
        rc, linhas, _ = metricas("vvazio", FIXTURE / "semdado")
        self.assertEqual(rc, 0)
        self.assertEqual(len(linhas), 5)
        for linha in linhas:
            self.assertTrue(linha.endswith("minutos=nao-medido voltas=nao-medido tempo=nao-medido"), linha)

    def test_demais_linhas_seguem(self):
        _, _, saida = metricas("vfix", FIXTURE)
        self.assertIn("metricas: pedido vfix ", saida)
        self.assertIn("metricas: fontes: ", saida)
        self.assertIn("fatia_portao=", saida)

    def test_dois_pedidos_com_dado_somam_no_portao(self):
        _, linhas, _ = metricas(None, FIXTURE / "soma")
        self.assertIn("metricas: fatia versao 7.7.7 portao review minutos=50 voltas=0 tempo=medido", linhas)

    def test_json_traz_a_fatia_por_versao(self):
        fatias = json.loads(metricas("vfix", FIXTURE, "--json")[2]).get("fatia_por_portao") or {}
        self.assertIn("9.9.9", fatias)
        fatia = fatias["9.9.9"]
        self.assertEqual(set(fatia), {"review", "qa", "seguranca", "ci", "revalidacao"})
        self.assertIsNone(fatia["ci"]["tempo"])


if __name__ == "__main__":
    unittest.main()
