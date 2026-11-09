#!/usr/bin/env python3
"""Forge: a árvore deste checkout já passou pela suíte na develop? (EST-M7, decisões do dono 7a e 29). Só biblioteca padrão.

Uso (SP4, 0.43.3): `python3 scripts/arvore-testada.py [--python X.Y]`, no checkout do evento. rc 0 só com a prova completa:
o evento está na lista branca, um commit do `git log` do HEAD tem a MESMA árvore (tree-sha) do HEAD e a execução `push` da
develop nesse commit tem o job de prova do Python pedido (padrão: o do interpretador) em `success`. Qualquer falta, erro de
git, de rede ou de formato sai 1 e a suíte roda inteira (falha fechada: só o rc 0 pula a suíte). Lê GH_TOKEN e
GITHUB_API_URL (padrão https://api.github.com), mais o `env:` do passo; nunca imprime o token.
  evento_elegivel(env): lista branca exata de eventos (C-1 de docs/security/ameacas/versao-040.md). O workflow vem de
      GITHUB_WORKFLOW_REF, que o runner define e o passo não sobrescreve; o resto vem do `env:` do passo.
  prova_valida(execucoes, jobs, d, python, repo): uma execução `push` da develop no commit `d`, do ci.yml do próprio
      repositório, concluída, com o job de prova do Python pedido em `success` na tentativa mais recente (C-3).
      `jobs` é {id da execução: [jobs]}. Campo ausente ou de tipo errado não prova.
  candidatos(arvore, log): os commits do `git log --format='%H %T'` com a mesma árvore do HEAD (a prova é da árvore).
  provar(env, python, arvore, log, ler): junta as três, com `ler(caminho)` da API injetado (sem rede nos testes).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

WORKFLOW_DE_PROVA = ".github/workflows/ci.yml"
PRS = {("homolog", "develop"), ("main", "homolog")}  # (BASE_REF, HEAD_REF)
PUSHES = {WORKFLOW_DE_PROVA: {"refs/heads/homolog", "refs/heads/main"}, ".github/workflows/release.yml": {"refs/heads/main"}}
JOBS_DE_PROVA = {"3.12": "checagem rápida (push na develop)", "3.14": "checagem rápida (push na develop, python 3.14)"}
SHA = re.compile(r"[0-9a-f]{40}")
PYTHON = re.compile(r"3\.\d{1,2}")
LIMITE_DO_LOG = 200  # commits do HEAD lidos atrás da mesma árvore (a promoção traz a develop a 1 ou 2 merges de distância)
LIMITE_DE_CANDIDATOS = 5  # commits com a mesma árvore consultados na API
LIMITE_DE_EXECUCOES = 10  # execuções do ci.yml por commit cujos jobs são lidos
PRAZO_DA_API_S = 20
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
    a = p.parse_args(argv)
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
