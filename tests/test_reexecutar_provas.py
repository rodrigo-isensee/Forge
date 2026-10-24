"""Arquivo de provas na branch (EST-030-L2, M15): formato do modelo e texto da regra que o descreve."""
import contextlib
import importlib.util
import io
import itertools
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
DOCS = AQUI.parent / "docs"


class ModeloDeProvas(unittest.TestCase):
    def rodar_copia(self, extra=()):
        """Copia o modelo para docs/provas/p.md num git temporário e roda o próprio script sobre a cópia."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            env = sem_manutencao({**os.environ, "HOME": tmp})
            (raiz / "tests").mkdir()
            (raiz / "tests" / "__init__.py").write_text("")
            (raiz / "tests" / "test_exemplo.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): pass\n")
            (raiz / "docs" / "provas").mkdir(parents=True)
            modelo = (DOCS / "provas" / "_modelo.md").read_text(encoding="utf-8")
            (raiz / "docs" / "provas" / "p.md").write_text(modelo + "".join(l + "\n" for l in extra), encoding="utf-8")
            git = lambda *a: subprocess.run(["git", "-C", tmp, *a], check=True, capture_output=True, env=env)
            git("init", "-q")
            git("add", "-A")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
            r = subprocess.run([sys.executable, str(AQUI.parent / "scripts" / "reexecutar-provas.py"), "--raiz", tmp, "docs/provas/p.md"],
                               capture_output=True, text=True, env={**env, "PYTHONDONTWRITEBYTECODE": "1"})
            return r.returncode, r.stdout + r.stderr

    def test_modelo_copiado_passa(self):
        rc, saida = self.rodar_copia()
        self.assertEqual(rc, 0, saida)
        self.assertIn("ok docs/provas/p.md:7 PQ-1", saida)
        self.assertIn("ok docs/provas/p.md:8 PQ-2", saida)
        self.assertIn("reexecutar-provas: 2 prova(s) cmd conferida(s)", saida)

    def test_prosa_antiga_do_formato_na_copia_reprova(self):
        rc, saida = self.rodar_copia(["`- PQ-<n> (cmd): `<comando>` · espera: <espera>`"])
        self.assertEqual(rc, 1, saida)
        self.assertIn("p.md:9: linha fora do formato do arquivo de provas", saida)

    def test_regra_descreve_o_arquivo_a_lista_permitida_e_a_falha_fechada(self):
        regra = (DOCS / "regras" / "R-PROVA.md").read_text(encoding="utf-8")
        for trecho in ("docs/provas/<pedido>.md", "scripts/reexecutar-provas.py", "sem shell", "lista permitida",
                       "falha fechada", "pull_request_target"):
            self.assertIn(trecho, regra)


spec = importlib.util.spec_from_file_location("reexecutar_provas", AQUI.parent / "scripts" / "reexecutar-provas.py")
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)


class Lista(unittest.TestCase):
    def test_permitidos(self):
        for cmd in ("python3 -m unittest tests.test_x", "python3 -m unittest -v a.b c.d", "git rev-parse --verify HEAD",
                    "git diff --numstat abc...HEAD", "git ls-files -- docs"):
            self.assertIsNone(rp.comando_permitido(cmd.split()), cmd)

    def test_opcao_de_git_fora_da_lista_cai_pelo_filtro_e_nao_pelo_prefixo(self):
        for cmd in ("git diff --numstat --output=x", "git diff --numstat --no-index a b", "git ls-files --ext-diff",
                    "git diff --name-only --textconv"):
            self.assertIn("opção de git", rp.comando_permitido(cmd.split()) or "", cmd)

    def test_recusados_por_falha_fechada(self):
        for cmd in ("rm -rf x", "python3 -c print(1)", "python3 -m unittest discover -s tests", "python3 -m unittest",
                    "python3 -m unittest discover", "python3 -m unittest discover tests", "python3 -m unittest tests.x discover",
                    "python3 -m unittest -v discover", "python3 -m unittest DISCOVER", "python3 -m unittest Discover -v",
                    "python3 -m unittest tests.x DiScOvEr", "python3 -m unittest ｄｉｓｃｏｖｅｒ", "python3 -m unittest dis\u200bcover",
                    "git diff --numstat /etc/hostname /dev/null", "git diff --numstat ../fora", "git diff --numstat a/../../b",
                    "git diff --numstat ~/x", "git ls-files -- /etc", "git diff --name-only ..",
                    "python3 -m http.server", "python3 scripts/x.py", "git push origin x", "git diff --output=x",
                    "git diff --no-index a b", "git log", "bash -c ls", "curl http://x", "python3 -m unittest a;b",
                    "git rev-parse $(id)"):
            self.assertIsNotNone(rp.comando_permitido(cmd.split()), cmd)


class Espera(unittest.TestCase):
    def test_cada_forma(self):
        casos = [("rc=0", "x\n", 0, None), ("rc=0", "", 1, "rc=0"), ("rc=0 e contém 'ab'", "xaby", 0, None),
                 ("rc=0 e contém 'zz'", "xaby", 0, "contém 'zz'"), ("rc=0 e igual 'ok'", "ok\n", 0, None), ("rc=0 e igual 'ok'", "ok2", 0, "igual 'ok'"),
                 ("rc=0 e linhas=2", "a\nb\n", 0, None), ("rc=0 e linhas=2", "a\n", 0, "linhas=2"), ("rc=0 e linhas>=2", "a\nb\nc", 0, None),
                 ("rc=0 e linhas>=2", "a", 0, "linhas>=2"), ("rc=0 e linhas=1", "a", 0, None), ("rc=0 e linhas=1", "a\nb", 0, "linhas=1")]
        for espera, saida, rc, esperado in casos:
            self.assertEqual(rp.avaliar(espera, saida, rc), esperado, (espera, saida, rc))

    def test_espera_ilegivel_falha_fechada(self):
        with self.assertRaises(rp.Falha):
            rp.avaliar("talvez", "x", 0)

    def test_espera_sem_rc0_falha_fechada_mesmo_com_saida_que_confere(self):
        for espera in ("linhas>=1", "contém 'x'", "igual 'x'", "linhas=1"):
            with self.assertRaises(rp.Falha, msg=espera):
                rp.avaliar(espera, "x", 128)


class Execucao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / "docs" / "provas").mkdir(parents=True)
        (self.raiz / "tests").mkdir()
        (self.raiz / "tests" / "t_ok.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): pass\n")
        (self.raiz / "tests" / "t_ruim.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): self.fail('x')\n")

    def rodar(self, linhas, nome="p.md"):
        (self.raiz / "docs" / "provas" / nome).write_text("\n".join(linhas) + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(AQUI.parent / "scripts" / "reexecutar-provas.py"), "--raiz", str(self.raiz),
                            f"docs/provas/{nome}"], capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode, r.stdout + r.stderr

    def test_prova_que_confere_passa_com_titulo_proposito_e_linha_vazia(self):
        rc, saida = self.rodar(["# Provas do pedido X", "", "Propósito: provas do pedido.", "## Provas",
                                "- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0"])
        self.assertEqual(rc, 0, saida)
        self.assertIn("ok docs/provas/p.md:5 PQ-1", saida)
        self.assertIn("1 prova(s) cmd", saida)

    def test_para_na_primeira_divergencia(self):
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest tests.t_ruim` · espera: rc=0",
                                "- PQ-2 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("PQ-1", saida)
        self.assertNotIn("ok docs/provas/p.md:2", saida)

    def test_comando_fora_da_lista_e_recusado_sem_executar(self):
        marca = self.raiz / "marca"
        rc, saida = self.rodar([f"- PQ-1 (cmd): `touch {marca}` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("recusado", saida)
        self.assertFalse(marca.exists())

    def test_metacaractere_e_recusado_antes_de_executar(self):
        marca = self.raiz / "marca"
        rc, saida = self.rodar([f"- PQ-1 (cmd): `git rev-parse HEAD; touch {marca}` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("recusado", saida)
        self.assertFalse(marca.exists())

    def test_comando_permitido_chega_ao_subprocess_como_lista_e_sem_shell(self):
        (self.raiz / "docs" / "provas" / "p.md").write_text("- PQ-1 (cmd): `python3 -m unittest tests.t_ok -v` · espera: rc=0\n", encoding="utf-8")
        chamada = {}

        def falso(argv, **kwargs):
            chamada.update(argv=argv, **kwargs)
            return subprocess.CompletedProcess(argv, 0, "", "")
        with mock.patch.object(rp.subprocess, "run", falso):
            self.assertEqual(rp.reexecutar("docs/provas/p.md", self.raiz, 5), 1)
        self.assertEqual(chamada["argv"], ["python3", "-m", "unittest", "tests.t_ok", "-v"])
        self.assertIs(chamada["shell"], False)

    def test_linha_que_parece_cmd_e_nao_casa_o_formato_falha_fechada(self):
        for linha in (" - PQ-2 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-3 (CMD): `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- **PQ-4** (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "* PQ-5 (Cmd): `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-6 (cmd): python3 -m unittest tests.t_ok · espera: rc=0"):
            rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", linha])
            self.assertNotEqual(rc, 0, linha)
            self.assertIn("fora do formato", saida, linha)

    def test_git_com_caminho_fora_da_arvore_e_recusado_e_nao_le_o_arquivo(self):
        subprocess.run(["git", "init", "-q", str(self.raiz)], check=True, env=sem_manutencao({**os.environ, "HOME": self.tmp.name}))
        for caminho in ("/etc/hostname", "../fora", "docs/../../fora", "~/x"):
            rc, saida = self.rodar([f"- PQ-1 (cmd): `git diff --numstat {caminho} /dev/null` · espera: rc=0 e contém 'hostname'"])
            self.assertEqual(rc, 1, caminho)
            self.assertIn("recusado", saida, caminho)

    def test_git_sem_repositorio_na_raiz_e_recusado(self):
        rc, saida = self.rodar(["- PQ-1 (cmd): `git ls-files` · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("sem repositório", saida)

    def test_git_dentro_da_arvore_passa(self):
        subprocess.run(["git", "init", "-q", str(self.raiz)], check=True, env=sem_manutencao({**os.environ, "HOME": self.tmp.name}))
        rc, saida = self.rodar(["- PQ-1 (cmd): `git ls-files -- docs` · espera: rc=0"])
        self.assertEqual(rc, 0, saida)

    def test_comando_sem_crases_e_recusado(self):
        rc, saida = self.rodar(["- PQ-1 (cmd): python3 -m unittest tests.t_ok · espera: rc=0"])
        self.assertEqual(rc, 1)
        self.assertIn("fora do formato", saida)

    def test_espera_que_sempre_passa_e_recusada(self):
        for espera in ("linhas>=0", "contém ''", "rc=0 e linhas>=0"):
            rc, saida = self.rodar([f"- PQ-1 (cmd): `python3 -m unittest tests.t_ruim` · espera: {espera}"])
            self.assertEqual(rc, 1, espera)
            self.assertIn("p.md:1: PQ-1: espera que sempre passa", saida, espera)

    def test_espera_sem_rc0_e_recusada_com_arquivo_linha_e_sem_rodar_o_comando(self):
        marca = self.raiz / "marca"
        (self.raiz / "tests" / "t_marca.py").write_text(f"import unittest\nclass T(unittest.TestCase):\n    def test(self): open({str(marca)!r}, 'w')\n")
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-2 (cmd): `python3 -m unittest tests.t_marca` · espera: linhas>=1",
                                "- PQ-3 (cmd): `python3 -m unittest tests.t_ok` · espera: talvez"])
        self.assertEqual(rc, 1)
        self.assertIn("p.md:2: PQ-2: espera sem rc=0", saida)
        self.assertFalse(marca.exists())
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: talvez"])
        self.assertIn("p.md:1: PQ-1: espera ilegível", saida)

    def test_variantes_de_grafia_da_linha_cmd_falham_fechadas(self):
        for linha in ("- PQ 1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ\u20111 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-1 (cmd ): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-1 ( cmd ): `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-1 (cmd\u200b): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-1 （cmd）: `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-1 (cmd) `python3 -m unittest tests.t_ok` · espera: rc=0", "-  PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-1 (cmd): `python3 -m unittest tests.t_ok`"):
            rc, saida = self.rodar([linha])
            self.assertNotEqual(rc, 0, linha)
            self.assertIn("p.md:1: linha fora do formato do arquivo de provas", saida, linha)
            self.assertNotIn("0 prova(s)", saida, linha)

    def test_arquivo_de_provas_inexistente_sai_com_mensagem_e_sem_traceback(self):
        r = subprocess.run([sys.executable, str(AQUI.parent / "scripts" / "reexecutar-provas.py"), "--raiz", str(self.raiz), "docs/provas/nada.md"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("reexecutar-provas: docs/provas/nada.md: não foi possível ler", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_linha_cmd_fora_do_formato_e_modelo_e_fora_de_provas_falham(self):
        self.assertEqual(self.rodar(["- PQ-1 (cmd): python3 -m unittest tests.t_ok"])[0], 1)
        self.assertEqual(self.rodar(["- PQ-1 (cmd): `git rev-parse HEAD` · espera: talvez"])[0], 1)
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0"], "_modelo.md")
        self.assertEqual(rc, 1)
        self.assertIn("é o modelo", saida)
        with self.assertRaises(rp.Falha):
            rp.reexecutar("../fora.md", self.raiz, 5)

    def test_ambiente_minimo_e_prazo_chegam_ao_subprocess(self):
        (self.raiz / "docs" / "provas" / "p.md").write_text("- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0\n", encoding="utf-8")
        chamada = {}

        def falso(argv, **kwargs):
            chamada.update(kwargs)
            return subprocess.CompletedProcess(argv, 0, "", "")
        with mock.patch.object(rp.subprocess, "run", falso), mock.patch.dict(os.environ, {"HOME": "/h", "GITHUB_TOKEN": "s"}):
            rp.reexecutar("docs/provas/p.md", self.raiz, 7)
        self.assertEqual(set(chamada["env"]), {"PATH", "LC_ALL", "PYTHONDONTWRITEBYTECODE"})
        self.assertEqual(chamada["timeout"], 7)
        self.assertEqual(chamada["cwd"], self.raiz)

    def test_passou_do_prazo_reprova_com_arquivo_linha(self):
        (self.raiz / "docs" / "provas" / "p.md").write_text("- PQ-1 (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0\n", encoding="utf-8")

        def estoura(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, 1)
        with mock.patch.object(rp.subprocess, "run", estoura), self.assertRaisesRegex(rp.Falha, r"p\.md:1: PQ-1: passou de 3s"):
            rp.reexecutar("docs/provas/p.md", self.raiz, 3)

    def test_ambiente_sem_segredo(self):
        original = os.environ.get("GITHUB_TOKEN")
        os.environ["GITHUB_TOKEN"] = "segredo"
        self.addCleanup(lambda: os.environ.pop("GITHUB_TOKEN") if original is None else os.environ.update(GITHUB_TOKEN=original))
        (self.raiz / "tests" / "t_env.py").write_text("import os, unittest\nclass T(unittest.TestCase):\n    def test(self): assert 'GITHUB_TOKEN' not in os.environ\n")
        rc, saida = self.rodar(["- PQ-1 (cmd): `python3 -m unittest tests.t_env` · espera: rc=0"])
        self.assertEqual(rc, 0, saida)


class ListaPositivaDeLinhas(unittest.TestCase):
    """Classe "linha ou comando aceito por uma forma que o script não modela": toda linha é lida e só passa uma forma permitida."""
    BASE = [l for l in (DOCS / "provas" / "_modelo.md").read_text(encoding="utf-8").splitlines() if l]  # título, Propósito e as PQ
    VALIDA = next(l for l in BASE if l.startswith("- PQ-1 "))
    ALFABETO = [chr(c) for c in range(0x20, 0x7F)] + [" ", "‑", "​", "﻿", "́", *"сеаор", "ο", *"（）［］"]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / ".git").mkdir()  # o git não roda: subprocess.run é trocado por um que devolve rc=0
        falso = mock.patch.object(rp.subprocess, "run", lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "x\n", ""))
        falso.start()
        self.addCleanup(falso.stop)

    def executar(self, linhas):
        """O caminho do script depois da leitura do arquivo; devolve (rc, saída) como o main()."""
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            try:
                rp.executar("docs/provas/p.md", "\n".join(linhas) + "\n", self.raiz, 5)
                return 0, saida.getvalue()
            except rp.Falha as erro:
                return 1, saida.getvalue() + str(erro)

    def assert_toda_linha_lida(self, linhas):
        """Oráculo pela saída do script: rc=0 implica que toda linha não vazia é título, Propósito ou `ok <arquivo>:<N>`."""
        rc, saida = self.executar(linhas)
        if rc != 0:
            return
        for numero, linha in enumerate(linhas, 1):
            if linha and not linha.startswith(("# ", "## ", "Propósito: ")):
                self.assertIn(f"ok docs/provas/p.md:{numero} PQ-", saida, (linhas, numero))

    def variantes(self, linha):
        yield "  " + linha
        yield "**" + linha + "**"
        for i in range(len(linha) + 1):
            if i < len(linha):
                yield linha[:i] + linha[i + 1:]
            for c in self.ALFABETO:
                yield linha[:i] + c + linha[i:]
                if i < len(linha):
                    yield linha[:i] + c + linha[i + 1:]

    def test_propriedade_toda_linha_gerada_e_lida_sozinha_e_ao_lado_de_prova_valida(self):
        vistos = 0
        for linha in self.BASE:
            for variante in set(self.variantes(linha)):
                self.assert_toda_linha_lida([variante])
                self.assert_toda_linha_lida([self.VALIDA, variante])
                vistos += 1
        self.assertGreater(vistos, 80000)

    def test_grafias_dos_pareceres_reprovam_ao_lado_de_prova_valida(self):
        resto = " PQ-2: `python3 -m unittest tests.t_ok` · espera: rc=0"
        for linha in ("- PQ-2 [cmd]: `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-2 {cmd}: `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-2 (cmd: `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-2 cmd: `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-2 (сmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-2 (cmd́): `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-2: `python3 -m unittest tests.t_ok` · espera: rc=0", "[cmd]" + resto, "- PQ-2 cmd: `python3 -m unittest tests.t_ok` · espera: rc=0",
                      "- PQ-1 cmd: `python3 -m unittest tests.t_ok` · espera: rc=0", "- PQ-2 (cmd): `python3 -m unittest tests.t_ok` · еspera: rc=0",
                      "- PQ-٣ (cmd): `python3 -m unittest tests.t_ok` · espera: rc=0", "texto livre", "| tabela |", "### Outra seção",
                      "## Outra", "Propósito: - PQ-2 (cmd): `x` · espera: rc=0"):
            for linhas in ([linha], [self.VALIDA, linha]):
                rc, saida = self.executar(linhas)
                self.assertEqual(rc, 1, linhas)
                self.assertIn(f"p.md:{len(linhas)}: linha fora do formato do arquivo de provas", saida, linhas)

    def test_um_titulo_de_cada_e_um_proposito_no_maximo(self):
        for repetida in ("# Outro título", "## Provas", "Propósito: outro."):
            rc, saida = self.executar([*self.BASE, repetida])
            self.assertEqual(rc, 1, repetida)
            self.assertIn("p.md:6: linha fora do formato", saida, repetida)

    def test_arquivo_sem_prova_conferida_reprova(self):
        for linhas in (["# Provas do pedido X"], ["# Provas do pedido X", "", "## Provas"], [""], []):
            rc, saida = self.executar(linhas)
            self.assertEqual(rc, 1, linhas)
            self.assertIn("nenhuma prova cmd", saida, linhas)

    def test_linha_ruim_reprova_antes_de_executar_qualquer_prova(self):
        chamadas = []
        with mock.patch.object(rp.subprocess, "run", lambda argv, **kw: chamadas.append(argv)), self.assertRaises(rp.Falha):
            rp.executar("docs/provas/p.md", self.VALIDA + "\ntexto\n", self.raiz, 5)
        self.assertEqual(chamadas, [])


class UnittestComModulo(unittest.TestCase):
    OPCOES = ["-v", "-q", "--locals", "--durations 1", "-f", "-c", "-b", "-k x"]

    def test_propriedade_todo_subconjunto_de_opcoes_sem_modulo_e_recusado(self):
        for n in range(len(self.OPCOES) + 1):
            for opcoes in itertools.combinations(self.OPCOES, n):
                argv = ["python3", "-m", "unittest", *" ".join(opcoes).split()]
                self.assertIsNotNone(rp.comando_permitido(argv), argv)

    def test_propriedade_discover_em_toda_grafia_de_caixa_e_largura_e_recusado(self):
        largura = {c: (c, c.upper(), chr(ord(c) + 0xFEE0), chr(ord(c.upper()) + 0xFEE0)) for c in "discover"}
        subconjuntos = [list(o) for n in range(3) for o in itertools.combinations(["-v", "-q", "-b", "-f"], n)]
        for i, grafia in enumerate(itertools.product(*(largura[c] for c in "discover"))):
            for argv_resto in (["".join(grafia)], ["tests.t_x", "".join(grafia)]):
                argv = ["python3", "-m", "unittest", *subconjuntos[i % len(subconjuntos)], *argv_resto]
                self.assertIsNotNone(rp.comando_permitido(argv), argv)

    def test_propriedade_toda_lista_aceita_traz_um_nome_de_modulo(self):
        fichas = ["-v", "-q", "-b", "-f", "-k", "x", "a", "a.b", "tests.t_x", "discover", "a.discover", "a..b", ".a", "a.", "1.b"]
        aceitas = 0
        for n in range(1, 4):
            for resto in itertools.product(fichas, repeat=n):
                if rp.comando_permitido(["python3", "-m", "unittest", *resto]) is None:
                    aceitas += 1
                    modulos = [a for a in resto if not a.startswith("-")]
                    self.assertTrue(modulos and all("." in a and "" not in a.split(".") and not a[0].isdigit() for a in modulos), resto)
        self.assertGreater(aceitas, 50)

    def preparar(self, init=""):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name)
        (raiz / "docs" / "provas").mkdir(parents=True)
        (raiz / "tests").mkdir()
        (raiz / "tests" / "__init__.py").write_text(init)  # pacote regular: a descoberta do unittest entra em tests/
        (raiz / "tests" / "test_sentinela.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test(self): open('sentinela', 'w').close()\n")
        return raiz

    def rodar(self, raiz, comando):
        (raiz / "docs" / "provas" / "p.md").write_text(f"- PQ-1 (cmd): `{comando}` · espera: rc=0\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(AQUI.parent / "scripts" / "reexecutar-provas.py"), "--raiz", str(raiz), "docs/provas/p.md"],
                           capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode, r.stdout + r.stderr

    def test_efeito_real_unittest_so_com_opcoes_nao_roda_a_suite(self):
        for comando in ("python3 -m unittest -v", "python3 -m unittest -b", "python3 -m unittest -q -f"):
            raiz = self.preparar()
            rc, saida = self.rodar(raiz, comando)
            self.assertEqual(rc, 1, (comando, saida))
            self.assertFalse((raiz / "sentinela").exists(), comando)
        raiz = self.preparar()
        rc, saida = self.rodar(raiz, "python3 -m unittest tests.test_sentinela")
        self.assertEqual(rc, 0, saida)
        self.assertTrue((raiz / "sentinela").exists())  # a sonda está viva

    def test_s2_nome_de_pacote_com_load_tests_de_descoberta_e_recusado(self):
        init = ("import os\ndef load_tests(loader, tests, pattern):\n    aqui = os.path.dirname(__file__)\n"
                "    return loader.discover(aqui, top_level_dir=os.path.dirname(aqui))\n")
        raiz = self.preparar(init)
        rc, saida = self.rodar(raiz, "python3 -m unittest tests")
        self.assertEqual(rc, 1, saida)
        self.assertIn("recusado", saida)
        self.assertFalse((raiz / "sentinela").exists())
        r = subprocess.run([sys.executable, "-m", "unittest", "tests"], cwd=raiz, capture_output=True, text=True,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((raiz / "sentinela").exists())  # medido: o nome do pacote sozinho roda a descoberta do load_tests


class PassoDoCi(unittest.TestCase):
    CI = (AQUI.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    def passo(self):
        m = re.search(r"(?m)^      - name: Provas cmd do arquivo de provas.*?(?=^      - name: )", self.CI, re.S)
        self.assertIsNotNone(m)
        return m.group(0)

    def test_so_no_pull_request_sem_segredo_e_com_o_script_da_base(self):
        passo = self.passo()
        self.assertIn("github.event_name == 'pull_request'", passo)
        self.assertNotIn("pull_request_target", self.CI)
        self.assertNotIn("secrets.", passo)
        self.assertNotIn("GITHUB_TOKEN", passo)
        self.assertIn('git cat-file -e "$BASE:scripts/reexecutar-provas.py"', passo)
        self.assertIn('script="$RUNNER_TEMP/base/scripts/reexecutar-provas.py"', passo)

    def test_so_em_pr_para_a_develop_as_promocoes_ficam_fora(self):
        condicao = re.search(r"(?m)^        if: (.*)$", self.passo()).group(1)
        self.assertIn("github.event_name == 'pull_request'", condicao)
        self.assertIn("github.base_ref == 'develop'", condicao)

    def test_roda_no_sha_do_pr_sobre_o_arquivo_da_branch(self):
        passo = self.passo()
        self.assertIn('git worktree add --detach "$RUNNER_TEMP/pr" "$HEAD_SHA"', passo)
        self.assertIn("docs/provas/*.md", passo)
        self.assertIn('--raiz "$RUNNER_TEMP/pr"', passo)
        self.assertNotIn("${{", passo.split("run:")[1])  # entrada do evento só por env:, nunca no script

    def test_erro_do_git_diff_falha_fechado_a_lista_vem_de_variavel_sob_set_e(self):
        passo = self.passo()
        self.assertIn('lista=$(git diff', passo)
        self.assertNotIn("< <(git diff", passo)
        self.assertNotIn("set +e", passo)

    def test_glob_do_passo_nao_casa_subpasta_de_provas(self):
        pathspec = re.search(r"-- '(:\(glob\)docs/provas/\*\.md)'\)", self.passo()).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            env = sem_manutencao({**os.environ, "HOME": tmp})
            git = lambda *a: subprocess.run(["git", "-C", tmp, *a], check=True, capture_output=True, text=True, env=env).stdout
            git("init", "-q")
            for f in ("docs/provas/a.md", "docs/provas/sub/b.md"):
                (Path(tmp) / f).parent.mkdir(parents=True, exist_ok=True)
                (Path(tmp) / f).write_text("x\n")
            git("add", "-A")
            self.assertEqual(git("diff", "--name-only", "--cached", "--", pathspec).split(), ["docs/provas/a.md"])

    def test_passo_vem_antes_da_suite(self):
        self.assertLess(self.CI.index("Provas cmd do arquivo de provas"), self.CI.index("- name: Testes do Forge\n        if: ${{ !cancelled() && steps"))


if __name__ == "__main__":
    unittest.main()
