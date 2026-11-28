"""FILTROS-L08-G2-ORIGIN-LOCAL (v0478 E2.1): os filtros L08 (commit já na base), G2 (merge da base pelo primeiro pai) e E2 (só a
integração da base) do escopo da conferência confiavam na `origin/<base>` local, que o autor reescreve (`git update-ref`) e assim
escondia do escopo o arquivo fora do declarado. Na conferência, o commit da base só sai do escopo se também for ancestral de uma
âncora: o Base-sha da entrega ou o de brief selado depois dele (os registros do Jarvis), como o merge-base e a junção limpa."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
import test_selo_e_entrega as selo  # noqa: E402  (pelo módulo: importar as classes as rodaria de novo aqui)

fc = selo.fc


class FiltrosAncorados(selo.Conferencia):
    develop_anda, ancorar, mesclar_develop = (selo.MergeDaBaseDepoisDoBrief.develop_anda, selo.MergeDaBaseDepoisDoBrief.ancorar,
                                             selo.MergeDaBaseDepoisDoBrief.mesclar_develop)

    def fora(self, ramo=None):
        """Um commit com `fora.txt` (fora do declarado): na branch ou, com `ramo`, numa branch lateral a partir do Base-sha."""
        if ramo:
            self.git("switch", "-q", "-c", ramo, self.base)
        self.gravar("fora.txt", "f\n")
        self.git("add", "fora.txt")
        sha = self.commit("feat: fora do declarado")
        if ramo:
            self.git("switch", "-q", "melhoria/x")
        return sha

    def depois_do_merge(self):
        self.gravar("bin/app", "x\ny\nz\n")
        self.git("add", "bin/app")
        self.commit("feat: depois do merge")

    def reprova_com_o_fora(self):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "fora.txt"', saida)

    def test_l08_commit_na_origin_develop_reescrita_segue_no_escopo(self):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.fora()
        self.entregar()
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD~1")  # a ref local passa a conter o commit do autor
        self.reprova_com_o_fora()

    def test_g2_merge_da_origin_develop_reescrita_segue_no_escopo(self):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        lateral = self.fora("lateral")
        self.git("update-ref", "refs/remotes/origin/develop", lateral)
        self.mesclar_develop()
        self.depois_do_merge()
        self.reprova_com_o_fora()
        self.assertIn('escopo: merge da "develop" sem âncora', self.conferir()[1])

    def test_merge_da_develop_real_ancorada_sai_do_escopo(self):  # o caminho legítimo do G2 segue: a âncora é registro do Jarvis
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        ponta, = self.develop_anda("a\n")
        self.ancorar(ponta)
        self.mesclar_develop()
        self.depois_do_merge()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("agents/outro.md", saida)
        self.assertNotIn("sem âncora", saida)

    def test_e2_integracao_so_vale_ancorada(self):
        lateral = self.fora("lateral")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "junta", lateral)
        head = self.git("rev-parse", "HEAD")
        self.assertIsNotNone(fc.diferem_dos_dois_pais(self.proj, self.base, head, lateral, None))  # sem âncora pedida: como antes
        self.assertIsNone(fc.diferem_dos_dois_pais(self.proj, self.base, head, lateral, [self.base]))
        self.assertIsNotNone(fc.diferem_dos_dois_pais(self.proj, self.base, head, lateral, [self.base, lateral]))


if __name__ == "__main__":
    unittest.main()
