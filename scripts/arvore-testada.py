#!/usr/bin/env python3
"""Forge: a árvore deste checkout já passou pela suíte na develop? (EST-M7, decisões do dono 7a e 29). Só biblioteca padrão.

Parte E3a-1: só a decisão, pura, sobre dicionários (sem git e sem rede). O git, a API e a linha de comando entram na
E3a-2; até lá, rodar o arquivo sai 1, e a suíte roda inteira (falha fechada: só o rc 0 pula a suíte).
  evento_elegivel(env): lista branca exata de eventos (C-1 de docs/security/ameacas/versao-040.md). O workflow vem de
      GITHUB_WORKFLOW_REF, que o runner define e o passo não sobrescreve; o resto vem do `env:` do passo.
  prova_valida(execucoes, jobs, d, python, repo): uma execução `push` da develop no commit `d`, do ci.yml do próprio
      repositório, concluída, com o job de prova do Python pedido em `success` na tentativa mais recente (C-3).
      `jobs` é {id da execução: [jobs]}. Campo ausente ou de tipo errado não prova.
"""
import re
import sys

WORKFLOW_DE_PROVA = ".github/workflows/ci.yml"
PRS = {("homolog", "develop"), ("main", "homolog")}  # (BASE_REF, HEAD_REF)
PUSHES = {WORKFLOW_DE_PROVA: {"refs/heads/homolog", "refs/heads/main"}, ".github/workflows/release.yml": {"refs/heads/main"}}
JOBS_DE_PROVA = {"3.12": "checagem rápida (push na develop)", "3.14": "checagem rápida (push na develop, python 3.14)"}
SHA = re.compile(r"[0-9a-f]{40}")
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


def prova_valida(execucoes, jobs, d, python, repo):
    """(True, 'develop <D7>, run <id>, job <nome>') só com a prova completa; senão (False, motivo)."""
    nome = JOBS_DE_PROVA.get(python)
    if not (nome and type(d) is str and SHA.fullmatch(d) and type(repo) is str and REPOSITORIO.fullmatch(repo)
            and type(execucoes) is list and type(jobs) is dict):
        return False, "entrada fora do formato"
    da_execucao = {"event": "push", "head_branch": "develop", "head_sha": d, "path": WORKFLOW_DE_PROVA,
                   "repository.full_name": repo, "head_repository.full_name": repo, "status": "completed"}
    for execucao in execucoes:
        run_id, tentativa = campo(execucao, "id", int), campo(execucao, "run_attempt", int)
        if None in (run_id, tentativa) or any(campo(execucao, k, str) != v for k, v in da_execucao.items()):
            continue
        do_job = {"name": nome, "conclusion": "success", "head_sha": d, "run_id": run_id, "run_attempt": tentativa}
        lista = jobs.get(run_id)
        com_nome = [j for j in lista if campo(j, "name", str) == nome] if type(lista) is list else []
        if len(com_nome) == 1 and all(campo(com_nome[0], k, type(v)) == v for k, v in do_job.items()):
            return True, f"develop {d[:7]}, run {run_id}, job {nome}"
    return False, f"nenhuma execução prova o job {nome} em develop {d[:7]}"


if __name__ == "__main__":
    print("arvore-testada: sem linha de comando até a E3a-2; a suíte roda inteira", file=sys.stderr)
    sys.exit(1)
