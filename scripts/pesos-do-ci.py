#!/usr/bin/env python3
"""Forge: refaz `tests/pesos-d4.json` com os tempos por unidade que as pernas do CI gravaram em anotação de check run
(CI-RAPIDO, v047). Só biblioteca padrão; lê só a API do GitHub; NUNCA escreve no repositório sozinho (R-MAIN, R-VERIFY):
o arquivo novo sai em --saida (ou no stdout) para o dev da stack conferir e commitar.

Uso: python3 -I scripts/pesos-do-ci.py [--repo DONO/REPO] [--execucoes N] [--saida ARQUIVO]
  Lê GH_TOKEN (opcional em repositório público) e GITHUB_API_URL (padrão https://api.github.com); nunca imprime o token.

O que entra (A2 do parecer de segurança, o mesmo filtro de `scripts/arvore-testada.py`):
  - execução `push` na `develop` do `.github/workflows/ci.yml`, `repository` e `head_repository` iguais ao `--repo`,
    concluída, `conclusion == success`;
  - job de perna da develop (`suíte (push na develop, python X.Y, parte K/N)`) em `success`, do mesmo run;
  - anotação `forge-tempos` com JSON `{"v": 1, "parte": "K/N", "python": "X.Y", "bloco": [i, m], "t": {unidade: s}}` cuja
    parte e Python batem com os do nome do job;
  - unidade que existe no plano da árvore atual, no alfabeto `[A-Za-z0-9_.]`, com segundos finitos em [0, TETO_S].
  Anotação fora do formato é descartada inteira. Anotação de PR (ou de fork) nunca entra: o filtro é da execução.
Cada unidade vale a média, entre os Pythons, da média das amostras de cada um; a unidade sem amostra mantém o peso do
arquivo atual (e o script avisa em stderr quais).
"""
import argparse
import json
import math
import os
import re
import statistics
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WORKFLOW = ".github/workflows/ci.yml"
PESOS = RAIZ / "tests" / "pesos-d4.json"
REPOSITORIO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
PERNA = re.compile(r"suíte \(push na develop, python (3\.[0-9]{1,2}), parte ([1-9][0-9]?)/([1-9][0-9]?)\)")
UNIDADE = re.compile(r"[A-Za-z0-9_.]{1,200}")
TETO_S = 900.0  # o `timeout-minutes` de 15 da perna: unidade acima disto é adulterada ou defeito
LIMITE_DE_EXECUCOES = 10
PRAZO_DA_API_S = 20


def campo(obj, caminho, tipo):
    """O valor em `caminho` (chaves separadas por ponto) se for exatamente do `tipo`; senão None (bool não é int)."""
    for chave in caminho.split("."):
        obj = obj.get(chave) if isinstance(obj, dict) else None
    return obj if type(obj) is tipo else None


def execucao_valida(execucao, repo):
    """True só para a execução `push` da develop do ci.yml do próprio repositório, concluída com sucesso."""
    da_execucao = {"event": "push", "head_branch": "develop", "path": WORKFLOW, "repository.full_name": repo,
                   "head_repository.full_name": repo, "status": "completed", "conclusion": "success"}
    return (campo(execucao, "id", int) is not None
            and all(campo(execucao, k, str) == v for k, v in da_execucao.items()))


def perna_valida(job):
    """(python, K, N) do job de perna da develop em `success`; None para qualquer outro."""
    achado = PERNA.fullmatch(campo(job, "name", str) or "")
    if not achado or campo(job, "conclusion", str) != "success" or campo(job, "id", int) is None:
        return None
    k, n = int(achado.group(2)), int(achado.group(3))
    return (achado.group(1), k, n) if k <= n else None


def ler_anotacao(anotacao, perna, conhecidas):
    """{unidade: segundos} de uma anotação `forge-tempos` da `perna` (python, K, N), ou None se qualquer coisa estiver fora
    do formato: JSON ilegível, versão, parte ou Python diferentes do job, unidade fora do alfabeto ou do plano, segundos
    não finitos, negativos ou acima do teto (a anotação inteira é descartada)."""
    titulo, mensagem = campo(anotacao, "title", str), campo(anotacao, "message", str)
    if not (titulo and titulo.startswith("forge-tempos ") and mensagem):
        return None
    try:
        dado = json.loads(mensagem)
    except ValueError:
        return None
    python, k, n = perna
    tempos = campo(dado, "t", dict)
    if not (isinstance(dado, dict) and dado.get("v") == 1 and tempos and campo(dado, "parte", str) == f"{k}/{n}"
            and campo(dado, "python", str) == python):
        return None
    saida = {}
    for nome, seg in tempos.items():
        if not (isinstance(nome, str) and UNIDADE.fullmatch(nome) and nome in conhecidas and type(seg) in (int, float)
                and math.isfinite(seg) and 0 <= seg <= TETO_S):
            return None
        saida[nome] = float(seg)
    return saida


def juntar(amostras):
    """{unidade: peso}: a média entre os Pythons da média das amostras de cada um. `amostras` é {(python, unidade): [s]}."""
    por_unidade = {}
    for (python, unidade), valores in amostras.items():
        por_unidade.setdefault(unidade, []).append(statistics.fmean(valores))
    return {u: round(statistics.fmean(v), 1) for u, v in sorted(por_unidade.items())}


def gerar(atuais, medidos, conhecidas):
    """(pesos novos, unidades sem medida): o medido vale; a unidade conhecida sem amostra mantém o peso atual (se tinha);
    chave que não é mais unidade do plano sai."""
    novos, sem_medida = {}, []
    for unidade in sorted(conhecidas):
        if unidade in medidos:
            novos[unidade] = medidos[unidade]
        elif unidade in atuais:
            novos[unidade] = atuais[unidade]
            sem_medida.append(unidade)
    return novos, sem_medida


def coletar(repo, ler, conhecidas, limite=LIMITE_DE_EXECUCOES):
    """({(python, unidade): [segundos]}, resumo): lê as execuções válidas da develop, os jobs de perna e as anotações.
    `ler(caminho)` devolve o JSON da API. Cada perna só conta uma vez por execução e a perna fora do conjunto 1..N
    completo da execução é descartada (amostra de execução parcial não entra)."""
    consulta = urllib.parse.urlencode({"event": "push", "branch": "develop", "status": "success", "per_page": 100})
    execucoes = [e for e in campo(ler(f"repos/{repo}/actions/workflows/ci.yml/runs?{consulta}"), "workflow_runs", list)
                 or [] if execucao_valida(e, repo)][:limite]
    amostras, usadas = {}, 0
    for execucao in execucoes:
        run_id = campo(execucao, "id", int)
        jobs = campo(ler(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"), "jobs", list) or []
        do_run = {}
        for job in jobs:
            perna = perna_valida(job)
            if perna is None or campo(job, "run_id", int) != run_id:
                continue
            lista = ler(f"repos/{repo}/check-runs/{campo(job, 'id', int)}/annotations?per_page=100")
            tempos = {}
            for anotacao in lista if isinstance(lista, list) else []:
                lido = ler_anotacao(anotacao, perna, conhecidas)
                if lido is not None:
                    tempos.update(lido)
            if tempos:
                do_run.setdefault(perna[0], {})[perna[1]] = (perna[2], tempos)
        for python, partes in do_run.items():
            quantas = {n for n, _ in partes.values()}
            if len(quantas) == 1 and set(partes) == set(range(1, next(iter(quantas)) + 1)):
                usadas += 1
                for _, tempos in partes.values():
                    for unidade, seg in tempos.items():
                        amostras.setdefault((python, unidade), []).append(seg)
    return amostras, f"{len(execucoes)} execução(ões) válida(s) da develop, {usadas} conjunto(s) completo(s) de pernas"


def leitor_da_api(env):
    """`ler(caminho)`: GET na API do GitHub (GITHUB_API_URL, padrão https://api.github.com), JSON, com prazo."""
    base = (env.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")
    cabecalhos = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if env.get("GH_TOKEN"):
        cabecalhos["Authorization"] = f"Bearer {env['GH_TOKEN']}"

    def ler(caminho):
        pedido = urllib.request.Request(f"{base}/{caminho}", headers=cabecalhos)
        with urllib.request.urlopen(pedido, timeout=PRAZO_DA_API_S) as r:
            return json.loads(r.read().decode("utf-8"))
    return ler


def unidades_do_plano():
    """As unidades do plano da árvore atual (as de `suite-partes.py` com os pesos de hoje)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("suite_partes", RAIZ / "scripts" / "suite-partes.py")
    partes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(partes)
    sp = partes.carregar_paralela()
    os.chdir(sp.RAIZ)
    sys.path.insert(0, str(sp.RAIZ / sp.TESTES))
    return set(partes.dividir_por_unidade(sp, partes.todos_os_modulos(sp), 1)[1])


def main(argv=None, env=None, ler=None, conhecidas=None):
    env = dict(os.environ if env is None else env)
    p = argparse.ArgumentParser(prog="pesos-do-ci", description="refaz tests/pesos-d4.json com os tempos do CI")
    p.add_argument("--repo", default=env.get("GITHUB_REPOSITORY", ""), help="DONO/REPO (padrão: GITHUB_REPOSITORY)")
    p.add_argument("--execucoes", type=int, default=LIMITE_DE_EXECUCOES)
    p.add_argument("--saida", help="arquivo de saída (padrão: stdout); nunca o próprio tests/pesos-d4.json sem querer")
    a = p.parse_args(argv)
    if not REPOSITORIO.fullmatch(a.repo) or not 1 <= a.execucoes <= 30:
        print("pesos-do-ci: --repo fora do formato DONO/REPO ou --execucoes fora de 1 a 30", file=sys.stderr)
        return 2
    try:
        conhecidas = unidades_do_plano() if conhecidas is None else conhecidas
        amostras, resumo = coletar(a.repo, ler or leitor_da_api(env), conhecidas, a.execucoes)
    except Exception as erro:  # rede, HTTP, JSON, plano: sem detalhe que possa trazer o token
        print(f"pesos-do-ci: erro ao ler a API ({type(erro).__name__})", file=sys.stderr)
        return 1
    if not amostras:
        print(f"pesos-do-ci: nenhuma amostra válida ({resumo}); os pesos não mudam", file=sys.stderr)
        return 1
    try:
        atuais = json.loads(PESOS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        atuais = {}
    novos, sem_medida = gerar(atuais if isinstance(atuais, dict) else {}, juntar(amostras), conhecidas)
    if sem_medida:
        print(f"pesos-do-ci: {len(sem_medida)} unidade(s) sem medida mantêm o peso atual: "
              f"{', '.join(sem_medida[:10])}{' ...' if len(sem_medida) > 10 else ''}", file=sys.stderr)
    texto = json.dumps(novos, indent=2, ensure_ascii=False) + "\n"
    if a.saida:
        Path(a.saida).write_text(texto, encoding="utf-8")
    else:
        sys.stdout.write(texto)
    print(f"pesos-do-ci: {len(novos)} unidades; {resumo}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
