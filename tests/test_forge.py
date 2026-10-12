"""Testes estruturais do Forge (só biblioteca padrão; rode com `python3 -m unittest discover -s tests -v`).

Garantem a integridade da fábrica a cada mudança: manifestos, agentes, skills, referências,
neutralidade (nada específico de um projeto), regras invioláveis, inicializador e hook de git.
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENTES = RAIZ / "agents"
SKILLS = RAIZ / "skills"
STACKS = RAIZ / "stacks"
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


def agentes_do_plugin():
    """Todo .md de agents/ e de stacks/*/agents/ (ADR 0001)."""
    return sorted(AGENTES.glob("*.md")) + sorted(STACKS.glob("*/agents/*.md"))


def skills_do_plugin():
    return sorted(SKILLS.glob("*/SKILL.md")) + sorted(STACKS.glob("*/skills/*/SKILL.md"))


def arquivos_texto():
    for pasta in ("agents", "skills", "stacks", "docs", "templates", "bin", "scripts", "hooks", "tests/transcricoes"):
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
        # "## [Não publicado]" pode vir no topo (ADR 0006); vale a primeira entrada numerada.
        primeira = re.search(r"^## \[?(\d+\.\d+\.\d+)", changelog, re.M)
        self.assertIsNotNone(primeira, "CHANGELOG.md sem entrada de versão")
        self.assertEqual(primeira.group(1), versao, "versão do plugin.json difere da última do CHANGELOG")


class ManifestoDoPlugin(unittest.TestCase):
    """ADR 0001: `agents` do plugin.json substitui a varredura de agents/; tudo precisa estar listado."""

    def setUp(self):
        self.manifesto = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))

    def test_agentes_listados_existem_e_vice_versa(self):
        listados = {(RAIZ / a).resolve() for a in self.manifesto["agents"]}
        for a in self.manifesto["agents"]:
            with self.subTest(agente=a):
                self.assertTrue(a.startswith("./") and a.endswith(".md"))
                self.assertTrue((RAIZ / a).is_file(), f"{a} listado e inexistente")
        existentes = {p.resolve() for p in agentes_do_plugin()}
        self.assertEqual({p.relative_to(RAIZ).as_posix() for p in existentes - listados}, set(), "agente fora do manifesto")
        self.assertEqual(len(listados), len(self.manifesto["agents"]), "agente listado duas vezes")

    def test_skills_de_stack_listadas_e_vice_versa(self):
        listadas = {(RAIZ / s).resolve() for s in self.manifesto["skills"]}
        for s in self.manifesto["skills"]:
            with self.subTest(skill=s):
                self.assertTrue((RAIZ / s / "SKILL.md").is_file(), f"{s} sem SKILL.md")
        existentes = {p.parent.resolve() for p in STACKS.glob("*/skills/*/SKILL.md")}
        self.assertEqual({p.relative_to(RAIZ).as_posix() for p in existentes - listadas}, set(), "skill de stack fora do manifesto")


class PacotesDeStack(unittest.TestCase):
    """ADR 0001: todo pacote em stacks/<nome>/ tem a mesma forma."""

    def test_stacks_esperadas_existem(self):
        for nome, itens in CONFIG["stacks_obrigatorias"].items():
            with self.subTest(stack=nome):
                self.assertEqual({p.stem for p in (STACKS / nome).glob("agents/*.md")}, set(itens["agentes"]))
                self.assertEqual({p.parent.name for p in (STACKS / nome).glob("skills/*/SKILL.md")}, set(itens["skills"]))

    def test_forma_do_pacote(self):
        pacotes = sorted(p for p in STACKS.iterdir() if p.is_dir())
        self.assertTrue(pacotes, "stacks/ vazia")
        for pacote in pacotes:
            with self.subTest(stack=pacote.name):
                self.assertRegex(pacote.name, r"^[a-z0-9-]+$")
                self.assertTrue(list(pacote.glob("skills/*/SKILL.md")), "stack sem skills")
                self.assertTrue((pacote / "seguranca.md").is_file(), "falta seguranca.md")
                self.assertTrue((pacote / "pronto.md").is_file(), "falta pronto.md")
                pronto = (pacote / "pronto.md").read_text(encoding="utf-8")
                self.assertRegex(pronto, r"(?m)^Comando sugerido: `[^`]+`", "pronto.md sem 'Comando sugerido: `...`'")
                extras = {p.name for p in pacote.iterdir()} - {"agents", "skills", "seguranca.md", "pronto.md"}
                self.assertEqual(extras, set(), "arquivo fora da forma do pacote")

    def test_nomes_de_agente_nao_colidem(self):
        nomes = [p.stem for p in agentes_do_plugin()]
        self.assertEqual(len(nomes), len(set(nomes)), "dois agentes com o mesmo nome")

    def test_nucleo_aponta_para_a_seguranca_da_stack(self):
        texto = (SKILLS / "cyber-security/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("stacks/<stack>/seguranca.md", texto)


class Agentes(unittest.TestCase):
    def setUp(self):
        self.agentes = agentes_do_plugin()
        self.skills = {p.parent.name for p in skills_do_plugin()}

    def test_time_completo(self):
        esperados = set(CONFIG["agentes_obrigatorios"])
        for itens in CONFIG["stacks_obrigatorias"].values():
            esperados |= set(itens["agentes"])
        self.assertEqual({p.stem for p in self.agentes}, esperados)

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
        # Os agentes de stack não ficam na tabela (o núcleo não os cita): o Jarvis os lê de stacks/<stack>/agents/.
        self.assertEqual(citados, {p.stem for p in AGENTES.glob("*.md")} - {"jarvis"})
        self.assertIn("stacks/<stack>/agents/", tabela)


class Skills(unittest.TestCase):
    def test_frontmatter_valido(self):
        for p in skills_do_plugin():
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


class NeutralidadeDoNucleo(unittest.TestCase):
    """ADR 0001: linguagem, framework e ferramenta só em stacks/ (e nas exceções explícitas do config)."""

    def setUp(self):
        self.cfg = CONFIG["neutralidade_nucleo"]

    def test_detector_acha_termo_de_stack(self):
        termos = [re.compile(t) for t in self.cfg["termos"]]
        self.assertTrue(any(t.search("Use React com TypeScript") for t in termos))
        self.assertFalse(any(t.search("Verifique o nó da árvore; reagir ao evento") for t in termos))

    def test_nucleo_sem_termos_de_stack(self):
        termos = [re.compile(t) for t in self.cfg["termos"]]
        for pasta in self.cfg["pastas"]:
            for p in sorted((RAIZ / pasta).rglob("*")):
                rel = p.relative_to(RAIZ).as_posix()
                if not p.is_file() or any(rel.startswith(i) for i in self.cfg["ignorar"]):
                    continue
                texto = p.read_text(encoding="utf-8", errors="ignore")
                for t in termos:
                    if t.pattern in self.cfg["excecoes"].get(rel, []):
                        continue
                    with self.subTest(arquivo=rel, termo=t.pattern):
                        achado = t.search(texto)
                        self.assertIsNone(achado, f"{rel}: stack no núcleo ({achado and achado.group(0)}); mova para stacks/ ou registre exceção em tests/config.json")

    def test_stack_declarada_no_modelo_e_no_init(self):
        self.assertIn("{{STACK}}", (RAIZ / "templates/projeto/CLAUDE.md").read_text(encoding="utf-8"))


class RegrasInviolaveis(unittest.TestCase):
    """Se alguém apagar uma regra da fábrica por engano, o CI quebra."""

    def test_trechos_obrigatorios(self):
        for rel, trechos in CONFIG["invariantes"].items():
            texto = (RAIZ / rel).read_text(encoding="utf-8")
            for t in trechos:
                with self.subTest(arquivo=rel, trecho=t):
                    self.assertRegex(texto, re.compile(t, re.S))


REGRAS = RAIZ / "docs" / "regras"


def palavras(texto: str) -> list:
    """Normaliza para comparar redações: minúsculas, sem pontuação nem marcação."""
    return re.findall(r"\w+", texto.lower())


def corpo_da_regra(caminho: Path) -> str:
    """Texto da regra sem frontmatter, título e linha de propósito (iguais em todas por formato)."""
    texto = re.sub(r"^---\n.*?\n---\n", "", caminho.read_text(encoding="utf-8"), flags=re.S)
    return "\n".join(l for l in texto.splitlines() if not l.startswith(("# ", "Propósito:")))


def sequencias(texto: str, n: int) -> set:
    p = palavras(texto)
    return {" ".join(p[i:i + n]) for i in range(len(p) - n + 1)}


class AntiDuplicacao(unittest.TestCase):
    """ADR 0002: o texto de cada regra vive só em docs/regras/R-<ID>.md; os outros arquivos citam o ID."""

    def setUp(self):
        cfg = CONFIG["anti_duplicacao"]
        self.n = cfg["palavras"]
        self.pastas = cfg["pastas"]
        self.excecoes = {" ".join(palavras(e)) for e in cfg["excecoes"]}

    def test_detector_acha_copia(self):
        fonte = "Nenhum agente faz commit, merge, rebase, reset, cherry-pick ou push na main do projeto."
        copia = "Lembrete: nenhum agente faz COMMIT merge rebase reset cherry-pick ou push na `main` do projeto!"
        self.assertTrue(sequencias(fonte, self.n) & sequencias(copia, self.n))
        self.assertFalse(sequencias(fonte, self.n) & sequencias("`R-MAIN` a main é do usuário", self.n))

    def test_regra_so_na_fonte(self):
        fontes = sorted(REGRAS.glob("R-*.md"))
        self.assertTrue(fontes, "docs/regras sem regras")
        alvos = [p for pasta in self.pastas if (RAIZ / pasta).is_dir()
                 for p in sorted((RAIZ / pasta).rglob("*")) if p.is_file()]
        textos = {p: sequencias(p.read_text(encoding="utf-8", errors="ignore"), self.n) for p in alvos}
        for fonte in fontes:
            trechos = sequencias(corpo_da_regra(fonte), self.n) - self.excecoes
            for alvo, seqs in textos.items():
                if alvo == fonte:
                    continue
                comum = trechos & seqs
                with self.subTest(regra=fonte.name, arquivo=str(alvo.relative_to(RAIZ))):
                    self.assertFalse(comum, f"texto da regra copiado; cite o ID. Ex.: \"{min(comum, default='')}\"")


class RegrasComId(unittest.TestCase):
    """ADR 0002: toda regra citada existe e diz como é verificada; o índice lista todas."""

    def setUp(self):
        self.regras = {p.stem: p for p in sorted(REGRAS.glob("R-*.md"))}

    def test_frontmatter_restrito(self):
        for nome, p in self.regras.items():
            with self.subTest(regra=p.name):
                fm = frontmatter(p)
                self.assertEqual(set(fm), {"id", "titulo", "verificada_por"}, "frontmatter só com id, titulo, verificada_por")
                self.assertEqual(fm["id"], nome, "id deve ser igual ao nome do arquivo")
                self.assertRegex(nome, r"^R-[A-Z]+$")
                self.assertTrue(fm["titulo"], "titulo vazio")
                self.assertTrue(fm["verificada_por"], "verificada_por vazio")

    def test_indice_lista_todas(self):
        indice = (REGRAS / "README.md").read_text(encoding="utf-8")
        for nome in self.regras:
            with self.subTest(regra=nome):
                self.assertIn(f"[`{nome}`]({nome}.md)", indice)

    def test_ids_citados_existem(self):
        origens = [RAIZ / ".claude" / "CLAUDE.md", *sorted(REGRAS.glob("*.md"))]
        for pasta in ("agents", "skills", "templates"):
            origens += [p for p in sorted((RAIZ / pasta).rglob("*")) if p.is_file()]
        for p in origens:
            for rid in set(re.findall(r"\bR-[A-Z][A-Z0-9-]*\b", p.read_text(encoding="utf-8", errors="ignore"))):
                with self.subTest(arquivo=str(p.relative_to(RAIZ)), regra=rid):
                    self.assertTrue(rid in self.regras, f"{rid} não existe em docs/regras/")


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
        self.assertRegex(claude_md, r"## Stack\n- Pacote do Forge: `node-react`")

    def test_stack_padrao_define_o_pronto_sugerido(self):
        forge_init("--nome", "Demo", str(self.tmp), cwd=self.tmp)
        claude_md = (self.tmp / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("`npm run pronto`", claude_md)

    def test_stack_desconhecida_ou_invalida_e_recusada(self):
        for ruim in ("inexistente", "../templates"):
            with self.subTest(stack=ruim):
                with self.assertRaises(subprocess.CalledProcessError) as erro:
                    forge_init("--stack", ruim, str(self.tmp), cwd=self.tmp)
                self.assertIn("stack desconhecida", erro.exception.stderr)

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


    def test_grava_versao_e_config_idempotente(self):
        self.rodar()
        plugin = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertEqual((self.tmp / ".forge/versao").read_text(encoding="utf-8").strip(), plugin)
        self.assertEqual(json.loads((self.tmp / ".forge/config.json").read_text(encoding="utf-8"))["teto_agentes"], 3)
        self.rodar()
        self.assertEqual((self.tmp / ".gitignore").read_text(encoding="utf-8").splitlines().count(".forge/run/"), 1)

    def test_nao_mexe_na_versao_existente(self):
        (self.tmp / ".forge").mkdir()
        (self.tmp / ".forge/versao").write_text("0.1.0\n", encoding="utf-8")
        self.rodar()
        self.assertEqual((self.tmp / ".forge/versao").read_text(encoding="utf-8"), "0.1.0\n")


# Documentos de um projeto antigo: só os do contrato sem frontmatter ganham `contrato: 0` (ADR 0004).
DOCS_ANTES = {
    "docs/reviews/p1-1.md": "# Review antigo\nparecer: aprovado\n",
    "docs/qa/p1.md": "# QA antigo\r\nok\r\n",
    "docs/architecture/features/p1.md": "# Plano antigo\n",
    "docs/reviews/p2-1.md": "---\ncontrato: 0\ntitulo: já marcado\n---\n# Review\n",
    "docs/reviews/README.md": "# Pareceres\n",
    "docs/qa/_modelo.md": "# Modelo\n",
    "docs/outro.md": "# Fora do contrato\n",
}
DOCS_DEPOIS = dict(DOCS_ANTES, **{
    "docs/reviews/p1-1.md": "---\ncontrato: 0\n---\n# Review antigo\nparecer: aprovado\n",
    "docs/qa/p1.md": "---\r\ncontrato: 0\r\n---\r\n# QA antigo\r\nok\r\n",
    "docs/architecture/features/p1.md": "---\ncontrato: 0\n---\n# Plano antigo\n",
})


class ForgeUpgrade(unittest.TestCase):
    """Projeto "antes" (sem .forge/, como criado por um forge-init antigo) migrado pelo projeto (ADR 0005)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-upgrade-"))
        git("init", "-q", "-b", "develop", cwd=self.tmp)
        git("config", "user.name", "t", cwd=self.tmp)
        git("config", "user.email", "t@example.com", cwd=self.tmp)
        (self.tmp / ".gitignore").write_text("node_modules/", encoding="utf-8")
        (self.tmp / "CLAUDE.md").write_text("meu conteúdo\n", encoding="utf-8")
        for rel, texto in DOCS_ANTES.items():
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / rel).write_bytes(texto.encode("utf-8"))
        git("add", "-A", cwd=self.tmp)
        git("commit", "-q", "-m", "antes", cwd=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def upgrade(self, *args):
        return subprocess.run([str(RAIZ / "bin/forge-upgrade"), "--ate", "0.5.0", *args, str(self.tmp)],
                              env=ambiente_limpo(), capture_output=True, text=True)

    def test_migra_e_segunda_vez_nao_muda_nada(self):
        r = self.upgrade()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("gh pr create --base develop", r.stdout)
        self.assertEqual(git("branch", "--show-current", cwd=self.tmp).stdout.strip(), "forge/upgrade-0.5.0")
        self.assertEqual((self.tmp / ".forge/versao").read_text(encoding="utf-8"), "0.5.0\n")
        self.assertEqual(json.loads((self.tmp / ".forge/config.json").read_text(encoding="utf-8"))["teto_agentes"], 3)
        self.assertEqual((self.tmp / ".gitignore").read_text(encoding="utf-8"), "node_modules/\n.forge/run/\n")
        self.assertEqual((self.tmp / "CLAUDE.md").read_text(encoding="utf-8"), "meu conteúdo\n")
        for rel, texto in DOCS_DEPOIS.items():
            self.assertEqual((self.tmp / rel).read_bytes().decode("utf-8"), texto, rel)
        docs = subprocess.run([str(RAIZ / "bin/forge-check"), "--raiz", str(self.tmp), "docs"],
                              env=ambiente_limpo(), capture_output=True, text=True)
        self.assertEqual((docs.returncode, docs.stdout), (0, ""))
        self.assertEqual(git("log", "--format=%s", "develop..HEAD", cwd=self.tmp).stdout.strip(),
                         "chore(forge): migração 0.5.0")
        antes = git("rev-parse", "HEAD", cwd=self.tmp).stdout
        r2 = self.upgrade()
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(git("rev-parse", "HEAD", cwd=self.tmp).stdout, antes)
        self.assertEqual(git("status", "--porcelain", cwd=self.tmp).stdout, "")
        # a própria migração é idempotente quando rodada direto sobre o resultado
        subprocess.run([sys.executable, str(RAIZ / "migrations/0.5.0/migrar"), str(self.tmp)], check=True)
        self.assertEqual(git("status", "--porcelain", cwd=self.tmp).stdout, "")

    def test_migracao_so_acrescenta_ao_gitignore(self):
        for antes, depois in (("a/\r\nb/\r\n", "a/\r\nb/\r\n.forge/run/\r\n"), ("a/\r\nb/", "a/\r\nb/\r\n.forge/run/\r\n"),
                              ("a/\n", "a/\n.forge/run/\n"), ("a/\n.forge/run/\n", "a/\n.forge/run/\n")):
            with self.subTest(antes=antes):
                (self.tmp / ".gitignore").write_bytes(antes.encode())
                subprocess.run([sys.executable, str(RAIZ / "migrations/0.5.0/migrar"), str(self.tmp)],
                               check=True, capture_output=True)
                self.assertEqual((self.tmp / ".gitignore").read_bytes().decode(), depois)

    def test_recusa_arvore_suja(self):
        (self.tmp / "sujeira.txt").write_text("x", encoding="utf-8")
        r = self.upgrade()
        self.assertEqual(r.returncode, 2)
        self.assertIn("não está limpa", r.stderr)
        self.assertEqual(git("branch", "--list", "forge/*", cwd=self.tmp).stdout, "")

    def test_simular_nao_grava(self):
        r = self.upgrade("--simular")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("migração 0.5.0", r.stdout)
        self.assertEqual(git("branch", "--show-current", cwd=self.tmp).stdout.strip(), "develop")
        self.assertEqual(git("status", "--porcelain", cwd=self.tmp).stdout, "")
        self.assertFalse((self.tmp / ".forge").exists())

    def test_nunca_parte_da_main(self):
        git("branch", "-m", "main", cwd=self.tmp)
        r = self.upgrade()
        self.assertEqual(r.returncode, 2)
        self.assertEqual(git("branch", "--list", "forge/*", cwd=self.tmp).stdout, "")
        self.assertEqual(git("branch", "--show-current", cwd=self.tmp).stdout.strip(), "main")


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

    def test_job_versao_cobre_develop_e_main(self):
        """ADR 0006: develop exige linha em [Não publicado]; main exige versão nova e changelog fechado."""
        texto = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for trecho in ("base_ref == 'develop' || github.base_ref == 'main'", "[Não publicado]", "a <= b"):
            self.assertIn(trecho, texto)

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


class VerificarContribuicao(unittest.TestCase):
    """scripts/verificar-contribuicao.sh barra segredo e caminho pessoal no diff contra a base."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-contrib-"))
        git("init", "-q", "-b", "trabalho", cwd=self.tmp)
        git("config", "user.email", "t@example.com", cwd=self.tmp)
        git("config", "user.name", "teste", cwd=self.tmp)
        (self.tmp / "base.txt").write_text("base\n")
        git("add", "base.txt", cwd=self.tmp)
        git("commit", "-q", "-m", "base", cwd=self.tmp)
        git("update-ref", "refs/remotes/origin/develop", "HEAD", cwd=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def verificar(self, nome, conteudo):
        (self.tmp / nome).write_text(conteudo)
        git("add", nome, cwd=self.tmp)
        git("commit", "-q", "-m", "muda", cwd=self.tmp)
        return subprocess.run(["bash", str(RAIZ / "scripts/verificar-contribuicao.sh")], cwd=self.tmp,
                              env=ambiente_limpo(), capture_output=True, text=True)

    def test_diff_limpo_passa(self):
        r = self.verificar("nota.md", "Melhoria sem dados.\nExemplo: /home/<usuario>/x\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_exemplo_marcado_passa(self):
        r = self.verificar("nota.md", "caminho /home/" + "fulano/x forge:exemplo\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_segredos_e_caminhos_falham(self):
        casos = {
            "chave sk": "k = sk" + "-" + "a" * 24,
            "token ghp": "t = ghp" + "_" + "b" * 24,
            "pat": "t = github" + "_pat_" + "c" * 24,
            "aws": "a = AKIA" + "D" * 16,
            "chave privada": "-----" + "BEGIN RSA PRIVATE KEY-----",
            "senha": "pass" + "word=" + "hunter22",
            "caminho pessoal": "cd /home/" + "fulano/projeto",
        }
        for rotulo, linha in casos.items():
            with self.subTest(caso=rotulo):
                r = self.verificar("n.md", linha + "\n")
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("n.md:1", r.stdout)
                self.assertNotIn(linha, r.stdout + r.stderr, "o valor não pode ser impresso")

    def test_arquivo_env_falha(self):
        r = self.verificar(".env", "X=1\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn(".env", r.stdout)

    def test_base_inexistente(self):
        r = subprocess.run(["bash", str(RAIZ / "scripts/verificar-contribuicao.sh"), "nao-existe"],
                           cwd=self.tmp, env=ambiente_limpo(), capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


def carregar_forge_check():
    carregador = importlib.machinery.SourceFileLoader("forge_check_teste", str(RAIZ / "bin/forge-check"))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
    carregador.exec_module(modulo)
    return modulo


class ForgeCheck(unittest.TestCase):
    """ADR 0004: validador do contrato entre agentes, em um projeto git temporário."""

    REVIEW = ("tipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\n"
              "parecer: {p}\nrevisor: forge:tech-lead\ndata: 2026-10-12\n")
    QA = ("tipo: qa\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: {p}\n"
          "escopo: completo\nbugs_criticos: 0\nbugs_altos: {a}\nbugs_medios: {m}\nbugs_baixos: 0\n"
          "data: 2026-10-12\n{extra}")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-check-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git("init", "-q", "-b", "melhoria/x", cwd=self.tmp)
        git("config", "user.email", "t@example.com", cwd=self.tmp)
        git("config", "user.name", "Teste", cwd=self.tmp)
        self.escrever("src/app.txt", "v1\n")
        git("add", "-A", cwd=self.tmp)
        git("commit", "-q", "-m", "base", cwd=self.tmp)

    def escrever(self, rel, texto):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")

    def head(self):
        return git("rev-parse", "HEAD", cwd=self.tmp).stdout.strip()

    def commitar(self):
        git("add", "-A", cwd=self.tmp)
        git("commit", "-q", "-m", "mudanca", cwd=self.tmp)

    def pareceres(self, commit, p="aprovado", a=0, m=0, extra=""):
        self.escrever("docs/reviews/p1.md", "---\n" + self.REVIEW.format(c=commit, p=p) + "---\n# r\n")
        self.escrever("docs/qa/p1.md", "---\n" + self.QA.format(c=commit, p=p, a=a, m=m, extra=extra) + "---\n# q\n")

    def check(self, *args):
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "--raiz", str(self.tmp), *args],
                           env=ambiente_limpo(), capture_output=True, text=True)
        return r.returncode, r.stdout

    def test_docs_validos_e_ignorados(self):
        self.pareceres(self.head())
        self.escrever("docs/qa/antigo.md", "---\ntipo: qa\ncontrato: 0\n---\nsem campos\n")
        self.escrever("docs/reviews/_modelo.md", "sem frontmatter\n")
        self.escrever("docs/architecture/features/f.md", "---\ntipo: plano-tecnico\ncontrato: 1\npedido: p1\n"
                      "estado: vigente\nux: docs/ux/f.md\nadrs: [0001, 0002]\nagentes: [node-backend]\n---\n")
        self.assertEqual(self.check("docs"), (0, ""))

    def test_docs_invalidos(self):
        casos = {
            "sem frontmatter": ("docs/reviews/a.md", "texto\n", "frontmatter"),
            "aninhamento": ("docs/reviews/a.md", "---\ntipo: review\ncontrato: 1\n  filho: x\n---\n", "frontmatter"),
            "campo ausente": ("docs/reviews/a.md", "---\ntipo: review\ncontrato: 1\n---\n", "pedido: obrigatório"),
            "parecer inválido": ("docs/reviews/a.md", "---\n" + self.REVIEW.format(c="abc1234", p="talvez") + "---\n",
                                 "parecer: use aprovado"),
            "qa com bug alto": ("docs/qa/a.md", "---\n" + self.QA.format(c="abc1234", p="aprovado", a=1, m=0, extra="") + "---\n",
                                "bugs_altos: parecer aprovado exige 0"),
            "qa médio sem aceite": ("docs/qa/a.md", "---\n" + self.QA.format(c="abc1234", p="aprovado", a=0, m=2, extra="") + "---\n",
                                    "aceite_usuario"),
            "plano com estado ruim": ("docs/architecture/features/a.md",
                                      "---\ntipo: plano-tecnico\ncontrato: 1\npedido: p\nestado: x\nux: u\nadrs: []\nagentes: [a]\n---\n",
                                      "estado: use proposta"),
        }
        for nome, (rel, texto, trecho) in casos.items():
            with self.subTest(nome):
                self.escrever(rel, texto)
                codigo, saida = self.check("docs")
                self.assertEqual(codigo, 1)
                self.assertIn(trecho, saida)
                self.assertRegex(saida, r"^\S+\.md: \S+: .+ \((R-[A-Z]+|ADR-0004)\)$".replace("^", "(?m)^", 1))
                (self.tmp / rel).unlink()

    def test_qa_medio_com_aceite_vale(self):
        self.pareceres(self.head(), m=2, extra="aceite_usuario: sim\n")
        self.assertEqual(self.check("docs"), (0, ""))

    def kanban(self, corpo):
        cab = "| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"
        self.escrever("KANBAN.md", "# Quadro\n\n" + corpo.format(cab=cab))

    def test_kanban_modelo_do_forge_e_valido(self):
        self.assertEqual(subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "--raiz",
                                         str(RAIZ / "templates/projeto"), "kanban"], capture_output=True, text=True).returncode, 0)

    def test_kanban_valido(self):
        self.kanban("## QA (WIP 2)\n{cab}| C1 | a | p1 | forge:qa-engineer | d | d | |\n| C2 | b | p1 | usuário | d | d | |\n"
                    "## Em andamento (WIP 1 por agente)\n{cab}| C3 | c | p1 | forge:node-backend | d | d | |\n")
        self.assertEqual(self.check("kanban"), (0, ""))

    def test_kanban_invalido(self):
        casos = {
            "id repetido": ("## Pronto\n{cab}| C1 | a | p | usuário | d | d | |\n| C1 | b | p | usuário | d | d | |\n", "repetido"),
            "responsável": ("## Pronto\n{cab}| C1 | a | p | Fulano | d | d | |\n", "Responsável"),
            "wip da coluna": ("## QA (WIP 1)\n{cab}| C1 | a | p | usuário | d | d | |\n| C2 | b | p | usuário | d | d | |\n", "limite 1"),
            "wip por agente": ("## Em andamento (WIP 1 por agente)\n{cab}| C1 | a | p | forge:node-backend | d | d | |\n"
                               "| C2 | b | p | forge:node-backend | d | d | |\n", "por agente"),
            "colunas": ("## Pronto\n| ID | Cartão |\n|---|---|\n", "colunas diferentes"),
        }
        for nome, (corpo, trecho) in casos.items():
            with self.subTest(nome):
                self.kanban(corpo)
                codigo, saida = self.check("kanban")
                self.assertEqual(codigo, 1)
                self.assertIn(trecho, saida)
                self.assertIn("(R-WIP)", saida)

    def test_pr_aprovado_no_head(self):
        self.pareceres(self.head())
        self.assertEqual(self.check("pr", "p1"), (0, ""))

    def test_raiz_depois_do_subcomando_e_git_isolado(self):
        self.pareceres(self.head())
        self.commitar()
        env = dict(ambiente_limpo(), GIT_DIR=str(self.tmp / "nao-existe"))  # GIT_* herdadas não valem
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "pr", "p1", "--raiz", str(self.tmp)],
                           env=env, capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_aviso_de_migracao_pendente(self):
        fc = carregar_forge_check()
        plugin = self.tmp / "plugin"
        (plugin / ".claude-plugin").mkdir(parents=True)
        (plugin / ".claude-plugin/plugin.json").write_text('{"version": "0.6.0"}', encoding="utf-8")
        for v in ("0.5.0", "0.6.0", "0.7.0"):
            (plugin / "migrations" / v).mkdir(parents=True)
            (plugin / "migrations" / v / "migrar").write_text("", encoding="utf-8")
        fc.PLUGIN = plugin
        self.assertEqual(fc.migracao_pendente(self.tmp), [])  # sem .forge/versao: não é projeto do Forge
        self.escrever(".forge/versao", "0.5.0\n")
        self.assertEqual(fc.migracao_pendente(self.tmp), ["0.6.0"])
        self.escrever(".forge/versao", "0.6.0\n")
        self.assertEqual(fc.migracao_pendente(self.tmp), [])

    def test_pr_sem_pareceres(self):
        codigo, saida = self.check("pr", "p1")
        self.assertEqual(codigo, 1)
        self.assertIn("(R-REVIEW)", saida)
        self.assertIn("(R-QA)", saida)

    def test_pr_commit_valido_se_so_parecer_e_quadro_mudaram(self):
        base = self.head()
        self.pareceres(base)
        self.escrever("KANBAN.md", "# Quadro\n")
        self.commitar()
        self.assertEqual(self.check("pr", "p1"), (0, ""))

    def test_pr_commit_desatualizado(self):
        base = self.head()
        self.pareceres(base)
        self.escrever("src/app.txt", "v2\n")
        self.commitar()
        codigo, saida = self.check("pr", "p1")
        self.assertEqual(codigo, 1)
        self.assertIn("src/app.txt mudou depois do parecer", saida)
        self.assertIn("(R-QA)", saida)

    def test_pr_parecer_reprovado_ou_commit_inexistente(self):
        self.pareceres(self.head(), p="reprovado")
        self.assertIn("não é aprovado", self.check("pr", "p1")[1])
        self.pareceres("deadbeef")
        self.assertIn("commit não existe", self.check("pr", "p1")[1])

    def test_pr_com_ref_le_os_pareceres_da_branch(self):
        git("switch", "-q", "-c", "develop", cwd=self.tmp)
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        self.escrever("src/app.txt", "v2\n")
        self.commitar()
        self.pareceres(self.head())
        self.commitar()
        git("switch", "-q", "develop", cwd=self.tmp)
        self.assertEqual(self.check("pr", "p1", "--ref", "melhoria/x"), (0, ""))
        self.assertIn("sem parecer", self.check("pr", "p1")[1])

    def test_pr_qa_com_bug_alto_falha(self):
        self.pareceres(self.head(), a=1)
        codigo, saida = self.check("pr", "p1")
        self.assertEqual(codigo, 1)
        self.assertIn("bugs_altos", saida)


class Orcamento(unittest.TestCase):
    def test_tamanho_dos_prompts(self):
        lim = CONFIG["limite_linhas"]
        for p in agentes_do_plugin():
            with self.subTest(agente=p.name):
                self.assertLessEqual(len(p.read_text(encoding="utf-8").splitlines()), lim["agente"])
        for p in skills_do_plugin():
            with self.subTest(skill=p.parent.name):
                self.assertLessEqual(len(p.read_text(encoding="utf-8").splitlines()), lim["skill"])


if __name__ == "__main__":
    unittest.main()


class Transcricoes(unittest.TestCase):
    """ADR 0007: verificador offline de sessões gravadas, sem IA e sem rede."""

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "transcricao", *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout

    def caso(self, nome, *args):
        return self.rodar("verificar", str(RAIZ / "tests/transcricoes" / nome), *args)

    def test_sessao_correta_passa(self):
        self.assertEqual(self.caso("ok.jsonl"), (0, ""))

    def test_viola_teto(self):
        cod, saida = self.caso("viola-teto.jsonl")
        self.assertEqual(cod, 1)
        self.assertEqual(saida.strip(), "transcricao: R-TETO: 4 agentes em segundo plano, teto 3 (evento 4)")

    def test_teto_configuravel(self):
        self.assertEqual(self.caso("viola-teto.jsonl", "--teto", "4")[0], 0)

    def test_viola_main(self):
        cod, saida = self.caso("viola-main.jsonl")
        self.assertEqual(cod, 1)
        self.assertEqual(saida.count("R-MAIN"), 2)

    def test_pr_sem_review_nem_qa_e_prompt_incompleto(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        arq = tmp / "t.jsonl"
        secoes = {n: n != "Ler" for n in ("Objetivo", "Ler", "Entregar", "Decisões e restrições", "Pronto quando", "Relatório")}
        linhas = [{"formato": "forge-transcricao/1", "origem": "x"},
                  {"ev": "agente", "t": "", "id": "a1", "tipo": "forge:node-backend", "bg": False, "secoes": secoes},
                  {"ev": "cmd", "t": "", "cmd": "gh pr create", "branch": "<branch>"}]
        arq.write_text("\n".join(json.dumps(l) for l in linhas) + "\n", encoding="utf-8")
        cod, saida = self.rodar("verificar", str(arq))
        self.assertEqual(cod, 1)
        for rid in ("PROMPT-PADRAO", "R-REVIEW", "R-QA"):
            self.assertIn(rid, saida)

    def test_anonimizador_so_deixa_a_lista_de_permissao(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        prompt = ("## Objetivo\nProjeto Zephyrus de ana.silva@exemplo.org em /home/ana/Zephyrus\n## Ler\nx\n"
                  "## Entregar\nx\n## Decisões e restrições\nx\n## Pronto quando\nx\n## Relatório\nx")
        brutos = [
            {"type": "user", "timestamp": "t0", "version": "9.9.9", "message": {"content": "segredo do usuario Zephyrus"}},
            {"type": "assistant", "timestamp": "t1", "gitBranch": "melhoria/zephyrus-x", "message": {"content": [
                {"type": "text", "text": "texto livre do assistente em /home/ana/"},
                {"type": "tool_use", "id": "u1", "name": "Agent", "input": {
                    "subagent_type": "zephyrus-dev", "run_in_background": "true", "prompt": prompt}},
                {"type": "tool_use", "id": "u2", "name": "Bash", "input": {
                    "command": "cd /home/ana/Zephyrus && git -C /home/ana/Zephyrus push origin melhoria/zephyrus-x "
                               "&& git config user.email ana.silva@exemplo.org && gh pr create --body 'Zephyrus'"}},
                {"type": "tool_use", "id": "u3", "name": "Read", "input": {"file_path": "/home/ana/Zephyrus/segredo.txt"}}]}},
            {"type": "user", "timestamp": "t2", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "u1", "content": "Async agent launched /home/ana/Zephyrus"}]}},
            {"type": "queue-operation", "timestamp": "2026-01-01T10:00:00.123Z", "content":
                "<task-notification><tool-use-id>u1</tool-use-id><summary>ana.silva@exemplo.org</summary></task-notification>"},
        ]
        entrada, saida = tmp / "e.jsonl", tmp / "s.jsonl"
        entrada.write_text("\n".join(json.dumps(b) for b in brutos), encoding="utf-8")
        self.assertEqual(self.rodar("anonimizar", str(entrada), str(saida))[0], 0)
        texto = saida.read_text(encoding="utf-8")
        for proibido in ("ana", "@", "/home", "Zephyrus", "zephyrus", "segredo", "texto livre", "Read"):
            self.assertNotIn(proibido, texto)
        eventos = [json.loads(l) for l in texto.splitlines()][1:]
        self.assertEqual([e["ev"] for e in eventos], ["agente", "cmd", "cmd", "fim"])
        self.assertEqual(eventos[0]["tipo"], "<agente>")
        self.assertEqual([e["cmd"] for e in eventos[1:3]], ["git push <branch>", "gh pr create"])
        self.assertTrue(all(eventos[0]["secoes"].values()))
        self.assertEqual([e["t"] for e in eventos], ["", "", "", "2026-01-01T10:00:00.123Z"])  # "t1" não é ISO 8601

    def test_linha_malformada_vira_violacao(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        arq = tmp / "t.jsonl"
        arq.write_text("\n".join([json.dumps({"formato": "forge-transcricao/1", "origem": "x"}), "{quebrado",
                                  json.dumps({"t": ""}), json.dumps({"ev": "fim", "t": "ontem", "id": "a1"}),
                                  json.dumps({"ev": "cmd", "t": "", "branch": "main"}),
                                  json.dumps({"ev": "fim", "t": "2026-01-01T10:00:00Z", "id": "a1"})]), encoding="utf-8")
        cod, saida = self.rodar("verificar", str(arq))
        self.assertEqual(cod, 1)
        self.assertEqual(saida.splitlines(), [
            "transcricao: formato: evento 1 inválido: não é JSON",
            "transcricao: formato: evento 2 inválido: `ev` deve ser um de agente, fim, cmd",
            "transcricao: formato: evento 3 inválido: `t` deve ser data e hora ISO 8601 ou vazio",
            "transcricao: formato: evento 4 inválido: `cmd` ausente ou de tipo errado"])
        arq.write_text("não é json\n", encoding="utf-8")
        self.assertEqual(self.rodar("verificar", str(arq))[0], 1)
