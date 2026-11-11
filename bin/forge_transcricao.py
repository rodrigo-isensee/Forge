"""Forge: `forge-check transcricao lastro|vereditos|decisoes|avisos` (FILA-31 F6, 0.45.7 E5.2): a linha de base da proteção contra
alucinação (M1, M3, P7) e os avisos dos hooks (L2), medidos sobre as transcrições locais, sem IA e sem rede. Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um desses quatro roda. `ctx` traz do forge-check os nomes que ele divide com
`transcricao custo`, `recusas` e `trava` (`objetos_jsonl`, `transcricoes_do_alvo`, `caminho_impresso`) e com o `escape resumo` (`taxa`).
"""
import hashlib
import json
import re
import sys


# ---- transcricao lastro / decisoes: a linha de base da proteção contra alucinação (M1 e M3), sem IA e sem rede ----
RE_SHA = re.compile(r"(?<![0-9A-Za-z])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![0-9A-Za-z])")
RE_PR = re.compile(r"(?<![0-9A-Za-z&])#(\d{1,6})(?!\d)")
RE_PUSH = re.compile(r"\bpush\b[^.\n]{0,25}\b(?:aceito|entrou|enviado|feito|realizado|passou)\b|\benviei\b[^.\n]{0,25}\b(?:branch|origin)\b", re.I)
RE_MESCLADO = re.compile(r"\bmescl(?:ado|ada|ei|ou)\b|\bmerged\b", re.I)
RE_TESTES = re.compile(r"\b(\d{1,6})\s+(?:testes?|tests?)\b[^.\n]{0,20}\b(?:ok|passa\w*|verdes?|passed)\b|\bok\s*\((\d{1,6})\s+tests?\)|\b(\d{1,6})\s+OK\b", re.I)
RE_NEGACAO = re.compile(r"\b(?:n[ãa]o|sem|nunca)\b", re.I)
# L12 (OK-5): afirmação absoluta sobre testes ou falhas; só medida, o lastro é uma saída de teste que terminou OK.
RE_ABSOLUTA = re.compile(r"\btodos os testes (?:passa\w*|est[ãa]o verdes|ficaram verdes)\b|\btudo verde\b|\b100\s?%\s+dos testes\b|"
                         r"\bnenhum(?:a)? (?:falha|erro|regress[ãa]o|teste (?:falha|falhou|quebr\w+))\b", re.I)
# Saída de `git push`; a de `git fetch` tem o mesmo formato, mas o destino é `origin/...`.
RE_SAIDA_PUSH = re.compile(r"\.\.\S+\s+\S+\s+->\s+(?!origin/)\S+|\[new (?:branch|tag)\]")


def sem_negacao(texto, achado):
    """Falso se a ocorrência vem negada ("não mesclei", "o push não passou") na mesma frase."""
    inicio = max(texto.rfind(".", 0, achado.start()), texto.rfind("\n", 0, achado.start()), achado.start() - 30)
    return RE_NEGACAO.search(texto[inicio + 1:achado.end()]) is None


def afirmacoes_do_relatorio(texto):
    """Afirmações verificáveis do texto: conjunto de (tipo, valor); `valor` é o que deve aparecer nas saídas.
    Em "mesclado", `valor` são os PRs citados no relatório (separados por vírgula; vazio se nenhum)."""
    achadas = {("sha", m.group(0)) for m in RE_SHA.finditer(texto)}
    prs = sorted({m.group(1) for m in RE_PR.finditer(texto)}, key=int)
    achadas |= {("pr", n) for n in prs}
    if any(sem_negacao(texto, m) for m in RE_PUSH.finditer(texto)):
        achadas.add(("push", ""))
    if any(sem_negacao(texto, m) for m in RE_MESCLADO.finditer(texto)):
        achadas.add(("mesclado", ",".join(prs)))
    achadas |= {("testes", m.group(1) or m.group(2) or m.group(3)) for m in RE_TESTES.finditer(texto)}
    if any(sem_negacao(texto, m) for m in RE_ABSOLUTA.finditer(texto)):
        achadas.add(("absoluta", ""))
    return achadas


def merge_provado(numero, saidas):
    """Prova positiva de merge: objeto JSON do PR com state MERGED ou mergedAt não nulo, ou a saída de `gh pr merge`.
    `numero` vazio vale para qualquer PR. `"mergedAt": null` e "Merge pull request" de `git log` não provam."""
    n = re.escape(numero) if numero else r"\d+"
    for obj in re.finditer(r"\{[^{}]*\}", saidas):
        o = obj.group(0)
        if re.search(rf'"number": ?{n}(?!\d)', o) and re.search(r'"state": ?"MERGED"|"mergedAt": ?"\d', o):
            return True
    return re.search(rf"\bmerged pull request #{n}(?!\d)", saidas, re.I) is not None


def testes_ok(numero, saidas):
    """`Ran N tests` seguido de `OK` (sem FAILED), `OK (N tests)` ou `N passed` sem `failed` na linha."""
    if re.search(rf"\bRan {numero} tests?\b[^\n]*\n\s*OK\b|\bOK \({numero} tests?\)", saidas):
        return True
    return any(re.search(rf"\b{numero} (?:passed|tests? passed)\b", l) and not re.search(r"fail", l, re.I)
               for l in saidas.splitlines())


def tem_lastro(afirmacao, saidas):
    tipo, valor = afirmacao
    if tipo == "sha":
        return valor in saidas
    if tipo == "pr":
        return re.search(rf"#{valor}(?!\d)|pull/{valor}(?!\d)|\"number\": ?{valor}(?!\d)", saidas) is not None
    if tipo == "push":
        return RE_SAIDA_PUSH.search(saidas) is not None
    if tipo == "mesclado":
        return any(merge_provado(n, saidas) for n in (valor.split(",") if valor else [""]))
    if tipo == "absoluta":
        return testes_ok(r"\d+", saidas)
    return testes_ok(valor, saidas)


def textos_do_conteudo(conteudo):
    if isinstance(conteudo, str):
        return [conteudo]
    return [b["text"] for b in conteudo if isinstance(b, dict) and isinstance(b.get("text"), str)] if isinstance(conteudo, list) else []


def ler_relatorios(arquivos, ctx):
    """Por subagente (sessão + agentId): o relatório final e o texto de todas as saídas de ferramenta sem erro.
    Devolve {sessão: [(relatório, saídas)]}; nenhum texto sai daqui para a impressão."""
    objetos_jsonl = ctx["objetos_jsonl"]
    agentes, ordem = {}, {}
    for o in objetos_jsonl(arquivos, "lastro"):
        agente = o.get("agentId")
        msg = o.get("message") if isinstance(o.get("message"), dict) else {}
        if not o.get("isSidechain") or not isinstance(agente, str):
            continue
        sessao = o.get("sessionId") if isinstance(o.get("sessionId"), str) else ""
        ordem.setdefault(sessao, f"s{len(ordem) + 1}")
        reg = agentes.setdefault((sessao, agente), {"saidas": [], "texto": "", "id": None, "entregue": ""})
        blocos = msg.get("content") if isinstance(msg.get("content"), list) else []
        if o.get("type") == "assistant":
            textos = [t for b in blocos if isinstance(b, dict) and b.get("type") == "text" for t in textos_do_conteudo([b])]
            if textos:
                reg["texto"] = (reg["texto"] + "\n" if reg["id"] == msg.get("id") else "") + "\n".join(textos)
                reg["id"] = msg.get("id")
            for b in blocos:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback" \
                        and isinstance(b.get("input"), dict) and isinstance(b["input"].get("message"), str):
                    reg["entregue"] = b["input"]["message"]
        elif o.get("type") == "user":
            for b in blocos:
                if isinstance(b, dict) and b.get("type") == "tool_result" and not b.get("is_error"):
                    reg["saidas"] += textos_do_conteudo(b.get("content"))
    saida = {}
    for (sessao, _), reg in agentes.items():
        relatorio = reg["entregue"] or reg["texto"]
        if relatorio:
            saida.setdefault(ordem[sessao], []).append((relatorio, "\n".join(reg["saidas"])))
    return saida


def medir_lastro(relatorios):
    """{sessão: (relatórios, afirmações, sem lastro)}."""
    medida = {}
    for sessao, itens in relatorios.items():
        total = sem = 0
        for relatorio, saidas in itens:
            for afirmacao in afirmacoes_do_relatorio(relatorio):
                total += 1
                sem += 0 if tem_lastro(afirmacao, saidas) else 1
        medida[sessao] = (len(itens), total, sem)
    return medida


RE_VEREDITO = re.compile(r"^\s*veredito:\s*(n[ãa]o cumpriu|cumpriu)\s*$", re.I | re.M)
# As linhas que reprovam no conferente.md: PQ não cumpriu, pendente:, escopo: que não seja ok, confira nem as que o entrega imprime sem reprovar
# (integração da base, sem commit, união de N briefs), forma: que não seja ok.
RE_LINHA_REPROVADA = re.compile(r"^\s*(?:PQ-\d+\s+n[ãa]o cumpriu\b|pendente:|escopo:\s*(?!ok\b|confira\b|integração da base|sem commit|união de \d+ briefs)\S|forma:\s*(?!ok\b)\S)", re.I | re.M)


def medir_vereditos(relatorios):
    """L13 (P7): {sessão: (relatórios com `veredito:`, os que contradizem as próprias linhas)}. `cumpriu` com linha `PQ-n não cumpriu`,
    `pendente:`, `forma:` ou `escopo:` que reprova (não `ok`, `confira`, integração da base, sem commit nem união de N briefs), ou `não cumpriu` sem nenhuma delas, é contradição. Só mede; nada do texto sai daqui."""
    medida = {}
    for sessao, itens in relatorios.items():
        total = contraditorios = 0
        for relatorio, _ in itens:
            vereditos = RE_VEREDITO.findall(relatorio)
            if not vereditos:
                continue
            total += 1
            cumpriu = not vereditos[-1].lower().startswith("n")
            contraditorios += 1 if cumpriu == (RE_LINHA_REPROVADA.search(relatorio) is not None) else 0
        medida[sessao] = (total, contraditorios)
    return medida


HOOKS_DE_AVISO, EVENTOS_DE_AVISO = ("doutor", "vigia"), ("Stop", "SubagentStop")


def hook_do_aviso(texto):
    """L2: o hook pelo prefixo exato que ele imprime (`linha` de hooks/doutor.py; o fim da linha de hooks/vigia.py); None se é de outro."""
    if texto.startswith("Forge doutor:"):
        return "doutor"
    if texto.startswith("Forge: ") and texto.endswith("(.forge/run/violacoes.jsonl)"):
        return "vigia"
    return None


JANELA_DE_ACAO = 3


def acao_do_bloco(b):
    """L2 (E4b): o bloco do assistente age sobre o aviso: lê `.forge/run/violacoes.jsonl`, roda `forge doutor` ou `bin/forge-doutor`, ou cita o vigia ou o doutor."""
    if b.get("type") == "text":
        return any(nome in str(b.get("text")).lower() for nome in ("vigia", "doutor"))
    entrada = json.dumps(b.get("input"), ensure_ascii=False)  # só o tool_use tem `input`
    return any(alvo in entrada for alvo in (".forge/run/violacoes.jsonl", "forge doutor", "bin/forge-doutor"))


def avisos_dos_hooks(arquivos, ctx):
    """L2 (LAC-L2): ({(hook, evento, dia, hash): vezes}, [[id, hook, com ação]]) dos `hook_system_message` do `doutor` e do `vigia`. Evento fora de Stop e
    SubagentStop vira `outro`; dia ilegível, `sem_data`. O texto só se casa e vira hash interno, que nunca sai daqui (T-14). O id `s<n>#<i>` é
    determinístico (n: posição do arquivo na lista ordenada; i: ordem do aviso nele); a ação conta nas JANELA_DE_ACAO chamadas seguintes do arquivo (E4b)."""
    objetos_jsonl = ctx["objetos_jsonl"]
    vezes, lista, abertos, atual = {}, [], [], 0  # abertos: [aviso, chamadas que faltam na janela]
    for n, o in ((n, o) for n, arq in enumerate(arquivos, 1) for o in objetos_jsonl([arq], "avisos")):
        if n != atual:
            abertos, i, atual = [], 0, n
        msg = o.get("message") if isinstance(o.get("message"), dict) else {}
        for b in msg.get("content") if o.get("type") == "assistant" and isinstance(msg.get("content"), list) else []:
            b = b if isinstance(b, dict) else {}
            acao = acao_do_bloco(b)
            for aberto in abertos:
                aberto[0][2] = aberto[0][2] or acao
                aberto[1] -= b.get("type") == "tool_use"
            abertos = [a for a in abertos if a[1] > 0]
        anexo = o.get("attachment") if isinstance(o.get("attachment"), dict) else {}
        texto = anexo.get("content")
        if o.get("type") != "attachment" or anexo.get("type") != "hook_system_message" or not isinstance(texto, str):
            continue
        hook = hook_do_aviso(texto)
        if hook is None:
            continue
        evento = anexo.get("hookEvent") if anexo.get("hookEvent") in EVENTOS_DE_AVISO else "outro"
        dia = str(o.get("timestamp"))[:10]
        dia = dia if re.fullmatch(r"\d{4}-\d{2}-\d{2}", dia) else "sem_data"
        chave = (hook, evento, dia, hashlib.sha256(texto.encode("utf-8", "replace")).digest())
        vezes[chave] = vezes.get(chave, 0) + 1
        i += 1
        lista.append([f"s{n}#{i}", hook, False])
        abertos.append([lista[-1], JANELA_DE_ACAO])
    return vezes, lista


def cmd_transcricao_avisos(alvo, raiz, amostra, ctx):
    """`transcricao avisos`: avisos do `doutor` e do `vigia` por hook, evento e dia, únicos e reincidência no mesmo dia. Só números."""
    transcricoes_do_alvo, caminho_impresso = ctx["transcricoes_do_alvo"], ctx["caminho_impresso"]
    try:
        arquivos, onde = transcricoes_do_alvo(alvo, raiz)
    except OSError as erro:
        print(f"avisos: caminho inexistente: {caminho_impresso(erro.filename or alvo)}")
        return 1
    if not arquivos:
        print(f"avisos: nenhum arquivo .jsonl em {caminho_impresso(onde)}")
        return 1
    print(f"avisos: vai ler {len(arquivos)} arquivo(s) .jsonl em {caminho_impresso(onde)}; só disco local, sem rede; "
          "a saída traz só números, nunca o texto do aviso", file=sys.stderr)
    (vezes, lista), no_dia = avisos_dos_hooks(arquivos, ctx), {}
    for (hook, _, dia, h), n in vezes.items():
        no_dia[(hook, dia, h)] = no_dia.get((hook, dia, h), 0) + n
    soma = [0, 0, 0]
    for hook in HOOKS_DE_AVISO:
        valores = [sum(n for k, n in vezes.items() if k[0] == hook), len({k[3] for k in vezes if k[0] == hook}),
                   sum(n - 1 for k, n in no_dia.items() if k[0] == hook)]
        print(f"avisos: hook {hook} avisos={valores[0]} unicos={valores[1]} reincidencia={valores[2]}")
        soma = [a + b for a, b in zip(soma, valores)]
    for i, rotulo in ((1, "evento"), (2, "dia")):
        for valor in sorted({k[i] for k in vezes}):
            print(f"avisos: {rotulo} {valor} " + " ".join(
                f"{hook}={sum(n for k, n in vezes.items() if k[0] == hook and k[i] == valor)}" for hook in HOOKS_DE_AVISO))
    print(f"avisos: total: avisos={soma[0]} unicos={soma[1]} reincidencia={soma[2]}")
    print(f"avisos: com_acao={sum(1 for aviso in lista if aviso[2])}")
    for id_, hook, _ in lista[:max(amostra, 0)]:
        print(f"avisos: amostra {id_} {hook}")  # só id e o tipo do conjunto fechado, nunca o texto (T-14)
    return 0


RE_OPCAO = re.compile(r"^\s*(?:[-*+]\s+)?(\|\s*)?(?:\*\*\s*)?(Op[çc][ãa]o\s+)?([A-F])(\*\*)?\s*(?:([).:|,])(?:\*\*)?)?(?=\s|$)")
RE_RECOMENDO = re.compile(r"recomendo|recomenda[çc][ãa]o:", re.I)
RE_DECIDIDO = re.compile(r"^\s*(?:\*\*)?(?:Decidido|Escolhida):", re.I)


def sem_codigo_nem_citacao(texto):
    saida, em_codigo, em_provas = [], False, False
    for linha in texto.splitlines():
        if linha.lstrip().startswith("```"):
            em_codigo = not em_codigo
            continue
        if em_codigo or linha.lstrip().startswith(">"):
            continue
        if re.match(r"^\s*Provas:\s*$", linha):
            em_provas = True
            continue
        if em_provas and not linha.strip():
            em_provas = False
        if not em_provas:
            saida.append(linha)
    return saida


def grupos_de_opcoes(texto):
    """[(índice da linha onde começa, recomenda?)] dos grupos de opções A/B/C (>= 2 opções) fora de código e citação."""
    linhas = sem_codigo_nem_citacao(texto)
    opcoes, pergunta = [], False
    for i, linha in enumerate(linhas):
        tabela = linha.lstrip().startswith("|")
        if not tabela and linha.strip():
            pergunta = "?" in linha
        m = RE_OPCAO.match(linha)
        if m and (m.group(2) or m.group(4) or m.group(5)) and not (m.group(1) and not pergunta):
            opcoes.append((i, m.group(3)))
    grupos, atual = [], []
    for i, letra in opcoes:
        if letra == "A":
            grupos.append(atual)
            atual = []
        if letra == "A" or atual:
            atual.append((i, letra))
    grupos.append(atual)
    saida = []
    for g in (g for g in grupos if len(g) >= 2):
        if any(RE_DECIDIDO.match(l) for l in linhas[g[-1][0] + 1:g[-1][0] + 4]):
            continue
        saida.append((g[0][0], RE_RECOMENDO.search("\n".join(linhas[g[0][0]:])) is not None))
    return saida


def ler_respostas_do_jarvis(arquivos, ctx):
    """{sessão: [texto da resposta final de cada turno]} da sessão principal (fora de subagentes)."""
    objetos_jsonl = ctx["objetos_jsonl"]
    ordem, respostas, ultimo = {}, {}, {}
    for o in objetos_jsonl(arquivos, "decisoes"):
        if o.get("isSidechain") or o.get("type") not in ("assistant", "user"):
            continue
        sessao = o.get("sessionId") if isinstance(o.get("sessionId"), str) else ""
        rotulo = ordem.setdefault(sessao, f"s{len(ordem) + 1}")
        respostas.setdefault(rotulo, [])
        msg = o.get("message") if isinstance(o.get("message"), dict) else {}
        blocos = msg.get("content")
        if o["type"] == "assistant":
            textos = [b["text"] for b in blocos if isinstance(b, dict) and b.get("type") == "text"
                      and isinstance(b.get("text"), str)] if isinstance(blocos, list) else []
            if textos:
                antes = ultimo.get(rotulo)
                junto = (antes[1] + "\n" if antes and antes[0] == msg.get("id") else "") + "\n".join(textos)
                ultimo[rotulo] = (msg.get("id"), junto)
        elif not (isinstance(blocos, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in blocos)):
            if rotulo in ultimo:  # um pedido novo do usuário fecha o turno
                respostas[rotulo].append(ultimo.pop(rotulo)[1])
    for rotulo, texto in ultimo.items():
        respostas[rotulo].append(texto[1])
    return respostas


def medir_decisoes(respostas):
    """{sessão: (respostas, com grupo, com violação)}: violação = mais de um grupo ou grupo sem `Recomendo`."""
    medida = {}
    for sessao, textos in respostas.items():
        com_grupo = violacoes = 0
        for t in textos:
            grupos = grupos_de_opcoes(t)
            com_grupo += bool(grupos)
            violacoes += len(grupos) > 1 or any(not recomenda for _, recomenda in grupos)
        medida[sessao] = (len(textos), com_grupo, violacoes)
    return medida


def cmd_transcricao_medida(rotulo, alvo, ler, medir, campos, den, raiz, ctx):
    """Anuncia (stderr), lê e imprime uma linha por sessão e o total, só com números. `campos`: nomes das colunas."""
    transcricoes_do_alvo, caminho_impresso, taxa = ctx["transcricoes_do_alvo"], ctx["caminho_impresso"], ctx["taxa"]
    try:
        arquivos, onde = transcricoes_do_alvo(alvo, raiz)
    except OSError as erro:
        print(f"{rotulo}: caminho inexistente: {caminho_impresso(erro.filename or alvo)}")
        return 1
    if not arquivos:
        print(f"{rotulo}: nenhum arquivo .jsonl em {caminho_impresso(onde)}")
        return 1
    print(f"{rotulo}: vai ler {len(arquivos)} arquivo(s) .jsonl em {caminho_impresso(onde)}; só disco local, sem rede; "
          "a saída traz só números, nunca texto, nome ou caminho", file=sys.stderr)
    medida = medir(ler(arquivos, ctx))
    soma = [0] * len(campos)
    for sessao, valores in sorted(medida.items(), key=lambda x: int(x[0][1:])):
        print(f"{rotulo}: sessao {sessao}: " + " ".join(f"{c}={v}" for c, v in zip(campos, valores))
              + f" taxa={taxa(valores[-1], valores[den])}")
        soma = [a + b for a, b in zip(soma, valores)]
    print(f"{rotulo}: total: sessoes={len(medida)} " + " ".join(f"{c}={v}" for c, v in zip(campos, soma))
          + f" taxa={taxa(soma[-1], soma[den])}")
    return 0


MEDIDAS = {"lastro": (ler_relatorios, medir_lastro, ("relatorios", "afirmacoes", "sem_lastro"), 1),
           "vereditos": (ler_relatorios, medir_vereditos, ("vereditos", "contraditorios"), 0),
           "decisoes": (ler_respostas_do_jarvis, medir_decisoes, ("respostas", "com_grupo", "violacoes"), 0)}


def executar(a, raiz, ctx):
    """O subcomando `transcricao <acao>` deste grupo; devolve o código de saída."""
    if a.acao == "avisos":
        return cmd_transcricao_avisos(a.alvo, raiz, a.amostra, ctx)
    return cmd_transcricao_medida(a.acao, a.alvo, *MEDIDAS[a.acao], raiz, ctx)
