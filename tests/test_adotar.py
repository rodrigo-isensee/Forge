"""`forge adotar` (fase E do lote único, L46): traz um projeto existente para o Forge sem quebrar nada.

Repositórios temporários; a confirmação vem por um pseudoterminal (o "s" só vale digitado, C-40-1).
Controles: a leitura não muda a árvore nem o `.git/` (C-46-1), nada do repositório roda (C-46-2: `core.fsmonitor`
de armadilha) e o `core.hooksPath` de outra ferramenta fica (C-46-3).
"""
import hashlib
import json
import os
import pty
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ADOTAR = RAIZ / "bin" / "forge-adotar"


def ambiente(home):
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    env.update(HOME=str(home), GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="T",
               GIT_COMMITTER_EMAIL="t@t", PATH="/usr/bin:/bin")
    return env


def impressao(pasta):
    """Hash de tudo o que há na pasta (nomes, modos e conteúdo), .git/ incluído."""
    h = hashlib.sha256()
    for arq in sorted(p for p in pasta.rglob("*")):
        h.update(str(arq.relative_to(pasta)).encode())
        if arq.is_file() and not arq.is_symlink():
            h.update(oct(arq.stat().st_mode).encode() + arq.read_bytes())
    return h.hexdigest()


class Base(unittest.TestCase):
    def _callTestMethod(self, method):
        """Exceção que não é de asserção (prazo estourado, arquivo que não veio) também é falha do comportamento:
        o mutante que a provoca morre, em vez de sair como erro de execução."""
        try:
            method()
        except (AssertionError, unittest.SkipTest):
            raise
        except Exception as e:  # noqa: BLE001
            self.fail(f"{type(e).__name__}: {e}")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="adotar-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.env = ambiente(self.home)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.git("init", "-q", "-b", "main")
        (self.proj / "app.txt").write_text("código do projeto\n", encoding="utf-8")
        (self.proj / "CLAUDE.md").write_text("meu CLAUDE.md\n", encoding="utf-8")
        (self.proj / "package.json").write_text('{"scripts": {"test": "x"}}\n', encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "inicial")
        self.forge = ADOTAR

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.proj), *args], env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def adotar(self, *args):
        return subprocess.run([sys.executable, str(self.forge), *args], cwd=self.proj, env=self.env,
                              capture_output=True, text=True, timeout=60)

    def adotar_no_terminal(self, resposta, *args):
        mestre, escravo = pty.openpty()
        try:
            p = subprocess.Popen([sys.executable, str(self.forge), *args], cwd=self.proj, env=self.env, stdin=escravo,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            os.close(escravo)
            os.write(mestre, resposta.encode())
            try:
                saida, _ = p.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
                p.communicate()
                raise
        finally:
            os.close(mestre)
        return p.returncode, saida


class Leitura(Base):
    def test_diagnostico_nao_muda_nada_nem_roda_o_fsmonitor_do_projeto(self):  # C-46-1 e C-46-2
        marca = self.tmp / "rodou"
        armadilha = self.tmp / "armadilha.sh"
        armadilha.write_text(f"#!/bin/sh\ntouch {marca}\n", encoding="utf-8")
        armadilha.chmod(0o755)
        self.git("config", "core.fsmonitor", str(armadilha))
        os.utime(self.proj / "app.txt", (1, 1))  # índice desatualizado: um `git status` comum o regravaria
        antes = impressao(self.proj)
        for args in ((), ("--so-ler",)):
            with self.subTest(args=args):
                r = self.adotar(*args)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn("nada foi alterado", r.stdout)
                self.assertIn("Recomendação", r.stdout)
                self.assertEqual(impressao(self.proj), antes)
        self.assertFalse(marca.exists(), "o fsmonitor do projeto rodou")

    def test_sem_terminal_nao_aplica(self):  # C-40-1: nenhuma entrada fora do terminal confirma
        antes = impressao(self.proj)
        r = subprocess.run([sys.executable, str(ADOTAR)], cwd=self.proj, env=self.env, input="s\n",
                           capture_output=True, text=True, timeout=60)
        self.assertIn("só vale digitada", r.stdout)
        self.assertEqual(impressao(self.proj), antes)

    def test_mostra_hooks_branches_e_arquivos_que_ficam(self):
        self.git("config", "core.hooksPath", "outra-ferramenta/hooks")
        saida = self.adotar("--so-ler").stdout
        self.assertIn("core.hooksPath=outra-ferramenta/hooks é de outra ferramenta e fica como está", saida)
        self.assertIn("main sim/não; develop não/não; homolog não/não", saida)
        self.assertIn("já existem e ficam como estão: CLAUDE.md", saida)

    def test_diagnostico_mostra_branch_remoto_pronto_e_settings_mesclado(self):
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "settings")
        saida = self.adotar("--so-ler").stdout
        self.assertIn("- git: branch main; remoto: nenhum", saida)
        self.assertIn("- trabalho não salvo: nenhum", saida)
        self.assertIn("- pronto: npm test (o projeto já tem (package.json))", saida)
        self.assertIn("(o .claude/settings.json é mesclado, sem apagar nada)", saida)
        (self.proj / "package.json").write_text("{}\n", encoding="utf-8")
        saida = self.adotar("--so-ler").stdout
        self.assertIn("- trabalho não salvo: 1 arquivo(s)", saida)
        self.assertIn("- pronto: (sugerido pelo pacote) (o sugerido pelo pacote;", saida)
        self.git("remote", "add", "origin", "https://exemplo.invalid/x.git")
        self.assertIn("remoto: origin", self.adotar("--so-ler").stdout)

    def test_variaveis_git_do_ambiente_nao_desviam_a_leitura(self):
        self.env["GIT_DIR"] = str(self.tmp / "nao-existe")
        r = self.adotar("--so-ler")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("- git: branch main", r.stdout)

    def test_hooks_ativos_em_git_hooks_aparecem(self):
        gancho = self.proj / ".git" / "hooks" / "pre-commit"
        gancho.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        gancho.chmod(0o755)
        self.assertIn("ativos em .git/hooks (pre-commit)", self.adotar("--so-ler").stdout)

    def test_arvore_suja_para(self):  # C-46-1: árvore suja para
        (self.proj / "novo.txt").write_text("x\n", encoding="utf-8")
        antes = impressao(self.proj)
        r = self.adotar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("trabalho não salvo", r.stdout)
        self.assertEqual(impressao(self.proj), antes)
        self.assertEqual(self.adotar("--so-ler").returncode, 0)

    def test_projeto_que_ja_usa_o_forge(self):
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge" / "versao").write_text("0.40.0\n", encoding="utf-8")
        r = self.adotar()
        self.assertEqual(r.returncode, 0)
        self.assertIn("já usa o Forge (versão 0.40.0)", r.stdout)

    def test_recusa_o_clone_do_forge_a_pasta_pessoal_e_pasta_sem_git(self):
        r = subprocess.run([sys.executable, str(ADOTAR), str(RAIZ)], env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("próprio Forge", r.stderr)
        r = subprocess.run([sys.executable, str(ADOTAR), str(self.home)], env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("pasta pessoal", r.stderr)
        solta = self.tmp / "solta"
        solta.mkdir()
        r = subprocess.run([sys.executable, str(ADOTAR), str(solta)], env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("não está no git", r.stderr)

    def test_opcao_desconhecida_sai_2(self):
        for args in (("--sim",), ("--stack",), ("--stack", "../x")):
            with self.subTest(args=args):
                self.assertEqual(self.adotar(*args).returncode, 2)


class Aplicar(Base):
    def test_com_s_cria_a_branch_e_adota_sem_sobrescrever_nem_trocar_o_hooks_path(self):  # C-46-3
        self.git("config", "core.hooksPath", "outra-ferramenta/hooks")
        codigo, saida = self.adotar_no_terminal("s\nn\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.git("branch", "--show-current"), "chore/adotar-forge")
        self.assertFalse((self.proj / "outra-ferramenta").exists(), "sem o sim, nada é encadeado")
        self.assertEqual(self.git("branch", "--list", "develop"), "", "sem o sim, sem develop")
        self.assertTrue((self.proj / ".forge" / "versao").is_file())
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"), "meu CLAUDE.md\n")
        self.assertEqual(self.git("config", "core.hooksPath"), "outra-ferramenta/hooks")
        self.assertIn("ainda sem commit e sem envio", saida)
        self.assertEqual(self.git("log", "--oneline", "main").count("\n"), 0, "não pode criar commit")

    def test_sem_o_s_nada_muda(self):
        antes = impressao(self.proj)
        codigo, saida = self.adotar_no_terminal("n\n")
        self.assertEqual(codigo, 0)
        self.assertIn("Nada foi alterado", saida)
        self.assertEqual(impressao(self.proj), antes)

    def test_sem_versionar_deixa_no_git_so_a_declaracao(self):  # FILA-24, D1 = B
        codigo, saida = self.adotar_no_terminal("s\nn\nn\n", "--sem-versionar")
        self.assertEqual(codigo, 0, saida)
        visiveis = sorted(l[3:] for l in self.git("status", "--porcelain", "-uall").splitlines())
        self.assertEqual(visiveis, [".claude/settings.json", ".forge/config.json", ".forge/versao"])


    def test_encadeia_no_pre_push_da_outra_ferramenta_sem_trocar_o_hooks_path(self):  # D5
        pasta = self.proj / "outra-ferramenta" / "hooks"
        pasta.mkdir(parents=True)
        original = "#!/bin/sh\ncat > \"$(git rev-parse --show-toplevel)/../recebido\"\n"
        (pasta / "pre-push").write_text(original, encoding="utf-8")
        (pasta / "pre-push").chmod(0o755)
        self.git("add", ".")
        self.git("commit", "-qm", "hook")
        self.git("config", "core.hooksPath", "outra-ferramenta/hooks")
        codigo, saida = self.adotar_no_terminal("s\ns\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.git("config", "core.hooksPath"), "outra-ferramenta/hooks")
        texto = (pasta / "pre-push").read_text(encoding="utf-8")
        self.assertTrue(texto.startswith("#!/bin/sh\n# Forge"), texto)
        self.assertIn("Posso acrescentar no começo de outra-ferramenta/hooks/pre-push", saida)
        self.assertTrue(texto.endswith(original.split("\n", 1)[1]), "o hook do projeto continua inteiro")
        sha = self.git("rev-parse", "HEAD")
        zero = "0" * 40
        falsos = self.tmp / "falsos"  # MP1311 E1.16: o pre-push.local gerado roda o pronto rápido da stack (pnpm exec ...)
        falsos.mkdir()
        (falsos / "pnpm").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (falsos / "pnpm").chmod(0o755)
        self.env["PATH"] = f"{falsos}:{self.env['PATH']}"
        rodar = lambda linha: subprocess.run(["sh", str(pasta / "pre-push"), "origin", "x"], cwd=self.proj, env=self.env,  # noqa: E731
                                             input=linha, capture_output=True, text=True)
        r = rodar(f"refs/heads/main {sha} refs/heads/main {zero}\n")
        self.assertEqual(r.returncode, 1, "a main fica protegida pelo pre-push do Forge")
        self.assertFalse((self.tmp / "recebido").exists())
        linha = f"refs/heads/x {sha} refs/heads/x {zero}\n"
        r = rodar(linha)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.tmp / "recebido").read_text(encoding="utf-8"), linha, "o hook do projeto recebe a entrada")

    def test_hooks_ativos_em_git_hooks_ganham_pre_push_que_chama_o_do_forge(self):
        gancho = self.proj / ".git" / "hooks" / "pre-commit"
        gancho.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        gancho.chmod(0o755)
        codigo, saida = self.adotar_no_terminal("s\ns\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(subprocess.run(["git", "-C", str(self.proj), "config", "core.hooksPath"], env=self.env,
                                        capture_output=True).returncode, 1, "core.hooksPath não muda")
        self.assertIn(".githooks/pre-push", (self.proj / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8"))
        self.assertIn("Posso criar .git/hooks/pre-push", saida)
        self.assertEqual(gancho.read_text(encoding="utf-8"), "#!/bin/sh\nexit 0\n")

    def test_hooks_path_absoluto_tambem_encadeia(self):
        pasta = self.tmp / "ganchos"
        pasta.mkdir()
        self.git("config", "core.hooksPath", str(pasta))
        codigo, saida = self.adotar_no_terminal("s\ns\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertIn(".githooks/pre-push", (pasta / "pre-push").read_text(encoding="utf-8"))

    def test_hook_que_nao_e_de_shell_fica_como_esta(self):
        pasta = self.proj / "ganchos"
        pasta.mkdir()
        (pasta / "pre-push").write_text("#!/usr/bin/env python3\nprint(1)\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "hook")
        self.git("config", "core.hooksPath", "ganchos")
        codigo, saida = self.adotar_no_terminal("s\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("não é de shell", saida)
        self.assertEqual((pasta / "pre-push").read_text(encoding="utf-8"), "#!/usr/bin/env python3\nprint(1)\n")

    def test_develop_nasce_da_main_so_com_o_sim(self):  # D5
        codigo, saida = self.adotar_no_terminal("s\ns\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.git("rev-parse", "develop"), self.git("rev-parse", "main"))
        self.assertIn("develop criada a partir da main", saida)

    def test_registra_o_pedido_com_stack_e_pronto_supostos_e_passa_o_pronto_do_projeto(self):  # D5
        self.git("rm", "-q", "CLAUDE.md")
        self.git("commit", "-qm", "sem CLAUDE.md")
        codigo, saida = self.adotar_no_terminal("s\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        pedido = (self.proj / "docs" / "pedidos" / "adotar-forge.md").read_text(encoding="utf-8")
        historico = pedido.split("## Histórico", 1)[1]
        self.assertIn("suposição de stack: node-react", historico)
        self.assertIn("suposição de pronto: npm test (o projeto já tem (package.json))", historico)
        self.assertIn("npm test", (self.proj / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_pedido_que_ja_existe_nao_e_sobrescrito(self):
        pedidos = self.proj / "docs" / "pedidos"
        pedidos.mkdir(parents=True)
        (pedidos / "adotar-forge.md").write_text("meu\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "pedido")
        codigo, saida = self.adotar_no_terminal("s\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual((pedidos / "adotar-forge.md").read_text(encoding="utf-8"), "meu\n")


    def prontos_para_o_sandbox(self):
        """bwrap falso no PATH e a credencial do bot no ambiente: o forge-init ligaria o sandbox de um projeto novo."""
        bin_falso = self.tmp / "bin"
        bin_falso.mkdir()
        (bin_falso / "bwrap").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (bin_falso / "bwrap").chmod(0o755)
        self.env.update(PATH=f"{bin_falso}:{self.env['PATH']}", GH_TOKEN="x", GIT_CONFIG_COUNT="0")

    def sandbox(self):
        caixa = json.loads((self.proj / ".claude" / "settings.json").read_text(encoding="utf-8")).get("sandbox")
        return caixa.get("enabled") if isinstance(caixa, dict) else None

    def test_sandbox_nunca_liga_sozinho_so_oferece(self):  # 0.45.0, item 3
        self.prontos_para_o_sandbox()
        codigo, saida = self.adotar_no_terminal("s\nn\nn\n")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Oferta: o sandbox do Bash está desligado", saida)
        self.assertIsNone(self.sandbox())

    def test_sandbox_liga_com_o_s(self):
        codigo, saida = self.adotar_no_terminal("s\nn\ns\n")
        self.assertEqual(codigo, 0, saida)
        self.assertIs(self.sandbox(), True)


class Deteccao(Base):
    """A stack vem da linha `Detecção:` do pacote (núcleo neutro, ADR 0001): numa cópia do Forge com dois pacotes."""

    def setUp(self):
        super().setUp()
        copia = self.tmp / "forge"
        for pasta in ("bin", "templates", "stacks", ".claude-plugin"):
            shutil.copytree(RAIZ / pasta, copia / pasta, symlinks=True)
        outra = copia / "stacks" / "outra"
        outra.mkdir()
        (outra / "pronto.md").write_text("# Pronto\n\nComando sugerido: `make pronto`\n\nDetecção: `marcador.cfg`\n",
                                         encoding="utf-8")
        self.forge = copia / "bin" / "forge-adotar"
        self.git("rm", "-q", "package.json")
        self.git("commit", "-qm", "sem pacote")

    def test_detecta_pelo_arquivo_do_pacote(self):
        (self.proj / "marcador.cfg").write_text("x\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "marcador")
        self.assertIn("stack: outra (detectada", self.adotar("--so-ler").stdout)

    def test_stack_sem_pacote_guarda_a_pendencia_e_para(self):  # D5 e skill novo-projeto
        antes = impressao(self.proj)
        r = self.adotar("--so-ler")
        self.assertIn("sem pacote", r.stdout)
        self.assertNotIn("- pronto:", r.stdout, "sem stack, sem linha de pronto")
        self.assertFalse((self.home / ".local" / "state").exists(), "a leitura não guarda nada")
        r = self.adotar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("escolha com --stack", r.stdout)
        self.assertIn("Pendência guardada", r.stdout)
        self.assertTrue(list((self.home / ".local" / "state" / "forge" / "sugestoes").iterdir()))
        self.assertEqual(impressao(self.proj), antes)
        self.assertIn("stack: outra (escolhida", self.adotar("--so-ler", "--stack", "outra").stdout)


if __name__ == "__main__":
    unittest.main()
