#!/usr/bin/env python3
"""Forge: parecer de review e de QA antes de PR e de merge (ADR 0003, R-REVIEW, R-QA).

PreToolUse (Bash) com `gh pr create` ou `git merge <branch>` na branch de integração: exige parecer aprovado
e válido para a branch (validado pelo forge-check, ADR 0004). Libera mudança só de documentação (.md),
atualização a partir de uma branch de integração e promoção entre branches de integração.
"""
import re
from pathlib import Path

from _comum import (INTEGRACAO, bloquear, executar, forge_check, git, nome_da_branch, segmentos, sem_atribuicoes,
                     separar_regra)

PREFILTRO = re.compile(r"\bgh\b.*\bpr\b.*\bcreate\b|\bgit\b.*\bmerge\b", re.S)
MERGE_COM_VALOR = {"-m", "-F", "-s", "-X", "--message", "--file", "--strategy", "--strategy-option", "--into-name"}
MERGE_SEM_ALVO = {"--abort", "--continue", "--quit", "--skip"}
GIT_COM_VALOR = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
BASES = ("develop", "origin/develop", "main", "origin/main", "master", "origin/master")


def opcao(args, longa, curta):
    for i, a in enumerate(args):
        if a in (longa, curta) and i + 1 < len(args):
            return args[i + 1]
        if a.startswith(longa + "="):
            return a.split("=", 1)[1]
    return None


def analisar(toks):
    """('cd', dir) | ('pr', dir, base, head) | ('merge', dir, [refs]) | None."""
    toks = sem_atribuicoes(toks)
    if not toks:
        return None
    if toks[0] == "cd":
        return ("cd", toks[1] if len(toks) > 1 else None)
    if toks[0] == "gh" and "pr" in toks:
        i = toks.index("pr")
        if toks[i + 1: i + 2] == ["create"]:
            args = toks[i + 2:]
            return ("pr", None, opcao(args, "--base", "-B"), opcao(args, "--head", "-H"))
        return None
    if toks[0] != "git":
        return None
    i, pasta = 1, None
    while i < len(toks) and toks[i].startswith("-"):
        if toks[i] in GIT_COM_VALOR:
            pasta = toks[i + 1] if toks[i] == "-C" and i + 1 < len(toks) else pasta
            i += 2
        else:
            i += 1
    if toks[i: i + 1] != ["merge"]:
        return None
    args, refs, j = toks[i + 1:], [], 0
    if MERGE_SEM_ALVO & set(args):
        return None
    while j < len(args):
        if args[j] in MERGE_COM_VALOR:
            j += 2
            continue
        if not args[j].startswith("-"):
            refs.append(args[j])
        j += 1
    return ("merge", pasta, refs)


def existe(raiz, ref):
    return git(raiz, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0


def verificar(hook, raiz, branch, ref, base):
    """Bloqueia se a branch muda código e não tem parecer de review e de QA aprovado e válido."""
    if base:
        cod, arquivos = git(raiz, "diff", "--name-only", f"{base}...{ref or 'HEAD'}")
        if not cod and all(a.endswith(".md") for a in arquivos.splitlines()):
            return  # só documentação: não passa por QA (R-QA)
    fc = forge_check()
    pedidos = fc.pedidos_da_branch(raiz, branch, ref)
    if not pedidos:
        bloquear("R-REVIEW", f"nenhum parecer em docs/reviews/ e docs/qa/ com `branch: {branch}`; "
                             "faça o code review e o QA (R-QA) antes do PR ou do merge.")
    for pedido in pedidos:
        violacoes = fc.cmd_pr(raiz, pedido, ref)
        if violacoes:
            rid, texto = separar_regra(violacoes[0], "R-REVIEW")
            extra = f" (e mais {len(violacoes) - 1})" if len(violacoes) > 1 else ""
            bloquear(rid, f"{texto}{extra}; confira com forge-check pr {pedido}.")


def pull_request(hook, pasta, base, head):
    raiz = hook.projeto(pasta)
    if not raiz:
        return
    atual = git(raiz, "branch", "--show-current")[1]
    branch = nome_da_branch(head) if head else atual
    if not branch or branch in INTEGRACAO:
        return  # HEAD solto ou promoção entre branches de integração
    ref = None
    if head and branch != atual:
        ref = next((r for r in (head, f"origin/{branch}") if existe(raiz, r)), None)
        if ref is None:
            return  # a branch não existe localmente: nada a conferir aqui
    candidatas = (base, f"origin/{base}") if base else (b for b in BASES if nome_da_branch(b) != branch)
    verificar(hook, raiz, branch, ref, next((b for b in candidatas if existe(raiz, b)), None))


def merge(hook, pasta, refs):
    raiz = hook.projeto(pasta)
    if not raiz or git(raiz, "branch", "--show-current")[1] not in INTEGRACAO:
        return  # atualizar uma branch de trabalho é livre; o portão é a entrada na integração
    for ref in refs:
        branch = nome_da_branch(ref)
        if branch in INTEGRACAO or ref in ("HEAD", "FETCH_HEAD") or not existe(raiz, ref):
            continue
        verificar(hook, raiz, branch, ref, "HEAD")


def principal(hook):
    comando = hook.campo("tool_input", "command")
    if hook.campo("tool_name") != "Bash" or not isinstance(comando, str) or not PREFILTRO.search(comando):
        return
    pasta = hook.cwd()
    try:
        partes = [analisar(s) for s in segmentos(comando)]
    except ValueError:
        return  # aspas desbalanceadas: o próprio shell vai recusar
    for parte in partes:
        if parte is None:
            continue
        if parte[0] == "cd":
            pasta = pasta / Path(parte[1]).expanduser() if parte[1] else Path.home()
        elif parte[0] == "pr":
            pull_request(hook, pasta, parte[2], parte[3])
        else:
            merge(hook, pasta / parte[1] if parte[1] else pasta, parte[2])


if __name__ == "__main__":
    executar("parecer", principal)
