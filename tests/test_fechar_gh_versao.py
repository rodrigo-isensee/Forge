"""GH-VERSAO-MINIMA (v047, E1.198): o passo 1 do forge-fechar confere gh >= 2.47 antes de abrir PR e busca origin/homolog se faltar no clone."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar_sha_conferido as sc  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


class FecharGhVersao(unittest.TestCase):
    tearDown, git, fechar, chamadas, criacoes = (sc.FecharShaConferido.tearDown, sc.FecharShaConferido.git, sc.FecharShaConferido.fechar,
                                                 sc.FecharShaConferido.chamadas, sc.FecharShaConferido.criacoes)
    setUp = sc.FecharShaConferido.setUp

    def para_com(self, versao):
        r = self.fechar("p1", "--ref", "melhoria/x", VERSAO_GH=versao)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("passo 1", r.stderr)
        self.assertIn(f"gh {versao[:4]}", r.stderr)
        self.assertIn("preparar-estacao.sh", r.stderr)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual([c for c in self.chamadas() if c.startswith("forge-check")], [])  # parou antes do forge-check

    def test_gh_2_45_do_apt_para_no_passo_1_sem_abrir_nada(self):
        self.para_com("2.45.0")

    def test_gh_logo_abaixo_do_minimo_para(self):
        self.para_com("2.46.9")

    def test_gh_de_major_menor_para(self):
        self.para_com("1.99.0")

    def segue_com(self, versao):
        r = self.fechar("p1", "--ref", "melhoria/x", VERSAO_GH=versao)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_gh_na_versao_minima_segue(self):
        self.segue_com("2.47.0")

    def test_gh_recente_segue(self):
        self.segue_com("2.104.0")

    def test_gh_de_major_maior_segue(self):
        self.segue_com("3.0.1")

    def test_versao_ilegivel_para(self):
        (self.tmp / "gh").write_text('#!/usr/bin/env bash\n[ "$1" = "--version" ] && echo "lixo" && exit 0\nexit 0\n', encoding="utf-8")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não consegui ler a versão do gh", r.stderr)

    def test_busca_origin_homolog_quando_falta(self):
        self.git("branch", "homolog", "develop", cwd=self.remoto)  # só no servidor: o clone não tem a ref remota
        self.assertEqual(self.git("branch", "-r", "--list", "origin/homolog"), "")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("origin/homolog", self.git("branch", "-r", "--list", "origin/homolog"))

    def test_sem_homolog_no_servidor_so_avisa(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("sem origin/homolog", r.stderr)


if __name__ == "__main__":
    unittest.main()
