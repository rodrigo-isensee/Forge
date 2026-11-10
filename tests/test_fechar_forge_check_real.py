"""E7 (TEMPO-B2): o `forge-fechar` com o `bin/forge-check` real no passo 1. Módulo próprio para que só ele, e não todo `test_fechar_*`
(que importa `test_fechar`), entre no mapa FORGE_CHECK do `bin/forge-testes`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` falso) sem herdar os testes dele.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class FecharComOForgeCheckReal(unittest.TestCase):
    """E7 (TEMPO-B2, review A1 do L08): o `forge-fechar` passa o sha da branch ao `forge-check pr`; com o `forge-check` real, o passo 1
    acha a branch pelo sha, lê os briefs dela e para sem a linha `entrega conferida` do head (nada é aberto nem mesclado)."""

    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown  # o cenário do Fechar, sem herdar os testes dele

    def setUp(self):
        base.Fechar.setUp(self)
        real = self.tmp / "check-real"
        real.write_text(f'#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\nexec "{sys.executable}" "{base.RAIZ / "bin" / "forge-check"}" "$@"\n',
                        encoding="utf-8")
        real.chmod(0o755)
        self.env["FORGE_CHECK"] = str(real)
        self.git("switch", "-q", "melhoria/x")
        self.entrega = self.git("rev-parse", "HEAD")
        for pasta, tipo, extra in (("reviews", "review", "revisor: forge:tech-lead\n"),
                                   ("qa", "qa", "escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\n")):
            (self.proj / "docs" / pasta).mkdir(parents=True)
            (self.proj / "docs" / pasta / "x.md").write_text(
                f"---\ntipo: {tipo}\ncontrato: 1\npedido: x\nbranch: melhoria/x\ncommit: {self.entrega}\nparecer: aprovado\n{extra}"
                "data: 2026-11-04\n---\n# parecer\n", encoding="utf-8")
        self.git("add", "docs")
        self.git("commit", "-q", "-m", "docs: pareceres")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        contrib = self.tmp / ".forge-contrib" / "docs"  # HOME é o tmp: o pedido e o brief moram onde o Jarvis do Forge os guarda
        (contrib / "briefs").mkdir(parents=True)
        (contrib / "pedidos").mkdir(parents=True)
        (contrib / "briefs" / "real-tech-lead-1.md").write_text("Pedido: real\nBranch: melhoria/x   Base: develop\n\n## Objetivo\nx\n",
                                                               encoding="utf-8")
        self.pedido = contrib / "pedidos" / "real.md"

    def test_sem_a_conferida_do_head_para_no_passo_1(self):
        self.pedido.write_text("# real\n\n## Histórico\n- 2026-11-04 08:00: aberto\n", encoding="utf-8")
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("conferência: nenhuma linha", r.stdout + r.stderr)
        self.assertIn("parou no passo 1", r.stdout + r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith(("gh pr create", "gh pr merge"))])

    def test_com_a_conferida_do_head_fecha(self):
        self.pedido.write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.entrega} (E1.2)\n", encoding="utf-8")
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue([c for c in self.chamadas() if c.startswith("gh pr merge melhoria/x --auto --squash")])



if __name__ == "__main__":
    unittest.main()
