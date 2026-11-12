"""Forge: as medidas de governança do processo (0.43.1, frente H): `forge-check metricas` e `forge-check regras`.

`metricas` lê o `## Histórico` dos pedidos, o registro de conferências (docs/kanban/conferencias.md) e o git, e dá, por item e por
período: tempo do código pronto (primeira `entrega conferida <sha>`) até a develop e até a main (o merge da linha de primeiro pai que
trouxe o sha), voltas, revalidações, suítes e falhas, minutos de espera do dono e as reprovações por classe. O mérito das
reprovações é anotado pelo próprio Jarvis no registro: sai marcado `declarada`, nunca como medida. Desde a 0.43.3 também a espera
por portão (as recusas do R-TETO em `recusas.log`, RN-6) e os tokens por item (CUSTO): os transcritos dos subagentes da raiz
(`~/.claude/projects/<raiz>/<sessão>/subagents/*.jsonl`, ou as pastas de `FORGE_TRANSCRITOS`) ligados ao item pelo brief citado no primeiro pedido do agente e pelo
`Cobre:` do brief; sem fonte, `-`.

`regras` lista cada docs/regras/R-*.md com os campos `Revisar em: AAAA-MM-DD` e `Medida:` (o número que justifica a regra); falta,
data vencida ou medida sem número dão aviso (rc 0); com `--estrito`, rc 1.

Com `--log-prepush <log>` (F8, 0.43.3), lê as linhas `pre-push: duracao inicio=... fim=... plano=... rc=...` que o
.githooks/pre-push grava no log do envio e dá, por plano, envios, falhas, p50 e máximo da duração em segundos.

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
# B2 do review da 0.43.3: o transcrito longo é o que mais custa, então o teto dele é largo, mas existe; a leitura é linha a linha.
TETO_DO_TRANSCRITO = 256 * 1024 * 1024  # bytes por subagents/*.jsonl; maior fica de fora e sai aviso
TETO_DE_TRANSCRITOS = 5000  # arquivos por pasta, os mais novos; os demais ficam de fora e sai aviso

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
    "espera_portao_min": "estimada (recusas.log do R-TETO: da primeira à última recusa de cada sequência do mesmo portão, "
                         "com até 10 min entre elas)",
    "tokens": "medida (usage dos transcritos dos subagentes com --transcritos: entrada, saída e cache; '-' sem fonte)",
    "lead": "medida (da primeira linha do item no Histórico à chegada do sha na develop e na main), com fatias: autor até a entrega "
            "conferida, portões dela à chegada, dono pela espera_dono_min, sem sobreposição",
    "fatia_portao": "medida (Histórico do pedido: de `brief selado`/`delegad` ao `entregue`/`aprovad`/`reprovad`/`passou` do mesmo portão), "
                    "estimada (sem o início, da linha anterior do Histórico ao fim) ou nao-medido (sem linha do portão); voltas por contagem",
    "colunas": "medida (docs/kanban/historico.md: minutos de cada cartão em cada coluna até o movimento seguinte; o aberto conta "
               "até agora, menos no Pronto)",
}
RECUSA = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}) (\w+) R-TETO .*\bmotivo=(\w+)\s*$")
INTERVALO_DA_ESPERA = datetime.timedelta(minutes=10)  # recusas do mesmo portão mais próximas que isso são a mesma espera
BRIEF_NO_PROMPT = re.compile(r"docs/briefs/([\w.@+-]+)\.md")
COBRE = re.compile(r"^\s*(?:Etapa:.*?)?\bCobre:\s*(.+?)\s*$", re.M)
CHAVES_DE_USO = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
# X2 (0.44.1): o orçamento de tokens declarado no pedido (`Tokens previstos: 2.000.000`, `500k`, `3M`) e a versão dele (`Versão: X.Y.Z`)
PREVISTO = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?tokens previstos:(?:\*\*)?\s*(\d[\d._]*)\s*(k|m)?\b", re.I | re.M)
VERSAO_DO_PEDIDO = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?vers[aã]o:(?:\*\*)?\s*v?(\d+\.\d+\.\d+)", re.I | re.M)
VERSAO_COMPLETA = re.compile(r"\d+\.\d+\.\d+")
MULTIPLO = {"": 1, "k": 1000, "m": 1_000_000}


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


def _minutos(a, b):
    return round((b - a).total_seconds() / 60, 1)


def _dentro(janelas, a, b):
    """Minutos das `janelas` (união) cortadas em [a, b]."""
    return uniao_em_minutos([(max(i, a), min(f, b)) for i, f in janelas if min(f, b) > max(i, a)])


def fatias(inicio, pronto, chegada, janelas):
    """0.45.3: o lead time do item (do início à chegada numa ref) em minutos de autor (do início à entrega conferida), de portões
    (da entrega à chegada) e de espera do dono (as janelas do item, tiradas das outras duas), com a porcentagem de cada; None sem
    entrega, sem chegada ou com a chegada antes da entrega."""
    if not pronto or not chegada or chegada < pronto:
        return None
    total = _minutos(inicio, chegada)
    partes = {"autor_min": round(_minutos(inicio, pronto) - _dentro(janelas, inicio, pronto), 1),
              "portoes_min": round(_minutos(pronto, chegada) - _dentro(janelas, pronto, chegada), 1),
              "dono_min": _dentro(janelas, inicio, chegada)}
    return {**partes, **{k.replace("_min", "_pct"): round(100 * v / total, 1) if total else None for k, v in partes.items()}}


def somar_fatias(lista):
    """As fatias de vários itens somadas em minutos, com a porcentagem sobre o total; None sem nenhuma."""
    lista = [f for f in lista if f]
    if not lista:
        return None
    soma = {k: round(sum(f[k] for f in lista), 1) for k in ("autor_min", "portoes_min", "dono_min")}
    total = sum(soma.values())
    return {**soma, **{k.replace("_min", "_pct"): round(100 * v / total, 1) if total else None for k, v in soma.items()}}


def minutos_por_coluna(raiz_pedidos, agora, janela):
    """0.45.3 (card voltas-tempo-colunas): {coluna: {minutos, cartoes, abertos}} lido de docs/kanban/historico.md. Cada movimento
    abre o trecho do cartão na coluna `Para` até o movimento seguinte dele; o último fica aberto até `agora`, menos no Pronto (fim
    do fluxo). Conta o trecho que começa na janela. ([], aviso|None) sem o arquivo; só leitura."""
    arq = raiz_pedidos / "docs" / "kanban" / "historico.md"
    texto = ler_texto(arq)
    if texto is None:
        return None, (None if not arq.exists() else "historico.md ilegível, link simbólico ou grande demais")
    por_cartao = {}
    for linha in texto.splitlines():
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(celulas) < 4 or not re.match(r"\d{4}-\d{2}-\d{2}T", celulas[0]):
            continue
        try:
            momento = datetime.datetime.fromisoformat(celulas[0])
        except ValueError:
            continue
        if momento.tzinfo is not None:
            por_cartao.setdefault(celulas[1].casefold(), []).append((momento, celulas[3]))
    colunas = {}
    for movimentos in por_cartao.values():
        movimentos.sort(key=lambda m: m[0])
        for (inicio, coluna), seguinte in zip(movimentos, movimentos[1:] + [None]):
            aberto = seguinte is None
            if not janela(inicio) or (aberto and sem_acento(coluna) == "pronto"):
                continue
            d = colunas.setdefault(coluna, {"minutos": 0.0, "cartoes": 0, "abertos": 0})
            d["minutos"] = round(d["minutos"] + _minutos(inicio, agora if aberto else seguinte[0]), 1)
            d["cartoes"] += 1
            d["abertos"] += aberto
    return dict(sorted(colunas.items())), None


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
        janelas = esperas.get(item, [])
        registro = {"pedido": pedido, "item": d["item"], "periodo_base": (pronto or d["inicio"]),
                    "pronto": pronto.isoformat(timespec="minutes") if pronto else None, "sha": sha,
                    "develop": develop.isoformat(timespec="minutes") if develop else None,
                    "main": main.isoformat(timespec="minutes") if main else None,
                    "pronto_ate_develop_h": horas_entre(pronto, develop), "pronto_ate_main_h": horas_entre(pronto, main),
                    "aberto_h": horas_entre(pronto, agora) if pronto and not develop else None,
                    "inicio": d["inicio"].isoformat(timespec="minutes"),
                    "lead_develop_h": horas_entre(d["inicio"], develop), "lead_main_h": horas_entre(d["inicio"], main),
                    "fatias_develop": fatias(d["inicio"], pronto, develop, janelas),
                    "fatias_main": fatias(d["inicio"], pronto, main, janelas),
                    "voltas": d["voltas"], "revalidacoes": d["revalidacoes"], "suites": d["suites"],
                    "suites_falhas": d["suites_falhas"], "espera_dono_min": uniao_em_minutos(janelas),
                    "branches": sorted(d["branches"])}
        if usar_gh:
            ci = [c for c in (ci_da_branch(b) for b in registro["branches"]) if c is not None]
            registro["ci"] = {"execucoes": sum(c[0] for c in ci), "falhas": sum(c[1] for c in ci)} if ci else "nao-medido"
        saida.append(registro)
    return sorted(saida, key=lambda r: (r["item"] == "-", r["periodo_base"]))


def arquivos_de_recusas(raiz):
    """Os `recusas.log` que o hook `agentes` grava (RN-6): o do diretório comum do git (clone do Forge) e o da cópia principal."""
    candidatos = []
    codigo, comum = git(raiz, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not codigo and comum:
        candidatos += [Path(comum) / "forge" / "run" / "recusas.log", Path(comum).parent / ".forge" / "run" / "recusas.log"]
    candidatos.append(Path(raiz) / ".forge" / "run" / "recusas.log")
    return list(dict.fromkeys(c for c in candidatos if c.is_file() and not c.is_symlink()))


def esperas_por_portao(arquivos, janela):
    """{portão: {"recusas": n, "espera_min": minutos}} das linhas do `recusas.log`: recusas do mesmo portão (motivo) com até
    `INTERVALO_DA_ESPERA` entre elas formam uma espera, que vai da primeira à última; recusa solta conta 0 min. Linha fora da forma
    é ignorada."""
    por_motivo = {}
    for arq in arquivos:
        for linha in (ler_texto(arq) or "").splitlines():
            achou = RECUSA.match(linha)
            if achou:
                quando = datetime.datetime.fromisoformat(achou.group(1)).astimezone()
                if janela(quando):
                    por_motivo.setdefault(achou.group(3), []).append(quando)
    saida = {}
    for motivo, horas in sorted(por_motivo.items()):
        horas.sort()
        total, inicio = 0.0, horas[0]
        for anterior, atual in zip(horas, horas[1:] + [None]):
            if atual is None or atual - anterior > INTERVALO_DA_ESPERA:
                total += (anterior - inicio).total_seconds() / 60
                inicio = atual
        saida[motivo] = {"recusas": len(horas), "espera_min": round(total, 1)}
    return saida


VERMELHO_DA_EXECUCAO = ("failure", "timed_out", "startup_failure")
VERMELHO_DO_CHECK = ("FAILURE", "TIMED_OUT", "STARTUP_FAILURE", "ERROR")
VERSAO_DA_BRANCH = re.compile(r"melhoria/v(\d)(\d{2})(\d)\b")


def _versao_da_branch(texto):
    """"0.45.6" de um texto com `melhoria/v0456` (branch do PR ou título do merge na main), ou "-" se não houver."""
    achou = VERSAO_DA_BRANCH.search(texto or "")
    return ".".join(str(int(g)) for g in achou.groups()) if achou else "-"


def _gh_lista(args):
    """A lista JSON de `gh <args>`, ou None se o gh falha (sem rede, sem login) ou devolve outra forma."""
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=GH_TIMEOUT_S)
        lista = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None
    return [x for x in lista if isinstance(x, dict)] if isinstance(lista, list) else None


def main_vermelha_e_merges(versoes, usar_gh):
    """{versão: {"main_vermelha": n, "merge_vermelho": n, "origem": medido|nao-medido}}: (a) execuções de CI da main que terminaram
    vermelhas (`gh run list --branch main`, a versão vem do `melhoria/vNNNN` do título do merge) e (b) PRs mesclados cujos checks
    estavam vermelhos (`statusCheckRollup`, a versão vem da branch do PR). Versão sem nenhuma execução ou PR lido, ou sem `usar_gh`
    ou com o gh falhando, fica `nao-medido` (None): dado ausente nunca vira zero. `versoes` são as versões dos pedidos; as achadas
    no gh entram também."""
    execucoes = _gh_lista(["run", "list", "--branch", "main", "--limit", "100", "--json", "conclusion,displayTitle"]) if usar_gh else None
    prs = _gh_lista(["pr", "list", "--state", "merged", "--limit", "100", "--json", "headRefName,statusCheckRollup"]) if usar_gh else None
    a, b = {}, {}
    for e in execucoes or []:
        if e.get("conclusion"):
            vezes = a.setdefault(_versao_da_branch(e.get("displayTitle")), [0, 0])
            vezes[0] += e["conclusion"] in VERMELHO_DA_EXECUCAO
            vezes[1] += 1
    for pr in prs or []:
        checks = [c for c in pr.get("statusCheckRollup") or [] if isinstance(c, dict)]
        if checks:
            vezes = b.setdefault(_versao_da_branch(pr.get("headRefName")), [0, 0])
            vezes[0] += any((c.get("conclusion") or c.get("state")) in VERMELHO_DO_CHECK for c in checks)
            vezes[1] += 1
    saida = {}
    for versao in sorted(set(versoes) | set(a) | set(b)):
        saida[versao] = {"main_vermelha": a[versao][0] if versao in a else None,
                         "merge_vermelho": b[versao][0] if versao in b else None,
                         "origem": "medido" if versao in a or versao in b else "nao-medido"}
    return saida


def primeiro_pedido(arq):
    """O texto do primeiro registro `user` do transcrito (o prompt do agente) e a soma do uso de tokens das respostas, com cada
    mensagem contada uma vez (o mesmo `id` se repete nos pedaços de uma resposta). (None, 0) se o arquivo não é lido: link,
    não regular ou acima de TETO_DO_TRANSCRITO (B2). Lê linha a linha, sem o arquivo inteiro na memória."""
    try:
        if arq.is_symlink() or not arq.is_file() or arq.stat().st_size > TETO_DO_TRANSCRITO:
            return None, 0
        with open(arq, encoding="utf-8", errors="replace") as fonte:
            return _uso_do_transcrito(fonte)
    except OSError:
        return None, 0


def _uso_do_transcrito(linhas):
    """(prompt, tokens) de `primeiro_pedido`, a partir das linhas do transcrito."""
    prompt, usos = None, {}
    for linha in linhas:
        try:
            registro = json.loads(linha)
        except ValueError:
            continue
        mensagem = registro.get("message") if isinstance(registro, dict) else None
        if not isinstance(mensagem, dict):
            continue
        if prompt is None and registro.get("type") == "user":
            conteudo = mensagem.get("content")
            prompt = conteudo if isinstance(conteudo, str) else " ".join(
                str(c.get("text", "")) for c in conteudo if isinstance(c, dict)) if isinstance(conteudo, list) else ""
        uso = mensagem.get("usage")
        if registro.get("type") == "assistant" and isinstance(uso, dict):
            usos[mensagem.get("id") or len(usos)] = sum(v for k in CHAVES_DE_USO if isinstance(v := uso.get(k), int))
    return prompt, sum(usos.values())


def transcritos_da_raiz(raiz):
    """A pasta de transcritos do Claude Code da `raiz` (`~/.claude/projects/<caminho com / trocado por ->`), se existe; a dos
    subagentes fica dentro dela, em `<sessão>/subagents/`."""
    pasta = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9-]", "-", str(Path(raiz).resolve()))
    return [pasta] if pasta.is_dir() else []


def grande_demais(arq):
    try:
        return not arq.is_symlink() and arq.stat().st_size > TETO_DO_TRANSCRITO
    except OSError:
        return False


def transcritos_da_pasta(pasta, avisos=None):
    """Os `subagents/*.jsonl` da pasta, no máximo TETO_DE_TRANSCRITOS (os mais novos, em ordem de nome); o resto vira aviso (B2)."""
    achados = sorted(Path(pasta).glob("*/subagents/*.jsonl")) + sorted(Path(pasta).glob("subagents/*.jsonl"))
    if len(achados) <= TETO_DE_TRANSCRITOS:
        return achados

    def idade(arq):
        try:
            return arq.lstat().st_mtime
        except OSError:
            return 0
    mantidos = set(sorted(achados, key=idade, reverse=True)[:TETO_DE_TRANSCRITOS])
    if avisos is not None:
        avisos.append(f"{len(achados) - TETO_DE_TRANSCRITOS} transcritos mais antigos de {pasta} ficaram fora dos tokens "
                      f"(teto de {TETO_DE_TRANSCRITOS} por pasta)")
    return [a for a in achados if a in mantidos]


def tokens_por_item(pastas, raiz_pedidos, avisos=None):
    """{(pedido, item): {"tokens": n, "agentes": k}} dos transcritos `*.jsonl` das `pastas` (busca recursiva): o brief citado no
    primeiro pedido do agente dá o pedido (`Pedido:` ou o nome `<pedido>-<papel>-<n>`) e os itens (`Cobre:`); sem `Cobre:`, o item é
    `-`. Os itens vêm do `Cobre:` e das citações do Entregar; agente que cobre vários itens divide os tokens entre eles (rateio).
    Transcrito sem brief citado fica de fora (não é de item); o acima dos tetos (B2) também, com aviso em `avisos`."""
    saida = {}
    for pasta in pastas:
        for arq in transcritos_da_pasta(pasta, avisos):
            prompt, tokens = primeiro_pedido(arq)
            if prompt is None and avisos is not None and grande_demais(arq):
                avisos.append(f"transcrito {arq.name} passa de {TETO_DO_TRANSCRITO // 1024 // 1024} MB e ficou fora dos tokens")
            nome = BRIEF_NO_PROMPT.search(prompt or "")
            if not nome or not tokens:
                continue
            brief = ler_texto(raiz_pedidos / "docs" / "briefs" / f"{nome.group(1)}.md") or ""
            pedido = re.search(r"^Pedido:\s*(\S+)", brief, re.M)
            pedido = pedido.group(1).removesuffix(".md").rsplit("/", 1)[-1] if pedido else re.sub(r"-[a-z-]+-\d+$", "", nome.group(1))
            cobre = COBRE.search(brief)
            itens = list(dict.fromkeys(ITEM.findall(" ".join([cobre.group(1) if cobre else ""] + secao(brief, "Entregar")))))
            for item in itens or ["-"]:
                d = saida.setdefault((pedido, item), {"tokens": 0, "agentes": 0})
                d["tokens"] += tokens // len(itens or ["-"])
                d["agentes"] += 1
    return saida


def previsto_do_pedido(texto):
    """X2: os tokens previstos do pedido (inteiro), ou None sem a linha."""
    achado = PREVISTO.search(texto)
    if not achado:
        return None
    return int(re.sub(r"[._]", "", achado.group(1))) * MULTIPLO[(achado.group(2) or "").lower()]


def orcamento_de_tokens(por_pedido, textos):
    """X2: {"versoes": {versão: {previsto, gasto}}, "alertas": [...]} dos pedidos com `Tokens previstos:`; o gasto é o `tokens` medido
    (sem medida conta 0). Alerta quando o gasto passa do previsto, por pedido e por versão. Grava `tokens_previstos` em cada pedido."""
    versoes, alertas = {}, []
    for r in por_pedido:
        texto = textos[r["pedido"]]
        previsto, gasto = previsto_do_pedido(texto), r.get("tokens") or 0
        r["tokens_previstos"] = previsto
        if previsto is None:
            continue
        versao = VERSAO_DO_PEDIDO.search(texto)
        soma = versoes.setdefault(versao.group(1) if versao else "-", {"previsto": 0, "gasto": 0})
        soma["previsto"] += previsto
        soma["gasto"] += gasto
        alertas += [_alerta(f"pedido {r['pedido']}", gasto, previsto)] * (gasto > previsto)
    alertas += [_alerta(f"versão {v}", s["gasto"], s["previsto"]) for v, s in versoes.items() if s["gasto"] > s["previsto"]]
    return {"versoes": versoes, "alertas": alertas}


def _alerta(quem, gasto, previsto):
    return f"{quem}: gasto {gasto} tokens passa do previsto {previsto} (+{round((gasto - previsto) * 100 / max(previsto, 1))}%)"


def resumo(itens, conferencias):
    tempos = [i["pronto_ate_develop_h"] for i in itens if i["pronto_ate_develop_h"] is not None]
    tempos_main = [i["pronto_ate_main_h"] for i in itens if i["pronto_ate_main_h"] is not None]
    classes, meritos = reprovacoes(conferencias)
    leads = [i["lead_develop_h"] for i in itens if i.get("lead_develop_h") is not None]
    return {"itens_prontos": sum(1 for i in itens if i["pronto"]),
            "lead_develop_h_p50": round(statistics.median(leads), 2) if leads else None,
            "fatias_develop": somar_fatias([i.get("fatias_develop") for i in itens]),
            "fatias_main": somar_fatias([i.get("fatias_main") for i in itens]),
            "pronto_ate_develop_h_p50": round(statistics.median(tempos), 2) if tempos else None, "n_develop": len(tempos),
            "pronto_ate_main_h_p50": round(statistics.median(tempos_main), 2) if tempos_main else None, "n_main": len(tempos_main),
            "abertos": sum(1 for i in itens if i["pronto"] and not i["develop"]),
            "voltas": sum(i["voltas"] for i in itens), "revalidacoes": sum(i["revalidacoes"] for i in itens),
            "suites": sum(i["suites"] for i in itens), "suites_falhas": sum(i["suites_falhas"] for i in itens),
            "espera_dono_min": round(sum(i["espera_dono_min"] for i in itens), 1),
            "reprovacoes_por_classe": classes, "merito_declarado": meritos,
            "tokens": sum(i["tokens"] for i in itens if i.get("tokens") is not None) if any(i.get("tokens") is not None for i in itens) else None}


# ---- fatia por portão (0.45.6, AV4(c)): review, QA, segurança, CI e revalidação, por versão, lidos do Histórico ----
PORTOES = {"review": re.compile(r"\breview\b|\brevisao\b"), "qa": re.compile(r"\bqa\b"),
           "seguranca": re.compile(r"\bseguranca\b"), "ci": re.compile(r"\bci\b"), "revalidacao": REVALIDACAO}
INICIO_DE_PORTAO = re.compile(r"brief selado|delegad")
FIM_DE_PORTAO = re.compile(r"entregue|aprovad|reprovad|\bpassou\b|\bverde\b|vermelh|falhou")


def fatia_do_pedido(eventos):
    """{portão: {minutos, voltas, tempo}} de um pedido; portão sem linha no Histórico sai `None` (nunca 0 por dado ausente).
    `tempo`: `medido` (início e fim do portão), `estimado` (sem início: da linha anterior ao fim) ou None (nada fechou)."""
    saida = {p: None for p in PORTOES}
    for portao, padrao in PORTOES.items():
        aberto, anterior, d = None, None, None
        for h, _item, s, _original in eventos:
            if padrao.search(s):
                d = d or {"minutos": 0.0, "voltas": 0, "tempo": None}
                d["voltas"] += bool(VOLTA.search(s) or portao == "revalidacao")
                if FIM_DE_PORTAO.search(s) and (aberto or anterior):
                    d["minutos"] += _minutos(aberto or anterior, h)
                    d["tempo"] = "medido" if aberto and d["tempo"] != "estimado" else "estimado"
                    aberto = None
                elif INICIO_DE_PORTAO.search(s):
                    aberto = aberto or h
            anterior = h
        saida[portao] = d
    return saida


def somar_fatia(partes):
    """Junta as fatias de vários pedidos da mesma versão; falta de dado fica None."""
    saida = {p: None for p in PORTOES}
    for parte in partes:
        for portao, d in parte.items():
            if d is None:
                continue
            s = saida[portao] = saida[portao] or {"minutos": 0.0, "voltas": 0, "tempo": None}
            s["voltas"] += d["voltas"]
            if d["tempo"]:
                s["minutos"] = round(s["minutos"] + d["minutos"], 1)
                s["tempo"] = "estimado" if "estimado" in (s["tempo"], d["tempo"]) else "medido"
    return saida


def calcular(raiz, raiz_pedidos, pedidos=None, desde=None, ate=None, por="dia", fuso=None, agora=None,
             develop="origin/develop", main="origin/main", usar_gh=False, transcritos=None, recusas=None):
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
    variavel = [t for t in os.environ.get("FORGE_TRANSCRITOS", "").split(os.pathsep) if t]
    pastas = [Path(t) for t in (transcritos or variavel)] or transcritos_da_raiz(raiz)
    custos = tokens_por_item(pastas, raiz_pedidos, avisos) if pastas else None
    itens, por_pedido, textos, por_versao = [], [], {}, {}
    for nome in nomes:
        texto = ler_texto(pasta / f"{nome}.md") if ID_DE_PEDIDO.fullmatch(nome) and nome.strip(".") else None
        if texto is None:
            avisos.append(f"pedido {nome!r} ausente, fora de docs/pedidos/, link simbólico ou ilegível")
            continue
        doc = itens_do_pedido(nome, texto, fuso, chegadas, agora, usar_gh, janela)
        textos[nome] = texto
        versao = VERSAO_DO_PEDIDO.search(texto)
        eventos = [e for e in eventos_do_pedido(texto, fuso) if janela(e[0])]
        por_versao.setdefault(versao.group(1) if versao else nome, []).append(fatia_do_pedido(eventos))
        for i in doc:
            custo = custos.get((nome, i["item"])) if custos is not None else None
            i["tokens"] = custo["tokens"] if custo else None
        itens += doc
        registro = [c for c in conferencias if c["pedido"].casefold() == nome.casefold()]
        if doc or registro:
            por_pedido.append({"pedido": nome, **resumo(doc, registro)})
            if custos is not None:  # o pedido soma todos os agentes dele, também os de item sem linha no Histórico
                por_pedido[-1]["tokens"] = sum(d["tokens"] for (p, _), d in custos.items() if p == nome) or None
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
    arquivos = [Path(r) for r in recusas] if recusas else arquivos_de_recusas(raiz)
    portoes = esperas_por_portao(arquivos, lambda q: janela(q))
    colunas, aviso = minutos_por_coluna(raiz_pedidos, agora, janela)
    avisos += [aviso] if aviso else []
    return {"fontes": FONTES, "por": por, "itens": itens, "pedidos": por_pedido, "periodos": lista_periodos,
            "espera_por_portao": portoes if arquivos else None, "orcamento": orcamento_de_tokens(por_pedido, textos),
            "colunas": colunas, "fatia_por_portao": {v: somar_fatia(f) for v, f in por_versao.items()},
            "main_vermelha": main_vermelha_e_merges([v for v in por_versao if VERSAO_COMPLETA.fullmatch(v)], usar_gh)}, avisos


def _n(valor):
    return "nao-medido" if valor is None else f"{valor:g}" if isinstance(valor, float) else str(valor)


def _contagem(d):
    return ",".join(f"{k}={v}" for k, v in d.items()) or "-"


def _fatias(f):
    return "-" if f is None else f"autor={_n(f['autor_pct'])}%,portoes={_n(f['portoes_pct'])}%,dono={_n(f['dono_pct'])}%"


def linhas_de_texto(dados):
    saida = []
    for i in dados["itens"]:
        destino = _n(i["pronto_ate_develop_h"]) if i["develop"] else ("aberto" if i["pronto"] else "-")
        linha = (f"metricas: item {i['pedido']} {i['item']} pronto={i['pronto'] or '-'} develop_h={destino} "
                 f"main_h={_n(i['pronto_ate_main_h']) if i['main'] else ('aberto' if i['pronto'] else '-')} "
                 f"aberto_h={_n(i['aberto_h']) if i['aberto_h'] is not None else '-'} voltas={i['voltas']} "
                 f"revalidacoes={i['revalidacoes']} suites={i['suites']} falhas={i['suites_falhas']} espera_dono_min={_n(i['espera_dono_min'])} "
                 f"lead_develop_h={_n(i['lead_develop_h'])} lead_main_h={_n(i['lead_main_h'])} fatias_develop={_fatias(i['fatias_develop'])} "
                 f"fatias_main={_fatias(i['fatias_main'])} tokens={'-' if i.get('tokens') is None else i['tokens']}")
        if "ci" in i:
            linha += " ci=" + (f"{i['ci']['execucoes']}/{i['ci']['falhas']}" if isinstance(i["ci"], dict) else i["ci"])
        saida.append(linha)
    for chave, grupo in (("pedido", dados["pedidos"]), ("periodo", dados["periodos"])):
        for r in grupo:
            saida.append(f"metricas: {chave} {r[chave]} prontos={r['itens_prontos']} develop_h_p50={_n(r['pronto_ate_develop_h_p50'])}"
                         f"(n={r['n_develop']}) main_h_p50={_n(r['pronto_ate_main_h_p50'])}(n={r['n_main']}) abertos={r['abertos']} "
                         f"voltas={r['voltas']} revalidacoes={r['revalidacoes']} suites={r['suites']} falhas={r['suites_falhas']} "
                         f"espera_dono_min={_n(r['espera_dono_min'])} reprovacoes={_contagem(r['reprovacoes_por_classe'])} "
                         f"merito(declarada)={_contagem(r['merito_declarado'])} lead_develop_h_p50={_n(r['lead_develop_h_p50'])} "
                         f"fatias_develop={_fatias(r['fatias_develop'])} fatias_main={_fatias(r['fatias_main'])} "
                         f"tokens={'-' if r.get('tokens') is None else r['tokens']}")
    for versao, soma in dados.get("orcamento", {}).get("versoes", {}).items():
        saida.append(f"metricas: orcamento versao {versao} previsto={soma['previsto']} gasto={soma['gasto']}")
    saida += [f"metricas: alerta: {a}" for a in dados.get("orcamento", {}).get("alertas", [])]
    for coluna, d in (dados.get("colunas") or {}).items():
        saida.append(f"metricas: coluna {coluna} minutos={_n(d['minutos'])} cartoes={d['cartoes']} abertos={d['abertos']}")
    for versao, fatia in (dados.get("fatia_por_portao") or {}).items():
        for portao, d in fatia.items():
            saida.append(f"metricas: fatia versao {versao} portao {portao} "
                         + ("minutos=nao-medido voltas=nao-medido tempo=nao-medido" if d is None else
                            f"minutos={_n(d['minutos']) if d['tempo'] else 'nao-medido'} voltas={d['voltas']} "
                            f"tempo={d['tempo'] or 'nao-medido'}"))
    for versao, d in (dados.get("main_vermelha") or {}).items():
        saida.append(f"metricas: ci versao {versao} main_vermelha={_n(d['main_vermelha'])} merge_com_check_vermelho={_n(d['merge_vermelho'])} "
                     f"origem={d['origem']}")
    portoes = dados.get("espera_por_portao")
    if portoes is None:
        saida.append("metricas: portao - (sem recusas.log: o hook agentes ainda não recusou nada ou a fonte falta)")
    for portao, d in (portoes or {}).items():
        saida.append(f"metricas: portao {portao} recusas={d['recusas']} espera_min={_n(d['espera_min'])}")
    for plano, r in dados.get("prepush", {}).items():
        saida.append(f"metricas: prepush plano={plano} envios={r['envios']} falhas={r['falhas']} p50_s={_n(r['p50_s'])} "
                     f"max_s={_n(r['max_s'])}")
    if "prepush" in dados and not dados["prepush"]:
        saida.append("metricas: prepush nenhuma linha de duração nos logs")
    if dados.get("placar") is not None:
        p = dados["placar"]
        saida.append(f"metricas: placar decididas={p['decididas']} perguntas={p['perguntas']} revertidas={p['revertidas']}")
    fontes = {**FONTES, "prepush": "medida (linhas `pre-push: duracao` do log do envio)"} if "prepush" in dados else FONTES
    saida.append("metricas: fontes: " + "; ".join(f"{k}={v}" for k, v in fontes.items()))
    return saida


LINHA_DE_DURACAO = re.compile(r"pre-push: duracao inicio=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) "
                              r"fim=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) plano=([a-z]{1,20}) rc=(\d{1,3})$")


def duracoes_do_prepush(logs, desde=None, ate=None):
    """F8: ({plano: {envios, falhas, p50_s, max_s}}, avisos) das linhas de duração do pre-push nos `logs` (caminhos).
    A linha vale no fim de uma linha do log (prefixo de hora ou de marca do registrador é aceito); fim antes do início ou
    fora do formato não conta. `desde` e `ate` filtram pela data do início (UTC)."""
    por_plano, avisos = {}, []
    for caminho in logs:
        texto = ler_texto(Path(caminho))
        if texto is None:
            avisos.append(f"log do pre-push {caminho!r} ausente, link simbólico, ilegível ou grande demais")
            continue
        for linha in texto.splitlines():
            achado = LINHA_DE_DURACAO.search(linha.rstrip())
            if not achado:
                continue
            inicio, fim = (datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ") for x in achado.group(1, 2))
            if fim < inicio or (desde and inicio.date() < desde) or (ate and inicio.date() > ate):
                continue
            por_plano.setdefault(achado.group(3), []).append(((fim - inicio).total_seconds(), int(achado.group(4))))
    saida = {}
    for plano, envios in sorted(por_plano.items()):
        segundos = [s for s, _ in envios]
        saida[plano] = {"envios": len(envios), "falhas": sum(1 for _, rc in envios if rc != 0),
                        "p50_s": round(statistics.median(segundos), 1), "max_s": round(max(segundos), 1)}
    return saida, avisos


def placar_das_decisoes(raiz_pedidos):
    """Orkastery 3 (0.44.2): decididas × perguntas × revertidas de docs/kanban/decisoes-obvias.jsonl (bin/forge_decisor.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import forge_decisor  # noqa: PLC0415
    except ImportError:
        return None
    finally:
        sys.path.pop(0)
    return forge_decisor.placar(raiz_pedidos)


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
    dados, avisos = calcular(raiz, raiz_pedidos, a.pedido, desde, ate, a.por, fuso, agora, a.develop, a.main, a.gh,
                             getattr(a, "transcritos", None), getattr(a, "recusas", None))
    if getattr(a, "log_prepush", None):
        dados["prepush"], mais = duracoes_do_prepush(a.log_prepush, desde, ate)
        avisos += mais
    dados["placar"] = placar_das_decisoes(raiz_pedidos)
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


# ---- avaliação de fora (0.45.3): a cadência do AQ, lida do CHANGELOG.md e de docs/avaliacoes/ ----
CADENCIA_DA_AVALIACAO = 5  # versões publicadas desde a última avaliação
VERSAO_DO_CHANGELOG = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})", re.M)
NOME_DA_AVALIACAO = re.compile(r"(\d{4}-\d{2}-\d{2})[A-Za-z0-9._-]*\.md")
VERSAO_DA_AVALIACAO = re.compile(r"^versao:\s*v?(\d+\.\d+\.\d+)\s*$", re.M)


def avaliacao_pendente(raiz):
    """(pendente, [versões desde a última avaliação, da mais nova], nome da última | None), ou None sem CHANGELOG.md legível.
    A última é a docs/avaliacoes/<AAAA-MM-DD>*.md de maior nome; contam as versões depois da `versao:` dela ou, sem essa linha,
    as publicadas depois da data do nome. Só lê."""
    texto = ler_texto(Path(raiz) / "CHANGELOG.md")
    if texto is None:
        return None
    versoes = VERSAO_DO_CHANGELOG.findall(texto)
    pasta = Path(raiz) / "docs" / "avaliacoes"
    nomes = sorted(p.name for p in pasta.glob("*.md") if NOME_DA_AVALIACAO.fullmatch(p.name))
    ultima, desde = (nomes[-1] if nomes else None), versoes
    if ultima:
        achou = VERSAO_DA_AVALIACAO.search(ler_texto(pasta / ultima) or "")
        numeros = [v for v, _ in versoes]
        if achou and achou.group(1) in numeros:
            desde = versoes[:numeros.index(achou.group(1))]
        else:
            data = NOME_DA_AVALIACAO.fullmatch(ultima).group(1)
            desde = [(v, d) for v, d in versoes if d > data]
    return len(desde) >= CADENCIA_DA_AVALIACAO, [v for v, _ in desde], ultima


def frase_da_avaliacao(estado):
    pendente, desde, ultima = estado
    origem = f"docs/avaliacoes/{ultima}" if ultima else "o início (nenhuma docs/avaliacoes/*.md)"
    if pendente:
        return (f"avaliação de fora pendente: {len(desde)} versões desde {origem} (a mais nova: {desde[0]}); "
                "acione o AQ (forge-dev:aq)")
    return f"em dia: {len(desde)} de {CADENCIA_DA_AVALIACAO} versões desde {origem}"


def cmd_avaliacao(raiz):
    """Só avisa, nunca barra: rc 0 pendente ou em dia; rc 2 sem CHANGELOG.md legível."""
    estado = avaliacao_pendente(raiz)
    if estado is None:
        print(f"avaliacao: CHANGELOG.md ausente ou ilegível em {raiz}; nada medido")
        return 2
    print(f"avaliacao: {frase_da_avaliacao(estado)}")
    return 0


def executar(a, raiz, raiz_pedidos):
    """Despacho dos subcomandos; None se `a.cmd` não é deles."""
    if a.cmd == "avaliacao":
        return cmd_avaliacao(raiz)
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
