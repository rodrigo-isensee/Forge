"""Forge: `forge-check medida` (D12, E3a e E3b) e `forge-check escape registrar|resumo` (M14b) (FILA-31 F6, 0.45.7 E5.5): a medida de um
tópico mesclado, gravada em docs/kanban/medidas.md com o aviso de piora da release, e o defeito escapado, registrado e resumido em
docs/kanban/escapes.md. Só biblioteca padrão, sem rede.

Importado pelo `bin/forge-check` só quando um desses roda. `ctx` traz do forge-check os nomes que ele divide com `voltas`, `retro`,
`esperas`, o quadro e o parser (`git`, `_hora`, `_minutos`, `_numero`, `_sem_acento`, `_ler_tabela`, `_tabela_segura`, `ISO8601`,
`HORA_DO_REGISTRO`, `ID_DE_PEDIDO`, `SEM_QUADRO`, `caminho_impresso`, `acrescentar_ao_arquivo`, `tipo_da_espera`, `recusa_do_campo` e
os valores aceitos de `escape registrar`, que o parser também usa: `ACHADO_POR`, `GRAVIDADES`, `CONTROLES_QUE_FALTARAM`, `ORIGENS` e
`SEM_ORIGEM`; a janela padrão do `escape resumo`, `JANELA_DE_ESCAPES`, fica no forge-check, no parser).
"""
import datetime
import re
import statistics
import sys


# ---- D12 (E3a): a medida de um tópico mesclado, gravada em docs/kanban/medidas.md; aviso, nunca trava ----
TOPICO_PEQUENO = 300  # linhas alteradas (adições mais remoções) abaixo das quais o tópico é pequeno
CABECALHO_DE_MEDIDAS = ("| data-hora | pedido | merge | ativo_min (historico.md) | linhas (git diff) | pequeno | tokens (entregas.md) |\n"
                        "|---|---|---|---|---|---|---|\n")


def tempo_ativo(movimentos, fim, ctx):
    """Minutos do primeiro movimento [(hora, de, para, motivo)] até `fim`, menos cada trecho aberto por um movimento que põe o cartão
    na espera do dono ou traz `espera deliberada:` no motivo (o trecho vai até o movimento seguinte); None sem movimento até `fim`."""
    _minutos, tipo_da_espera, _sem_acento = ctx["_minutos"], ctx["tipo_da_espera"], ctx["_sem_acento"]
    antes = [m for m in movimentos if m[0] <= fim]
    if not antes:
        return None
    fins = [m[0] for m in antes[1:]] + [fim]
    parados = sum(_minutos(m[0], ate) for m, ate in zip(antes, fins)
                  if tipo_da_espera(m[2], m[3]) == "dono" or _sem_acento(m[3]).startswith("espera deliberada:"))
    return round(_minutos(antes[0][0], fim) - parados, 1)


def tokens_do_pedido(raiz, pedido, ctx):
    """A soma da coluna tokens das linhas do pedido em docs/kanban/entregas.md, ou `lacuna:<motivo>` (nunca um zero sem fonte)."""
    _tabela_segura = ctx["_tabela_segura"]
    arq = raiz / "docs" / "kanban" / "entregas.md"
    linhas, aviso = _tabela_segura(arq)
    if aviso or not arq.is_file():
        return "lacuna:entregas.md-ilegivel" if aviso else "lacuna:sem-entregas.md"
    valores = [c[3] for c in linhas if len(c) >= 4 and c[1].casefold() == pedido.casefold()]
    if not valores:
        return "lacuna:sem-linha-do-pedido"
    if not all(re.fullmatch(r"[0-9]+", v) for v in valores):
        return "lacuna:tokens-nao-numericos"
    return str(sum(int(v) for v in valores))


def cmd_medida(raiz, pedido, merge, ctx):
    """Grava em docs/kanban/medidas.md a linha do tópico (tempo ativo até a data de commit do merge, linhas de `<merge>^1..<merge>`,
    tokens) e imprime o aviso de piora da release (E3b) ou `medida: só tabela (n=<tópicos pequenos da release atual>)`. rc 0; entrada recusada,
    rc 2, sem gravar. O `--merge` só chega ao git como sha40 minúsculo e depois de `--end-of-options`."""
    git, _hora, _numero, _ler_tabela, ISO8601 = ctx["git"], ctx["_hora"], ctx["_numero"], ctx["_ler_tabela"], ctx["ISO8601"]
    ID_DE_PEDIDO, SEM_QUADRO, caminho_impresso = ctx["ID_DE_PEDIDO"], ctx["SEM_QUADRO"], ctx["caminho_impresso"]
    acrescentar_ao_arquivo = ctx["acrescentar_ao_arquivo"]
    arq = raiz / "docs" / "kanban" / "medidas.md"
    recusa = ("--pedido fora de [A-Za-z0-9._-]" if not ID_DE_PEDIDO.fullmatch(pedido) or not pedido.strip(".")
              else "--merge não é um sha40 minúsculo" if not re.fullmatch(r"[0-9a-f]{40}", merge)
              else SEM_QUADRO.format(cmd="medida", raiz=caminho_impresso(raiz)) if not (raiz / "KANBAN.md").is_file()
              else "docs/kanban/medidas.md é link simbólico; não escrevo através dele" if arq.is_symlink() else None)
    cod, data = git(raiz, "log", "-1", "--format=%cI", "--end-of-options", merge) if recusa is None else (1, "")
    fim = _hora(data) if not cod and ISO8601.match(data) else None
    if recusa or fim is None:
        print(f"medida: {recusa or 'commit do --merge ausente no repositório'}; nada gravado", file=sys.stderr)
        return 2
    movimentos = sorted((h, c[2], c[3], "|".join(c[4:])) for c in _ler_tabela(raiz / "docs" / "kanban" / "historico.md")
                        if len(c) >= 5 and c[1].casefold() == pedido.casefold() and ISO8601.match(c[0]) and (h := _hora(c[0])))
    ativo = tempo_ativo(movimentos, fim, ctx)
    cod, stat = git(raiz, "diff", "--shortstat", "--end-of-options", f"{merge}^1", merge)
    linhas = None if cod else sum(int(n) for n in re.findall(r"(\d+) (?:insertion|deletion)", stat))
    celulas = (datetime.datetime.now().astimezone().isoformat(timespec="seconds"), pedido, merge,
               "lacuna:sem-movimento" if ativo is None else _numero(ativo), "lacuna:git-diff" if linhas is None else str(linhas),
               "-" if linhas is None else "sim" if linhas < TOPICO_PEQUENO else "nao", tokens_do_pedido(raiz, pedido, ctx))
    acrescentar_ao_arquivo(arq, "| " + " | ".join(celulas) + " |\n", CABECALHO_DE_MEDIDAS)
    print("| " + " | ".join(celulas) + " |")
    atual, anterior, tags = releases_da_medida(raiz, _ler_tabela(arq), ctx)
    print("\n".join(piora_da_release(atual, anterior, tags, ctx)) or f"medida: só tabela (n={len(atual)})")
    return 0


def releases_da_medida(raiz, linhas, ctx):
    """D12 (E3b): os tópicos pequenos de medidas.md, um por merge (vale a última medida), separados pelas tags v* (git local):
    a release atual é o merge que nenhuma tag contém; a anterior, o que a última tag (por versão) contém e a penúltima não."""
    git = ctx["git"]
    tags = git(raiz, "tag", "--list", "v*", "--sort=-v:refname")[1].split()
    atual, anterior = [], []
    for sha, c in {c[2]: c for c in linhas if len(c) >= 7 and re.fullmatch(r"[0-9a-f]{40}", c[2])}.items():
        cod, saida = git(raiz, "tag", "--list", "v*", f"--contains={sha}")
        dentro = set(saida.split())
        if cod or c[5] != "sim":
            continue
        if not dentro:
            atual.append(c)
        elif tags[0] in dentro and (len(tags) < 2 or tags[1] not in dentro):
            anterior.append(c)
    return atual, anterior, tags


def piora_da_release(atual, anterior, tags, ctx):
    """D12 (E3b, item 2): um aviso por métrica cuja mediana na release atual (3 ou mais tópicos com número) sobe mais de 20% sobre
    a da anterior e em que pelo menos 2 tópicos passam do maior valor dela; célula `lacuna:` fica fora. Nunca trava."""
    _numero = ctx["_numero"]
    for col, nome in ((3, "tempo ativo (min, historico.md)"), (6, "tokens novos (entregas.md)")):
        agora, antes = ([float(c[col]) for c in grupo if re.fullmatch(r"[0-9]+(\.[0-9]+)?", c[col])] for grupo in (atual, anterior))
        if len(agora) < 3 or not antes:
            continue
        m0, m1, teto = statistics.median(antes), statistics.median(agora), max(antes)
        acima = sum(1 for v in agora if v > teto)
        if m1 > 1.2 * m0 and acima >= 2:
            yield (f"medida: aviso: piora no {nome}: mediana {_numero(m0)} → {_numero(m1)} (limite +20%: {_numero(1.2 * m0)}), "
                   f"{acima} tópicos acima do maior da anterior ({_numero(teto)}); n={len(agora)} contra {len(antes)}; "
                   f"fonte: docs/kanban/medidas.md, release atual (sem tag v*) contra {tags[0]}")


# ---- M14b: defeito escapado (bug achado depois do parecer final), registrado em docs/kanban/escapes.md ----
CABECALHO_ESCAPES = ("| data-hora | pedido | parecer-final | achado-por | gravidade | controle-que-faltou | nota | origem |\n"
                     "|---|---|---|---|---|---|---|---|\n")


def origem_do_escape(celulas, ctx):
    """A origem de uma linha de `escapes.md`: a 8.ª coluna; a linha antiga (7 colunas) ou com valor fora de ORIGENS é `nao-classificado`."""
    ORIGENS, SEM_ORIGEM = ctx["ORIGENS"], ctx["SEM_ORIGEM"]
    return celulas[7] if len(celulas) >= 8 and celulas[7] in ORIGENS else SEM_ORIGEM


def cmd_escape_registrar(raiz, pedido, parecer_final, achado_por, gravidade, controle, nota, origem, ctx):
    """Registra um defeito escapado em docs/kanban/escapes.md: uma linha de formato fixo com a hora real `AAAA-MM-DD HH:MM`. Só acrescenta;
    cria o arquivo com o cabeçalho se faltar. `parecer_final` é o parecer (caminho em docs/reviews, qa... ou commit) depois do qual o bug
    apareceu; `controle` é o que deveria tê-lo achado (`nenhum` se nenhum controle existente alcançava); `origem` é a fase onde o defeito
    nasceu (`ORIGENS`, padrão `nao-classificado`; a coluna vai depois da `nota`, para a linha antiga seguir válida). Recusa sem gravar; a recusa cita o
    campo, nunca o valor."""
    recusa_do_campo, ID_DE_PEDIDO, SEM_QUADRO = ctx["recusa_do_campo"], ctx["ID_DE_PEDIDO"], ctx["SEM_QUADRO"]
    caminho_impresso, ACHADO_POR, GRAVIDADES = ctx["caminho_impresso"], ctx["ACHADO_POR"], ctx["GRAVIDADES"]
    CONTROLES_QUE_FALTARAM, ORIGENS = ctx["CONTROLES_QUE_FALTARAM"], ctx["ORIGENS"]
    campos = (("--pedido", pedido), ("--parecer-final", parecer_final), ("--nota", nota))
    for nome, valor in campos:
        if "|" in valor or re.search(r"[\x00-\x1f\x7f]", valor) or len(valor.splitlines()) > 1:
            return [f"escape: {nome} não pode ter `|` nem quebra de linha"]
        motivo = recusa_do_campo(valor, nome)
        if motivo:
            return [f"escape: {motivo}"]
    pedido, parecer_final, nota = pedido.strip(), parecer_final.strip(), nota.strip()
    if not ID_DE_PEDIDO.fullmatch(pedido) or not parecer_final or not nota:
        return ["escape: --pedido (letras, números, `.`, `_` e `-`), --parecer-final e --nota não podem ser vazios"]
    for nome, valor, validos in (("--achado-por", achado_por, ACHADO_POR), ("--gravidade", gravidade, GRAVIDADES),
                                 ("--controle-que-faltou", controle, CONTROLES_QUE_FALTARAM), ("--origem", origem, ORIGENS)):
        if valor not in validos:
            return [f"escape: {nome} deve ser um de {', '.join(validos)}"]
    if not (raiz / "KANBAN.md").is_file():
        return [SEM_QUADRO.format(cmd="escape", raiz=caminho_impresso(raiz))]
    arq = raiz / "docs" / "kanban" / "escapes.md"
    if arq.is_symlink():
        return ["escape: docs/kanban/escapes.md é link simbólico; não escrevo através dele"]
    arq.parent.mkdir(parents=True, exist_ok=True)
    existe = arq.is_file() and arq.stat().st_size > 0
    falta_quebra = False
    if existe:
        with arq.open("rb") as f:
            f.seek(-1, 2)
            falta_quebra = f.read(1) != b"\n"
    hora = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    linha = f"| {hora} | {pedido} | {parecer_final} | {achado_por} | {gravidade} | {controle} | {nota} | {origem} |\n"
    with arq.open("a", encoding="utf-8") as f:
        if not existe:
            f.write(CABECALHO_ESCAPES)
        elif falta_quebra:
            f.write("\n")
        f.write(linha)
    return [linha.rstrip("\n")]


def cmd_escape_resumo(raiz, dias, agora, ctx):
    """Conta os escapes dos últimos `dias` por gravidade e por controle que faltou, e a taxa sobre os pedidos que chegaram a "Pronto" na
    mesma janela (`docs/kanban/historico.md`). Só leitura; sem escapes registrados a taxa é 0, e sem pedido pronto, `-`."""
    _ler_tabela, HORA_DO_REGISTRO, _hora, ISO8601 = ctx["_ler_tabela"], ctx["HORA_DO_REGISTRO"], ctx["_hora"], ctx["ISO8601"]
    _sem_acento, GRAVIDADES = ctx["_sem_acento"], ctx["GRAVIDADES"]
    CONTROLES_QUE_FALTARAM, ORIGENS = ctx["CONTROLES_QUE_FALTARAM"], ctx["ORIGENS"]
    agora = agora or datetime.datetime.now().astimezone()
    inicio = agora - datetime.timedelta(days=dias)
    escapes = []
    for c in _ler_tabela(raiz / "docs" / "kanban" / "escapes.md"):
        if len(c) >= 7 and HORA_DO_REGISTRO.fullmatch(c[0]):
            hora = _hora(c[0].replace(" ", "T"))
            if hora and hora >= inicio:
                escapes.append(c)
    prontos = {c[1].casefold() for c in _ler_tabela(raiz / "docs" / "kanban" / "historico.md")
               if len(c) >= 5 and ISO8601.match(c[0]) and _sem_acento(c[3]) == "pronto" and (_hora(c[0]) or agora) >= inicio}
    print("escapes: gravidade: " + " ".join(f"{g}={sum(1 for e in escapes if e[4] == g)}" for g in GRAVIDADES))
    print("escapes: controle: " + " ".join(f"{k}={sum(1 for e in escapes if e[5] == k)}" for k in CONTROLES_QUE_FALTARAM))
    print("escapes: origem: " + " ".join(f"{o}={sum(1 for e in escapes if origem_do_escape(e, ctx) == o)}" for o in ORIGENS))
    taxa = f"{len(escapes) / len(prontos):.2f}" if prontos else "-"
    print(f"escapes: total: escapes={len(escapes)} pedidos_prontos={len(prontos)} taxa={taxa} dias={dias}")
    return 0
