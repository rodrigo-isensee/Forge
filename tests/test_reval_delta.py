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


class Validade(Repositorio):
    def test_texto_ou_forma_nao_desatualiza_e_codigo_sim(self):
        parecer = self.commitar(BASE, "parecer")
        self.commitar({"README.md": "ortografia\n", "docs/x.md": "a \nb\n", "changelog.d/x.md": "- y\n"})
        self.assertIsNone(fc.commit_vale(self.repo, parecer))
        self.commitar({"docs/propostas/_modelo.md": "b\n"})
        self.assertIn("desatualizado: docs/propostas/_modelo.md", fc.commit_vale(self.repo, parecer))

    def base_nova(self, arquivos):
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar(arquivos, "base nova")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        git("merge", "-q", "--no-edit", "develop", cwd=self.repo)

    def test_com_base_texto_depois_do_merge_vale_e_conflito_de_texto_nao(self):
        parecer = self.commitar({"README.md": "branch\n", "src/app.txt": "v2\n"}, "parecer")
        self.base_nova({"docs/y.md": "y\n"})
        self.commitar({"docs/propostas/p.md": "depois\n"})
        self.assertIsNone(fc.commit_vale(self.repo, parecer, base="develop"))
        git("switch", "-q", "develop", cwd=self.repo)
        self.commitar({"README.md": "develop\n"}, "conflito")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        with self.assertRaises(subprocess.CalledProcessError):
            git("merge", "-q", "--no-edit", "develop", cwd=self.repo)
        self.commitar({"README.md": "resolvido\n"}, "resolução")
        self.assertIn("README.md", fc.commit_vale(self.repo, parecer, base="develop") or "")

    def test_delta_classe_so_com_a_flag(self):
        inicio = self.commitar(BASE, "parecer")
        self.commitar({"README.md": "x\n", "bin/x": "b\n"})
        rc, sem = self.check("delta", inicio)
        rc2, com = self.check("delta", inicio, "--classe")
        self.assertEqual((rc, rc2), (0, 0))
        self.assertNotIn("classe", sem)
        self.assertIn('delta: "README.md" classe texto\n', com)
        self.assertIn('delta: "bin/x" classe codigo\n', com)
        self.assertTrue(com.endswith("delta: classe codigo\n"), com)


# C-2 com o adendo da volta 1 (modelo de ameaças da 0.37): cada citação de um caminho de TEXTO por código, agente ou
# skill, conferida uma a uma pelo security-engineer como não normativa. Chave (arquivo, caminho), valor (linhas, motivo).
# Mudar esta lista é diff em tests/ (codigo), com review e com o parecer de segurança.
_NOME = {"bin/forge-check": 1, "scripts/suite-paralela.py": 1, "bin/forge-novo-projeto": 2, "tests/test_catraca.py": 1,
         "tests/test_changelog.py": 1, "tests/test_ci_local.py": 7, "tests/test_estado_da_branch.py": 1, "tests/test_etapa_do_brief.py": 1,
         "tests/test_hooks.py": 2, "tests/test_isencoes.py": 5, "tests/test_pre_push_parecer.py": 1, "tests/test_prepush_so_docs.py": 2,
         "tests/test_salvar_desfazer.py": 3, "tests/test_suite_reuso.py": 1, "tests/e2e-instalacao.sh": 1,
         "tests/test_classe_risco.py": 1, "tests/test_parecer_conteudo.py": 2,
         "tests/test_t1_codigo_sem_teste.py": 1}  # 0.43.1 G e F: nome de arquivo sintético
CITACOES_CONHECIDAS = {**{(a, "README.md"): (n, "nome") for a, n in _NOME.items()},
                       ("hooks/conformidade.json", "docs/propostas/"): (1, "destino"),
                       ("agents/agile-coach.md", "docs/retrospectivas/"): (2, "destino"),
                       ("skills/kanban-scrum/SKILL.md", "docs/retrospectivas/"): (1, "destino"),
                       ("tests/test_hooks.py", "docs/propostas/"): (17, "destino"),
                       ("tests/test_brief_forma_aceita.py", "docs/propostas/"): (14, "destino"),  # 0.43.3: briefs sintéticos
                       ("hooks/conformidade.py", "README.md"): (1, "prosa"),  # 0.43.1 T: o jarvis.md não cita mais o README.md
                       ("skills/novo-projeto/SKILL.md", "docs/propostas/"): (1, "prosa"),
                       ("tests/apoio_volta_unica.py", "docs/propostas/"): (1, "prosa"),
                       ("tests/test_forge.py", "README.md"): (15, "teste-le"), ("tests/test_conferir_reversao.py", "README.md"): (14, "teste-le"), ("tests/test_doutor.py", "README.md"): (1, "teste-le"),
                       ("tests/test_forge.py", "docs/propostas/"): (2, "teste-le"),
                       # 0.45.7 E1: o texto da R-WIP mora em docs/regras/README.md; o invariante, o teste e o apoio o leem
                       ("tests/test_jarvis_nucleo.py", "README.md"): (1, "teste-le"),  # lê a linha da R-WIP em docs/regras/README.md
                       ("tests/config.json", "README.md"): (2, "teste-le"), ("tests/apoio_regra_id.py", "README.md"): (1, "teste-le")}
MOTIVOS = ("nome", "destino", "prosa", "teste-le")
LE_CONTEUDO = ("read_text(", "open(", '"show"', "cat ")  # (d): leitura de conteúdo não se esconde atrás de `nome`


def conferir_citacoes(citacoes, conhecidas):
    """Problemas da guarda: `citacoes` é {(arquivo, caminho): [linhas que citam]} achado na varredura."""
    problemas = []
    for (arquivo, caminho), (linhas, motivo) in sorted(conhecidas.items()):
        if motivo not in MOTIVOS or motivo == "teste-le" and not arquivo.startswith("tests/"):
            problemas.append(f"(c) {arquivo} · {caminho}: motivo {motivo!r}")
        if not isinstance(linhas, int) or linhas < 1:
            problemas.append(f"(b) {arquivo} · {caminho}: contagem {linhas!r} na lista")
    for chave in sorted(set(citacoes) | set(conhecidas)):
        achadas, conhecida = len(citacoes.get(chave, [])), conhecidas.get(chave, (0, ""))[0]
        if achadas != conhecida:
            problemas.append(f"({'a' if achadas > conhecida else 'b'}) {chave[0]} · {chave[1]}: {achadas} linhas, a lista diz {conhecida}")
        problemas += [f"(d) {chave[0]} lê {chave[1]}: {linha.strip()}" for linha in citacoes.get(chave, [])
                      if not chave[0].startswith("tests/") and any(x in linha for x in LE_CONTEUDO)]
    return problemas


class Guarda(unittest.TestCase):
    maxDiff = None
    # C-2: só CHANGELOG.md e changelog.d/ ficam fora (lidos pela release; o CI do PR prova). Fora da varredura ficam a
    # definição de TEXTO e este arquivo, que são a lista.
    TOLERADOS = ("CHANGELOG.md", "changelog.d/")
    PASTAS = ("bin", "hooks", "scripts", "tests", ".github", ".githooks", "agents", "skills")
    CORPUS = re.compile(r"^tests/(hooks|fixtures|transcricoes|migracoes|mutantes)/")

    def varrer(self):
        caminhos = [x for x in fc.TEXTO if x not in self.TOLERADOS]
        self.assertGreaterEqual(len(caminhos), 3)
        arquivos = [p for d in self.PASTAS for p in (RAIZ / d).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        self.assertGreater(len(arquivos), 100)
        citacoes = {}
        for p in arquivos:
            rel = p.relative_to(RAIZ).as_posix()
            if self.CORPUS.match(rel) or p == Path(__file__).resolve():
                continue
            for linha in p.read_text(encoding="utf-8", errors="replace").splitlines():
                for caminho in caminhos:
                    if caminho in linha and not linha.startswith("TEXTO = ("):
                        citacoes.setdefault((rel, caminho), []).append(linha)
        return citacoes

    def test_caminho_de_texto_so_e_citado_como_a_lista_conhece(self):
        self.assertEqual(conferir_citacoes(self.varrer(), CITACOES_CONHECIDAS), [],
                         "citação nova de caminho de TEXTO: tire-o de TEXTO em bin/forge-check ou leve ao parecer de segurança")

    def test_reprova_citacao_nova_folga_motivo_e_leitura(self):  # (a) a (d) do adendo, em lista e varredura sintéticas
        lista = {("bin/x", "README.md"): (1, "nome"), ("tests/test_x.py", "README.md"): (2, "teste-le")}
        vale = {("bin/x", "README.md"): ['if nome == "README.md":'], ("tests/test_x.py", "README.md"): ["a README.md", "b README.md"]}
        self.assertEqual(conferir_citacoes(vale, lista), [])
        casos = {"(a)": ({**vale, ("agents/x.md", "docs/propostas/"): ["siga docs/propostas/x.md"]}, lista),
                 "(a) ": ({**vale, ("bin/x", "README.md"): ['if nome == "README.md":', "x"]}, lista),
                 "(b)": ({**vale, ("tests/test_x.py", "README.md"): ["a README.md"]}, lista),
                 "(b) ": ({k: v for k, v in vale.items() if k[0] == "bin/x"}, lista),
                 "(b)  ": (vale, {**lista, ("bin/y", "README.md"): (0, "nome")}),
                 "(c)": (vale, {**lista, ("bin/x", "README.md"): (1, "leitura")}),
                 "(c) ": ({**vale, ("bin/y", "README.md"): ["y"]}, {**lista, ("bin/y", "README.md"): (1, "teste-le")}),
                 "(d)": ({**vale, ("bin/x", "README.md"): ['Path("README.md").read_text()']}, lista),
                 "(d) ": ({**vale, ("bin/x", "README.md"): ["cat README.md"]}, lista)}
        for rotulo, (citacoes, conhecidas) in casos.items():
            with self.subTest(rotulo):
                problemas = conferir_citacoes(citacoes, conhecidas)
                self.assertTrue(problemas and all(x.startswith(rotulo.strip()) for x in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
