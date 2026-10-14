"""Primeiro uso (F5): `forge atualizar`, `forge voltar-versao` e o aviso de versão nova do doutor, sem rede.

O "Forge publicado" é um repositório bare local com tags `vX.Y.Z` (cada tag leva uma cópia do plugin real com a
versão trocada); o `claude` do PATH é falso e só registra como foi chamado; HOME, estado e git são temporários.
As confirmações são respondidas num terminal de verdade (pty), como a pessoa faria.
"""
import json
import os
import pty
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ATUALIZAR = RAIZ / "bin" / "forge-atualizar"
VOLTAR = RAIZ / "bin" / "forge-voltar-versao"
HOOK = RAIZ / "hooks" / "doutor.py"
VERSAO = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
HOJE = "2026-10-14"

CLAUDE_FALSO = r"""#!/usr/bin/env bash
echo "claude $*" >> "$FAKE_DIR/claude.log"
if [ -f "$FAKE_DIR/claude-falha" ] && [[ "$*" == *"$(cat "$FAKE_DIR/claude-falha")"* ]]; then
  echo "claude falso: falhou de propósito" >&2; exit 1
fi
# Imita o defeito do `claude` real: `marketplace remove` sem `--scope` reescreve o settings.json do projeto (o cwd)
if [ "$2 $3" = "marketplace remove" ] && [[ "$*" != *"--scope user"* ]] && [ -f "$PWD/.claude/settings.json" ]; then
  echo '{}' > "$PWD/.claude/settings.json"
fi
if [ -f "$FAKE_DIR/suja-projeto" ] && [ "$2 $3" = "marketplace remove" ]; then
  echo '{"agent": "outro"}' > "$(cat "$FAKE_DIR/suja-projeto")/.claude/settings.json"
fi
exit 0
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="atualizar-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home, self.bin, self.fake = self.tmp / "home", self.tmp / "bin", self.tmp / "fake"
        for p in (self.home, self.bin, self.fake):
            p.mkdir()
        (self.bin / "claude").write_text(CLAUDE_FALSO, encoding="utf-8")
        (self.bin / "claude").chmod(0o755)
        self.gitconfig = self.home / "gitconfig"
        self.gitconfig.write_text("[user]\n\tname = Pessoa Teste\n\temail = pessoa@exemplo.test\n", encoding="utf-8")
        self.publicado = self.tmp / "forge-publicado.git"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CLAUDE_PROJECT_DIR"}
        self.env.update(HOME=str(self.home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.gitconfig),
                        PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_DIR=str(self.fake), FORGE_HOJE=HOJE,
                        FORGE_REPO_URL=str(self.publicado), FORGE_PERMITE_LOCAL="1")
        self.env.pop("XDG_STATE_HOME", None)
        self.git("init", "-q", "--bare", "-b", "main", str(self.publicado), cwd=self.tmp)
        self.montar_projeto()
        self.escrever_home(".claude/plugins/installed_plugins.json",
                           json.dumps({"version": 2, "plugins": {"forge@forge": [{"scope": "user", "version": VERSAO}]}}))
        self.escrever_home(".claude/settings.json", json.dumps({
            "sandbox": {"enabled": True},
            "extraKnownMarketplaces": {"forge": {"source": {"source": "github", "repo": "dono/Forge"}}}}))
        self.publicar(VERSAO)

    def montar_projeto(self):
        remoto = self.tmp / "remoto.git"
        self.proj = self.tmp / "proj"
        self.git("init", "-q", "--bare", "-b", "main", str(remoto), cwd=self.tmp)
        self.git("clone", "-q", str(remoto), str(self.proj), cwd=self.tmp)
        self.escrever(".forge/versao", VERSAO + "\n")
        self.escrever(".forge/perfil", "iniciante\n")
        self.escrever(".claude/settings.json", json.dumps({"agent": "forge:jarvis", "enabledPlugins": {"forge@forge": True}}))
        self.escrever(".githooks/pre-push", "#!/bin/sh\nexit 0\n")
        (self.proj / ".githooks" / "pre-push").chmod(0o755)
        self.escrever(".gitignore", ".forge/run/\n.forge/local.json\n.claude/settings.local.json\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: inicio")
        self.git("push", "-q", "origin", "main")
        for ramo in ("develop", "homolog"):
            self.git("branch", ramo)
            self.git("push", "-q", "origin", ramo)
        self.git("config", "core.hooksPath", ".githooks")

    def git(self, *args, cwd=None, ok=True):
        r = subprocess.run(["git", *args], cwd=cwd or self.proj, env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def escrever(self, rel, texto):
        arq = self.proj / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def escrever_home(self, rel, texto):
        arq = self.home / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def publicar(self, versao, falha=None, novidade="Passa a avisar quando sai versão nova."):
        """Cria a tag v<versao> no Forge publicado: cópia do plugin real, versão trocada e um CHANGELOG pequeno."""
        trabalho = self.tmp / f"pub-{versao}"
        if trabalho.exists():
            return
        trabalho.mkdir()
        for pasta in ("bin", "migrations", "templates", ".claude-plugin"):
            shutil.copytree(RAIZ / pasta, trabalho / pasta)
        plugin = trabalho / ".claude-plugin" / "plugin.json"
        dados = json.loads(plugin.read_text(encoding="utf-8"))
        dados["version"] = versao
        plugin.write_text(json.dumps(dados), encoding="utf-8")
        (trabalho / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## [Não publicado]\n### Adicionado\n- **Ainda não saiu:** não deve aparecer.\n\n"
            f"## [{versao}] - 2026-10-14\n### Adicionado\n- **Novidade {versao}:** {novidade} Detalhe técnico que não precisa aparecer.\n\n"
            f"## [{VERSAO}] - 2026-10-13\n### Adicionado\n- **Antiga:** já está instalada.\n", encoding="utf-8")
        if falha == "simulacao":
            (trabalho / "bin" / "forge-upgrade").write_text("#!/usr/bin/env python3\nimport sys\nprint('migração quebrada', file=sys.stderr)\nsys.exit(3)\n", encoding="utf-8")
            (trabalho / "bin" / "forge-upgrade").chmod(0o755)
        if falha == "doutor":
            (trabalho / "bin" / "forge-doutor").write_text("#!/usr/bin/env python3\nimport sys\nprint('Forge doutor: 1 coisa para ver\\n- problema novo do doutor')\nsys.exit(1)\n", encoding="utf-8")
            (trabalho / "bin" / "forge-doutor").chmod(0o755)
        self.git("init", "-q", "-b", "main", cwd=trabalho)
        self.git("add", "-A", cwd=trabalho)
        self.git("commit", "-q", "-m", f"release {versao}", cwd=trabalho)
        self.git("tag", f"v{versao}", cwd=trabalho)
        self.git("push", "-q", str(self.publicado), f"v{versao}", cwd=trabalho)

    def rodar(self, script, *args, respostas=None, cwd=None, env=None):
        """Com `respostas`, num terminal (pty) que responde cada pergunta na ordem; sem elas, sem terminal."""
        env = env or self.env
        if respostas is None:
            r = subprocess.run([sys.executable, str(script), *args], env=env, cwd=cwd or self.proj, capture_output=True,
                               text=True, timeout=120, stdin=subprocess.DEVNULL)
            return r.returncode, r.stdout + r.stderr
        mestre, escravo = pty.openpty()
        os.write(mestre, "".join(r + "\n" for r in respostas).encode())
        p = subprocess.Popen([sys.executable, str(script), *args], env=env, cwd=cwd or self.proj, stdin=escravo,
                             stdout=escravo, stderr=escravo, close_fds=True)
        os.close(escravo)
        saida, limite = b"", time.time() + 25
        while time.time() < limite:
            if not select.select([mestre], [], [], 1)[0]:
                continue
            try:
                bloco = os.read(mestre, 4096)
            except OSError:
                break
            if not bloco:
                break
            saida += bloco
        if p.poll() is None:  # pergunta sem resposta: o teste falha em vez de travar
            p.kill()
            saida += b"\n[TRAVOU esperando resposta]"
        p.wait(timeout=30)
        os.close(mestre)
        return p.returncode, saida.decode("utf-8", "replace").replace("\r", "")

    def chamadas_do_claude(self):
        arq = self.fake / "claude.log"
        return arq.read_text(encoding="utf-8").splitlines() if arq.exists() else []

    def ramos(self):
        return set(self.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines())

    def pontos(self):
        pasta = self.home / ".local/state/forge/retorno" / self.proj.name
        return sorted(pasta.iterdir()) if pasta.is_dir() else []


class Atualizar(Base):
    def test_caminho_feliz_mostra_resumo_guarda_o_ponto_aplica_e_roda_o_doutor(self):
        self.publicar("9.9.0")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn(VERSAO, saida)
        self.assertIn("9.9.0", saida)
        self.assertIn("Novidade 9.9.0", saida)
        self.assertNotIn("Detalhe técnico", saida, "o resumo é a primeira frase, em linguagem simples")
        self.assertNotIn("Ainda não saiu", saida)
        self.assertNotIn("Antiga", saida)
        self.assertEqual(self.git("show", "forge/upgrade-9.9.0:.forge/versao"), "9.9.0")
        self.assertIn("forge/antes-" + VERSAO, self.git("tag", "--list", "forge/*").splitlines())
        (ponto,) = self.pontos()
        meta = json.loads((ponto / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["plugin_antes"], meta["plugin_depois"], meta["projeto_antes"]), (VERSAO, "9.9.0", VERSAO))
        self.assertEqual((ponto / "forge" / "versao").read_text(encoding="utf-8").strip(), VERSAO)
        self.assertFalse((ponto / "claude").exists(), "o ponto não guarda configuração do Claude")
        self.assertFalse((ponto / "forge" / "run").exists())
        chamadas = self.chamadas_do_claude()
        self.assertTrue(any(c.startswith("claude plugin marketplace add ") and c.endswith("#v9.9.0 --scope user") for c in chamadas), chamadas)
        self.assertEqual(self.git("ls-remote", "--heads", "origin").count("upgrade"), 0, "nunca envia nada")
        self.assertIn("gh pr create", saida)

    def test_fixar_so_fixa_a_versao_em_uso_e_nao_mexe_no_projeto(self):
        codigo, saida = self.rodar(ATUALIZAR, "--fixar", respostas=[])
        self.assertEqual(codigo, 0, saida)
        adds = [c for c in self.chamadas_do_claude() if " marketplace add " in c]
        self.assertEqual(len(adds), 1, adds)
        self.assertTrue(adds[0].endswith("#v" + VERSAO + " --scope user"))
        self.assertEqual(self.ramos(), {"main", "develop", "homolog"})

    def test_recusa_nao_muda_nada(self):
        self.publicar("9.9.0")
        for resposta in ("n", ""):
            codigo, saida = self.rodar(ATUALIZAR, respostas=[resposta])
            self.assertEqual(codigo, 0, saida)
            self.assertIn("não mudei nada", saida.lower())
        self.assertEqual(self.chamadas_do_claude(), [])
        self.assertEqual(self.ramos(), {"main", "develop", "homolog"})
        self.assertEqual(self.pontos(), [])
        self.assertEqual(self.git("tag", "--list", "forge/*"), "")

    def test_sem_terminal_recusa_e_explica(self):
        self.publicar("9.9.0")
        codigo, saida = self.rodar(ATUALIZAR)
        self.assertEqual(codigo, 2, saida)
        self.assertIn("terminal", saida)
        self.assertEqual(self.chamadas_do_claude(), [])

    def test_sem_versao_nova_diz_que_esta_em_dia(self):
        self.publicar(VERSAO)
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("última versão", saida)
        self.assertEqual(self.chamadas_do_claude(), [])

    def test_sem_rede_nao_muda_nada_e_explica(self):
        env = {**self.env, "FORGE_REPO_URL": str(self.tmp / "nao-existe.git")}
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"], env=env)
        self.assertEqual(codigo, 1, saida)
        self.assertIn("conexão", saida)
        self.assertIn("não mudei nada", saida.lower())
        self.assertEqual(self.chamadas_do_claude(), [])
        self.assertEqual(self.pontos(), [])

    def test_arvore_suja_recusa_antes_de_qualquer_coisa(self):
        self.publicar("9.9.0")
        self.escrever("novo.txt", "trabalho meu\n")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("forge salvar", saida)
        self.assertEqual(self.chamadas_do_claude(), [])

    def test_simulacao_que_falha_nao_toca_no_plugin_nem_no_projeto(self):
        self.publicar("9.9.1", falha="simulacao")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("simulação", saida)
        self.assertIn("não mudei nada", saida.lower())
        self.assertEqual(self.chamadas_do_claude(), [], "o plugin só muda depois de a simulação dar certo")
        self.assertEqual(self.ramos(), {"main", "develop", "homolog"})
        self.assertEqual((self.proj / ".forge/versao").read_text(encoding="utf-8").strip(), VERSAO)

    def test_doutor_que_falha_oferece_voltar_e_voltar_restaura(self):
        self.publicar("9.9.2", falha="doutor")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s", "s"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("Voltar para a versão " + VERSAO, saida)
        adds = [c for c in self.chamadas_do_claude() if " marketplace add " in c]
        self.assertTrue(adds[0].endswith("#v9.9.2 --scope user") and adds[-1].endswith("#v" + VERSAO + " --scope user"), adds)
        self.assertEqual(self.git("branch", "--show-current"), "main")
        self.assertIn("forge/upgrade-9.9.2", self.ramos(), "o trabalho da atualização não é apagado")
        self.assertEqual((self.proj / ".forge/versao").read_text(encoding="utf-8").strip(), VERSAO)

    def test_doutor_que_falha_e_a_pessoa_nao_quer_voltar(self):
        self.publicar("9.9.2", falha="doutor")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s", "n"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("forge voltar-versao", saida)
        adds = [c for c in self.chamadas_do_claude() if " marketplace add " in c]
        self.assertEqual(len(adds), 1, adds)
        self.assertEqual(self.git("branch", "--show-current"), "forge/upgrade-9.9.2")

    def test_falha_ao_trocar_o_plugin_devolve_o_anterior_e_nao_mexe_no_projeto(self):
        self.publicar("9.9.0")
        (self.fake / "claude-falha").write_text("#v9.9.0", encoding="utf-8")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        adds = [c for c in self.chamadas_do_claude() if " marketplace add " in c]
        self.assertEqual(adds[-1], "claude plugin marketplace add dono/Forge --scope user", adds)
        self.assertEqual(self.ramos(), {"main", "develop", "homolog"})


class Voltar(Base):
    def atualizar(self, versao="9.9.0"):
        self.publicar(versao)
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        (self.fake / "claude.log").unlink()

    def test_sem_ponto_de_retorno_diz_que_nao_ha_o_que_voltar(self):
        codigo, saida = self.rodar(VOLTAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("ponto de retorno", saida)

    def test_recusa_nao_muda_nada(self):
        self.atualizar()
        codigo, saida = self.rodar(VOLTAR, respostas=["n"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("não mudei nada", saida.lower())
        self.assertEqual(self.chamadas_do_claude(), [])
        self.assertEqual(self.git("branch", "--show-current"), "forge/upgrade-9.9.0")

    def test_sem_terminal_recusa(self):
        self.atualizar()
        codigo, saida = self.rodar(VOLTAR)
        self.assertEqual(codigo, 2, saida)
        self.assertEqual(self.chamadas_do_claude(), [])

    def test_atualizacao_nao_mesclada_volta_para_a_branch_de_antes_e_guarda_a_branch(self):
        self.atualizar()
        codigo, saida = self.rodar(VOLTAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        adds = self.chamadas_do_claude()
        self.assertTrue(any(c.endswith("#v" + VERSAO + " --scope user") for c in adds if " marketplace add " in c), adds)
        self.assertEqual(self.git("branch", "--show-current"), "main")
        self.assertEqual((self.proj / ".forge/versao").read_text(encoding="utf-8").strip(), VERSAO)
        self.assertIn("forge/upgrade-9.9.0", self.ramos(), "nunca apaga trabalho")
        self.assertIn("pull request", saida)

    def test_atualizacao_ja_mesclada_vira_branch_nova_com_os_arquivos_de_antes_sem_reescrever_historia(self):
        self.atualizar()
        self.git("switch", "-q", "develop")
        self.git("merge", "-q", "--no-ff", "-m", "Merge upgrade", "forge/upgrade-9.9.0")
        antes = self.git("rev-parse", "develop")
        codigo, saida = self.rodar(VOLTAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.git("rev-parse", "develop"), antes, "develop não é tocada")
        self.assertEqual(self.git("branch", "--show-current"), "forge/voltar-9.9.0")
        self.assertEqual((self.proj / ".forge/versao").read_text(encoding="utf-8").strip(), VERSAO)
        self.git("merge-base", "--is-ancestor", "develop", "HEAD")  # a história só cresce
        self.assertIn("chore(forge): volta", self.git("log", "-1", "--format=%s"))
        self.assertIn("pull request", saida)

    def test_falha_ao_trocar_o_plugin_aborta_antes_de_mexer_no_projeto(self):
        self.atualizar()
        (self.fake / "claude-falha").write_text("marketplace add", encoding="utf-8")
        codigo, saida = self.rodar(VOLTAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertEqual(self.git("branch", "--show-current"), "forge/upgrade-9.9.0")

    def test_voltar_duas_vezes_usa_o_ponto_mais_recente_e_nao_repete(self):
        self.atualizar()
        self.assertEqual(self.rodar(VOLTAR, respostas=["s"])[0], 0)
        codigo, saida = self.rodar(VOLTAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("ponto de retorno", saida)


class Defesas(Base):
    def importar(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        self.addCleanup(sys.path.remove, str(RAIZ / "bin"))
        import forge_versoes
        return forge_versoes

    def test_so_https_e_nenhum_outro_protocolo(self):
        v = self.importar()
        for ruim in ("http://github.com/x/Forge", "ext::sh -c id", "file:///tmp/x", "git://github.com/x/Forge",
                     "ssh://git@github.com/x/Forge", "/tmp/x", "-oProxyCommand=id", "https://", "https://u:p@github.com/x/Forge"):
            with self.subTest(ruim):
                self.assertFalse(v.url_valida(ruim, permite_local=False), ruim)
        self.assertTrue(v.url_valida("https://github.com/rodrigo-isensee/Forge", permite_local=False))

    def test_consulta_de_tags_usa_cwd_neutro_e_protocolos_negados(self):
        self.escrever_log = self.fake / "git.log"
        (self.bin / "git").write_text(
            f'#!/usr/bin/env bash\n{{ echo "cwd=$PWD"; echo "proto=$GIT_ALLOW_PROTOCOL"; echo "args=$*"; }} >> "{self.escrever_log}"\n'
            'echo "aaaa\trefs/tags/v9.9.0"\n', encoding="utf-8")
        (self.bin / "git").chmod(0o755)
        env = {k: v for k, v in self.env.items() if k not in ("FORGE_PERMITE_LOCAL", "FORGE_REPO_URL")}
        env["FORGE_REPO_URL"] = "https://github.com/exemplo/Forge"
        codigo = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import forge_versoes as v; "
             "print(v.ultima_versao(v.url_do_forge()))", str(RAIZ / "bin")],
            env=env, cwd=self.proj, capture_output=True, text=True)
        self.assertEqual(codigo.returncode, 0, codigo.stderr)
        self.assertIn("9.9.0", codigo.stdout)
        log = self.escrever_log.read_text(encoding="utf-8")
        self.assertNotIn(f"cwd={self.proj}", log, "cwd neutro: nunca dentro do projeto")
        self.assertIn("proto=https", log)
        self.assertIn("protocol.allow=never", log)
        self.assertIn("ls-remote", log)
        self.assertIn("https://github.com/exemplo/Forge", log)

    def test_url_ruim_na_variavel_e_ignorada_sem_chamar_o_git(self):
        v = self.importar()
        os.environ["FORGE_REPO_URL"] = "ext::sh -c id"
        self.addCleanup(os.environ.pop, "FORGE_REPO_URL")
        self.assertIsNone(v.url_do_forge())


class AvisoDoDoutor(Base):
    def setUp(self):
        super().setUp()
        self.escrever(".gitignore", ".forge/run/\n")
        self.env.pop("FORGE_VERIFICAR_VERSAO", None)

    def hook(self, evento, env=None):
        entrada = {"hook_event_name": evento, "session_id": "s1", "cwd": str(self.proj)}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=env or self.env, cwd=self.proj,
                              capture_output=True, text=True, timeout=30)

    def test_avisa_numa_linha_so_uma_vez_por_dia_e_so_ao_parar(self):
        self.publicar("9.9.0")
        r = self.hook("SessionStart")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), "ao abrir não escreve nada nem usa a rede")
        r = self.hook("Stop")
        self.assertEqual(r.returncode, 0, r.stderr)
        mensagem = json.loads(r.stdout)["systemMessage"]
        self.assertEqual(len(mensagem.splitlines()), 1)
        self.assertIn("9.9.0", mensagem)
        self.assertIn(VERSAO, mensagem)
        self.assertIn("forge atualizar", mensagem)
        r = self.hook("Stop")
        self.assertEqual((r.returncode, r.stdout), (0, ""), "uma vez por dia")

    def test_sem_versao_nova_fica_em_silencio(self):
        self.publicar(VERSAO)
        for evento in ("SessionStart", "Stop"):
            r = self.hook(evento)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), evento)

    def test_sem_rede_fica_em_silencio(self):
        env = {**self.env, "FORGE_REPO_URL": str(self.tmp / "nao-existe.git")}
        r = self.hook("Stop", env=env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_desligar_a_consulta(self):
        self.publicar("9.9.0")
        r = self.hook("Stop", env={**self.env, "FORGE_VERIFICAR_VERSAO": "0"})
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_junto_com_problema_do_doutor_continua_uma_mensagem(self):
        self.publicar("9.9.0")
        self.git("config", "--unset", "core.hooksPath")
        r = self.hook("Stop")
        mensagem = json.loads(r.stdout)["systemMessage"]
        self.assertIn("9.9.0", mensagem)
        self.assertIn("Forge doutor", mensagem)


OPERACOES = (" marketplace add ", " marketplace remove ", " plugin update ", " plugin install ")


class Revisao(Base):
    """Correções do review do PR 111: escopo de usuário, ordem segura, ponto sem segredo, doutor antes e depois."""

    def py(self, codigo, env=None, cwd=None):
        return subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import forge_versoes as v\n" + codigo,
                               str(RAIZ / "bin")], env=env or self.env, cwd=cwd or self.proj, capture_output=True, text=True)

    def test_toda_operacao_do_plugin_usa_o_escopo_de_usuario_e_o_settings_do_projeto_fica_intacto(self):
        self.publicar("9.9.0")
        antes = (self.proj / ".claude/settings.json").read_text(encoding="utf-8")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        operacoes = [c for c in self.chamadas_do_claude() if any(o in c + " " for o in OPERACOES)]
        self.assertTrue(operacoes)
        for c in operacoes:
            self.assertIn("--scope user", c)
        self.assertEqual((self.proj / ".claude/settings.json").read_text(encoding="utf-8"), antes)
        self.assertEqual(self.git("show", "main:.claude/settings.json"), antes)

    def test_se_o_claude_mexer_em_arquivo_versionado_o_forge_restaura_e_avisa(self):
        self.publicar("9.9.0")
        (self.fake / "suja-projeto").write_text(str(self.proj), encoding="utf-8")
        antes = (self.proj / ".claude/settings.json").read_text(encoding="utf-8")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("restaurei", saida)
        self.assertEqual((self.proj / ".claude/settings.json").read_text(encoding="utf-8"), antes)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_falha_no_add_devolve_exatamente_a_fonte_e_o_escopo_originais(self):
        self.publicar("9.9.0")
        (self.fake / "claude-falha").write_text("#v9.9.0", encoding="utf-8")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        chamadas = self.chamadas_do_claude()
        adds = [c for c in chamadas if " marketplace add " in c]
        self.assertEqual(adds[-1], "claude plugin marketplace add dono/Forge --scope user", chamadas)
        self.assertTrue(any(c.startswith("claude plugin install forge@forge --scope user") or c.startswith("claude plugin update forge@forge --scope user")
                            for c in chamadas[chamadas.index(adds[-1]):]), chamadas)
        self.assertNotIn("#v" + VERSAO, adds[-1])

    def test_falha_no_update_e_no_install_tambem_devolve_a_fonte_original(self):
        self.publicar("9.9.0")
        (self.fake / "claude-falha").write_text("forge@forge --scope user", encoding="utf-8")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        adds = [c for c in self.chamadas_do_claude() if " marketplace add " in c]
        self.assertEqual(adds[-1], "claude plugin marketplace add dono/Forge --scope user")

    def test_sem_rede_ou_sem_a_tag_nada_e_removido(self):
        env = {**self.env, "FORGE_REPO_URL": str(self.tmp / "nao-existe.git")}
        r = self.py("print(v.fixar_plugin(v.url_do_forge(), '9.9.0'))", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("False", r.stdout)
        self.assertEqual(self.chamadas_do_claude(), [], "a checagem da tag vem antes do remove")
        r = self.py("print(v.fixar_plugin(v.url_do_forge(), '8.8.8'))")  # rede ok, tag inexistente
        self.assertIn("False", r.stdout)
        self.assertEqual(self.chamadas_do_claude(), [])

    def test_sem_a_marketplace_no_claude_nao_mexe_em_nada(self):
        self.escrever_home(".claude/settings.json", json.dumps({"sandbox": {"enabled": True}}))
        r = self.py(f"print(v.fixar_plugin(v.url_do_forge(), '{VERSAO}'))")
        self.assertIn("False", r.stdout)
        self.assertEqual([c for c in self.chamadas_do_claude() if "list" not in c], [])

    def test_ponto_de_retorno_nao_guarda_segredo_nem_o_que_nao_e_versionado_e_a_volta_nao_sobrescreve(self):
        self.publicar("9.9.0")
        self.escrever(".claude/settings.local.json", json.dumps({"env": {"TOKEN": "segredo-xyz"}}))
        self.escrever(".forge/local.json", '{"chave": "local-xyz"}')
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        (ponto,) = self.pontos()
        for arq in ponto.rglob("*"):
            if arq.is_file():
                texto = arq.read_text(encoding="utf-8", errors="replace")
                self.assertNotIn("segredo-xyz", texto, str(arq))
                self.assertNotIn("local-xyz", texto, str(arq))
        self.assertFalse(list(ponto.rglob("settings*.json")))
        self.assertEqual(ponto.stat().st_mode & 0o077, 0, "a pasta do ponto é só do dono")
        self.git("switch", "-q", "develop")
        self.git("merge", "-q", "--no-ff", "-m", "Merge upgrade", "forge/upgrade-9.9.0")
        self.escrever(".claude/settings.local.json", json.dumps({"env": {"TOKEN": "segredo-novo"}}))
        self.escrever(".forge/local.json", '{"chave": "local-novo"}')
        codigo, saida = self.rodar(VOLTAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("segredo-novo", (self.proj / ".claude/settings.local.json").read_text(encoding="utf-8"))
        self.assertIn("local-novo", (self.proj / ".forge/local.json").read_text(encoding="utf-8"))
        self.assertNotIn("local.json", saida.split("Arquivos que a atualização criou")[-1] if "Arquivos que a atualização criou" in saida else "")

    def test_dois_projetos_com_o_mesmo_nome_nao_compartilham_o_ponto(self):
        v = self.py("print(1)")
        self.assertEqual(v.returncode, 0)
        outro = self.tmp / "outro" / self.proj.name
        outro.mkdir(parents=True)
        r = self.py(f"from pathlib import Path\nv.criar_ponto(Path({str(self.proj)!r}), {{'projeto': {str(self.proj)!r}, 'plugin_antes': 'a', 'plugin_depois': 'b'}})\n"
                    f"print(v.ultimo_ponto(Path({str(outro)!r}))[0])")
        self.assertEqual(r.stdout.strip(), "None")

    def test_doutor_antes_e_depois_so_oferece_voltar_se_o_problema_for_novo(self):
        self.publicar("9.9.0")
        self.git("branch", "-q", "-D", "homolog")  # problema que já existe antes da atualização
        antes = subprocess.run([str(RAIZ / "bin" / "forge-doutor"), "--rapido", str(self.proj)], env=self.env, capture_output=True, text=True)
        self.assertIn("homolog", antes.stdout, "pré-condição: o doutor vê o problema antigo")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s", "n"])
        self.assertEqual(codigo, 0, saida)
        self.assertNotIn("Voltar para a versão", saida)
        self.assertIn("Já existiam antes", saida)

    def test_doutor_com_problema_novo_oferece_voltar(self):
        self.publicar("9.9.2", falha="doutor")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s", "n"])
        self.assertEqual(codigo, 1, saida)
        self.assertIn("problema novo do doutor", saida)
        self.assertIn("Voltar para a versão " + VERSAO, saida)

    def test_nao_diz_que_ficou_como_esta_depois_de_voltar(self):
        self.publicar("9.9.2", falha="doutor")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s", "s"])
        self.assertNotIn("Tudo bem, ficou como está", saida)

    def test_consulta_de_tags_ignora_repositorio_acima_da_pasta_temporaria(self):
        self.publicar("9.9.0")
        envolvente = self.tmp / "envolvente"
        envolvente.mkdir()
        self.git("init", "-q", cwd=envolvente)
        self.git("config", f"url.https://evil.invalid/x.insteadOf", str(self.publicado), cwd=envolvente)
        (envolvente / "t").mkdir()
        env = {**self.env, "TMPDIR": str(envolvente / "t")}
        r = self.py("print(v.ultima_versao(v.url_do_forge()))", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("'9.9.0'", r.stdout)


class Subcomandos(Base):
    def test_forge_lista_atualizar_e_voltar_versao(self):
        r = subprocess.run([str(RAIZ / "bin" / "forge")], env=self.env, capture_output=True, text=True)
        self.assertIn("atualizar", r.stdout)
        self.assertIn("voltar-versao", r.stdout)

    def test_nao_usa_comandos_destrutivos(self):
        for script in (ATUALIZAR, VOLTAR, RAIZ / "bin" / "forge_versoes.py"):
            texto = script.read_text(encoding="utf-8")
            for proibido in ("--force", "reset", "--no-verify", "clean -f", "branch -D", "rmtree(projeto"):
                self.assertNotIn(proibido, texto, f"{script.name}: {proibido}")


if __name__ == "__main__":
    unittest.main()
