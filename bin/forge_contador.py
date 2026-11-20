"""Forge: a contagem do contador da versão (AE2 C1, v0478 E56.1; desenho v0479-ae2-contador, seção 4.1).

Quais cartões foram entregues por PR mesclado na develop desde a marca, a maior tag `v<n>.<n>.<n>` do repositório (D4: a
versão em curso é a marca com o patch + 1). Os PRs são, na linha de primeiro pai, os merges `Merge pull request #N from ...`
(cartões lidos no intervalo `pai1..pai2`) e os squash `... (#N)` (cartões lidos na própria mensagem); os cartões, as linhas
`Cartão: <ID>` (entrega) e `Cartão-parcial: <ID>` (cita, não entrega; D3). Uma função só para o contador, o `quadro
sincronizar`, a citação e a medida: a mesma contagem por construção. Só leitura do git local, sem rede, só biblioteca padrão.
O teto da versão (C3) vem do `teto_da_versao` da configuração do projeto, com o parâmetro `padrao` (20) quando falta ou não vale.
"""
import json
import os
import re
import stat
import subprocess
import unicodedata

GIT_TIMEOUT_S = 10
REF_PADRAO = "origin/develop"
SEM_MARCA = "antes da primeira versão"
TAG_DE_VERSAO = re.compile(r"v(\d{1,9})\.(\d{1,9})\.(\d{1,9})")  # tag fora da forma não é marca
MERGE_DE_PR = re.compile(r"Merge pull request #(\d{1,9}) from \S+")
SQUASH_DE_PR = re.compile(r".*\(#(\d{1,9})\)")
LINHA_DE_CARTAO = re.compile(r"(cartão(-parcial)?):[ \t]*(.*?)[ \t\r]*", re.I)
ID_DO_CARTAO = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")  # a forma do atributo de pedido do `movimento`
TETO_DE_CITACOES = 10  # D9: por PR; acima, só as 10 primeiras, com aviso
TETO_DA_VERSAO = 20  # cartões por versão (diretriz 37): o padrão quando a configuração não traz um valor que vale
FAIXA_DO_TETO = range(1, 201)
TETO_DA_CONFIG = 65536  # bytes lidos da configuração
CONFIG = (".forge", "config.json")


class ContagemIndisponivel(Exception):
    """A contagem não sai (sem git, ref ausente ou inválida, git que trava): quem chama diz `não verificável`, nunca um número."""


def _git(raiz, *args):
    """stdout do `git -C raiz ...` em texto (byte inválido vira U+FFFD), sem as GIT_* herdadas e com limite de tempo."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(raiz), "-c", "log.showSignature=false", *args], capture_output=True, env=env,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise ContagemIndisponivel(f"git não respondeu ({type(e).__name__})") from e
    if r.returncode:
        raise ContagemIndisponivel(f"git {args[0]} saiu com {r.returncode}")
    return r.stdout.decode("utf-8", "replace")


def _commits(raiz, intervalo, primeira_linha=False):
    """[(sha, [pais], mensagem)] do `intervalo`, do mais antigo ao mais novo; registros separados por NUL (`-z`), que a mensagem
    não traz, então nenhum texto de commit forja outro registro."""
    saida = _git(raiz, "log", *(["--first-parent"] if primeira_linha else []), "--reverse", "-z", "--format=%H %P%n%B",
                 "--end-of-options", intervalo, "--")
    commits = []
    for registro in saida.split("\0"):
        cabeca, _, mensagem = registro.lstrip("\n").partition("\n")
        if cabeca:
            sha, *pais = cabeca.split()
            commits.append((sha, pais, mensagem))
    return commits


def marca(raiz):
    """(tag, versão em curso) da maior tag `v<n>.<n>.<n>` do repositório; (None, SEM_MARCA) sem tag na forma. Entre todas, não
    só as alcançáveis da develop: no fluxo develop → homolog → main a tag fica no merge da main, fora da linha da develop, e o
    intervalo `<tag>..<ref>` já tira da contagem o que a main recebeu."""
    tags = [m for t in _git(raiz, "tag", "--list", "v*").split() if (m := TAG_DE_VERSAO.fullmatch(t))]
    if not tags:
        return None, SEM_MARCA
    m = max(tags, key=lambda t: tuple(map(int, t.groups())))
    maior, menor, patch = map(int, m.groups())
    return m.group(0), f"{maior}.{menor}.{patch + 1}"


def citacoes(mensagens, avisos, rotulo):
    """(cartões, parciais) das linhas `Cartão:` e `Cartão-parcial:` das `mensagens`, na ordem e sem repetir (casefold). ID fora da
    forma (barra, controle, `Cf`, acima de 80) é recusado com aviso e nunca segue; acima de TETO_DE_CITACOES, só as primeiras."""
    achados = {False: {}, True: {}}
    for linha in (l for msg in mensagens for l in unicodedata.normalize("NFC", msg).split("\n")):
        m = LINHA_DE_CARTAO.fullmatch(linha)
        if not m:
            continue
        valor, parcial = m.group(3), bool(m.group(2))
        if not ID_DO_CARTAO.fullmatch(valor):
            avisos.append(f"{rotulo}: citação recusada, fora da forma: {ascii(valor[:40])}")
            continue
        if valor.casefold() in achados[parcial]:
            continue
        if len(achados[False]) + len(achados[True]) >= TETO_DE_CITACOES:
            avisos.append(f"{rotulo}: mais de {TETO_DE_CITACOES} citações de cartão; só as {TETO_DE_CITACOES} primeiras contam")
            break
        achados[parcial][valor.casefold()] = valor
    return list(achados[False].values()), list(achados[True].values())


def contar(raiz, ref=REF_PADRAO):
    """A contagem desde a marca: {marca, versao, prs: [{numero, sha, cartoes, parciais}], entregues, avisos}. `entregues` são
    os IDs com `Cartão:` em algum PR (o mesmo cartão em dois PRs conta uma vez). ContagemIndisponivel se não sai."""
    if not ref or ref.startswith("-"):
        raise ContagemIndisponivel(f"ref inválida: {ascii(ref)}")
    try:
        _git(raiz, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{ref}^{{commit}}")
    except ContagemIndisponivel as e:
        raise ContagemIndisponivel(f"ref ausente: {ref} ({e})") from e
    tag, versao = marca(raiz)
    avisos, prs, entregues = [], [], {}
    for sha, pais, mensagem in _commits(raiz, f"{tag}..{ref}" if tag else ref, primeira_linha=True):
        assunto = mensagem.split("\n", 1)[0]
        if len(pais) == 2 and (m := MERGE_DE_PR.fullmatch(assunto)):
            mensagens = [c[2] for c in _commits(raiz, f"{pais[0]}..{pais[1]}")]
        elif len(pais) == 1 and (m := SQUASH_DE_PR.fullmatch(assunto)):
            mensagens = [mensagem]
        else:
            continue
        cartoes, parciais = citacoes(mensagens, avisos, f"PR #{m.group(1)}")
        prs.append({"numero": int(m.group(1)), "sha": sha, "cartoes": cartoes, "parciais": parciais})
        for cartao in cartoes:
            entregues.setdefault(cartao.casefold(), cartao)
    return {"marca": tag, "versao": versao, "prs": prs, "entregues": list(entregues.values()), "avisos": avisos}


def ler_teto(raiz, padrao=TETO_DA_VERSAO):
    """(teto, aviso): o `teto_da_versao` da configuração de `raiz` (CONFIG) se é inteiro de 1 a 200; senão o `padrao`. Sem o
    arquivo ou sem a chave, aviso None; configuração que não abre, por link, grande, fora de objeto JSON ou valor que não vale
    (booleano, texto, fora da faixa) dão o aviso que quem chama manda ao stderr (CONFIG-TETO-SEM-GUARDA), nunca traceback."""
    try:
        fd = os.open(os.path.join(raiz, *CONFIG), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return padrao, None
    except OSError as e:
        return padrao, f"contador: {'/'.join(CONFIG)} não abre ({e.strerror}); teto {padrao}"
    try:  # pasta ou fifo não são lidas: o tipo é conferido no fd aberto, antes da leitura
        dados = os.read(fd, TETO_DA_CONFIG + 1) if stat.S_ISREG(os.fstat(fd).st_mode) else b""
    finally:
        os.close(fd)
    try:
        config = json.loads(dados.decode("utf-8")) if len(dados) <= TETO_DA_CONFIG else None
    except (ValueError, RecursionError):
        config = None
    if not isinstance(config, dict):
        return padrao, f"contador: {'/'.join(CONFIG)} não é objeto JSON regular de até {TETO_DA_CONFIG} bytes; teto {padrao}"
    if "teto_da_versao" not in config:
        return padrao, None
    valor = config["teto_da_versao"]
    if type(valor) is not int or valor not in FAIXA_DO_TETO:
        return padrao, f"contador: teto_da_versao {ascii(valor)[:30]} fora de inteiro de 1 a 200; teto {padrao}"
    return valor, None
