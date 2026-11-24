"""ENVIO-LEVE (decisão do dono, 2026-11-11; diretriz 15): o pre-push do Forge, sem opt-in, não roda teste nenhum (nem os
afetados, nem a suíte, nem toma a trava): ficam as checagens baratas (sintaxe) e os bloqueios de branch protegida; o CI do
PR é o portão.

Cada teste roda o hook de verdade num repositório descartável cujo teste, se rodasse, deixaria a marca `rodou`. Classe do
defeito: o envio voltar a rodar teste local (marca presente, trava criada) ou o bloqueio sumir junto com os testes.
Variantes: teste quebrado e envio verde (nada roda), trava ausente, linha de duração `plano=leve`, sintaxe quebrada barra,
branch protegida barra (main, homolog, develop), segredo no delta barra, envio não fast-forward barra, opt-in `afetados`
ainda roda, valor inválido do opt-in recusado, suíte inteira (opt-in `1`) com processo morto por sinal sem prova.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})
ZERO = "0" * 40
TOKEN = "ghp" + "_" + "Ab3" * 8  # montado aqui para a própria varredura do Forge não achar este arquivo
# Varredura mínima no lugar do script real (que o test_pre_push_segredo exercita): aqui só importa que o envio leve a chame
# e barre com o que ela acusar. Recebe a base e a ponta, como o script do CI, e imprime arquivo:linha, nunca o valor.
VARREDURA = ("# forge:ponta\nachou=0\nfor f in $(git diff --no-color --name-only \"$1\" \"$2\"); do\n"
             "  for n in $(git show \"$2:$f\" | grep -n 'gh''p_' | cut -d: -f1); do echo \"segredo em $f:$n\"; achou=1; done\n"
             "done\nexit \"$achou\"\n")
TESTE_QUE_MARCA = ("import unittest, pathlib\nclass T(unittest.TestCase):\n    def test_a(self):\n"
                   "        pathlib.Path('rodou').write_text('sim')\n        self.fail('de proposito')\n")


class EnvioLeve(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        self.repo = base / "repo"
        (self.repo / "tests").mkdir(parents=True)
        (self.repo / "bin").mkdir()
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "verificar-contribuicao.sh").write_text(VARREDURA)  # o hook lê o script da base
        for nome in ("forge-testes", "forge_apoio_testes.py"):  # o opt-in `afetados` precisa da ferramenta na árvore
            shutil.copy(RAIZ / "bin" / nome, self.repo / "bin" / nome)
        (self.repo / ".gitignore").write_text("rodou\n__pycache__/\n")
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(base / "home"), FORGE_TRAVA_ESPERA="5")
        self.git("init", "-q", "-b", "melhoria/x")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.commit("base", **{"tests/test_a.py": TESTE_QUE_MARCA})
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, msg, **arquivos):
        for nome, texto in arquivos.items():
            alvo = self.repo / nome
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def roda(self, destino="melhoria/x", remoto=ZERO, **extra):
        (self.repo / "rodou").unlink(missing_ok=True)
        sha = self.git("rev-parse", "HEAD")
        r = subprocess.run([str(HOOK), "origin", "u"], cwd=self.repo, env=dict(self.env, **extra), capture_output=True,
                           text=True, timeout=120, input=f"refs/heads/x {sha} refs/heads/{destino} {remoto}\n")
        return r.returncode, (self.repo / "rodou").exists(), r.stderr

    def test_envio_sem_opt_in_nao_roda_teste_nem_toma_a_trava(self):
        self.commit("toca codigo", **{"bin/ferramenta": "x = 1\n", "tests/test_b.py": TESTE_QUE_MARCA})
        codigo, rodou, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertFalse(rodou, "o envio leve não roda teste")
        self.assertIn("envio leve", erro)
        self.assertNotIn("rodando só os testes", erro)
        self.assertNotIn("vez ", erro)
        self.assertEqual(list(self.run_dir.rglob("*.lock")), [], "o envio leve não toma a trava de suíte")
        self.assertIn("plano=leve rc=0", erro)

    def test_sintaxe_quebrada_ainda_barra_nas_baratas(self):
        self.commit("quebra", **{"bin/ferramenta.py": "def f(:\n"})
        codigo, rodou, erro = self.roda()
        self.assertEqual(codigo, 1, erro)
        self.assertFalse(rodou)
        self.assertIn("erro de sintaxe Python em bin/ferramenta.py", erro)
        self.assertNotIn("envio leve", erro)

    def test_branch_protegida_continua_barrada(self):
        self.commit("toca codigo", **{"bin/ferramenta": "x = 1\n"})
        for destino in ("main", "homolog", "develop"):
            with self.subTest(destino):
                codigo, rodou, erro = self.roda(destino=destino)
                self.assertEqual(codigo, 1, erro)
                self.assertFalse(rodou)
                self.assertNotIn("envio leve", erro)

    def test_segredo_no_delta_ainda_barra_sem_imprimir_o_valor(self):
        # A branch neutraliza o próprio script de segredo: só a varredura da base (segredo_no_delta) pode barrar.
        self.commit("token", **{"a.md": f"t = {TOKEN}\n", "scripts/verificar-contribuicao.sh": "#!/bin/bash\nexit 0\n"})
        codigo, rodou, erro = self.roda()
        self.assertEqual((codigo, rodou), (1, False), erro)
        self.assertIn("varredura de segredo", erro)
        self.assertIn("a.md:1", erro)
        self.assertNotIn(TOKEN, erro, "o valor não pode sair")
        self.assertNotIn("envio leve", erro)

    def test_envio_nao_fast_forward_ainda_barra(self):
        base = self.git("rev-parse", "HEAD")
        remoto = self.commit("no remoto", **{"bin/ferramenta": "x = 1\n"})
        self.git("reset", "-q", "--hard", base)
        self.commit("reescrito", **{"bin/ferramenta": "x = 2\n"})
        codigo, rodou, erro = self.roda(remoto=remoto)
        self.assertEqual((codigo, rodou), (1, False), erro)
        self.assertIn("envio não fast-forward para melhoria/x", erro)
        self.assertNotIn("envio leve", erro)

    def test_opt_in_afetados_ainda_roda_os_testes(self):
        self.commit("toca o teste", **{"tests/test_a.py": TESTE_QUE_MARCA + "# x\n"})
        codigo, rodou, erro = self.roda(FORGE_PREPUSH_SUITE="afetados")
        self.assertIn("rodando só os testes afetados", erro)
        self.assertNotIn("envio leve", erro)
        self.assertEqual((codigo, rodou), (1, True), erro)  # o teste falha de propósito: com opt-in o envio é barrado

    def test_modo_suite_a_mao_roda_a_suite_mesmo_sem_opt_in(self):
        (self.repo / "rodou").unlink(missing_ok=True)
        r = subprocess.run([str(HOOK), "--suite"], cwd=self.repo, env=self.env, capture_output=True, text=True,
                           timeout=120, stdin=subprocess.DEVNULL)
        self.assertTrue((self.repo / "rodou").exists(), "o --suite à mão não é envio: roda a suíte")
        self.assertEqual(r.returncode, 1, r.stderr)  # o teste falha de propósito
        self.assertNotIn("envio leve", r.stderr)

    def test_suite_inteira_com_processo_morto_nao_anota_prova_nem_carimbo(self):  # E137.4: o OOM killer no opt-in `1`
        shutil.copy(RAIZ / "scripts" / "suite-paralela.py", self.repo / "scripts" / "suite-paralela.py")
        for apoio in ("guarda_git.py", "ambiente_git.py"):  # apoios que a suíte paralela importa
            shutil.copy(RAIZ / "tests" / apoio, self.repo / "tests" / apoio)
        morto = "import os, signal, unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        os.kill(os.getpid(), signal.SIGKILL)\n"
        self.commit("suite com teste que morre", **{"tests/test_a.py": morto})
        codigo, _, erro = self.roda(FORGE_PREPUSH_SUITE="1")
        self.assertEqual(codigo, 1, erro)
        self.assertIn("morto pelo sinal 9", erro)
        self.assertIn("testes do Forge falharam", erro)
        self.assertNotIn("envio leve", erro)
        self.assertEqual(list(self.run_dir.rglob("*.verde")), [], "suíte morta anotou a prova de árvore verde")
        self.assertFalse((self.repo / ".git" / "forge-suite-verde").exists(), "suíte morta gravou o carimbo K6")

    def test_valor_invalido_do_opt_in_e_recusado(self):
        codigo, rodou, erro = self.roda(FORGE_PREPUSH_SUITE="sim")
        self.assertEqual((codigo, rodou), (1, False))
        self.assertIn("FORGE_PREPUSH_SUITE vale 0", erro)


# Índice falso no lugar de scripts/indice-fixtures.py: grava a marca `indice-chamado` e sai com o código de INDICE_RC (o
# índice de verdade lê o corpus inteiro; aqui só importa o que o hook faz com cada saída).
INDICE_FALSO = ("import os, pathlib, sys\npathlib.Path('indice-chamado').write_text(' '.join(sys.argv[1:]))\n"
                "print('docs/hooks-fixtures.md: desatualizado; rode scripts/indice-fixtures.py')\n"
                "sys.exit(int(os.environ.get('INDICE_RC', '0')))\n")
PULADO = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.skipTest('depois')\n"
VERDE = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n"


class IndiceEPulos(EnvioLeve):
    """PREPUSH-INDICE-E-PULOS (v0478 E152.2): o envio leve, sem teste nenhum, roda o `scripts/indice-fixtures.py --conferir`
    quando o diff toca o corpus de fixtures, o gerador, o índice ou a config, e conta os pulos (skip, skipIf, skipUnless,
    expectedFailure, skipTest) nos testes tocados, na âncora e no HEAD, pela conta da catraca. Índice desatualizado ou
    pulo novo reprova; ferramenta que não roda é aviso (o CI confere). Vermelho até o dono aplicar o patch do hook."""

    def setUp(self):
        super().setUp()
        (self.repo / ".gitignore").write_text("rodou\nindice-chamado\n__pycache__/\n")
        apoios = {f"tests/{n}": (RAIZ / "tests" / n).read_text(encoding="utf-8") for n in ("catraca.py", "neutralidade.py")}
        self.commit("apoios", **apoios, **{"scripts/indice-fixtures.py": INDICE_FALSO, "tests/test_c.py": VERDE})
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.marca = self.repo / "indice-chamado"

    def test_indice_desatualizado_reprova_o_envio_leve(self):
        self.commit("fixture nova", **{"tests/hooks/caso/nova.json": "{}\n"})
        codigo, rodou, erro = self.roda(INDICE_RC="1")
        self.assertEqual((codigo, rodou), (1, False), erro)
        self.assertEqual(self.marca.read_text(), "--conferir", "o hook confere o índice, não o regrava")
        self.assertIn("docs/hooks-fixtures.md desatualizado", erro)
        self.assertIn("checagens baratas reprovadas", erro)
        self.assertNotIn("envio leve", erro)

    def test_cada_caminho_do_corpus_dispara_o_indice(self):
        for caminho in ("tests/hooks/caso/x.json", "scripts/indice-fixtures.py", "docs/hooks-fixtures.md", "tests/config.json"):
            with self.subTest(caminho):
                self.marca.unlink(missing_ok=True)
                texto = INDICE_FALSO + "# x\n" if caminho == "scripts/indice-fixtures.py" else "{}\n"
                self.commit(f"toca {caminho}", **{caminho: texto})
                codigo, _, erro = self.roda(INDICE_RC="1")
                self.assertEqual(codigo, 1, erro)
                self.assertTrue(self.marca.exists(), f"{caminho} no diff não chamou o índice")
                self.git("reset", "-q", "--hard", "refs/remotes/origin/develop")

    def test_indice_em_dia_segue_leve(self):
        self.commit("fixture nova", **{"tests/hooks/caso/nova.json": "{}\n"})
        codigo, rodou, erro = self.roda(INDICE_RC="0")
        self.assertEqual((codigo, rodou), (0, False), erro)
        self.assertTrue(self.marca.exists())
        self.assertIn("plano=leve rc=0", erro)

    def test_diff_fora_do_corpus_nao_chama_o_indice(self):
        self.commit("toca codigo", **{"bin/ferramenta": "x = 1\n"})
        codigo, _, erro = self.roda(INDICE_RC="1")
        self.assertEqual(codigo, 0, erro)
        self.assertFalse(self.marca.exists(), "o índice só roda com o corpus, o gerador, o índice ou a config no diff")

    def test_indice_que_nao_roda_e_so_aviso(self):
        self.commit("fixture nova", **{"tests/hooks/caso/nova.json": "{}\n"})
        codigo, _, erro = self.roda(INDICE_RC="2")
        self.assertEqual(codigo, 0, erro)
        self.assertIn("aviso: scripts/indice-fixtures.py --conferir não conferiu o índice (saída 2)", erro)

    def test_indice_que_e_link_nao_roda(self):  # a metade `! -L` da guarda
        (self.repo / "scripts" / "indice-real.py").write_text(INDICE_FALSO)
        (self.repo / "scripts" / "indice-fixtures.py").unlink()
        (self.repo / "scripts" / "indice-fixtures.py").symlink_to("indice-real.py")
        self.commit("indice vira link", **{"tests/hooks/caso/nova.json": "{}\n"})
        codigo, _, erro = self.roda(INDICE_RC="1")
        self.assertEqual(codigo, 0, erro)
        self.assertFalse(self.marca.exists(), "o hook não segue link no lugar do índice")

    def test_skip_novo_em_teste_tocado_reprova(self):
        self.commit("pula", **{"tests/test_c.py": PULADO})
        codigo, rodou, erro = self.roda()
        self.assertEqual((codigo, rodou), (1, False), erro)
        self.assertIn("subiram de 0 para 1", erro)
        self.assertIn("teste pulado novo em tests/", erro)
        self.assertNotIn("envio leve", erro)

    def test_skip_em_teste_novo_tambem_reprova(self):  # o arquivo não existe na âncora: conta 0 antes
        self.commit("teste novo ja pulado", **{"tests/test_d.py": PULADO})
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1, erro)
        self.assertIn("teste pulado novo em tests/", erro)

    def test_teste_tocado_sem_pulo_novo_segue_leve(self):
        self.commit("pulo na base", **{"tests/test_c.py": PULADO})
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.commit("mexe sem pular mais", **{"tests/test_c.py": PULADO + "# x\n"})
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("teste pulado", erro)
        self.assertIn("plano=leve rc=0", erro)

    def test_pulo_que_sai_nao_reprova(self):
        self.commit("pulo na base", **{"tests/test_c.py": PULADO})
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.commit("conserta", **{"tests/test_c.py": VERDE})
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)

    def test_sem_a_base_nao_conta(self):  # sem a base nada a comparar (o CI conta); tirar o `-n "$base_dev"` é equivalente: o merge-base falha
        self.commit("pula", **{"tests/test_c.py": PULADO})
        self.git("update-ref", "-d", "refs/remotes/origin/develop")
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("teste pulado", erro)

    def test_catraca_ilegivel_e_so_aviso(self):
        self.commit("pula e quebra a catraca", **{"tests/test_c.py": PULADO, "tests/neutralidade.py": "raise SystemExit(5)\n"})
        codigo, _, erro = self.roda()
        self.assertNotIn("teste pulado novo", erro)
        self.assertIn("aviso: a contagem de testes pulados não rodou", erro)
        self.assertEqual(codigo, 0, erro)


if __name__ == "__main__":
    unittest.main()
