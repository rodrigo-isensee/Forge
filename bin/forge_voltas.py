"""Forge: `forge-check voltas` (T-1, M13) e `forge-check esperas` (M14b) (FILA-31 F6, 0.45.7 E5.4): o vai e volta de cada pedido e
quanto tempo cada cartão esperou o dono ou uma credencial, lidos de docs/kanban, docs/briefs e docs/pedidos. Só leitura, sem rede, só
biblioteca padrão.

Importado pelo `bin/forge-check` só quando um desses dois roda. `ctx` traz do forge-check os nomes que ele divide com `retro`, `medida`,
`transcricao custo` e o quadro (`_sem_acento`, `_ler_tabela`, `_hora`, `_minutos`, `_numero`, `ISO8601`, `rodadas_de_brief`,
`relogios_do_cartao`, `tipo_da_espera`, `linhas_da_secao`, `cartoes_do_pedido`, `nome_seguro` e `sem_controle`).
"""
import datetime
import sys
from pathlib import Path


# ---- voltas (T-1, M13): o vai e volta lido do disco, só leitura ----
RANGO_DA_COLUNA = {"em andamento": 1, "conferencia": 2, "review": 3}  # colunas em que voltar é andar para trás


def classificar_volta(de, para, motivo, ctx):
    """Tipo da volta de uma transição do quadro, por padrão fixo de colunas e motivo; None se não é volta;
    `nao-classificado` se anda para trás fora do vocabulário (nunca some)."""
    _sem_acento = ctx["_sem_acento"]
    d, p, m = _sem_acento(de), _sem_acento(para), _sem_acento(motivo)
    if d == "conferencia" and p == "review":
        return "conferencia" if "nao cumpriu" in m else "revalidacao" if "revalida" in m else None
    if d == "review" and "reprov" in m:
        return "review"
    if d == "em andamento" and p == "aguardando o dono" and ("barrad" in m or "hook" in m):
        return "barrada"
    if d in RANGO_DA_COLUNA and p in RANGO_DA_COLUNA and RANGO_DA_COLUNA[p] < RANGO_DA_COLUNA[d]:
        return "nao-classificado"
    return None


TIPOS_DE_VOLTA = ("brief", "conferencia", "review", "revalidacao", "barrada", "nao-classificado")


def _fecha_volta(coluna, de, para, ctx):
    """A volta que saiu de `coluna` termina quando o cartão chega a ela; no fluxo paralelo (VV-4) o cartão sai de Em
    andamento direto para Review e nunca passa por Conferência: aí a volta termina nessa chegada a Review, ou na
    entrada em QA ou Integração."""
    _sem_acento = ctx["_sem_acento"]
    d, p = _sem_acento(de), _sem_acento(para)
    if p == coluna or p in ("qa", "integracao"):
        return True
    return coluna == "conferencia" and p == "review" and d not in ("conferencia", "review")


def voltas_do_cartao(movimentos, ctx):
    """De [(hora, de, para, motivo)] em ordem de hora: ([(tipo, hora, minutos|None)], minutos de construção|None).
    Minutos da volta: da linha dela até a próxima do cartão que volta à coluna de onde ela saiu, ou que fecha o fluxo
    paralelo (`_fecha_volta`) (None: ainda aberta);
    saída da mesma coluna dentro de uma volta dela ainda aberta não abre outra (a janela é uma só).
    Construção: da primeira entrada em Em andamento até a primeira saída dele para a Conferência."""
    _sem_acento, _minutos = ctx["_sem_acento"], ctx["_minutos"]
    voltas, abertas = [], {}  # abertas: coluna de saída -> hora em que a volta que saiu dela termina (None: aberta)
    for i, (hora, de, para, motivo) in enumerate(movimentos):
        tipo = classificar_volta(de, para, motivo, ctx)
        if tipo:
            coluna = _sem_acento(de)
            if coluna in abertas and (abertas[coluna] is None or hora < abertas[coluna]):
                continue  # mesma saída já contada: a janela é uma só
            volta = next((h for h, d2, p, _ in movimentos[i + 1:] if _fecha_volta(coluna, d2, p, ctx)), None)
            abertas[coluna] = volta
            voltas.append((tipo, hora, _minutos(hora, volta) if volta else None))
    inicio = next((h for h, _, p, _ in movimentos if _sem_acento(p) == "em andamento"), None)
    fim = next((h for h, d, p, _ in movimentos if inicio and h >= inicio and _sem_acento(d) == "em andamento"
                and _sem_acento(p) == "conferencia"), None)
    return voltas, (_minutos(inicio, fim) if inicio and fim else None)


META_PRONTO_ATE_DEVELOP = 30  # minutos (D-4)


def _uniao_de_minutos(janelas):
    """Minutos da união de [(inicio, fim)]: janelas que se sobrepõem contam uma vez."""
    total, fim = 0.0, None
    for ini, f in sorted(janelas):
        if fim is None or ini >= fim:
            total += (f - ini).total_seconds() / 60
        elif f > fim:
            total += (f - fim).total_seconds() / 60
        fim = f if fim is None or f > fim else fim
    return round(total, 1)


def reversoes_do_pedido(arquivo, ctx):
    """L11 (OK-6): quantas linhas do `## Histórico` do pedido dizem `suposição revertida`; 0 se o pedido não abre. Só leitura."""
    _sem_acento, linhas_da_secao = ctx["_sem_acento"], ctx["linhas_da_secao"]
    try:
        texto = Path(arquivo).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return sum(1 for linha in linhas_da_secao(texto, "Histórico") if "suposicao revertida" in _sem_acento(linha))


def cmd_voltas(raiz, pedido, ctx):
    """Imprime as voltas por pedido (linhas fixas, números e tipos). Só lê docs/kanban/historico.md, conferencias.md,
    docs/briefs e docs/pedidos."""
    _ler_tabela, _hora, ISO8601, _numero = ctx["_ler_tabela"], ctx["_hora"], ctx["ISO8601"], ctx["_numero"]
    rodadas_de_brief, relogios_do_cartao = ctx["rodadas_de_brief"], ctx["relogios_do_cartao"]
    historico = raiz / "docs" / "kanban" / "historico.md"
    if not historico.is_file():
        print("voltas: aviso: docs/kanban/historico.md ausente", file=sys.stderr)
    else:
        try:
            historico.read_text(encoding="utf-8", errors="replace")
        except OSError as erro:
            print(f"voltas: docs/kanban/historico.md ilegivel ({erro.strerror or erro}); nada medido", file=sys.stderr)
            return 1
    por_cartao, nomes = {}, {}
    for c in _ler_tabela(historico):
        hora = _hora(c[0]) if len(c) >= 5 and ISO8601.match(c[0]) else None
        if hora:
            por_cartao.setdefault(c[1].casefold(), []).append((hora, c[2], c[3], "|".join(c[4:])))
            nomes.setdefault(c[1].casefold(), c[1])
    pasta = raiz / "docs" / "pedidos"
    pedidos = {p.stem.casefold(): p.stem for p in pasta.glob("*.md")} if pasta.is_dir() else {}
    pedidos.update(nomes)
    if pedido and pedido.casefold() not in pedidos and not rodadas_de_brief(raiz, pedido)["total"]:
        print(f"voltas: pedido {pedido} nao existe (nem em docs/pedidos/ nem no historico)", file=sys.stderr)
        return 1
    escolhidos = [pedido.casefold()] if pedido else sorted(pedidos)
    pedidos.setdefault(pedido.casefold() if pedido else "", pedido or "")
    soma = [0, 0, 0.0]
    for chave in escolhidos:
        voltas, construcao = voltas_do_cartao(sorted(por_cartao.get(chave, []), key=lambda m: m[0]), ctx)
        rodadas = rodadas_de_brief(raiz, chave)
        linhas = [("brief", h, m, f" ref={o}") for o, _r, h, m in rodadas["extras"]] + \
                 [(t, h.isoformat(timespec="seconds"), m, "") for t, h, m in voltas]
        relogios = relogios_do_cartao(sorted(por_cartao.get(chave, []), key=lambda m: m[0]))  # L49 (D-4): os dois relógios
        if not linhas and not pedido and not relogios:
            continue  # o pedido que andou sem volta segue na lista pelo relógio
        nome, contagem = pedidos[chave], {t: 0 for t in TIPOS_DE_VOLTA}
        for tipo, inicio, minutos, ref in linhas:
            contagem[tipo] += 1
            print(f"voltas: {nome} {tipo} inicio={inicio or 'sem-hora'} minutos="
                  f"{_numero(minutos) if minutos is not None else 'sem-hora' if inicio is None else 'aberta'}{ref}")
        janelas = [(_hora(h.replace(" ", "T")), m, True) for _, _, h, m in rodadas["extras"] if h and m is not None]
        janelas += [(h, m, False) for _, h, m in voltas if m is not None]
        total = _uniao_de_minutos([(j[0] - datetime.timedelta(minutes=j[1]), j[0]) if j[2] else (j[0], j[0] + datetime.timedelta(minutes=j[1]))
                                   for j in janelas if j[0]])
        razao = f"{total / construcao:.2f}" if construcao else "-"
        print(f"voltas: {nome} resumo: " + " ".join(f"{t}={n}" for t, n in contagem.items())
              + f" minutos={_numero(total)} construcao={_numero(construcao) if construcao is not None else '-'} razao={razao}")
        if relogios:
            aberto, pronto = relogios
            dentro = "-" if pronto is None else "sim" if pronto <= META_PRONTO_ATE_DEVELOP else "nao"
            print(f"voltas: {nome} relogios: aberto_ate_develop={_numero(aberto)} pronto_ate_develop="
                  f"{_numero(pronto) if pronto is not None else '-'} meta={META_PRONTO_ATE_DEVELOP} dentro={dentro}")
        if reversoes := reversoes_do_pedido(pasta / f"{nome}.md", ctx):  # L11 (OK-6): o placar da escolha provisória revertida pelo dono
            print(f"voltas: {nome} reversoes={reversoes}")
        soma = [soma[0] + 1, soma[1] + len(linhas), soma[2] + total]
    print(f"voltas: total: pedidos={soma[0]} voltas={soma[1]} minutos={_numero(soma[2])}")
    return 0


# ---- M14b: esperas (quanto tempo um cartão ficou parado esperando o dono ou uma credencial), lidas de historico.md ----
TIPOS_DE_ESPERA = ("dono", "credencial", "outra")


def esperas_do_cartao(movimentos, ctx):
    """De [(hora, de, para, motivo)] em ordem de hora: [(tipo, hora, minutos|None)]. A espera começa no movimento que a abre e termina
    no primeiro movimento seguinte que não a continua (None: ainda aberta). Continua a espera o movimento que sai de uma espera de um
    tipo para outra coluna do mesmo tipo (Em andamento -> Aguardando o dono, depois Aguardando o dono -> Bloqueado com o motivo
    "Aguardando o dono: ...") e esse movimento não abre outra."""
    tipo_da_espera, _minutos = ctx["tipo_da_espera"], ctx["_minutos"]
    def continua(m, tipo):
        return tipo_da_espera(m[1]) == tipo and tipo_da_espera(m[2], m[3]) == tipo
    esperas = []
    for i, movimento in enumerate(movimentos):
        tipo = tipo_da_espera(movimento[2], movimento[3])
        if tipo is None or tipo_da_espera(movimento[1]) == tipo:
            continue
        j = i + 1
        while j < len(movimentos) and continua(movimentos[j], tipo):
            j += 1
        fim = movimentos[j][0] if j < len(movimentos) else None
        esperas.append((tipo, movimento[0], _minutos(movimento[0], fim) if fim else None))
    return esperas


def cmd_esperas(raiz, pedido, kanban, ctx):
    """Imprime as esperas por cartão (`esperas: <cartão> <tipo> inicio=<ISO> minutos=<n|aberta>`) e o total por tipo. Só lê
    docs/kanban/historico.md. Com `--pedido`, só os cartões do pedido (o casamento de `cartoes_do_pedido`, com o motivo do movimento também) e a lista deles. rc 1 se o pedido não tem cartão."""
    _ler_tabela, _hora, ISO8601, _numero = ctx["_ler_tabela"], ctx["_hora"], ctx["ISO8601"], ctx["_numero"]
    cartoes_do_pedido, nome_seguro, sem_controle = ctx["cartoes_do_pedido"], ctx["nome_seguro"], ctx["sem_controle"]
    por_cartao, nomes = {}, {}
    for c in _ler_tabela(raiz / "docs" / "kanban" / "historico.md"):
        hora = _hora(c[0]) if len(c) >= 5 and ISO8601.match(c[0]) else None
        if hora:
            por_cartao.setdefault(c[1].casefold(), []).append((hora, c[2], c[3], "|".join(c[4:])))
            nomes.setdefault(c[1].casefold(), c[1])
    if not por_cartao:
        print("esperas: aviso: docs/kanban/historico.md ausente ou sem movimento com hora", file=sys.stderr)
    escolhidos = sorted(nomes.values(), key=str.casefold)
    if pedido:
        motivos = {n: [m[3] for m in ms] for n, ms in por_cartao.items()}
        escolhidos = cartoes_do_pedido(raiz, pedido, escolhidos, kanban, motivos)
        if not escolhidos:
            print(f"esperas: pedido {nome_seguro(sem_controle(pedido))} sem cartão no histórico (cartão igual, da mesma família de nome, com o pedido na coluna Pedido do KANBAN.md ou no motivo do movimento)")
            return 1
        print(f"esperas: pedido {nome_seguro(sem_controle(pedido))} cartoes: " + " ".join(sem_controle(n) for n in escolhidos))
    soma = {t: [0, 0.0] for t in TIPOS_DE_ESPERA}
    abertas = 0
    for nome in escolhidos:
        for tipo, inicio, minutos in esperas_do_cartao(sorted(por_cartao[nome.casefold()], key=lambda m: m[0]), ctx):
            print(f"esperas: {sem_controle(nome)} {tipo} inicio={inicio.isoformat(timespec='seconds')} minutos={_numero(minutos) if minutos is not None else 'aberta'}")
            soma[tipo][0] += 1
            soma[tipo][1] += minutos or 0
            abertas += minutos is None
    print("esperas: total: " + " ".join(f"{t}={soma[t][0]} minutos_{t}={_numero(soma[t][1])}" for t in TIPOS_DE_ESPERA)
          + f" abertas={abertas} cartoes={len(escolhidos)}")
    return 0

