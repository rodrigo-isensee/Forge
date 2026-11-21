"""Forge: as autorizações do dono gravadas (ADR 0018, G1.1: formato, integridade e estado). Só biblioteca padrão; só leitura.

`forge-check autorizacao ler` lista cada concessão de `<raiz principal>/.forge/autorizacoes/` com o estado (ativa, pendente com o
motivo, vencida, retirada, usada, adulterada, inativa), a validade no `Fuso` e em UTC e a mensagem inteira do dono. Gravar e
travar vêm no G1.2 em diante. O alvo `item:<CARTAO>` (Emenda PR-VERDE, E1; PV-A2) vale só para o `Commit` que é o head do
`Ramo` com os pareceres aprovados nele. Erro ao ler qualquer evento vale como "não há autorização" (falha fechada): nenhuma fica ativa.
"""
import datetime
import hashlib
import os
import re
import stat
import subprocess
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

PASTA = Path(".forge") / "autorizacoes"
CAMPOS = ("Id", "Ato", "Alvos", "Validade", "Validade-utc", "Fuso", "Origem-da-validade", "Estado-inicial", "Motivo-da-pendencia",
          "Mensagem", "Hora-da-fala", "Sessao", "Pedido", "Sha256", "Gravado-por", "Autoriza")
AUTORIZA = "só o ato e os alvos acima, até a validade; não amplia outra regra (R-DECISAO)"
ATOS = ("rotulo-afrouxa-regra", "merge-main")
CARTAO = r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*"
ALVOS = re.compile(rf"pr:[1-9]\d*(, pr:[1-9]\d*)*|versao:\d+\.\d+\.\d+|item:{CARTAO}")
SHA40 = re.compile(r"[0-9a-f]{40}")
RAMO = re.compile(r"[A-Za-z0-9_]+(?:[./-][A-Za-z0-9_]+)*")  # sem `-` no início (opção do git) nem `..`
FRASE = re.compile(r"[;!?\n]|\.(?=\s|$)")  # o ponto dentro do cartão (`E57.57`) não separa frase
TERMOS_DO_ITEM = ("rotulo", "afrouxa")  # termos do ato `rotulo-afrouxa-regra`, o único do alvo `item:` (E1)
RESSALVA = re.compile(r"\b(nao|nunca|jamais|se|caso|exceto|salvo|desde que|a menos|ainda)\b")  # negação ou condição
PARECERES = tuple(f"docs/{p}/" for p in ("reviews", "qa", "security", "devops"))
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
    if campos["Alvos"].startswith("item:"):
        achados += do_item(campos, corpo)
    try:
        limite(campos)
    except (ValueError, LookupError, OSError) as e:  # ZoneInfoNotFoundError é LookupError
        achados.append(f"validade ilegível ({e})")
    return achados


def do_item(campos, corpo):
    """Por que a concessão de alvo `item:` não é íntegra (E1): ato do rótulo, `Commit` sha40, `Ramo` na forma; nasce `ativa` só
    com `item <CARTAO>` na mesma frase de um termo do ato e sem ressalva na mensagem (item 5 e A2 da ADR 0018)."""
    marcado = re.compile(rf"(?<![a-z0-9])item ?{re.escape(normal(campos['Alvos'][5:]))}(?![a-z0-9]|[.-][a-z0-9])")
    no_ato = any(marcado.search(f) and any(t in f for t in TERMOS_DO_ITEM) for f in FRASE.split(normal(corpo)))
    ativa, ramo = campos["Estado-inicial"] == "ativa", campos.get("Ramo", "")
    return [texto for falha, texto in (
        (campos["Ato"] != "rotulo-afrouxa-regra", "Ato do alvo item: não é rotulo-afrouxa-regra"),
        (not SHA40.fullmatch(campos.get("Commit", "")), "Commit não é sha de 40 caracteres"),
        (not RAMO.fullmatch(ramo), "Ramo fora da forma"),
        (ativa and not no_ato, "ativa sem item <CARTAO> na frase do ato"),
        (ativa and RESSALVA.search(normal(corpo)) is not None, "ativa com ressalva na mensagem")) if falha]


def git(raiz, *args):
    """Saída do `git` na raiz, ou None se ele falha (falha fechada); sem as variáveis GIT_* herdadas."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, env=env, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def fora_do_revisado(raiz, campos):
    """Por que o `Commit` não é o head do `Ramo` com os pareceres aprovados nele (E1); "" se é. Depois dele o `Ramo` só traz
    pareceres, e todo parecer do `Ramo` (ao menos um) aprova o `Commit`."""
    ramo, commit = campos["Ramo"], campos["Commit"]
    ponta = (git(raiz, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{ramo}^{{commit}}")
             or git(raiz, "rev-parse", "-q", "--verify", f"refs/heads/{ramo}^{{commit}}") or "").strip()
    if not ponta:
        return "Ramo sem ref no clone"
    if git(raiz, "merge-base", "--is-ancestor", commit, ponta) is None:
        return "Commit fora do Ramo"
    depois = git(raiz, "diff", "--name-only", commit, ponta)
    if depois is None or any(not a.startswith(PARECERES) for a in depois.split("\n") if a):
        return "Commit não é o head: o Ramo muda depois dele"
    achados = git(raiz, "grep", "-l", "-F", "-e", f"branch: {ramo}", ponta, "--", *PARECERES) or ""
    pareceres = [p for p in (frente(git(raiz, "show", a) or "") for a in achados.split("\n") if a) if p.get("branch") == ramo]
    if not pareceres or any(p.get("parecer") != "aprovado" or len(p.get("commit", "")) < 7
                            or not commit.startswith(p.get("commit", "")) for p in pareceres):
        return "Commit sem os pareceres aprovados nele"
    return ""


def frente(texto):
    """{campo: valor} do frontmatter de um parecer (ADR 0004)."""
    cabeca = texto.split("\n---", 1)[0] if texto.startswith("---\n") else ""
    return dict(linha.split(": ", 1) for linha in cabeca.split("\n")[1:] if ": " in linha)


def confirmada(nome, campos, lidos, gravador):
    """`C-<nome>` íntegro, do forge-check carregado e de fala posterior à da concessão (ADR 0018 item 5)."""
    conf, corpo = lidos.get(f"C-{nome}", ({}, ""))
    if conf.get("Confirma") != nome or conf.get("Sha256") != sha(corpo) or conf.get("Gravado-por") != gravador:
        return False
    try:
        return instante(conf.get("Hora-da-fala", "")) > instante(campos["Hora-da-fala"])
    except ValueError:
        return False


def estado(nome, nomes, lidos, gravador, agora, raiz):
    """(estado, motivo) da concessão `nome`; só `ativa` autoriza (item 7)."""
    campos, corpo = lidos[nome]
    achados = problemas(campos, corpo, gravador)
    if achados:
        return "adulterada", "; ".join(achados)
    if any(n.startswith("R-") and c.get("Retira") == nome for n, (c, _) in lidos.items()):
        return "retirada", ""
    if campos["Validade"] == "uso-unico" and f"U-{nome}" in nomes:
        return "usada", ""
    if agora >= limite(campos):
        return "vencida", ""
    if "pedido" in normal(campos["Origem-da-validade"]) and f"F-{campos['Pedido']}" in nomes:
        return "vencida", "pedido fechado"
    revisado = fora_do_revisado(raiz, campos) if campos["Alvos"].startswith("item:") else ""
    if revisado:
        return "inativa", revisado
    if campos["Estado-inicial"] == "pendente-confirmacao" and not confirmada(nome, campos, lidos, gravador):
        return "pendente", campos["Motivo-da-pendencia"]
    return "ativa", ""


def concessoes(raiz, gravador, agora):
    """([(nome, campos, corpo, estado, motivo)], erros). Com algum erro de leitura, nenhuma fica ativa (falha fechada)."""
    nomes, lidos, erros = eventos(Path(raiz) / PASTA)
    lista = []
    for nome in sorted((n for n in lidos if n.startswith("A-")), key=lambda n: int(n[2:])):
        est, motivo = estado(nome, nomes, lidos, gravador, agora, raiz)
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
