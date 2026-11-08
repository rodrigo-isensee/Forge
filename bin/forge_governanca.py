"""Forge: as medidas de governança do processo (0.43.1, frente H): `forge-check metricas` e `forge-check regras`.

`metricas` lê o `## Histórico` dos pedidos, o registro de conferências (docs/kanban/conferencias.md) e o git, e dá, por item e por
período: tempo do código pronto (primeira `entrega conferida <sha>`) até a develop e até a main (o merge da linha de primeiro pai que
trouxe o sha), voltas, revalidações, suítes e falhas, minutos de espera do dono e as reprovações por classe. O mérito das
reprovações é anotado pelo próprio Jarvis no registro: sai marcado `declarada`, nunca como medida.

`regras` lista cada docs/regras/R-*.md com os campos `Revisar em: AAAA-MM-DD` e `Medida:` (o número que justifica a regra); falta,
data vencida ou medida sem número dão aviso (rc 0); com `--estrito`, rc 1.

Só leitura, sem rede (o `gh` só com `--gh`), só biblioteca padrão. Uso em docs/governanca.md."""
import datetime
import json
import os
import re
import statistics
import subprocess
import sys
import unicodedata
from pathlib import Path

GIT_TIMEOUT_S = 10
GH_TIMEOUT_S = 20
ID_DE_PEDIDO = re.compile(r"[A-Za-z0-9._-]+")
TETO_DE_BYTES = 8_000_000  # arquivo maior não é lido (nada é contado e sai aviso)

# ---- Histórico: forma da linha e classes de evento (texto sem acento, minúsculo) ----
LINHA_DO_HISTORICO = re.compile(r"^- (\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}): (.*)$")
ITEM = re.compile(r"\bE\d+(?:[.-]\d+)*[a-z]?\b")
ITEM_NO_INICIO = re.compile(r"^\(([^)]*)\)")
CONFERIDA = re.compile(r"entrega conferida ([0-9a-f]{7,40})\b")
ITEM_DA_CONFERIDA = re.compile(r"entrega conferida [0-9a-f]{7,40} \(([^)]*)\)")
VOLTA = re.compile(r"nao cumpriu|reprovad[oa]s?\b|\breprovou\b")
REVALIDACAO = re.compile(r"revalid")
SUITE = re.compile(r"\bpush\b|\bsuite\b|\benvio\b")
SUITE_FALHOU = re.compile(r"\breprovou\b|\bfalhou\b|\brc [1-9]\b|nao passou")
SUITE_PASSOU = re.compile(r"\bpassou\b|\brc 0\b")
AO_DONO = re.compile(r"vai ao dono|vao ao dono|pergunta ao dono|levad[oa]s? ao dono|aguardando o dono"
                     r"|espera(?:ndo)? (?:a |da )?(?:decisao|resposta) do dono")
DO_DONO = re.compile(r"decisao do dono|ordem do dono")
HORA_ENTRE_PARENTESES = re.compile(r"(?:decisao|ordem) do dono \((\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2})\)")
PERGUNTA_REGISTRADA = re.compile(r"^pergunta ao dono \((\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2})\)")
DECISAO_REGISTRADA = re.compile(r"^(?:decisao|ordem) do dono \((\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2})\)")
BRANCH_CITADA = re.compile(r"\bmelhoria/[a-z0-9][a-z0-9._-]{0,80}")
COLUNAS_DO_REGISTRO = ("data-hora", "pedido", "brief", "modo", "rodada", "resultado", "merito", "nota", "classe", "autor")
REPROVACAO_NO_REGISTRO = re.compile(r"reprov|nao cumpriu")

# Como cada número foi obtido (vai na saída, para ninguém ler declaração como medida).
FONTES = {
    "pronto_ate_develop_h": "medida (hora do Histórico e data de commit do git)",
    "pronto_ate_main_h": "medida (hora do Histórico e data de commit do git)",
    "voltas": "contagem do Histórico (nao cumpriu, reprovado)",
    "revalidacoes": "contagem do Histórico (revalid)",
    "suites": "contagem do Histórico (push, suite ou envio com passou, reprovou, falhou ou rc)",
    "espera_dono_min": "estimada (do pedido ao dono até a DECISÃO/ORDEM DO DONO seguinte, sem sobreposição)",
    "reprovacoes_por_classe": "registro de conferências (classe anotada no registro)",
    "merito": "declarada (anotada pelo próprio Jarvis no registro; não é medida independente)",
    "ci": "gh run list da branch citada no item (só com --gh)",
}


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto)) if not unicodedata.combining(c)).casefold()


def ler_texto(arq):
    """Texto do arquivo, ou None se é link simbólico, não abre ou passa do teto de bytes. Só leitura."""
    try:
        if arq.is_symlink() or not arq.is_file() or arq.stat().st_size > TETO_DE_BYTES:
            return None
        return arq.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def secao(texto, nome):
    """Linhas da seção `## <nome>` (até o próximo `## `)."""
    linhas, dentro = [], False
    for linha in texto.splitlines():
        if linha.startswith("## "):
            dentro = sem_acento(linha[3:]).startswith(sem_acento(nome))
            continue
        if dentro:
            linhas.append(linha)
    return linhas


def hora(data, hh, mm, fuso):
    return datetime.datetime.fromisoformat(f"{data}T{hh}:{mm}").replace(tzinfo=fuso)


def item_da_linha(texto):
    """O item (E2-1, E3-1a, E2.2...) do primeiro parêntese da linha ou do parêntese que segue `entrega conferida <sha>`; None se
    a linha não cita item (vale para o pedido inteiro)."""
    for padrao in (ITEM_NO_INICIO, ITEM_DA_CONFERIDA):
        achou = padrao.search(texto)
        if achou and (item := ITEM.search(achou.group(1))):
            return item.group(0)
    return None


def eventos_do_pedido(texto, fuso):
    """[(hora, item|None, texto sem acento, texto original)] das linhas do Histórico, em ordem de hora."""
    eventos = []
    for linha in secao(texto, "Histórico"):
        achou = LINHA_DO_HISTORICO.match(linha.strip())
        if achou:
            data, hh, mm, resto = achou.groups()
            eventos.append((hora(data, hh, mm, fuso), item_da_linha(resto), sem_acento(resto), resto))
    return sorted(eventos, key=lambda e: e[0])


def classe_de_suite(texto):
    """`falhou`, `passou` ou None (a linha fala de push/suíte mas não diz o resultado, ou não fala)."""
    if not SUITE.search(texto):
        return None
    return "falhou" if SUITE_FALHOU.search(texto) else "passou" if SUITE_PASSOU.search(texto) else None


def uniao_em_minutos(janelas):
    """Minutos cobertos pela união das janelas [(inicio, fim)]."""
    total, fim = 0.0, None
    for ini, f in sorted(janelas):
        if fim is None or ini > fim:
            total += (f - ini).total_seconds() / 60
            fim = f
        elif f > fim:
            total += (f - fim).total_seconds() / 60
            fim = f
    return round(total, 1)


def esperas_do_dono(eventos, texto, fuso):
    """{item|None: [(inicio, fim)]}: do pedido ao dono (linha do Histórico ou PERGUNTA AO DONO registrada) até a primeira
    DECISÃO/ORDEM DO DONO seguinte (a hora entre parênteses, se houver; senão a da linha). Pedido sem resposta fica de fora."""
    respostas = []
    for h, _, s, _ in eventos:
        if DO_DONO.search(s):
            achou = HORA_ENTRE_PARENTESES.search(s)
            respostas.append(hora(*achou.groups(), fuso) if achou else h)
    perguntas = [(h, item) for h, item, s, _ in eventos if AO_DONO.search(s) and not DO_DONO.search(s)]
    for linha in secao(texto, "Decisões do usuário"):
        s = sem_acento(linha.strip().lstrip("- "))
        if achou := DECISAO_REGISTRADA.match(s):
            respostas.append(hora(*achou.groups(), fuso))
        elif achou := PERGUNTA_REGISTRADA.match(s):
            perguntas.append((hora(*achou.groups(), fuso), None))
    respostas.sort()
    janelas = {}
    for inicio, item in perguntas:
        fim = next((r for r in respostas if r >= inicio), None)
        if fim is not None:
            janelas.setdefault(item, []).append((inicio, fim))
    return janelas


# ---- git e gh ----
def git(raiz, *args):
    """(código, stdout sem espaços nas pontas); sem as variáveis GIT_* herdadas e com limite de tempo."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, env=env, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return r.returncode, r.stdout.strip()


class Chegada:
    """Quando um sha chegou a uma ref: o commit mais antigo da linha de primeiro pai da ref que o contém (o merge que o trouxe, ou o
    próprio sha num avanço rápido), achado por busca binária com `merge-base --is-ancestor` (conter é monotônico nessa linha). None se
    a ref não existe, o sha não existe ou não está na ref (ex.: squash)."""

    def __init__(self, raiz, ref):
        self.raiz, self.ref, self.cache = raiz, ref, {}
        cod, saida = git(raiz, "rev-list", "--first-parent", "--end-of-options", ref)
        self.linha = saida.split()[::-1] if not cod else None  # do mais antigo ao mais novo

    def __call__(self, sha):
        if self.linha is None or not re.fullmatch(r"[0-9a-f]{7,40}", sha):
            return None
        if sha not in self.cache:
            self.cache[sha] = self._chegada(sha)
        return self.cache[sha]

    def contem(self, sha, commit):
        return git(self.raiz, "merge-base", "--is-ancestor", sha, commit)[0] == 0

    def _chegada(self, sha):
        cod, cheio = git(self.raiz, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{sha}^{{commit}}")
        if cod or not self.linha or not self.contem(cheio, self.linha[-1]):
            return None
        baixo, alto = 0, len(self.linha) - 1
        while baixo < alto:
            meio = (baixo + alto) // 2
            if self.contem(cheio, self.linha[meio]):
                alto = meio
            else:
                baixo = meio + 1
        cod, data = git(self.raiz, "log", "-1", "--format=%cI", "--end-of-options", self.linha[baixo])
        return datetime.datetime.fromisoformat(data) if not cod and data else None


def ci_da_branch(branch):
    """(execuções, falhas) do CI da branch pelo `gh run list`, ou None se o gh falha (sem rede, sem login)."""
    try:
        r = subprocess.run(["gh", "run", "list", "--branch", branch, "--limit", "100", "--json", "conclusion"],
                           capture_output=True, text=True, timeout=GH_TIMEOUT_S)
        execucoes = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None
    if not isinstance(execucoes, list):
        return None
    concluidas = [e for e in execucoes if isinstance(e, dict) and e.get("conclusion")]
    return len(concluidas), sum(1 for e in concluidas if e["conclusion"] not in ("success", "skipped", "neutral"))


# ---- registro de conferências ----
def linhas_do_registro(raiz_pedidos):
    """[{data, pedido, resultado, merito, classe}] de docs/kanban/conferencias.md (colunas pelo cabeçalho); ([], aviso|None)."""
    arq = raiz_pedidos / "docs" / "kanban" / "conferencias.md"
    texto = ler_texto(arq)
    if texto is None:
        return [], (None if not arq.exists() else "conferencias.md ilegível, link simbólico ou grande demais")
    colunas, linhas = None, []
    for linha in texto.splitlines():
        if not linha.startswith("|"):
            continue
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        nomes = [sem_acento(c) for c in celulas]
        if "resultado" in nomes and "pedido" in nomes:
            colunas = {n.split(" ")[0]: i for i, n in enumerate(nomes)}
            for i, nome in enumerate(COLUNAS_DO_REGISTRO):  # classe e autor entraram depois, sem cabeçalho novo
                colunas.setdefault(nome, i if i >= len(nomes) else -1)
            continue
        if colunas is None or not re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", celulas[0]):
            continue
        valor = lambda nome: celulas[colunas[nome]] if 0 <= colunas.get(nome, -1) < len(celulas) else ""  # noqa: E731
        linhas.append({"data": celulas[0][:16], "pedido": valor("pedido"), "resultado": sem_acento(valor("resultado")),
                       "merito": sem_acento(valor("merito")).strip("—–- ") or "sem-merito", "classe": sem_acento(valor("classe")).strip("—–- ") or "sem-classe"})
    return linhas, None


def reprovacoes(linhas):
    """({classe: n}, {mérito: n}) das linhas reprovadas (`reprov` ou `não cumpriu`)."""
    classes, meritos = {}, {}
    for c in linhas:
        if REPROVACAO_NO_REGISTRO.search(c["resultado"]):
            classes[c["classe"]] = classes.get(c["classe"], 0) + 1
            meritos[c["merito"]] = meritos.get(c["merito"], 0) + 1
    return dict(sorted(classes.items())), dict(sorted(meritos.items()))


# ---- métricas ----
def horas_entre(a, b):
    return round((b - a).total_seconds() / 3600, 2) if a and b else None


def periodo_de(momento, por):
    if por == "semana":
        ano, semana, _ = momento.isocalendar()
        return f"{ano}-S{semana:02d}"
    return momento.date().isoformat()


def itens_do_pedido(pedido, texto, fuso, chegadas, agora, usar_gh, janela):
    """Um dicionário por item do Histórico (e um `-` com o que não cita item), com as medidas do item."""
    eventos = [e for e in eventos_do_pedido(texto, fuso) if janela(e[0])]
    esperas = esperas_do_dono(eventos, texto, fuso)
    itens = {}
    for h, item, s, original in eventos:
        d = itens.setdefault(item, {"pedido": pedido, "item": item or "-", "inicio": h, "conferidas": [], "voltas": 0,
                                    "revalidacoes": 0, "suites": 0, "suites_falhas": 0, "branches": set()})
        if achou := CONFERIDA.search(s):
            d["conferidas"].append((h, achou.group(1)))
        elif VOLTA.search(s) and not SUITE.search(s):
            d["voltas"] += 1
        if REVALIDACAO.search(s):
            d["revalidacoes"] += 1
        if resultado := classe_de_suite(s):
            d["suites"] += 1
            d["suites_falhas"] += resultado == "falhou"
        d["branches"].update(BRANCH_CITADA.findall(original))
    saida = []
    for item, d in itens.items():
        pronto, sha = (d["conferidas"][0][0], d["conferidas"][-1][1]) if d["conferidas"] else (None, None)
        develop, main = (chegadas[0](sha), chegadas[1](sha)) if sha else (None, None)
        registro = {"pedido": pedido, "item": d["item"], "periodo_base": (pronto or d["inicio"]),
                    "pronto": pronto.isoformat(timespec="minutes") if pronto else None, "sha": sha,
                    "develop": develop.isoformat(timespec="minutes") if develop else None,
                    "main": main.isoformat(timespec="minutes") if main else None,
                    "pronto_ate_develop_h": horas_entre(pronto, develop), "pronto_ate_main_h": horas_entre(pronto, main),
                    "aberto_h": horas_entre(pronto, agora) if pronto and not develop else None,
                    "voltas": d["voltas"], "revalidacoes": d["revalidacoes"], "suites": d["suites"],
                    "suites_falhas": d["suites_falhas"], "espera_dono_min": uniao_em_minutos(esperas.get(item, [])),
                    "branches": sorted(d["branches"])}
        if usar_gh:
            ci = [c for c in (ci_da_branch(b) for b in registro["branches"]) if c is not None]
            registro["ci"] = {"execucoes": sum(c[0] for c in ci), "falhas": sum(c[1] for c in ci)} if ci else "nao-medido"
        saida.append(registro)
    return sorted(saida, key=lambda r: (r["item"] == "-", r["periodo_base"]))


def resumo(itens, conferencias):
    tempos = [i["pronto_ate_develop_h"] for i in itens if i["pronto_ate_develop_h"] is not None]
    tempos_main = [i["pronto_ate_main_h"] for i in itens if i["pronto_ate_main_h"] is not None]
    classes, meritos = reprovacoes(conferencias)
    return {"itens_prontos": sum(1 for i in itens if i["pronto"]),
            "pronto_ate_develop_h_p50": round(statistics.median(tempos), 2) if tempos else None, "n_develop": len(tempos),
            "pronto_ate_main_h_p50": round(statistics.median(tempos_main), 2) if tempos_main else None, "n_main": len(tempos_main),
            "abertos": sum(1 for i in itens if i["pronto"] and not i["develop"]),
            "voltas": sum(i["voltas"] for i in itens), "revalidacoes": sum(i["revalidacoes"] for i in itens),
            "suites": sum(i["suites"] for i in itens), "suites_falhas": sum(i["suites_falhas"] for i in itens),
            "espera_dono_min": round(sum(i["espera_dono_min"] for i in itens), 1),
            "reprovacoes_por_classe": classes, "merito_declarado": meritos}


def calcular(raiz, raiz_pedidos, pedidos=None, desde=None, ate=None, por="dia", fuso=None, agora=None,
             develop="origin/develop", main="origin/main", usar_gh=False):
    """O dicionário completo das métricas (o que o `--json` imprime) e a lista de avisos."""
    fuso = fuso or datetime.datetime.now().astimezone().tzinfo
    agora = agora or datetime.datetime.now(fuso)
    pasta, avisos = raiz_pedidos / "docs" / "pedidos", []
    nomes = pedidos or (sorted(p.stem for p in pasta.glob("*.md")) if pasta.is_dir() else [])

    def janela(momento):
        return (desde is None or momento.date() >= desde) and (ate is None or momento.date() <= ate)

    chegadas = (Chegada(raiz, develop), Chegada(raiz, main))
    for ref, chegada in zip((develop, main), chegadas):
        if chegada.linha is None:
            avisos.append(f"ref {ref} ausente no git de {raiz}: tempos até ela saem nao-medido")
    conferencias, aviso = linhas_do_registro(raiz_pedidos)
    avisos += [aviso] if aviso else []
    conferencias = [c for c in conferencias if janela(datetime.datetime.fromisoformat(c["data"].replace(" ", "T")))]
    itens, por_pedido = [], []
    for nome in nomes:
        texto = ler_texto(pasta / f"{nome}.md") if ID_DE_PEDIDO.fullmatch(nome) and nome.strip(".") else None
        if texto is None:
            avisos.append(f"pedido {nome!r} ausente, fora de docs/pedidos/, link simbólico ou ilegível")
            continue
        doc = itens_do_pedido(nome, texto, fuso, chegadas, agora, usar_gh, janela)
        itens += doc
        registro = [c for c in conferencias if c["pedido"].casefold() == nome.casefold()]
        if doc or registro:
            por_pedido.append({"pedido": nome, **resumo(doc, registro)})
    periodos = {}
    for i in itens:
        periodos.setdefault(periodo_de(i["periodo_base"], por), []).append(i)
    conf_por_periodo = {}
    escolhidos = {n.casefold() for n in nomes}
    for c in conferencias:
        if c["pedido"].casefold() in escolhidos:
            momento = datetime.datetime.fromisoformat(c["data"].replace(" ", "T")).replace(tzinfo=fuso)
            conf_por_periodo.setdefault(periodo_de(momento, por), []).append(c)
    lista_periodos = [{"periodo": p, **resumo(periodos.get(p, []), conf_por_periodo.get(p, []))}
                      for p in sorted(set(periodos) | set(conf_por_periodo))]
    for i in itens:
        i.pop("periodo_base")
    return {"fontes": FONTES, "por": por, "itens": itens, "pedidos": por_pedido, "periodos": lista_periodos}, avisos


def _n(valor):
    return "nao-medido" if valor is None else f"{valor:g}" if isinstance(valor, float) else str(valor)


def _contagem(d):
    return ",".join(f"{k}={v}" for k, v in d.items()) or "-"


def linhas_de_texto(dados):
    saida = []
    for i in dados["itens"]:
        destino = _n(i["pronto_ate_develop_h"]) if i["develop"] else ("aberto" if i["pronto"] else "-")
        linha = (f"metricas: item {i['pedido']} {i['item']} pronto={i['pronto'] or '-'} develop_h={destino} "
                 f"main_h={_n(i['pronto_ate_main_h']) if i['main'] else ('aberto' if i['pronto'] else '-')} "
                 f"aberto_h={_n(i['aberto_h']) if i['aberto_h'] is not None else '-'} voltas={i['voltas']} "
                 f"revalidacoes={i['revalidacoes']} suites={i['suites']} falhas={i['suites_falhas']} espera_dono_min={_n(i['espera_dono_min'])}")
        if "ci" in i:
            linha += " ci=" + (f"{i['ci']['execucoes']}/{i['ci']['falhas']}" if isinstance(i["ci"], dict) else i["ci"])
        saida.append(linha)
    for chave, grupo in (("pedido", dados["pedidos"]), ("periodo", dados["periodos"])):
        for r in grupo:
            saida.append(f"metricas: {chave} {r[chave]} prontos={r['itens_prontos']} develop_h_p50={_n(r['pronto_ate_develop_h_p50'])}"
                         f"(n={r['n_develop']}) main_h_p50={_n(r['pronto_ate_main_h_p50'])}(n={r['n_main']}) abertos={r['abertos']} "
                         f"voltas={r['voltas']} revalidacoes={r['revalidacoes']} suites={r['suites']} falhas={r['suites_falhas']} "
                         f"espera_dono_min={_n(r['espera_dono_min'])} reprovacoes={_contagem(r['reprovacoes_por_classe'])} "
                         f"merito(declarada)={_contagem(r['merito_declarado'])}")
    saida.append("metricas: fontes: " + "; ".join(f"{k}={v}" for k, v in FONTES.items()))
    return saida


def cmd_metricas(raiz, raiz_pedidos, a):
    """Imprime as métricas em texto (linhas `metricas:`) ou em JSON. rc 0; entrada inválida, rc 2."""
    try:
        desde = datetime.date.fromisoformat(a.desde) if a.desde else None
        ate = datetime.date.fromisoformat(a.ate) if a.ate else None
        fuso = datetime.datetime.strptime(a.fuso, "%z").tzinfo if a.fuso else None
        agora = datetime.datetime.fromisoformat(a.agora) if a.agora else None
    except ValueError as erro:
        print(f"metricas: data, hora ou fuso inválido ({erro}); use AAAA-MM-DD, AAAA-MM-DDTHH:MM e ±HH:MM")
        return 2
    if agora is not None and agora.tzinfo is None:
        agora = agora.replace(tzinfo=fuso or datetime.datetime.now().astimezone().tzinfo)
    dados, avisos = calcular(raiz, raiz_pedidos, a.pedido, desde, ate, a.por, fuso, agora, a.develop, a.main, a.gh)
    for aviso in avisos:
        print(f"metricas: aviso: {aviso}", file=sys.stderr)
    print(json.dumps(dados, ensure_ascii=False, indent=1) if a.json else "\n".join(linhas_de_texto(dados)))
    return 0


# ---- validade das regras ----
REVISAR_EM = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?revisar em:(?:\*\*)?\s*(\S+)", re.I | re.M)
MEDIDA = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?medida:(?:\*\*)?[ \t]*(.*)$", re.I | re.M)
A_VENCER_DIAS = 14


def validade_da_regra(texto, hoje):
    """(estado, revisar_em|None, medida|None, avisos). Estado: `ok`, `a-vencer` (até 14 dias; sem aviso) ou `aviso`."""
    avisos, revisar, medida = [], None, None
    achou = REVISAR_EM.search(sem_acento(texto))
    if not achou:
        avisos.append("sem 'Revisar em: AAAA-MM-DD'")
    else:
        try:
            revisar = datetime.date.fromisoformat(achou.group(1).strip("*`.,;"))
        except ValueError:
            avisos.append(f"'Revisar em' com data inválida ({achou.group(1)[:20]})")
    achou = MEDIDA.search(texto)
    medida = achou.group(1).strip().strip("*").strip() if achou else None
    if not medida:
        avisos.append("sem 'Medida:'" if achou is None else "'Medida:' vazia")
    elif not re.search(r"\d", medida):
        avisos.append("'Medida:' sem número")
    if revisar and revisar < hoje:
        avisos.append(f"vencida em {revisar.isoformat()}")
    estado = "aviso" if avisos else "a-vencer" if revisar and (revisar - hoje).days <= A_VENCER_DIAS else "ok"
    return estado, revisar, medida, avisos


def cmd_regras(raiz, hoje=None, estrito=False, como_json=False):
    """Uma linha por docs/regras/R-*.md e o resumo. rc 0 (avisos são só avisos); com `estrito`, rc 1 se houver aviso; rc 2 sem regras."""
    hoje = hoje or datetime.date.today()
    pasta = raiz / "docs" / "regras"
    arquivos = sorted(pasta.glob("R-*.md")) if pasta.is_dir() else []
    if not arquivos:
        print(f"regras: nenhuma docs/regras/R-*.md em {raiz}")
        return 2
    resultado = []
    for arq in arquivos:
        texto = ler_texto(arq)
        if texto is None:
            resultado.append({"regra": arq.stem, "estado": "aviso", "revisar_em": None, "medida": None,
                              "avisos": ["ilegível, link simbólico ou grande demais"]})
            continue
        estado, revisar, medida, avisos = validade_da_regra(texto, hoje)
        resultado.append({"regra": arq.stem, "estado": estado, "revisar_em": revisar.isoformat() if revisar else None,
                          "medida": medida, "avisos": avisos})
    com_aviso = sum(1 for r in resultado if r["avisos"])
    if como_json:
        print(json.dumps({"hoje": hoje.isoformat(), "regras": resultado, "avisos": com_aviso}, ensure_ascii=False, indent=1))
    else:
        for r in resultado:
            linha = f"regras: {r['regra']} estado={r['estado']} revisar_em={r['revisar_em'] or '-'} medida={'sim' if r['medida'] else 'nao'}"
            print(linha + ("" if not r["avisos"] else " aviso: " + "; ".join(r["avisos"])))
        print(f"regras: {len(resultado)} regras, {len(resultado) - com_aviso} em dia, {com_aviso} com aviso"
              + (" (--estrito: reprova)" if estrito and com_aviso else ""))
    return 1 if estrito and com_aviso else 0


def registrar_subcomandos(sub, comum):
    """Os subparsers `metricas` e `regras` do forge-check (as opções ficam aqui, junto da lógica)."""
    me = sub.add_parser("metricas", parents=[comum], help="tempo do código pronto à develop e à main, voltas, revalidações, suítes, "
                        "espera do dono e reprovações por classe (mérito: declarada), por item e por período; só leitura (0.43.1 H)")
    me.add_argument("--pedido", action="append", help="id em docs/pedidos/ (repita para vários; padrão: todos)")
    me.add_argument("--desde", help="AAAA-MM-DD (inclusive)")
    me.add_argument("--ate", help="AAAA-MM-DD (inclusive)")
    me.add_argument("--por", choices=("dia", "semana"), default="dia", help="período do agrupamento (padrão: dia)")
    me.add_argument("--fuso", help="fuso das horas do Histórico, ±HHMM ou ±HH:MM (padrão: o da máquina)")
    me.add_argument("--agora", help="AAAA-MM-DDTHH:MM para o aberto_h (padrão: agora; serve para reproduzir)")
    me.add_argument("--develop", default="origin/develop", help="ref da develop (padrão: origin/develop)")
    me.add_argument("--main", default="origin/main", help="ref da main (padrão: origin/main)")
    me.add_argument("--gh", action="store_true", help="conta as execuções e falhas do CI das branches citadas (gh run list; usa rede)")
    me.add_argument("--json", action="store_true", help="saída em JSON")
    rg = sub.add_parser("regras", parents=[comum], help="validade das regras: 'Revisar em:' e 'Medida:' de cada docs/regras/R-*.md; "
                        "aviso rc 0, --estrito rc 1 (0.43.1 H)")
    rg.add_argument("--estrito", action="store_true", help="reprova (rc 1) se alguma regra tem aviso")
    rg.add_argument("--hoje", help="AAAA-MM-DD (padrão: hoje; serve para reproduzir)")
    rg.add_argument("--json", action="store_true", help="saída em JSON")


def executar(a, raiz, raiz_pedidos):
    """Despacho dos dois subcomandos; None se `a.cmd` não é deles."""
    if a.cmd == "metricas":
        return cmd_metricas(raiz, raiz_pedidos, a)
    if a.cmd == "regras":
        try:
            hoje = datetime.date.fromisoformat(a.hoje) if a.hoje else None
        except ValueError:
            print("regras: --hoje fora de AAAA-MM-DD")
            return 2
        return cmd_regras(raiz, hoje, a.estrito, a.json)
    return None
