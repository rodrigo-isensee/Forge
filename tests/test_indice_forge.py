"""O índice do Forge (docs/indice-forge.md, H7) está em dia com bin/, hooks/ e scripts/."""
import importlib.machinery
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "indice-forge.py"


def carregar():
    carregador = importlib.machinery.SourceFileLoader("indice_forge", str(SCRIPT))
    spec = importlib.util.spec_from_loader(carregador.name, carregador)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def ambiente_limpo():
    """O ambiente sem as variáveis GIT_* de quem roda a suíte (AR-4), com o git sem manutenção."""
    return sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})


class IndiceDoForge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indice = carregar()

    def test_indice_esta_em_dia(self):
        self.assertEqual((RAIZ / self.indice.INDICE).read_text(encoding="utf-8"), self.indice.gerar(),
                         "docs/indice-forge.md desatualizado: rode scripts/indice-forge.py")

    def test_toda_entrada_versionada_tem_linha(self):
        texto = (RAIZ / "docs" / "indice-forge.md").read_text(encoding="utf-8")
        lista = self.indice.arquivos(RAIZ)
        self.assertGreaterEqual(len(lista), 60)
        for caminho in lista:
            with self.subTest(caminho=caminho):
                self.assertIn(f"| `{Path(caminho).name}` |", texto)
        self.assertIn("| `indice-forge.py` | índice do Forge", texto)

    def test_lista_dada_entra_uma_vez_na_secao_da_pasta(self):
        texto = self.indice.gerar(RAIZ, ["bin/forge-testes"])
        self.assertNotIn("| `forge-check` |", texto)
        linha = "| `forge-testes` | teste dirigido durante a iteração do autor"
        self.assertEqual(texto.count(linha), 1)
        self.assertEqual(texto.count("\n| `"), 1)
        self.assertLess(texto.index("## `bin/`"), texto.index(linha))
        self.assertLess(texto.index(linha), texto.index("## `hooks/`"))

    def test_conferir_da_rc_0_em_dia(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--conferir"], capture_output=True, text=True,
                           env=ambiente_limpo(), cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("em dia", r.stdout)


class Main(unittest.TestCase):
    """Os ramos do main sobre uma raiz temporária, com o gerar trocado (o texto do índice não importa aqui)."""

    def setUp(self):
        self.indice = carregar()
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        (self.raiz / "docs").mkdir()
        self.destino = self.raiz / "docs" / "indice-forge.md"
        for alvo, valor in (("RAIZ", self.raiz), ("gerar", lambda raiz: "novo\n")):
            remendo = mock.patch.object(self.indice, alvo, valor)
            remendo.start()
            self.addCleanup(remendo.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def rodar(self, argv):
        saida, erro = io.StringIO(), io.StringIO()
        with redirect_stdout(saida), redirect_stderr(erro):
            codigo = self.indice.main(argv)
        return codigo, saida.getvalue(), erro.getvalue()

    def test_conferir_desatualizado_da_rc_1_e_nao_grava(self):
        self.destino.write_text("velho\n", encoding="utf-8")
        codigo, saida, _ = self.rodar(["--conferir"])
        self.assertEqual(codigo, 1)
        self.assertIn("desatualizado", saida)
        self.assertEqual(self.destino.read_text(encoding="utf-8"), "velho\n")

    def test_conferir_sem_arquivo_da_rc_1(self):
        self.assertEqual(self.rodar(["--conferir"])[0], 1)
        self.assertFalse(self.destino.exists())

    def test_conferir_em_dia_da_rc_0(self):
        self.destino.write_text("novo\n", encoding="utf-8")
        self.assertEqual(self.rodar(["--conferir"])[0], 0)

    def test_sem_argumento_grava(self):
        self.assertEqual(self.rodar([])[0], 0)
        self.assertEqual(self.destino.read_text(encoding="utf-8"), "novo\n")

    def test_argumento_desconhecido_da_rc_2_e_nao_grava(self):
        for argv in (["--gravar"], ["--conferir", "x"]):
            with self.subTest(argv=argv):
                codigo, _, erro = self.rodar(argv)
                self.assertEqual(codigo, 2)
                self.assertIn("--conferir", erro)
                self.assertFalse(self.destino.exists())


class PrimeiraLinhaDeDoc(unittest.TestCase):
    def setUp(self):
        self.indice = carregar()
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def doc(self, nome, texto):
        (self.raiz / nome).write_text(texto, encoding="utf-8")
        return self.indice.primeira_linha_de_doc(self.raiz, nome)

    def test_python_pela_docstring_sem_o_prefixo(self):
        self.assertEqual(self.doc("a.py", '"""Forge: faz a | b.\n\nResto."""\n'), "faz a \\| b.")
        self.assertEqual(self.doc("forge-x", '#!/usr/bin/env python3\n# comentário\n"""Faz x."""\n'), "Faz x.")
        self.assertEqual(self.doc("b.py", "# só comentário\nx = 1\n"), "—")

    def test_shell_pelo_primeiro_comentario_depois_do_shebang(self):
        self.assertEqual(self.doc("s", "#!/usr/bin/env bash\n# shellcheck disable=SC2034\n# Forge: faz s.\n# mais\n"),
                         "faz s.")
        self.assertEqual(self.doc("t", "#!/usr/bin/env bash\nset -e\n# depois do código\n"), "—")

    def test_sem_shebang_nem_python_fica_sem_doc(self):
        self.assertEqual(self.doc("c.json", '{\n# não é comentário\n}\n'), "—")

    def test_texto_longo_e_cortado(self):
        doc = self.doc("l.py", '"""' + "x" * 200 + '"""\n')
        self.assertEqual(doc, "x" * self.indice.MAXIMO_DO_TEXTO + "…")
        self.assertEqual(self.doc("m.py", '"""' + "y" * self.indice.MAXIMO_DO_TEXTO + '"""\n'),
                         "y" * self.indice.MAXIMO_DO_TEXTO)


class SoNomeEDoc(unittest.TestCase):
    """Review A1 de v0478: o índice não traz o que muda com teste de outra trilha (coluna de testes e contagem)."""

    def setUp(self):
        self.indice = carregar()

    def test_tabela_so_com_arquivo_e_doc_e_sem_contagem(self):
        texto = self.indice.gerar(RAIZ, ["bin/forge-testes", "scripts/indice-forge.py"])
        self.assertEqual(texto.count("| Arquivo | O que faz |\n| --- | --- |\n"), 3)
        self.assertNotIn("Testes |", texto)
        self.assertNotIn("Os 2 arquivos", texto)
        self.assertIn("bin/forge-testes --listar <arquivo>", texto)

    def test_teste_novo_nao_muda_o_indice(self):
        """Um módulo de teste a mais no plano não pode mudar o texto: só o arquivo e a doc contam."""
        antes = self.indice.gerar(RAIZ, ["bin/forge-testes"])
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            for caminho in ("bin/forge-testes", "tests/test_forge_testes_outro.py"):
                (raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
            (raiz / "bin" / "forge-testes").write_bytes((RAIZ / "bin" / "forge-testes").read_bytes())
            (raiz / "tests" / "test_forge_testes_outro.py").write_text("# bin/forge-testes\n", encoding="utf-8")
            self.assertEqual(self.indice.gerar(raiz, ["bin/forge-testes"]), antes)

    def test_o_plano_dirigido_das_pastas_roda_o_indice(self):
        """Review A2 de v0478: o índice vencido aparece no plano dirigido de bin/, hooks/ e scripts/, não só no CI."""
        # o caminho de fora das pastas vai partido: inteiro, o teste o leria (arquivo lido) e o plano dele teria de trazê-lo
        casos = {"bin/forge-status": True, "bin/forge_meta.py": True, "hooks/_comum.py": True, "hooks/hooks.json": True,
                 "scripts/indice-forge.py": True, "scripts/validar-plugin.sh": True, "agents/" + "qa-engineer.md": False}
        for caminho, entra in casos.items():
            with self.subTest(caminho=caminho):
                r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-testes"), "--listar", caminho],
                                   capture_output=True, text=True, env=ambiente_limpo(), cwd=RAIZ)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("forge-testes: dirigido (", r.stdout)
                self.assertEqual("test_indice_forge" in r.stdout, entra, r.stdout)

    def test_raiz_sem_o_teste_do_indice_segue_dirigida_sem_ele(self):
        """Raiz sem tests/test_indice_forge.py (projeto ou raiz de teste): o plano não pede o módulo que falta."""
        carregador = importlib.machinery.SourceFileLoader("forge_testes_a2", str(RAIZ / "bin" / "forge-testes"))
        spec = importlib.util.spec_from_loader(carregador.name, carregador)
        testes = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(testes)
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            for caminho in ("bin/forge-xyz", "tests/test_forge_xyz.py", "tests/test_forge.py"):
                (raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
                (raiz / caminho).write_text("x = 1\n", encoding="utf-8")
            self.assertEqual(testes.planejar(["bin/forge-xyz"], raiz), ("dirigido", ["test_forge", "test_forge_xyz"]))
            (raiz / "tests" / "test_indice_forge.py").write_text("x = 1\n", encoding="utf-8")
            self.assertEqual(testes.planejar(["bin/forge-xyz"], raiz),
                             ("dirigido", ["test_forge", "test_forge_xyz", "test_indice_forge"]))


class Arquivos(unittest.TestCase):
    def setUp(self):
        self.indice = carregar()
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        env = ambiente_limpo()
        subprocess.run(["git", "init", "-q", str(self.raiz)], check=True, env=env)
        for caminho in ("bin/forge-a", "hooks/b.py", "scripts/c.sh", "scripts/sub/d.py", "tests/e.py", "f.py"):
            (self.raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
            (self.raiz / caminho).write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.raiz), "add", "."], check=True, env=env)
        (self.raiz / "bin" / "nao-versionado").write_text("x\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_so_versionados_do_primeiro_nivel_das_pastas(self):
        self.assertEqual(self.indice.arquivos(self.raiz), ["bin/forge-a", "hooks/b.py", "scripts/c.sh"])

    def test_git_dir_herdado_nao_desvia_a_leitura(self):
        with mock.patch.dict(os.environ, {"GIT_DIR": str(self.raiz / "nao-existe")}):
            self.assertEqual(self.indice.arquivos(self.raiz), ["bin/forge-a", "hooks/b.py", "scripts/c.sh"])


if __name__ == "__main__":
    unittest.main()
