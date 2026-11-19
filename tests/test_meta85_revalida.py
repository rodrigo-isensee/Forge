"""META85-REVALIDA-SO-QUEM-BARROU (v0478 E34.1): o `forge-check parecer delta` termina com a linha `revalida:`. Revalida o parecer que
barrou e, dos aprovados, só aquele cujo domínio a correção mexeu (a mesma regra do `forge-check pr`, `commit_vale`); o aprovado cujo
domínio não mudou segue valendo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_volta_por_delta import Repositorio  # noqa: E402

PARECER = ("---\ntipo: {tipo}\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: {p}\n"
           "revisor: forge:{revisor}\ndata: 2026-11-19\n---\n# Parecer\n")
CAMINHO = {"review": ("docs/reviews/p1.md", "tech-lead"), "revisao-seguranca": ("docs/security/p1.md", "security-engineer")}


class RevalidaSoQuemBarrou(Repositorio):
    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"src/app.py": "x = 1\n"}, "entrega")

    def parecer(self, tipo, veredito):
        rel, revisor = CAMINHO[tipo]
        self.commitar({rel: PARECER.format(tipo=tipo, c=self.c1, p=veredito, revisor=revisor)}, f"parecer {tipo}")
        return rel

    def revalida(self, rel):
        rc, saida = self.check("parecer", "delta", rel)
        self.assertEqual(rc, 0, saida)
        linhas = [l for l in saida.splitlines() if l.startswith("revalida: ")]
        self.assertEqual(len(linhas), 1, saida)
        return linhas[0]

    def test_parecer_que_barrou_revalida(self):
        rel = self.parecer("review", "reprovado")
        self.commitar({"docs/guia.md": "# guia\n"}, "correção fora do domínio")
        self.assertEqual(self.revalida(rel), "revalida: sim (este parecer barrou)")

    def test_aprovado_com_dominio_intacto_segue_valendo(self):
        rel = self.parecer("revisao-seguranca", "aprovado")
        self.commitar({"docs/guia.md": "# guia\n", "tests/test_app.py": "def test_x():\n    assert True\n"}, "correção do review")
        self.assertEqual(self.revalida(rel), "revalida: não (não barrou e o domínio não mudou; o parecer segue valendo)")

    def test_aprovado_com_dominio_mudado_continua_revalidando(self):
        rel = self.parecer("revisao-seguranca", "aprovado")
        self.commitar({"src/app.py": "x = 2\n"}, "correção que mexe no código")
        linha = self.revalida(rel)
        self.assertTrue(linha.startswith("revalida: sim (desatualizado: src/app.py mudou depois do parecer"), linha)

    def test_review_aprovado_com_codigo_mudado_revalida(self):
        rel = self.parecer("review", "aprovado")
        self.commitar({"src/app.py": "x = 3\n"}, "correção do QA")
        self.assertTrue(self.revalida(rel).startswith("revalida: sim (desatualizado:"))


if __name__ == "__main__":
    import unittest
    unittest.main()
