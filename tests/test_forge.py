"""Testes estruturais do Forge (só biblioteca padrão; rode com `python3 -m unittest discover -s tests -v`).

Garantem a integridade da fábrica a cada mudança: manifestos, agentes, skills, referências,
neutralidade (nada específico de um projeto), regras invioláveis, inicializador e hook de git.
"""
import hashlib
import importlib.machinery
import importlib.util
import contextlib
import io
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from neutralidade import termos_achados  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

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


def minimo(itens, n, rotulo):
    """Guarda contra teste que passa em silêncio: o que o teste percorre não pode estar vazio.

    `n` é o tamanho de hoje menos uma margem pequena; pasta renomeada ou glob que deixou de casar
    derruba o teste em vez de deixá-lo verde sem ter lido nada. Devolve a lista para encadear.
    """
    itens = list(itens)
    if len(itens) < n:
        raise AssertionError(f"{rotulo}: {len(itens)} itens, esperava ao menos {n} (pasta ou glob vazio?)")
    return itens


def agentes_do_plugin():
    """Todo .md de agents/ e de stacks/*/agents/ (ADR 0001)."""
    return minimo(sorted(AGENTES.glob("*.md")) + sorted(STACKS.glob("*/agents/*.md")), 7, "agentes do plugin")


def skills_do_plugin():
    return minimo(sorted(SKILLS.glob("*/SKILL.md")) + sorted(STACKS.glob("*/skills/*/SKILL.md")), 11, "skills do plugin")


def arquivos_texto():
    achados = []
    for pasta in ("agents", "skills", "stacks", "docs", "templates", "bin", "scripts", "hooks", "tests/transcricoes"):
        achados += [p for p in (RAIZ / pasta).rglob("*") if p.is_file()]
    return minimo(achados, 150, "arquivos de texto varridos")


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
        for a in minimo(self.manifesto["agents"], 7, "agentes do manifesto"):
            with self.subTest(agente=a):
                self.assertTrue(a.startswith("./") and a.endswith(".md"))
                self.assertTrue((RAIZ / a).is_file(), f"{a} listado e inexistente")
        existentes = {p.resolve() for p in agentes_do_plugin()}
        self.assertEqual({p.relative_to(RAIZ).as_posix() for p in existentes - listados}, set(), "agente fora do manifesto")
        self.assertEqual(len(listados), len(self.manifesto["agents"]), "agente listado duas vezes")

    def test_skills_de_stack_listadas_e_vice_versa(self):
        listadas = {(RAIZ / s).resolve() for s in self.manifesto["skills"]}
        for s in minimo(self.manifesto["skills"], 1, "skills de stack do manifesto"):
            with self.subTest(skill=s):
                self.assertTrue((RAIZ / s / "SKILL.md").is_file(), f"{s} sem SKILL.md")
        existentes = {p.parent.resolve() for p in minimo(STACKS.glob("*/skills/*/SKILL.md"), 1, "skills de stack em disco")}
        self.assertEqual({p.relative_to(RAIZ).as_posix() for p in existentes - listadas}, set(), "skill de stack fora do manifesto")


class PacotesDeStack(unittest.TestCase):
    """ADR 0001: todo pacote em stacks/<nome>/ tem a mesma forma."""

    def test_stacks_esperadas_existem(self):
        for nome, itens in minimo(CONFIG["stacks_obrigatorias"].items(), 1, "stacks obrigatórias"):
            with self.subTest(stack=nome):
                self.assertEqual({p.stem for p in (STACKS / nome).glob("agents/*.md")}, set(itens["agentes"]))
                self.assertEqual({p.parent.name for p in (STACKS / nome).glob("skills/*/SKILL.md")}, set(itens["skills"]))

    def test_forma_do_pacote(self):
        pacotes = sorted(p for p in STACKS.iterdir() if p.is_dir())
        self.assertTrue(pacotes, "stacks/ vazia")
        minimo(pacotes, 1, "pacotes em stacks/")
        for pacote in pacotes:
            with self.subTest(stack=pacote.name):
                self.assertRegex(pacote.name, r"^[a-z0-9-]+$")
                self.assertTrue(list(pacote.glob("skills/*/SKILL.md")), "stack sem skills")
                self.assertTrue((pacote / "seguranca.md").is_file(), "falta seguranca.md")
                self.assertTrue((pacote / "pronto.md").is_file(), "falta pronto.md")
                pronto = (pacote / "pronto.md").read_text(encoding="utf-8")
                self.assertRegex(pronto, r"(?m)^Comando sugerido: `[^`]+`", "pronto.md sem 'Comando sugerido: `...`'")
                if (pacote / "pesados.json").exists():
                    pesados = json.loads((pacote / "pesados.json").read_text(encoding="utf-8"))
                    self.assertTrue(isinstance(pesados, list) and all(isinstance(x, str) and x.strip() for x in pesados))
                extras = {p.name for p in pacote.iterdir()} - {"agents", "skills", "seguranca.md", "pronto.md", "pesados.json"}
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

    def test_conferente_so_leitura(self):
        """R-PROVA e R-BRIEF: o conferente confere sem escrever. Sem ferramenta de escrita no frontmatter, em haiku, e
        com o papel só de leitura na política do hook `conformidade` (o Bash dele fica na lista branca de leitura)."""
        fm = frontmatter(AGENTES / "conferente.md")
        ferramentas = {t.strip() for t in fm["tools"].split(",")}
        self.assertFalse(ferramentas & {"Write", "Edit", "MultiEdit", "NotebookEdit", "Agent"}, ferramentas)
        self.assertEqual(fm["model"], "haiku")
        politica = json.loads((RAIZ / "hooks" / "conformidade.json").read_text(encoding="utf-8"))
        papeis = [p for p, tipos in politica["papeis"].items() if "forge:conferente" in tipos]
        self.assertEqual(papeis, ["conferente"])
        self.assertIn("conferente", politica["so_leitura"]["papeis"])
        for papel in politica["so_leitura"]["papeis"]:
            with self.subTest(papel=papel):
                self.assertFalse([a for a, quem in politica["acoes"].items() if papel in quem])
                self.assertFalse([c["caminho"] for c in politica["caminhos"] if papel in c["quem"]])

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
        self.assertEqual(citados, {p.stem for p in minimo(AGENTES.glob("*.md"), 5, "agentes do núcleo")} - {"jarvis"})
        self.assertIn("stacks/<stack>/agents/", tabela)


class Skills(unittest.TestCase):
    def test_frontmatter_valido(self):
        for p in skills_do_plugin():
            with self.subTest(skill=p.parent.name):
                fm = frontmatter(p)
                self.assertEqual(fm.get("name"), p.parent.name)
                self.assertGreater(len(fm.get("description", "")), 40)


    def test_qa_tem_vermelho_antes_do_verde_e_mutacao(self):
        texto = (SKILLS / "qa-testing" / "SKILL.md").read_text(encoding="utf-8")
        for titulo in ("## Vermelho antes do verde", "## Mutação no código alterado"):
            self.assertIn(titulo, texto)


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
        entradas = minimo(CONFIG["termos_proibidos_hash"], 10, "termos proibidos por hash")
        for p in arquivos_texto():
            texto = p.read_text(encoding="utf-8", errors="ignore")
            with self.subTest(arquivo=str(p.relative_to(RAIZ))):
                self.assertEqual(termos_achados(texto, entradas), set(), "termo de projeto (compare por hash em tests/config.json)")

    def test_detector_por_hash(self):
        """Sem o nome em claro: monta a entrada a partir de uma palavra neutra e confere cada tipo de casamento."""
        sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
        palavra = [{"tipo": "palavra", "n": 5, "sha256": sha("zebra")}]
        trecho = [{"tipo": "trecho", "n": 5, "sha256": sha("zebra")}]
        par = [{"tipo": "par", "n": [2, 3], "sha256": sha("zebra")}]
        self.assertTrue(termos_achados("a Zebra.", palavra))
        self.assertFalse(termos_achados("zebras", palavra))
        self.assertTrue(termos_achados("minhaZEBRAs", trecho))
        self.assertTrue(termos_achados("ze bra", par) and termos_achados("zebra", trecho))
        self.assertFalse(termos_achados("ze  bra", par))
        self.assertFalse(termos_achados("ze-bra", par))


NUCLEO_MIN = 75  # arquivos do núcleo (menos os ignorados) lidos pelo teste de ausência de termos de stack


class NeutralidadeDoNucleo(unittest.TestCase):
    """ADR 0001: linguagem, framework e ferramenta só em stacks/ (e nas exceções explícitas do config)."""

    def setUp(self):
        self.cfg = CONFIG["neutralidade_nucleo"]

    def test_detector_acha_termo_de_stack(self):
        termos = [re.compile(t) for t in self.cfg["termos"]]
        self.assertTrue(any(t.search("Use React com TypeScript") for t in termos))
        self.assertFalse(any(t.search("Verifique o nó da árvore; reagir ao evento") for t in termos))

    def test_nucleo_sem_termos_de_stack(self):
        termos = minimo((re.compile(t) for t in self.cfg["termos"]), 14, "termos de stack do núcleo")
        varridos = 0
        for pasta in self.cfg["pastas"]:
            for p in sorted((RAIZ / pasta).rglob("*")):
                rel = p.relative_to(RAIZ).as_posix()
                if not p.is_file() or any(rel.startswith(i) for i in self.cfg["ignorar"]):
                    continue
                varridos += 1
                texto = p.read_text(encoding="utf-8", errors="ignore")
                for t in termos:
                    if t.pattern in self.cfg["excecoes"].get(rel, []):
                        continue
                    with self.subTest(arquivo=rel, termo=t.pattern):
                        achado = t.search(texto)
                        self.assertIsNone(achado, f"{rel}: stack no núcleo ({achado and achado.group(0)}); mova para stacks/ ou registre exceção em tests/config.json")
        minimo(range(varridos), NUCLEO_MIN, "arquivos do núcleo varridos")

    def test_stack_declarada_no_modelo_e_no_init(self):
        self.assertIn("{{STACK}}", (RAIZ / "templates/projeto/CLAUDE.md").read_text(encoding="utf-8"))


class RegrasInviolaveis(unittest.TestCase):
    """Se alguém apagar uma regra da fábrica por engano, o CI quebra."""

    def test_trechos_obrigatorios(self):
        invariantes = minimo(CONFIG["invariantes"].items(), 23, "arquivos com invariantes")
        minimo((t for _, ts in invariantes for t in ts), 95, "trechos invariantes")
        for rel, trechos in invariantes:
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
        minimo(fontes, 13, "regras em docs/regras")
        alvos = [p for pasta in self.pastas if (RAIZ / pasta).is_dir()
                 for p in sorted((RAIZ / pasta).rglob("*")) if p.is_file()]
        minimo(alvos, 110, "arquivos comparados pelo anti-duplicação")
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
        self.regras = {p.stem: p for p in minimo(sorted(REGRAS.glob("R-*.md")), 13, "regras em docs/regras")}

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
        minimo(origens, 45, "arquivos que citam IDs de regra")
        for p in origens:
            for rid in set(re.findall(r"\bR-[A-Z][A-Z0-9-]*\b", p.read_text(encoding="utf-8", errors="ignore"))):
                with self.subTest(arquivo=str(p.relative_to(RAIZ)), regra=rid):
                    self.assertTrue(rid in self.regras, f"{rid} não existe em docs/regras/")


def ambiente_limpo():
    """Ambiente sem as variáveis GIT_* herdadas (um hook do git exporta GIT_DIR e afins) e sem config
    global/de sistema: o git dos testes só enxerga o repositório temporário em que roda. Sem `CLAUDE_PROJECT_DIR`
    (a raiz da sessão que roda os testes): o hook decide a sessão por ela, e cada fixture declara a sua.
    Sem as variáveis `FORGE_*` (ex.: `FORGE_ABERTURA_FEITA`, que o `jarvis-forge` exporta na sessão aberta por ele):
    elas mudam o comportamento dos scripts, e quem precisa de uma a define de propósito depois, em `env`."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    # O git 2.55 dispara `maintenance run --auto --detach` depois do commit; o repack em segundo plano escreve
    # (maintenance.lock, tmp de pack) enquanto o tearDown apaga o repositório temporário e o rmtree falha.
    env.update(GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="maintenance.auto", GIT_CONFIG_VALUE_0="false",
               GIT_CONFIG_KEY_1="gc.auto", GIT_CONFIG_VALUE_1="0")
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
        for arq in minimo(modelo.rglob("*"), 27, "entradas do modelo de projeto"):
            if arq.is_file():
                self.assertTrue((self.tmp / arq.relative_to(modelo)).is_file(), arq.relative_to(modelo))
        claude_md = (self.tmp / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("# Demo", claude_md)
        self.assertIn("`make pronto`", claude_md)
        for arq in minimo(self.tmp.rglob("*"), 27, "entradas do projeto gerado"):
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


    def test_pesados_padrao_vem_da_stack_e_o_nucleo_nao_traz_lista(self):
        self.assertEqual(json.loads((RAIZ / "templates/projeto/.forge/config.json").read_text(encoding="utf-8"))["pesados"], [])
        self.rodar()
        da_stack = json.loads((RAIZ / "stacks/node-react/pesados.json").read_text(encoding="utf-8"))
        self.assertTrue(da_stack)
        config = self.tmp / ".forge/config.json"
        self.assertEqual(json.loads(config.read_text(encoding="utf-8"))["pesados"], da_stack)
        config.write_text('{"pesados": ["meu-comando"]}\n', encoding="utf-8")  # config do projeto não é tocada
        self.rodar()
        self.assertEqual(json.loads(config.read_text(encoding="utf-8"))["pesados"], ["meu-comando"])

    def test_grava_versao_e_config_idempotente(self):
        self.rodar()
        plugin = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertEqual((self.tmp / ".forge/versao").read_text(encoding="utf-8").strip(), plugin)
        self.assertEqual(json.loads((self.tmp / ".forge/config.json").read_text(encoding="utf-8")).get("teto_agentes"), None)
        self.rodar()
        self.assertEqual((self.tmp / ".gitignore").read_text(encoding="utf-8").splitlines().count(".forge/run/"), 1)

    def test_projeto_antigo_fica_com_versao_zero(self):
        (self.tmp / "KANBAN.md").write_text("# Quadro\n", encoding="utf-8")
        saida = self.rodar().stdout
        self.assertEqual((self.tmp / ".forge/versao").read_text(encoding="utf-8"), "0.0.0\n")
        self.assertIn("forge-upgrade", saida)
        self.rodar()
        self.assertEqual((self.tmp / ".forge/versao").read_text(encoding="utf-8"), "0.0.0\n")

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
        self.assertEqual(json.loads((self.tmp / ".forge/config.json").read_text(encoding="utf-8")).get("teto_agentes"), None)
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


class Migracao070(unittest.TestCase):
    """Migração 0.7.0: só `teto_agentes` igual a 3 sai do config; fixtures antes/depois em tests/migracoes/0.7.0/."""

    def migrar(self, projeto):
        return subprocess.run([sys.executable, str(RAIZ / "migrations/0.7.0/migrar"), str(projeto)],
                              capture_output=True, text=True)

    def test_fixtures_antes_e_depois(self):
        casos = sorted((RAIZ / "tests/migracoes/0.7.0").glob("*.json"))
        self.assertGreaterEqual(len(casos), 5)
        minimo(casos, 5, "fixtures de migração 0.7.0")
        for caso in casos:
            dados = json.loads(caso.read_text(encoding="utf-8"))
            with self.subTest(caso=caso.stem), tempfile.TemporaryDirectory() as tmp:
                config = Path(tmp) / ".forge/config.json"
                config.parent.mkdir()
                config.write_text(json.dumps(dados["antes"]), encoding="utf-8")
                r = self.migrar(tmp)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn(dados["saida"], r.stdout)
                self.assertEqual(json.loads(config.read_text(encoding="utf-8")), dados["depois"])
                if not dados["saida"]:
                    self.assertEqual(config.read_text(encoding="utf-8"), json.dumps(dados["antes"]))  # nem reformata
                depois = config.read_bytes()
                self.assertEqual(self.migrar(tmp).stdout, "")  # idempotente
                self.assertEqual(config.read_bytes(), depois)

    def test_config_ausente_ou_ilegivel_nao_muda(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.migrar(tmp).returncode, 0)
            self.assertFalse((Path(tmp) / ".forge/config.json").exists())
            config = Path(tmp) / ".forge/config.json"
            config.parent.mkdir()
            config.write_text("{quebrado", encoding="utf-8")
            r = self.migrar(tmp)
            self.assertEqual((r.returncode, config.read_text(encoding="utf-8")), (0, "{quebrado"))
            self.assertIn("ilegível", r.stdout)

    def test_leia_resume_para_o_forge_upgrade(self):
        self.assertIn("teto_agentes", (RAIZ / "migrations/0.7.0/LEIA.md").read_text(encoding="utf-8").splitlines()[2])


class HookPrePush(unittest.TestCase):
    """O hook do modelo de projeto bloqueia a main e respeita o pre-push.local."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.remoto = self.tmp / "remoto.git"
        self.repo = self.tmp / "repo"
        git("init", "-q", "--bare", str(self.remoto), cwd=self.tmp)
        # o receive-pack local não herda GIT_CONFIG_*: sem isto ele dispara a manutenção em segundo plano no remoto
        git("config", "receive.autogc", "false", cwd=self.remoto)
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

    def commit_novo(self, msg, amend=False):
        args = ["commit", "-q", "--allow-empty", "-m", msg] + (["--amend"] if amend else [])
        git(*args, cwd=self.repo)

    def test_fast_forward_passa(self):
        self.assertEqual(self.push("HEAD:feature/ff").returncode, 0)
        self.commit_novo("segundo")
        self.assertEqual(self.push("HEAD:feature/ff").returncode, 0)

    def test_historico_reescrito_e_recusado(self):
        self.assertEqual(self.push("HEAD:feature/rw").returncode, 0)
        self.commit_novo("reescrito", amend=True)
        for refspec in ("--force", "+HEAD:feature/rw"):
            with self.subTest(refspec=refspec):
                args = ["--force", "origin", "HEAD:feature/rw"] if refspec == "--force" else ["origin", refspec]
                r = subprocess.run(["git", "-C", str(self.repo), "push", *args], cwd=self.repo,
                                   env=ambiente_limpo(), capture_output=True, text=True)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("R-VERIFY", r.stderr)

    def test_remoto_com_commit_desconhecido_pede_fetch(self):
        self.assertEqual(self.push("HEAD:feature/u").returncode, 0)
        outro = self.tmp / "outro"
        git("clone", "-q", str(self.remoto), str(outro), cwd=self.tmp)
        for k, v in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
            git("config", k, v, cwd=outro)
        git("checkout", "-q", "feature/u", cwd=outro)
        git("commit", "-q", "--allow-empty", "-m", "de outro clone", cwd=outro)
        self.assertEqual(subprocess.run(["git", "-C", str(outro), "push", "origin", "feature/u"], cwd=outro,
                                        env=ambiente_limpo(), capture_output=True).returncode, 0)
        self.commit_novo("local")  # o remoto avançou e este clone não fez fetch
        r = self.push("HEAD:feature/u")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("git fetch", r.stderr)
        self.assertNotIn("R-VERIFY", r.stderr)

    def test_apagar_branch_passa(self):
        self.assertEqual(self.push("HEAD:feature/del").returncode, 0)
        self.assertEqual(self.push(":feature/del").returncode, 0)

    def test_apagar_tag_passa(self):
        git("tag", "v0", cwd=self.repo)
        self.assertEqual(self.push("v0").returncode, 0)
        self.assertEqual(self.push(":refs/tags/v0").returncode, 0)

    def test_branch_nova_passa(self):
        self.assertEqual(self.push("HEAD:feature/nova").returncode, 0)

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
        for wf in minimo(sorted((RAIZ / ".github" / "workflows").glob("*.yml")), 3, "workflows"):
            for n, linha in enumerate(wf.read_text(encoding="utf-8").splitlines(), 1):
                m = re.search(r"\buses:\s*(\S+)", linha)
                if m and not m.group(1).startswith("./"):
                    with self.subTest(arquivo=wf.name, linha=n):
                        self.assertRegex(m.group(1), r"@[0-9a-f]{40}$", "fixe a ação por SHA de 40 caracteres")

    def test_release_sem_credencial_no_checkout(self):
        """Com `contents: write`, o token não fica gravado no .git enquanto os testes rodam."""
        texto = (RAIZ / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false", texto)

    def test_job_versao_cobre_develop_e_main(self):
        """ADR 0006: develop exige linha em [Não publicado]; main exige versão nova e changelog fechado."""
        texto = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for trecho in ("github.base_ref == 'develop'", "github.base_ref == 'main'", "changelog.d", "a <= b"):
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

    def test_atalhos_do_jarvis_com_ajuda(self):
        """--help mostra o uso e sai com 0; opção desconhecida sai com 2, sem abrir nada."""
        for script in ("jarvis", "jarvis-forge"):
            with self.subTest(script=script):
                r = subprocess.run(["bash", str(RAIZ / "scripts" / script), "--help"], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn(f"Uso: {script} [--sem-tmux]", r.stdout)
                self.assertNotIn("set -", r.stdout)
                r = subprocess.run(["bash", str(RAIZ / "scripts" / script), "--xpto"], capture_output=True, text=True)
                self.assertEqual((r.returncode, r.stdout), (2, ""))
                self.assertIn("--help", r.stderr)


class SandboxDoBash(unittest.TestCase):
    def test_settings_do_forge_com_sandbox_obrigatorio(self):
        cfg = json.loads((RAIZ / ".claude/settings.json").read_text())["sandbox"]
        self.assertIs(cfg["enabled"], True)
        self.assertIs(cfg["failIfUnavailable"], True)
        self.assertIs(cfg["allowUnsandboxedCommands"], False)

    def test_apis_de_modelo_negadas(self):
        negados = json.loads((RAIZ / ".claude/settings.json").read_text())["sandbox"]["network"]["deniedDomains"]
        for dominio in ("api.anthropic.com", "api.openai.com", "generativelanguage.googleapis.com"):
            self.assertIn(dominio, negados)

    def test_deny_write_so_estado_nao_versionado(self):
        # N6: denyWrite em arquivo versionado quebra git pull/checkout/merge no checkout principal.
        deny = json.loads((RAIZ / ".claude/settings.json").read_text())["sandbox"]["filesystem"]["denyWrite"]
        self.assertIn(".forge/", deny)
        r = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, check=True)
        versionados = r.stdout.splitlines()
        for caminho in deny:
            prefixo = caminho if caminho.endswith("/") else None
            travados = [f for f in versionados if f == caminho or (prefixo and f.startswith(prefixo))]
            self.assertEqual(travados, [], f"denyWrite {caminho} cobre arquivo versionado: {travados[:3]}")

    def test_credenciais_do_dono_ilegiveis(self):
        deny = json.loads((RAIZ / ".claude/settings.json").read_text())["sandbox"]["filesystem"]["denyRead"]
        for caminho in ("~/.ssh", "~/.config/gh", "~/.git-credentials"):
            self.assertIn(caminho, deny)

    def test_settings_versionado_nao_tem_env(self):
        # O env tem caminhos da maquina (UID) e config de credencial: fica no settings.local.json.
        texto = (RAIZ / ".claude/settings.json").read_text()
        self.assertNotIn("env", json.loads(texto))
        self.assertNotRegex(texto, r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|GH_TOKEN|-----BEGIN")

    def test_configurar_ambiente_local_gera_env_e_mescla(self):
        script = RAIZ / "scripts/configurar-ambiente-local.sh"
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / ".claude").mkdir()
            destino = raiz / ".claude/settings.local.json"
            destino.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}, "env": {"MINHA": "1"}}))
            ambiente = {**os.environ, "TMPDIR": "/tmp/xyz"}
            for _ in range(2):  # idempotente
                subprocess.run(["bash", str(script), str(raiz)], check=True, capture_output=True, env=ambiente)
            cfg = json.loads(destino.read_text())
            env = cfg["env"]
            self.assertEqual(cfg["permissions"], {"allow": ["Bash(ls)"]})
            self.assertEqual(env["MINHA"], "1")
            self.assertEqual(env["GIT_CONFIG_COUNT"], str(len([k for k in env if k.startswith("GIT_CONFIG_KEY_")])))
            pares = {env[f"GIT_CONFIG_KEY_{i}"] + "=" + env[f"GIT_CONFIG_VALUE_{i}"] for i in range(int(env["GIT_CONFIG_COUNT"]))}
            self.assertIn("url.https://github.com/.insteadOf=git@github.com:", pares)
            self.assertIn("credential.https://github.com.helper=!gh auth git-credential", pares)
            self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
            base = f"/tmp/xyz/claude-{os.getuid()}/cache"
            self.assertEqual(env["npm_config_cache"], f"{base}/pacotes-js")
            self.assertEqual(env["PLAYWRIGHT_BROWSERS_PATH"], f"{base}/playwright")
            linhas = (raiz / ".gitignore").read_text().splitlines()
            self.assertEqual(linhas.count("/.claude/settings.local.json"), 1)
            self.assertNotRegex(destino.read_text(), r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|GH_TOKEN")

    def test_excluded_commands_so_leitura_de_tmux(self):
        excluidos = json.loads((RAIZ / ".claude/settings.json").read_text())["sandbox"]["excludedCommands"]
        self.assertTrue(excluidos)
        for comando in excluidos:
            self.assertRegex(comando, r"^tmux (ls|capture-pane|has-session)\b")
            self.assertNotRegex(comando, r"send-keys|new-session|kill-|run-shell")

    def test_apis_de_modelo_negadas_com_curinga(self):
        negados = json.loads((RAIZ / ".claude/settings.json").read_text())["sandbox"]["network"]["deniedDomains"]
        for dominio in ("*.anthropic.com", "*.openai.com"):
            self.assertIn(dominio, negados)

    def test_validar_plugin_usa_copia_limpa(self):
        texto = (RAIZ / "scripts/validar-plugin.sh").read_text()
        self.assertIn("git ls-files", texto)
        self.assertIn("claude plugin validate", texto)
        self.assertTrue(os.access(RAIZ / "scripts/validar-plugin.sh", os.X_OK))

    def test_estacao_instala_dependencias_do_sandbox(self):
        texto = (RAIZ / "scripts/preparar-estacao.sh").read_text()
        self.assertIn("bubblewrap", texto)
        self.assertIn("socat", texto)

    def test_gitignore_cobre_pontos_de_montagem_sem_ignorar_versionados(self):
        linhas = {l.strip() for l in (RAIZ / ".gitignore").read_text().splitlines()}
        raiz = [".bash_profile", ".bashrc", ".profile", ".zprofile", ".zshrc", ".gitconfig", ".gitmodules",
                ".ripgreprc", ".mcp.json", ".idea", ".vscode", ".forge"]
        # tests/neutralidade.py é versionado (develop, #42): não é ponto de montagem, então não entra aqui.
        claude = ["agents", "commands", "hooks", "skills", "workflows", "output-styles", "routines",
                  "launch.json", "loop.md", "scheduled_tasks.json", "settings.local.json"]
        for padrao in [f"/{n}" for n in raiz] + [f"/.claude/{n}" for n in claude]:
            self.assertIn(padrao, linhas)
        versionados_ignorados = subprocess.run(
            ["git", "ls-files", "-ci", "--exclude-standard"], cwd=RAIZ, capture_output=True, text=True, check=True).stdout
        self.assertEqual(versionados_ignorados.strip(), "", "o .gitignore casa com arquivo versionado")


class JarvisForgeVigente(unittest.TestCase):
    """ADR 0009, seção 4: o jarvis-forge carrega a cópia vigente (clone da origin/develop), não a de trabalho."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self.home = tmp / "home"
        (self.home / "Forge").mkdir(parents=True)
        self.vigente = self.home / ".local/share/forge/vigente"
        self.registro = tmp / "chamadas"
        bin_falso = tmp / "bin"
        bin_falso.mkdir()
        corpos = {
            "claude": 'exit 0',
            "tmux": 'exit 0',
            "git": ('case "$*" in\n'
                    '  *"remote get-url"*) [ -z "${STUB_GIT_SEM_ORIGIN:-}" ] || exit 2; echo https://exemplo.invalido/Forge.git ;;\n'
                    '  "clone "*) mkdir -p "${@: -1}/.git" ;;\n'
                    '  *"rev-parse HEAD"*) [ -n "${STUB_GIT_HEAD_FIXO:-}" ] && echo fixo || wc -l < "$REGISTRO" ;;\n'
                    '  *"rev-list"*) printf "%s" "${STUB_GIT_ADIANTE:-}" ;;\n'
                    '  *"status --porcelain"*) printf "%s" "${STUB_GIT_SUJO:-}" ;;\n'
                    'esac'),
        }
        for nome, corpo in corpos.items():
            falso = bin_falso / nome
            falso.write_text(f'#!/usr/bin/env bash\necho "{nome} $*" >> "{self.registro}"\n{corpo}\n')
            falso.chmod(0o755)
        self.env = ambiente_limpo()
        self.env.update(HOME=str(self.home), PATH=f"{bin_falso}:{self.env['PATH']}")
        self.env["REGISTRO"] = str(self.registro)
        self.env.pop("XDG_DATA_HOME", None)
        self.env.pop("TMUX", None)

    def rodar(self, *args, **env):
        r = subprocess.run(["bash", str(RAIZ / "scripts/jarvis-forge"), *args], env={**self.env, **env},
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        return r

    def chamadas(self):
        return self.registro.read_text().splitlines() if self.registro.exists() else []

    def test_cria_a_copia_vigente_uma_vez_e_nao_toca_depois(self):
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        clones = [c for c in self.chamadas() if c.startswith("git clone")]
        self.assertEqual(len(clones), 1)
        self.assertIn("--branch develop", clones[0])
        self.assertIn(str(self.vigente), clones[0])
        claude = [c for c in self.chamadas() if c.startswith("claude --")]
        self.assertIn(f"--plugin-dir {self.vigente} ", claude[0] + " ")
        self.registro.unlink()
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith("git ") and "remote get-url" not in c
                          and (" clone " in c or " reset " in c or " checkout " in c)], "recriou ou resetou a cópia vigente")
        self.assertIn(f"--plugin-dir {self.vigente} ", [c for c in self.chamadas() if c.startswith("claude --")][0] + " ")

    def test_respeita_xdg_data_home(self):
        outro = Path(self._tmp.name) / "dados"
        r = self.rodar("--sem-tmux", XDG_DATA_HOME=str(outro))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((outro / "forge/vigente/.git").is_dir())
        self.assertFalse(self.vigente.exists())

    def test_atualizar_vigente_limpa_faz_fetch_e_reset_so_nela(self):
        (self.vigente / ".git").mkdir(parents=True)
        r = self.rodar("--atualizar-vigente")
        self.assertEqual(r.returncode, 0, r.stderr)
        git = [c for c in self.chamadas() if c.startswith("git ")]
        self.assertTrue(all(f"-C {self.vigente} " in c or "remote get-url" in c for c in git), git)
        self.assertTrue(any(" fetch " in c for c in git))
        self.assertTrue(any("reset --quiet --hard refs/remotes/origin/develop" in c for c in git))
        self.assertFalse([c for c in self.chamadas() if c.startswith(("claude", "tmux")) and "has-session" not in c],
                         "abriu sessão")

    def test_atualizar_vigente_recusa_mudancas_locais(self):
        (self.vigente / ".git").mkdir(parents=True)
        r = self.rodar("--atualizar-vigente", STUB_GIT_SUJO=" M hooks/conformidade.py\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("mudanças locais", r.stderr)
        self.assertFalse([c for c in self.chamadas() if " reset " in c or " fetch " in c])

    def test_nunca_apaga_diretorio_que_nao_e_clone_do_forge(self):
        """JFV-01: diretório do usuário no caminho da cópia vigente fica intacto, nos dois modos."""
        self.vigente.mkdir(parents=True)
        arquivo = self.vigente / "nao-apagar.txt"
        arquivo.write_text("importante\n")
        for args in (("--sem-tmux",), ("--atualizar-vigente",)):
            with self.subTest(args=args):
                r = self.rodar(*args)
                self.assertEqual(r.returncode, 1, r.stderr)
                self.assertIn("não é um clone do Forge", r.stderr)
                self.assertEqual(arquivo.read_text(), "importante\n")
                self.assertFalse([c for c in self.chamadas() if c.startswith(("claude", "tmux"))])
                self.assertFalse([c for c in self.chamadas() if " clone " in c or " reset " in c])

    def test_recusa_clone_de_outra_origem(self):
        (self.vigente / ".git").mkdir(parents=True)
        (self.vigente / "x.txt").write_text("x")
        # o stub responde a mesma URL para qualquer pasta; força a diferença só na cópia vigente
        git_falso = Path(self.env["PATH"].split(":")[0]) / "git"
        corpo = git_falso.read_text().replace('*"remote get-url"*)',
                                              f'*"-C {self.vigente} remote get-url"*) echo https://outro.invalido/x.git ;;\n  *"remote get-url"*)')
        git_falso.write_text(corpo)
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue((self.vigente / "x.txt").exists())
        self.assertFalse([c for c in self.chamadas() if c.startswith("claude")])

    def test_atualizar_vigente_recusa_commits_locais(self):
        """JFV-02: commit local que não está na origin/develop não é descartado pelo reset."""
        (self.vigente / ".git").mkdir(parents=True)
        r = self.rodar("--atualizar-vigente", STUB_GIT_ADIANTE="a2e58b5 local\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("commits locais", r.stderr)
        self.assertFalse([c for c in self.chamadas() if " reset " in c])  # o fetch vem antes, para conferir com a origin atual

    def test_sem_origin_sugere_dev(self):
        """JFV-03: mensagem do próprio script, sem criar nada."""
        r = self.rodar("--sem-tmux", STUB_GIT_SEM_ORIGIN="1")
        self.assertEqual(r.returncode, 1)
        self.assertIn("não tem o remoto 'origin'", r.stderr)
        self.assertIn("--dev", r.stderr)
        self.assertFalse(self.vigente.exists())

    def test_atualizar_avisa_sessao_aberta_so_se_a_copia_mudou(self):
        (self.vigente / ".git").mkdir(parents=True)
        r = self.rodar("--atualizar-vigente")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("tmux has-session -t jarvis-Forge", "\n".join(self.chamadas()))
        self.assertIn("reinicie", r.stderr)
        self.registro.unlink()
        r = self.rodar("--atualizar-vigente", STUB_GIT_HEAD_FIXO="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("reinicie", r.stderr)

    def test_dev_com_atualizar_vigente_sai_com_2(self):
        r = self.rodar("--dev", "--atualizar-vigente")
        self.assertEqual(r.returncode, 2)
        self.assertIn("não combinam", r.stderr)
        self.assertFalse(self.chamadas())

    def test_xdg_data_home_com_espaco(self):
        outro = Path(self._tmp.name) / "meus dados"
        r = self.rodar("--sem-tmux", XDG_DATA_HOME=str(outro))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((outro / "forge/vigente/.git").is_dir())
        claude = [c for c in self.chamadas() if c.startswith("claude --")][0]
        self.assertIn(f"--plugin-dir {outro}/forge/vigente ", claude)

    def test_xdg_data_home_relativo_e_recusado(self):
        r = self.rodar("--sem-tmux", XDG_DATA_HOME="dados")
        self.assertEqual(r.returncode, 2)
        self.assertIn("absoluto", r.stderr)
        self.assertFalse(self.chamadas())

    def test_sessao_e_chat_remoto_por_modo(self):
        self.rodar("--dev")
        self.rodar()
        tmux = [c for c in self.chamadas() if c.startswith("tmux new-session")]
        self.assertIn("-s jarvis-Forge-dev ", tmux[0] + " ")
        self.assertIn("-s jarvis-Forge ", tmux[1] + " ")
        self.registro.unlink()
        self.rodar("--sem-tmux", "--dev")
        self.rodar("--sem-tmux")
        claude = [c for c in self.chamadas() if c.startswith("claude --")]
        self.assertIn("--remote-control Jarvis - Forge (dev)", claude[0])
        self.assertIn("--remote-control Jarvis - Forge", claude[1])
        self.assertNotIn("(dev)", claude[1])

    def test_dev_usa_a_copia_de_trabalho_com_aviso(self):
        r = self.rodar("--sem-tmux", "--dev")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("AVISO", r.stderr)
        claude = [c for c in self.chamadas() if c.startswith("claude --")][0]
        self.assertIn("--plugin-dir . ", claude)
        self.assertFalse(self.vigente.exists())
        self.assertFalse([c for c in self.chamadas() if c.startswith("git ")])

    def test_dev_atravessa_o_tmux(self):
        r = self.rodar("--dev")
        self.assertEqual(r.returncode, 0, r.stderr)
        tmux = [c for c in self.chamadas() if c.startswith("tmux ")][0]
        self.assertIn("jarvis-Forge", tmux)
        self.assertIn("--dev", tmux)


class JarvisForgeAbrir(unittest.TestCase):
    """Ao abrir, o jarvis-forge atualiza a cópia vigente (só fast-forward) e consulta a fonte de harness (1 vez por dia).
    Repositórios bare locais e HOME temporário; nunca a rede."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "home"
        self.origem = self.tmp / "origem.git"
        semente = self.tmp / "semente"
        git("init", "--bare", "-b", "develop", str(self.origem), cwd=self.tmp)
        git("clone", "-q", str(self.origem), str(semente), cwd=self.tmp)
        (semente / "bin").mkdir()
        self.chamadas_fontes = self.tmp / "fontes.log"
        fc = semente / "bin/forge-check"
        fc.write_text(f'#!/usr/bin/env bash\necho "$*" >> "{self.chamadas_fontes}"\n'
                      'echo "fontes: F1 tem versão nova (aaaaaaa -> bbbbbbb)"\n')
        fc.chmod(0o755)
        (semente / "a.txt").write_text("1\n")
        self.semente = semente
        self.publicar("inicial")
        self.home.mkdir()
        git("clone", "-q", str(self.origem), str(self.home / "Forge"), cwd=self.tmp)
        self.vigente = self.home / ".local/share/forge/vigente"
        bin_falso = self.tmp / "bin"
        bin_falso.mkdir()
        self.log = self.tmp / "chamadas"
        for nome in ("claude", "tmux"):
            falso = bin_falso / nome
            falso.write_text(f'#!/usr/bin/env bash\necho "{nome} $*" >> "{self.log}"\n')
            falso.chmod(0o755)
        self.env = ambiente_limpo()
        self.env.update(HOME=str(self.home), PATH=f"{bin_falso}:{self.env['PATH']}",
                        XDG_STATE_HOME=str(self.tmp / "estado"), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        for k in ("XDG_DATA_HOME", "TMUX"):
            self.env.pop(k, None)

    def publicar(self, msg):
        (self.semente / "a.txt").write_text(msg + "\n")
        git("add", "-A", cwd=self.semente)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg, cwd=self.semente)
        git("push", "-q", "origin", "develop", cwd=self.semente)

    def rodar(self, *args, env=None, sem_tmux=True):
        return subprocess.run(["bash", str(RAIZ / "scripts/jarvis-forge"), *args, *(["--sem-tmux"] if sem_tmux else [])],
                              env={**self.env, **(env or {})}, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=60, cwd=self.tmp)  # nunca a raiz do repositório

    def head(self, pasta):
        return git("rev-parse", "HEAD", cwd=pasta).stdout.strip()

    def abriu(self):
        return self.log.exists() and any(c.startswith("claude --") for c in self.log.read_text().splitlines())

    def test_fast_forward_atualiza_a_copia_vigente_ao_abrir(self):
        self.assertEqual(self.rodar().returncode, 0)
        self.publicar("novo")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(self.vigente), git("rev-parse", "develop", cwd=self.origem).stdout.strip())
        self.assertIn("atualizada", r.stderr)
        self.assertTrue(self.abriu())

    def test_recusa_com_mudanca_local_e_segue_com_a_copia_atual(self):
        self.rodar()
        antes = self.head(self.vigente)
        (self.vigente / "a.txt").write_text("sujo\n")
        self.publicar("novo")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(self.vigente), antes)
        self.assertEqual((self.vigente / "a.txt").read_text(), "sujo\n")
        self.assertIn("mudanças locais", r.stderr)
        self.assertTrue(self.abriu())

    def test_recusa_com_commit_local_sem_descartar(self):
        self.rodar()
        (self.vigente / "b.txt").write_text("b\n")
        git("add", "-A", cwd=self.vigente)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "local", cwd=self.vigente)
        antes = self.head(self.vigente)
        self.publicar("novo")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(self.vigente), antes)
        self.assertIn("commits locais", r.stderr)

    def test_sem_rede_avisa_numa_linha_e_segue(self):
        self.rodar()
        antes = self.head(self.vigente)
        self.origem.rename(self.tmp / "sumiu.git")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(self.vigente), antes)
        self.assertIn("sem rede", r.stderr)
        self.assertEqual(len([l for l in r.stderr.splitlines() if "sem rede" in l]), 1)
        self.assertTrue(self.abriu())

    def test_consulta_diaria_das_fontes_uma_vez_com_cache_da_data(self):
        r = self.rodar()
        self.assertIn("versão nova", r.stderr)
        self.assertEqual(self.chamadas_fontes.read_text().split(), ["fontes"])
        self.assertEqual(len(list((self.tmp / "estado/forge").glob("fontes-????-??-??"))), 1)
        r = self.rodar()
        self.assertNotIn("versão nova", r.stderr)
        self.assertEqual(self.chamadas_fontes.read_text().split(), ["fontes"])  # não consultou de novo

    def publicar_tag_ambigua(self):
        """Tag `origin/develop` na origem apontando para um commit de fora da develop (a branch melhoria/x)."""
        git("switch", "--no-track", "-q", "-c", "melhoria/x", cwd=self.semente)
        (self.semente / "a.txt").write_text("codigo nao revisado\n")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "x", cwd=self.semente)
        git("push", "-q", "origin", "melhoria/x", cwd=self.semente)
        git("tag", "origin/develop", cwd=self.semente)
        git("push", "-q", "origin", "refs/tags/origin/develop", cwd=self.semente)
        git("switch", "-q", "develop", cwd=self.semente)
        return git("rev-parse", "melhoria/x", cwd=self.semente).stdout.strip()

    def test_tag_origin_develop_nao_e_usada_ao_abrir(self):
        self.rodar()
        self.publicar_tag_ambigua()
        self.publicar("novo")
        esperado = git("rev-parse", "refs/heads/develop", cwd=self.origem).stdout.strip()
        r = self.rodar()
        self.assertEqual(self.head(self.vigente), esperado, r.stderr)

    def test_tag_origin_develop_nao_e_usada_ao_abrir_mesmo_sem_novidade_na_develop(self):
        self.rodar()
        antes = self.head(self.vigente)
        mal = self.publicar_tag_ambigua()
        self.rodar()
        self.assertEqual(self.head(self.vigente), antes)
        self.assertNotEqual(self.head(self.vigente), mal)

    def test_tag_origin_develop_nao_e_usada_no_atualizar_vigente(self):
        self.rodar()
        mal = self.publicar_tag_ambigua()
        self.publicar("novo")
        esperado = git("rev-parse", "refs/heads/develop", cwd=self.origem).stdout.strip()
        r = self.rodar("--atualizar-vigente")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(self.vigente), esperado)
        self.assertNotEqual(self.head(self.vigente), mal)

    def test_branch_diferente_da_develop_nao_atualiza(self):
        self.rodar()
        git("switch", "--no-track", "-q", "-c", "outra", cwd=self.vigente)
        antes = self.head(self.vigente)
        self.publicar("novo")
        r = self.rodar()
        self.assertEqual(self.head(self.vigente), antes)
        self.assertIn("não está na develop", r.stderr)
        self.assertTrue(self.abriu())

    def test_sessao_tmux_aberta_nao_atualiza(self):
        self.rodar()
        antes = self.head(self.vigente)
        self.publicar("novo")
        r = self.rodar(sem_tmux=False)  # o tmux falso responde que a sessão existe
        self.assertEqual(self.head(self.vigente), antes, r.stderr)

    def test_dev_nao_atualiza(self):
        self.rodar()
        antes = self.head(self.vigente)
        self.publicar("novo")
        r = self.rodar("--dev")
        self.assertEqual(self.head(self.vigente), antes, r.stderr)

    def test_xdg_state_home_relativo_e_recusado(self):
        r = self.rodar(env={"XDG_STATE_HOME": "relativo"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("XDG_STATE_HOME", r.stderr)
        self.assertFalse(self.abriu())


class ForgeCheckFontes(unittest.TestCase):
    """`forge-check fontes`: compara o commit mais recente de cada fonte do registro local com o último revisado.
    Usa um `git` falso no PATH (nunca a rede); só URLs https:// chegam a ele, e sempre com o protocolo travado."""

    TOPO = "b" * 40
    URL = "https://exemplo.invalid/org/repo.git"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "home"
        self.chamadas = self.tmp / "git.log"
        bin_falso = self.tmp / "bin"
        bin_falso.mkdir()
        git_falso = bin_falso / "git"
        git_falso.write_text(f'#!/usr/bin/env bash\necho "$*" >> "{self.chamadas}"\n'
                             '[ -n "${FALSO_FALHA:-}" ] && exit 128\n'
                             'printf "%s\\tHEAD\\n" "$FALSO_TOPO"\n')
        git_falso.chmod(0o755)
        self.bin_falso = bin_falso

    def registrar(self, commit, url=None, codigo="F1"):
        pasta = self.home / ".forge-contrib/fontes"
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "fontes.json").write_text(json.dumps(
            {codigo: {"url": url or self.URL, "clone": "x", "versao_revisada": "1", "commit_revisado": commit}}))

    def rodar(self, topo=None, falha=False):
        env = ambiente_limpo()
        env.update(HOME=str(self.home), PATH=f"{self.bin_falso}:{env['PATH']}", FALSO_TOPO=topo or self.TOPO)
        if falha:
            env["FALSO_FALHA"] = "1"
        return subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "fontes"], env=env,
                              capture_output=True, text=True, timeout=60)

    def chamou_git(self):
        return self.chamadas.exists() and self.chamadas.read_text().strip() != ""

    def test_versao_nova(self):
        self.registrar("a" * 7)
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.splitlines()), 1)
        self.assertIn("F1", r.stdout)
        self.assertIn("versão nova", r.stdout)

    def test_chama_o_git_com_o_protocolo_travado_em_https(self):
        self.registrar("a" * 7)
        self.rodar()
        linha = self.chamadas.read_text().strip()
        negados = " ".join(f"-c protocol.{p}.allow=never" for p in ("ext", "file", "ssh", "git", "http"))
        self.assertEqual(linha, f"-c protocol.allow=never {negados} -c protocol.https.allow=always ls-remote -- {self.URL} HEAD")

    def test_git_do_cwd_malicioso_nao_executa_comando(self):
        """Um .git gravável no cwd (insteadOf para ext:: e protocol.ext.allow=always) não pode ser lido."""
        alvo = self.tmp / "executou"
        cwd = self.tmp / "cwd"
        cwd.mkdir()
        sh = lambda *a: subprocess.run(["git", *a], cwd=cwd, env=ambiente_limpo(), capture_output=True, check=True)
        sh("init", "-q")
        sh("config", f"url.ext::sh -c touch% {alvo}.insteadOf", "https://127.0.0.1:1/r.git")
        sh("config", "protocol.ext.allow", "always")
        self.registrar("a" * 7, url="https://127.0.0.1:1/r.git")
        env = ambiente_limpo()
        env["HOME"] = str(self.home)
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "fontes"], env=env, cwd=cwd,
                           capture_output=True, text=True, timeout=60)
        self.assertFalse(alvo.exists(), r.stdout + r.stderr)
        self.assertEqual(r.returncode, 3)

    def test_sem_novidade(self):
        self.registrar(self.TOPO[:7])
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("versão nova", r.stdout)
        self.assertLessEqual(len(r.stdout.splitlines()), 1)

    def test_sem_registro_fica_em_silencio(self):
        r = self.rodar()
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_fonte_inalcancavel_sai_com_3_sem_barulho(self):
        self.registrar("a" * 7)
        r = self.rodar(falha=True)
        self.assertEqual(r.returncode, 3)
        self.assertNotIn("versão nova", r.stdout)

    def test_url_que_nao_e_https_e_recusada_sem_chamar_o_git(self):
        recusadas = ["ext::sh -c touch% /tmp/x", "file:///tmp/repo", "/tmp/repo", "ssh://git@host/repo.git",
                     "git@host:org/repo.git", "http://host/repo.git", "https://host/repo;touch x",
                     "https://host/repo touch", "https://host/repo\nx", "HTTPS-://x", "ftp://host/x"]
        for url in recusadas:
            with self.subTest(url=url):
                self.registrar("a" * 7, url=url)
                r = self.rodar()
                self.assertFalse(self.chamou_git(), url)
                self.assertIn("recusad", r.stdout + r.stderr)
                self.assertNotIn("versão nova", r.stdout)

    def test_controle_na_saida_e_filtrado(self):
        self.registrar("a" * 7, codigo="F\x1b]0;pwn\x07\x1b[31m1")
        r = self.rodar()
        for c in ("\x1b", "\x07", "\r"):
            self.assertNotIn(c, r.stdout + r.stderr)

    def test_topo_que_nao_e_hexadecimal_e_tratado_como_falha(self):
        self.registrar("a" * 7)
        r = self.rodar(topo="\x1b[31mpwn")
        self.assertNotIn("\x1b", r.stdout + r.stderr)
        self.assertNotIn("versão nova", r.stdout)
        self.assertEqual(r.returncode, 3)


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

    def commitar(self, mensagem="mudanca"):
        git("add", "-A", cwd=self.tmp)
        git("commit", "-q", "-m", mensagem, cwd=self.tmp)

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

    def cartoes(self, *obs, agente="forge:tech-lead"):
        linhas = "".join(f"| C{i} | a | p | {agente} | d | d | {o} |\n" for i, o in enumerate(obs, 1))
        self.kanban("## Em andamento (WIP 1 por agente)\n{cab}" + linhas)

    def test_instancias_worktrees_distintas_passam(self):
        self.cartoes("worktree: principal", "worktree: wt-a", "worktree: wt-b")
        self.assertEqual(self.check("kanban"), (0, ""))
        self.cartoes("worktree: principal", "worktree: wt-a")
        self.assertEqual(self.check("kanban"), (0, ""))

    def test_cartoes_sem_worktree_barram(self):
        for nome, obs in {"sem campo": ("", ""), "só um com campo": ("worktree: wt-a", ""),
                          "worktree repetida": ("worktree: wt-a", "worktree: wt-a")}.items():
            with self.subTest(nome):
                self.cartoes(*obs)
                codigo, saida = self.check("kanban")
                self.assertEqual(codigo, 1)
                self.assertIn("worktree", saida)
                self.assertIn("por agente", saida)
                self.assertIn("(R-WIP)", saida)

    def test_instancias_acima_do_teto_barram(self):
        quatro = ("worktree: a", "worktree: b", "worktree: c", "worktree: d")
        self.cartoes(*quatro)
        codigo, saida = self.check("kanban")
        self.assertEqual(codigo, 1)
        self.assertIn("limite 3 instâncias", saida)
        self.assertIn("R-TETO", saida)
        self.escrever(".forge/config.json", json.dumps({"teto_maximo": 2}))  # teto_maximo menor reduz o limite
        self.cartoes("worktree: a", "worktree: b", "worktree: c")
        codigo, saida = self.check("kanban")
        self.assertEqual(codigo, 1)
        self.assertIn("limite 2 instâncias", saida)
        self.cartoes("worktree: a", "worktree: b")
        self.assertEqual(self.check("kanban"), (0, ""))

    def test_pr_aprovado_no_head(self):
        self.pareceres(self.head())
        self.commitar("pareceres")
        self.assertEqual(self.check("pr", "p1"), (0, ""))

    def test_pr_parecer_so_na_arvore_de_trabalho_falha(self):
        """PA-4: o parecer no disco e fora do commit não vale (novo, só no índice ou editado depois)."""
        self.pareceres(self.head())
        saida = self.check("pr", "p1")
        self.assertEqual(saida[0], 1)
        self.assertIn("docs/reviews/p1.md: parecer presente na árvore de trabalho e ausente no commit (HEAD)", saida[1])
        self.assertIn("docs/qa/p1.md: parecer presente na árvore de trabalho e ausente no commit (HEAD)", saida[1])
        git("add", "docs/reviews/p1.md", "docs/qa/p1.md", cwd=self.tmp)  # no índice, ainda não commitado
        self.assertIn("ausente no commit", self.check("pr", "p1")[1])
        self.commitar("pareceres")
        self.assertEqual(self.check("pr", "p1"), (0, ""))
        self.escrever("docs/qa/p1.md", (self.tmp / "docs/qa/p1.md").read_text(encoding="utf-8") + "revalidado\n")
        saida = self.check("pr", "p1")[1]  # versão nova no disco, a do commit é a antiga
        self.assertIn("docs/qa/p1.md: parecer presente na árvore de trabalho e ausente no commit", saida)
        self.assertNotIn("docs/reviews/p1.md: parecer presente", saida)

    def test_pr_parecer_editado_nao_escapa_por_skip_worktree_nem_assume_unchanged(self):
        """PA-4: a conferência compara os bytes do disco com os do HEAD; o índice não a engana."""
        self.pareceres(self.head())
        self.commitar("pareceres")
        for marca in ("--skip-worktree", "--assume-unchanged"):
            git("update-index", marca, "docs/qa/p1.md", cwd=self.tmp)
            self.escrever("docs/qa/p1.md", (self.tmp / "docs/qa/p1.md").read_text(encoding="utf-8") + "editado\n")
            saida = self.check("pr", "p1")
            self.assertEqual(saida[0], 1, marca)
            self.assertIn("docs/qa/p1.md: parecer presente na árvore de trabalho e ausente no commit", saida[1])
            git("update-index", "--no-" + marca[2:], "docs/qa/p1.md", cwd=self.tmp)
            git("checkout", "--", "docs/qa/p1.md", cwd=self.tmp)
            self.assertEqual(self.check("pr", "p1"), (0, ""), marca)

    def test_pr_com_ref_nao_olha_a_arvore_de_trabalho(self):
        git("switch", "-q", "-c", "develop", cwd=self.tmp)
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        self.pareceres(self.head())
        self.commitar("pareceres")
        git("switch", "-q", "develop", cwd=self.tmp)
        self.assertEqual(self.check("pr", "p1", "--ref", "melhoria/x"), (0, ""))

    def autoria(self, *registros):
        """Grava .forge/run/autoria.jsonl como o hook conformidade: (caminho, papel) com o hash do texto atual."""
        linhas = []
        for rel, papel in registros:
            hash_ = hashlib.sha256((self.tmp / rel).read_text(encoding="utf-8").strip().encode()).hexdigest()
            linhas.append(json.dumps({"caminho": rel, "sha256": hash_, "agente": "x", "papel": papel,
                                      "quando": "2026-10-13T10:00:00"}))
        self.escrever(".forge/run/autoria.jsonl", "\n".join(linhas) + "\n")

    def test_pr_com_autoria_do_papel_certo_vale(self):
        self.pareceres(self.head())
        self.commitar("pareceres")
        self.autoria(("docs/reviews/p1.md", "tech-lead"), ("docs/qa/p1.md", "qa"))
        self.assertEqual(self.check("pr", "p1"), (0, ""))

    def test_pr_autoria_de_papel_errado_ou_ausente_falha(self):
        self.pareceres(self.head())
        casos = {
            "qa gravado pelo tech-lead": ([("docs/reviews/p1.md", "tech-lead"), ("docs/qa/p1.md", "tech-lead")],
                                          "docs/qa/p1.md: autoria: sem registro de que o papel `qa`"),
            "review gravado pela sessão principal": ([("docs/reviews/p1.md", "jarvis"), ("docs/qa/p1.md", "qa")],
                                                     "docs/reviews/p1.md: autoria: sem registro de que o papel `tech-lead`"),
            "só o review registrado": ([("docs/reviews/p1.md", "tech-lead")], "docs/qa/p1.md: autoria"),
        }
        for nome, (registros, trecho) in casos.items():
            with self.subTest(nome):
                self.autoria(*registros)
                codigo, saida = self.check("pr", "p1")
                self.assertEqual(codigo, 1)
                self.assertIn(trecho, saida)

    def test_pr_autoria_de_versao_anterior_do_parecer_falha(self):
        self.pareceres(self.head())
        self.autoria(("docs/reviews/p1.md", "tech-lead"), ("docs/qa/p1.md", "qa"))
        self.escrever("docs/qa/p1.md", (self.tmp / "docs/qa/p1.md").read_text(encoding="utf-8") + "editado à mão\n")
        self.assertIn("docs/qa/p1.md: autoria", self.check("pr", "p1")[1])

    def test_pr_sem_arquivo_de_autoria_nao_exige(self):
        self.pareceres(self.head())
        self.commitar("pareceres")
        self.assertFalse((self.tmp / ".forge/run/autoria.jsonl").exists())
        self.assertEqual(self.check("pr", "p1"), (0, ""))

    def test_pr_autoria_com_ref_compara_o_texto_da_branch(self):
        git("switch", "-q", "-c", "develop", cwd=self.tmp)
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        self.escrever("src/app.txt", "v2\n")
        self.commitar()
        self.pareceres(self.head())
        self.commitar()
        self.autoria(("docs/reviews/p1.md", "tech-lead"), ("docs/qa/p1.md", "qa"))
        git("switch", "-q", "develop", cwd=self.tmp)
        self.assertEqual(self.check("pr", "p1", "--ref", "melhoria/x"), (0, ""))

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

    SEGURANCA = ("tipo: revisao-seguranca\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\n"
                 "parecer: {p}\nrevisor: forge:security-engineer\ndata: 2026-10-14\n{extra}")

    def test_docs_de_devops_e_seguranca(self):
        self.escrever("docs/security/postura.md", "# Postura, sem frontmatter: documento livre\n")
        self.escrever("docs/security/p1.md", "---\n" + self.SEGURANCA.format(c="abc1234", p="riscos-aceitos", extra="") + "---\n")
        self.escrever("docs/devops/p1.md", "---\ntipo: revisao-devops\ncontrato: 1\npedido: p1\nbranch: b\ncommit: abc1234\n"
                      "parecer: talvez\nrevisor: forge:devops-engineer\ndata: 2026-10-14\n---\n")
        codigo, saida = self.check("docs")
        self.assertEqual(codigo, 1)
        self.assertNotIn("docs/security/p1.md", saida)  # o aceite é conferido no `pr`, pelo arquivo em docs/security/aceites/
        self.assertIn("docs/devops/p1.md: parecer: use aprovado ou reprovado (R-REVIEW)", saida)
        self.assertNotIn("postura.md", saida)

    def entrega(self, arquivo, texto="x\n"):
        git("branch", "-f", "develop", cwd=self.tmp)
        self.escrever(arquivo, texto)
        self.commitar()

    def test_pr_com_pipeline_exige_devops_e_seguranca(self):
        self.entrega(".github/workflows/ci.yml")
        self.pareceres(self.head())
        saida = self.check("pr", "p1")[1]
        self.assertIn("docs/devops: revisao-devops: sem parecer", saida)
        self.assertIn("docs/security: revisao-seguranca: sem parecer", saida)
        self.assertIn("(R-SEGURANCA)", saida)

    def test_pr_com_pareceres_de_devops_e_seguranca_vale(self):
        self.entrega("Dockerfile", "FROM scratch\n")
        head = self.head()
        self.pareceres(head)
        self.escrever("docs/devops/p1.md", "---\ntipo: revisao-devops\ncontrato: 1\npedido: p1\nbranch: melhoria/x\n"
                      f"commit: {head}\nparecer: aprovado\nrevisor: forge:devops-engineer\ndata: 2026-10-14\n---\n")
        self.escrever("docs/security/p1.md", "---\n" + self.SEGURANCA.format(c=head, p="aprovado", extra="") + "---\n")
        self.commitar("pareceres")
        self.assertEqual(self.check("pr", "p1"), (0, ""))
        self.autoria(("docs/reviews/p1.md", "tech-lead"), ("docs/qa/p1.md", "qa"), ("docs/devops/p1.md", "tech-lead"),
                     ("docs/security/p1.md", "seguranca"))
        self.assertIn("docs/devops/p1.md: autoria", self.check("pr", "p1")[1])

    def test_pr_sem_gatilho_nao_exige_devops_nem_seguranca(self):
        self.entrega("src/outro.txt")
        self.pareceres(self.head())
        self.commitar("pareceres")
        self.assertEqual(self.check("pr", "p1"), (0, ""))

    def test_pr_gatilhos_de_seguranca_pelo_diff(self):
        for arquivo in ("package-lock.json", "app/.env", "db/migrations/001.sql", "hooks/conformidade.json", "docs/regras/R-X.md"):
            with self.subTest(arquivo=arquivo):
                git("branch", "-q", "-f", "develop", "HEAD", cwd=self.tmp)
                self.escrever(arquivo, "x\n")
                self.commitar()
                self.pareceres(self.head())
                saida = self.check("pr", "p1")[1]
                self.assertIn("docs/security: revisao-seguranca: sem parecer", saida)
                self.assertNotIn("revisao-devops", saida)

    def exige(self, arquivo, devops=True, seguranca=True):
        """Entrega que só muda `arquivo` exige (ou não) os pareceres de devops e de segurança."""
        git("branch", "-q", "-f", "develop", "HEAD", cwd=self.tmp)
        self.escrever(arquivo, "x\n")
        self.commitar()
        self.pareceres(self.head())
        saida = self.check("pr", "p1")[1]
        self.assertEqual("revisao-devops" in saida, devops, saida)
        self.assertEqual("revisao-seguranca" in saida, seguranca, saida)

    def test_pr_terraform_exige_devops_e_seguranca(self):
        for arquivo in ("infra/main.tf", "main.tf", "env/prod.tfvars", "x.tf.json"):
            with self.subTest(arquivo=arquivo):
                self.exige(arquivo)

    def test_pr_pastas_de_infraestrutura_exigem_devops_e_seguranca(self):
        for arquivo in ("infra/a.txt", "deploy/a.txt", "terraform/a.txt", "k8s/a.txt", "helm/a.txt", "x/deploy/a.txt"):
            with self.subTest(arquivo=arquivo):
                self.exige(arquivo)

    def test_pr_manifestos_de_dependencia_exigem_seguranca(self):
        for arquivo in ("requirements.txt", "requirements-dev.txt", "pyproject.toml", "package.json", "Gemfile",
                        "go.mod", "Cargo.toml", "app/package.json"):
            with self.subTest(arquivo=arquivo):
                self.exige(arquivo, devops=False)

    def test_pr_renomear_o_arquivo_de_travas_ainda_dispara(self):
        self.escrever("pnpm-lock.yaml", "a: 1\n")
        self.commitar()
        git("branch", "-q", "-f", "develop", "HEAD", cwd=self.tmp)
        git("mv", "pnpm-lock.yaml", "vendor-deps.yaml", cwd=self.tmp)
        self.escrever("vendor-deps.yaml", "a: 1\nb: 2\n")
        self.commitar()
        self.pareceres(self.head())
        self.assertIn("docs/security: revisao-seguranca: sem parecer", self.check("pr", "p1")[1])

    def test_pr_renomear_dockerfile_ainda_exige_devops(self):
        self.escrever("Dockerfile", "FROM scratch\n")
        self.commitar()
        git("branch", "-q", "-f", "develop", "HEAD", cwd=self.tmp)
        git("mv", "Dockerfile", "base.img", cwd=self.tmp)
        self.commitar()
        self.pareceres(self.head())
        self.assertIn("revisao-devops: sem parecer", self.check("pr", "p1")[1])

    def dependabot(self, mensagem, arquivo="package-lock.json"):
        git("branch", "-q", "-f", "develop", "HEAD", cwd=self.tmp)
        git("switch", "-q", "-c", "dependabot/npm/foo", cwd=self.tmp)
        self.escrever(arquivo, "x\n")
        self.commitar(mensagem)
        self.pareceres(self.head())
        return self.check("pr", "p1")[1]

    def test_branch_dependabot_com_mensagem_bump_ainda_exige_seguranca(self):
        self.assertIn("revisao-seguranca: sem parecer", self.dependabot("Bump foo from 1.2.3 to 1.2.4"))

    def aceite(self, texto=None, commit=None):
        self.entrega("package-lock.json", f"{git('rev-list', '--count', 'HEAD', cwd=self.tmp).stdout.strip()}\n")  # conteúdo novo a cada chamada (subTests)
        head = self.head()
        self.pareceres(head)
        self.escrever("docs/devops/p1.md", "---\ntipo: revisao-devops\ncontrato: 1\npedido: p1\nbranch: melhoria/x\n"
                      f"commit: {head}\nparecer: aprovado\nrevisor: forge:devops-engineer\ndata: 2026-10-14\n---\n")
        self.escrever("docs/security/p1.md", "---\n" + self.SEGURANCA.format(c=head, p="riscos-aceitos", extra="") + "---\n")
        if texto is not None:
            self.escrever("docs/security/aceites/p1.md", texto.replace("{HEAD}", commit or head))
        self.commitar("pareceres")
        return self.check("pr", "p1")

    def test_riscos_aceitos_sem_o_arquivo_de_aceite_reprova(self):
        codigo, saida = self.aceite()
        self.assertEqual(codigo, 1)
        self.assertIn("docs/security/aceites/p1.md", saida)
        self.assertIn("(R-SEGURANCA)", saida)

    def test_riscos_aceitos_com_aceite_no_frontmatter_do_parecer_nao_basta(self):
        self.entrega("package-lock.json")
        head = self.head()
        self.pareceres(head)
        self.escrever("docs/security/p1.md", "---\n" + self.SEGURANCA.format(
            c=head, p="riscos-aceitos", extra="aceite_usuario: sim\n") + "---\n")
        self.assertIn("docs/security/aceites/p1.md", self.check("pr", "p1")[1])

    def test_riscos_aceitos_com_o_arquivo_de_aceite_vale(self):
        self.assertEqual(self.aceite("---\npedido: p1\ncommit: {HEAD}\naceite: sim\n---\nAceito o risco X.\n"), (0, ""))

    def test_aceite_de_commit_antigo_reprova(self):
        codigo, saida = self.aceite("---\npedido: p1\ncommit: {HEAD}\naceite: sim\n---\n", commit="0" * 40)
        self.assertEqual(codigo, 1)
        self.assertIn("commit", saida)
        self.assertIn("(R-SEGURANCA)", saida)

    def test_aceite_sem_commit_reprova(self):
        self.assertEqual(self.aceite("---\npedido: p1\naceite: sim\n---\n")[0], 1)

    def test_aceite_de_outro_pedido_ou_nao_nao_vale(self):
        for texto in ("---\npedido: p2\ncommit: {HEAD}\naceite: sim\n---\n", "---\npedido: p1\ncommit: {HEAD}\naceite: nao\n---\n", "aceito\n"):
            with self.subTest(texto=texto):
                self.assertEqual(self.aceite(texto)[0], 1)

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

    def esperado(self, nome, *trechos):
        cod, saida = self.caso(nome)
        self.assertEqual(cod, 1, saida)
        for t in trechos:
            self.assertIn(t, saida)
        return saida

    def test_papel(self):
        self.assertEqual(self.caso("papel-ok.jsonl"), (0, ""))
        saida = self.esperado(
            "papel-viola.jsonl",
            "R-CONFORMIDADE.papel: `gh pr create` pelo papel `qa` (forge:qa-engineer); permitido: jarvis, tech-lead (evento 3)",
            "escrita em `docs/reviews/` pelo papel `qa`", "escrita em `.claude/` pelo papel `jarvis` (sessão principal); permitido: só o usuário",
            "`git merge <branch>` pelo papel `dev` (<agente>)", "`pacote instalar` pelo papel `qa`")
        self.assertEqual(saida.count("R-CONFORMIDADE.papel"), 5)

    def test_contorno(self):
        self.assertEqual(self.caso("contorno-ok.jsonl"), (0, ""))
        cod, saida = self.caso("contorno-encaminhado.jsonl")  # o papel certo refaz a ação: só a 1ª tentativa é achado
        self.assertEqual((cod, saida.count("\n"), "R-CONFORMIDADE.papel" in saida, "contorno" in saida), (1, 1, True, False))
        self.esperado(
            "contorno-viola.jsonl",
            "R-CONFORMIDADE.contorno: `flag --no-verify` barrado (evento 4) e tentado de novo por script (evento 6)",
            "`escrita docs/regras/` barrado (evento 8) e tentado de novo por outra ferramenta (Bash) (evento 9)",
            "`escrita docs/regras/` barrado (evento 8) e tentado de novo por outro agente (<agente>) (evento 10)")

    def test_sandbox(self):
        self.assertEqual(self.caso("sandbox-ok.jsonl"), (0, ""))
        self.esperado("sandbox-viola.jsonl", "R-CONFORMIDADE.sandbox: dangerouslyDisableSandbox usado por forge:node-backend (evento 3)")

    def test_verify_em_script_gravado(self):
        self.assertEqual(self.caso("verify-script-ok.jsonl"), (0, ""))
        self.esperado("verify-script-viola.jsonl",
                      "R-VERIFY: script gravado na sessão com --no-verify, --force (evento 3) e executado (evento 4)")

    def test_custo(self):
        self.assertEqual(self.caso("custo-ok.jsonl"), (0, ""))
        saida = self.esperado("custo-viola.jsonl", "comando pago `claude -p`", "comando pago `plugin eval`", "api.openai.com")
        self.assertEqual(saida.count("R-CUSTO"), 3)

    def test_copia(self):
        self.assertEqual(self.caso("copia-ok.jsonl"), (0, ""))
        self.esperado("copia-viola.jsonl", "R-COPIA: escrita em .claude/agents|skills por forge:software-architect (evento 3)")

    def test_decisao_so_avisa(self):
        self.assertEqual(self.caso("decisao-ok.jsonl"), (0, ""))
        for nome, trecho in (("decisao-viola.jsonl", "3 perguntas"), ("decisao-opcoes.jsonl", "opções sem recomendação")):
            cod, saida = self.caso(nome)
            self.assertEqual(cod, 0)
            self.assertEqual(saida.strip(), f"transcricao: aviso: R-DECISAO: a mensagem final {'traz ' if 'perguntas' in trecho else 'lista '}{trecho}"
                             f"{'; uma decisão por vez' if 'perguntas' in trecho else ' do time'}")

    def test_anonimizador_mantem_so_o_que_as_propriedades_usam(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        cwd = "/" + "home" + "/ana/Zephyrus"  # montado para não parecer caminho pessoal real

        def uso(i, nome, entrada, lado=False, extra=None):
            return {"type": "assistant", "timestamp": "2026-01-01T10:00:00Z", "cwd": cwd, "isSidechain": lado,
                    **(extra or {}), "message": {"content": [{"type": "tool_use", "id": i, "name": nome, "input": entrada}]}}

        def resultado(i, texto, erro=True, lado=False):
            return {"type": "user", "timestamp": "2026-01-01T10:00:01Z", "isSidechain": lado,
                    "message": {"content": [{"type": "tool_result", "tool_use_id": i, "is_error": erro, "content": texto}]}}

        brutos = [
            uso("d1", "Agent", {"subagent_type": "forge:qa-engineer", "prompt": "Zephyrus"}),
            {"type": "user", "toolUseResult": {"agentId": "ag1"}, "message": {"content": [
                {"type": "tool_result", "tool_use_id": "d1", "content": "pronto Zephyrus"}]}},
            uso("b1", "Bash", {"command": "git push --no-verify origin x", "dangerouslyDisableSandbox": True}),
            resultado("b1", "PreToolUse:Bash hook blocking error: Zephyrus segredo"),
            uso("w1", "Write", {"file_path": cwd + "/docs/reviews/x.md", "content": "texto Zephyrus"}),
            uso("w2", "Write", {"file_path": cwd + "/.claude/agents/zeph.md", "content": "Zephyrus"}),
            uso("w3", "Write", {"file_path": cwd + "/ferramentas/zeph.sh", "content": "git push --force origin x"}),
            uso("b2", "Bash", {"command": "cat > /tmp/zeph2.sh <<'EOF'\ngit commit --no-verify\nEOF\nbash /tmp/zeph2.sh && bash ferramentas/zeph.sh"}),
            uso("b3", "Bash", {"command": "claude -p 'Zephyrus' && curl https://api.openai.com/v1/x && npm install zeph-pkg && npm ci"},
                lado=True, extra={"agentId": "ag1"}),
            resultado("b3", "Permission to use Bash has been denied. Zephyrus", lado=True),
            {"type": "assistant", "timestamp": "2026-01-01T10:09:00Z", "message": {"content": [
                {"type": "text", "text": "Qual caminho, Zephyrus?\n- Opção A\n- Opção B\nE o prazo?"}]}},
        ]
        entrada, saida = tmp / "e.jsonl", tmp / "s.jsonl"
        entrada.write_text("\n".join(json.dumps(b) for b in brutos), encoding="utf-8")
        self.assertEqual(self.rodar("anonimizar", str(entrada), str(saida))[0], 0)
        texto = saida.read_text(encoding="utf-8")
        for proibido in ("ana", "Zephyrus", "zeph", "segredo", "/home", "/tmp"):
            self.assertNotIn(proibido, texto)
        eventos = [json.loads(l) for l in texto.splitlines()][1:]
        resumo = [(e["ev"], e.get("cmd") or e.get("alvo") or e.get("causa") or "", e.get("ator", "")) for e in eventos]
        self.assertIn(("sandbox", "", ""), resumo)
        self.assertIn(("cmd", "flag --no-verify", ""), resumo)
        self.assertIn(("bloqueio", "hook", ""), resumo)
        self.assertIn(("escrita", "docs/reviews/", ""), resumo)
        self.assertIn(("cmd", "executa f2", ""), resumo)
        self.assertIn(("cmd", "custo claude -p", "forge:qa-engineer"), resumo)
        self.assertIn(("cmd", "custo api api.openai.com", "forge:qa-engineer"), resumo)
        self.assertIn(("cmd", "pacote instalar", "forge:qa-engineer"), resumo)
        self.assertIn(("cmd", "pacote congelado", "forge:qa-engineer"), resumo)
        self.assertIn(("bloqueio", "permissao", "forge:qa-engineer"), resumo)
        self.assertEqual(resumo[-1][0], "resposta")
        self.assertEqual({k: eventos[-1][k] for k in ("perguntas", "opcoes", "recomenda")},
                         {"perguntas": 2, "opcoes": 2, "recomenda": False})
        self.assertEqual(sum(1 for e in eventos if e["ev"] == "escrita" and e["copia"]), 1)
        self.assertEqual(sorted(e["arq"] for e in eventos if e["ev"] == "escrita" and e["arq"]), ["f1", "f2"])
        self.assertEqual(sum(1 for e in eventos if e["ev"] == "cmd" and e["cmd"].startswith("executa ")), 2)
        cod, saida_v = self.rodar("verificar", str(saida))
        self.assertEqual(cod, 1)
        for regra in ("R-VERIFY", "R-CUSTO", "R-COPIA", "R-CONFORMIDADE.sandbox", "R-CONFORMIDADE.contorno", "R-DECISAO"):
            self.assertIn(regra, saida_v)

    def anonimizado(self, *comandos):
        """Anonimiza uma sessão sintética com um Bash por comando e devolve os eventos gerados (sem o cabeçalho)."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        brutos = [{"type": "assistant", "timestamp": "2026-01-01T10:00:00Z", "cwd": "/x/p", "message": {"content": [
            {"type": "tool_use", "id": f"b{n}", "name": "Bash", "input": {"command": c}}]}} for n, c in enumerate(comandos)]
        entrada, saida = tmp / "e.jsonl", tmp / "s.jsonl"
        entrada.write_text("\n".join(json.dumps(b) for b in brutos), encoding="utf-8")
        self.assertEqual(self.rodar("anonimizar", str(entrada), str(saida))[0], 0)
        return [json.loads(l) for l in saida.read_text(encoding="utf-8").splitlines()][1:]

    def tokens(self, *comandos):
        return [e.get("cmd") or e.get("alvo") for e in self.anonimizado(*comandos)]

    def test_ativar_o_hook_da_fabrica_nao_e_r_verify(self):
        self.assertEqual(self.tokens("git config core.hooksPath .githooks", "git -C /x/p config core.hooksPath .githooks"), [])
        for c in ("git config core.hooksPath /dev/null", "git config --global core.hooksPath .githooks",
                  "git -c core.hooksPath=/dev/null config core.hooksPath .githooks"):
            self.assertIn("flag core.hooksPath", self.tokens(c), c)

    def test_forca_direta_e_refspec_com_mais(self):
        self.assertEqual(self.tokens("git push -f origin x", "git push origin +x", "git push --force-with-lease origin x"),
                         ["git push --force <branch>"] * 3)

    def test_pip_com_arquivo_e_instalacao_congelada(self):
        self.assertEqual(self.tokens("pip install -r requirements.txt", "pip install --requirement r.txt",
                                     "pip install -r r.txt pacote", "pip install pacote"),
                         ["pacote congelado", "pacote congelado", "pacote instalar", "pacote instalar"])

    def test_heredoc_so_com_delimitador_valido_e_fechado(self):
        # deslocamento de bits, <<< e heredoc sem fechamento não escondem o comando seguinte
        for c in ("python3 -c 'print(1 << 2)' && git push --force origin x", "python3 -c 'print(1 << 2)'\ngit push -f origin x",
                  "cat <<< oi && git push -f origin x", "cat <<EOF\ngit push -f origin x"):
            self.assertIn("git push --force <branch>", self.tokens(c), c)
        self.assertEqual(self.tokens("cat <<-'FIM'\n\tgit push -f origin x\n\tFIM\ngit status"), [])  # corpo do heredoc não é comando

    def test_so_forge_nao_vale_no_verificador(self):
        eventos = [{"ev": "escrita", "t": "", "alvo": "tests/hooks/", "copia": False, "arq": "", "flags": [], "via": "Write", "ator": "<agente>"},
                   {"ev": "escrita", "t": "", "alvo": "docs/reviews/", "copia": False, "arq": "", "flags": [], "via": "Write", "ator": "<agente>"}]
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        arq = tmp / "t.jsonl"
        arq.write_text("\n".join(json.dumps(l) for l in [{"formato": "forge-transcricao/1", "origem": "x"}, *eventos]) + "\n", encoding="utf-8")
        cod, saida = self.rodar("verificar", str(arq))
        self.assertEqual(cod, 1)
        self.assertNotIn("tests/hooks/", saida)
        self.assertIn("docs/reviews/", saida)

    def test_exit_2_generico_nao_e_bloqueio(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-transc-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)

        def sessao(texto):
            brutos = [{"type": "assistant", "timestamp": "2026-01-01T10:00:00Z", "message": {"content": [
                {"type": "tool_use", "id": "b1", "name": "Bash", "input": {"command": "git push --no-verify origin x"}}]}},
                {"type": "user", "timestamp": "2026-01-01T10:00:01Z", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "b1", "is_error": True, "content": texto}]}}]
            e, s = tmp / "e.jsonl", tmp / "s.jsonl"
            e.write_text("\n".join(json.dumps(b) for b in brutos), encoding="utf-8")
            self.assertEqual(self.rodar("anonimizar", str(e), str(s))[0], 0)
            return [x["ev"] for x in map(json.loads, s.read_text(encoding="utf-8").splitlines()[1:])]

        self.assertNotIn("bloqueio", sessao("Error: Exit code 2\ngrep: x: No such file"))
        self.assertIn("bloqueio", sessao("Error: Exit code 2\nR-VERIFY: git push --no-verify"))

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
            "transcricao: formato: evento 2 inválido: `ev` deve ser um de agente, fim, cmd, escrita, bloqueio, sandbox, resposta",
            "transcricao: formato: evento 3 inválido: `t` deve ser data e hora ISO 8601 ou vazio",
            "transcricao: formato: evento 4 inválido: `cmd` ausente ou de tipo errado"])
        arq.write_text("não é json\n", encoding="utf-8")
        self.assertEqual(self.rodar("verificar", str(arq))[0], 1)


class CustoDeTokens(unittest.TestCase):
    """`forge-check transcricao custo`: tokens lidos das transcrições locais, sem rede e anonimizados (fonte F1, lote 4)."""
    USO = RAIZ / "tests/transcricoes/uso"

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "transcricao", "custo", *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr

    def test_tokens_por_sessao_com_subagentes_e_duplicata_de_streaming(self):
        cod, saida, _ = self.rodar(str(self.USO))
        self.assertEqual(cod, 0, saida)
        self.assertIn("custo: sessao s1: entrada=373 saida=205 cache_criacao=1003 cache_leitura=2954 total=4535", saida)
        self.assertIn("custo: sessao s2: entrada=30 saida=10 cache_criacao=0 cache_leitura=0 total=40", saida)

    def test_principal_a_parte(self):
        saida = self.rodar(str(self.USO))[1]
        self.assertIn("custo: principal: entrada=380 saida=185 cache_criacao=1000 cache_leitura=2300 total=3865", saida)

    def test_subagente_por_tipo_e_modelo(self):
        saida = self.rodar(str(self.USO))[1]
        self.assertIn("custo: subagente forge:tech-lead claude-sonnet-4: mensagens=3 entrada=22 saida=28 "
                      "cache_criacao=0 cache_leitura=650 total=700", saida)
        self.assertIn("custo: subagente forge:qa-engineer claude-haiku-4: mensagens=1 entrada=1 saida=2 "
                      "cache_criacao=3 cache_leitura=4 total=10", saida)

    def test_compactacoes(self):
        self.assertIn("custo: compactacoes: quantidade=1 tokens_antes=9000", self.rodar(str(self.USO))[1])

    def test_relancamento_do_mesmo_prompt_e_retrabalho(self):
        saida = self.rodar(str(self.USO))[1]
        self.assertIn("custo: retrabalho: relancamentos=1", saida)
        self.assertRegex(saida, r"custo: retrabalho: hash=[0-9a-f]{8} tipo=forge:tech-lead lancamentos=2")

    def test_aceita_arquivo_unico_e_ignora_linha_corrompida(self):
        cod, saida, _ = self.rodar(str(self.USO / "sessao-b.jsonl"))
        self.assertEqual(cod, 0)
        self.assertIn("custo: sessao s1: entrada=30 saida=10 cache_criacao=0 cache_leitura=0 total=40", saida)
        self.assertIn("custo: retrabalho: relancamentos=0", saida)

    def test_saida_anonimizada(self):
        cod, saida, erro = self.rodar(str(self.USO))
        for proibido in ("SEGREDO", "pessoa", "projeto-secreto", "/home", "sessao-a", "sessao-b"):
            self.assertNotIn(proibido, saida)
        self.assertNotIn("SEGREDO", erro)

    def test_anuncia_o_que_vai_ler_antes_de_ler(self):
        erro = self.rodar(str(self.USO))[2]
        self.assertIn("custo: vai ler 2 arquivo(s) .jsonl em ", erro)
        self.assertIn(str(self.USO), erro)

    def test_entregas_gera_linhas_do_quadro(self):
        saida = self.rodar(str(self.USO), "--entregas", "--entrega", "exemplo")[1]
        linhas = [l for l in saida.splitlines() if l.startswith("| ")]
        self.assertTrue(all(l.count("|") == 8 for l in linhas), linhas)  # 7 colunas de docs/kanban/entregas.md
        self.assertTrue(any("| exemplo | jarvis (principal) | 3865 |" in l for l in linhas), linhas)
        self.assertTrue(any("| exemplo | forge:tech-lead | 700 |" in l for l in linhas), linhas)
        self.assertTrue(any("2026-01-02" in l for l in linhas) or any("2026-01-01" in l for l in linhas))

    def test_caminho_inexistente_falha_sem_traceback(self):
        cod, saida, erro = self.rodar(str(self.USO / "nao-existe"))
        self.assertEqual(cod, 1)
        self.assertNotIn("Traceback", erro)

    def test_pasta_sem_transcricoes_diz_que_nao_ha_o_que_ler(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-custo-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        cod, saida, erro = self.rodar(str(tmp))
        self.assertEqual(cod, 1)
        self.assertIn("nenhum arquivo .jsonl", saida + erro)

    def pasta_com(self, nome, conteudo):
        tmp = Path(tempfile.mkdtemp(prefix="forge-custo-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / nome).write_text(conteudo, encoding="utf-8")
        return tmp

    def test_arquivo_ilegivel_avisa_e_e_pulado_sem_traceback(self):
        # Simula o PermissionError no `open` (sem chmod), para o teste valer também como root e em qualquer usuário.
        tmp = Path(tempfile.mkdtemp(prefix="forge-custo-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        ruim = tmp / "ruim.jsonl"
        bom = tmp / "bom.jsonl"
        ruim.write_text("{}\n", encoding="utf-8")
        bom.write_text(
            '{"type":"assistant","message":{"id":"m1","model":"m","usage":{"input_tokens":1,"output_tokens":2}}}\n', encoding="utf-8")
        abrir_de_verdade = open

        def abrir_com_permissao_negada(arquivo, *args, **kwargs):
            if Path(arquivo) == ruim:
                raise PermissionError(13, "Permission denied")
            return abrir_de_verdade(arquivo, *args, **kwargs)

        fc = carregar_forge_check()
        erro = io.StringIO()
        with mock.patch.object(fc, "open", abrir_com_permissao_negada, create=True), contextlib.redirect_stderr(erro):
            dados = fc.ler_uso([ruim, bom])
        self.assertEqual(dados["ilegiveis"], 1)
        self.assertIn("aviso", erro.getvalue())
        self.assertNotIn("Traceback", erro.getvalue())
        self.assertNotIn("ruim.jsonl", erro.getvalue())
        self.assertEqual(len(dados["mensagens"]), 1)
        self.assertEqual(dados["mensagens"][0][4]["output_tokens"], 2)
        self.assertEqual(dados["mensagens"][0][4]["input_tokens"], 1)

    def test_linha_malformada_e_contada_em_stderr(self):
        erro = self.rodar(str(self.USO / "sessao-b.jsonl"))[2]
        self.assertRegex(erro, r"custo: aviso: [1-9]\d* linhas? ignoradas?")

    def test_arquivo_sem_usage_sai_com_codigo_diferente_de_zero(self):
        tmp = self.pasta_com("lixo.jsonl", 'nao e json\n{"type":"user"}\n')
        cod, saida, erro = self.rodar(str(tmp))
        self.assertNotEqual(cod, 0)
        self.assertIn("nenhuma mensagem com usage", saida + erro)
        self.assertNotIn("total=0", saida)


class MedirAlucinacao(unittest.TestCase):
    """`forge-check transcricao lastro` e `decisoes`: linha de base de M1 e M3, sobre transcrições sintéticas."""

    def rodar(self, acao, linhas):
        tmp = Path(tempfile.mkdtemp(prefix="forge-medida-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "s.jsonl").write_text("".join(json.dumps(o) + "\n" for o in linhas), encoding="utf-8")
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "transcricao", acao, str(tmp)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout, r.stderr

    @staticmethod
    def subagente(relatorio, saida, erro=False):
        base = {"isSidechain": True, "agentId": "a1", "sessionId": "sess"}
        return [
            {**base, "type": "user", "message": {"role": "user", "content": "faca"}},
            {**base, "type": "assistant", "message": {"id": "m1", "role": "assistant", "content": [
                {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "x"}}]}},
            {**base, "type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t1", "is_error": erro, "content": [{"type": "text", "text": saida}]}]}},
            {**base, "type": "assistant", "message": {"id": "m2", "role": "assistant", "content": [
                {"type": "tool_use", "id": "t2", "name": "SubagentHandback", "input": {"message": relatorio}}]}},
        ]

    @staticmethod
    def jarvis(*respostas):
        linhas = []
        for i, texto in enumerate(respostas):
            linhas.append({"type": "user", "sessionId": "sess", "message": {"role": "user", "content": f"pedido {i}"}})
            linhas.append({"type": "assistant", "sessionId": "sess", "message": {
                "id": f"j{i}", "role": "assistant", "content": [{"type": "text", "text": texto}]}})
        return linhas

    def lastro(self, relatorio, saida, erro=False):
        return self.rodar("lastro", self.subagente(relatorio, saida, erro))[0]

    def test_afirmacoes_com_lastro_nas_saidas(self):
        saida = ("3f2a9c1..8b04e7d  melhoria/x -> melhoria/x\nhttps://github.com/o/r/pull/118\n✓ Merged pull request #118 (x)\n"
                 "Ran 312 tests in 4s\nOK\nabc1234 commit")
        relatorio = "Commit abc1234, PR #118, push aceito, mesclado, 312 testes OK."
        self.assertIn("lastro: sessao s1: relatorios=1 afirmacoes=5 sem_lastro=0 taxa=0.0%", self.lastro(relatorio, saida))

    def test_afirmacoes_sem_lastro(self):
        saida = "! [rejected] melhoria/x -> melhoria/x (pre-receive hook declined)\nRan 10 tests\nFAILED"
        relatorio = "Commit abc1234, PR #118, push aceito, mesclado, 312 testes OK."
        self.assertIn("lastro: sessao s1: relatorios=1 afirmacoes=5 sem_lastro=5 taxa=100.0%", self.lastro(relatorio, saida))

    def test_saida_com_erro_nao_da_lastro_e_nada_vaza(self):
        saida = self.lastro("Commit abc1234 entrou.", "abc1234", erro=True)
        self.assertIn("afirmacoes=1 sem_lastro=1 taxa=100.0%", saida)
        self.assertNotIn("abc1234", saida)
        self.assertNotIn("a1", saida.replace("afirmacoes", ""))

    def test_total_zero_vira_na_e_nao_zero_por_cento(self):
        # M07 do estudo de mutação: `taxa` com total zero devolve "n/a", nunca "0.0%" nem divisão por zero.
        # M14 (hooks/vigia.py, `<` por `<=` em `podar`) é equivalente: a igualdade exata de dois instantes
        # em ponto flutuante não ocorre num teste real. M15 (`>=` por `>` em `arquivos_em_vigor`) é limite de
        # proteção: matá-lo pede 3000 arquivos num teste, custo alto para ganho pequeno; fica sem teste.
        saida = self.lastro("Nada a afirmar aqui.", "qualquer saida")
        self.assertIn("afirmacoes=0 sem_lastro=0 taxa=n/a", saida)
        self.assertNotIn("0.0%", saida)

    def test_decisao_unica_com_recomendo_e_ok(self):
        saida, _ = self.rodar("decisoes", self.jarvis("Qual caminho?\n- **A)** copiar\n- **B)** mover\nRecomendo A, e so isso."))
        self.assertIn("decisoes: sessao s1: respostas=1 com_grupo=1 violacoes=0 taxa=0.0%", saida)

    def test_decisao_dupla_e_violacao(self):
        texto = "1.\nA) x\nB) y\nRecomendo A.\n\n2.\nA) z\nB) w\nRecomendo B."
        saida, _ = self.rodar("decisoes", self.jarvis("so texto", texto))
        self.assertIn("decisoes: sessao s1: respostas=2 com_grupo=1 violacoes=1 taxa=50.0%", saida)

    def test_decisao_sem_recomendo_e_violacao(self):
        saida, _ = self.rodar("decisoes", self.jarvis("Escolha:\nA: x\nB: y"))
        self.assertIn("respostas=1 com_grupo=1 violacoes=1 taxa=100.0%", saida)

    def test_codigo_citacao_e_lista_numerada_nao_contam(self):
        texto = "```\nA) x\nB) y\n```\n> A) q\n> B) r\n1) um\n2) dois\nA casa, B casa"
        saida, _ = self.rodar("decisoes", self.jarvis(texto))
        self.assertIn("respostas=1 com_grupo=0 violacoes=0", saida)

    def test_mesclado_exige_prova_de_merge_do_pr_citado(self):
        aberto = '{"mergedAt": null, "number": 120, "state": "OPEN"}\nMerge pull request #117 from o/x'
        self.assertIn("afirmacoes=2 sem_lastro=1", self.lastro("PR #120 mesclado.", aberto))
        outro = '{"mergedAt": "2026-10-14T10:00:00Z", "number": 117, "state": "MERGED"}'
        self.assertIn("afirmacoes=2 sem_lastro=1", self.lastro("PR #120 mesclado.", aberto + "\n" + outro))
        pronto = '{"mergedAt": "2026-10-14T10:00:00Z", "number": 120, "state": "MERGED"}'
        self.assertIn("afirmacoes=2 sem_lastro=0", self.lastro("PR #120 mesclado.", pronto))
        self.assertIn("afirmacoes=2 sem_lastro=0", self.lastro("PR #120 mesclado.", "\u2713 Merged pull request #120 (x)"))

    def test_testes_ok_exige_ok_e_nao_failed(self):
        falha = "Ran 312 tests in 4s\n\nFAILED (failures=2)"
        self.assertIn("afirmacoes=1 sem_lastro=1", self.lastro("312 testes OK.", falha))
        self.assertIn("afirmacoes=1 sem_lastro=0", self.lastro("312 testes OK.", "Ran 312 tests in 4s\n\nOK"))
        self.assertIn("afirmacoes=1 sem_lastro=1", self.lastro("312 testes OK.", "312 passed, 2 failed"))
        self.assertIn("afirmacoes=1 sem_lastro=0", self.lastro("312 testes OK.", "312 passed in 2s"))

    def test_negacao_fetch_e_forma_curta_de_testes(self):
        self.assertIn("afirmacoes=0", self.lastro("Não mesclei. O push não passou.", "x"))
        self.assertIn("afirmacoes=1 sem_lastro=1", self.lastro("Push feito.", "a1b2c3d..e4f5a6b  develop -> origin/develop"))
        self.assertIn("afirmacoes=1 sem_lastro=0", self.lastro("Push feito.", "a1b2c3d..e4f5a6b  x -> x"))
        self.assertIn("afirmacoes=1 sem_lastro=0", self.lastro("Suíte: 556 OK.", "Ran 556 tests in 9s\n\nOK"))

    def test_linha_malformada_e_duas_sessoes(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-medida-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for i in (1, 2):
            linhas = [{**o, "sessionId": f"x{i}"} for o in self.subagente("Commit abc1234.", "abc1234" if i == 1 else "z")]
            (tmp / f"s{i}.jsonl").write_text("{quebrada\n" + "".join(json.dumps(o) + "\n" for o in linhas), encoding="utf-8")
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "transcricao", "lastro", str(tmp)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sessao s1: relatorios=1 afirmacoes=1 sem_lastro=0", r.stdout)
        self.assertIn("sessao s2: relatorios=1 afirmacoes=1 sem_lastro=1", r.stdout)
        self.assertIn("total: sessoes=2", r.stdout)
        self.assertIn("2 linhas ignoradas", r.stderr)

    def test_decisao_decidido_encerra_o_grupo(self):
        saida, _ = self.rodar("decisoes", self.jarvis("A) x\nB) y\nDecidido: A."))
        self.assertIn("respostas=1 com_grupo=0 violacoes=0", saida)

    def test_subagente_nao_conta_como_resposta_do_jarvis(self):
        saida, _ = self.rodar("decisoes", self.subagente("A) x\nB) y", "z") + self.jarvis("ok"))
        self.assertIn("respostas=1 com_grupo=0 violacoes=0", saida)


class ConferirBrief(unittest.TestCase):
    """`forge-check brief` (C2, C4) e `brief gerar` (PA-2): forma e corte do brief por regra, sobre fixtures sintéticos."""

    PASTA = RAIZ / "tests" / "fixtures" / "brief"
    PEDIDO = PASTA / "pedido.md"

    def rodar(self, *args, cwd=None):
        r = subprocess.run([sys.executable, str(RAIZ / "bin/forge-check"), "brief", *map(str, args)],
                           capture_output=True, text=True, cwd=cwd or RAIZ)
        return r.returncode, r.stdout

    def conferir(self, nome, *extra, pedido=None):
        return self.rodar(self.PASTA / nome, "--pedido", pedido or self.PEDIDO, *extra)

    def variante(self, nome, troca, pedido=False):
        """Cópia temporária do fixture com uma troca de texto (a troca tem de acertar o texto)."""
        origem = (self.PEDIDO if pedido else self.PASTA / nome).read_text(encoding="utf-8")
        velho, novo = troca
        self.assertIn(velho, origem)
        tmp = Path(tempfile.mkdtemp(prefix="forge-brief-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        destino = tmp / ("pedido.md" if pedido else nome)
        destino.write_text(origem.replace(velho, novo), encoding="utf-8")
        return destino

    def test_etapa_de_outro_papel_nao_e_corte(self):
        rc, saida = self.conferir("etapa-outro-papel.md")
        self.assertIn('corte: etapa (ok) "E3" por E3.1, E3.2, E3.3', saida)
        self.assertNotIn("corte: sem marca", saida)
        self.assertEqual(rc, 0, saida)
        self.assertTrue(saida.endswith("resultado: aprovado\n"))

    def test_corte_sem_marca_reprova(self):
        rc, saida = self.conferir("corte-sem-marca.md")
        self.assertIn('corte: sem marca "E2"', saida)
        self.assertEqual(rc, 1)
        self.assertTrue(saida.endswith("resultado: reprovado\n"))

    def test_corte_completo_passa_e_cada_campo_da_marca_conta(self):
        rc, saida = self.conferir("corte-completo.md")
        self.assertIn('corte: real (marca completa) "E2"', saida)
        self.assertEqual(rc, 0, saida)
        for campo in ("justificativa", "consequência", "decisão"):
            with self.subTest(campo=campo):
                arq = self.variante("corte-completo.md", (f"{campo}:", "motivo:"))
                rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
                self.assertIn(f'corte: sem marca "E2" (falta: {campo}', saida)
                self.assertEqual(rc, 1)

    def test_marca_sem_a_frase_literal_nao_vale(self):
        arq = self.variante("corte-completo.md", ("Retira do escopo original", "Retira do escopo"))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn('corte: sem marca "E2"', saida)
        self.assertEqual(rc, 1)

    def test_trecho_citado_precisa_existir_no_pedido(self):
        arq = self.variante("corte-completo.md", ("Atualizar a documentação do recurso A.", "Escrever outra coisa qualquer."))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn('corte: trecho fora do pedido "E2"', saida)
        self.assertEqual(rc, 1)

    def test_pq_cmd_sem_espera_reprova(self):
        rc, saida = self.conferir("pq-cmd-sem-espera.md")
        self.assertIn("forma: PQ-2 sem espera", saida)
        self.assertEqual(rc, 1)

    def test_espera_invalida_e_tipo_desconhecido_reprovam(self):
        arq = self.variante("etapa-outro-papel.md", ("espera: contém 'recurso'", "espera: parecido com recurso"))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn("forma: PQ-2 sem espera", saida)
        arq = self.variante("etapa-outro-papel.md", ("PQ-3 (push)", "PQ-3 (print)"))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn('forma: PQ-3 tipo desconhecido "print"', saida)
        arq = self.variante("etapa-outro-papel.md", ("PQ-3 (push)", "PQ-3"))
        self.assertIn("forma: PQ-3 sem tipo", self.rodar(arq, "--pedido", self.PEDIDO)[1])

    def test_espera_combinada_e_espera_fraca(self):
        arq = self.variante("etapa-outro-papel.md", ("espera: contém 'recurso'", "espera: rc=0 e contém 'recurso'"))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertEqual(rc, 0, saida)
        arq = self.variante("etapa-outro-papel.md", ("espera: contém 'recurso'", "espera: contém '1'"))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn("aviso: PQ-2 espera fraca", saida)
        self.assertEqual(rc, 0, "aviso não reprova")

    def test_pedido_sem_ids_nao_reprova_o_corte(self):
        rc, saida = self.conferir("corte-sem-marca.md", pedido=self.PASTA / "pedido-sem-ids.md")
        self.assertIn("corte: não verificável (pedido sem IDs)", saida)
        self.assertNotIn("corte: sem marca", saida)
        self.assertEqual(rc, 0, saida)

    def test_item_que_so_existe_em_etapas_e_etapa(self):
        rc, saida = self.conferir("item-so-em-etapas.md")
        self.assertIn('corte: etapa (ok) "E3" por E3.2', saida)
        self.assertEqual(rc, 0, saida)

    def test_item_que_so_existe_em_escopo_e_corte_real(self):
        arq = self.variante("item-so-em-etapas.md", ('"validação de qualidade da branch"', '"Revisão, QA e publicação de cada branch."'))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn('corte: sem marca "E3" (item de ## Escopo retirado sem a marca)', saida)
        self.assertEqual(rc, 1)

    def test_item_do_escopo_sumido_do_brief_e_corte(self):
        arq = self.variante("item-so-em-etapas.md", ("- Documentação do recurso A (E2).\n", ""))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn('corte: sem marca "E2" (nem no Entregar nem no Fora do escopo)', saida)
        self.assertEqual(rc, 1)

    def test_citacao_parecida_nao_cobre_o_item(self):
        for falsa in ("(E10)", "(E1.2)", "E1 sem parênteses"):
            with self.subTest(falsa=falsa):
                arq = self.variante("item-so-em-etapas.md", ("(E1)", falsa))
                self.assertIn('corte: sem marca "E1"', self.rodar(arq, "--pedido", self.PEDIDO)[1])

    def test_etapa_do_papel_do_destino_que_falta_e_corte(self):
        pedido = self.variante("", ("E3.3 (dono)", "E3.4 (dev-exemplo): ajustes pedidos na revisão. E3.3 (dono)"), pedido=True)
        rc, saida = self.conferir("etapa-outro-papel.md", pedido=pedido)
        self.assertIn('corte: sem marca "E3.4" (etapa do papel do destino fora do Entregar)', saida)
        self.assertIn('corte: etapa (ok) "E3"', saida)
        self.assertEqual(rc, 1)
        # outro destino: a etapa passa a ser de outro papel
        rc, saida = self.conferir("etapa-outro-papel.md", "--destino", "forge:revisor", pedido=pedido)
        self.assertNotIn('"E3.4"', saida)

    def test_forma_exige_as_secoes_e_nao_aceita_bloco_sem_preencher(self):
        arq = self.variante("etapa-outro-papel.md", ("## Relatório", "## Outra coisa"))
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn('forma: falta seção "Relatório"', saida)
        self.assertEqual(rc, 1)
        arq = self.variante("etapa-outro-papel.md", ("## Objetivo\n", "## Objetivo\nPREENCHER\n"))
        self.assertIn("forma: bloco gerado sem preencher (PREENCHER)", self.rodar(arq, "--pedido", self.PEDIDO)[1])

    def test_brief_com_commit_precisa_de_pq_que_o_conferente_confira(self):
        arq = self.variante("etapa-outro-papel.md", ("- PQ-1 (sha)", "- PQ-1 (cmd): `pytest` · espera: rc=0 · antes: "))
        arq.write_text(re.sub(r"- PQ-3 \(push\).*\n", "", arq.read_text(encoding="utf-8")), encoding="utf-8")
        rc, saida = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn("forma: sem PQ que o conferente confira", saida)
        self.assertIn("PQ-1: cmd · espera ok · verificador: autor", saida)
        self.assertEqual(rc, 1)

    def test_verificador_do_cmd_segue_a_lista_do_conferente(self):
        fc = carregar_forge_check()
        for cmd in ("git log -1 --format=%h", "gh pr view 12 --json state", "grep -c x a.md && test -e b",
                    "forge-check pr p1", "git -C wt rev-parse HEAD", "bin/forge-check brief a.md --pedido p"):
            with self.subTest(cmd=cmd):
                self.assertTrue(fc.comando_do_conferente(cmd))
        for cmd in ("python3 -m unittest -q", "scripts/validar-plugin.sh", "git push origin x", "gh pr merge 1",
                    "cat a > b", "echo $(id)", "git log | sed 's/a/b/'", "forge-check transcricao custo"):
            with self.subTest(cmd=cmd):
                self.assertFalse(fc.comando_do_conferente(cmd))

    def test_saida_igual_nas_tres_execucoes(self):
        saidas = {self.conferir("etapa-outro-papel.md")[1] for _ in range(3)}
        self.assertEqual(len(saidas), 1)

    def test_linha_do_arquivo_traz_o_hash_completo_e_o_caminho_e_conferido(self):
        arq = self.PASTA / "etapa-outro-papel.md"
        _, saida = self.conferir("etapa-outro-papel.md")
        esperado = hashlib.sha256(arq.read_bytes()).hexdigest()
        self.assertIn(f"arquivo: {len(arq.read_bytes())} bytes sha256 {esperado}", saida)
        self.assertEqual(len(esperado), 64)
        self.assertNotIn("arquivo-caminho", saida)  # sem --destino o caminho não é conferido
        rc, saida = self.conferir("etapa-outro-papel.md", "--destino", "forge:dev-exemplo")
        self.assertIn("forma: Arquivo fora do padrão docs/briefs/pedido-sintetico-dev-exemplo-<n>.md", saida)
        self.assertEqual(rc, 1)
        tmp = Path(tempfile.mkdtemp(prefix="forge-brief-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "docs" / "briefs").mkdir(parents=True)
        certo = tmp / "docs" / "briefs" / "pedido-sintetico-dev-exemplo-1.md"
        certo.write_bytes(arq.read_bytes())
        rc, saida = self.rodar(certo, "--pedido", self.PEDIDO, "--destino", "forge:dev-exemplo")
        self.assertIn("arquivo-caminho: ok", saida)
        self.assertEqual(rc, 0, saida)
        outro = tmp / "docs" / "briefs" / "pedido-sintetico-outro-1.md"
        outro.write_bytes(arq.read_bytes())
        self.assertIn("forma: Arquivo fora do padrão", self.rodar(outro, "--pedido", self.PEDIDO, "--destino", "forge:dev-exemplo")[1])

    def test_arquivo_ou_pedido_ilegivel_sai_com_2(self):
        rc, saida = self.rodar(self.PASTA / "nao-existe.md", "--pedido", self.PEDIDO)
        self.assertEqual(rc, 2)
        rc, saida = self.conferir("etapa-outro-papel.md", pedido=self.PASTA / "nao-existe.md")
        self.assertEqual(rc, 2)

    def test_pedido_por_id_le_docs_pedidos(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-brief-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "docs" / "pedidos").mkdir(parents=True)
        shutil.copy(self.PEDIDO, tmp / "docs" / "pedidos" / "pedido-sintetico.md")
        rc, saida = self.rodar(self.PASTA / "etapa-outro-papel.md", "--pedido", "pedido-sintetico", "--raiz", tmp)
        self.assertEqual(rc, 0, saida)

    # PA-2: brief gerar
    def test_gerar_copia_as_decisoes_literalmente_e_traz_a_marca_e_as_provas(self):
        rc, saida = self.rodar("gerar", "--pedido", self.PEDIDO, "--destino", "forge:dev-exemplo", "--branch", "melhoria/a")
        self.assertEqual(rc, 0, saida)
        for linha in self.PEDIDO.read_text(encoding="utf-8").splitlines():
            if "DECISÃO DO DONO" in linha:
                self.assertIn(f"- {linha}\n", saida)
        self.assertIn("Retira do escopo original", saida)
        self.assertIn("E3.1 (revisor): revisão de código da branch.", saida)
        self.assertNotIn("E1.1 (dev-exemplo)", saida)  # etapa do papel do destino não vai para o Fora do escopo
        self.assertIn("git ls-remote origin refs/heads/melhoria/a", saida)
        self.assertRegex(saida, r"Base-sha: (?:[0-9a-f]{40}|PREENCHER)")
        self.assertEqual(self.rodar("gerar", "--pedido", self.PEDIDO, "--destino", "forge:dev-exemplo", "--branch", "melhoria/a")[1], saida)

    def test_gerar_sem_destino_pede_o_destino_e_o_brief_gerado_nao_passa_sem_preencher(self):
        rc, saida = self.rodar("gerar", "--pedido", self.PEDIDO)
        self.assertIn("PREENCHER: rode com --destino", saida)
        tmp = Path(tempfile.mkdtemp(prefix="forge-brief-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        arq = tmp / "gerado.md"
        arq.write_text(saida, encoding="utf-8")
        rc, conferido = self.rodar(arq, "--pedido", self.PEDIDO)
        self.assertIn("forma: bloco gerado sem preencher (PREENCHER)", conferido)
        self.assertEqual(rc, 1)

    def test_gerar_com_pedido_ilegivel_sai_com_2(self):
        self.assertEqual(self.rodar("gerar", "--pedido", self.PASTA / "nao-existe.md")[0], 2)

    def test_conferente_lista_o_comando_e_a_passada_unica(self):
        conferente = (RAIZ / "agents" / "conferente.md").read_text(encoding="utf-8")
        self.assertIn("forge-check brief <arquivo> --pedido <pedido>", conferente)
        for rel in ("agents/conferente.md", "docs/regras/R-BRIEF.md", "agents/jarvis.md"):
            with self.subTest(arquivo=rel):
                self.assertIn("todos os achados", (RAIZ / rel).read_text(encoding="utf-8"))


class PraticasDeEspecificacao(unittest.TestCase):
    """Critérios EARS, bug, constituição e DORA presentes nos lugares certos."""

    def texto(self, rel: str) -> str:
        return (RAIZ / rel).read_text(encoding="utf-8")

    def test_ux_design_tem_ears_e_bug(self):
        t = self.texto("skills/ux-design/SKILL.md")
        for trecho in ("QUANDO <evento> O SISTEMA DEVE", "## Especificação de bug", "O que não deve mudar", "critério → teste"):
            self.assertIn(trecho, t)

    def test_constituicao_no_modelo_e_no_plano_tecnico(self):
        self.assertTrue((RAIZ / "templates/projeto/docs/constituicao.md").is_file())
        self.assertIn("constituicao.md", self.texto("skills/software-architecture/SKILL.md"))
        self.assertIn("constituicao.md", self.texto("templates/projeto/CLAUDE.md"))

    def test_dora_na_skill_e_no_agile_coach(self):
        for rel in ("skills/kanban-scrum/SKILL.md", "agents/agile-coach.md"):
            t = self.texto(rel)
            for m in ("DORA", "lead time de mudança", "taxa de falha", "recuperação"):
                self.assertIn(m, t.lower() if m.islower() else t, rel)

    def test_qa_converte_criterio_em_teste(self):
        self.assertIn("critério → teste", self.texto("agents/qa-engineer.md"))
