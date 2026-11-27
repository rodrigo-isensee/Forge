"""Forge: as autorizações do dono gravadas (ADR 0018, G1.1: formato, integridade e estado; G1.2: gravar). Só biblioteca padrão.

`forge-check autorizacao ler` lista cada concessão de `<raiz principal>/.forge/autorizacoes/` com o estado (ativa, pendente com o
motivo, vencida, retirada, usada, adulterada, inativa), a validade no `Fuso` e em UTC e a mensagem inteira do dono. Gravar e
travar vêm no G1.2 em diante. O alvo `item:<CARTAO>` (Emenda PR-VERDE, E1; PV-A2) vale só para o `Commit` que é o head do
`Ramo` com os pareceres aprovados nele. Erro ao ler qualquer evento vale como "não há autorização" (falha fechada): nenhuma fica ativa.
"""
import datetime
import hashlib
import json
import os
import pwd
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
FIXOS = ("so-aperta-com-seguranca",)  # Emenda AUTORIZACOES-FIXAS: só alvo `fixo` e validade `fixa`, sem o teto da D1 (corte-diario saiu: VERSAO-COM-20)
SO_NO_FORGE = ("rotulo-pelo-time",)  # Emenda ROTULO-PELO-TIME: fixo como os dois, e só ativo no repositório do próprio Forge
SEM_PRAZO = (*FIXOS, *SO_NO_FORGE)
ATOS = ("rotulo-afrouxa-regra", "merge-main", *SEM_PRAZO)
CARTAO = r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*"
ALVOS = re.compile(rf"pr:[1-9]\d*(, pr:[1-9]\d*)*|versao:\d+\.\d+\.\d+|item:{CARTAO}|fixo")
SHA40 = re.compile(r"[0-9a-f]{40}")
RAMO = re.compile(r"[A-Za-z0-9_]+(?:[./-][A-Za-z0-9_]+)*")  # sem `-` no início (opção do git) nem `..`
FRASE = re.compile(r"[;!?\n]|\.(?=\s|$)")  # o ponto dentro do cartão (`E57.57`) não separa frase
TERMOS_DO_ITEM = frozenset(("rotulo", "afrouxa"))  # termos do ato `rotulo-afrouxa-regra`, o único do alvo `item:` (E1)
# Vocabulário fechado da concessão (item 5 da ADR 0018): só cresce por ADR, e nenhuma marca de negação ou condição entra nele.
VOCABULARIO = frozenset((
    "rotulo afrouxa regra main item pr versao "  # termos de ato e marcadores de alvo (o alvo marcado sai antes)
    "ate hoje hj amanha esta noite fim deste pedido segunda terca quarta quinta sexta sabado domingo feira "  # validade (item 6)
    "pode podem autorizo autorizado autorizada liberado liberada libero aplicar aplique aplica mesclar mescle "  # permissão
    "o a os as um uma de do da dos das no na nos nas em para pra pelo pela ao aos com "  # artigos e preposições
    "por favor obrigado obrigada ok sim").split())  # cortesia
VOCABULARIO_FIXO = VOCABULARIO | frozenset("fixo fixa aperta seguranca escrito time decide registra homologacao".split())
DATA_OU_HORA = re.compile(r"\b\d{1,2}(?:/\d{1,2}(?:/\d{2,4})?|:\d{2}|h\d{0,2})\b")  # "18/11", "12:00", "18h" (item 6)
EXIGIDOS = ("review", "qa", "revisao-seguranca")  # o rótulo afrouxa-regra só cabe em mudança de controle: classe C (P5)
PARECERES = tuple(f"docs/{p}/" for p in ("reviews", "qa", "security", "devops"))
PASTA_DO_TIPO = dict(zip(("review", "qa", "revisao-seguranca", "revisao-devops"), PARECERES))  # tipo preso à pasta (ADR 0004)
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
    escrito e no uso único; 7 dias com prazo). A `Validade` no `Fuso` tem de dar o mesmo instante (A6); senão, ValueError. Ato fixo
    (Emenda AUTORIZACOES-FIXAS, F1): só com validade `fixa`, que só ele tem, e sem fim."""
    fixo = campos["Ato"] in SEM_PRAZO
    if fixo != (campos["Validade"] == "fixa") or fixo != (campos["Validade-utc"] == "fixa"):
        raise ValueError("validade fixa só nos atos fixos, e eles só com ela")
    if fixo:
        return datetime.datetime.max.replace(tzinfo=UTC)
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
        ((campos["Ato"] in SEM_PRAZO) != (campos["Alvos"] == "fixo"), "alvo fixo só nos atos fixos, e eles só com ele"),
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


def fora_do_vocabulario(texto, alvo=None, vocabulario=VOCABULARIO):
    """Palavras do texto normalizado fora do `vocabulario` (item 5 da ADR 0018), sem o trecho do `alvo` (regex do alvo com
    marcador) nem data ou hora; [] se toda palavra pertence a ele. Uma regra só para o leitor e o `gravar` da G1.2."""
    limpo = DATA_OU_HORA.sub(" ", alvo.sub(" ", normal(texto)) if alvo else normal(texto))
    return sorted(set(re.findall(r"[a-z0-9]+|[^a-z0-9\s.,;:!?#/()\"'-]", limpo)) - vocabulario)  # emoji e outra escrita contam (A5)


def do_item(campos, corpo):
    """Por que a concessão de alvo `item:` não é íntegra (E1): ato do rótulo, `Commit` sha40, `Ramo` na forma; nasce `ativa` só
    com `item <CARTAO>` na mesma frase de um termo do ato (palavra inteira, fora do nome do cartão) e com toda palavra da
    mensagem no vocabulário fechado (item 5 e A2 da ADR 0018)."""
    marcado = re.compile(rf"(?<![a-z0-9])item ?{re.escape(normal(campos['Alvos'][5:]))}(?![a-z0-9]|[.-][a-z0-9])")
    no_ato = any(marcado.search(f) and TERMOS_DO_ITEM & set(re.findall(r"[a-z0-9]+", marcado.sub(" ", f)))
                 for f in FRASE.split(normal(corpo)))
    fora = fora_do_vocabulario(corpo, marcado)
    ativa, ramo = campos["Estado-inicial"] == "ativa", campos.get("Ramo", "")
    return [texto for falha, texto in (
        (campos["Ato"] != "rotulo-afrouxa-regra", "Ato do alvo item: não é rotulo-afrouxa-regra"),
        (not SHA40.fullmatch(campos.get("Commit", "")), "Commit não é sha de 40 caracteres"),
        (not RAMO.fullmatch(ramo), "Ramo fora da forma"),
        (ativa and not no_ato, "ativa sem item <CARTAO> na frase do ato"),
        (ativa and bool(fora), f"ativa com ressalva ou palavra fora do vocabulário: {', '.join(fora)}")) if falha]


def git(raiz, *args):
    """Saída do `git` na raiz, ou None se ele falha (falha fechada); sem as variáveis GIT_* herdadas."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, env=env, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def ponta_do_ramo(raiz, ramo):
    """sha da ponta do `ramo` no clone (a ref do origin vale antes da local), ou ""."""
    return (git(raiz, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{ramo}^{{commit}}")
            or git(raiz, "rev-parse", "-q", "--verify", f"refs/heads/{ramo}^{{commit}}") or "").strip()


def fora_do_revisado(raiz, campos):
    """Por que o `Commit` não é o head do `Ramo` com os pareceres aprovados nele (E1); "" se é. Depois dele o `Ramo` só traz
    pareceres do próprio `Ramo` (renomeação conta como saída e entrada), os EXIGIDOS estão entre eles, e todo parecer do `Ramo`
    aprova o `Commit`, cada um na pasta do seu tipo. Parecer de devops, se houver, também tem de aprovar; a classe do diff segue
    conferida no merge."""
    ramo, commit = campos["Ramo"], campos["Commit"]
    ponta = ponta_do_ramo(raiz, ramo)
    if not ponta:
        return "Ramo sem ref no clone"
    if git(raiz, "merge-base", "--is-ancestor", commit, ponta) is None:
        return "Commit fora do Ramo"
    depois = git(raiz, "diff", "--no-renames", "--name-only", commit, ponta)
    if depois is None or any(not a.startswith(PARECERES) or frente(git(raiz, "show", f"{ponta}:{a}") or "").get("branch") != ramo
                             for a in depois.splitlines()):
        return "Commit não é o head: o Ramo muda depois dele"
    achados = git(raiz, "grep", "-l", "-F", "-e", f"branch: {ramo}", ponta, "--", *PARECERES) or ""
    lidos = [(a.split(":", 1)[-1], frente(git(raiz, "show", a) or "")) for a in achados.splitlines()]
    if any(not p for _, p in lidos):  # S5: achado sem cabeçalho legível (sem fecho, CRLF) barra em vez de sumir
        return "Parecer sem cabeçalho legível"
    if any(p.get("branch") == ramo and not caminho.startswith(PASTA_DO_TIPO.get(p.get("tipo"), "?")) for caminho, p in lidos):
        return "Parecer com tipo fora da sua pasta"
    pareceres = [p for _, p in lidos if p.get("branch") == ramo]
    if not set(EXIGIDOS) <= {p.get("tipo") for p in pareceres} or any(p.get("parecer") != "aprovado" or len(p.get("commit", "")) < 7
                            or not commit.startswith(p.get("commit", "")) for p in pareceres):
        return "Commit sem os pareceres aprovados nele"
    return ""


def slug(url):
    """`dono/repo` minúsculo de uma URL do GitHub (https ou ssh, com ou sem `.git`)."""
    return re.sub(r"^.*github\.com[/:]", "", url.strip().lower()).removesuffix(".git").strip("/")


def fora_do_forge(raiz):
    """Por que `raiz` não é o repositório do próprio Forge (Emenda ROTULO-PELO-TIME); "" se é. Projeto (`.forge/versao`) nunca
    é; o `origin` da raiz tem de ser o `repository` do plugin.json ao lado deste módulo (o manifesto da raiz não decide)."""
    try:
        meu = json.loads((Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        meu = None
    forge = slug(str(meu.get("repository", ""))) if isinstance(meu, dict) else ""
    if not forge or (Path(raiz) / ".forge" / "versao").exists():
        return "só vale no repositório do Forge: a raiz é projeto ou o plugin não diz o repositório"
    if slug(git(raiz, "config", "--get", "remote.origin.url") or "") != forge:
        return "só vale no repositório do Forge: o origin é outro"
    return ""


def frente(texto):
    """{campo: valor} do frontmatter de um parecer (ADR 0004): do `---` do topo até a primeira linha só `---`, o fecho do
    `ler_frontmatter` do forge-check (S5); `---` no começo de outra linha não fecha e, sem o fecho, vazio (o corpo não vale)."""
    linhas = texto.split("\n")
    if linhas[0] != "---":
        return {}
    for fecho, linha in enumerate(linhas[1:], 1):
        if linha.strip() == "---":
            return dict(campo.split(": ", 1) for campo in linhas[1:fecho] if ": " in campo)
    return {}


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
    if instante(campos["Hora-da-fala"]) > agora:  # A3: fala no futuro nunca autoriza, como no gravar
        return "adulterada", "Hora-da-fala no futuro"
    if any(n.startswith("R-") and c.get("Retira") == nome for n, (c, _) in lidos.items()):
        return "retirada", ""
    if campos["Validade"] == "uso-unico" and f"U-{nome}" in nomes:
        return "usada", ""
    if agora >= limite(campos):
        return "vencida", ""
    if "pedido" in normal(campos["Origem-da-validade"]) and f"F-{campos['Pedido']}" in nomes:
        return "vencida", "pedido fechado"
    fora = fora_do_forge(raiz) if campos["Ato"] in SO_NO_FORGE else ""
    if fora:
        return "inativa", fora
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


# G1.2: o `gravar` (itens 1 a 6 e E1 da ADR 0018). O corpo é só a mensagem lida da transcrição: nenhum texto vem do comando.
ATO_DO_TERMO = {"rotulo": "rotulo-afrouxa-regra", "afrouxa": "rotulo-afrouxa-regra", "main": "merge-main",
                "aperta": "so-aperta-com-seguranca",
                "homologacao": "rotulo-pelo-time"}
DIAS = ("segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo")
TETO_DA_MENSAGEM = 64 * 1024


class Recusa(Exception):
    pass


def casa_do_dono():
    """Pasta do usuário pelo banco de senhas (A4): o `HOME` do chamador não escolhe a pasta das transcrições."""
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def mensagem_do_dono(transcricao, uuid):
    """(texto, Hora-da-fala, sessão) da mensagem `uuid` digitada pelo dono, inteira, lida da transcrição da sessão em curso onde o
    Claude Code a grava, sem link; registro único, da sessão, com `origin` humano (positivo: resumo de compactação recusa)."""
    arq = Path(transcricao)
    if (arq.is_symlink() or not arq.is_file() or arq.suffix != ".jsonl" or arq.stem != os.environ.get("CLAUDE_CODE_SESSION_ID")
            or arq.resolve().parent.parent != (casa_do_dono() / ".claude" / "projects").resolve()):
        raise Recusa("transcrição não é o .jsonl comum da sessão em curso em ~/.claude/projects")
    achados = [r for r in map(json.loads, filter(str.strip, arq.read_text(encoding="utf-8").splitlines()))
               if isinstance(r, dict) and r.get("uuid") == uuid]
    r = achados[0] if len(achados) == 1 else {}
    conteudo = r["message"].get("content") if isinstance(r.get("message"), dict) else None
    if isinstance(conteudo, list) and len(conteudo) == 1 and isinstance(conteudo[0], dict) and conteudo[0].get("type") == "text":
        conteudo = conteudo[0].get("text")
    if (r.get("type") != "user" or r.get("origin") != {"kind": "human"} or any(r.get(c) for c in ("isMeta", "isSidechain",
            "isCompactSummary", "isVisibleInTranscriptOnly", "toolUseResult", "sourceToolUseID"))
            or r.get("sessionId") != arq.stem or not isinstance(conteudo, str) or conteudo.lstrip().startswith("<")
            or not conteudo.strip() or len(conteudo.encode("utf-8")) > TETO_DA_MENSAGEM):
        raise Recusa("a mensagem não é uma só, digitada pelo dono nesta sessão")
    return conteudo, r.get("timestamp", ""), arq.stem


def fim_do_termo(termo, fala):
    """Fim (UTC) do termo do item 6: 48 h sem prazo escrito, 7 dias no fim do pedido (que para também no `F-<Pedido>`). Data,
    dia da semana e "esta noite" dão None: esta etapa não lê o fuso do dono, e o prazo local nasce pendente (uso único)."""
    if termo in SEM_PRAZO_ESCRITO:
        return fala + datetime.timedelta(hours=48)
    return fala + datetime.timedelta(days=7) if "pedido" in termo else None


def leitura(texto, ato, alvos, fala):
    """Campos de escopo e validade lidos do texto todo (itens 5 e 6). Sem termo de ato ou com outro ato: Recusa."""
    norm = normal(texto)
    marcado = re.compile(rf"(?<![a-z0-9])(?:(?:pr|pull) ?#?|#)([1-9]\d*)(?![\w.])|(?<![\w.])(\d+\.\d+\.\d+)(?![\w.])"
                         rf"|(?<![a-z0-9])item ?({CARTAO.lower()})(?![\w-])")
    termo = re.compile(r"ate (?:o )?fim deste pedido|ate amanha|esta noite|\bhoje\b|\bhj\b|ate (?:a )?(?:" + "|".join(DIAS)
                       + r")(?:[- ]feira)?|ate \d{1,2}/\d{1,2}(?: \d{1,2}(?::\d{2}|h(?:\d{2})?))?(?![\w/:])")
    do_texto, fora_do_ato, atos = set(), False, set()
    for frase in FRASE.split(norm):
        achados = {f"pr:{p}" if p else f"versao:{v}" if v else f"item:{i}" for p, v, i in marcado.findall(frase)}
        termos = {ATO_DO_TERMO[w] for w in re.findall(r"[a-z0-9]+", marcado.sub(" ", frase)) if w in ATO_DO_TERMO}
        do_texto, atos, fora_do_ato = do_texto | achados, atos | termos, fora_do_ato or bool(achados and not termos)
    if ato not in atos:
        raise Recusa(f"o texto não tem termo do ato {ato}")
    termos = [re.sub(r"ate a |-feira| feira", lambda m: "ate " if m[0] == "ate a " else "", t) for t in termo.findall(norm)]
    resto = termo.sub(" ", norm)
    fins = [fim_do_termo(t, fala) for t in termos or ["sem termo"]]
    fixo = ato in SEM_PRAZO  # Emenda AUTORIZACOES-FIXAS (F2): sem alvo marcado nem termo de validade no texto; vocabulário próprio
    fora = fora_do_vocabulario(texto, marcado, VOCABULARIO_FIXO if fixo else VOCABULARIO)
    motivos = [m for falha, m in (
        (len(atos) > 1, "mais de um ato"),
        (do_texto != (set() if fixo else {normal(a) for a in alvos.split(", ")}), "alvos do texto diferentes dos declarados"),
        (fora_do_ato, "alvo fora da frase do ato"), (len(termos) > 1, "mais de um termo de validade"),
        (fixo and bool(termos), "termo de validade em ato fixo"), (None in fins, "prazo local sem fuso nesta etapa"),
        (bool(DATA_OU_HORA.search(resto) or {"amanha", "noite", "fim", *DIAS} & set(re.findall(r"[a-z]+", resto))),
         "termo de validade fora do mapa"),
        (bool(fora), f"palavra fora do vocabulário: {', '.join(fora)}"))
        if falha]
    fim = "" if None in fins or "termo de validade fora do mapa" in motivos else min(fins).strftime(DATA)
    validade = ({"Validade": "fixa", "Validade-utc": "fixa", "Fuso": "UTC", "Origem-da-validade": "sem prazo"} if fixo else
                {"Validade": f"ate:{fim}" if fim else "uso-unico", "Validade-utc": fim or "uso-unico", "Fuso": "UTC",
                 "Origem-da-validade": "; ".join(termos) or "sem termo"})
    return {**validade, "Estado-inicial": "pendente-confirmacao" if motivos else "ativa", "Motivo-da-pendencia": "; ".join(motivos) or "nenhum"}


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


def commit_do_ramo(raiz, ramo):
    """sha de 40 do commit que o parecer de review do `ramo` aprova (E1: o `gravar` lê o sha dos pareceres), ou "". Parecer de
    outro ramo ou que não aprova esse commit cai depois, no `fora_do_revisado` (falha fechada)."""
    achados = git(raiz, "grep", "-l", "-F", "-e", f"branch: {ramo}", ponta_do_ramo(raiz, ramo), "--", PASTA_DO_TIPO["review"]) or ""
    curtos = sorted(frente(git(raiz, "show", arq) or "").get("commit", "") for arq in achados.splitlines())
    curto = curtos[0] if curtos else ""
    valido = re.fullmatch(r"[0-9a-f]{7,40}", curto)  # nunca opção do git nem nome de ref
    return (git(raiz, "rev-parse", "-q", "--verify", f"{curto}^{{commit}}") or "").strip() if valido else ""


def gravar_novo(arq, conteudo):
    """Arquivo novo aberto com `x`, sem seguir link (item 1): FileExistsError se já existe."""
    fd = os.open(arq, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(conteudo)


def pedido_aberto(raiz, pedido, pedido_existe):
    """A6: o `Pedido` tem arquivo no registro de pedidos e não tem o `F-<Pedido>` gravado; sem como conferir, não está aberto."""
    return bool(pedido_existe and pedido_existe(pedido)) and not os.path.lexists(Path(raiz) / PASTA / f"F-{pedido}")


def concessao_lida(raiz, a, gravador, agora, pedido_existe=None):
    """(campos, corpo) da concessão da mensagem `a.mensagem`, ou Recusa com o que o leitor (G1.1) recusaria."""
    if not re.fullmatch(r"[0-9a-f]+(?:-[0-9a-f]+)*", a.mensagem):
        raise Recusa("--mensagem não é um uuid")
    texto, carimbo, sessao = mensagem_do_dono(a.transcricao, a.mensagem)
    if not agora - datetime.timedelta(hours=48) <= (fala := instante(carimbo)) <= agora:
        raise Recusa("Hora-da-fala no futuro ou fora da sessão (mais de 48 h)")
    campos = {"Id": "A-0", "Ato": a.ato, "Alvos": a.alvos, **leitura(texto, a.ato, a.alvos, fala),
              "Mensagem": a.mensagem, "Hora-da-fala": carimbo, "Sessao": sessao, "Pedido": a.pedido, "Sha256": sha(texto),
              "Gravado-por": gravador, "Autoriza": AUTORIZA}
    item = campos["Alvos"].startswith("item:")
    if item:
        campos.update(Commit=commit_do_ramo(raiz, a.ramo), Ramo=a.ramo)  # ref sob refs/: nunca opção do git
    achados = problemas(campos, texto, gravador) or ([fora_do_revisado(raiz, campos)] if item else [])
    if any(achados):
        raise Recusa("; ".join(achados))
    if "pedido" in normal(campos["Origem-da-validade"]) and not pedido_aberto(raiz, a.pedido, pedido_existe):
        motivos = [m for m in (campos["Motivo-da-pendencia"],) if m != "nenhum"] + ["pedido inexistente ou fechado"]
        campos.update({"Estado-inicial": "pendente-confirmacao", "Motivo-da-pendencia": "; ".join(motivos)})
    return campos, texto


def cmd_gravar(raiz, a, ctx, agora=None):
    """Grava `A-<n>` com a mensagem inteira do dono (itens 1 a 6); `M-<uuid>` com `x` antes: uma concessão por mensagem."""
    pasta = Path(raiz) / PASTA
    try:
        campos, texto = concessao_lida(raiz, a, ctx["gravador"], agora or datetime.datetime.now(UTC), ctx.get("pedido_existe"))
        if pasta.parent.is_symlink() or pasta.is_symlink():
            raise Recusa(f"{PASTA}: não é pasta comum")
        pasta.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            gravar_novo(pasta / f"M-{a.mensagem}", "")
        except FileExistsError:
            raise Recusa("a mensagem já gerou concessão") from None
        campos["Id"] = f"A-{1 + max((int(x.name[2:]) for x in pasta.glob('A-*') if x.name[2:].isdigit()), default=0)}"
        gravar_novo(pasta / campos["Id"], "".join(f"{k}: {v}\n" for k, v in campos.items()) + "\n" + texto)  # corrida: recusa
    except (Recusa, ValueError, OSError) as e:  # JSON, UTF-8 e carimbo ilegíveis são ValueError; A-<n> que já existe, OSError
        print(ctx["seguro"](f"autorizacao: recusada: {e}"))
        return 1
    print(ctx["seguro"](f"autorizacao: {campos['Id']} gravada · {campos['Estado-inicial']} ({campos['Motivo-da-pendencia']}) · "
                        f"{campos['Ato']} · {campos['Alvos']} · validade {campos['Validade']} {campos['Fuso']}"))
    return 0


def cmd_ler_ato(raiz, ctx, agora, ato):
    """Emenda AUTORIZACOES-FIXAS (F3), pelo `ler --ato <ato sem prazo>`: a concessão ativa mais nova do ato; rc 1 sem ela (erro de
    leitura na pasta deixa todas inativas: falha fechada)."""
    lista, _ = concessoes(raiz, ctx["gravador"], agora)
    ativas = [(nome, campos) for nome, campos, _, est, _ in lista if est == "ativa" and campos["Ato"] == ato]
    if not ativas:
        print(f"autorizacao: nenhuma {ato} ativa")
        return 1
    nome, campos = ativas[-1]
    print(f"autorizacao: {nome} sha256 {campos['Sha256']} · {ato} · {campos['Alvos']}")
    return 0


def executar(a, raiz, ctx):
    if a.acao == "ler" and a.ato in SEM_PRAZO:  # o forge-check autorizacao ler --ato <ato sem prazo> (F3; ROTULO-PELO-TIME)
        return cmd_ler_ato(raiz, ctx, datetime.datetime.now(UTC), a.ato)
    return cmd_gravar(raiz, a, ctx) if a.acao == "gravar" else cmd_ler(raiz, ctx)
