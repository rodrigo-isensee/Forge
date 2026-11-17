"""Forge: as autorizações do dono gravadas (ADR 0018, G1.1: formato, integridade e estado). Só biblioteca padrão; só leitura.

`forge-check autorizacao ler` lista cada concessão de `<raiz principal>/.forge/autorizacoes/` com o estado (ativa, pendente com o
motivo, vencida, adulterada, inativa), a validade no `Fuso` e em UTC e a mensagem inteira do dono. Gravar e
travar vêm no G1.2 em diante. Erro ao ler qualquer evento vale como "não há autorização" (falha fechada): nenhuma fica ativa.
"""
import datetime
import hashlib
import os
import re
import stat
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

PASTA = Path(".forge") / "autorizacoes"
CAMPOS = ("Id", "Ato", "Alvos", "Validade", "Validade-utc", "Fuso", "Origem-da-validade", "Estado-inicial", "Motivo-da-pendencia",
          "Mensagem", "Hora-da-fala", "Sessao", "Pedido", "Sha256", "Gravado-por", "Autoriza")
AUTORIZA = "só o ato e os alvos acima, até a validade; não amplia outra regra (R-DECISAO)"
ATOS = ("rotulo-afrouxa-regra", "merge-main")
ALVOS = re.compile(r"pr:[1-9]\d*(, pr:[1-9]\d*)*|versao:\d+\.\d+\.\d+")
ESTADOS_INICIAIS = ("ativa", "pendente-confirmacao")
PEDIDO = r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*"
NOME = re.compile(rf"A-\d+|C-A-\d+|R-\d+|U-A-\d+(-\d+)?|M-[0-9a-f-]+|F-{PEDIDO}")
LIDOS = ("A-", "C-", "R-")  # U-, M- e F- (fechamento gravado do pedido) valem pela presença (só apertam)
SEM_PRAZO_ESCRITO = ("sem termo", "hoje", "hj", "ate amanha")  # D1: 48 h desde a fala; prazo escrito: 7 dias
DATA = "%Y-%m-%d %H:%M"
UTC = datetime.timezone.utc
LINHA = re.compile(r"([A-Za-z0-9-]+): (.*)")


class Ilegivel(Exception):
    pass


def sha(corpo):
    return hashlib.sha256(corpo.encode("utf-8")).hexdigest()


def ler_evento(arq):
    """({campo: valor}, corpo) de um evento: cabeçalho `Campo: valor`, linha vazia, corpo byte a byte. Link, arquivo que não é
    comum, texto fora de UTF-8 ou cabeçalho fora da forma (campo repetido inclusive) levantam `Ilegivel`."""
    try:
        fd = os.open(arq, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    except OSError as e:
        raise Ilegivel(f"{arq.name}: {e.strerror or e}") from None
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise Ilegivel(f"{arq.name}: não é arquivo comum")
    with os.fdopen(fd, "rb") as f:
        bruto = f.read()
    try:
        cabecalho, separador, corpo = bruto.decode("utf-8").partition("\n\n")
    except UnicodeDecodeError:
        raise Ilegivel(f"{arq.name}: não é UTF-8") from None
    campos = {}
    for linha in cabecalho.split("\n"):
        achado = LINHA.fullmatch(linha)
        if not separador or not achado or achado.group(1) in campos:
            raise Ilegivel(f"{arq.name}: cabeçalho fora da forma")
        campos[achado.group(1)] = achado.group(2)
    return campos, corpo


def eventos(pasta):
    """(nomes presentes, {nome: (campos, corpo)} dos A-, C- e R-, erros). Pasta ausente: nada; pasta que é link: erro."""
    if pasta.is_symlink() or (pasta.exists() and not pasta.is_dir()):
        return set(), {}, [f"{PASTA}: não é pasta comum"]
    nomes, lidos, erros = set(), {}, []
    for arq in sorted(pasta.iterdir()) if pasta.exists() else ():
        if not NOME.fullmatch(arq.name):
            erros.append(f"{arq.name}: nome fora da forma")
            continue
        nomes.add(arq.name)
        try:
            if arq.name.startswith(LIDOS):
                lidos[arq.name] = ler_evento(arq)
        except Ilegivel as e:
            erros.append(str(e))
    return nomes, lidos, erros


def normal(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).lower().strip()


def instante(texto):
    """Carimbo da transcrição (ISO com fuso; `Z` é UTC) em UTC; sem fuso é ilegível, nunca o relógio local."""
    momento = datetime.datetime.fromisoformat(texto.replace("Z", "+00:00"))
    if momento.tzinfo is None:
        raise ValueError("Hora-da-fala sem fuso")
    return momento.astimezone(UTC)


def limite(campos):
    """Instante (UTC) em que a concessão para: a `Validade-utc` ou o teto da D1, o que vier antes (48 h desde a fala sem prazo
    escrito e no uso único; 7 dias com prazo). A `Validade` no `Fuso` tem de dar o mesmo instante (A6); senão, ValueError."""
    curto = campos["Validade"] == "uso-unico" or normal(campos["Origem-da-validade"]) in SEM_PRAZO_ESCRITO
    teto = instante(campos["Hora-da-fala"]) + datetime.timedelta(hours=48 if curto else 7 * 24)
    if campos["Validade"] == campos["Validade-utc"] == "uso-unico":
        return teto
    if not campos["Validade"].startswith("ate:"):
        raise ValueError("Validade fora da forma")
    local = datetime.datetime.strptime(campos["Validade"][4:], DATA).replace(tzinfo=ZoneInfo(campos["Fuso"]))
    utc = datetime.datetime.strptime(campos["Validade-utc"], DATA).replace(tzinfo=UTC)
    if local != utc:
        raise ValueError("Validade no Fuso e Validade-utc não batem")
    return min(utc, teto)


def problemas(campos, corpo, gravador):
    """Por que a concessão não é íntegra; [] se é (itens 2, 6 e 7 da ADR 0018)."""
    faltam = [c for c in CAMPOS if c not in campos]
    if faltam:
        return [f"campo ausente: {', '.join(faltam)}"]
    achados = [texto for falha, texto in (
        (campos["Sha256"] != sha(corpo), "Sha256 não bate com o corpo"),
        (campos["Gravado-por"] != gravador, "Gravado-por não é o forge-check carregado"),
        (campos["Ato"] not in ATOS, "Ato fora da lista"),
        (not ALVOS.fullmatch(campos["Alvos"]), "Alvos fora da forma"),
        (campos["Estado-inicial"] not in ESTADOS_INICIAIS, "Estado-inicial fora da lista"),
        (not re.fullmatch(PEDIDO, campos["Pedido"]), "Pedido fora da forma"),
        (campos["Autoriza"] != AUTORIZA, "Autoriza fora do texto fixo")) if falha]
    try:
        limite(campos)
    except (ValueError, LookupError, OSError) as e:  # ZoneInfoNotFoundError é LookupError
        achados.append(f"validade ilegível ({e})")
    return achados


def estado(nome, nomes, lidos, gravador, agora):
    """(estado, motivo) da concessão `nome`; só `ativa` autoriza (item 7)."""
    campos, corpo = lidos[nome]
    if achados := problemas(campos, corpo, gravador):
        return "adulterada", "; ".join(achados)
    if agora >= limite(campos):
        return "vencida", ""
    if "pedido" in normal(campos["Origem-da-validade"]) and f"F-{campos['Pedido']}" in nomes:
        return "vencida", "pedido fechado"
    if campos["Estado-inicial"] == "pendente-confirmacao":  # a confirmação C-<Id>, a retirada e o uso vêm no G1.1c
        return "pendente", campos["Motivo-da-pendencia"]
    return "ativa", ""


def concessoes(raiz, gravador, agora):
    """([(nome, campos, corpo, estado, motivo)], erros). Com algum erro de leitura, nenhuma fica ativa (falha fechada)."""
    nomes, lidos, erros = eventos(Path(raiz) / PASTA)
    lista = []
    for nome in sorted((n for n in lidos if n.startswith("A-")), key=lambda n: int(n[2:])):
        est, motivo = estado(nome, nomes, lidos, gravador, agora)
        if erros and est == "ativa":
            est, motivo = "inativa", "evento ilegível na pasta"
        lista.append((nome, *lidos[nome], est, motivo))
    return lista, erros


def cmd_ler(raiz, ctx, agora=None):
    seguro = ctx["seguro"]
    lista, erros = concessoes(raiz, ctx["gravador"], agora or datetime.datetime.now(UTC))
    for nome, campos, corpo, est, motivo in lista:
        print(seguro(f"autorizacao: {nome} · {est}{f' ({motivo})' if motivo else ''} · {campos.get('Ato', '?')} · "
                     f"{campos.get('Alvos', '?')} · validade {campos.get('Validade', '?')} {campos.get('Fuso', '?')} = "
                     f"{campos.get('Validade-utc', '?')} UTC · pedido {campos.get('Pedido', '?')}"))
        print("\n".join(f"> {seguro(linha)}" for linha in corpo.split("\n")))
    for erro in erros:
        print(seguro(f"autorizacao: erro: {erro}"))
    adulteradas = sum(est == "adulterada" for *_, est, _ in lista)
    ativas = sum(est == "ativa" for *_, est, _ in lista)
    print(f"autorizacao: {adulteradas} adulterada(s), {len(erros)} erro(s) de leitura, {ativas} ativa(s); só leitura, nada barra")
    return 1 if erros or adulteradas else 0


def executar(a, raiz, ctx):
    return cmd_ler(raiz, ctx)
