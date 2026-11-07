#!/usr/bin/env python3
"""Forge: a árvore deste checkout já passou pela suíte na develop? (EST-M7, decisões do dono 7a e 29). Só biblioteca padrão.

Parte E3a-1: só a decisão, pura, sobre dicionários (sem git e sem rede). O git, a API e a linha de comando entram na
E3a-2; até lá, rodar o arquivo sai 1, e a suíte roda inteira (falha fechada: só o rc 0 pula a suíte).
  evento_elegivel(env): lista branca exata de eventos (C-1 de docs/security/ameacas/versao-040.md). O workflow vem de
      GITHUB_WORKFLOW_REF, que o runner define e o passo não sobrescreve; o resto vem do `env:` do passo.
"""
import re
import sys

WORKFLOW_DE_PROVA = ".github/workflows/ci.yml"
PRS = {("homolog", "develop"), ("main", "homolog")}  # (BASE_REF, HEAD_REF)
PUSHES = {WORKFLOW_DE_PROVA: {"refs/heads/homolog", "refs/heads/main"}, ".github/workflows/release.yml": {"refs/heads/main"}}
REPOSITORIO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def campo(obj, caminho, tipo):
    """O valor em `caminho` (chaves separadas por ponto) se for exatamente do `tipo`; senão None (bool não é int)."""
    for chave in caminho.split("."):
        obj = obj.get(chave) if isinstance(obj, dict) else None
    return obj if type(obj) is tipo else None


def evento_elegivel(env):
    """(True, motivo) só para PR develop->homolog e homolog->main do próprio repositório no ci.yml, push na homolog
    ou na main no ci.yml e push na main no release.yml; qualquer outro caso, (False, motivo)."""
    repo, evento, ref = (campo(env, k, str) or "" for k in ("REPO", "EVENTO", "REF"))
    origem, _, _ = (campo(env, "GITHUB_WORKFLOW_REF", str) or "").partition("@")
    workflow = origem.removeprefix(repo + "/")
    if not REPOSITORIO.fullmatch(repo) or workflow == origem:
        return False, "REPO ou GITHUB_WORKFLOW_REF fora do formato"
    if evento == "pull_request":
        par = (campo(env, "BASE_REF", str), campo(env, "HEAD_REF", str))
        ok = workflow == WORKFLOW_DE_PROVA and par in PRS and campo(env, "HEAD_REPO", str) == repo
        return ok, f"pull_request {par[1]} -> {par[0]} em {workflow}: {'elegível' if ok else 'fora da lista'}"
    ok = evento == "push" and ref in PUSHES.get(workflow, ())
    return ok, f"{evento or '(sem evento)'} {ref} em {workflow}: {'elegível' if ok else 'fora da lista'}"


if __name__ == "__main__":
    print("arvore-testada: sem linha de comando até a E3a-2; a suíte roda inteira", file=sys.stderr)
    sys.exit(1)
