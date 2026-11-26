"""CI-NAO-CANCELA-ENVIO-SO-DE-PARECER (v0481 E22.1): o job `obsoletas` do ci.yml cancela os runs anteriores do PR, menos quando o
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

CI = (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
GH_FALSO = """#!/bin/sh
case "$1" in
  api) printf '%s' "$FALSO_ARQUIVOS"; [ "${FALSO_API_FALHA:-0}" = 0 ] ;;
  run) case "$2" in
         list) printf '%s\\n' 5 6 99 ;;
         cancel) for a; do u=$a; done; echo "$u" >> "$FALSO_CANCELADOS" ;;
       esac ;;
esac
"""


def bloco_obsoletas():
    m = re.search(r"(?ms)^  obsoletas:\n(.*?)^  [a-z0-9-]+:\n", CI)
    return m.group(1)


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
        self.assertIn("head.repo.full_name == github.repository", b)  # fork nao tem token de escrita


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

    def test_outros_docs_e_o_devops_nao_contam_como_parecer(self):
        self.assertEqual(self.rodar("docs/devops/a.md\n"), ["5", "6"])
        self.assertEqual(self.rodar("docs/reviews-x/a.md\n"), ["5", "6"])

    def test_falha_fechada_cancela_quando_nao_prova(self):
        self.assertEqual(self.rodar("docs/reviews/a.md\n", before=""), ["5", "6"])  # sem sha anterior
        self.assertEqual(self.rodar("docs/reviews/a.md\n", acao="opened"), ["5", "6"])
        self.assertEqual(self.rodar("", ), ["5", "6"])  # diff vazio nao prova
        self.assertEqual(self.rodar("docs/reviews/a.md\n", api_falha=True), ["5", "6"])  # compare falhou
        grande = "".join(f"docs/reviews/{i}.md\n" for i in range(300))
        self.assertEqual(self.rodar(grande), ["5", "6"])  # compare corta em 300 arquivos


if __name__ == "__main__":
    unittest.main()
