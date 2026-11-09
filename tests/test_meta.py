"""S4 (0.44.2): `forge-check meta --armar|--desarmar|--estado` grava o objetivo onde o hook de Stop (hooks/meta.py) o lê
(fixtures em tests/hooks/meta)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")


class Meta(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-meta-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(self.tmp)], check=True)
        (self.tmp / ".forge").mkdir()

    def rodar(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "meta", *args], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout

    def test_armar_grava_no_run_do_hook_e_desarmar_tira(self):
        rc, out = self.rodar("--armar", "p1", "--checagem", "python3 -m unittest tests.x", "--checagem", "true")
        self.assertEqual(rc, 0, out)
        meta = json.loads((self.tmp / ".forge" / "run" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["pedido"], meta["armado"], meta["checagens"]), ("p1", True, [["python3", "-m", "unittest", "tests.x"], ["true"]]))
        self.assertIn("armado=True", self.rodar("--estado")[1])
        self.assertEqual(self.rodar("--desarmar")[0], 0)
        self.assertEqual(self.rodar("--estado")[0], 1)

    def test_sem_checagem_ou_pedido_invalido_recusa(self):
        self.assertEqual(self.rodar("--armar", "p1")[0], 2)
        self.assertEqual(self.rodar("--armar", "../x", "--checagem", "true")[0], 2)
        self.assertEqual(self.rodar("--armar", "p1", "--checagem", "'aberta")[0], 2)
        self.assertFalse((self.tmp / ".forge" / "run" / "meta.json").exists())


class Jargao(unittest.TestCase):
    def test_lista_vem_da_tabela_do_modo_iniciante(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        self.assertEqual(set(meta.jargao()), {"pull request", "PR", "branch", "merge", "mesclar", "commit", "repositório", "hook", "CI",
                                              "deploy"})

    def test_ultima_mensagem_com_texto_do_assistente(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        ferramenta = {"type": "tool_use", "name": "Bash", "input": {}}
        linhas = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "velha"}]}},
                  {"type": "user", "message": {"content": "oi"}},
                  {"type": "assistant", "message": {"content": [ferramenta, {"type": "text", "text": "nova"}]}},
                  {"type": "user", "message": {"content": [{"type": "text", "text": "do dono"}]}},
                  {"type": "assistant", "message": {"content": [ferramenta]}}]
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "t.jsonl"
            arq.write_text("\n".join(json.dumps(l) for l in linhas) + "\n", encoding="utf-8")
            self.assertEqual(meta.ultima_mensagem(str(arq)), "nova")

    def test_medida_que_falha_nao_troca_o_stop(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        chamado = []

        class Falso:
            def campo(self, *_):
                return "/x"

            def projeto(self, *_a, **_k):
                return Path("/x")

            def cwd(self):
                return Path("/x")

            def registrar_erro(self, erro):
                chamado.append(erro)

        original_medir, original_meta = meta.medir_mensagem, meta.avaliar_meta
        meta.medir_mensagem = lambda hook: (_ for _ in ()).throw(RuntimeError("medida"))
        meta.avaliar_meta = lambda hook, raiz: chamado.append("meta")
        try:
            meta.principal(type("H", (Falso,), {"campo": lambda self, *c: "Stop"})())
        finally:
            meta.medir_mensagem, meta.avaliar_meta = original_medir, original_meta
        self.assertIsInstance(chamado[0], RuntimeError)
        self.assertEqual(chamado[1], "meta", "a falha da medida não pula a conferência do objetivo")


if __name__ == "__main__":
    unittest.main()
