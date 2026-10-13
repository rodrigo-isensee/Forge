"""Testes dos hooks do plugin (ADR 0003): cada fixture em tests/hooks/<hook>/<caso>.json roda o script do hook
com a entrada no stdin, num projeto git temporário, e confere o código de saída, o stderr e o estado.

Formato do fixture:
  descricao   texto livre
  forge       false para projeto sem .forge/versao (padrão: true)
  arquivos    {caminho: texto ou lista de linhas} gravados antes do commit inicial (branch develop)
  config      objeto gravado em .forge/config.json; `config_bruta` grava o texto como está
  git         passos depois do commit inicial: {"branch": b} | {"checkout": b} | {"worktree": pasta, "branch": b}
              | {"ref": "refs/remotes/origin/b"} (aponta para o HEAD)
              | {"arquivos": {...}, "commit": msg}  ({HEAD} no texto vira o hash do commit atual)
  proc        /proc simulado do hook `agentes`: {"loadavg": texto, "mem_gb": número} ou {"ausente": true}
              (padrão: load 5, 3 GB livres, ou seja, teto adaptativo 3)
  estado      {arquivo: objeto ou texto} gravados em .forge/run/ antes de rodar
  entrada     JSON do hook ({raiz} e {tmp} viram caminhos; "{agora-N}" e os PIDs viram números: "{pid_vivo}" é a
              sessão que chama o hook, "{pid_outro}" outra sessão viva, "{pid_morto}" uma encerrada)
  esperado    codigo, stderr (trecho), estado {arquivo: {contem: [...], ausente: [...]}}, sem_arquivo [...],
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

HOOKS = RAIZ / "hooks"
FIXTURES = Path(__file__).resolve().parent / "hooks"
PESADOS_DA_STACK = json.loads((RAIZ / "stacks/node-react/pesados.json").read_text(encoding="utf-8"))


def pid_morto():
    p = subprocess.Popen([sys.executable, "-c", ""])
    p.wait()
    return p.pid


def substituir(valor, mapa, agora):
    if isinstance(valor, dict):
        return {k: substituir(v, mapa, agora) for k, v in valor.items()}
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
        git("add", "-A", cwd=raiz)
        git("commit", "-q", "-m", "base", cwd=raiz)
        for passo in d.get("git", []):
            if "worktree" in passo:
                git("worktree", "add", "-q", "-b", passo["branch"], str(tmp / passo["worktree"]), cwd=raiz)
            elif "branch" in passo:
                git("switch", "-q", "-c", passo["branch"], cwd=raiz)
            elif "checkout" in passo:
                git("switch", "-q", passo["checkout"], cwd=raiz)
            elif "ref" in passo:  # ex.: refs/remotes/origin/x apontando para o HEAD, como depois de um fetch
                git("update-ref", passo["ref"], "HEAD", cwd=raiz)
            if "arquivos" in passo:
                mapa["{HEAD}"] = git("rev-parse", "HEAD", cwd=raiz).stdout.strip()
                self.gravar(raiz, passo["arquivos"], mapa)
            if "commit" in passo:
                git("add", "-A", cwd=raiz)
                git("commit", "-q", "-m", passo["commit"], cwd=raiz)
        agora = time.time()
        if d.get("estado"):
            run = raiz / ".forge" / "run"
            run.mkdir(parents=True, exist_ok=True)
            for nome, conteudo in d["estado"].items():
                conteudo = substituir(conteudo, mapa, agora)
                (run / nome).write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo),
                                        encoding="utf-8")
        entrada = substituir(d["entrada"], mapa, agora)
        entrada.setdefault("cwd", str(raiz))
        return raiz, entrada

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


def rodar(hook, entrada, cwd, proc=None):
    env = ambiente_limpo()
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
                r = rodar(f.hook, entrada, raiz, montar_proc(tmp, f.dados.get("proc")))
                esperado = f.dados["esperado"]
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
                self.assertEqual(codigos, {0, 2})
                self.assertIn("sem-forge-versao", nomes)
                self.assertIn("erro-interno", nomes)

    def test_hooks_json(self):
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        self.assertFalse({"SessionStart", "UserPromptSubmit"} & set(d["hooks"]), "hook não injeta contexto")
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
        for hook in ("agentes", "parecer", "pesado", "quadro"):
            for entrada in ("", "não é json", "[1, 2]"):
                with self.subTest(hook=hook, entrada=entrada):
                    r = subprocess.run([sys.executable, str(HOOKS / f"{hook}.py")], input=entrada, cwd=tmp,
                                       env=ambiente_limpo(), capture_output=True, text=True, timeout=30)
                    self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
