"""PREPUSH-TAGS (cartão 2 da 0.34): o push só de tags de commits que já estão no remoto não roda teste nem entra na fila."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_pre_push import ZERO, Repo  # noqa: E402


def tag(nome, sha, remoto=ZERO):
    return f"refs/tags/{nome} {sha} refs/tags/{nome} {remoto}\n"


class PrePushTags(Repo):
    def test_tags_de_commit_ja_no_remoto_saem_sem_teste_e_sem_fila(self):
        self.git("tag", "-a", "v2", "-m", "r", self.base)
        rc, marcas, erro = self.envia(tag("v1", self.base), tag("v2", self.git("rev-parse", "v2")))
        self.assertEqual((rc, marcas), (0, set()), erro)
        self.assertIn("só leva tags", erro)
        self.assertNotIn("esperando a vez", erro)

    def test_falha_fechada_entra_na_fila(self):
        novo = self.commit(**{"src/app.py": "y\n"})
        self.git("update-ref", "refs/remotes/outro/x", novo)
        solto = self.commit(**{"src/app.py": "z\n"})
        for nome, linhas, remoto in (("commit novo", [tag("v3", solto)], "origin"),
                                     ("commit só em outro remoto", [tag("v3", novo)], "origin"),
                                     ("tag com branch", [tag("v1", self.base), f"refs/heads/x {novo} refs/heads/melhoria/x {self.base}\n"], "origin"),
                                     ("remoto por URL", [tag("v1", self.base)], "https://example.com/r.git")):
            with self.subTest(nome):
                self.assert_fila(self.envia(*linhas, remoto=remoto))

    def test_tag_nao_abre_develop_homolog_main_nem_tag_movida(self):
        for destino in ("develop", "homolog", "main"):
            with self.subTest(destino):
                rc, _, erro = self.envia(tag("v1", self.base), f"refs/heads/x {self.base} refs/heads/{destino} {ZERO}\n")
                self.assertEqual(rc, 1)
                self.assertIn("bloqueado", erro)
        outro = self.commit(**{"src/app.py": "y\n"})
        self.git("reset", "-q", "--hard", self.base)
        lateral = self.commit(**{"docs/guia.md": "l\n"})
        for sha in (outro, lateral):
            self.git("update-ref", f"refs/remotes/origin/r{sha[:6]}", sha)
        rc, _, erro = self.envia(tag("v1", lateral, outro))
        self.assertEqual(rc, 1)
        self.assertIn("R-VERIFY", erro)


if __name__ == "__main__":
    unittest.main()
