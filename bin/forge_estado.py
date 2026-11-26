"""Forge: `forge-check status` (S1a, v0481 E20.1): o estado da fábrica numa tela curta, lido da ferramenta na hora, para o Jarvis
nunca afirmar estado de memória. Só leitura, sem `git fetch`; só biblioteca padrão.

Seis linhas `status: ...`: o último merge na develop e a idade (`gh api .../commits/develop`); os PRs abertos em esperando
revisão, esperando rótulo do dono (título com `afrouxa-regra` sem o rótulo), em conflito e quebrados (check reprovado); o contador
da versão (a 1.ª linha do `bin/forge-contador`); as decisões do dono abertas e a idade da mais antiga (o leitor do
`forge_dono.cmd_abertas`); a última versão publicada (`gh release view`); a versão do plugin da sessão (o plugin.json ao lado deste
forge-check). Leitura que falha (sem rede, sem gh, saída fora da forma) vira `<item>: não verificável (<motivo>)`, nunca erro: rc 0.
"""
import datetime as dt
import subprocess
import sys
from pathlib import Path

QUEBRADO = {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
ROTULO_DO_DONO = "afrouxa-regra"
GRUPOS = ("esperando revisão", "esperando rótulo do dono", "em conflito", "quebrados")
TETO_DO_CONTADOR_S = 20


class NaoVerificavel(Exception):
    pass


def instante(texto):
    """O datetime com fuso de um ISO 8601 do GitHub (`...Z`); fora da forma, NaoVerificavel."""
    try:
        return dt.datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        raise NaoVerificavel(f"data ilegível: {str(texto)[:40]}") from None


def idade(antes, agora):
    """`há N min`, `há N h` (até 47 h) ou `há N d`; no futuro, `há 0 min`."""
    minutos = max(0, int((agora - antes).total_seconds() // 60))
    if minutos < 60:
        return f"há {minutos} min"
    return f"há {minutos // 60} h" if minutos < 48 * 60 else f"há {minutos // 1440} d"


def lido(ctx, raiz, *args):
    """O JSON do `gh <args>` pelo `gh_json` do forge-check; sem saída, NaoVerificavel com o stderr."""
    dados, erro = ctx["gh_json"](raiz, *args)
    if dados is None:
        raise NaoVerificavel(" ".join(str(erro or "gh sem saída").split())[:120])
    return dados


def ultimo_merge(ctx, raiz, agora):
    dados = lido(ctx, raiz, "api", "repos/{owner}/{repo}/commits/develop")
    try:
        sha, quando, titulo = dados["sha"][:9], dados["commit"]["committer"]["date"], dados["commit"]["message"].split("\n")[0]
    except (KeyError, TypeError, AttributeError):
        raise NaoVerificavel("resposta fora da forma") from None
    return f"{sha} {idade(instante(quando), agora)} ({quando}) · {titulo[:80]}"


def grupo_do_pr(pr):
    """O índice em GRUPOS: conflito, depois o rótulo do dono que falta, depois check reprovado; o resto espera revisão."""
    if pr.get("mergeable") == "CONFLICTING":
        return 2
    rotulos = {r.get("name") for r in pr.get("labels") or []}
    if ROTULO_DO_DONO in (pr.get("title") or "") and ROTULO_DO_DONO not in rotulos:
        return 1
    checks = pr.get("statusCheckRollup") or []
    if any((c.get("conclusion") or c.get("state")) in QUEBRADO for c in checks):
        return 3
    return 0


def prs_abertos(ctx, raiz, agora):
    prs = lido(ctx, raiz, "pr", "list", "--state", "open", "--limit", "100",
               "--json", "number,title,mergeable,labels,statusCheckRollup")
    if not isinstance(prs, list) or not all(isinstance(p, dict) and isinstance(p.get("number"), int) for p in prs):
        raise NaoVerificavel("resposta fora da forma")
    grupos = [[] for _ in GRUPOS]
    for pr in prs:
        grupos[grupo_do_pr(pr)].append(f"#{pr['number']}")
    partes = [f"{nome} {len(g)}" + (f" ({' '.join(g)})" if g else "") for nome, g in zip(GRUPOS, grupos)]
    return f"{len(prs)} · " + " · ".join(partes)


def contador(ctx, raiz, agora):
    try:
        r = subprocess.run([sys.executable, "-I", str(ctx["plugin"] / "bin" / "forge-contador"), "--raiz", str(raiz)],
                           capture_output=True, text=True, timeout=TETO_DO_CONTADOR_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as erro:
        raise NaoVerificavel(type(erro).__name__) from None
    if r.returncode != 0 or not r.stdout.strip():
        raise NaoVerificavel(" ".join((r.stderr or "forge-contador sem saída").split())[:120])
    return r.stdout.strip().splitlines()[0]


def decisoes(ctx, raiz, agora):
    linhas, codigo = ctx["abertas"](ctx["pedidos"])
    if codigo:
        raise NaoVerificavel(linhas[0] if linhas else "leitura recusada")
    abertas = [linha.split(" | ") for linha in linhas if linha.startswith("aberta:")]
    if not abertas:
        return "0"
    horas = sorted(c[2] for c in abertas if len(c) > 2 and c[2] != "—")
    if not horas:
        return f"{len(abertas)} · idade não verificável (sem data)"
    antes = dt.datetime.fromisoformat(horas[0]).replace(tzinfo=agora.tzinfo)
    return f"{len(abertas)} · a mais antiga {idade(antes, agora)} ({horas[0]})"


def ultima_versao(ctx, raiz, agora):
    dados = lido(ctx, raiz, "release", "view", "--json", "tagName,publishedAt")
    if not isinstance(dados, dict) or not dados.get("tagName"):
        raise NaoVerificavel("resposta fora da forma")
    return f"{dados['tagName']} {idade(instante(dados.get('publishedAt')), agora)} ({dados.get('publishedAt')})"


def plugin_da_sessao(ctx, raiz, agora):
    return ctx["versao"]() or "não verificável (plugin.json ilegível)"


ITENS = (("último merge na develop", ultimo_merge), ("PRs abertos", prs_abertos), ("contador da versão", contador),
         ("decisões do dono abertas", decisoes), ("última versão publicada", ultima_versao),
         ("plugin da sessão", plugin_da_sessao))


def executar(a, raiz, ctx):
    """Imprime as seis linhas e sai com 0; `a.agora` (ISO 8601 com fuso) fixa o relógio, senão vale a hora local."""
    try:
        agora = instante(a.agora) if a.agora else dt.datetime.now().astimezone()
    except NaoVerificavel:
        agora = None
    if agora is None or agora.tzinfo is None:
        print("status: --agora ilegível ou sem fuso (use, por exemplo, 2026-11-26T10:00-03:00)")
        return 2
    for nome, ler in ITENS:
        try:
            texto = ler(ctx, Path(raiz), agora)
        except NaoVerificavel as erro:
            texto = f"não verificável ({erro})"
        print(ctx["seguro"](f"status: {nome}: {texto}"))
    return 0
