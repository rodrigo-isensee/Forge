"""Teste-oráculo do lote B do v047 (A9 e A10 do plano de segurança da E1.133, E1.170): destino opaco sem resto no hook
`conformidade` e a liberação de link do #512 que não se alarga com corpo de mais de um comando.

Escrito pelo security-engineer (EXT-1). O autor o roda e não o edita. Autocontido: biblioteca padrão, o hook sob teste
(`hooks/conformidade.py`, rodado como subprocesso) e os utilitários deste arquivo; nada de `tests/test_hooks.py`.

O esperado não vem da regra do hook. Para cada caso, o bash calcula num repositório temporário o caminho real que a linha
grava (`printf %s <destino>`, com o nome da origem quando o destino é pasta) ou de que o link parte; o caso espera 2 se o
caminho cai no `.git` (o próprio, inclusive o `.git` arquivo da worktree, ou dentro dele ou do diretório comum), senão 0.
Exceção declarada: os três casos da A10 (ii) do plano em que o corpo do rev-parse tem mais de um comando e a origem do
link é `HEAD` esperam 2 pelo plano (o valor que o hook leria não é o do bash), marcados `plano`.

Orçamento: até 150 execuções do hook; pelo menos 10 com o prazo de produção (3 s)."""
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HOOKS = RAIZ / "hooks"
TETO_DE_EXECUCOES = 150
PRAZO_LARGO_S = 120

ARQUIVOS = {"x": "x\n", "config": "c\n", "pre-push": "p\n", "lugar.txt": ".git\n", "docs/a.md": "a\n",
            "hooks/pre-push": "p\n", "src/app.js": "v1\n", "README.md": "projeto\n", ".gitignore": ".forge/run/\n",
            ".forge/config.json": "{}\n"}

LANCADOR = """
import runpy, sys
sys.path.insert(0, sys.argv[1])
import _comum
_comum.forge_check().GIT_TIMEOUT_S = 120
if sys.argv[3] != "producao":
    _comum.PRAZO_DA_DECISAO_S = float(sys.argv[3])
sys.argv = [sys.argv[2]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def ambiente():
    """Sem GIT_*, FORGE_* e a raiz da sessão herdados; git sem configuração global nem manutenção automática."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_COUNT="2",
               GIT_CONFIG_KEY_0="gc.auto", GIT_CONFIG_VALUE_0="0",
               GIT_CONFIG_KEY_1="maintenance.auto", GIT_CONFIG_VALUE_1="false", LC_ALL="C")
    for nome in ("GH_CONFIG_DIR", "XDG_CONFIG_HOME"):
        env.pop(nome, None)
    return env


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, env=ambiente(), check=True, capture_output=True, text=True,
                          timeout=60)


def montar(tmp, amb):
    """O repositório do caso; devolve (raiz da sessão, cwd do comando, agente, env extra)."""
    raiz = tmp / "proj"
    raiz.mkdir()
    git("init", "-q", "-b", "develop", cwd=raiz)
    git("config", "user.email", "t@example.com", cwd=raiz)
    git("config", "user.name", "Teste", cwd=raiz)
    arquivos = dict(ARQUIVOS)
    if amb == "clone":  # clone do Forge, papel com lista (aq): a `Guarda` age; a gramática só de leitura recusa `$`
        arquivos[".claude-plugin/plugin.json"] = '{"name": "forge"}\n'
    else:
        arquivos[".forge/versao"] = "0.5.0\n"
    for rel, conteudo in arquivos.items():
        (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
        (raiz / rel).write_text(conteudo, encoding="utf-8")
    git("add", "-A", cwd=raiz)
    git("commit", "-q", "-m", "base", cwd=raiz)
    extra = {"CLAUDE_PROJECT_DIR": str(raiz)}
    if amb == "projeto":
        git("switch", "-q", "-c", "melhoria/x", cwd=raiz)
        return raiz, raiz, "forge:tech-lead", extra
    if amb == "worktree":
        git("worktree", "add", "-q", "-b", "melhoria/w", str(tmp / "wt"), cwd=raiz)
        extra["CLAUDE_PROJECT_DIR"] = str(tmp / "wt")
        return raiz, tmp / "wt", "forge:tech-lead", extra
    (tmp / "home").mkdir()
    extra["HOME"] = str(tmp / "home")
    return raiz, raiz, "forge-dev:aq", extra


def bases_do_git(pasta):
    r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir"], cwd=pasta,
                       env=ambiente(), capture_output=True, text=True, timeout=30)
    return {Path(os.path.realpath(pasta / ".git"))} | {Path(os.path.realpath(p)) for p in r.stdout.split()}


def no_git(pasta, alvo):
    real = Path(os.path.realpath(alvo))
    return any(real == b or b in real.parents for b in bases_do_git(pasta))


def caminho_pelo_bash(pasta, prefixo, palavra, tmpdir):
    """O caminho que o bash dá à `palavra` depois do `prefixo`, rodado na pasta do caso (cópia descartável)."""
    env = ambiente()
    env.update(HOME=str(pasta), TMPDIR=str(tmpdir))
    r = subprocess.run(["bash", "--norc", "--noprofile", "-c", f"{prefixo}printf %s {palavra}"], cwd=pasta, env=env,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    if r.returncode or not r.stdout:
        return None
    return Path(pasta, r.stdout)


def esperado_pelo_bash(pasta, caso, tmpdir):
    alvo = caminho_pelo_bash(pasta, caso["prefixo"], caso["palavra"], tmpdir)
    if alvo is None:
        return None
    if caso["tipo"] == "link":  # a origem do link: só os nomes que a política protege dentro do `.git`
        if not no_git(pasta, alvo):
            return 0
        return 0 if alvo.name == "HEAD" else 2
    if caso.get("origem") and alvo.is_dir():
        alvo = alvo / caso["origem"]
    return 2 if no_git(pasta, alvo) else 0


def C(nome, linha, palavra, prefixo="", origem=None, amb="projeto", tipo="destino", plano=None, producao=False):
    return dict(nome=nome, linha=linha, palavra=palavra, prefixo=prefixo, origem=origem, amb=amb, tipo=tipo,
                plano=plano, producao=producao)


G = '"$(echo .git)"'
CASOS = [
    # Sondas do plano (S1 a S14) e controles
    C("S1", f"cp config {G}", G, origem="config", producao=True),
    C("S2", 'cp pre-push "$(echo .git/hooks)"', '"$(echo .git/hooks)"', origem="pre-push", producao=True),
    C("S3", 'cp x "$(printf %s .git/config)"', '"$(printf %s .git/config)"', origem="x", producao=True),
    C("S4", 'echo a > "$(echo .git/config)"', '"$(echo .git/config)"', producao=True),
    C("S5", 'f(){ echo .git; }; cp config "$(f)"', '"$(f)"', prefixo="f(){ echo .git; }; ", origem="config",
      producao=True),
    C("S6", 'cp x "${GITD:-.git}"', '"${GITD:-.git}"', origem="x", producao=True),
    C("S7-controle-resto", 'cp x "$(echo .git)/config"', '"$(echo .git)/config"', origem="x"),
    C("S8", 'cp config "$(git rev-parse --git-dir;)"', '"$(git rev-parse --git-dir;)"', origem="config",
      producao=True),
    C("S9", 'cp config "$(git rev-parse --git-dir&&:)"', '"$(git rev-parse --git-dir&&:)"', origem="config"),
    C("S10", 'cp config "$(git rev-parse --git-dir|cat)"', '"$(git rev-parse --git-dir|cat)"', origem="config"),
    C("S11", "cp config \"$(eval 'git rev-parse --git-dir')\"", "\"$(eval 'git rev-parse --git-dir')\"",
      origem="config"),
    C("S12", "cp config \"$(sh -c 'git rev-parse --git-dir')\"", "\"$(sh -c 'git rev-parse --git-dir')\"",
      origem="config"),
    C("S13", "cp config \"$(git rev-parse $'--git-dir')\"", "\"$(git rev-parse $'--git-dir')\"", origem="config"),
    C("S14", "cp config $(echo $(git rev-parse --git-dir))", "$(echo $(git rev-parse --git-dir))", origem="config"),
    C("controle-rev-parse", 'cp config "$(git rev-parse --git-dir)"', '"$(git rev-parse --git-dir)"',
      origem="config"),
    C("controle-literal", "cp x .git/config", ".git/config", origem="x"),
    # Casos de abuso do plano (seção 2)
    C("curinga-interrogacao", 'cp x "$(echo .gi?)"', '"$(echo .gi?)"', origem="x"),
    C("crase", "cp config `echo .git`", "`echo .git`", origem="config"),
    C("tee", 'echo a | tee "$(echo .git/config)"', '"$(echo .git/config)"', producao=True),
    C("dd", 'dd of="$(echo .git/config)" if=x', '"$(echo .git/config)"', producao=True),
    C("cp-r-hooks", f"cp -r hooks {G}", G, origem="hooks"),
    C("ln-s-hook", 'ln -s x "$(echo .git/hooks/pre-push)"', '"$(echo .git/hooks/pre-push)"', origem="x"),
    C("variavel-da-linha", 'd=$(echo .git); cp config "$d"', '"$d"', prefixo="d=$(echo .git); ", origem="config"),
    C("u3-cat", 'cp config "$(cat lugar.txt)"', '"$(cat lugar.txt)"', origem="config"),
    C("subshell", f"(cp config {G})", G, origem="config"),
    C("heredoc", f"bash <<'EOF'\ncp config {G}\nEOF", G, origem="config"),
    C("worktree-S1", f"cp config {G}", G, origem="config", amb="worktree"),
    # D1: mecanismos e formas do destino
    C("so-barra", f"cp config {G}/", G, origem="config"),
    C("t-palavra", f"cp -t {G} config", G, origem="config"),
    C("target-directory", f"cp --target-directory={G} config", G, origem="config"),
    C("install-D", 'install -D x "$(echo .git/hooks/pre-push)"', '"$(echo .git/hooks/pre-push)"'),
    C("mv", f"mv config {G}", G, origem="config"),
    C("ln-fisico", f"ln config {G}", G, origem="config"),
    C("anexa", 'echo a >> "$(echo .git/config)"', '"$(echo .git/config)"'),
    C("clobber", 'echo a >| "$(echo .git/config)"', '"$(echo .git/config)"'),
    C("e-maior", 'echo a &> "$(echo .git/config)"', '"$(echo .git/config)"'),
    C("fd2", 'echo a 2> "$(echo .git/config)"', '"$(echo .git/config)"'),
    C("tee-a", 'tee -a "$(echo .git/config)" < x', '"$(echo .git/config)"'),
    C("ln-s-pasta", f"ln -s ../pre-push {G}/hooks", '"$(echo .git)"/hooks', origem="pre-push"),
    # D2: formas do valor
    C("padrao-igual-dois-pontos", 'cp x "${GITD:=.git}"', '"${GITD:=.git}"', origem="x"),
    C("padrao-hifen", 'cp x "${GITD-.git}"', '"${GITD-.git}"', origem="x"),
    C("padrao-igual", 'cp x "${GITD=.git}"', '"${GITD=.git}"', origem="x"),
    C("padrao-com-substituicao", 'cp x "${GITD:-$(echo .git)}"', '"${GITD:-$(echo .git)}"', origem="x"),
    C("funcao-palavra-function", 'function f { echo .git; }; cp config "$(f)"', '"$(f)"',
      prefixo="function f { echo .git; }; ", origem="config"),
    C("funcao-subshell", 'f() ( echo .git ); cp config "$(f)"', '"$(f)"', prefixo="f() ( echo .git ); ",
      origem="config"),
    C("ponto-barra", 'cp config "$(echo ./.git)"', '"$(echo ./.git)"', origem="config"),
    C("absoluto-pwd", 'cp config "$(echo "$PWD"/.git)"', '"$(echo "$PWD"/.git)"', origem="config"),
    C("cd-pwd", 'cp config "$(cd .git && pwd)"', '"$(cd .git && pwd)"', origem="config"),
    C("absolute-git-dir", 'cp config "$(git rev-parse --absolute-git-dir)"',
      '"$(git rev-parse --absolute-git-dir)"', origem="config"),
    C("git-common-dir", 'cp config "$(git rev-parse --git-common-dir)"', '"$(git rev-parse --git-common-dir)"',
      origem="config"),
    C("git-path-hooks", 'cp pre-push "$(git rev-parse --git-path hooks)"', '"$(git rev-parse --git-path hooks)"',
      origem="pre-push"),
    C("colchete", 'cp config "$(ls -d .[g]it)"', '"$(ls -d .[g]it)"', origem="config"),
    C("colchete-final", 'cp config "$(echo .gi[t])"', '"$(echo .gi[t])"', origem="config"),
    C("aspas-vazias-na-palavra", 'cp config "$(echo .g""it)"', '"$(echo .g""it)"', origem="config"),
    C("aspas-simples-na-palavra", "cp config \"$(echo .g'i't)\"", "\"$(echo .g'i't)\"", origem="config"),
    C("variavel-concatenada", 'a=.g; cp config "$(echo ${a}it)"', '"$(echo ${a}it)"', prefixo="a=.g; ",
      origem="config"),
    C("variavel-vazia-no-meio", 'cp config "$(echo .gi${z}t)"', '"$(echo .gi${z}t)"', origem="config"),
    C("u3-redirecao-de-leitura", 'cp config "$(<lugar.txt)"', '"$(<lugar.txt)"', origem="config"),
    C("u3-head", 'cp config "$(head -n1 lugar.txt)"', '"$(head -n1 lugar.txt)"', origem="config"),
    C("mktemp-dentro-do-git", 'cp config "$(mktemp -d -p .git)"', '"$(mktemp -d -p .git)"', origem="config"),
    C("dirname", 'cp config "$(dirname .git/x)"', '"$(dirname .git/x)"', origem="config"),
    C("variavel-e-logico", 'd=$(echo .git) && cp config "$d"', '"$d"', prefixo="d=$(echo .git) && ",
      origem="config"),
    C("variavel-export", 'export d=$(echo .git); cp config "$d"', '"$d"', prefixo="export d=$(echo .git); ",
      origem="config"),
    C("pipe-no-corpo", 'cp config "$(echo .git | cat)"', '"$(echo .git | cat)"', origem="config"),
    C("sem-aspas", "cp config $(echo .git)", "$(echo .git)", origem="config"),
    # D6: posição na linha física e lógica
    C("depois-de-ponto-e-virgula", f"true; cp config {G}", G, origem="config"),
    C("depois-de-e-logico", f"true && cp config {G}", G, origem="config"),
    C("depois-de-ou-logico", f"false || cp config {G}", G, origem="config"),
    C("depois-de-pipe", f"echo | cp config {G}", G, origem="config"),
    C("continuacao", f"cp config \\\n{G}", G, origem="config"),
    C("grupo-chaves", f"{{ cp config {G}; }}", G, origem="config"),
    C("if-then", f"if true; then cp config {G}; fi", G, origem="config"),
    C("for-do", f"for i in 1; do cp config {G}; done", G, origem="config"),
    C("heredoc-redirecao", "bash <<'EOF'\necho a > \"$(echo .git/config)\"\nEOF", '"$(echo .git/config)"'),
    # D7: ambiente
    C("worktree-git-arquivo", f"echo a > {G}", G, amb="worktree"),
    C("worktree-rev-parse", 'cp config "$(git rev-parse --git-dir)"', '"$(git rev-parse --git-dir)"',
      origem="config", amb="worktree"),
    C("worktree-git-path", 'cp pre-push "$(git rev-parse --git-path hooks)"', '"$(git rev-parse --git-path hooks)"',
      origem="pre-push", amb="worktree"),
    C("worktree-funcao", 'f(){ echo .git/config; }; echo a > "$(f)"', '"$(f)"',
      prefixo="f(){ echo .git/config; }; ", amb="worktree"),
    C("clone-S1", f"cp config {G}", G, origem="config", amb="clone"),
    C("clone-hooks", 'cp pre-push "$(echo .git/hooks)"', '"$(echo .git/hooks)"', origem="pre-push", amb="clone"),
    C("clone-redirecao", 'echo a > "$(echo .git/config)"', '"$(echo .git/config)"', amb="clone"),
    C("clone-padrao", 'cp x "${GITD:-.git}"', '"${GITD:-.git}"', origem="x", amb="clone"),
    # Dimensão nova (E1.170), D2: remoção de aspas e concatenação dentro da palavra do corpo. O bash junta `.g'i't`,
    # `${a}it` (com `a=.g` na linha) e `.gi${z}t` (`z` vazia) em `.git`; é a classe da barra invertida do U2.
    C("d2b-aspas-simples-redirecao", "echo a > \"$(echo .g'i't/config)\"", "\"$(echo .g'i't/config)\""),
    C("d2b-aspas-duplas-redirecao", 'echo a > "$(echo .g""it/config)"', '"$(echo .g""it/config)"'),
    C("d2b-aspas-no-fim-redirecao", 'echo a > "$(echo .gi"t"/config)"', '"$(echo .gi"t"/config)"'),
    C("d2b-variavel-concatenada-redirecao", 'a=.g; echo a > "$(echo ${a}it/config)"', '"$(echo ${a}it/config)"',
      prefixo="a=.g; "),
    C("d2b-duas-variaveis-redirecao", 'a=.g b=it; echo a > "$(echo $a$b/config)"', '"$(echo $a$b/config)"',
      prefixo="a=.g b=it; "),
    C("d2b-variavel-vazia-redirecao", 'echo a > "$(echo .gi${z}t/config)"', '"$(echo .gi${z}t/config)"'),
    C("d2b-substituicao-vazia-redirecao", 'echo a > "$(echo .gi$(:)t/config)"', '"$(echo .gi$(:)t/config)"'),
    C("d2b-variavel-inteira-redirecao", 'a=.git; echo a > "$(echo $a/config)"', '"$(echo $a/config)"',
      prefixo="a=.git; "),
    C("d2b-aspas-simples-tee-hook", "echo a | tee \"$(echo .g'i't/hooks/pre-push)\"",
      "\"$(echo .g'i't/hooks/pre-push)\""),
    C("d2b-aspas-simples-cp-neutro", "cp x \"$(echo .g'i't)\"", "\"$(echo .g'i't)\"", origem="x"),
    C("d2b-aspas-simples-cp-hook", "cp pre-push \"$(echo .g'i't/hooks)\"", "\"$(echo .g'i't/hooks)\"",
      origem="pre-push"),
    C("d2b-variavel-concatenada-cp-neutro", 'a=.g; cp x "$(echo ${a}it)"', '"$(echo ${a}it)"', prefixo="a=.g; ",
      origem="x"),
    C("d2b-funcao-com-aspas-cp-neutro", "f(){ echo .g'i't; }; cp x \"$(f)\"", '"$(f)"',
      prefixo="f(){ echo .g'i't; }; ", origem="x"),
    C("funcao-palavra-function-cp-neutro", 'function f { echo .git; }; cp x "$(f)"', '"$(f)"',
      prefixo="function f { echo .git; }; ", origem="x"),
    C("funcao-palavra-function-redirecao", 'function f { echo .git/config; }; echo a > "$(f)"', '"$(f)"',
      prefixo="function f { echo .git/config; }; "),
    # A10: origem de link vinda de rev-parse com mais de um comando
    C("a10-ln-ponto-e-virgula-echo-head", 'ln "$(git rev-parse --git-dir; echo x)"/HEAD h',
      '"$(git rev-parse --git-dir; echo x)"/HEAD', tipo="link", plano=2),
    C("a10-ln-e-logico-config", 'ln "$(git rev-parse --git-dir && echo x)"/config h',
      '"$(git rev-parse --git-dir && echo x)"/config', tipo="link", plano=2),
    C("a10-ln-crase-head", "ln `git rev-parse --git-dir;`/HEAD h", "`git rev-parse --git-dir;`/HEAD", tipo="link",
      plano=2),
    C("a10-ln-true-antes-config", 'ln "$(true; git rev-parse --git-dir)"/config h',
      '"$(true; git rev-parse --git-dir)"/config', tipo="link"),
    C("a10-ln-dois-comandos-hooks", 'ln "$(git rev-parse --git-dir >/dev/null; echo .git/hooks)"/pre-push h',
      '"$(git rev-parse --git-dir >/dev/null; echo .git/hooks)"/pre-push', tipo="link"),
    C("a10-ln-s-pipe-config", 'ln -s "$(git rev-parse --git-dir|cat)"/config h',
      '"$(git rev-parse --git-dir|cat)"/config', tipo="link"),
    C("a10-cp-s-colado-config", 'cp -s "$(git rev-parse --git-dir;)"/config h',
      '"$(git rev-parse --git-dir;)"/config', tipo="link"),
    C("a10-ln-true-antes-head-plano", 'ln -s "$(true; git rev-parse --git-dir)"/HEAD h',
      '"$(true; git rev-parse --git-dir)"/HEAD', tipo="link", plano=2),
    # Corpus de legítimos (rc 0 pelo bash)
    C("leg-literal", "cp x docs/a.md", "docs/a.md", origem="x", producao=True),
    C("leg-mv", "mv x y", "y", origem="x"),
    C("leg-date", 'cp x "$(date +%F).log"', '"$(date +%F).log"', origem="x", producao=True),
    C("leg-mktemp", 'cp x "$(mktemp)"', '"$(mktemp)"', origem="x"),
    C("leg-tee-mktemp", 'echo a | tee "$(mktemp)"', '"$(mktemp)"'),
    C("leg-variavel-mktemp", 'out=$(mktemp -d); cp x "$out"/', '"$out"/', prefixo="out=$(mktemp -d); ",
      origem="x"),
    C("leg-padrao-docs", 'cp x "${OUT:-docs}"/', '"${OUT:-docs}"/', origem="x"),
    C("leg-u3-mktemp", 'cp config "$(mktemp -d)"', '"$(mktemp -d)"', origem="config"),
    C("leg-toplevel", 'cp x "$(git rev-parse --show-toplevel)"', '"$(git rev-parse --show-toplevel)"', origem="x"),
    C("leg-short-head-sufixo", 'echo a > "$(git rev-parse --short HEAD).txt"',
      '"$(git rev-parse --short HEAD).txt"'),
    C("leg-short-head", 'echo a > "$(git rev-parse --short HEAD)"', '"$(git rev-parse --short HEAD)"'),
    C("leg-echo-docs", 'cp x "$(echo docs)"', '"$(echo docs)"', origem="x"),
    C("leg-github", 'cp x "$(echo .github)"', '"$(echo .github)"', origem="x"),
    C("leg-x-ponto-git", 'cp x "$(echo x.git)"', '"$(echo x.git)"', origem="x"),
    C("leg-gitignore", 'echo a >> "$(echo .gitignore)"', '"$(echo .gitignore)"'),
    C("leg-redirecao-docs", 'echo a > "$(echo docs/a.md)"', '"$(echo docs/a.md)"'),
    C("leg-funcao-docs", 'f(){ echo docs; }; cp x "$(f)"', '"$(f)"', prefixo="f(){ echo docs; }; ", origem="x"),
    C("leg-u3-pwd", 'cp config "$(pwd)"/', '"$(pwd)"/', origem="config"),
    C("leg-link-512", 'ln -s "$(git rev-parse --git-dir)"/HEAD h', '"$(git rev-parse --git-dir)"/HEAD', tipo="link",
      producao=True),
    C("leg-link-512-crase", "ln -s `git rev-parse --git-dir`/HEAD h", "`git rev-parse --git-dir`/HEAD",
      tipo="link"),
    C("leg-worktree-docs", 'cp x "$(echo docs)"', '"$(echo docs)"', origem="x", amb="worktree"),
]
# Leituras legítimas: o bash não grava nada; o esperado é 0 por construção (sem destino de escrita).
LEITURAS = ['git log -1 "$(git rev-parse --abbrev-ref HEAD)"', 'cat "$(git rev-parse --git-dir;)/HEAD"',
            "cat .git/HEAD", 'cat "$(echo .git)/config"']


def rodar_hook(linha, tmp, amb, producao):
    raiz, cwd, agente, extra = montar(tmp, amb)
    entrada = {"tool_name": "Bash", "tool_input": {"command": linha}, "agent_type": agente,
               "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9", "cwd": str(cwd)}
    env = ambiente()
    env.pop("FORGE_GUARDA_ABERTA", None)
    env.update(extra)
    comando = [sys.executable, "-I", "-c", LANCADOR, str(HOOKS), str(HOOKS / "conformidade.py"),
               "producao" if producao else str(PRAZO_LARGO_S)]
    r = subprocess.run(comando, input=json.dumps(entrada), cwd=raiz, env=env, capture_output=True, text=True,
                       timeout=PRAZO_LARGO_S)
    return cwd, r


def executar(caso):
    tmp = Path(tempfile.mkdtemp(prefix="forge-oraculo-v047-"))
    try:
        for sub in ("a", "b", "t"):
            (tmp / sub).mkdir()
        _, r = rodar_hook(caso["linha"], tmp / "a", caso["amb"], caso["producao"])
        pasta, _, _, _ = montar(tmp / "b", caso["amb"])
        if caso["amb"] == "worktree":
            pasta = tmp / "b" / "wt"
        esperado = esperado_pelo_bash(pasta, caso, tmp / "t")
        return esperado, r.returncode, r.stderr.strip()[:300]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def executar_leitura(linha):
    tmp = Path(tempfile.mkdtemp(prefix="forge-oraculo-v047-"))
    try:
        _, r = rodar_hook(linha, tmp, "projeto", False)
        return r.returncode, r.stderr.strip()[:300]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def em_paralelo(funcao, itens):
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        return list(pool.map(funcao, itens))


class OraculoV047DestinoOpaco(unittest.TestCase):
    def test_orcamento_e_cobertura(self):
        self.assertLessEqual(len(CASOS) + len(LEITURAS), TETO_DE_EXECUCOES)
        self.assertGreaterEqual(sum(c["producao"] for c in CASOS), 10)
        for amb in ("projeto", "worktree", "clone"):
            self.assertGreaterEqual(sum(c["amb"] == amb for c in CASOS), 3, amb)
        self.assertEqual(len({c["nome"] for c in CASOS}), len(CASOS))

    def test_hook_concorda_com_o_bash(self):
        resultados = em_paralelo(executar, CASOS)
        recusas = 0
        for caso, (pelo_bash, obtido, erro) in zip(CASOS, resultados):
            with self.subTest(caso=caso["nome"]):
                self.assertIsNotNone(pelo_bash, f"o bash não calculou o caminho de {caso['linha']!r}")
                esperado = caso["plano"] if caso["plano"] is not None else pelo_bash
                if caso["plano"] is None and caso["nome"].startswith("leg-"):
                    self.assertEqual(pelo_bash, 0, "legítimo que o bash põe no .git: caso mal escrito")
                recusas += esperado == 2
                self.assertNotIn("Traceback", erro)
                self.assertEqual(obtido, esperado, f"{caso['linha']!r}: {erro}")
        self.assertGreaterEqual(recusas, 80, "casos com o caminho real no .git")

    def test_leituras_legitimas_liberam(self):
        for linha, (obtido, erro) in zip(LEITURAS, em_paralelo(executar_leitura, LEITURAS)):
            with self.subTest(linha=linha):
                self.assertEqual(obtido, 0, f"{linha!r}: {erro}")


if __name__ == "__main__":
    unittest.main()
