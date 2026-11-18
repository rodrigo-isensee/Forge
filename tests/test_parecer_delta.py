"""E3.49 (v0474): o `parecer delta` tira do delta os pareceres e o quadro (LIVRES), mas não o `.md` de `docs/devops/` que não é parecer
(sem frontmatter: runbook, postura), que muda o que o revisor leu."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_volta_por_delta import Repositorio  # noqa: E402

REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
          "revisor: forge:tech-lead\ndata: 2026-11-17\n---\n# Parecer\n")
DEVOPS = ("---\ntipo: revisao-devops\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
          "revisor: forge:devops-engineer\ndata: 2026-11-17\n---\n# Parecer\n")


class DocumentoDeDevops(Repositorio):
    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"src/app.txt": "v2\n"}, "entrega")
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=self.c1)}, "parecer")

    def delta(self):
        rc, saida = self.check("parecer", "delta", "docs/reviews/p1.md")
        self.assertEqual(rc, 0, saida)
        return saida

    def test_documento_sem_frontmatter_fica_no_delta(self):
        self.commitar({"docs/devops/runbook.md": "# Runbook\npasso novo\n"}, "docs: runbook")
        self.assertIn('"docs/devops/runbook.md"', self.delta())

    def test_documento_apagado_fica_no_delta(self):
        self.commitar({"docs/devops/runbook.md": "# Runbook\n"}, "docs: runbook")
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=self.head())}, "parecer de novo")
        (self.repo / "docs" / "devops" / "runbook.md").unlink()
        self.commitar({}, "docs: apaga o runbook")
        self.assertIn('"docs/devops/runbook.md"', self.delta())

    def test_parecer_de_devops_sai_do_delta(self):
        self.commitar({"docs/devops/p1.md": DEVOPS.format(c=self.c1)}, "parecer devops")
        saida = self.delta()
        self.assertNotIn("docs/devops/p1.md", saida)
        self.assertIn("delta: nenhum arquivo do domínio mudou", saida)

    def test_livre_fora_de_devops_sem_frontmatter_segue_fora_do_delta(self):
        self.commitar({"KANBAN.md": "# Quadro\n", "docs/security/postura.md": "# Postura\n"}, "quadro e postura")
        saida = self.delta()
        self.assertNotIn("KANBAN.md", saida)
        self.assertNotIn("postura.md", saida)
