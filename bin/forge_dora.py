"""Forge: DORA e vazão (0.45.7, TM-16): `forge-check dora`, só leitura, sem rede, só biblioteca padrão.

Dá só o que `voltas`, `esperas` e `metricas` ainda não dão (o lead por item do Histórico fica no `metricas`):
- frequência de entrega: releases (tags `vX.Y.Z` do git) por semana ISO;
- espera da mudança: horas do commit (data de autor, sem merges) até a release que o publicou (`anterior..tag`);
- taxa de falha: releases com ao menos um escape (docs/kanban/escapes.md) até a release seguinte, sobre as releases;
- recuperação: horas do escape até a release seguinte (`abertas`: escapes sem release depois);
- vazão: cartões que chegaram a "Pronto" em docs/kanban/historico.md (o primeiro movimento de cada um), por semana ISO.
Abaixo de MINIMO_PARA_RESUMO valores, a saída traz os números brutos e nenhuma taxa, média ou percentil. Linha do quadro
incompleta (sem cartão, coluna vazia, data ilegível ou sem fuso) não entra na conta e sai `recusado` com o motivo."""
import datetime
import json
import re
import statistics

from forge_governanca import git, ler_texto, periodo_de, sem_acento

MINIMO_PARA_RESUMO = 20
TAG_DE_VERSAO = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
COMECA_COM_DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
FONTES = ("frequencia e espera_da_mudanca: tags vX.Y.Z e commits do git; taxa_de_falha e recuperacao: docs/kanban/escapes.md "
          "contra as releases; vazao: docs/kanban/historico.md; lead por item, voltas e esperas: metricas, voltas e esperas")


class SemFuso(ValueError):
    pass


def releases(raiz):
    """([(tag, data)] das tags `vX.Y.Z` em ordem de versão, [avisos])."""
    rc, saida = git(raiz, "for-each-ref", "--format=%(refname:short)%09%(creatordate:iso-strict)", "refs/tags")
    if rc != 0:
        return [], ["git não leu as tags; frequência, espera, falha e recuperação sem release"]
    lista = []
    for linha in saida.splitlines():
        nome, _, data = linha.partition("\t")
        if achou := TAG_DE_VERSAO.fullmatch(nome):
            lista.append((tuple(map(int, achou.groups())), nome, datetime.datetime.fromisoformat(data)))
    return [(nome, data) for _, nome, data in sorted(lista)], []


def esperas_da_mudanca(raiz, lista, janela):
    """Horas de cada commit sem merge de `anterior..tag` até a data da tag, das releases dentro da janela."""
    horas = []
    for (anterior, _), (tag, data) in zip(lista, lista[1:]):
        if not janela(data):
            continue
        _, saida = git(raiz, "log", "--no-merges", "--format=%aI", f"{anterior}..{tag}")
        horas += [round((data - datetime.datetime.fromisoformat(d)).total_seconds() / 3600, 2) for d in saida.split()]
    return horas


def iso_com_fuso(texto):
    data = datetime.datetime.fromisoformat(texto)
    if data.tzinfo is None:
        raise SemFuso
    return data


def linhas_do_quadro(arq, colunas, ler_data):
    """[(número da linha, data, células)] das linhas de tabela que começam por data, e [(fonte, cartão, motivo)] das recusadas:
    data que `ler_data` não lê ou alguma das `colunas` primeiras células vazia."""
    boas, recusadas = [], []
    for n, linha in enumerate((ler_texto(arq) or "").splitlines(), 1):
        c = [x.strip() for x in linha.strip().strip("|").split("|")] + [""] * colunas
        if not linha.lstrip().startswith("|") or not COMECA_COM_DATA.match(c[0]):
            continue
        motivo = None
        try:
            data = ler_data(c[0])
        except SemFuso:
            motivo = "data-hora sem fuso"
        except ValueError:
            motivo = "data-hora ilegível"
        if motivo is None and not all(c[1:colunas]):
            motivo = "coluna vazia ou faltando"
        if motivo is None:
            boas.append((n, data, c))
        else:
            recusadas.append((f"{arq.name}:{n}", c[1] or "-", motivo))
    return boas, recusadas


def vazao(raiz_pedidos, janela):
    """({semana: cartões}, recusadas): cada cartão conta uma vez, na semana do primeiro movimento para "Pronto"."""
    boas, recusadas = linhas_do_quadro(raiz_pedidos / "docs" / "kanban" / "historico.md", 4, iso_com_fuso)
    primeiro = {}
    for _, data, c in boas:
        cartao = c[1].casefold()
        if sem_acento(c[3]) == "pronto" and data < primeiro.get(cartao, data + datetime.timedelta(seconds=1)):
            primeiro[cartao] = data
    semanas = {}
    for data in filter(janela, primeiro.values()):
        semanas[periodo_de(data, "semana")] = semanas.get(periodo_de(data, "semana"), 0) + 1
    return dict(sorted(semanas.items())), recusadas


def falhas(raiz_pedidos, lista, janela, fuso):
    """(releases com escape, horas de recuperação, abertas, recusadas). O escape cai na última release até a hora dele."""
    def ler(texto):
        return datetime.datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=fuso)
    boas, recusadas = linhas_do_quadro(raiz_pedidos / "docs" / "kanban" / "escapes.md", 2, ler)
    com_falha, horas, abertas = set(), [], 0
    for n, data, c in filter(lambda b: janela(b[1]), boas):
        ultima = next((nome for nome, d in reversed(lista) if d <= data), None)
        if ultima is None:
            recusadas.append((f"escapes.md:{n}", c[1], "escape antes da primeira release"))
            continue
        com_falha.add(ultima)
        seguinte = next((d for _, d in lista if d > data), None)
        if seguinte is None:
            abertas += 1
            continue
        horas.append(round((seguinte - data).total_seconds() / 3600, 2))
    return com_falha, horas, abertas, recusadas


def resumir(valores):
    """Abaixo de MINIMO_PARA_RESUMO, os brutos; a partir dele, p50 e p90."""
    if len(valores) < MINIMO_PARA_RESUMO:
        return {"n": len(valores), "brutos": sorted(valores)}
    return {"n": len(valores), "p50": round(statistics.median(valores), 2), "p90": round(statistics.quantiles(valores, n=10)[8], 2)}


def por_semana(semanas):
    """Contagem por semana: os brutos sempre; a média por semana com ao menos uma, só com MINIMO_PARA_RESUMO ou mais."""
    r = {"n": sum(semanas.values()), "semanas": semanas}
    if r["n"] >= MINIMO_PARA_RESUMO:
        r["media_por_semana"] = round(r["n"] / len(semanas), 2)
    return r


def calcular(raiz, raiz_pedidos, desde=None, ate=None, fuso=None):
    fuso = fuso or datetime.datetime.now().astimezone().tzinfo

    def janela(data):
        dia = data.astimezone(fuso).date()
        return (desde is None or dia >= desde) and (ate is None or dia <= ate)
    lista, avisos = releases(raiz)
    na_janela = [d for _, d in lista if janela(d)]
    freq = {}
    for d in na_janela:
        freq[periodo_de(d, "semana")] = freq.get(periodo_de(d, "semana"), 0) + 1
    com_falha, recuperacao, abertas, recusadas = falhas(raiz_pedidos, lista, janela, fuso)
    semanas, mais = vazao(raiz_pedidos, janela)
    taxa = {"entregas": len(na_janela), "com_falha": len(com_falha)}
    if len(na_janela) >= MINIMO_PARA_RESUMO:
        taxa["taxa_pct"] = round(100 * len(com_falha) / len(na_janela), 1)
    return {"frequencia": por_semana(dict(sorted(freq.items()))), "espera_da_mudanca_h": resumir(esperas_da_mudanca(raiz, lista, janela)),
            "taxa_de_falha": taxa, "recuperacao_h": {**resumir(recuperacao), "abertas": abertas}, "vazao": por_semana(semanas),
            "recusados": [{"fonte": f, "cartao": c, "motivo": m} for f, c, m in recusadas + mais], "avisos": avisos}


def linhas_de_texto(dados):
    """Uma linha por medida (`chave=valor`, valor em JSON compacto), uma por recusado e por aviso, e as fontes."""
    def campos(d):
        return " ".join(f"{k}={json.dumps(v, ensure_ascii=False, separators=(',', ':'))}" for k, v in d.items())
    saida = [f"dora: {nome} {campos(dados[nome])}" for nome in ("frequencia", "espera_da_mudanca_h", "taxa_de_falha", "recuperacao_h", "vazao")]
    saida += [f"dora: recusado {r['fonte']} {r['cartao']} motivo: {r['motivo']}" for r in dados["recusados"]]
    saida += [f"dora: aviso: {a}" for a in dados["avisos"]]
    return saida + [f"dora: fontes: {FONTES}; abaixo de {MINIMO_PARA_RESUMO} valores, os números brutos"]


def executar(a, raiz, raiz_pedidos):
    """rc 0 (data e fuso já validados pelo argparse do forge-check, que sai com rc 2)."""
    dados = calcular(raiz, raiz_pedidos, a.desde, a.ate, a.fuso)
    print(json.dumps(dados, ensure_ascii=False, indent=1) if a.json else "\n".join(linhas_de_texto(dados)))
    return 0
