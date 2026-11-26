"""M9.2 do G2 (pedido v0481, E21.1; docs/security/ameacas/g2-parecer-status.md, T9): o hook `conformidade` registra a autoria
do parecer a publicar (`.forge/pareceres/<pedido>/<tipo>.md`), e o `forge-check parecer publicar` (G2.1, #878) aceita o parecer
gravado pelo papel do tipo e recusa sem o registro. De ponta a ponta: o hook de verdade num subprocesso, o `gh` falso de
`test_forge_pareceres` (sem rede)."""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge_pareceres import PEDIDO, GhFalso, fc, parecer  # noqa: E402
from test_hooks import rodar  # noqa: E402


class AutoriaDoPublicar(GhFalso):
    def setUp(self):
        super().setUp()
        (self.repo / ".forge").mkdir(exist_ok=True)
        (self.repo / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")

    def grava(self, texto, rel=f".forge/pareceres/{PEDIDO}/review.md"):
        arq = self.repo / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def hook(self, arq, papel="forge:tech-lead"):
        """O PostToolUse do Write, como o Claude Code o chama depois da gravação."""
        entrada = {"tool_name": "Write", "tool_input": {"file_path": str(arq)}, "agent_type": papel,
                   "hook_event_name": "PostToolUse", "tool_use_id": "toolu_1"}
        r = rodar("conformidade", entrada, self.repo, extra={"CLAUDE_PROJECT_DIR": str(self.repo)})
        self.assertEqual(r.returncode, 0, r.stderr)

    def registros(self):
        arq = self.repo / ".forge" / "run" / "autoria.jsonl"
        return [json.loads(x) for x in arq.read_text(encoding="utf-8").splitlines()] if arq.exists() else []

    def publicar(self, arq):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            rc = fc().cmd_parecer_publicar(self.repo, str(arq))
        return rc, saida.getvalue()

    def test_autoria_registra_forge_pareceres(self):
        self.hook(self.grava(parecer(self.sha)))
        self.assertEqual([(r["caminho"], r["papel"]) for r in self.registros()],
                         [(f".forge/pareceres/{PEDIDO}/review.md", "tech-lead")])

    def test_caminho_por_papel_em_forge_pareceres(self):
        """O registro leva o papel de quem gravou: o QA que grava o `review.md` não vira autoria do tech-lead."""
        self.hook(self.grava(parecer(self.sha)), papel="forge:qa-engineer")
        self.assertEqual([r["papel"] for r in self.registros()], ["qa"])

    def test_fora_de_pedido_e_tipo_nao_registra(self):
        for rel in (".forge/pareceres/review.md", f".forge/pareceres/{PEDIDO}/velho/review.md",
                    f".forge/pareceres/{PEDIDO}/review.txt", f".forge/outros/{PEDIDO}/review.md"):
            with self.subTest(rel=rel):
                self.hook(self.grava(parecer(self.sha), rel))
                self.assertEqual(self.registros(), [])

    def test_ponta_a_ponta_publica_com_autoria_do_hook(self):
        arq = self.grava(parecer(self.sha))
        self.hook(arq)
        rc, saida = self.publicar(arq)
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"parecer publicado: parecer-review aprovado {self.sha[:7]}", saida)

    def test_ponta_a_ponta_recusa_sem_autoria(self):
        rc, saida = self.publicar(self.grava(parecer(self.sha)))
        self.assertEqual(rc, 1, saida)
        self.assertIn("autoria: sem registro de que o papel `tech-lead` gravou este texto (M9.1)", saida)
        self.assertEqual(self.chamadas(), [], "recusado antes de chamar o gh")

    def test_ponta_a_ponta_recusa_autoria_de_outro_papel(self):
        arq = self.grava(parecer(self.sha))
        self.hook(arq, papel="forge:qa-engineer")
        rc, saida = self.publicar(arq)
        self.assertEqual(rc, 1, saida)
        self.assertIn("papel `tech-lead`", saida)


if __name__ == "__main__":
    unittest.main()
