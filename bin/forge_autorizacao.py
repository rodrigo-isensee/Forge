"""Forge: as autorizações do dono gravadas (ADR 0018, G1.1a: formato e integridade). Só biblioteca padrão; só leitura, nada barra.

`forge-check autorizacao ler` lista cada concessão de `<raiz principal>/.forge/autorizacoes/` com a integridade e a mensagem inteira
do dono. O estado pela validade (Fuso, Validade-utc, teto, confirmação, retirada e uso) vem no G1.1b; gravar e travar, no G1.2 em
diante. Erro ao ler qualquer evento vale como "não há autorização" (falha fechada).
"""
import hashlib
import os
import re
import stat
from pathlib import Path

PASTA = Path(".forge") / "autorizacoes"
CAMPOS = ("Id", "Ato", "Alvos", "Validade", "Validade-utc", "Fuso", "Origem-da-validade", "Estado-inicial", "Motivo-da-pendencia",
          "Mensagem", "Hora-da-fala", "Sessao", "Sha256", "Gravado-por", "Autoriza")
AUTORIZA = "só o ato e os alvos acima, até a validade; não amplia outra regra (R-DECISAO)"
ATOS = ("rotulo-afrouxa-regra", "merge-main")
ALVOS = re.compile(r"pr:[1-9]\d*(, pr:[1-9]\d*)*|versao:\d+\.\d+\.\d+")
ESTADOS_INICIAIS = ("ativa", "pendente-confirmacao")
NOME = re.compile(r"A-\d+|C-A-\d+|R-\d+|U-A-\d+(-\d+)?|M-[0-9a-f-]+")
LIDOS = ("A-", "C-", "R-")  # U- e M- valem pela presença (só apertam)
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


def problemas(campos, corpo, gravador):
    """Por que a concessão não é íntegra; [] se é (item 7 da ADR 0018; a validade é do G1.1b)."""
    faltam = [c for c in CAMPOS if c not in campos]
    if faltam:
        return [f"campo ausente: {', '.join(faltam)}"]
    return [texto for falha, texto in (
        (campos["Sha256"] != sha(corpo), "Sha256 não bate com o corpo"),
        (campos["Gravado-por"] != gravador, "Gravado-por não é o forge-check carregado"),
        (campos["Ato"] not in ATOS, "Ato fora da lista"),
        (not ALVOS.fullmatch(campos["Alvos"]), "Alvos fora da forma"),
        (campos["Estado-inicial"] not in ESTADOS_INICIAIS, "Estado-inicial fora da lista"),
        (campos["Autoriza"] != AUTORIZA, "Autoriza fora do texto fixo")) if falha]


def cmd_ler(raiz, ctx):
    seguro = ctx["seguro"]
    _, lidos, erros = eventos(Path(raiz) / PASTA)
    adulteradas = 0
    for nome in sorted((n for n in lidos if n.startswith("A-")), key=lambda n: int(n[2:])):
        campos, corpo = lidos[nome]
        achados = problemas(campos, corpo, ctx["gravador"])
        adulteradas += bool(achados)
        print(seguro(f"autorizacao: {nome} · {'adulterada (' + '; '.join(achados) + ')' if achados else 'íntegra'} · "
                     f"{campos.get('Ato', '?')} · {campos.get('Alvos', '?')} · validade {campos.get('Validade', '?')} "
                     f"{campos.get('Fuso', '?')} = {campos.get('Validade-utc', '?')} UTC"))
        print("\n".join(f"> {seguro(linha)}" for linha in corpo.split("\n")))
    for erro in erros:
        print(seguro(f"autorizacao: erro: {erro}"))
    print(f"autorizacao: {adulteradas} adulterada(s), {len(erros)} erro(s) de leitura; estado pela validade no G1.1b; nada barra")
    return 1 if erros or adulteradas else 0


def executar(a, raiz, ctx):
    return cmd_ler(raiz, ctx)
