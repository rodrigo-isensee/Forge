"""AQ-5 e Z7 (0.43.3): o brief de review, segurança e QA leva o sha a revisar (`Revisar-sha:`, calculado pelo `brief selar`), o
`forge-check parecer novo` imprime o esqueleto válido do parecer com esse sha em `commit:`, e o `forge-check pr` recusa o `commit:` que é
um commit só de parecer (o HEAD depois dos pareceres paralelos), com a dica do sha certo. Sem rede."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_selo_e_entrega import Repositorio, fc  # noqa: E402

PARECER = """---
tipo: {tipo}
contrato: 1
pedido: x
branch: melhoria/x
commit: {commit}
parecer: aprovado
{extra}data: 2026-01-01
---
# Parecer

## Achados
"""


class Base(Repositorio):
    def codigo_e_pareceres(self):
        """Um commit de código e, por cima, dois commits só de parecer (QA e review paralelos); devolve o sha do código."""
        self.entregar()
        codigo = self.git("rev-parse", "HEAD")
        self.gravar("docs/qa/x.md", PARECER.format(tipo="qa", commit=codigo, extra="escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\n"
                                                   "bugs_medios: 0\nbugs_baixos: 0\n"))
        self.git("add", "docs/qa/x.md")
        self.so_qa = self.commit("docs(qa): parecer")
        return codigo


class ShaARevisar(Base):
    def test_pula_os_commits_so_de_parecer(self):
        codigo = self.codigo_e_pareceres()
        self.assertEqual(fc.so_de_parecer(self.proj, self.so_qa), True)
        self.assertEqual(fc.so_de_parecer(self.proj, codigo), False)
        self.assertEqual(fc.so_de_parecer(self.proj, self.so_qa, "x"), True)
        self.assertEqual(fc.so_de_parecer(self.proj, self.so_qa, "outro"), False)  # parecer de outro pedido é entrega
        self.assertEqual(fc.sha_a_revisar(self.proj, "melhoria/x"), codigo)
        self.assertIsNone(fc.sha_a_revisar(self.proj, "nao-existe"))

    def test_gerar_do_review_traz_o_revisar_sha(self):
        codigo = self.codigo_e_pareceres()
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:tech-lead", "--cobre", "E1.2",
                               "--etapa", "review", "--branch", "melhoria/x")
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"\nRevisar-sha: {codigo}\n", saida)
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:node-backend", "--branch", "melhoria/x",
                               "--etapa", "codigo")
        self.assertNotIn("Revisar-sha:", saida)  # o brief de código não revisa

    def test_selar_corrige_ou_acrescenta_o_revisar_sha(self):
        codigo = self.codigo_e_pareceres()
        cabeca = "Branch: melhoria/x   Base: develop\nEtapa: review\n"
        for texto, digitado in ((cabeca + "Revisar-sha: " + "1" * 40 + "\n\n## Objetivo\n", "1" * 40), (cabeca + "\n## Objetivo\n", "ausente")):
            with self.subTest(digitado=digitado):
                correcoes, reprovas = [], []
                novo = fc.corrigir_revisar_sha(self.proj, texto, "melhoria/x", correcoes, reprovas)
                self.assertEqual(reprovas, [])
                self.assertIn(f"Revisar-sha: {codigo}\n", novo)
                self.assertEqual(novo.count("Revisar-sha:"), 1)
                self.assertTrue(correcoes[0].startswith(f"corrigido: Revisar-sha {digitado} -> {codigo}"), correcoes)
        texto = "Branch: melhoria/x\nEtapa: codigo\n\n## Objetivo\n"
        self.assertEqual(fc.corrigir_revisar_sha(self.proj, texto, "melhoria/x", [], []), texto)  # só nas etapas de parecer


class RecusaNoPr(Base):
    def test_commit_do_head_com_parecer_paralelo_e_recusado_com_a_dica(self):
        codigo = self.codigo_e_pareceres()
        self.gravar("docs/reviews/x.md", PARECER.format(tipo="review", commit=self.so_qa, extra="revisor: forge:tech-lead\n"))
        self.git("add", "docs/reviews/x.md")
        self.commit("docs(review): parecer")
        motivo = fc.commit_de_pareceres_paralelos(self.proj, self.so_qa, "x")
        self.assertIn("é um commit só de parecer", motivo)
        self.assertIn(f"`commit: {codigo}`", motivo)
        self.assertIsNone(fc.commit_de_pareceres_paralelos(self.proj, codigo, "x"))
        rc, saida = self.rodar("pr", "x", "--base", "develop")
        self.assertIn(f"docs/reviews/x.md: commit: {self.so_qa[:12]} é um commit só de parecer", saida)
        self.assertNotIn("docs/qa/x.md: commit:", saida)  # o QA gravou o sha do código: vale


class ParecerNovo(Base):
    def novo(self, tipo, parecer="aprovado", pedido="x"):
        return self.rodar("parecer", "novo", "--tipo", tipo, "--pedido", pedido, "--branch", "melhoria/x", "--parecer", parecer)

    def test_esqueleto_valido_de_cada_tipo_com_o_sha_a_revisar(self):
        codigo = self.codigo_e_pareceres()
        for tipo, (contrato, _, _) in fc.TIPO_DO_PARECER_NOVO.items():
            for parecer in ("aprovado", "reprovado"):
                with self.subTest(tipo=tipo, parecer=parecer):
                    rc, saida = self.novo(tipo, parecer)
                    self.assertEqual(rc, 0, saida)
                    rel = f"{fc.CONTRATOS[contrato][0]}/x.md"
                    self.assertIn(f"parecer novo: grave em {rel}; commit: {codigo[:12]}", saida)
                    texto = saida[saida.index("---\n"):]
                    campos, violacoes = fc.validar_documento(rel, texto, estrito=True)
                    self.assertEqual(violacoes, [])
                    self.assertEqual((campos["commit"], campos["parecer"], campos["tipo"]), (codigo, parecer, contrato))

    def test_o_revisar_sha_do_brief_selado_vence(self):
        self.codigo_e_pareceres()
        arq = self.brief()
        arq.write_text(arq.read_text(encoding="utf-8").replace("Etapa: codigo", "Etapa: codigo\nRevisar-sha: " + self.base, 1), encoding="utf-8")
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        sha, fonte = fc.commit_do_parecer_novo(self.proj, "exemplo", "melhoria/x", "codigo")
        self.assertEqual((sha, fonte), (self.base, "Revisar-sha do brief selado exemplo-node-backend-1.md"))

    def test_entrada_invalida_recusa(self):
        rc, saida = self.rodar("parecer", "novo", "--tipo", "review", "--pedido", "../x", "--branch", "melhoria/x", "--parecer", "aprovado")
        self.assertEqual(rc, 2, saida)
        rc, saida = self.rodar("parecer", "novo", "--tipo", "review", "--pedido", "x", "--branch", "nao-existe", "--parecer", "aprovado")
        self.assertEqual(rc, 2, saida)
        self.assertIn("sem o sha a revisar", saida)
        rc, saida = self.rodar("parecer", "novo", "--tipo", "review", "--pedido", "x", "--branch", "melhoria/x")
        self.assertEqual(rc, 2, saida)  # sem --parecer: o veredito é de quem revisa


if __name__ == "__main__":
    import unittest
    unittest.main()
