"""Testes estruturais do Forge (só biblioteca padrão; rode com `python3 -m unittest discover -s tests -v`).

Garantem a integridade da fábrica a cada mudança: manifestos, agentes, skills, referências,
neutralidade (nada específico de um projeto), regras invioláveis, inicializador e hook de git.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENTES = RAIZ / "agents"
SKILLS = RAIZ / "skills"
MODELOS_VALIDOS = {"opus", "sonnet", "haiku", "inherit"}
CONFIG = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))


def frontmatter(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        raise AssertionError(f"{caminho.relative_to(RAIZ)}: sem frontmatter")
    campos = {}
    for linha in m.group(1).splitlines():
        if ":" in linha and not linha.startswith(" "):
            chave, valor = linha.split(":", 1)
            campos[chave.strip()] = valor.strip()
    return campos


def arquivos_texto():
    for pasta in ("agents", "skills", "docs", "templates", "bin", "scripts"):
        for p in (RAIZ / pasta).rglob("*"):
            if p.is_file():
                yield p


class Manifestos(unittest.TestCase):
    def test_plugin_json(self):
        d = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(d["name"], "forge")
        self.assertRegex(d["version"], r"^\d+\.\d+\.\d+$")

    def test_marketplace_aponta_para_a_raiz(self):
        d = json.loads((RAIZ / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(d["name"], "forge")
        self.assertEqual([p["source"] for p in d["plugins"] if p["name"] == "forge"], ["."])
        self.assertNotIn("version", d["plugins"][0], "versão só no plugin.json")

    def test_changelog_tem_a_versao_atual(self):
        versao = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        changelog = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
        primeira = re.search(r"^## \[?(\d+\.\d+\.\d+)", changelog, re.M)
        self.assertIsNotNone(primeira, "CHANGELOG.md sem entrada de versão")
        self.assertEqual(primeira.group(1), versao, "versão do plugin.json difere da última do CHANGELOG")


class Agentes(unittest.TestCase):
    def setUp(self):
        self.agentes = sorted(AGENTES.glob("*.md"))
        self.skills = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}

    def test_time_completo(self):
        nomes = {p.stem for p in self.agentes}
        self.assertEqual(nomes, set(CONFIG["agentes_obrigatorios"]))

    def test_frontmatter_valido(self):
        for p in self.agentes:
            with self.subTest(agente=p.name):
                fm = frontmatter(p)
                self.assertEqual(fm.get("name"), p.stem, "name deve ser igual ao nome do arquivo")
                self.assertGreater(len(fm.get("description", "")), 40, "descrição curta demais")
                self.assertTrue(fm.get("tools"), "tools vazio")
                self.assertIn(fm.get("model"), MODELOS_VALIDOS)

    def test_skills_citadas_existem(self):
        for p in self.agentes:
            fm = frontmatter(p)
            for s in [x.strip() for x in fm.get("skills", "").split(",") if x.strip()]:
                with self.subTest(agente=p.name, skill=s):
                    self.assertIn(s.removeprefix("forge:"), self.skills)

    def test_time_do_jarvis_existe(self):
        texto = (AGENTES / "jarvis.md").read_text(encoding="utf-8")
        tabela = re.search(r"## Time\n(.*?)\n## ", texto, re.S).group(1)
        citados = set(re.findall(r"^\| `(?:forge:)?([a-z-]+)` \|", tabela, re.M))
        self.assertEqual(citados, {p.stem for p in self.agentes} - {"jarvis"})


class Skills(unittest.TestCase):
    def test_frontmatter_valido(self):
        for p in sorted(SKILLS.glob("*/SKILL.md")):
            with self.subTest(skill=p.parent.name):
                fm = frontmatter(p)
                self.assertEqual(fm.get("name"), p.parent.name)
                self.assertGreater(len(fm.get("description", "")), 40)


class Referencias(unittest.TestCase):
    def test_caminhos_do_plugin_existem(self):
        padrao = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")
        for p in arquivos_texto():
            for rel in padrao.findall(p.read_text(encoding="utf-8", errors="ignore")):
                with self.subTest(arquivo=str(p.relative_to(RAIZ)), ref=rel):
                    self.assertTrue((RAIZ / rel.rstrip(".")).exists(), f"{rel} não existe no Forge")


class Neutralidade(unittest.TestCase):
    """A fábrica serve N projetos: nada de nomes ou regras de um projeto específico."""

    def test_sem_termos_de_projeto(self):
        termos = [re.compile(t, re.I) for t in CONFIG["termos_proibidos"]]
        for p in arquivos_texto():
            texto = p.read_text(encoding="utf-8", errors="ignore")
            for t in termos:
                with self.subTest(arquivo=str(p.relative_to(RAIZ)), termo=t.pattern):
                    self.assertIsNone(t.search(texto))


class RegrasInviolaveis(unittest.TestCase):
    """Se alguém apagar uma regra da fábrica por engano, o CI quebra."""

    def test_trechos_obrigatorios(self):
        for rel, trechos in CONFIG["invariantes"].items():
            texto = (RAIZ / rel).read_text(encoding="utf-8")
            for t in trechos:
                with self.subTest(arquivo=rel, trecho=t):
                    self.assertRegex(texto, re.compile(t, re.S))


def ambiente_limpo():
    """Ambiente sem as variáveis GIT_* herdadas (um hook do git exporta GIT_DIR e afins) e sem config
    global/de sistema: o git dos testes só enxerga o repositório temporário em que roda."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return env


def git(*args, cwd):
    return subprocess.run(["git", "-C", str(cwd), *args], cwd=cwd, env=ambiente_limpo(),
                          check=True, capture_output=True, text=True)


def forge_init(*args, cwd):
    return subprocess.run(["bash", str(RAIZ / "bin/forge-init"), *args], cwd=cwd, env=ambiente_limpo(),
                          check=True, capture_output=True, text=True)


class ForgeInit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-init-"))
        git("init", "-q", "-b", "trabalho", cwd=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rodar(self, *extra):
        return forge_init("--nome", "Demo", "--pronto", "make pronto", *extra, str(self.tmp), cwd=self.tmp)

    def test_cria_estrutura_completa(self):
        self.rodar()
        modelo = RAIZ / "templates/projeto"
        for arq in modelo.rglob("*"):
            if arq.is_file():
                self.assertTrue((self.tmp / arq.relative_to(modelo)).is_file(), arq.relative_to(modelo))
        claude_md = (self.tmp / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("# Demo", claude_md)
        self.assertIn("`make pronto`", claude_md)
        for arq in self.tmp.rglob("*"):
            if arq.is_file() and ".git" not in arq.parts:
                self.assertNotIn("{{", arq.read_text(encoding="utf-8", errors="ignore"), arq)
        self.assertEqual(git("config", "core.hooksPath", cwd=self.tmp).stdout.strip(), ".githooks")
        self.assertTrue(os.access(self.tmp / ".githooks/pre-push", os.X_OK))
        settings = json.loads((self.tmp / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["agent"], "forge:jarvis")
        self.assertTrue(settings["enabledPlugins"]["forge@forge"])

    def test_mescla_settings_existente(self):
        (self.tmp / ".claude").mkdir()
        existente = {"enabledPlugins": {"outro@mkt": True}, "permissions": {"deny": ["Read(./segredo)"]}}
        (self.tmp / ".claude/settings.json").write_text(json.dumps(existente), encoding="utf-8")
        self.assertIn("mesclado .claude/settings.json", self.rodar().stdout)
        s = json.loads((self.tmp / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(s["agent"], "forge:jarvis")
        self.assertTrue(s["enabledPlugins"]["outro@mkt"], "não pode apagar plugin do projeto")
        self.assertTrue(s["enabledPlugins"]["forge@forge"])
        self.assertIn("forge", s["extraKnownMarketplaces"])
        self.assertIn("Read(./segredo)", s["permissions"]["deny"])
        self.assertIn("Bash(git * --no-verify*)", s["permissions"]["deny"])

    def test_nao_sobrescreve_sem_forcar(self):
        (self.tmp / "CLAUDE.md").write_text("meu conteúdo\n", encoding="utf-8")
        saida = self.rodar().stdout
        self.assertIn("mantido  CLAUDE.md", saida)
        self.assertEqual((self.tmp / "CLAUDE.md").read_text(encoding="utf-8"), "meu conteúdo\n")
        self.rodar("--forcar")
        self.assertIn("# Demo", (self.tmp / "CLAUDE.md").read_text(encoding="utf-8"))


class HookPrePush(unittest.TestCase):
    """O hook do modelo de projeto bloqueia a main e respeita o pre-push.local."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.remoto = self.tmp / "remoto.git"
        self.repo = self.tmp / "repo"
        git("init", "-q", "--bare", str(self.remoto), cwd=self.tmp)
        git("init", "-q", "-b", "main", str(self.repo), cwd=self.tmp)
        for k, v in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
            git("config", k, v, cwd=self.repo)
        forge_init("--nome", "H", str(self.repo), cwd=self.repo)
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", "inicio", cwd=self.repo)
        git("remote", "add", "origin", str(self.remoto), cwd=self.repo)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def push(self, ref):
        return subprocess.run(["git", "-C", str(self.repo), "push", "origin", ref], cwd=self.repo,
                              env=ambiente_limpo(), capture_output=True, text=True)

    def test_bloqueia_main(self):
        r = self.push("HEAD:main")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("envio para a main bloqueado", r.stderr)

    def test_permite_outra_branch(self):
        self.assertEqual(self.push("HEAD:feature/x").returncode, 0)

    def test_pre_push_local_que_falha_bloqueia(self):
        local = self.repo / ".githooks/pre-push.local"
        local.write_text("#!/usr/bin/env bash\necho falhou >&2\nexit 1\n", encoding="utf-8")
        local.chmod(0o755)
        self.assertNotEqual(self.push("HEAD:feature/y").returncode, 0)


class IsolamentoDoGit(unittest.TestCase):
    """Regressão: dentro de um hook (ex.: pre-push numa worktree) o git exporta GIT_DIR e afins.
    Os testes não podem herdá-los, senão escrevem no repositório real em vez do temporário."""

    def test_variaveis_git_herdadas_nao_afetam_outro_repositorio(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-sentinela-"))
        self.addCleanup(shutil.rmtree, tmp)
        sentinela = tmp / "sentinela"
        git("init", "-q", "-b", "trabalho", str(sentinela), cwd=tmp)
        git("-c", "user.name=s", "-c", "user.email=s@s", "commit", "-q", "--allow-empty", "-m", "s", cwd=sentinela)
        config = (sentinela / ".git/config").read_bytes()
        head = git("rev-parse", "HEAD", cwd=sentinela).stdout
        herdadas = {"GIT_DIR": str(sentinela / ".git"), "GIT_WORK_TREE": str(sentinela),
                    "GIT_INDEX_FILE": str(sentinela / ".git/index")}
        with mock.patch.dict(os.environ, herdadas):
            for classe, metodo in ((ForgeInit, "test_cria_estrutura_completa"), (HookPrePush, "test_permite_outra_branch")):
                caso = classe(metodo)
                caso.setUp()
                try:
                    getattr(caso, metodo)()
                finally:
                    caso.tearDown()
        self.assertEqual((sentinela / ".git/config").read_bytes(), config, "config da sentinela mudou")
        self.assertEqual(git("rev-parse", "HEAD", cwd=sentinela).stdout, head, "HEAD da sentinela mudou")


class CI(unittest.TestCase):
    def test_acoes_fixadas_por_sha(self):
        """Toda ação de terceiros usa SHA completo (40 hex); Dependabot atualiza."""
        for wf in sorted((RAIZ / ".github" / "workflows").glob("*.yml")):
            for n, linha in enumerate(wf.read_text(encoding="utf-8").splitlines(), 1):
                m = re.search(r"\buses:\s*(\S+)", linha)
                if m and not m.group(1).startswith("./"):
                    with self.subTest(arquivo=wf.name, linha=n):
                        self.assertRegex(m.group(1), r"@[0-9a-f]{40}$", "fixe a ação por SHA de 40 caracteres")

    def test_dependabot_para_actions(self):
        texto = (RAIZ / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("github-actions", texto)


class PrepararEstacao(unittest.TestCase):
    def test_scripts_existem_e_sao_executaveis(self):
        for nome in ("preparar-estacao.sh", "jarvis-forge", "jarvis", "instalar-atalho.sh"):
            with self.subTest(script=nome):
                caminho = RAIZ / "scripts" / nome
                self.assertTrue(caminho.is_file())
                self.assertTrue(os.access(caminho, os.X_OK))

    def test_simular_nao_instala_nada(self):
        """--simular sai 0, imprime o plano e não cria nada no HOME nem chama sudo/rede."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            bin_falso = Path(tmp) / "bin"
            bin_falso.mkdir()
            registro = Path(tmp) / "chamadas"
            for nome in ("sudo", "curl", "apt-get", "gh"):
                falso = bin_falso / nome
                falso.write_text(f'#!/bin/sh\necho "{nome} $*" >> "{registro}"\nexit 1\n')
                falso.chmod(0o755)
            env = ambiente_limpo()
            env.update(HOME=str(home), PATH=f"{bin_falso}:{env['PATH']}")
            r = subprocess.run(["bash", str(RAIZ / "scripts/preparar-estacao.sh"), "--simular"],
                               env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("[simular]", r.stdout)
            self.assertFalse(registro.exists(), "chamou comando que altera o sistema")
            for criado in (".nvm", "Forge", ".local/bin/jarvis", ".local/bin/jarvis-forge"):
                self.assertFalse((home / criado).exists(), f"criou {criado} no HOME")

    def test_argumento_invalido(self):
        r = subprocess.run(["bash", str(RAIZ / "scripts/preparar-estacao.sh"), "--x"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


class Orcamento(unittest.TestCase):
    def test_tamanho_dos_prompts(self):
        lim = CONFIG["limite_linhas"]
        for p in sorted(AGENTES.glob("*.md")):
            with self.subTest(agente=p.name):
                self.assertLessEqual(len(p.read_text(encoding="utf-8").splitlines()), lim["agente"])
        for p in sorted(SKILLS.glob("*/SKILL.md")):
            with self.subTest(skill=p.parent.name):
                self.assertLessEqual(len(p.read_text(encoding="utf-8").splitlines()), lim["skill"])


if __name__ == "__main__":
    unittest.main()
