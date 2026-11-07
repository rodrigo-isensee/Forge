"""EST-M4 (E3a da 0.37): o parecer não envelhece por delta só de `texto` ou de `forma` (`classes_do_intervalo`,
`commit_vale`, `delta --classe`), com os controles C-1 a C-5 do modelo de ameaças da 0.37, em repositório temporário."""
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_volta_por_delta import Repositorio, carregar_forge_check  # noqa: E402

fc = carregar_forge_check()
CONFIG = json.dumps({"invariantes": {"docs/propostas/inv.md": ["x"]}})
BASE = {"README.md": "a\nb\n", "docs/propostas/p.md": "a\nb\n", "docs/propostas/_modelo.md": "a\n", "docs/propostas/fm.md": "---\nx: 1\n---\n",
        "docs/propostas/inv.md": "a\n", "docs/x.md": "a\nb\n", "docs/fm.md": "---\nx: 1\n---\n", "docs/regras/R-X.md": "a\n", "docs/adr/0001-x.md": "a\n", "docs/x.py": "a\n", "agents/a.md": "a\n", "bin/x": "a\n", "tests/config.json": CONFIG}


class Classes(Repositorio):
    def setUp(self):
        super().setUp()
        self.antes = self.commitar(BASE, "base do item")

    def classe(self, mudanca):
        git("reset", "-q", "--hard", self.antes, cwd=self.repo)  # cada caso parte da mesma base
        mudanca()
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", "depois", cwd=self.repo)
        return fc.classes_do_intervalo(self.repo, self.antes, "HEAD", fc.nomes_do_intervalo(self.repo, self.antes, "HEAD"))

    def escrever(self, rel, texto):
        return lambda: (self.repo / rel).write_text(texto, encoding="utf-8")

    def test_texto_e_lista_branca_e_o_normativo_e_codigo(self):  # C-1
        casos = {"README.md": "texto", "docs/propostas/p.md": "texto", "docs/propostas/_modelo.md": "codigo",
                 "docs/propostas/fm.md": "codigo", "docs/propostas/inv.md": "codigo", "docs/x.md": "codigo", "agents/a.md": "codigo"}
        for rel, esperada in casos.items():
            with self.subTest(rel):
                self.assertEqual(self.classe(self.escrever(rel, "outro texto\n")), {rel: esperada})

    def test_forma_so_com_espaco_no_fim_em_md_fora_das_pastas_de_codigo(self):  # C-3, C-4
        casos = {"docs/x.md": ("a  \nb", "forma"), "docs/x.py": ("a  \n", "codigo"), "bin/x": ("a \n", "codigo"),
                 "agents/a.md": ("a \n", "codigo"), "docs/propostas/inv.md": ("a \n", "codigo")}
        casos_x = {"indentação": " a\nb\n", "linha em branco": "a\n\nb\n", "espaço interno": "a\nb \tb\n"}
        for rel, (texto, esperada) in casos.items():
            with self.subTest(rel):
                self.assertEqual(self.classe(self.escrever(rel, texto)), {rel: esperada})
        for nome, texto in casos_x.items():
            with self.subTest(nome):
                self.assertEqual(self.classe(self.escrever("docs/x.md", texto)), {"docs/x.md": "codigo"})

    def test_forma_nunca_em_frontmatter_regras_nem_adr(self):  # C-1 também no ramo forma
        casos = {"docs/fm.md": "---\nx: 1 \n---\n", "docs/propostas/fm.md": "--- \nx: 1\n---\n",
                 "docs/regras/R-X.md": "a \n", "docs/adr/0001-x.md": "a \n"}
        for rel, texto in casos.items():
            with self.subTest(rel):
                self.assertEqual(self.classe(self.escrever(rel, texto)), {rel: "codigo"})

    def test_modo_link_e_renome_sao_codigo(self):  # C-5 (A4, A5)
        self.assertEqual(self.classe(lambda: os.chmod(self.repo / "README.md", 0o755)), {"README.md": "codigo"})
        self.assertEqual(self.classe(lambda: ((self.repo / "docs/propostas/p.md").unlink(),
                                              os.symlink("../../agents/a.md", self.repo / "docs/propostas/p.md"))),
                         {"docs/propostas/p.md": "codigo"})
        self.assertEqual(self.classe(lambda: git("mv", "bin/x", "docs/propostas/x.md", cwd=self.repo)),
                         {"bin/x": "codigo", "docs/propostas/x.md": "texto"})

    def test_config_ilegivel_fecha_tudo_em_codigo(self):
        mudanca = lambda: (self.escrever("tests/config.json", "{")(), self.escrever("README.md", "c\n")())  # noqa: E731
        self.assertEqual(self.classe(mudanca)["README.md"], "codigo")


if __name__ == "__main__":
    unittest.main()
