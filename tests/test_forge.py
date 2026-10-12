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


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class ForgeInit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-init-"))
        git("init", "-q", "-b", "trabalho", cwd=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rodar(self, *extra):
        return subprocess.run(["bash", str(RAIZ / "bin/forge-init"), "--nome", "Demo", "--pronto", "make pronto", *extra, str(self.tmp)],
                              capture_output=True, text=True, check=True)

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
        subprocess.run(["bash", str(RAIZ / "bin/forge-init"), "--nome", "H", str(self.repo)], check=True, capture_output=True)
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", "inicio", cwd=self.repo)
        git("remote", "add", "origin", str(self.remoto), cwd=self.repo)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def push(self, ref):
        return subprocess.run(["git", "push", "origin", ref], cwd=self.repo, capture_output=True, text=True)

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


if __name__ == "__main__":
    unittest.main()
