#!/usr/bin/env python3
"""Forge: a árvore deste checkout já passou pela suíte na develop? (EST-M7, decisões do dono 7a e 29). Só biblioteca padrão.

Uso (SP4, 0.43.3): `python3 scripts/arvore-testada.py [--python X.Y]`, no checkout do evento. rc 0 só com a prova completa:
o evento está na lista branca, um commit do `git log` do HEAD tem a MESMA árvore (tree-sha) do HEAD e a execução `push` da
develop nesse commit tem o job de prova do Python pedido (padrão: o do interpretador) em `success`. Qualquer falta, erro de
git, de rede ou de formato sai 1 e a suíte roda inteira (falha fechada: só o rc 0 pula a suíte). Lê GH_TOKEN e
GITHUB_API_URL (padrão https://api.github.com), mais o `env:` do passo; nunca imprime o token.
  evento_elegivel(env, raiz): lista branca exata de eventos (C-1 de docs/security/ameacas/versao-040.md). O workflow vem de
      GITHUB_WORKFLOW_REF, que o runner define e o passo não sobrescreve; o resto vem do `env:` do passo. O par do PR é o da
      tabela única PROMOCOES de tests/catraca.py (`promocao_aceita`, com HEAD_SHA na develop do servidor quando a linha pede).
  prova_valida(execucoes, jobs, d, python, repo): uma execução `push` da develop no commit `d`, do ci.yml do próprio
      repositório, concluída, com o job de prova do Python pedido em `success` na tentativa mais recente (C-3).
      `jobs` é {id da execução: [jobs]}. Campo ausente ou de tipo errado não prova.
  candidatos(arvore, log): os commits do `git log --format='%H %T'` com a mesma árvore do HEAD (a prova é da árvore).
  provar(env, python, arvore, log, ler): junta as três, com `ler(caminho)` da API injetado (sem rede nos testes).
  prova_do_pr(env, ler): F6 (v0481), `--do-pr`, só no push na develop: o commit é o merge de um PR do próprio repositório
      cujo head tem a MESMA árvore, descende da develop anterior e que tem o run do ci.yml de `pull_request` desse PR (base
      develop, base do run ancestral do head), concluído, com o job "bateria" em `success` na tentativa mais recente (A1 do
      parecer de segurança do #929); sem tudo isso, a suíte do push roda inteira.
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

WORKFLOW_DE_PROVA = ".github/workflows/ci.yml"
PUSHES = {WORKFLOW_DE_PROVA: {"refs/heads/homolog", "refs/heads/main"}, ".github/workflows/release.yml": {"refs/heads/main"}}
NOME_DA_BATERIA = "bateria"  # o check exigido do PR (agregador do ci.yml)
JOBS_DE_PROVA = {"3.12": "checagem rápida (push na develop)"}
SHA = re.compile(r"[0-9a-f]{40}")
PYTHON = re.compile(r"3\.\d{1,2}")
LIMITE_DO_LOG = 200  # commits do HEAD lidos atrás da mesma árvore (a promoção traz a develop a 1 ou 2 merges de distância)
LIMITE_DE_CANDIDATOS = 5  # commits com a mesma árvore consultados na API
LIMITE_DE_EXECUCOES = 10  # execuções do ci.yml por commit cujos jobs são lidos
PRAZO_DA_API_S = 20
REPOSITORIO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def _catraca():
    """tests/catraca.py ao lado deste script: a tabela PROMOCOES é uma só (R-FLUXO)."""
    caminho = Path(__file__).resolve().parent.parent / "tests" / "catraca.py"
    spec = importlib.util.spec_from_file_location("catraca_da_arvore", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


CATRACA = _catraca()


def campo(obj, caminho, tipo):
    """O valor em `caminho` (chaves separadas por ponto) se for exatamente do `tipo`; senão None (bool não é int)."""
    for chave in caminho.split("."):
        obj = obj.get(chave) if isinstance(obj, dict) else None
    return obj if type(obj) is tipo else None


def evento_elegivel(env, raiz="."):
    """(True, motivo) só para PR de promoção (PROMOCOES) do próprio repositório no ci.yml, push na homolog
    ou na main no ci.yml e push na main no release.yml; qualquer outro caso, (False, motivo)."""
    repo, evento, ref = (campo(env, k, str) or "" for k in ("REPO", "EVENTO", "REF"))
    origem, _, _ = (campo(env, "GITHUB_WORKFLOW_REF", str) or "").partition("@")
    workflow = origem.removeprefix(repo + "/")
    if not REPOSITORIO.fullmatch(repo) or workflow == origem:
        return False, "REPO ou GITHUB_WORKFLOW_REF fora do formato"
    if evento == "pull_request":
        par = (campo(env, "BASE_REF", str), campo(env, "HEAD_REF", str))
        ok = (workflow == WORKFLOW_DE_PROVA and campo(env, "HEAD_REPO", str) == repo
              and CATRACA.promocao_aceita(raiz, par[1], par[0], campo(env, "HEAD_SHA", str)))
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


def candidatos(arvore, log):
    """Os commits (no máximo LIMITE_DE_CANDIDATOS, na ordem do log, sem repetir) cuja árvore é `arvore`. `log` é a saída de
    `git log --format='%H %T'`; linha fora do formato é ignorada (não prova nada)."""
    if not (type(arvore) is str and SHA.fullmatch(arvore) and type(log) is str):
        return []
    achados = []
    for linha in log.splitlines():
        partes = linha.split(" ")
        if len(partes) == 2 and SHA.fullmatch(partes[0]) and partes[1] == arvore and partes[0] not in achados:
            achados.append(partes[0])
    return achados[:LIMITE_DE_CANDIDATOS]


def provar(env, python, arvore, log, ler):
    """(True, motivo) só com evento elegível, commit de mesma árvore e prova válida dele; senão (False, motivo).
    `ler(caminho)` devolve o JSON da API (pode lançar: quem chama trata como falta de prova)."""
    ok, motivo = evento_elegivel(env)
    if not ok:
        return False, motivo
    repo = env["REPO"]
    lista = candidatos(arvore, log)
    if not lista:
        return False, "nenhum commit do HEAD tem a árvore do HEAD (fora do formato)"
    for commit in lista:
        consulta = urllib.parse.urlencode({"head_sha": commit, "event": "push", "branch": "develop", "per_page": 100})
        execucoes = campo(ler(f"repos/{repo}/actions/runs?{consulta}"), "workflow_runs", list) or []
        jobs = {}
        for execucao in [e for e in execucoes if campo(e, "path", str) == WORKFLOW_DE_PROVA][:LIMITE_DE_EXECUCOES]:
            run_id = campo(execucao, "id", int)
            if run_id is not None:
                jobs[run_id] = campo(ler(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"), "jobs", list)
        ok, motivo = prova_valida(execucoes, jobs, commit, python, repo)
        if ok:
            return True, f"árvore {arvore[:7]} igual à de {motivo}"
    return False, f"nenhum dos {len(lista)} commits com a árvore {arvore[:7]} tem a prova do Python {python} na develop"


def prova_do_pr(env, ler):
    """(True, motivo) só com o push na develop do ci.yml do próprio repositório, um PR mesclado neste commit (base develop, head do
    mesmo repositório), árvore do head igual à do commit, develop anterior e base do PR ancestrais do head e, no head e no ramo desse
    PR (a lista `pull_requests` do run some após o merge), o run do ci.yml de `pull_request` do próprio repositório, concluído, com o job `bateria` em success na tentativa mais recente
    (A1 do parecer de segurança do #929: padrão C-3 do `prova_valida`; check solto de outro app, de outra base ou de outro
    workflow não prova); senão (False, motivo). `ler(caminho)` devolve o JSON da API (pode lançar: falha fechada)."""
    repo, evento, ref, sha = (campo(env, k, str) or "" for k in ("REPO", "EVENTO", "REF", "SHA"))
    origem, _, _ = (campo(env, "GITHUB_WORKFLOW_REF", str) or "").partition("@")
    if not (REPOSITORIO.fullmatch(repo) and SHA.fullmatch(sha) and origem == f"{repo}/{WORKFLOW_DE_PROVA}"
            and evento == "push" and ref == "refs/heads/develop"):
        return False, "só o push na develop do ci.yml do próprio repositório"
    commit = ler(f"repos/{repo}/commits/{sha}")
    arvore = campo(commit, "commit.tree.sha", str)
    pais = campo(commit, "parents", list) or []
    anterior = campo(pais[0], "sha", str) if pais else None
    if not (arvore and anterior and SHA.fullmatch(arvore) and SHA.fullmatch(anterior)):
        return False, "commit sem árvore ou sem pai no formato"
    prs = ler(f"repos/{repo}/commits/{sha}/pulls?per_page=10")
    for pr in (prs if type(prs) is list else [])[:LIMITE_DE_CANDIDATOS]:
        cabeca, numero = campo(pr, "head.sha", str), campo(pr, "number", int)
        ramo, base = campo(pr, "head.ref", str), campo(pr, "base.sha", str)
        if not (cabeca and SHA.fullmatch(cabeca) and numero is not None and ramo and base and SHA.fullmatch(base)
                and campo(pr, "base.ref", str) == "develop" and campo(pr, "head.repo.full_name", str) == repo
                and campo(pr, "merge_commit_sha", str) == sha and campo(pr, "merged_at", str)):
            continue
        if campo(ler(f"repos/{repo}/git/commits/{cabeca}"), "tree.sha", str) != arvore:
            continue
        if campo(ler(f"repos/{repo}/compare/{anterior}...{cabeca}"), "status", str) not in ("ahead", "identical"):
            continue
        achou, motivo = bateria_do_run_do_pr(repo, cabeca, ramo, base, ler)
        if achou:
            return True, f"árvore {arvore[:7]} igual à do head {cabeca[:7]} do PR #{numero}, {motivo}"
    return False, f"nenhum PR mesclado em {sha[:7]} tem head de mesma árvore, descendente da develop e com a bateria verde no run do PR"


def bateria_do_run_do_pr(repo, cabeca, ramo, base, ler):
    """(True, 'run <id>, job bateria') só com o run mais recente do ci.yml do evento pull_request, do próprio repositório, concluído,
    no head e no ramo do PR (head_sha e head_branch: a lista `pull_requests` do run some depois do merge, então não liga), com a
    base do PR (`base`, contra a develop) ancestral do head, e com um único job `bateria` em success na tentativa mais recente
    do run; senão (False, motivo)."""
    consulta = urllib.parse.urlencode({"head_sha": cabeca, "event": "pull_request", "per_page": 100})
    execucoes = campo(ler(f"repos/{repo}/actions/runs?{consulta}"), "workflow_runs", list) or []
    da_execucao = {"event": "pull_request", "head_sha": cabeca, "path": WORKFLOW_DE_PROVA, "repository.full_name": repo,
                   "head_repository.full_name": repo, "status": "completed", "head_branch": ramo}
    validas = []
    for execucao in execucoes:
        run_id, tentativa = campo(execucao, "id", int), campo(execucao, "run_attempt", int)
        if None in (run_id, tentativa) or any(campo(execucao, k, str) != v for k, v in da_execucao.items()):
            continue
        validas.append((run_id, tentativa))
    if not validas:
        return False, "nenhum run do ci.yml do PR no head"
    run_id, tentativa = max(validas)  # o mais recente decide: um run vermelho depois de um verde reprova
    if campo(ler(f"repos/{repo}/compare/{base}...{cabeca}"), "status", str) not in ("ahead", "identical"):
        return False, "base do PR fora do head"
    lista = campo(ler(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"), "jobs", list) or []
    com_nome = [j for j in lista if campo(j, "name", str) == NOME_DA_BATERIA]
    do_job = {"conclusion": "success", "head_sha": cabeca, "run_id": run_id, "run_attempt": tentativa}
    if len(com_nome) == 1 and all(campo(com_nome[0], k, type(v)) == v for k, v in do_job.items()):
        return True, f"run {run_id}, job {NOME_DA_BATERIA}"
    return False, f"o job {NOME_DA_BATERIA} do run {run_id} não está em success na tentativa mais recente"


def leitor_da_api(env):
    """`ler(caminho)`: GET autenticado na API do GitHub (GITHUB_API_URL, padrão https://api.github.com), JSON, com prazo."""
    base = (env.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")
    cabecalhos = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if env.get("GH_TOKEN"):
        cabecalhos["Authorization"] = f"Bearer {env['GH_TOKEN']}"

    def ler(caminho):
        with urllib.request.urlopen(urllib.request.Request(f"{base}/{caminho}", headers=cabecalhos), timeout=PRAZO_DA_API_S) as r:
            return json.loads(r.read().decode("utf-8"))
    return ler


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, timeout=60, check=True).stdout.strip()


def main(argv=None, env=None):
    env = dict(os.environ if env is None else env)
    p = argparse.ArgumentParser(prog="arvore-testada", description="rc 0: a árvore do HEAD já passou na suíte da develop")
    p.add_argument("--python", default=f"{sys.version_info.major}.{sys.version_info.minor}",
                   help="versão do job de prova (padrão: a deste interpretador)")
    p.add_argument("--do-pr", action="store_true", help="F6: o push na develop reaproveita a prova do PR mesclado")
    a = p.parse_args(argv)
    if a.do_pr:
        try:
            ok, motivo = prova_do_pr(env, leitor_da_api(env))
        except Exception as erro:  # rede, HTTP, JSON: falha fechada, sem detalhe que possa trazer o token
            ok, motivo = False, f"erro ao ler a prova ({type(erro).__name__})"
        print(f"arvore-testada: {'provada: ' + motivo + '; a suíte do push não roda de novo' if ok else 'sem prova (' + motivo + '); a suíte do push roda inteira'}")
        return 0 if ok else 1
    if not PYTHON.fullmatch(a.python):
        print("arvore-testada: --python fora do formato X.Y; sem prova, a suíte roda inteira", file=sys.stderr)
        return 1
    try:
        arvore = git("rev-parse", "--verify", "HEAD^{tree}")
        log = git("log", f"-n{LIMITE_DO_LOG}", "--format=%H %T", "HEAD")
        ok, motivo = provar(env, a.python, arvore, log, leitor_da_api(env))
    except Exception as erro:  # git, rede, HTTP, JSON: falha fechada, sem detalhe que possa trazer o token
        ok, motivo = False, f"erro ao ler a prova ({type(erro).__name__})"
    if ok:
        print(f"arvore-testada: provada: {motivo}; a suíte não roda de novo")
        return 0
    print(f"arvore-testada: sem prova ({motivo}); a suíte roda inteira")
    return 1


if __name__ == "__main__":
    sys.exit(main())
