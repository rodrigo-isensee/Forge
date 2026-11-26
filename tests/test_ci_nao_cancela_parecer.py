"""CI-NAO-CANCELA-ENVIO-SO-DE-PARECER (v0481 E22.1): o job `obsoletas` do obsoletas.yml cancela os runs anteriores do PR, menos quando o
envio novo so traz docs/reviews, docs/qa ou docs/security. O script do job roda de verdade com um `gh` falso no PATH."""
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

WF = Path(__file__).resolve().parent.parent / ".github" / "workflows"
CI = (WF / "ci.yml").read_text(encoding="utf-8")
OBS = (WF / "obsoletas.yml").read_text(encoding="utf-8")
GH_FALSO = """#!/bin/sh
case "$1" in
  api) case "$*" in
         *compare*) printf '%s' "$FALSO_ARQUIVOS"; [ "${FALSO_API_FALHA:-0}" = 0 ] ;;
         *) printf '%s\\n' "5 o/r old" "6 o/r old" "99 o/r old" "10 o/r old" "7 fork/r old" "4 o/r def" "8 o/r def" ;;
       esac ;;
  run) case "$2" in
         cancel) for a; do u=$a; done; echo "$u" >> "$FALSO_CANCELADOS" ;;
       esac ;;
esac
"""


def bloco_obsoletas():
    return re.search(r"(?ms)^  obsoletas:\n(.*)\Z", OBS).group(1)


def script():
    return re.search(r"(?ms)^        run: \|\n(.*)\Z", bloco_obsoletas()).group(1).replace("\n          ", "\n").strip()


class ObsoletasEstatico(unittest.TestCase):
    def test_concorrencia_so_cancela_fora_de_pr_e_o_job_tem_permissao_minima(self):
        self.assertIn("cancel-in-progress: ${{ github.event_name != 'pull_request' }}", CI)
        self.assertIn("format('-{0}', github.run_id)", CI)
        b = bloco_obsoletas()
        self.assertIn("      actions: write", b)
        self.assertIn("      contents: read", b)
        self.assertIn("timeout-minutes:", b)
        self.assertNotIn("${{", script())  # entrada nao confiavel so por env
        self.assertNotIn("continue-on-error", b)
        self.assertIn("    if: github.event.pull_request.head.repo.full_name == github.repository\n", b)  # fork nao tem token de escrita
        self.assertNotIn("write", re.sub(r"(?m)^\s*#.*$", "", CI).replace("writes", ""))  # o ci.yml segue sem escrita
        self.assertEqual(re.sub(r"(?m)^\s*#.*$", "", OBS).count("actions: write"), 1)


class ObsoletasRoda(unittest.TestCase):
    def rodar(self, arquivos, acao="synchronize", before="abc", api_falha=False):
        with tempfile.TemporaryDirectory() as d:
            gh = Path(d, "gh")
            gh.write_text(GH_FALSO, encoding="utf-8")
            gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
            cancelados = Path(d, "cancelados")
            env = {"PATH": f"{d}:{os.environ['PATH']}", "GH_TOKEN": "x", "REPO": "o/r", "HEAD_REF": "melhoria/x",
                   "HEAD_SHA": "def", "BEFORE": before, "ACAO": acao, "RUN_ID": "10", "FALSO_ARQUIVOS": arquivos,
                   "FALSO_CANCELADOS": str(cancelados), "FALSO_API_FALHA": "1" if api_falha else "0"}
            subprocess.run(["bash", "-c", script()], env=env, check=True, capture_output=True)
            return cancelados.read_text().split() if cancelados.exists() else []

    def test_envio_so_de_parecer_nao_cancela_nada(self):
        self.assertEqual(self.rodar("docs/reviews/a.md\ndocs/qa/b.md\ndocs/security/c.md\n"), [])

    def test_envio_com_codigo_cancela_so_os_runs_mais_antigos(self):
        self.assertEqual(self.rodar("docs/reviews/a.md\ntests/x.py\n"), ["5", "6"])

    def test_nunca_cancela_o_proprio_run_nem_run_de_outro_repositorio(self):
        # o gh falso lista o RUN_ID (10) e um run do fork (7, mais antigo que o RUN_ID): nenhum dos dois cai
        self.assertEqual(self.rodar("tests/x.py\n"), ["5", "6"])

    def test_nunca_cancela_o_ci_do_proprio_head_mesmo_com_id_menor_que_o_run_id(self):
        # o CI do push nasce antes do Obsoletas: ids 4 e 8 (< RUN_ID 10) com o head_sha atual (def) seguem
        cancelados = self.rodar("tests/x.py\n")
        self.assertNotIn("4", cancelados)
        self.assertNotIn("8", cancelados)

    def test_outros_docs_e_o_devops_nao_contam_como_parecer(self):
        self.assertEqual(self.rodar("docs/devops/a.md\n"), ["5", "6"])
        self.assertEqual(self.rodar("docs/reviews-x/a.md\n"), ["5", "6"])

    def test_falha_fechada_cancela_quando_nao_prova(self):
        self.assertEqual(self.rodar("docs/reviews/a.md\n", before=""), ["5", "6"])  # sem sha anterior
        self.assertEqual(self.rodar("docs/reviews/a.md\n", acao="opened"), ["5", "6"])
        self.assertEqual(self.rodar("", ), ["5", "6"])  # diff vazio nao prova
        self.assertEqual(self.rodar("docs/reviews/a.md\n", api_falha=True), ["5", "6"])  # compare falhou
        quase = "".join(f"docs/reviews/{i}.md\n" for i in range(299))
        self.assertEqual(self.rodar(quase), [])  # 299 arquivos de parecer ainda provam
        grande = "".join(f"docs/reviews/{i}.md\n" for i in range(300))
        self.assertEqual(self.rodar(grande), ["5", "6"])  # compare corta em 300 arquivos


if __name__ == "__main__":
    unittest.main()
