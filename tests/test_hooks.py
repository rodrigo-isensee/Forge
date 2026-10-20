"""Testes dos hooks do plugin (ADR 0003): cada fixture em tests/hooks/<hook>/<caso>.json roda o script do hook
com a entrada no stdin, num projeto git temporário, e confere o código de saída, o stderr e o estado.

Formato do fixture:
  descricao   texto livre
  forge       false para projeto sem .forge/versao (padrão: true)
  arquivos    {caminho: texto ou lista de linhas} gravados antes do commit inicial (branch develop)
  config      objeto gravado em .forge/config.json; `config_bruta` grava o texto como está
  executaveis [caminho] relativos à raiz que ganham permissão de execução (ex.: um `gh` falso, sem rede, no PATH do `env`)
  links       {caminho: alvo} links simbólicos criados depois dos arquivos ({raiz} e {tmp} valem no alvo)
  env         variáveis de ambiente do processo do hook ({tmp} vale; ex.: FORGE_GUARDA_ABERTA, HOME)
  git         passos depois do commit inicial: {"branch": b} | {"checkout": b} | {"worktree": pasta, "branch": b} (com "solto": true, HEAD solto)
              | {"ref": "refs/remotes/origin/b"} (aponta para o HEAD) | {"config": {chave: valor}} (git config local)
              | {"arquivos": {...}, "commit": msg}  ({HEAD} no texto vira o hash do commit atual)
  repos       {pasta relativa a {tmp}: {"arquivos": {...}, "branch": b, "remotos": {nome: url}}} outros repositórios git
              (ex.: um clone do Forge em {tmp}/home/Forge), com um commit inicial
  proc        /proc simulado do hook `agentes`: {"loadavg": texto, "mem_gb": disponível, "mem_total_gb": total (16),
              "nproc": núcleos (8)} ou {"ausente": true} (padrão: sem leitura, ou seja, o padrão 3)
  estado      {arquivo: objeto ou texto} gravados em .forge/run/ antes de rodar
  entrada     JSON do hook ({raiz} e {tmp} viram caminhos; "{agora-N}" e os PIDs viram números: "{pid_vivo}" é a
              sessão que chama o hook, "{pid_outro}" outra sessão viva, "{pid_morto}" uma encerrada)
  passos      antes da `entrada`, em ordem: {"entrada": {...}} roda o hook (código 0; no SessionStart, stdout vazio); {"gravar": {caminho: texto}} e
              {"anexar": {caminho: texto}} mexem em arquivos ({tmp} e {raiz} valem; relativo = da raiz do projeto)
              Também em passos: {"remover": [caminho]} apaga arquivos (como um `git rm` que o hook não viu) e
              {"git": [argumentos]} roda o git no projeto (como um comando que o hook não viu, ex.: sparse-checkout)
              Em caminhos e textos, {marca} e {marca_wt} valem pela marca da sessão (`.git/forge/projeto-<hash da raiz>`) do
              projeto e da worktree `{tmp}/wt`
  esperado    codigo, saida (trecho do systemMessage; só o `vigia` escreve no stdout), pergunta (trecho do motivo: só o
              `conformidade` pede confirmação, `permissionDecision: ask` no stdout, código 0), stderr (trecho), estado {arquivo: {contem: [...], ausente: [...]}}, sem_arquivo [...],
              sem_run (true: .forge/run/ não foi criado), erros_log (trecho)
              sem_caminho ([caminho]: não existem; {tmp} vale)
"""
import concurrent.futures
import contextlib
import hashlib
import io
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
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo, git, minimo  # noqa: E402
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
        for chave, pasta in (("{marca}", raiz), ("{marca_wt}", tmp / "wt")):  # a marca da sessão: uma por raiz
            mapa[chave] = f".git/forge/projeto-{hashlib.sha256(os.path.realpath(pasta).encode()).hexdigest()[:16]}"
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
        for rel in d.get("executaveis", []):
            (raiz / rel).chmod(0o755)
        for rel, alvo in d.get("links", {}).items():
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (raiz / rel).symlink_to(substituir(alvo, mapa, 0))
        git("add", "-A", cwd=raiz)
        git("commit", "-q", "-m", "base", cwd=raiz)
        for passo in d.get("git", []):
            if "worktree" in passo:
                if passo.get("solto"):  # HEAD solto, sem branch (cópia de review)
                    git("worktree", "add", "-q", "--detach", str(tmp / passo["worktree"]), cwd=raiz)
                else:
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
            for caminho in passo.get("remover", []):
                (raiz / substituir(caminho, self.mapa, 0)).unlink()
            if "git" in passo:
                git(*substituir(passo["git"], self.mapa, 0), cwd=raiz)
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
    proc = proc or {"ausente": True}
    if not proc.get("ausente"):
        (pasta / "loadavg").write_text(proc["loadavg"] + "\n", encoding="utf-8")
        kb = int(proc["mem_gb"] * 1024 * 1024)
        total = int(proc.get("mem_total_gb", 16) * 1024 * 1024)
        (pasta / "meminfo").write_text(f"MemTotal:       {total} kB\nMemFree:  1 kB\nMemAvailable:   {kb} kB\n",
                                       encoding="utf-8")
    return pasta


def rodar(hook, entrada, cwd, proc=None, extra=None):
    env = ambiente_limpo()
    env.pop("FORGE_GUARDA_ABERTA", None)
    env.pop("FORGE_CARGA_LIVRE", None)
    env.update(extra or {})
    if proc is not None:
        env["FORGE_PROC"] = str(proc)
    return subprocess.run([sys.executable, str(HOOKS / f"{hook}.py")], input=json.dumps(entrada), cwd=cwd,
                          env=env, capture_output=True, text=True, timeout=30)


class Hooks(unittest.TestCase):
    def setUp(self):
        self.fixtures = minimo([Fixture(p) for p in sorted(FIXTURES.glob("*/*.json"))], 460, "fixtures em tests/hooks/")

    def test_fixtures(self):
        self.assertTrue(self.fixtures, "nenhum fixture em tests/hooks/")
        outro = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])  # outra sessão viva
        self.addCleanup(outro.wait)
        self.addCleanup(outro.kill)
        em_serie = [f for f in self.fixtures if self.depende_de_pid_ou_trava(f)]
        em_paralelo = [f for f in self.fixtures if f not in em_serie]
        verificados = []
        # Montar e rodar é espera de subprocesso (não segura o GIL); cada fixture tem a sua pasta temporária.
        # As falhas voltam como objeto e viram subTest na thread principal, com o mesmo nome de caso.
        trabalhadores = max(1, min(4, (os.cpu_count() or 2) // 2))
        with concurrent.futures.ThreadPoolExecutor(max_workers=trabalhadores) as pool:
            futuros = [(f, pool.submit(self.executar_fixture, f, self._pasta_temporaria(), outro.pid))
                       for f in em_paralelo]
            for f, futuro in futuros:
                with self.subTest(fixture=f"{f.hook}/{f.caminho.stem}"):
                    verificados.append(f)
                    erro = futuro.exception()
                    if erro is not None:
                        raise erro
        for f in em_serie:  # PID e trava global do `pesado`: um de cada vez, depois do paralelo
            with self.subTest(fixture=f"{f.hook}/{f.caminho.stem}"):
                verificados.append(f)
                self.executar_fixture(f, self._pasta_temporaria(), outro.pid)
        self.assertEqual(len(verificados), len(self.fixtures), "todo fixture é verificado")

    def _pasta_temporaria(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        return tmp

    @staticmethod
    def depende_de_pid_ou_trava(f):
        return f.hook == "pesado" or "{pid_" in json.dumps(f.dados)

    def executar_fixture(self, f, tmp, outro_pid):
        raiz, entrada = f.montar(tmp, outro_pid)
        proc = montar_proc(tmp, f.dados.get("proc"))
        extra = {k: v.replace("{tmp}", str(tmp)) for k, v in f.dados.get("env", {}).items()}
        extra["FORGE_NPROC"] = str((f.dados.get("proc") or {}).get("nproc", 8))
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
        elif "pergunta" in esperado:  # só o conformidade: pede a confirmação da pessoa, com a consequência
            self.assertEqual(f.hook, "conformidade")
            saida = json.loads(r.stdout)["hookSpecificOutput"]
            self.assertEqual((saida["hookEventName"], saida["permissionDecision"]), ("PreToolUse", "ask"))
            self.assertNotIn("\n", saida["permissionDecisionReason"], "uma linha só")
            self.assertIn(esperado["pergunta"], saida["permissionDecisionReason"])
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
        for caminho in esperado.get("sem_caminho", []):
            self.assertFalse(Path(substituir(caminho, f.mapa, 0)).exists(), f"{caminho} não deveria existir")
        for nome in esperado.get("sem_arquivo", []):
            self.assertFalse((run / nome).exists(), f"{nome} deveria ter sido removido")
        if "erros_log" in esperado:
            self.assertIn(esperado["erros_log"], (run / "erros.log").read_text(encoding="utf-8"))
        elif (run / "erros.log").exists():  # só o aviso do FORGE_NPROC/FORGE_PROC (que os testes fixam) é esperado
            outras = [l for l in (run / "erros.log").read_text(encoding="utf-8").splitlines() if " Aviso: FORGE_" not in l]
            self.assertEqual(outras, [], "erro interno inesperado")
        if run.exists() and not f.dados.get("estado"):  # o hook criou .forge/run/
            self.assertEqual((run / ".gitignore").read_text(encoding="utf-8"), "*\n")


    def test_git_rm_com_pathspec_magico_bloqueia(self):
        """As formas do pathspec do git (`:(literal)`, `:(glob)`, `:(icase)`, `:/`, curinga e `-r :/`) valem pelo que o git
        resolve, como `:(top)` (fixture `git-rm-pathspec-magica-bloqueia`); pathspec que não alcança caminho em vigor passa."""
        formas = {"git rm ':(literal).forge/versao'": 2, "git rm ':(glob)**/versao'": 2, "git rm ':(icase).FORGE/VERSAO'": 2,
                  "git rm ':/.forge/versao'": 2, "git rm '*versao'": 2, "git rm -r ':/'": 2, "git rm -r '*'": 2,
                  "git checkout HEAD -- ':(top).forge/versao'": 2, "git restore -s HEAD ':(glob)**/versao'": 2,
                  "git rm ':(top)src/app.js'": 0, "git rm 'src/*.js'": 0, "git checkout -- .": 0, "git restore .": 0}
        for comando, codigo in formas.items():
            with self.subTest(comando=comando):
                tmp = self._pasta_temporaria()
                dados = {"arquivos": {"src/app.js": "v1\n", ".githooks/pre-push": "#!/bin/sh\n"},
                         "env": {"CLAUDE_PROJECT_DIR": "{tmp}/proj"},
                         "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": "forge:dev",
                                     "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
                         "esperado": {"codigo": codigo, "stderr": "R-CONFORMIDADE"}}
                arquivo = tmp / "conformidade" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(dados), encoding="utf-8")
                self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    def test_pathspecs_por_variavel_de_ambiente_valem_como_as_opcoes(self):
        """`GIT_*_PATHSPECS` (atribuição na linha, `env`, `export`) ligam o modo de pathspec como as opções `--*-pathspecs`
        (fixture `git-rm-env-icase-pathspecs-bloqueia`); falso explícito e pathspec que não alcança caminho em vigor passam."""
        formas = {"GIT_ICASE_PATHSPECS=1 git rm .FORGE/VERSAO": 2, "env GIT_ICASE_PATHSPECS=1 git rm -q .FORGE/VERSAO": 2,
                  "export GIT_ICASE_PATHSPECS=1; git rm .FORGE/VERSAO": 2,
                  "GIT_ICASE_PATHSPECS=1 git checkout HEAD -- .FORGE/VERSAO": 2,
                  "GIT_GLOB_PATHSPECS=1 git rm '**/versao'": 2, "GIT_ICASE_PATHSPECS=0 git rm .FORGE/VERSAO": 0,
                  "GIT_ICASE_PATHSPECS=1 git rm src/app.js": 0}
        for comando, codigo in formas.items():
            with self.subTest(comando=comando):
                tmp = self._pasta_temporaria()
                dados = {"arquivos": {"src/app.js": "v1\n", ".githooks/pre-push": "#!/bin/sh\n"},
                         "env": {"CLAUDE_PROJECT_DIR": "{tmp}/proj"},
                         "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": "forge:dev",
                                     "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
                         "esperado": {"codigo": codigo, "stderr": "R-CONFORMIDADE"}}
                arquivo = tmp / "conformidade" / "caso.json"
                arquivo.parent.mkdir()
                arquivo.write_text(json.dumps(dados), encoding="utf-8")
                self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    # R-CONTRIB: o rótulo afrouxa-regra só do dono (fixtures `rotulo-so-dono-*`); aqui, as formas da volta 1 -----------
    @staticmethod
    def dados_da_sessao_do_forge(comando, gh, codigo):
        """Sessão do Forge (a raiz é um clone do Forge, sem `.forge/versao`) com um `gh` falso no PATH, sem rede."""
        esperado = {"codigo": codigo}
        if codigo:
            esperado["stderr"] = "R-CONTRIB: "
        return {"arquivos": {"src/app.js": "v1\n", "bin/gh": gh, ".claude-plugin/plugin.json": "{\"name\": \"forge\"}"},
                "executaveis": ["bin/gh"], "forge": False,
                "env": {"HOME": "{tmp}/home", "CLAUDE_PROJECT_DIR": "{tmp}/proj", "PATH": "{tmp}/proj/bin:/usr/bin:/bin"},
                "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "hook_event_name": "PreToolUse",
                            "tool_use_id": "toolu_9"},
                "esperado": esperado}

    def rodar_dados(self, dados):
        tmp = self._pasta_temporaria()
        arquivo = tmp / "conformidade" / "caso.json"
        arquivo.parent.mkdir()
        arquivo.write_text(json.dumps(dados), encoding="utf-8")
        self.executar_fixture(Fixture(arquivo), tmp, os.getpid())

    def test_rotulo_so_dono_formas_alternativas(self):
        """Volta 1 (segurança A2, A3, A4 e R2): GraphQL por caminho ou URL, REST com `?…` ou `#…`, crase (fora de aspas
        simples) e criar ou renomear rótulo com o nome barram outra conta; a conta do dono passa; o resto não muda."""
        mutacao = "mutation { addLabelsToLabelable(input:{labelableId:\\\"X\\\", labelIds:[\\\"Y\\\"]}) { clientMutationId } }"
        barram = [
            f"gh api /graphql -f query=\"{mutacao}\"",
            f"gh api https://api.github.com/graphql -f query=\"{mutacao}\"",
            f"gh api https://ghe.exemplo/api/graphql -f query=\"{mutacao}\"",
            f"gh api 'graphql?x=1' -f query=\"{mutacao}\"",
            "gh api 'repos/o/r/issues/70/labels?x=1' -f 'labels[]=afrouxa-regra'",
            "gh api 'repos/o/r/issues/70/labels#x' -f 'labels[]=afrouxa-regra'",
            "gh api 'https://api.github.com/repos/o/r/issues/70/labels/' -f 'labels[]=afrouxa-regra'",
            "echo `gh pr edit 70 --add-label afrouxa-regra`",
            "x=`gh pr edit 70 --add-label afrouxa-regra`",
            "echo \"a `gh issue edit 70 --add-label afrouxa-regra` b\"",
            "bash -c 'echo `gh pr edit 70 --add-label afrouxa-regra`'",
            "echo `gh pr edit 70 --add-label afrouxa-regra",  # crase sem par: não se analisa e cita o rótulo
            "gh label create afrouxa-regra",
            "gh label edit tmp --name afrouxa-regra",
            "gh label edit afrouxa-regra --name tmp",
            "gh api -X PATCH repos/o/r/labels/afrouxa-regra -f new_name=tmp",
            "gh api repos/o/r/labels/tmp -X PATCH -f new_name=afrouxa-regra",
            "gh api repos/o/r/labels -f name=afrouxa-regra",
            "gh api graphql -f query='mutation { updateLabel(input:{id:\"L\", name:\"x\"}) { clientMutationId } }'",
            "gh api /graphql -f query='mutation { createLabel(input:{repositoryId:\"R\", name:\"x\"}) { clientMutationId } }'",
        ]
        passam = ["echo 'a `gh pr edit 70 --add-label afrouxa-regra` b'", "gh issue comment 70 --body 'cite `afrouxa-regra`'",
                  "gh label create bug", "gh label edit bug --name defeito", "gh pr edit 70 --add-label bug",
                  "gh api /graphql -f query='query { viewer { login } }'", "gh api 'repos/o/r/issues/70/labels?x=1' -f 'labels[]=bug'",
                  "echo `date`"]
        casos = [(c, "#!/bin/sh\necho outra-pessoa\n", 2) for c in barram]
        casos += [(c, "#!/bin/sh\necho outra-pessoa\n", 0) for c in passam]
        casos += [(c, "#!/bin/sh\necho Rodrigo-Isensee\n", 0) for c in barram[:9] + barram[12:15]]
        for comando, gh, codigo in minimo(casos, 40, "casos de rótulo"):
            with self.subTest(comando=comando, gh=gh.split()[-1], codigo=codigo):
                self.rodar_dados(self.dados_da_sessao_do_forge(comando, gh, codigo))

    def test_rotulo_so_dono_volta_2_crase_escapada_comentario_clone_e_remocao(self):
        """Volta 2 (segurança B1, review 1 a 3): a crase escapada em `bash -c`/`sh -c`/`eval`, a aspa simples de um comentário
        antes da crase, `gh label clone` e `--remove-label afrouxa-regra` exigem o dono; a conta do dono passa; o resto não muda."""
        rotulo = "gh pr edit 70 --add-label afrouxa-regra"
        barram = [
            f'bash -c "echo \\`{rotulo}\\`"',
            f'sh -c "x=\\`{rotulo}\\`"',
            f'eval "echo \\`{rotulo}\\`"',
            f"echo hi # don't\nx=`{rotulo}`",
            f"echo hi # don't\necho \"`{rotulo}`\"",
            "gh label clone o/outro",
            "gh label clone o/outro --force",
            "gh pr edit 70 --remove-label afrouxa-regra",
            "gh issue edit 70 --remove-label=afrouxa-regra",
            "gh pr edit 70 --remove-label bug,afrouxa-regra",
            "gh api -X DELETE repos/o/r/issues/70/labels/afrouxa-regra",
        ]
        passam = [f'bash -c "echo \\`date\\`"', f'echo "\\`{rotulo}\\`"', f"echo hi # don't\nx=`date`",
                  "echo a # `" + rotulo + "`", "gh pr edit 70 --remove-label bug", "gh label list"]
        casos = [(c, "#!/bin/sh\necho outra-pessoa\n", 2) for c in barram]
        casos += [(c, "#!/bin/sh\necho outra-pessoa\n", 0) for c in passam]
        casos += [(c, "#!/bin/sh\necho Rodrigo-Isensee\n", 0) for c in barram]
        for comando, gh, codigo in minimo(casos, 20, "casos de rótulo da volta 2"):
            with self.subTest(comando=comando, gh=gh.split()[-1], codigo=codigo):
                self.rodar_dados(self.dados_da_sessao_do_forge(comando, gh, codigo))

    def test_rotulo_so_dono_volta_2_sessao_de_projeto(self):
        """Segurança R5: as formas da crase escapada e do comentário também são barradas na sessão de projeto (R-CONTRIB),
        quando apontam para o Forge; a mesma linha sem apontar para o Forge passa."""
        alvo = "gh pr edit https://github.com/rodrigo-isensee/Forge/pull/70 --add-label afrouxa-regra"
        casos = [
            (f'bash -c "echo \\`{alvo}\\`"', 2), (f'sh -c "x=\\`{alvo}\\`"', 2), (f'eval "echo \\`{alvo}\\`"', 2),
            (f"echo hi # don't\nx=`{alvo}`", 2), (f"echo hi # don't\necho \"`{alvo}`\"", 2),
            ('bash -c "echo \\`date\\`"', 0), ("echo hi # don't\nx=`date`", 0),
        ]
        for comando, codigo in minimo(casos, 6, "casos de projeto da volta 2"):
            with self.subTest(comando=comando):
                esperado = {"codigo": codigo}
                if codigo:  # barra por R-CONTRIB (alvo no Forge) ou R-CONFORMIDADE (crase com ação crítica, não modelada)
                    esperado["stderr"] = "R-CON"
                self.rodar_dados({"arquivos": {"src/app.js": "v1\n"}, "env": {"HOME": "{tmp}/home", "CLAUDE_PROJECT_DIR": "{tmp}/proj"},
                                  "entrada": {"tool_name": "Bash", "tool_input": {"command": comando}, "hook_event_name": "PreToolUse",
                                              "tool_use_id": "toolu_9"}, "esperado": esperado})

    def test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook(self):
        """Segurança A1: `gh` que não responde (com um filho segurando a saída) barra dentro do timeout do hook."""
        limite = min(h["timeout"] for g in json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
                     for h in g["hooks"] if h["args"][0].endswith("/conformidade.py"))
        inicio = time.monotonic()
        self.rodar_dados(self.dados_da_sessao_do_forge("gh pr edit 70 --add-label afrouxa-regra",
                                                       "#!/bin/sh\nsleep 30\necho outra-pessoa\n", 2))
        self.assertLess(time.monotonic() - inicio, limite - 1, "a decisão sai antes do Claude Code matar o hook")

    def test_timeout_de_rede_dos_hooks_abaixo_do_hooks_json(self):
        """Segurança A1: todo subprocesso de rede dos hooks (`gh`, `curl`, `git fetch`...) tem limite de tempo menor que o
        menor timeout do hooks.json; senão o Claude Code mata o hook e o comando segue (falha aberta)."""
        import ast
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        limite = min(h["timeout"] for grupos in d["hooks"].values() for g in grupos for h in g["hooks"])
        rede, git_rede = {"gh", "curl", "wget", "ssh"}, {"fetch", "pull", "push", "ls-remote", "clone"}
        achados = []
        for arquivo in minimo(sorted(HOOKS.glob("*.py")), 5, "scripts de hook"):
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
            constantes = {alvo.id: no.value.value for no in arvore.body if isinstance(no, ast.Assign)
                          and isinstance(no.value, ast.Constant) for alvo in no.targets if isinstance(alvo, ast.Name)}
            for funcao in (n for n in ast.walk(arvore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
                listas = [n for n in ast.walk(funcao) if isinstance(n, ast.List) and n.elts
                          and isinstance(n.elts[0], ast.Constant)]
                de_rede = [n for n in listas if n.elts[0].value in rede or n.elts[0].value == "git" and any(
                    isinstance(e, ast.Constant) and e.value in git_rede for e in n.elts[1:])]
                if not de_rede:
                    continue
                prazos = [k.value for n in ast.walk(funcao) if isinstance(n, ast.Call) for k in n.keywords if k.arg == "timeout"]
                with self.subTest(arquivo=arquivo.name, funcao=funcao.name):
                    achados.append(funcao.name)
                    self.assertTrue(prazos, "subprocesso de rede sem timeout")
                    for prazo in prazos:
                        valor = prazo.value if isinstance(prazo, ast.Constant) else constantes.get(getattr(prazo, "id", None))
                        self.assertIsInstance(valor, (int, float), f"timeout não resolvido: {ast.dump(prazo)}")
                        self.assertLess(valor, limite, f"timeout {valor} s não fica abaixo dos {limite} s do hooks.json")
        minimo(achados, 1, "subprocessos de rede nos hooks")

    def test_rotulo_so_dono_erro_inesperado_falha_fechado(self):
        """Revisão (4) e segurança R3: erro do analisador que não é ValueError barra na sessão do Forge quando a linha
        cita o rótulo (mesmo com a conta do dono: o hook não pôde decidir); a linha que não cita segue a regra geral."""
        for comando, codigo in {"gh pr edit 70 --add-label afrouxa-regra": 2, "gh pr edit 70 --add-label bug": 0,
                                "gh api graphql -f query='mutation { addLabelsToLabelable(input:{}) { x } }'": 2}.items():
            with self.subTest(comando=comando):
                tmp = self._pasta_temporaria()
                f = Fixture.__new__(Fixture)
                f.caminho, f.hook = tmp / "conformidade" / "caso.json", "conformidade"
                f.dados = self.dados_da_sessao_do_forge(comando, "#!/bin/sh\necho Rodrigo-Isensee\n", codigo)
                raiz, entrada = f.montar(tmp, os.getpid())
                envoltorio = tmp / "envoltorio.py"
                envoltorio.write_text(
                    f"import sys\nsys.path.insert(0, {str(HOOKS)!r})\nimport conformidade\n"
                    "def quebra(*a, **k):\n    raise RuntimeError('quebra de teste')\n"
                    "conformidade.conteudos_de_crase = quebra\n"
                    "conformidade.executar('conformidade', conformidade.principal, conformidade.CRITICO)\n", encoding="utf-8")
                env = ambiente_limpo()
                env.pop("FORGE_GUARDA_ABERTA", None)
                env.update({k: v.replace("{tmp}", str(tmp)) for k, v in f.dados["env"].items()})
                r = subprocess.run([sys.executable, str(envoltorio)], input=json.dumps(entrada), cwd=raiz, env=env,
                                   capture_output=True, text=True, timeout=30)
                self.assertEqual(r.returncode, codigo, r.stderr)
                if codigo:
                    self.assertIn("R-CONTRIB: erro interno ao conferir o rótulo afrouxa-regra", r.stderr)

    def test_contrib_graphql_por_caminho_na_sessao_de_projeto(self):
        """Segurança R4: na sessão de projeto, `/graphql` e a URL completa do GraphQL valem como `graphql` (R-CONTRIB)."""
        consulta = "mutation { closePullRequest(input:{pullRequestId:\"X\"}) { clientMutationId } }"
        casos = {f"gh api /graphql -f query='{consulta}'": 2, f"gh api https://api.github.com/graphql -f query='{consulta}'": 2,
                 "gh api /graphql -f query='mutation { addLabelsToLabelable(input:{labelableId:\"X\"}) { x } }'": 2,
                 "gh api 'graphql?a=1' -f query='mutation { updatePullRequest(input:{}) { x } }'": 2,
                 "gh api /graphql -f query='query { viewer { login } }'": 0}
        for comando, codigo in casos.items():
            with self.subTest(comando=comando):
                esperado = {"codigo": codigo, **({"stderr": "R-CONTRIB: gh api"} if codigo else {})}
                self.rodar_dados({"arquivos": {"src/app.js": "v1\n"}, "env": {"HOME": "{tmp}/home"},
                                  "entrada": {"tool_name": "Bash", "tool_input": {"command": comando},
                                              "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
                                  "esperado": esperado})

    def test_marca_de_projeto_por_raiz_e_nunca_apagada(self):
        """A chave da marca é a raiz da cópia de trabalho: a worktree irmã tem marca própria e não herda a do clone; o
        `SessionStart` só grava, nunca apaga."""
        import _comum
        tmp = self._pasta_temporaria()
        clone, wt = tmp / "clone", tmp / "wt"
        clone.mkdir()
        git("init", "-q", "-b", "develop", cwd=clone)
        git("config", "user.email", "t@example.com", cwd=clone)
        git("config", "user.name", "Teste", cwd=clone)
        (clone / ".forge").mkdir()
        (clone / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("add", "-A", cwd=clone)
        git("commit", "-q", "-m", "base", cwd=clone)
        git("worktree", "add", "-q", "-b", "melhoria/w", str(wt), cwd=clone)
        self.assertNotEqual(_comum.marca_de_projeto(clone), _comum.marca_de_projeto(wt))
        self.assertEqual(_comum.marca_de_projeto(clone).parent, _comum.marca_de_projeto(wt).parent)
        _comum.marcar_projeto(clone)
        (wt / ".forge" / "versao").unlink()
        self.assertTrue(_comum.projeto_marcado(clone))
        self.assertFalse(_comum.projeto_marcado(wt), "a worktree irmã não herda a marca do clone")
        self.assertIsNone(_comum.raiz_do_projeto(wt))
        _comum.marcar_projeto(wt)  # sem `.forge/versao`: não grava e, sobretudo, não apaga a marca do clone
        self.assertTrue(_comum.marca_de_projeto(clone).is_file())

    def test_cada_hook_tem_caso_que_passa_e_que_bloqueia(self):
        scripts = {p.stem for p in minimo(HOOKS.glob("*.py"), 5, "scripts de hook") if not p.name.startswith("_")}
        self.assertEqual({f.hook for f in self.fixtures}, scripts)
        for hook in scripts:
            codigos = {f.dados["esperado"]["codigo"] for f in self.fixtures if f.hook == hook}
            nomes = {f.caminho.stem for f in self.fixtures if f.hook == hook}
            with self.subTest(hook=hook):
                self.assertEqual(codigos, {0} if hook in ("vigia", "doutor") else {0, 2})  # o vigia e o doutor avisam, nunca bloqueiam
                self.assertIn("sem-forge-versao", nomes)
                self.assertIn("erro-interno", nomes)

    def test_hooks_json(self):
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        self.assertNotIn("UserPromptSubmit", d["hooks"], "hook não injeta contexto")
        self.assertNotIn("additionalContext", (HOOKS / "vigia.py").read_text(encoding="utf-8").replace(
            "nunca `additionalContext`", ""), "o vigia só avisa o usuário (systemMessage)")
        for evento in ("SessionStart", "Stop"):  # SessionStart: o stdout vira contexto do modelo (ADR 0003, item 1)
            comandos = {h["args"][0].rsplit("/", 1)[-1] for g in d["hooks"].get(evento, []) for h in g["hooks"]}
            self.assertLessEqual(comandos, {"vigia.py", "doutor.py"}, f"só o vigia e o doutor (sem stdout no SessionStart) ficam em {evento}")
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
        minimo(usados, 5, "hooks registrados em hooks.json")
        self.assertEqual(usados, {f.hook for f in self.fixtures})
        matchers = {g.get("matcher") for g in d["hooks"]["PreToolUse"]}
        self.assertIn("Agent|Task", matchers)

    def test_medicao_do_proc_real_nao_quebra(self):
        sys.path.insert(0, str(HOOKS))
        import agentes
        carga, memoria, total = agentes.medir()
        self.assertTrue(carga is None or carga >= 0)
        self.assertTrue(memoria is None or memoria > 0)
        self.assertTrue(total is None or total >= (memoria or 0))
        self.assertEqual(agentes.medir(Path("/nao/existe")), (None, None, None))
        self.assertTrue((agentes.nucleos() or 1) >= 1)

    def test_faixas_do_teto_segue_o_hardware(self):
        """R-TETO: bloqueia com load >= 0,8 x nproc ou MemAvailable <= max(1 GB, 15% do total); o teto é nproc."""
        sys.path.insert(0, str(HOOKS))
        import agentes
        casos = [  # (load, disponível, total, nproc, carga alta)
            (3, 6, 8, 16, False), (12.7, 6, 8, 16, False), (12.8, 6, 8, 16, True),
            (6.39, 8, 16, 8, False), (6.4, 8, 16, 8, True), (0.1, 2.5, 16, 8, False), (0.1, 2.4, 16, 8, True),
            (0.1, 1.1, 4, 8, False), (0.1, 1.0, 4, 8, True), (0.8, 8, 16, 1, True), (0.7, 8, 16, 1, False)]
        for carga, memoria, total, nproc, alta in casos:
            with self.subTest(carga=carga, memoria=memoria, total=total, nproc=nproc):
                self.assertEqual(agentes.carga_alta(carga, memoria, total, nproc), alta)
                self.assertEqual(agentes.teto_adaptativo(carga, memoria, total, nproc), nproc)
        for faltando in range(4):  # sem uma das medidas: nunca é carga alta e o teto cai no padrão 3
            medidas = [1.0, 6.0, 16.0, 8]
            medidas[faltando] = None
            self.assertFalse(agentes.carga_alta(*medidas))
            self.assertEqual(agentes.teto_adaptativo(*medidas), 3)

    def test_teto_sem_leitura_nunca_passa_de_nproc(self):  # A3
        sys.path.insert(0, str(HOOKS))
        import agentes
        for nproc, esperado in ((1, 1), (2, 2), (3, 3), (8, 3), (None, 3)):
            with self.subTest(nproc=nproc):
                self.assertEqual(agentes.teto_adaptativo(None, None, None, nproc), esperado)

    def test_teto_maximo_vale_igual_sobre_o_fixo_e_o_adaptativo(self):  # A2
        sys.path.insert(0, str(HOOKS))
        import agentes
        pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, pasta, True)
        (pasta / "loadavg").write_text("0.1\n", encoding="utf-8")
        (pasta / "meminfo").write_text("MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"FORGE_NPROC": "16"}):
            self.assertEqual(agentes.calcular_teto({"teto_agentes": 8, "teto_maximo": 5}, pasta)[0], 5)
            self.assertEqual(agentes.calcular_teto({"teto_agentes": 4, "teto_maximo": 5}, pasta)[0], 4)
            self.assertEqual(agentes.calcular_teto({"teto_maximo": 5}, pasta)[0], 5)
            self.assertEqual(agentes.calcular_teto({}, pasta)[0], 16)

    def test_nucleos_respeita_a_afinidade(self):  # A4
        sys.path.insert(0, str(HOOKS))
        import agentes
        env = {k: v for k, v in os.environ.items() if k != "FORGE_NPROC"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(os, "sched_getaffinity", create=True, return_value={0, 1}), \
                    mock.patch.object(os, "cpu_count", return_value=16):
                self.assertEqual(agentes.nucleos(), 2)
            with mock.patch.object(os, "sched_getaffinity", create=True, side_effect=OSError), \
                    mock.patch.object(os, "cpu_count", return_value=16):
                self.assertIsNone(agentes.nucleos())
            with mock.patch.object(os, "cpu_count", return_value=4):
                saved = getattr(os, "sched_getaffinity", None)
                if saved is not None:
                    del os.sched_getaffinity
                try:
                    self.assertEqual(agentes.nucleos(), 4)
                finally:
                    if saved is not None:
                        os.sched_getaffinity = saved

    def test_variaveis_de_substituicao_ficam_no_erros_log(self):  # R1
        raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, raiz, True)
        git("init", "-q", cwd=raiz)
        (raiz / ".forge").mkdir()
        (raiz / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        proc = montar_proc(raiz, {"loadavg": "0.1 0.1 0.1", "mem_gb": 8})
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(raiz),
                   "tool_input": {"subagent_type": "x", "description": "d"}}
        r = rodar("agentes", entrada, raiz, proc, {"FORGE_NPROC": "8"})
        self.assertEqual(r.returncode, 0, r.stderr)
        logs = list(raiz.glob("**/erros.log"))
        self.assertEqual(len(logs), 1, "um erros.log")
        texto = logs[0].read_text(encoding="utf-8")
        self.assertIn("agentes Aviso: FORGE_NPROC=8", texto)
        self.assertIn("agentes Aviso: FORGE_PROC=", texto)

    def test_raiz_de_estado_no_clone_do_forge(self):
        """Anti-alucinação, fatia 3: a raiz do clone do Forge (cópia principal e worktree) é achada; o projeto vem antes
        do manifesto e pasta sem manifesto não é clone."""
        sys.path.insert(0, str(HOOKS))
        import _comum
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        clone, wt, projeto, alheio = tmp / "Forge", tmp / "wt" / "aa", tmp / "proj", tmp / "alheio"
        for pasta in (clone, projeto, alheio):
            (pasta / "docs").mkdir(parents=True)
            git("init", "-q", "-b", "develop", cwd=pasta)
            git("config", "user.email", "t@example.com", cwd=pasta)
            git("config", "user.name", "Teste", cwd=pasta)
        for pasta in (clone, projeto):
            (pasta / ".claude-plugin").mkdir()
            (pasta / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
        (projeto / ".forge").mkdir()
        (projeto / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("add", "-A", cwd=clone)
        git("commit", "-q", "-m", "base", cwd=clone)
        git("worktree", "add", "-q", "-b", "melhoria/x", str(wt), cwd=clone)
        self.assertEqual(_comum.raiz_de_estado(clone / "docs"), clone)
        self.assertEqual(_comum.raiz_de_estado(wt / "docs"), wt)
        self.assertEqual(_comum.raiz_de_estado(projeto / "docs"), projeto)
        self.assertIsNone(_comum.raiz_de_estado(alheio / "docs"))
        self.assertIsNone(_comum.raiz_de_estado(tmp))
        hook = _comum.Hook("parecer")
        hook.entrada = {"cwd": str(wt), "tool_input": {"command": "gh pr ready"}}
        self.assertIsNone(hook.projeto(wt))  # sem o pedido, o hook segue só nos projetos
        self.assertEqual(hook.projeto(wt, clone_do_forge=True), wt)
        self.assertEqual(hook.copia_principal().resolve(), clone.resolve())  # o estado vai para a cópia principal
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
            self.assertFalse(_comum.sessao_vigiada(hook))  # pasta corrente no clone, fora de ~/.forge-contrib
            self.assertTrue(_comum.sessao_vigiada(hook, clone_do_forge=True))
            hook.entrada["cwd"] = str(tmp)
            os.environ["CLAUDE_PROJECT_DIR"] = str(clone)  # sessão do dono em ~/Forge, pasta corrente fora dela
            self.assertTrue(_comum.sessao_vigiada(hook, clone_do_forge=True))
            erro = io.StringIO()
            with self.assertRaises(SystemExit) as saida, contextlib.redirect_stderr(erro):
                _comum.falhar_fechado(hook, re.compile(r"\bpr\b.*\bready\b"), "", clone_do_forge=True)
            self.assertEqual(saida.exception.code, 2)
            self.assertIn("erro interno do hook parecer", erro.getvalue())

    def test_suite_do_forge_e_pesada(self):
        # TA-2: no clone do Forge a suíte completa é pesada; em projeto, só o que a config lista.
        sys.path.insert(0, str(HOOKS))
        import _comum
        import pesado
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        clone, projeto = tmp / "Forge", tmp / "proj"
        for pasta in (clone, projeto):
            (pasta / ".claude-plugin").mkdir(parents=True)
            (pasta / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
            git("init", "-q", "-b", "develop", cwd=pasta)
        (projeto / ".forge").mkdir()
        (projeto / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        suite = "python3 -m unittest discover -s tests -q"
        hook = _comum.Hook("pesado")
        raiz = hook.projeto(clone, clone_do_forge=True)
        self.assertEqual(raiz, clone)
        self.assertTrue(pesado.pesado(suite, pesado.pesados_da_raiz(hook, raiz)))
        self.assertTrue(pesado.pesado("cd tests && PYTHONPATH=. python -m unittest discover", pesado.pesados_da_raiz(hook, raiz)))
        self.assertFalse(pesado.pesado("python3 -m unittest tests.test_forge", pesado.pesados_da_raiz(hook, raiz)))
        self.assertFalse(pesado.pesado("echo python3 -m unittest discover", pesado.pesados_da_raiz(hook, raiz)))
        hook = _comum.Hook("pesado")
        raiz = hook.projeto(projeto, clone_do_forge=True)
        self.assertEqual(raiz, projeto)
        self.assertFalse(pesado.pesado(suite, pesado.pesados_da_raiz(hook, raiz)))  # projeto: só o que a config lista

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

    def test_escrita_permitida_malformada_bloqueia(self):
        """ADR 0009, seção 6.6: `escrita_permitida` com forma errada (ou lista vazia) falha fechado, não libera."""
        base = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        for nome, valor in {"não objeto": ["docs/"], "papel sem lista": {"aq": "docs/propostas/"},
                            "lista vazia": {"aq": []}, "item não texto": {"aq": [7]}}.items():
            with self.subTest(nome):
                r = self.rodar_com_politica(dict(base, escrita_permitida=valor), "ls", "forge-dev:aq")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("política de conformidade inválida", r.stderr)

    def test_erro_interno_com_lista_de_permissao_falha_fechado(self):
        """ADR 0009, seções 6.6 e 7: erro interno na decisão do papel com `escrita_permitida` barra (o caminho não
        tem marcador crítico, e sem isso o hook liberaria). Outro papel segue a regra geral (libera)."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-hook-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        raiz = tmp / "proj"
        (raiz / ".forge").mkdir(parents=True)
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=raiz)
        ilegivel = raiz / "docs" / "propostas" / "ilegivel"  # `exists()` em pasta sem permissão levanta PermissionError
        (ilegivel / "sub").mkdir(parents=True)
        ilegivel.chmod(0)
        self.addCleanup(ilegivel.chmod, 0o755)
        if os.access(ilegivel / "sub", os.X_OK):
            self.skipTest("o processo ignora permissões de pasta (root)")
        env = ambiente_limpo()
        env.pop("FORGE_GUARDA_ABERTA", None)
        for papel, esperado in {"forge-dev:aq": 2, "forge:dev": 0}.items():
            with self.subTest(papel):
                entrada = {"tool_name": "Write", "tool_input": {"file_path": str(ilegivel / "sub" / "x.md")},
                           "agent_type": papel, "hook_event_name": "PreToolUse", "cwd": str(raiz)}
                r = subprocess.run([sys.executable, str(HOOKS / "conformidade.py")], input=json.dumps(entrada), cwd=raiz,
                                   env=env, capture_output=True, text=True, timeout=30)
                self.assertEqual(r.returncode, esperado, r.stderr)
                if esperado:
                    self.assertIn("erro interno do hook conformidade para o papel aq", r.stderr)

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
            "so_leitura em lista": dict(base, so_leitura=["conferente"]),
            "so_leitura sem comandos": dict(base, so_leitura={"papeis": ["conferente"], "saidas": []}),
            "so_leitura: saidas não lista": dict(base, so_leitura=dict(base["so_leitura"], saidas="/dev/null")),
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

    def test_vv2_politica_libera_so_entrega_e_delta_e_protege_pedidos(self):  # VV-2, A1 e B2
        politica = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        comandos = politica["so_leitura"]["comandos"]
        self.assertIn("forge-check entrega", comandos)
        self.assertIn("forge-check delta", comandos)
        self.assertEqual([c for c in comandos if c.startswith("forge-check")],
                         ["forge-check pr", "forge-check docs", "forge-check brief", "forge-check entrega", "forge-check delta"])
        protegidos = {e["caminho"]: e["quem"] for e in politica["caminhos"]}
        for caminho in ("docs/pedidos/", "~/.forge-contrib/docs/pedidos/", "docs/briefs/", "~/.forge-contrib/docs/briefs/"):
            self.assertEqual(protegidos[caminho], ["jarvis"], caminho)


if __name__ == "__main__":
    unittest.main()
