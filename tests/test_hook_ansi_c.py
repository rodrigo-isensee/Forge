"""HOOK-ANSI-C (cartão LEITOR-ANSI-C): o leitor dos hooks não junta `$'it\\'s'` com o `\\'` seguinte numa palavra só.

O bash lê `$'…'` até o `'` que fecha (`\\'` dentro é aspa literal); o `shlex` toma `\\'` por fecho de aspas simples e,
sozinho, liberaria `echo $'it\\'s'; cat .env\\'`. O leitor fiel (`palavras_do_texto`) sabe a diferença e `leituras`
falha fechado nela. Só arquivos de um diretório temporário: nenhum teste lê ou apaga `.env` ou `.git` reais."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_forge import ambiente_limpo  # noqa: E402
import test_hooks  # noqa: E402  (o módulo, não a classe Hooks: importada, o unittest a rodaria aqui também)
from test_hooks import FIXTURES, Fixture, modulos_dos_hooks  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / "hooks" / "conformidade.py"

SEM_PAR = "aspas sem par na leitura do hook"
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; _comum.forge_check().GIT_TIMEOUT_S = 120; "
            "_comum.PRAZO_DA_DECISAO_S = 120.0; sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")

CASO_ENV = "echo $'it\\'s'; cat .env\\'"
CASO_GIT = "echo $'it\\'s'; rm -rf .git \\'"
# A mesma linha como argumento entre aspas duplas (segurança A1): o shell de fora troca `\$` por `$` e `\\` por `\`, e o
# de dentro recebe `echo $'it\'s'; cat .env \'`; o hook relê o texto com `\$'…'`, que para ele é aspas simples.
ANINHADO_ENV = r'''bash -c "echo \$'it\\'s'; cat .env \\'"'''
ANINHADO_GIT = r'''bash -c "echo \$'it\\'s'; rm -rf .git \\'"'''
ANINHADO_EVAL = r'''eval "echo \$'it\\'s'; cat .env \\'"'''
ANINHADO_SH = r'''sh -c "echo \$'it\\'s'; cat .env \\'"'''


class HookAnsiC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = Path(tempfile.mkdtemp(prefix="forge-ansi-c-"))
        env = ambiente_limpo()
        for args in (("init", "-q", "-b", "develop"), ("config", "user.email", "t@example.com"),
                     ("config", "user.name", "Teste")):
            subprocess.run(["git", "-C", str(cls.raiz), *args], env=env, check=True, capture_output=True)
        (cls.raiz / ".forge").mkdir()
        (cls.raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        (cls.raiz / ".forge" / "config.json").write_text("{}", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.raiz, ignore_errors=True)

    def conformidade(self, comando):
        entrada = {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": "forge:node-backend",
                   "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"}
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOK.parent), str(HOOK)], input=json.dumps(entrada),
                              cwd=self.raiz, env=ambiente_limpo(), capture_output=True, text=True, timeout=120)

    def bash(self, comando, arquivos):
        """O bash real roda `comando` num diretório temporário só dele, com os `arquivos` {nome: conteúdo | None (pasta)}."""
        pasta = Path(tempfile.mkdtemp(prefix="forge-ansi-c-bash-"))
        self.addCleanup(shutil.rmtree, pasta, ignore_errors=True)
        for nome, conteudo in arquivos.items():
            if conteudo is None:
                (pasta / nome).mkdir()
            else:
                (pasta / nome).write_text(conteudo, encoding="utf-8")
        r = subprocess.run(["bash", "--norc", "--noprofile", "-c", comando], cwd=pasta, capture_output=True, text=True,
                           timeout=30)
        return r, pasta

    def test_o_bash_roda_o_segundo_comando(self):
        r, _ = self.bash(CASO_ENV, {".env'": "SEGREDO-FALSO\n"})
        self.assertEqual(r.stdout, "it's\nSEGREDO-FALSO\n")
        r, pasta = self.bash(CASO_GIT, {".git": None, "'": ""})
        self.assertEqual(r.stdout, "it's\n")
        self.assertFalse((pasta / ".git").exists(), "o bash separou o `;` e rodou o rm")

    def test_os_dois_casos_do_cartao_saem_2(self):
        for comando in (CASO_ENV, CASO_GIT):
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn(SEM_PAR, r.stderr)

    def test_a_aspa_escapada_mais_adiante_na_linha_tambem_falha_fechado(self):
        for comando in ("true && echo $'x\\'y' && cat .env\\'", "echo $'a\\\\b' $'it\\'s'; cat .env\\'",
                        "echo \"$(echo $'it\\'s'; cat .env\\')\""):
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual(r.returncode, 2, r.stderr)

    def test_controles_a_decisao_de_hoje_nao_muda(self):
        for comando in ("echo $'it\\'s'", "printf %s $'a\\'b'"):  # sem par para o `shlex`: já saíam 2
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual((r.returncode, SEM_PAR in r.stderr), (2, True), r.stderr)
        for comando in ("echo $'a\\\\b\\nc'", "echo $'a\\nb'", "echo $'a\\\\'", "echo it\\'s; echo ok"):  # saíam 0
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_barra_barra_antes_do_fecho_nao_e_aspa_escapada(self):
        r = self.conformidade("echo $'a\\\\'; cat .env")  # o `\\` é a barra; o `'` fecha; o `;` separa e o cat é recusado
        self.assertEqual(r.returncode, 2)
        self.assertIn("ler .env", r.stderr)
        self.assertNotIn(SEM_PAR, r.stderr)

    def test_o_bash_roda_o_segundo_comando_no_nivel_aninhado(self):
        for comando in (ANINHADO_ENV, ANINHADO_EVAL):
            with self.subTest(comando=comando):
                r, _ = self.bash(comando, {".env": "SEGREDO-FALSO\n", "'": ""})
                self.assertEqual(r.stdout, "it's\nSEGREDO-FALSO\n")
        r, pasta = self.bash(ANINHADO_GIT, {".git": None, "'": ""})
        self.assertEqual(r.stdout, "it's\n")
        self.assertFalse((pasta / ".git").exists(), "o shell de dentro separou o `;` e rodou o rm")

    def test_o_nivel_aninhado_entre_aspas_duplas_sai_2(self):
        for comando in (ANINHADO_ENV, ANINHADO_GIT, ANINHADO_EVAL, ANINHADO_SH):
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn(SEM_PAR, r.stderr)

    def test_controles_do_nivel_aninhado_saem_0(self):
        for comando in (r'''bash -c "echo \$'a\\nb'"''', r'''bash -c "echo \$'a\\\\'"''',
                        r'''bash -c "echo \$'a'; echo it\\'s"''', r'''eval "echo \$'a\\x41'"'''):
            with self.subTest(comando=comando):
                r = self.conformidade(comando)
                self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_o_leitor_fiel_marca_so_a_aspa_escapada(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        import _comum
        self.assertTrue(_comum.palavras_do_texto("echo $'it\\'s'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo $'a\\\\'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo $'a\\nb'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo 'it\\'; echo ok").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto("echo \"$'\\'\"").aspa_escapada)
        self.assertTrue(_comum.palavras_do_texto(r"echo \$'it\'s'; cat .env \'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto(r"echo \$'a\\'; echo ok").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto(r"echo \$'a\nb'").aspa_escapada)
        self.assertFalse(_comum.palavras_do_texto(r"echo \$'a'; echo it\'s").aspa_escapada)


class AtalhosDoLote(unittest.TestCase):
    """Custo do hook no lote de heredocs (CI do PR #474, 0.44.0): o leitor pula de uma vez o que só avança, o nome do programa e a
    pasta resolvida ficam guardados e o caminho se compara pelo texto. A leitura tem de sair igual à de antes (as saídas abaixo são
    as da develop, conferidas por comparação com o código antigo em 200 mil textos)."""

    @classmethod
    def setUpClass(cls):
        cls.c, cls.conf, _ = modulos_dos_hooks()

    def test_leitor_igual_ao_de_antes(self):
        c = self.c
        leitura = c.palavras_do_texto("x=`echo 'a`b' c`")  # na crase, o acento fecha também dentro das aspas simples
        self.assertEqual([[p.valor for p in s.palavras] for s in leitura.simples], [["echo", "a"], ["x=_b c`"]])
        self.assertTrue(leitura.duvida)
        leitura = c.palavras_do_texto("echo 'a b' c|d >f 2>&1")
        self.assertEqual([[p.valor for p in s.palavras] for s in leitura.simples], [["echo", "a b", "c"], ["d"]])
        self.assertEqual([(r.prefixo, r.operador, r.alvo.valor) for r in leitura.simples[1].redirecoes], [("", ">", "f"), ("2", ">&", "1")])
        self.assertEqual(c.varrer_comentarios("ab.c # x\nd=~e"), (frozenset({5}), 10))
        self.assertEqual(c.varrer_comentarios("a_b-c/d:e@f,g+h%i~j^k*l?m[n]o{p}q!r # s"), (frozenset({36}), 39))
        self.assertEqual(c.varrer_comentarios("x >#y"), (frozenset(), 3))
        achados, duvida = c.heredocs("cat <<'E' $((1+2)) ${x} $[1] $'a' <<<w ((y)) \"$(z)\" `q`\nbody\nE\necho fim")
        self.assertEqual([(h.operador, h.delimitador, h.corpo, h.fim) for h in achados], [(4, "E", (56, 61), 63)])
        self.assertIsNone(duvida)
        self.assertEqual(c.ansi_c_decodificado("a $'\\x68i' \"q\" 'r' $\"s\""), "a 'hi' \"q\" 'r' \"s\"")
        self.assertEqual(c.ansi_c_decodificado("plain text only"), "plain text only")
        self.assertEqual([t for t, _, _ in c.fichas("a  # c\nb")], ["a", "\n", "b"])
        self.assertEqual([(t, sinal) for t, sinal, _ in c.fichas("a | b>c")], [("a", False), ("|", True), ("b", False), (">", True), ("c", False)])

    def test_nome_relativo_e_pasta_resolvida_como_o_pathlib(self):
        c, conf = self.c, self.conf
        for palavra in ("/usr/bin/python3", "a/", "a/.", "..", "", "x"):
            self.assertEqual(c.nome_do_caminho(palavra), Path(palavra).name, palavra)
        for posix, base, esperado in (("/a/b/c", "/a", "b/c"), ("/a", "/a", "."), ("/ab/c", "/a", None), ("/a/b", "/", "a/b"),
                                      ("/x", "/a", None)):
            self.assertEqual(conf.relativo_ao_pai(posix, Path(base)), esperado, (posix, base))
        tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "real").mkdir()
        (tmp / "pela").symlink_to(tmp / "real")
        (tmp / "real" / "alvo").write_text("x", encoding="utf-8")
        (tmp / "real" / "atalho").symlink_to(tmp / "real" / "alvo")
        for caminho in ("pela/novo", "pela/atalho", "pela/..", "pela/.", "real/alvo", "pela"):
            self.assertEqual(conf.realpath_pela_pasta(str(tmp / caminho)), os.path.realpath(tmp / caminho), caminho)


class CorpusDosCaminhos(unittest.TestCase):
    """O subconjunto do corpus de tests/hooks/conformidade que passa pela escrita em caminho protegido, pelo nome do programa e pelo
    `entrega --pedido` do conferente (D4): roda rápido, para os mutantes da 0.44.0 (o corpus inteiro é do test_hooks)."""
    SELECAO = re.compile(r"^(conferente-entrega|aq-escreve|home-|lancador-|heredoc-donos-1-|i-perl|fc-|trava-forge-atualizar)|tee|claude|"
                         r"manifesto|xargs")
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_subconjunto(self):
        casos = [(f"conformidade/{p.stem}", Fixture(p)) for p in sorted((FIXTURES / "conformidade").glob("*.json")) if self.SELECAO.search(p.stem)]
        self.assertGreaterEqual(len(casos), 150)
        self.assertEqual(self.executar_em_lote(casos), len(casos))


if __name__ == "__main__":
    unittest.main()
