#!/usr/bin/env python3
"""Forge: o agente do time grava e roda git de escrita só na própria cópia de trabalho (R-CONFORMIDADE,
HOOK-AGENTE-FORA-DA-PROPRIA-COPIA).

PreToolUse em Bash, Write, Edit, MultiEdit e NotebookEdit, só com `agent_id` (a sessão principal, o Jarvis, segue livre).
A cópia do agente é a worktree do projeto, ou o clone em `~/.forge-contrib/wt/`, cujo HEAD está numa branch de escrita da
reserva dele no registro do R-TETO (`agentes.json`, lido pelo `agentes`). Ordem da decisão, por alvo: dentro da cópia,
libera; noutra cópia do projeto (a raiz da sessão, outra worktree ou outro clone com branch), recusa; na pasta de controle
(`~/.forge-contrib` fora de `wt/`), nas temporárias e em `/dev`, libera; fora disso, recusa. Alvos lidos: o caminho do
Write/Edit, o destino de `>` e `>>` e a pasta do `git` de escrita (com `cd` e `-C`). Sem a cópia no registro, libera e
anota no erros.log (falta de dado não trava o time). Limites em docs/hooks.md.
"""
import os
import shlex
import subprocess
import tempfile
from pathlib import Path

from _comum import Aviso, bloquear, executar

CAMPO_DO_CAMINHO = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}
GIT_DE_ESCRITA = frozenset("add am apply checkout cherry-pick clean commit merge mv pull push rebase reset restore revert rm "
                           "stash switch tag".split())
SEPARADORES = frozenset({";", "&&", "||", "|", "|&", "&", "(", ")", ";;"})
REDIRECOES = frozenset({">", ">>", ">|"})
VALOR_DO_GIT = frozenset({"-C", "-c"})  # opções do git antes do subcomando que levam a palavra seguinte


def palavras(texto):
    """Os tokens da linha (`shlex` com pontuação), até o primeiro `<<` (o corpo do heredoc não é comando); a aspa sem par
    corta a leitura ali, e o que veio antes dela segue lido."""
    lex = shlex.shlex(texto.split("<<", 1)[0].replace("\n", " ; "), posix=True, punctuation_chars=True)
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


def alvos_do_segmento(segmento, pasta):
    """(alvos, pasta depois) de um comando simples: destinos de redireção, a pasta do `git` de escrita e o `cd`."""
    alvos = [resolver(segmento[i + 1], pasta) for i in range(len(segmento) - 1) if segmento[i] in REDIRECOES]
    nome = (segmento + [""])[0]
    if nome == "cd":
        return alvos, resolver((segmento[1:] + ["~"])[0], pasta)
    if nome == "git":
        pasta_git, sub = pasta, ""
        for anterior, token in zip(segmento, segmento[1:]):
            if anterior == "-C" and not sub:  # depois do subcomando, `-C` é dele (`git commit -C <commit>`)
                pasta_git = resolver(token, pasta_git)
            elif not (sub or token.startswith("-") or anterior in VALOR_DO_GIT):
                sub = token
        alvos.append(pasta_git if sub in GIT_DE_ESCRITA else None)
    return alvos, pasta


def alvos_do_bash(comando, cwd):
    """Os alvos de escrita da linha, comando a comando, seguindo o `cd`; o alvo incerto (variável) fica de fora."""
    alvos, pasta, segmento = [], str(cwd), []
    for token in palavras(comando) + [";"]:
        if token in SEPARADORES:
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


def copias(raiz):
    """{pasta real: ref} das cópias com branch: as worktrees do projeto e os clones de `~/.forge-contrib/wt/`."""
    saida, pasta = {}, None
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    feito = subprocess.run(["git", "-C", str(raiz), "worktree", "list", "--porcelain"], capture_output=True, text=True,
                           env=ambiente, timeout=5, check=False)
    for linha in feito.stdout.splitlines():
        if linha.startswith("worktree "):
            pasta = os.path.realpath(linha[9:])
        elif linha.startswith("branch refs/heads/"):
            saida[pasta] = linha[7:]
    wt = Path.home() / ".forge-contrib" / "wt"
    for filho in sorted(wt.iterdir()) if wt.is_dir() else []:
        saida.setdefault(os.path.realpath(filho), head_de(filho))
    return saida


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
    todas, refs = copias(raiz), branches_do_agente(raiz, aid)
    proprias = [p for p, ref in todas.items() if ref in refs]
    if not proprias:
        hook.registrar_erro(Aviso(f"copia: agente {aid} sem cópia no registro; a escrita fora dela não foi conferida"))
        return
    outras = [os.path.realpath(raiz), *todas]  # a própria entra também: o alvo dentro dela não chega a essa conta
    for alvo in lista:
        fora = not any(dentro(alvo, p) for p in proprias)
        if fora and (any(dentro(alvo, p) for p in outras) or not livre(alvo)):
            bloquear("R-CONFORMIDADE", f"{alvo} fica fora da sua cópia ({proprias[0]}): grave e rode git de escrita só nela")


if __name__ == "__main__":
    executar("copia", principal)
