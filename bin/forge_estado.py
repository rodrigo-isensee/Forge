"""Forge: `forge-check status` (S1a, v0481 E20.1): o estado da fábrica lido na hora, para o Jarvis nunca afirmar estado de memória.
Só leitura, sem `git fetch`. Seis linhas `status:`: último merge na develop (`gh api .../commits/develop`); PRs abertos por grupo
(rótulo do dono: título com `afrouxa-regra` sem o rótulo; quebrado: check reprovado); 1.ª linha do `bin/forge-contador`; decisões do
dono abertas (`forge_dono.cmd_abertas`); `gh release view`; o plugin.json deste forge-check. Leitura que falha vira `não verificável
(<motivo>)`, nunca erro: rc 0. A única escrita (F4, v0481 E34.6): a lista `prs-abertos.json` que o hook `vigia` lê sem rede,
com o papel a disparar em cada PR (`papel_do_pr`); o PR de fork, o que espera só o dono e o que espera o CI ficam fora."""
import datetime as dt
import os
import subprocess
import sys
import time
from pathlib import Path

QUEBRADO = {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
PENDENTE = {"QUEUED", "IN_PROGRESS", "PENDING", "WAITING", "REQUESTED", "EXPECTED"}
CHECK_DE_PARECER, CHECKS_DE_PORTAO = "bateria (pareceres)", {"bateria (pareceres)", "bateria", "catraca"}
PORTOES = (("docs/reviews/", "review"), ("docs/qa/", "QA"), ("docs/security/", "segurança"))
ROTULO_DO_DONO = "afrouxa-regra"
CAMPOS_DO_PR = "number,title,mergeable,labels,statusCheckRollup,headRefName,baseRefName,isCrossRepository,files"
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


def _objetos(valor):
    """Os objetos de uma lista lida do `gh`; o resto, e o que não é lista, fica de fora."""
    return [v for v in valor if isinstance(v, dict)] if isinstance(valor, list) else []


def papel_do_pr(pr):
    """O papel a disparar no PR aberto, ou None quando ele é de fork (`isCrossRepository` verdadeiro ou ausente: a dúvida
    cala) ou espera só o dono (base `main`, rótulo) ou o CI."""
    if pr.get("isCrossRepository") is not False or pr.get("baseRefName") == "main":
        return None
    if pr.get("mergeable") == "CONFLICTING":
        return "autor"
    checks = _objetos(pr.get("statusCheckRollup"))
    falhos = {c.get("name") for c in checks if (c.get("conclusion") or c.get("state")) in QUEBRADO}
    if falhos - CHECKS_DE_PORTAO:
        return "autor"
    if any((c.get("status") or c.get("state")) in PENDENTE for c in checks):
        return None
    if CHECK_DE_PARECER in falhos:
        arquivos = [str(f.get("path")) for f in _objetos(pr.get("files"))]
        faltam = [papel for pasta, papel in PORTOES if not any(a.startswith(pasta) for a in arquivos)]
        return "/".join(faltam) or "autor"
    rotulos = {r.get("name") for r in _objetos(pr.get("labels"))}
    if ROTULO_DO_DONO in (pr.get("title") or "") and ROTULO_DO_DONO not in rotulos:
        return None
    return "autor" if falhos else "integração"


def vigia():
    """O hook `vigia` (dono do nome, do prazo e da leitura da lista), importado de hooks/ com o `agentes`, que ele importa na hora."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
    try:
        import agentes  # noqa: F401 - fica em sys.modules para o `import agentes` tardio do vigia
        import vigia as modulo
    finally:
        sys.path.remove(str(Path(__file__).resolve().parent.parent / "hooks"))
    return modulo


def gravar_prs_abertos(caminho, prs, agora_s):
    """Grava a lista do vigia, só com o PR que tem papel, de forma atômica e modo 0600; sem a pasta de estado, nada.
    Erro de escrita (pasta sem escrita, disco cheio, diretório no caminho) não sobe: o `status` sai com rc 0 e, no
    `proximo`, a falha não muda nada; o vigia segue com a lista que já havia."""
    if caminho is None or not caminho.parent.is_dir():
        return
    itens = [{"number": p["number"], "head": p.get("headRefName"), "papel": papel} for p in prs if (papel := papel_do_pr(p))]
    try:
        vigia().gravar_json(caminho, {"versao": 1, "gravado_em": int(agora_s), "prs": itens[:100]})
        os.chmod(caminho, 0o600)
    except OSError:  # a lista é só apoio do aviso: a gravação falha calada, sem deixar o temporário do gravar_json
        try:
            caminho.with_name(f"{caminho.name}.{os.getpid()}.tmp").unlink(missing_ok=True)
        except OSError:
            pass  # pasta sem escrita: o temporário nem chegou a existir


def renovar_prs_abertos(raiz, gh_json):
    """`forge-check proximo`: com a pasta de estado e a lista ausente ou vencida, uma leitura do `gh` e a gravação; falha não muda nada."""
    modulo = vigia()
    caminho = modulo.lista_de_prs(raiz)
    try:
        if caminho is None or not caminho.parent.is_dir() or time.time() - os.stat(caminho).st_mtime <= modulo.PRAZO_DA_LISTA_S:
            return
    except FileNotFoundError:
        pass
    prs = gh_json(raiz, "pr", "list", "--state", "open", "--limit", "100", "--json", CAMPOS_DO_PR)[0]
    if isinstance(prs, list) and all(isinstance(p, dict) and isinstance(p.get("number"), int) for p in prs):
        gravar_prs_abertos(caminho, prs, time.time())


def prs_abertos(ctx, raiz, agora):
    prs = lido(ctx, raiz, "pr", "list", "--state", "open", "--limit", "100", "--json", CAMPOS_DO_PR)
    if not isinstance(prs, list) or not all(isinstance(p, dict) and isinstance(p.get("number"), int) for p in prs):
        raise NaoVerificavel("resposta fora da forma")
    gravar_prs_abertos(ctx.get("lista_de_prs"), prs, agora.timestamp())
    grupos = [[] for _ in GRUPOS]
    for pr in prs:
        grupos[grupo_do_pr(pr)].append(f"#{pr['number']}")
    partes = [f"{nome} {len(g)}" + (f" ({' '.join(g)})" if g else "") for nome, g in zip(GRUPOS, grupos)]
    return f"{len(prs)} · " + " · ".join(partes)


def contador(ctx, raiz, agora):
    try:
        r = subprocess.run([sys.executable, "-I", str(ctx["plugin"] / "bin" / "forge-contador"), "--raiz", str(raiz)],
                           capture_output=True, text=True, timeout=TETO_DO_CONTADOR_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:  # DEVELOP-DO-GITHUB (v048 E14.1): o contador lê a develop do origin pela rede
        raise NaoVerificavel(f"TimeoutExpired: forge-contador passou de {TETO_DO_CONTADOR_S} s lendo a develop do "
                             "origin") from None
    except OSError as erro:
        raise NaoVerificavel(type(erro).__name__) from None
    if r.returncode != 0 or not r.stdout.strip():
        raise NaoVerificavel(" ".join((r.stderr or "forge-contador sem saída").split())[:160])
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
    antes = instante(horas[0]).replace(tzinfo=agora.tzinfo)  # data fora do calendário (2026-02-30): NaoVerificavel
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
