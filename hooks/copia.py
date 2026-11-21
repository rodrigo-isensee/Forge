#!/usr/bin/env python3
"""Forge: o agente do time grava e roda git de escrita só na própria cópia (R-CONFORMIDADE).

HOOK-AGENTE-FORA-DA-PROPRIA-COPIA, pedido v0478 E88.1 e E88.6. PreToolUse em Bash, Write, Edit, MultiEdit e NotebookEdit,
só com `agent_id` (a sessão principal, o Jarvis, segue livre). Alvos: o caminho do Write/Edit, o destino das redireções e
a pasta do `git` de escrita. Por alvo: numa cópia (worktree do projeto, clone de `~/.forge-contrib/wt/` ou de `.forge/wt/`),
libera só se o HEAD dela está numa branch de escrita da reserva do agente (`agentes.json`); na raiz da sessão, que nunca é
cópia própria, recusa; na pasta de controle, nas temporárias e em `/dev`, libera; fora disso, recusa. Sem reserva no
registro, libera e anota no erros.log. Limites em docs/hooks.md.
"""
import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path

from _comum import Aviso, bloquear, executar

CAMPO_DO_CAMINHO = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}
GIT_DE_ESCRITA = frozenset("add am apply branch checkout checkout-index cherry-pick clean clone commit init merge mv pull push "
                           "read-tree rebase reset restore revert rm stash switch symbolic-ref tag update-index update-ref "
                           "worktree".split())
OPCAO_DE_LEITURA = {"tag": {"-l", "--list", "--contains", "--no-contains", "--points-at", "--merged", "--no-merged", "-v"},
                    "branch": {"-l", "--list", "--contains", "--no-contains", "--points-at", "--merged", "--no-merged"},
                    "apply": {"--check", "--stat", "--numstat", "--summary"}, "stash": {"list", "show"},
                    "worktree": {"list"}}
SOLTOS_DE_LEITURA = {"tag": 0, "branch": 0, "symbolic-ref": 1}  # quantos argumentos sem opção ainda são leitura
OPCAO_DE_ESCRITA = frozenset("-d -D --delete -m -M --move -c -C --copy -f --force -u --set-upstream-to --apply".split())
VALOR_DO_GIT = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace"})  # opções do git com valor separado
PREFIXOS = frozenset("command env exec nice nohup time timeout".split())
PONTUACAO = frozenset("();&|<>")


def sem_corpo(texto):
    """O texto sem o corpo dos heredocs (`<<FIM` e `<<-FIM`, não `<<<`): da linha seguinte até a que é só o delimitador;
    o heredoc sem fim deixa o texto inteiro."""
    linhas, saida, i = texto.split("\n"), [], 0
    while i < len(linhas):
        saida.append(linhas[i])
        for traco, fim in re.findall(r"(?<!<)<<(?!<)(-?)\s*['\"]?(\w+)", linhas[i]):
            achado = next((j for j in range(i + 1, len(linhas)) if (linhas[j].lstrip("\t") if traco else linhas[j]) == fim), None)
            if achado is None:
                return texto
            i = achado
        i += 1
    return "\n".join(saida)


def palavras(texto):
    """Os tokens da linha (`shlex` com pontuação), sem o corpo dos heredocs e com a barra antes da quebra desfeita; a
    aspa sem par corta a leitura ali, e o que veio antes dela segue lido."""
    lex = shlex.shlex(sem_corpo(texto).replace("\\\n", "").replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    saida = []
    try:
        for token in lex:
            saida.append(token)
    except ValueError:
        pass
    return saida


def resolver(palavra, pasta):
    """Caminho real de `palavra` a partir de `pasta`; None se a pasta é incerta ou sobra variável ou substituição."""
    p = os.path.expanduser(os.path.expandvars(palavra))
    if pasta is None or "$" in p or "`" in p:
        return None
    return os.path.realpath(os.path.join(pasta, p))


def leitura(sub, args):
    """A forma que só lê de um subcomando de escrita (`git tag -l`, `git stash list`, `git apply --check`)."""
    if OPCAO_DE_ESCRITA.intersection(args):
        return False
    soltos = [a for a in args if not a.startswith("-")]
    return bool(OPCAO_DE_LEITURA.get(sub, set()).intersection(args)) or len(soltos) <= SOLTOS_DE_LEITURA.get(sub, -1)


def alvos_do_git(antes, args, pasta):
    """As pastas do `git` de escrita (`-C`, `--git-dir`, `--work-tree`, `GIT_DIR=`, `GIT_WORK_TREE=`, o destino do
    `clone` e do `init`, o subcomando de `-c alias.`), ou [] se ele só lê."""
    extras = [resolver(t.partition("=")[2], pasta) for t in antes if t.partition("=")[0] in ("GIT_DIR", "GIT_WORK_TREE")]
    apelidos, i = {}, 0
    while i < len(args) and args[i].startswith("-"):
        opcao, igual, valor = args[i].partition("=")
        if not igual and opcao in VALOR_DO_GIT:
            valor, i = (args[i + 1:] + [""])[0], i + 1
        if opcao == "-C":
            pasta = resolver(valor, pasta)
        elif opcao in ("--git-dir", "--work-tree"):
            extras.append(resolver(valor, pasta))
        elif opcao == "-c" and valor.startswith("alias."):
            nome, _, texto = valor[6:].partition("=")
            apelidos[nome] = (texto.split() + [""])[0]
        i += 1
    sub = (args[i:] + [""])[0]
    sub, resto = apelidos.get(sub, sub), args[i + 1:]
    if not (sub in GIT_DE_ESCRITA or sub.startswith("!")) or leitura(sub, resto):
        return []
    if sub in ("clone", "init") and resto and not resto[-1].startswith("-"):
        return [resolver(resto[-1], pasta)]
    return extras or [pasta]


def alvos_do_segmento(segmento, pasta):
    """(alvos, pasta depois) de um comando simples: destinos de redireção, as pastas do `git` de escrita e o `cd`."""
    alvos, comando, i = [], [], 0
    while i < len(segmento):
        token, seguinte = segmento[i], (segmento[i + 1:] + [""])[0]
        if set(token) <= PONTUACAO:  # redireção: o destino de `>`, `>>`, `&>` vira alvo; o de `>&1` e `>&-` não
            if ">" in token and not re.fullmatch(r"\d*|-", seguinte):
                alvos.append(resolver(seguinte, pasta))
            i += 2
            continue
        if not (token.isdigit() and seguinte and set(seguinte) <= PONTUACAO):  # o descritor de `2>` não é argumento
            comando.append(token)
        i += 1
    inicio = next((k for k, t in enumerate(comando) if not re.match(r"[A-Za-z_]\w*=", t)), len(comando))
    nome = os.path.basename((comando + [""])[inicio])
    if nome in PREFIXOS:  # `env`, `timeout 60`, `command`: vale o git que vem depois
        inicio = next((k for k in range(inicio, len(comando)) if os.path.basename(comando[k]) == "git"), inicio)
        nome = os.path.basename(comando[inicio])
    if nome == "cd":
        destino = (comando[inicio + 1:] + ["~"])[0]
        return alvos, None if destino == "-" else resolver(destino, pasta)
    if nome == "git":
        alvos += alvos_do_git(comando[:inicio], comando[inicio + 1:], pasta)
    return alvos, pasta


def alvos_do_bash(comando, cwd):
    """Os alvos de escrita da linha, comando a comando, seguindo o `cd`; o alvo incerto (variável) fica de fora."""
    alvos, pasta, segmento = [], str(cwd), []
    for token in palavras(comando) + [";"]:
        if token and set(token) <= set("();&|"):
            novos, pasta = alvos_do_segmento(segmento, pasta)
            alvos, segmento = alvos + novos, []
        else:
            segmento.append(token)
    return list(filter(None, alvos))


def alvos(hook):
    bash, cwd, entrada = hook.campo("tool_name") == "Bash", hook.cwd(), hook.campo("tool_input")
    chave = "command" if bash else CAMPO_DO_CAMINHO.get(hook.campo("tool_name"), "")
    valor = entrada.get(chave) if isinstance(entrada, dict) else None
    if not isinstance(valor, str) or not valor:
        return []
    return alvos_do_bash(valor, cwd) if bash else [os.path.realpath(cwd / valor)]


def dentro(caminho, pasta):
    return caminho == pasta or caminho.startswith(pasta.rstrip(os.sep) + os.sep)


def head_de(pasta):
    """`refs/heads/<b>` do HEAD do clone ou da worktree em `pasta` (só disco), ou None."""
    marca = pasta / ".git"
    try:
        if marca.is_file():
            marca = Path(marca.read_text(encoding="utf-8").partition("gitdir:")[2].strip())
        texto = (marca / "HEAD").read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return None
    return texto[5:] if texto.startswith("ref: refs/heads/") else None


def worktrees(raiz):
    """{pasta real: ref ou None} das worktrees do projeto, sem a raiz (que nunca vale como cópia própria)."""
    saida, pasta = {}, None
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    feito = subprocess.run(["git", "-C", str(raiz), "worktree", "list", "--porcelain"], capture_output=True, text=True,
                           env=ambiente, timeout=5, check=False)
    for linha in feito.stdout.splitlines():
        if linha.startswith("worktree "):
            pasta = os.path.realpath(linha[9:])
            saida[pasta] = None
        elif linha.startswith("branch refs/heads/"):
            saida[pasta] = linha[7:]
    saida.pop(os.path.realpath(raiz), None)
    return saida


def copia_do_alvo(alvo, raiz, trabalho):
    """(pasta, ref) da cópia que contém o alvo: a worktree, ou o clone de `~/.forge-contrib/wt/` ou de `.forge/wt/`,
    do qual só esse HEAD é lido (sem varrer `wt/`); fora de cópia, None."""
    for pasta in sorted(trabalho, key=len, reverse=True):
        if dentro(alvo, pasta):
            return pasta, trabalho[pasta]
    for base in (os.path.realpath(Path.home() / ".forge-contrib" / "wt"), os.path.realpath(Path(raiz) / ".forge" / "wt")):
        if dentro(alvo, base) and alvo != base:
            pasta = os.path.join(base, os.path.relpath(alvo, base).split(os.sep)[0])
            return pasta, head_de(Path(pasta))
    return None


def branches_do_agente(raiz, aid):
    """As refs das branches de escrita da reserva do agente `aid` no registro do R-TETO."""
    import agentes  # só aqui, com alvo de escrita: o custo do import fica fora das outras chamadas
    arquivo = agentes.arquivo_de_estado(raiz)
    estado = agentes.ler_estado(arquivo)  # sem diretório comum (None), o erro vai ao erros.log e libera
    return {f"refs/heads/{b}" for a in estado.get("agentes", []) if isinstance(a, dict) and a.get("id") == aid
            for b in agentes.escritas_do_registro(a)}


def livre(caminho):
    """Pasta de controle (`~/.forge-contrib` fora de `wt/`), temporárias e `/dev`."""
    controle = os.path.realpath(Path.home() / ".forge-contrib")
    if dentro(caminho, controle) and not dentro(caminho, os.path.join(controle, "wt")):
        return True
    return any(dentro(caminho, os.path.realpath(t)) for t in (tempfile.gettempdir(), "/tmp", "/var/tmp", "/dev"))


def principal(hook):
    aid = hook.campo("agent_id")
    lista = alvos(hook) if hook.campo("hook_event_name") == "PreToolUse" and isinstance(aid, str) and aid else []
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True) if lista else None
    if raiz is None:
        return
    refs = branches_do_agente(raiz, aid)
    if not refs:
        hook.registrar_erro(Aviso(f"copia: agente {aid} sem cópia no registro; a escrita fora dela não foi conferida"))
        return
    trabalho, sua = worktrees(raiz), ", ".join(sorted(refs))
    for alvo in lista:
        achada = copia_do_alvo(alvo, raiz, trabalho)
        if achada is not None and achada[1] not in refs:
            bloquear("R-CONFORMIDADE", f"{alvo} fica na cópia {achada[0]}, cujo HEAD não está na sua reserva "
                                       f"({sua}): grave e rode git de escrita só na cópia da sua branch")
        if achada is None and (dentro(alvo, os.path.realpath(raiz)) or not livre(alvo)):
            bloquear("R-CONFORMIDADE", f"{alvo} fica fora da sua cópia (a worktree ou o clone com HEAD em {sua}): grave "
                                       "e rode git de escrita só nela")


if __name__ == "__main__":
    executar("copia", principal)
