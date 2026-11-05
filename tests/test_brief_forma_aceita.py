"""E7 BRIEF-FORMA-ACEITA (versao-035): o brief gerado de código traz as formas de commit e merge que os hooks aceitam, e cada
forma de commit da constante passa pelo hook `conformidade` (a oferta não envelhece em relação ao hook). Sem rede."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_etapa_do_brief import Base, fc  # noqa: E402

HOOKS = Path(__file__).resolve().parent.parent / "hooks"
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; "
            "sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")


class FormasNoBrief(Base):
    def gerar(self, destino, *extra):
        return self.rodar("brief", "gerar", "--pedido", self.pedido, "--destino", f"forge:{destino}", *extra)

    def test_brief_de_codigo_traz_a_secao_com_cada_forma(self):
        rc, saida = self.gerar("dev-exemplo", "--cobre", "E1.1", "--branch", "melhoria/x")
        self.assertEqual(rc, 0, saida)
        self.assertIn("## Formas aceitas pelos hooks (copie, não reescreva)", saida)
        for _, comando in fc.FORMAS_DE_COMMIT:
            self.assertIn(comando, saida)
        self.assertIn("git merge-base --is-ancestor <mergeCommit> origin/develop", saida.split("## Formas aceitas")[1])

    def test_brief_de_review_nao_traz_a_secao(self):
        rc, saida = self.gerar("revisor-exemplo", "--cobre", "E1.2", "--etapa", "review", "--branch", "melhoria/x")
        self.assertNotIn("Formas aceitas pelos hooks", saida)


class FormasPassamNoHook(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-formas-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = sem_manutencao(dict(os.environ, HOME=str(self.tmp), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull))
        (self.tmp / ".forge").mkdir()
        (self.tmp / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")  # o hook só age dentro de um projeto do Forge
        subprocess.run(["git", "init", "-q", "-b", "melhoria/x", str(self.tmp)], check=True, env=self.env, timeout=60)

    def pelo_hook(self, comando):
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": comando},
                   "cwd": str(self.tmp), "agent_type": "forge:tech-lead", "session_id": "s"}
        limpo = {k: v for k, v in self.env.items() if not k.startswith("FORGE_")}
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / "conformidade.py")],
                              input=json.dumps(entrada), cwd=self.tmp, env=limpo, capture_output=True, text=True, timeout=120)

    def test_cada_forma_de_commit_passa_no_hook_conformidade_como_tech_lead(self):
        for nome, forma in fc.FORMAS_DE_COMMIT:
            r = self.pelo_hook(forma)
            with self.subTest(forma=nome):
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_o_teste_distingue_aceita_de_recusada(self):  # controle: o hook está de pé e recusa `--no-verify` (R-VERIFY)
        r = self.pelo_hook("git commit --no-verify -m 'x'")
        self.assertEqual(r.returncode, 2, r.stderr)


if __name__ == "__main__":
    unittest.main()
