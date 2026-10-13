"""Testes dos hooks do plugin (ADR 0003): cada fixture em tests/hooks/<hook>/<caso>.json roda o script do hook
com a entrada no stdin, num projeto git temporário, e confere o código de saída, o stderr e o estado.

Formato do fixture:
  descricao   texto livre
  forge       false para projeto sem .forge/versao (padrão: true)
  arquivos    {caminho: texto ou lista de linhas} gravados antes do commit inicial (branch develop)
  config      objeto gravado em .forge/config.json; `config_bruta` grava o texto como está
  links       {caminho: alvo} links simbólicos criados depois dos arquivos ({raiz} e {tmp} valem no alvo)
  env         variáveis de ambiente do processo do hook ({tmp} vale; ex.: FORGE_GUARDA_ABERTA, HOME)
  git         passos depois do commit inicial: {"branch": b} | {"checkout": b} | {"worktree": pasta, "branch": b}
              | {"ref": "refs/remotes/origin/b"} (aponta para o HEAD) | {"config": {chave: valor}} (git config local)
              | {"arquivos": {...}, "commit": msg}  ({HEAD} no texto vira o hash do commit atual)
  repos       {pasta relativa a {tmp}: {"arquivos": {...}, "branch": b, "remotos": {nome: url}}} outros repositórios git
              (ex.: um clone do Forge em {tmp}/home/Forge), com um commit inicial
  proc        /proc simulado do hook `agentes`: {"loadavg": texto, "mem_gb": número} ou {"ausente": true}
              (padrão: load 5, 3 GB livres, ou seja, teto adaptativo 3)
  estado      {arquivo: objeto ou texto} gravados em .forge/run/ antes de rodar
  entrada     JSON do hook ({raiz} e {tmp} viram caminhos; "{agora-N}" e os PIDs viram números: "{pid_vivo}" é a
              sessão que chama o hook, "{pid_outro}" outra sessão viva, "{pid_morto}" uma encerrada)
  passos      antes da `entrada`, em ordem: {"entrada": {...}} roda o hook (código 0; no SessionStart, stdout vazio); {"gravar": {caminho: texto}} e
              {"anexar": {caminho: texto}} mexem em arquivos ({tmp} e {raiz} valem; relativo = da raiz do projeto)
  esperado    codigo, saida (trecho do systemMessage; só o `vigia` escreve no stdout), stderr (trecho), estado {arquivo: {contem: [...], ausente: [...]}}, sem_arquivo [...],
              sem_run (true: .forge/run/ não foi criado), erros_log (trecho)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

HOOKS = RAIZ / "hooks"
FIXTURES = Path(__file__).resolve().parent / "hooks"
PESADOS_DA_STACK = json.loads((RAIZ / "stacks/node-react/pesados.json").read_text(encoding="utf-8"))


def pid_morto():
    p = subprocess.Popen([sys.executable, "-c", ""])
    p.wait()
    return p.pid


def substituir(valor, mapa, agora):
    if isinstance(valor, dict):
        return {substituir(k, mapa, agora): substituir(v, mapa, agora) for k, v in valor.items()}
    if isinstance(valor, list):
        return [substituir(v, mapa, agora) for v in valor]
    if isinstance(valor, str):
        m = re.fullmatch(r"\{agora-(\d+)\}", valor)
        if m:
            return agora - int(m.group(1))
        if valor in ("{pid_vivo}", "{pid_outro}", "{pid_morto}"):
            return mapa[valor]
        for chave, texto in mapa.items():
            if isinstance(texto, str):
                valor = valor.replace(chave, texto)
    return valor


def texto(conteudo):
    return "\n".join(conteudo) + "\n" if isinstance(conteudo, list) else conteudo


def conferir_passo(entrada, r):
    """Saída dos `passos`: sempre código 0; no SessionStart o stdout vira contexto do modelo, então tem de ser vazio."""
    assert r.returncode == 0, f"passo {entrada.get('hook_event_name')} saiu com {r.returncode}: {r.stderr}"
    if entrada.get("hook_event_name") == "SessionStart":
        assert r.stdout == "", f"SessionStart não escreve no stdout (ADR 0003, item 1): {r.stdout!r}"


class Fixture:
    def __init__(self, caminho):
        self.caminho = caminho
        self.dados = json.loads(caminho.read_text(encoding="utf-8"))
        self.hook = caminho.parent.name

    def montar(self, tmp, outro):
        raiz = tmp / "proj"
        raiz.mkdir()
        d = self.dados
        mapa = {"{tmp}": str(tmp), "{raiz}": str(raiz), "{pid_vivo}": os.getpid(), "{pid_outro}": outro,
                "{pid_morto}": pid_morto()}
        git("init", "-q", "-b", "develop", cwd=raiz)
        git("config", "user.email", "t@example.com", cwd=raiz)
        git("config", "user.name", "Teste", cwd=raiz)
        arquivos = dict(d.get("arquivos", {}))
        arquivos.setdefault("README.md", "projeto\n")
        if d.get("forge", True):
            arquivos[".forge/versao"] = "0.5.0\n"
        arquivos[".forge/config.json"] = json.dumps({"pesados": PESADOS_DA_STACK})  # como o forge-init grava
        if "config" in d:
            arquivos[".forge/config.json"] = json.dumps(d["config"])
        if "config_bruta" in d:
            arquivos[".forge/config.json"] = d["config_bruta"]
        arquivos[".gitignore"] = ".forge/run/\n"
        self.gravar(raiz, arquivos, mapa)
        for rel, alvo in d.get("links", {}).items():
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (raiz / rel).symlink_to(substituir(alvo, mapa, 0))
        git("add", "-A", cwd=raiz)
        git("commit", "-q", "-m", "base", cwd=raiz)
        for passo in d.get("git", []):
            if "worktree" in passo:
                git("worktree", "add", "-q", "-b", passo["branch"], str(tmp / passo["worktree"]), cwd=raiz)
            elif "branch" in passo:
                git("switch", "-q", "-c", passo["branch"], cwd=raiz)
            elif "checkout" in passo:
                git("switch", "-q", passo["checkout"], cwd=raiz)
            elif "config" in passo:
                for chave, valor in passo["config"].items():
                    git("config", chave, valor, cwd=raiz)
            elif "ref" in passo:  # ex.: refs/remotes/origin/x apontando para o HEAD, como depois de um fetch
                git("update-ref", passo["ref"], "HEAD", cwd=raiz)
            if "arquivos" in passo:
                mapa["{HEAD}"] = git("rev-parse", "HEAD", cwd=raiz).stdout.strip()
                self.gravar(raiz, passo["arquivos"], mapa)
            if "commit" in passo:
                git("add", "-A", cwd=raiz)
                git("commit", "-q", "-m", passo["commit"], cwd=raiz)
        for pasta, conf in d.get("repos", {}).items():
            self.repositorio(tmp / pasta, conf, mapa)
        agora = time.time()
        if d.get("estado"):
            run = raiz / ".forge" / "run"
            run.mkdir(parents=True, exist_ok=True)
            for nome, conteudo in d["estado"].items():
                conteudo = substituir(conteudo, mapa, agora)
                (run / nome).write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo),
                                        encoding="utf-8")
        self.passos = d.get("passos", [])
        self.mapa, self.agora = mapa, agora
        entrada = substituir(d["entrada"], mapa, agora)
        entrada.setdefault("cwd", str(raiz))
        return raiz, entrada

    def executar_passos(self, raiz, rodar_hook):
        """Roda os `passos` (ver o cabeçalho) antes da entrada principal."""
        for passo in self.passos:
            if "entrada" in passo:
                entrada = substituir(passo["entrada"], self.mapa, self.agora)
                entrada.setdefault("cwd", str(raiz))
                conferir_passo(entrada, rodar_hook(entrada))
            for modo, chave in (("w", "gravar"), ("a", "anexar")):
                for caminho, conteudo in passo.get(chave, {}).items():
                    alvo = raiz / substituir(caminho, self.mapa, 0)
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    with open(alvo, modo, encoding="utf-8") as f:
                        f.write(substituir(texto(conteudo), self.mapa, 0))

    def repositorio(self, pasta, conf, mapa):
        """Outro repositório git do fixture (`repos`): arquivos, um commit e os remotos."""
        pasta.mkdir(parents=True)
        git("init", "-q", "-b", conf.get("branch", "develop"), cwd=pasta)
        git("config", "user.email", "t@example.com", cwd=pasta)
        git("config", "user.name", "Teste", cwd=pasta)
        self.gravar(pasta, {"README.md": "repo\n", **conf.get("arquivos", {})}, mapa)
        git("add", "-A", cwd=pasta)
        git("commit", "-q", "-m", "base", cwd=pasta)
        for nome, url in conf.get("remotos", {}).items():
            git("remote", "add", nome, url, cwd=pasta)

    @staticmethod
    def gravar(raiz, arquivos, mapa):
        for rel, conteudo in arquivos.items():
            p = raiz / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(substituir(texto(conteudo), mapa, 0), encoding="utf-8")


def montar_proc(tmp, proc):
    """/proc simulado em tmp/proc (FORGE_PROC); `{"ausente": true}` aponta para uma pasta sem os arquivos."""
    pasta = tmp / "proc"
    pasta.mkdir()
    proc = proc or {"loadavg": "5.00 5.00 5.00 1/100 1", "mem_gb": 3}
    if not proc.get("ausente"):
        (pasta / "loadavg").write_text(proc["loadavg"] + "\n", encoding="utf-8")
        kb = int(proc["mem_gb"] * 1024 * 1024)
        (pasta / "meminfo").write_text(f"MemTotal:       16000000 kB\nMemFree:  1 kB\nMemAvailable:   {kb} kB\n",
                                       encoding="utf-8")
    return pasta


def rodar(hook, entrada, cwd, proc=None, extra=None):
    env = ambiente_limpo()
    env.pop("FORGE_GUARDA_ABERTA", None)
    env.update(extra or {})
    if proc is not None:
        env["FORGE_PROC"] = str(proc)
    return subprocess.run([sys.executable, str(HOOKS / f"{hook}.py")], input=json.dumps(entrada), cwd=cwd,
                          env=env, capture_output=True, text=True, timeout=30)


class Hooks(unittest.TestCase):
    def setUp(self):
        self.fixtures = [Fixture(p) for p in sorted(FIXTURES.glob("*/*.json"))]

    def test_fixtures(self):
        self.assertTrue(self.fixtures, "nenhum fixture em tests/hooks/")
        outro = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])  # outra sessão viva
        self.addCleanup(outro.wait)
        self.addCleanup(outro.kill)
        for f in self.fixtures:
            with self.subTest(fixture=f"{f.hook}/{f.caminho.stem}"):
                tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                raiz, entrada = f.montar(tmp, outro.pid)
                proc = montar_proc(tmp, f.dados.get("proc"))
                extra = {k: v.replace("{tmp}", str(tmp)) for k, v in f.dados.get("env", {}).items()}
                f.executar_passos(raiz, lambda e: rodar(f.hook, e, raiz, proc, extra))
                r = rodar(f.hook, entrada, raiz, proc, extra)
                esperado = f.dados["esperado"]
                if "saida" in esperado:  # só o vigia: aviso ao usuário, nunca contexto para o modelo
                    self.assertEqual(f.hook, "vigia")
                    self.assertNotEqual(entrada.get("hook_event_name"), "SessionStart", "SessionStart é silencioso")
                    saida = json.loads(r.stdout)
                    self.assertEqual(list(saida), ["systemMessage"])
                    self.assertNotIn("\n", saida["systemMessage"], "uma linha só")
                    self.assertRegex(saida["systemMessage"], r"^Forge: \d+ (violação\(ões\)|aviso\(s\)|mudança\(s\))(, \d+ \S+)* — ")
                    self.assertIn(esperado["saida"], saida["systemMessage"])
                else:
                    self.assertEqual(r.stdout, "", "hook nunca escreve no stdout (ADR 0003: silencioso)")
                self.assertEqual(r.returncode, esperado["codigo"], r.stderr)
                if esperado["codigo"] == 0:
                    self.assertEqual(r.stderr, "", "sem violação, sem saída")
                else:
                    linha = r.stderr.rstrip("\n")
                    self.assertNotIn("\n", linha, "uma linha só")
                    self.assertLessEqual(len(linha), 200)
                    self.assertRegex(linha, r"^R-[A-Z]+: ")
                    self.assertIn(esperado["stderr"], linha)
                run = raiz / ".forge" / "run"
                if esperado.get("sem_run"):
                    self.assertFalse(run.exists(), ".forge/run/ não deveria ser criado")
                for nome, conf in esperado.get("estado", {}).items():
                    conteudo = (run / nome).read_text(encoding="utf-8")
                    for trecho in conf.get("contem", []):
                        self.assertIn(trecho, conteudo)
                    for trecho in conf.get("ausente", []):
                        self.assertNotIn(trecho, conteudo)
                for nome in esperado.get("sem_arquivo", []):
                    self.assertFalse((run / nome).exists(), f"{nome} deveria ter sido removido")
                if "erros_log" in esperado:
                    self.assertIn(esperado["erros_log"], (run / "erros.log").read_text(encoding="utf-8"))
                elif run.exists():
                    self.assertFalse((run / "erros.log").exists(), "erro interno inesperado")
                if run.exists() and not f.dados.get("estado"):  # o hook criou .forge/run/
                    self.assertEqual((run / ".gitignore").read_text(encoding="utf-8"), "*\n")

    def test_cada_hook_tem_caso_que_passa_e_que_bloqueia(self):
        scripts = {p.stem for p in HOOKS.glob("*.py") if not p.name.startswith("_")}
        self.assertEqual({f.hook for f in self.fixtures}, scripts)
        for hook in scripts:
            codigos = {f.dados["esperado"]["codigo"] for f in self.fixtures if f.hook == hook}
            nomes = {f.caminho.stem for f in self.fixtures if f.hook == hook}
            with self.subTest(hook=hook):
                self.assertEqual(codigos, {0} if hook == "vigia" else {0, 2})  # o vigia avisa, nunca bloqueia
                self.assertIn("sem-forge-versao", nomes)
                self.assertIn("erro-interno", nomes)

    def test_hooks_json(self):
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        self.assertNotIn("UserPromptSubmit", d["hooks"], "hook não injeta contexto")
        self.assertNotIn("additionalContext", (HOOKS / "vigia.py").read_text(encoding="utf-8").replace(
            "nunca `additionalContext`", ""), "o vigia só avisa o usuário (systemMessage)")
        for evento in ("SessionStart", "Stop"):  # SessionStart: o stdout vira contexto do modelo (ADR 0003, item 1)
            comandos = {h["args"][0].rsplit("/", 1)[-1] for g in d["hooks"].get(evento, []) for h in g["hooks"]}
            self.assertLessEqual(comandos, {"vigia.py"}, f"só o vigia (silencioso, sem stdout) fica em {evento}")
        usados = set()
        for evento, grupos in d["hooks"].items():
            for g in grupos:
                for h in g["hooks"]:
                    with self.subTest(evento=evento, matcher=g.get("matcher")):
                        self.assertEqual(h["command"], "python3", "forma exec, sem shell")
                        self.assertEqual(h.get("timeout"), 10, "sem timeout, o padrão do Claude Code é 600 s")
                        self.assertEqual(len(h["args"]), 1)
                        rel = h["args"][0].replace("${CLAUDE_PLUGIN_ROOT}/", "")
                        self.assertTrue((RAIZ / rel).is_file(), rel)
                        usados.add(Path(rel).stem)
        self.assertEqual(usados, {f.hook for f in self.fixtures})
        matchers = {g.get("matcher") for g in d["hooks"]["PreToolUse"]}
        self.assertIn("Agent|Task", matchers)

    def test_medicao_do_proc_real_nao_quebra(self):
        sys.path.insert(0, str(HOOKS))
        import agentes
        carga, memoria = agentes.medir()
        self.assertTrue(carga is None or carga >= 0)
        self.assertTrue(memoria is None or memoria > 0)
        self.assertEqual(agentes.medir(Path("/nao/existe")), (None, None))

    def test_faixas_do_teto_adaptativo(self):
        sys.path.insert(0, str(HOOKS))
        import agentes
        casos = [((1, 6), 5), ((2.9, 4.1), 5), ((3, 6), 4), ((3.9, 3.1), 4), ((4, 6), 3), ((3.5, 3), 3),
                 ((6, 8), 3), ((6.1, 8), 2), ((0.1, 1.9), 2), ((0.1, 2), 3), ((1, 4), 4)]
        for (carga, memoria), esperado in casos:
            with self.subTest(carga=carga, memoria=memoria):
                self.assertEqual(agentes.teto_adaptativo(carga, memoria), esperado)
        self.assertEqual(agentes.teto_adaptativo(None, 6), 3)

    def test_entrada_invalida_libera(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for hook in ("agentes", "conformidade", "parecer", "pesado", "quadro", "vigia"):
            for entrada in ("", "não é json", "[1, 2]"):
                with self.subTest(hook=hook, entrada=entrada):
                    r = subprocess.run([sys.executable, str(HOOKS / f"{hook}.py")], input=entrada, cwd=tmp,
                                       env=ambiente_limpo(), capture_output=True, text=True, timeout=30)
                    self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_politica_de_conformidade_malformada_bloqueia(self):
        """Entrada de `caminhos` sem chave ou com tipo errado: falha fechado (saída 2), não libera com KeyError."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        malformadas = {"sem motivo": {"caminho": ".github/", "quem": []},
                       "branch não texto": {"caminho": ".github/", "quem": [], "motivo": "m", "branch": 7},
                       "quem não lista": {"caminho": ".github/", "quem": "jarvis", "motivo": "m"},
                       "so_forge não booleano": {"caminho": ".github/", "quem": [], "motivo": "m", "so_forge": "s"},
                       "entrada não objeto": "docs/"}
        for nome, entrada in malformadas.items():
            with self.subTest(nome):
                tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                shutil.copytree(HOOKS, tmp / "plugin" / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
                politica = dict(base, caminhos=[entrada, *base["caminhos"]])
                (tmp / "plugin" / "hooks" / "conformidade.json").write_text(json.dumps(politica), encoding="utf-8")
                raiz = tmp / "proj"
                (raiz / ".forge").mkdir(parents=True)
                (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
                git("init", "-q", "-b", "develop", cwd=raiz)
                entrada_hook = {"tool_name": "Write", "tool_input": {"file_path": str(raiz / ".github/workflows/ci.yml")},
                                "agent_type": "forge:dev", "hook_event_name": "PreToolUse", "cwd": str(raiz)}
                env = ambiente_limpo()
                env.pop("FORGE_GUARDA_ABERTA", None)
                r = subprocess.run([sys.executable, str(tmp / "plugin" / "hooks" / "conformidade.py")],
                                   input=json.dumps(entrada_hook), cwd=raiz, env=env, capture_output=True, text=True,
                                   timeout=30)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("política de conformidade inválida", r.stderr)

    def rodar_com_politica(self, politica, comando, agent_type):
        """Roda o hook sobre uma cópia do plugin com a política dada; devolve o processo."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(HOOKS, tmp / "plugin" / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        (tmp / "plugin" / "hooks" / "conformidade.json").write_text(json.dumps(politica), encoding="utf-8")
        raiz = tmp / "proj"
        (raiz / ".forge").mkdir(parents=True)
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=raiz)
        entrada_hook = {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": agent_type,
                        "hook_event_name": "PreToolUse", "cwd": str(raiz)}
        env = ambiente_limpo()
        env.pop("FORGE_GUARDA_ABERTA", None)
        return subprocess.run([sys.executable, str(tmp / "plugin" / "hooks" / "conformidade.py")],
                              input=json.dumps(entrada_hook), cwd=raiz, env=env, capture_output=True, text=True,
                              timeout=30)

    def test_politica_com_chave_de_topo_malformada_bloqueia(self):
        """Qualquer chave de topo ausente ou com tipo errado: falha fechado (saída 2), nunca libera."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        sem = lambda chave: {k: v for k, v in base.items() if k != chave}
        npm_sem_congelados = {"npm": {"adicionam": ["install"]}}
        malformadas = {
            "papeis em lista": dict(base, papeis=["forge:qa-engineer"]),
            "papeis sem lista de tipos": dict(base, papeis={"qa": "forge:qa-engineer"}),
            "papeis ausente": sem("papeis"),
            "sem_agent_type não texto": dict(base, sem_agent_type=None),
            "sem_agent_type ausente": sem("sem_agent_type"),
            "papel_padrao não texto": dict(base, papel_padrao=3),
            "papel_padrao ausente": sem("papel_padrao"),
            "acoes em lista": dict(base, acoes=["dev"]),
            "acoes com valor não lista": dict(base, acoes={"instalar_pacote": "dev"}),
            "acoes ausente": sem("acoes"),
            "acoes sem ação conhecida": dict(base, acoes={}),
            "pacotes ausente": sem("pacotes"),
            "pacotes em lista": dict(base, pacotes=["npm"]),
            "pacotes: npm sem congelados": dict(base, pacotes=npm_sem_congelados),
            "pacotes: adicionam não lista": dict(base, pacotes={"npm": {"adicionam": "install", "congelados": []}}),
            "pacotes: flags_congeladas não lista": dict(
                base, pacotes={"npm": {"adicionam": [], "congelados": [], "flags_congeladas": None}}),
            "pacotes: so_arquivo não lista": dict(
                base, pacotes={"npm": {"adicionam": [], "congelados": [], "so_arquivo": "-r"}}),
            "flags_congeladas null": dict(base, flags_congeladas=None),
            "flags_congeladas ausente": sem("flags_congeladas"),
            "caminhos ausente": sem("caminhos"),
        }
        for nome, politica in malformadas.items():
            with self.subTest(nome):
                r = self.rodar_com_politica(politica, "echo oi", "forge:dev")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("política de conformidade inválida", r.stderr)

    def test_qa_nao_instala_pacote_com_pacotes_malformado(self):
        """O furo do review: com `pacotes` malformado o `qa` rodava `npm install x`; agora o hook bloqueia."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        politica = dict(base, pacotes={"npm": {"adicionam": ["install"]}})
        r = self.rodar_com_politica(politica, "npm install x", "forge:qa-engineer")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("política de conformidade inválida", r.stderr)

    def test_politica_vigente_passa_na_validacao(self):
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        r = self.rodar_com_politica(base, "echo oi", "forge:dev")
        self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_varredura_do_vigia_nao_desce_em_pastas_ignoradas(self):
        sys.path.insert(0, str(HOOKS))
        import vigia
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        raiz = tmp / "proj"
        (raiz / ".git").mkdir(parents=True)
        (raiz / ".forge").mkdir()
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        (raiz / ".claude").mkdir()
        (raiz / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
        (raiz / ".gitignore").write_text(".forge/run/\n.claude/worktrees/\n", encoding="utf-8")
        for i in range(60):  # 6000 arquivos numa worktree do Claude Code, com node_modules
            pasta = raiz / ".claude" / "worktrees" / f"w{i % 3}" / "node_modules" / f"p{i}"
            pasta.mkdir(parents=True)
            for j in range(100):
                (pasta / f"f{j}.js").write_text("x", encoding="utf-8")
        visitadas = []
        original = os.walk

        def espiao(*a, **k):
            for pasta, dirs, nomes in original(*a, **k):
                visitadas.append(pasta)
                yield pasta, dirs, nomes
        vigia.os.walk = espiao
        try:
            self.assertEqual(sorted(vigia.hashes(raiz)), [".claude/settings.json", ".forge/versao"])
        finally:
            vigia.os.walk = original
        self.assertLess(len(visitadas), 10, "não desce em .claude/worktrees")
        git("init", "-q", "-b", "develop", cwd=raiz)
        git("-c", "user.email=t@example.com", "-c", "user.name=T", "add", "-A", cwd=raiz)
        git("-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-q", "-m", "base", cwd=raiz)
        entrada = {"cwd": str(raiz), "session_id": "s"}
        rodar("vigia", {**entrada, "hook_event_name": "SessionStart", "source": "startup"}, raiz)
        tempos = []
        for _ in range(3):
            t0 = time.perf_counter()
            r = rodar("vigia", {**entrada, "hook_event_name": "Stop"}, raiz)
            tempos.append(time.perf_counter() - t0)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        self.assertLess(sorted(tempos)[1], 1.0, "mediana do Stop com 6000 arquivos em worktrees")

    def test_vigia_estado_e_leitura_do_git_status(self):
        sys.path.insert(0, str(HOOKS))
        import vigia
        self.assertEqual(vigia.caminho_da_linha("R  .githooks/a -> .githooks/b"), ".githooks/b")
        self.assertEqual(vigia.caminho_da_linha('?? ".claude/novo arquivo.md"'), ".claude/novo arquivo.md")
        self.assertEqual(vigia.caminho_da_linha(" M .githooks/pre-push"), ".githooks/pre-push")
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        log = tmp / "violacoes.jsonl"
        log.write_text("x" * (vigia.LIMITE_LOG + 1), encoding="utf-8")
        vigia.rotacionar(log)
        self.assertFalse(log.exists())
        self.assertTrue((tmp / "violacoes.jsonl.1").exists())
        (tmp / "t.jsonl").write_text("", encoding="utf-8")
        agora = time.time()
        estado = {"raizes": {str(tmp): {}, "/nao/existe": {}}, "git": {"/nao/existe": ["x"]},
                  "transcricoes": {str(tmp / "t.jsonl"): 0, "/nao/existe.jsonl": 0},
                  "bloqueios": [{"em": agora}, {"em": agora - 10_000}]}
        vigia.podar(estado, agora, 7200)
        self.assertEqual(list(estado["raizes"]), [str(tmp)])
        self.assertEqual(estado["git"], {})
        self.assertEqual(list(estado["transcricoes"]), [str(tmp / "t.jsonl")])
        self.assertEqual(len(estado["bloqueios"]), 1)


if __name__ == "__main__":
    unittest.main()
