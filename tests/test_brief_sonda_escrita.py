"""BRIEF-SONDA-ESCRITA (v0481 E45.53): a entrada da sonda que o `brief gerar --volta` copia do parecer cita um caminho
(`.git/hooks/...`, a cópia de teste da sonda) que não é arquivo a gravar: a sonda vai ao corpus de testes. O `brief` com
`Volta-de:` e `--ref` não lê esse caminho como escrita; qualquer outra linha do Entregar segue barrada, e a sonda alterada ou
sem par no parecer segue recusada."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_volta_por_delta as vv2  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

ENTRADA = "cópia com `.git/hooks/reference-transaction` executável que grava `marca`, `lista_fechada(cópia)`"
BARRADA = 'escrita: barrada ".git/hooks/reference-transaction"'


class SondaComCaminhoDeHook(vv2.BriefDeVolta):
    def setUp(self):
        super().setUp()
        self.parecer("reprovado", self.ACHADOS + f"\n## Sondas\n- S3 · {ENTRADA} · espera: hook não executado · obtido: executado\n")
        rc, saida = self.gerar()
        self.assertEqual(rc, 0, saida)
        self.texto = self.preenchido(saida)
        self.linha = next(l for l in self.texto.splitlines() if l.startswith("- (sonda review "))
        self.assertIn(ENTRADA, self.linha)

    def test_volta_com_a_sonda_do_parecer_nao_barra_a_escrita(self):  # o caso do brief tl-443
        rc, saida = self.conferir(self.texto)
        self.assertEqual(rc, 0, saida)
        self.assertNotIn(BARRADA, saida)
        self.assertNotIn("difere do parecer", saida)

    def test_linha_comum_do_entregar_com_o_caminho_segue_barrada(self):
        texto = self.texto.replace(self.linha, self.linha + "\n- grave `.git/hooks/reference-transaction` na cópia")
        rc, saida = self.conferir(texto)
        self.assertEqual(rc, 1, saida)
        self.assertIn(BARRADA, saida)

    def test_sem_ref_ou_sem_volta_de_a_entrada_segue_barrada(self):  # sem o parecer relido, a sonda não se confere
        casos = {"sem --ref": (self.texto, None), "sem Volta-de": ("\n".join(l for l in self.texto.splitlines() if not l.startswith("Volta-de:")) + "\n", "melhoria/x")}
        for nome, (texto, ref) in casos.items():
            with self.subTest(nome):
                rc, saida = self.conferir(texto, ref=ref)
                self.assertEqual(rc, 1, saida)
                self.assertIn(BARRADA, saida)

    def test_sonda_alterada_ou_sem_par_no_parecer_e_recusada(self):
        casos = {"entrada trocada": (self.linha.replace("grava `marca`", "grava `outra`"), "volta: sonda S3 difere do parecer docs/reviews/p1.md"),
                 "sonda a mais": (self.linha + "\n" + self.linha.replace(" S3)", " S9)"), "volta: sonda S9 de review não está nos pareceres lidos"),
                 "S3 repetida com outra entrada": (self.linha + "\n" + self.linha.replace("reference-transaction", "post-checkout"),
                                                   "volta: sonda S3 de review não está nos pareceres lidos")}
        for nome, (troca, esperado) in casos.items():
            with self.subTest(nome):
                rc, saida = self.conferir(self.texto.replace(self.linha, troca))
                self.assertEqual(rc, 1, saida)
                self.assertIn(esperado, saida)


    def test_sonda_de_parecer_de_outro_pedido_segue_barrada(self):  # revisao-seguranca A1, sonda S1
        entrada = "cópia com `.git/hooks/pre-push` executável"
        outro = self.REVIEW.replace("pedido: pedido-sintetico", "pedido: outro-pedido").format(
            c=self.c1[:7], p="reprovado", corpo=self.ACHADOS + f"\n## Sondas\n- S7 · {entrada} · espera: barrado · obtido: gravado\n")
        self.commitar({"docs/reviews/outro.md": outro}, "parecer de outro pedido")
        linha = f"- (sonda review {self.c1[:7]} S7) grave no corpus da branch: {entrada} · espera: barrado"
        rc, saida = self.conferir(self.texto.replace(self.linha, self.linha + "\n" + linha), "--parecer", "docs/reviews/outro.md")
        self.assertEqual(rc, 1, saida)
        self.assertIn('escrita: barrada ".git/hooks/pre-push"', saida)
        self.assertIn("volta: sonda S7 de review não está nos pareceres lidos", saida)

    def test_sonda_de_parecer_com_problema_segue_barrada(self):  # o parecer que a volta recusa não isenta a escrita
        self.parecer("reprovado", self.ACHADOS + "- A9 fora do formato\n" + f"\n## Sondas\n- S3 · {ENTRADA} · espera: hook não executado · obtido: executado\n")
        rc, saida = self.conferir(self.texto)
        self.assertEqual(rc, 1, saida)
        self.assertIn(BARRADA, saida)
        self.assertIn("volta: parecer docs/reviews/p1.md:", saida)

    def test_ref_ilegivel_ou_parecer_fora_da_ref_segue_barrada(self):
        casos = {"--ref sem commit": ((), "nada/aqui"), "--parecer fora da ref": (("--parecer", "docs/reviews/nao-existe.md"), "melhoria/x")}
        for nome, (extra, ref) in casos.items():
            with self.subTest(nome):
                rc, saida = self.conferir(self.texto, *extra, ref=ref)
                self.assertEqual(rc, 1, saida)
                self.assertIn(BARRADA, saida)


for _nome in [n for n in dir(vv2.BriefDeVolta) if n.startswith("test_")]:  # os testes herdados já rodam no módulo deles
    setattr(SondaComCaminhoDeHook, _nome, None)


if __name__ == "__main__":
    unittest.main()
