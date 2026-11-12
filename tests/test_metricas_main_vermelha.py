"""0.45.6 E5.1: `forge-check metricas` mostra, por versão, quantas vezes a main ficou vermelha e quantos merges tiveram check
vermelho (fonte: `gh run list` e `gh pr list`, aqui um `gh` falso que devolve a saída gravada em tests/fixtures). Dado ausente
sai `nao-medido`, nunca zero."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FIXTURE = RAIZ / "tests" / "fixtures" / "metricas-main-vermelha"
GH_FALSO = """#!/bin/sh
case "$1 $2" in
  "run list") cat "$FIXTURE/run-list.json" ;;
  "pr list") cat "$FIXTURE/pr-list.json" ;;
  *) exit 1 ;;
esac
"""
SEM_DADO = "main_vermelha=nao-medido merge_com_check_vermelho=nao-medido origem=nao-medido"


class MainVermelha(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def linhas(self, gh_corpo=GH_FALSO, gh=True):
        pasta = Path(self.tmp.name)
        (pasta / "gh").write_text(gh_corpo)
        (pasta / "gh").chmod(0o755)
        env = sem_manutencao()
        env["PATH"] = f"{pasta}:/usr/bin:/bin"
        env["FIXTURE"] = str(FIXTURE)
        r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), "--raiz", str(FIXTURE), "metricas",
                            "--fuso=-03:00", "--agora", "2026-11-03T00:00", *(["--gh"] if gh else [])],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return [x for x in r.stdout.splitlines() if x.startswith("metricas: ci ")]

    def test_conta_main_vermelha_e_merge_com_check_vermelho_por_versao(self):
        self.assertEqual(self.linhas(), [
            "metricas: ci versao - main_vermelha=1 merge_com_check_vermelho=1 origem=medido",
            "metricas: ci versao 0.45.4 main_vermelha=0 merge_com_check_vermelho=0 origem=medido",
            "metricas: ci versao 0.45.5 main_vermelha=2 merge_com_check_vermelho=2 origem=medido",
            "metricas: ci versao 0.46.0 " + SEM_DADO,
        ])

    def test_sem_a_opcao_gh_nada_vira_zero(self):
        self.assertEqual(self.linhas(gh=False), ["metricas: ci versao 0.45.5 " + SEM_DADO, "metricas: ci versao 0.46.0 " + SEM_DADO])

    def test_gh_que_falha_nao_vira_zero(self):
        self.assertEqual(self.linhas("#!/bin/sh\nexit 1\n"), ["metricas: ci versao 0.45.5 " + SEM_DADO, "metricas: ci versao 0.46.0 " + SEM_DADO])

    def test_resposta_de_forma_errada_nao_vira_zero(self):
        self.assertEqual(self.linhas("#!/bin/sh\necho '{\"erro\":1}'\n"),
                         ["metricas: ci versao 0.45.5 " + SEM_DADO, "metricas: ci versao 0.46.0 " + SEM_DADO])

    def test_so_um_lado_medido_deixa_o_outro_nao_medido(self):
        corpo = GH_FALSO.replace('"pr list") cat "$FIXTURE/pr-list.json" ;;', '"pr list") exit 1 ;;')
        self.assertIn("metricas: ci versao 0.45.5 main_vermelha=2 merge_com_check_vermelho=nao-medido origem=medido", self.linhas(corpo))


if __name__ == "__main__":
    unittest.main()
