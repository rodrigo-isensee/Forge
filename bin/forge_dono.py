"""Forge: a conversa com o dono e entre sessões, gravada no disco (0.44.1). Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um destes roda:
- `decisoes --pedido P --resposta "1a 2c"` (O4): a resposta curta do dono lida contra a última `PERGUNTA AO DONO` do pedido.
- `anotar` e `brief selar` (0.45.7, E6 a E8): a gramática da origem da recomendação de corte, a marca de recomendação revertida e a
  conferência da decisão do dono (`confere=`), lidas aqui e chamadas pelo forge-check.
  Opções `1a)`, `1b)`...; `[recomendada]` e `[reversível]` ou `[irreversível]` no texto da opção (com ou sem acento, qualquer
  caixa). Vocabulário fechado: os códigos da pergunta e as palavras de PALAVRAS (aprova a recomendada marcada `[reversível]` de
  cada questão sem código). O ambíguo volta como pergunta (rc 1); a palavra solta nunca vale para opção irreversível nem sem marca. Só lê: o Jarvis grava a decisão com `forge-check anotar`.
- `pedido fala --gravar|--ler --pedido P` (S2): as palavras do dono, literais, com sha256, em docs/pedidos/<P>/fala-<stamp>.md;
  gravar não amplia autorização (o registro diz isso) e ler confere o hash de cada fala.
- `recado --para RAIZ --texto T` e `recado --confirmar [ARQ]` (S8): texto entre sessões em <RAIZ>/.forge/recados/, com
  cabeçalho (raiz de destino, versão do plugin, sha256); a sessão de outra raiz ou de outra versão recusa.
- `pausa --gravar --retoma-em H --onde T` e `pausa --retomar [--esperar]` (X1): onde parou na pausa por limite de uso (Q1), em
  .forge/pausa.json, e a retomada quando a cota renova. Não contorna limite nem troca de conta: só espera o horário dado.
- `cmd_abertas` (diretriz 29, v047 E1.135): as perguntas abertas ao dono de todos os pedidos e do painel `Aguardando o dono` do
  KANBAN.md, por peso; só leitura. O registro no forge-check (`decisoes --abertas`) vem depois, em outra entrega.
"""
import datetime
import hashlib
import json
import os
import re
import time
import unicodedata
from pathlib import Path

PALAVRAS = frozenset({"aprovo", "aprovado", "aprovada", "sim", "ok"})  # O4: a palavra solta aprova a recomendada
CODIGO = re.compile(r"(\d{1,2})([a-z])")
OPCAO = re.compile(r"(?<!\w)(\d{1,2})([a-z])\)")
PERGUNTA = re.compile(r"^PERGUNTA AO DONO \(([^)]*)\): (?:.*?→ )?\"(.*)\"\s*$", re.M)
TETO_DO_TEXTO = 64 * 1024  # bytes da fala e do recado
CABECALHO = re.compile(r"^([A-Za-z0-9-]+): (.*)$", re.M)
ESPERA_MAXIMA = datetime.timedelta(hours=24)  # X1: a cota renova em horas; mais que isso é engano no --retoma-em


def _agora():
    return datetime.datetime.now().astimezone()


def _sha(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _recusa_do_texto(texto):
    """Motivo para recusar o texto literal (vazio, grande ou com NUL), ou None."""
    if not texto.strip():
        return "--texto vazio"
    if len(texto.encode("utf-8")) > TETO_DO_TEXTO or "\x00" in texto:
        return f"--texto passa de {TETO_DO_TEXTO} bytes ou tem NUL"
    return None


def _gravar_novo(pasta, prefixo, conteudo):
    """Grava `conteudo` num arquivo novo `<prefixo>-<stamp>.md` da `pasta` (aberto com `x`, nunca sobrescreve; sem seguir link)."""
    if pasta.is_symlink() or pasta.parent.is_symlink():
        raise OSError(f"{pasta.name} é link simbólico")
    pasta.mkdir(parents=True, exist_ok=True, mode=0o700)
    base = _agora().strftime("%Y%m%d-%H%M%S")
    for n in range(100):
        arq = pasta / f"{prefixo}-{base}-{n:02d}.md"
        try:
            with open(arq, "x", encoding="utf-8") as f:
                f.write(conteudo)
            return arq
        except FileExistsError:
            continue
    raise OSError("cem arquivos no mesmo segundo")


def _gravar_seguro(arq, conteudo):
    """X1 (review da 0.44.1): grava `arq` sem seguir link (nem na pasta nem no arquivo): escreve num temporário novo da mesma pasta
    (O_CREAT|O_EXCL|O_NOFOLLOW, 0600) e o troca de lugar com os.replace, que substitui o próprio link, nunca o alvo dele."""
    if arq.parent.is_symlink() or arq.parent.parent.is_symlink() or arq.is_symlink():
        raise OSError(f"{arq.name} ou a pasta dele é link simbólico")
    arq.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = arq.with_name(f".{arq.name}.{os.getpid()}.tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(conteudo)
        os.replace(temp, arq)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _ler_registro(arq):
    """({campo: valor} do cabeçalho, corpo) de uma fala ou recado: cabeçalho até a primeira linha vazia."""
    cabecalho, _, corpo = arq.read_text(encoding="utf-8").partition("\n\n")
    return dict(CABECALHO.findall(cabecalho)), corpo.removesuffix("\n")


# ---- O4: resposta do dono por código curto ----

def opcoes_da_pergunta(literal):
    """{questão: {letra: texto da opção}} dos códigos `Na)` do literal; o texto vai até o próximo código."""
    achados = list(OPCAO.finditer(literal))
    questoes = {}
    for m, fim in zip(achados, [m.start() for m in achados[1:]] + [len(literal)]):
        questoes.setdefault(int(m.group(1)), {})[m.group(2)] = literal[m.end():fim].strip()
    return questoes


def marcas(texto):
    """O4 (review da 0.44.1): as marcas `[...]` da opção, sem acento e em minúsculas (`[Irreversivel]` é `irreversivel`)."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return {m.strip().lower() for m in re.findall(r"\[([^\[\]]{1,40})\]", sem_acento)}


def ler_resposta(questoes, resposta):
    """(escolhas {questão: letra}, ambiguidades [texto]). Fora do vocabulário, código que não existe, duas opções para a mesma
    questão, palavra solta sem recomendação única, sobre opção irreversível ou sem a marca `[reversível]` (com ou sem acento, em
    qualquer caixa): ambiguidade. A palavra solta só escolhe a recomendada marcada reversível; o resto, só o código."""
    escolhas, ambiguas, solta = {}, [], False
    for token in filter(None, re.split(r"[\s,;.]+", resposta.lower())):
        codigo = CODIGO.fullmatch(token)
        if token in PALAVRAS:
            solta = True
        elif not codigo:
            ambiguas.append(f"`{token[:40]}` fora do vocabulário (códigos da pergunta ou {', '.join(sorted(PALAVRAS))})")
        elif codigo.group(2) not in questoes.get(int(codigo.group(1)), {}):
            ambiguas.append(f"o código {token} não existe na pergunta")
        elif escolhas.setdefault(int(codigo.group(1)), codigo.group(2)) != codigo.group(2):
            ambiguas.append(f"duas opções para a questão {codigo.group(1)}")
    for n in sorted(set(questoes) - set(escolhas)) if solta else ():
        recomendadas = [l for l, texto in questoes[n].items() if "[recomendada]" in texto]
        if len(recomendadas) != 1:
            ambiguas.append(f"a questão {n} não tem uma recomendada só: responda com o código")
        elif "irreversivel" in marcas(questoes[n][recomendadas[0]]):
            ambiguas.append(f"a questão {n} é irreversível: a palavra solta não vale, responda com o código")
        elif "reversivel" not in marcas(questoes[n][recomendadas[0]]):
            ambiguas.append(f"a questão {n} não marca a recomendada como [reversível]: a palavra solta não vale, responda com o código")
        else:
            escolhas[n] = recomendadas[0]
    return escolhas, ambiguas


# ---- E6, E7 e E8 (0.45.7): origem da recomendação de corte, recomendação revertida e conferência da decisão ----

CAMPOS_DE_ORIGEM = {"origem": "origem", "procurado": "procurado", "seguir": "seguir", "nao seguir": "não seguir"}
CORTE = re.compile(r"(?<![a-z])(?:cort(?!esi)|descart|afrouxa|retir|remov|apag|aposent|abandon|deslig|deix\S*(?:\s+\S+){0,3}?\s+de\s+lado)")
# sobre o texto sem acento, em casefold; `cortesia` não é corte; `deixar (o teste) de lado` e `desligar` são
LUGARES_DO_NAO_ACHADA = 2  # `origem: não achada` só vale com `procurado:` de 2 lugares ou mais
MARCA_REVERTIDA = "recomendação revertida"
CRITERIOS = ("rapido", "seguro", "barato", "mede")
CONFERE = re.compile(r"confere=(rapido|seguro|barato|mede|nao-passa)")
ENTRADA_DA_CONFERENCIA = datetime.datetime(2026, 11, 12, 0, 0)  # PQ-A3: decisão do dono antes disto nunca trava o selar
FORJA = re.compile(r"atributos\s*:|(?:revertida|confere|origem|forge)\s*=")  # sobre o texto em NFKC, sem `Cf`, em casefold
DATA_DA_LINHA = re.compile(r"(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?")
FRASE_DA_DECISAO = "DECISÃO DO DONO"
FRASE_DA_PERGUNTA = "PERGUNTA AO DONO ("
MARCA_DE_ATRIBUTOS = " · atributos: "  # a mesma do forge-check


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).casefold()


def recusa_da_forja(texto):
    """E7 e E8 (PQ-A4): motivo para recusar o literal ou o contexto que escreve `atributos:`, `revertida=`, `confere=`, `origem=` ou
    `forge=` (a marca só nasce da ferramenta), ou None."""
    normal = "".join(c for c in unicodedata.normalize("NFKC", texto or "") if unicodedata.category(c) != "Cf").casefold()
    return "a marca `atributos:` e as chaves `revertida=`, `confere=`, `origem=` e `forge=` só a ferramenta grava" if FORJA.search(normal) else None


def campos_de_origem(texto):
    """E6: {campo: valor} dos campos `origem:`, `procurado:`, `seguir:` e `não seguir:` do texto da opção, separados por ` · `."""
    campos = {}
    for segmento in texto.split("·"):
        achado = re.match(r"\s*(origem|procurado|seguir|nao seguir)\s*:", _sem_acento(segmento))
        if achado:
            campos[achado.group(1)] = segmento.partition(":")[2].strip()
    return campos


def _sem_campos(texto):
    return " ".join(s for s in texto.split("·") if not re.match(r"\s*(origem|procurado|seguir|nao seguir)\s*:", _sem_acento(s)))


def e_corte(texto):
    """E6: a opção recomenda cortar: raiz do léxico fora dos campos de origem; a marca `[corte]` cai na raiz `cort`."""
    return CORTE.search(_sem_acento(_sem_campos(texto))) is not None


def falta_de_origem(campos):
    """E6: o que falta aos campos de origem, ou None."""
    faltam = [nome for chave, nome in CAMPOS_DE_ORIGEM.items() if not campos.get(chave)]
    if faltam:
        return "recomendação de corte sem " + ", ".join(f"`{nome}:`" for nome in faltam)
    lugares = [p for p in re.split(r",|;|\s+e\s+", campos["procurado"]) if p.strip()]
    if _sem_acento(campos["origem"]).strip(" .") == "nao achada" and len(lugares) < LUGARES_DO_NAO_ACHADA:
        return f"`origem: não achada` pede `procurado:` com {LUGARES_DO_NAO_ACHADA} lugares ou mais"
    return None


def recusa_de_corte(questoes, escolhas=None):
    """E6: [motivo] de cada opção `[recomendada]` de corte sem a origem completa; com `escolhas`, só a recomendada escolhida
    (PQ-A2: a opção de corte que o dono escolhe sem ser a recomendada é dele e leva a marca da E7)."""
    motivos = []
    for n in sorted(questoes):
        for letra, texto in questoes[n].items():
            if "recomendada" not in marcas(texto) or (escolhas is not None and escolhas.get(n) != letra) or not e_corte(texto):
                continue
            if motivo := falta_de_origem(campos_de_origem(texto)):
                motivos.append(f"{n}{letra}: {motivo}")
    return motivos


def divergencia(questoes, escolhas):
    """E7: {questão: (recomendada, escolhida)} onde o dono escolheu outra que a única `[recomendada]` da questão."""
    saida = {}
    for n, letra in escolhas.items():
        recomendadas = [l for l, texto in questoes.get(n, {}).items() if "recomendada" in marcas(texto)]
        if len(recomendadas) == 1 and recomendadas[0] != letra:
            saida[n] = (recomendadas[0], letra)
    return saida


def _valor(texto):
    return " ".join(re.sub(r"[;=·|\x00-\x1f\x7f]", " ", texto).split())[:160]


def ultima_pergunta(texto):
    perguntas = PERGUNTA.findall(texto)
    return opcoes_da_pergunta(perguntas[-1][1]) if perguntas else {}


def leitura_da_decisao(pedido_txt, literal):
    """E6 e E7: (atributos {revertida, origem}, recusa ou None) da decisão cujo literal é só códigos (`1b 2a`), lida contra a
    última `PERGUNTA AO DONO`; em prosa, ({}, None) e a decisão conta como não lida."""
    tokens = list(filter(None, re.split(r"[\s,;.]+", literal.lower())))
    if not tokens or not all(CODIGO.fullmatch(t) for t in tokens):
        return {}, None
    questoes = ultima_pergunta(pedido_txt)
    escolhas, ambiguas = ler_resposta(questoes, literal) if questoes else ({}, ["o pedido não tem `PERGUNTA AO DONO` com opções `1a)`"])
    if ambiguas or not escolhas:
        return {}, f"o literal em códigos não se lê contra a última pergunta ({'; '.join(ambiguas)}); leia com `decisoes --resposta`"
    if motivos := recusa_de_corte(questoes, escolhas):
        return {}, "; ".join(motivos) + "; volta ao dono como pergunta com a origem"
    atributos = {}
    if diverge := divergencia(questoes, escolhas):
        atributos["revertida"] = ",".join(f"{n}{e}-contra-{n}{r}" for n, (r, e) in sorted(diverge.items()))
    origens = [o for n, l in sorted(escolhas.items()) if (o := campos_de_origem(questoes[n][l]).get("origem"))]
    if origens:
        atributos["origem"] = _valor(", ".join(origens))
    return atributos, None


def alternativa(pedido_txt, literal):
    """E8: o texto (sem marcas nem campos de origem) da `[recomendada]` única de cada questão da última `PERGUNTA AO DONO`; com o
    literal em códigos, só das questões que ele responde. None sem recomendada."""
    questoes = ultima_pergunta(pedido_txt)
    tokens = list(filter(None, re.split(r"[\s,;.]+", literal.lower())))
    if tokens and all(CODIGO.fullmatch(t) for t in tokens):
        respondidas = {int(CODIGO.fullmatch(t).group(1)) for t in tokens}
        questoes = {n: q for n, q in questoes.items() if n in respondidas}
    textos = []
    for n in sorted(questoes):
        recomendadas = [t for t in questoes[n].values() if "recomendada" in marcas(t)]
        if len(recomendadas) == 1:
            textos.append(" ".join(re.sub(r"\[[^\[\]]{1,40}\]", " ", _sem_campos(recomendadas[0])).split()).strip(" ·"))
    return "; ".join(t for t in textos if t)[:160] or None


def modelo_da_pergunta(literal, pedido_txt=""):
    """E8: as linhas do modelo da `PERGUNTA AO DONO` para a decisão que não passa no critério (`confere=nao-passa`); a alternativa é
    o texto da `[recomendada]` da última pergunta (sem ela, o Jarvis escreve a dele no lugar indicado)."""
    texto = alternativa(pedido_txt, literal) or "<a do Jarvis: a última pergunta não tem [recomendada]>"
    return ["decisao: confere=nao-passa: antes de cumprir, pergunte ao dono com `forge-check anotar --tipo pergunta`; modelo:",
            f"pergunta: 1a) alternativa: {texto} [recomendada] · origem: <ref> · procurado: <onde> · seguir: <custo> · "
            f"não seguir: <custo> · 1b) seguir a decisão \"{literal[:120]}\""]


def atributos_da_linha(linha):
    """{chave: valor} da marca ` · atributos: ` no fim da linha (só o último segmento)."""
    _, marca, resto = linha.rstrip().rpartition(MARCA_DE_ATRIBUTOS)
    if not marca:
        return {}
    return {k.strip(): v.strip() for k, _, v in (p.partition("=") for p in resto.split(";"))}


def data_da_linha(linha):
    """O instante da decisão (prefixo `AAAA-MM-DD[ HH:MM]:` ou `(AAAA-MM-DD HH:MM)` logo depois da frase), ou None sem data."""
    achado = DATA_DA_LINHA.search(linha[:linha.find(FRASE_DA_DECISAO) + len(FRASE_DA_DECISAO) + 19])  # só linha de decisão chega aqui
    if achado is None:
        return None
    return datetime.datetime.fromisoformat(f"{achado.group(1)} {achado.group(2) or '00:00'}")


def pendencias_da_conferencia(texto, e_decisao, entrada=ENTRADA_DA_CONFERENCIA):
    """E8: [(linha, motivo)] das decisões do dono a partir de `entrada` sem `confere=` de critério (ausente, vazio, fora do vocabulário
    ou `nao-passa`) que não têm, depois delas, uma `PERGUNTA AO DONO` e, depois dela, uma decisão com `confere=` de critério."""
    abertas, perguntadas = {}, {}
    for n, linha in enumerate(texto.split("\n"), 1):
        if linha.strip().lstrip("-*> ").startswith(FRASE_DA_PERGUNTA):
            perguntadas.update(abertas)
            abertas = {}
        elif e_decisao(linha):
            valor = atributos_da_linha(linha).get("confere", "")
            passa = valor in CRITERIOS
            if passa:
                perguntadas = {}
            quando = data_da_linha(linha)
            if not passa and quando is not None and quando >= entrada:
                abertas[n] = f"`confere={valor}` sem pergunta e resposta do dono depois" if valor else "sem `confere=`"
    return sorted({**abertas, **perguntadas}.items())


def _devolver(questoes, ctx):
    for n in sorted(questoes):
        print(f"pergunta: {n}) " + " · ".join(f"{n}{l}) {ctx['seguro'](t)[:120]}" for l, t in questoes[n].items()))


def cmd_resposta(raiz, pedido, resposta, ctx):
    arq = ctx["pedido"](raiz, pedido)
    if arq is None:
        print(f"decisoes: pedido {ctx['seguro'](pedido)} ausente ou fora de docs/pedidos/; nada lido")
        return 2
    perguntas = PERGUNTA.findall(arq.read_text(encoding="utf-8"))
    questoes = opcoes_da_pergunta(perguntas[-1][1]) if perguntas else {}
    if not questoes:
        print("decisoes: o pedido não tem `PERGUNTA AO DONO` com opções `1a)`; a resposta não tem contra o que ser lida")
        return 2
    escolhas, ambiguas = ler_resposta(questoes, resposta)
    if ambiguas or not escolhas:
        print(f"decisoes: resposta ambígua ({'; '.join(ambiguas) or 'nenhuma questão respondida'}); volta ao dono como pergunta:")
        _devolver(questoes, ctx)
        return 1
    if motivos := recusa_de_corte(questoes, escolhas):  # E6: a pergunta gravada antes da trava não vira decisão de corte sem origem
        print(f"decisoes: {'; '.join(motivos)}; volta ao dono como pergunta, com a origem:")
        _devolver(questoes, ctx)
        return 1
    for n in sorted(questoes):
        if n in escolhas:
            print(f"resposta: {n} -> {n}{escolhas[n]}: {ctx['seguro'](questoes[n][escolhas[n]])[:160]}")
        else:
            print(f"resposta: {n} -> sem resposta: segue pendente")
    for n, (r, e) in sorted(divergencia(questoes, escolhas).items()):
        print(f"resposta: {MARCA_REVERTIDA} na questão {n} ({n}{e} contra {n}{r}): dono contra o time")
    print(f"decisoes: grave com `forge-check anotar --pedido {pedido} --tipo decisao --confere <critério> --literal <a resposta>` (a pergunta de "
          f"{perguntas[-1][0]})")
    return 0


# ---- S2: a fala do dono literal ----

def cmd_fala(raiz, a, ctx):
    arq = ctx["pedido"](raiz, a.pedido)
    if arq is None:
        print(f"pedido fala: pedido {ctx['seguro'](a.pedido)} ausente ou fora de docs/pedidos/; nada feito")
        return 2
    pasta = arq.parent / a.pedido
    if a.gravar:
        motivo = _recusa_do_texto(a.texto)
        if motivo:
            print(f"pedido fala: {motivo}; nada gravado")
            return 2
        conteudo = (f"Pedido: {a.pedido}\nHora: {_agora():%Y-%m-%d %H:%M}\nSha256: {_sha(a.texto)}\n"
                    "Autoriza: nada além do que o pedido já registra (gravar a fala não amplia autorização; R-DECISAO)\n\n"
                    f"{a.texto}\n")
        try:
            gravado = _gravar_novo(pasta, "fala", conteudo)
        except OSError as e:
            print(f"pedido fala: não gravei ({ctx['seguro'](e)}); nada gravado")
            return 2
        print(f"pedido fala: gravada {gravado.relative_to(arq.parent.parent.parent)} sha256 {_sha(a.texto)}")
        return 0
    falas = sorted(pasta.glob("fala-*.md"))
    adulteradas = 0
    for f in falas:
        campos, corpo = _ler_registro(f)
        integra = campos.get("Sha256") == _sha(corpo)
        adulteradas += not integra
        print(f"fala: {f.name} {campos.get('Hora', '?')} {'íntegra' if integra else 'ADULTERADA (sha256 não bate)'}")
        print("\n".join(f"> {ctx['seguro'](l)}" for l in corpo.splitlines()))
    print(f"pedido fala: {len(falas)} fala(s), {adulteradas} adulterada(s); leia antes de perguntar de novo (R-DECISAO)")
    return 1 if adulteradas else 0


# ---- S8: recado entre sessões ----

def cmd_recado(raiz, a, ctx):
    versao = ctx["versao"]()
    if a.para:
        destino = Path(os.path.realpath(a.para))
        motivo = _recusa_do_texto(a.texto) or (None if destino.is_dir() else "--para não é uma pasta")
        if motivo:
            print(f"recado: {motivo}; nada gravado")
            return 2
        conteudo = (f"Para: {destino}\nDe: {os.path.realpath(raiz)}\nVersao: {versao}\nHora: {_agora():%Y-%m-%d %H:%M}\n"
                    f"Sha256: {_sha(a.texto)}\n\n{a.texto}\n")
        try:
            gravado = _gravar_novo(destino / ".forge" / "recados", "recado", conteudo)
        except OSError as e:
            print(f"recado: não gravei ({ctx['seguro'](e)}); nada gravado")
            return 2
        print(f"recado: gravado {gravado}; a outra sessão confirma com `forge-check recado --confirmar {gravado.name}`")
        return 0
    pasta = Path(raiz) / ".forge" / "recados"
    nomes = sorted(pasta.glob("recado-*.md"))
    arq = pasta / Path(a.confirmar).name if a.confirmar else (nomes[-1] if nomes else None)
    if arq is None or not arq.is_file():
        print("recado: nenhum recado para esta sessão em .forge/recados/")
        return 2
    campos, corpo = _ler_registro(arq)
    recusas = [f"sessão errada: o recado é para {ctx['seguro'](campos.get('Para', '?'))}"] * (campos.get("Para") != os.path.realpath(raiz))
    recusas += [f"versão defasada: recado da {ctx['seguro'](campos.get('Versao', '?'))}, esta sessão na {versao}"] * (
        campos.get("Versao") != versao)
    recusas += ["texto adulterado: o sha256 não bate"] * (campos.get("Sha256") != _sha(corpo))
    if recusas:
        print(f"recado: recusado ({'; '.join(recusas)})")
        return 1
    print(f"recado: confirmado {arq.name} de {ctx['seguro'](campos.get('De', '?'))} ({campos.get('Hora', '?')})")
    print("\n".join(f"> {ctx['seguro'](l)}" for l in corpo.splitlines()))
    return 0


# ---- X1: pausa por limite de uso e retomada ----

def horario(texto, agora):
    """O instante de `AAAA-MM-DDTHH:MM` ou de `HH:MM` (hoje, ou amanhã se já passou), no fuso local; ValueError se inválido."""
    if re.fullmatch(r"\d{2}:\d{2}", texto):
        alvo = datetime.datetime.combine(agora.date(), datetime.time.fromisoformat(texto), agora.tzinfo)
        return alvo + datetime.timedelta(days=1) if alvo <= agora else alvo
    alvo = datetime.datetime.fromisoformat(texto)
    return alvo if alvo.tzinfo else alvo.replace(tzinfo=agora.tzinfo)


def cmd_pausa(raiz, a, ctx):
    arq, agora = Path(raiz) / ".forge" / "pausa.json", _agora()
    if a.gravar:
        try:
            alvo = horario(a.retoma_em, agora)
        except ValueError:
            print("pausa: --retoma-em é HH:MM ou AAAA-MM-DDTHH:MM (a hora em que a cota renova); nada gravado")
            return 2
        if not a.onde.strip() or alvo - agora > ESPERA_MAXIMA:
            print("pausa: --onde (onde parou) é obrigatório e a retomada fica em até 24 h; nada gravado")
            return 2
        dados = {"motivo": "limite de uso (Q1)", "gravada": agora.isoformat(timespec="minutes"),
                 "retoma_em": alvo.isoformat(timespec="minutes"), "onde": a.onde.strip()[:500], "pedido": a.pedido}
        try:
            _gravar_seguro(arq, json.dumps(dados, ensure_ascii=False, indent=1) + "\n")
        except OSError as e:
            print(f"pausa: não gravei .forge/pausa.json ({ctx['seguro'](str(e))[:160]}); nada gravado")
            return 2
        print(f"pausa: gravada; retoma em {dados['retoma_em']}; `forge-check pausa --retomar --esperar` em segundo plano retoma sozinho")
        return 0
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
        alvo = horario(dados["retoma_em"], agora)
    except (OSError, ValueError, KeyError, TypeError):
        print("pausa: nenhuma pausa gravada em .forge/pausa.json")
        return 0
    while a.esperar and _agora() < alvo:
        time.sleep(min(60, max(0.2, (alvo - _agora()).total_seconds())))
    if _agora() < alvo:
        print(f"pausa: a cota ainda não renovou; retoma em {dados['retoma_em']} (com --esperar, espera até lá)")
        return 1
    arq.replace(arq.with_name(f"pausa-retomada-{_agora():%Y%m%d-%H%M%S}.json"))
    print(f"pausa: cota renovada; retome: {ctx['seguro'](dados.get('onde', '?'))}")
    if dados.get("pedido"):
        print(f"pausa: próximo passo: `forge-check proximo {ctx['seguro'](dados['pedido'])}`")
    return 0


# ---- Diretriz 29 (FOCO-NAS-DECISOES, v047 E1.135): as perguntas abertas ao dono de todos os pedidos, numa leitura só ----

_DATA = r"(\d{4}-\d{2}-\d{2})(?:[ T]~?(\d{2})[:h](\d{2}))?"  # 2026-11-13 08:52, 2026-11-03 ~13h48 ou só a data


def _data(s):
    """`_DATA` com grupos nomeados `dia<s>`, `hora<s>` e `min<s>`."""
    return rf"(?P<dia{s}>\d{{4}}-\d{{2}}-\d{{2}})(?:[ T]~?(?P<hora{s}>\d{{2}})[:h](?P<min{s}>\d{{2}}))?"


# As formas do registro: `PERGUNTA AO DONO (data): corpo`, `DECISÃO DO DONO data: corpo`, `- data: PERGUNTA AO DONO: corpo`,
# `- data: DECISÃO DO DONO "literal"`, `DECISÃO DO DONO (data), corpo` e a forma antiga `PERGUNTA: (data) corpo` ou
# `PERGUNTA: data · corpo`; `DECISÃO DO DONO pendente` não é decisão. As outras falas (`ORDEM DO DONO`...) só separam pergunta
# e decisão. Trecho depois da data limitado (A2 da segurança: `[^):\n]*` seguido de `\s*` era quadrático).
LINHA_DO_REGISTRO = re.compile(rf"^\s*(?:[-*]\s+)?(?:{_data(0)}(?::\d{{2}})?(?:[-+]\d{{2}}:?\d{{2}})?\s*:\s*)?"
                               rf"(?P<frase>PERGUNTA AO DONO|DECISÃO DO DONO|PERGUNTA(?=:)|[A-ZÁÂÃÉÊÍÓÔÕÚÇ]{{2,20}} DO DONO)"
                               rf"(?:\s+de)?(?:\s*\(?{_data(1)}[^):\n]{{0,80}}\)?)?\s*(?:[:,]|(?=\x22))\s*(?P<corpo>.*)$")
DATA_DO_CORPO = re.compile(rf"\(?(?:dono,\s*)?{_data(1)}\)?\s*[·:—–-]?\s*")  # forma antiga: a data no começo do corpo
# Forma antiga respondida na própria linha: `PERGUNTA: nenhuma`, `· resposta: "A"`, `(respondida: B)` ou `? → "A"`.
RESPONDIDA_NA_LINHA = re.compile(r"^nenhuma\b|\brespondida\b|\bresposta\s*(?::\s*\S|[\x22“])|→", re.I)
CITACAO = re.compile(r"\bpergunta(?:\s+ao\s+dono)?(?:\s+\d{1,2}[a-z]?)?\s+de\s+~?(\d{2})[:h](\d{2})\b", re.I)  # `pergunta 1 de 10:00`
DATA_DA_CELULA = re.compile(rf".*?{_DATA}|")  # casa sempre: sem data, os grupos vazios
PESOS = (("irreversível", re.compile(r"irreversivel")),  # sobre o texto sem acento e em minúsculas; o primeiro que casa vale
         ("dinheiro", re.compile(r"dinheiro|\bpag(?:ar|a|o|as|os)\b|cobrad|r\$|us\$|\bfatura")),
         ("escopo", re.compile(r"\bescopo\b")))
OUTRO_PESO = "outro"
RECOMENDACAO = re.compile(r"\brecomend(?:ação|acao|ado|ada|o)\b\s*:?\s*([^;.·\"]{1,160})", re.I)
SEM_PENDENCIA = "Não há decisão sua pendente"
LARGURA_DA_PERGUNTA = 200


def _limpo(texto, largura=160):
    """O texto numa linha: sem caractere de controle nem `|` (o separador da saída), cortado em `largura` com `…`."""
    texto = " ".join(re.sub(r"[\x00-\x1f\x7f|]", " ", texto).split())
    return texto if len(texto) <= largura else texto[:largura - 1] + "…"


def peso(texto):
    """(posição, nome) do peso da pergunta: irreversível, dinheiro, escopo; sem nenhum, `outro`, por último."""
    plano = _sem_acento(texto)
    return next(((n, nome) for n, (nome, regra) in enumerate(PESOS) if regra.search(plano)), (len(PESOS), OUTRO_PESO))


def recomendada(texto):
    """A opção `[recomendada]` da pergunta (`1a) texto`) ou o que segue `recomendação:` no texto; `—` sem nenhuma."""
    opcoes = [f"{n}{letra}) {re.sub(r'\[[^\[\]]{1,40}\]', ' ', t)}" for n, q in sorted(opcoes_da_pergunta(texto).items())
              for letra, t in sorted(q.items()) if "recomendada" in marcas(t)]
    achado = RECOMENDACAO.search(texto)
    return _limpo("; ".join(opcoes) or (achado.group(1) if achado else "")) or "—"


def _hora(data, hora, minuto):
    """`AAAA-MM-DD HH:MM`, `AAAA-MM-DD` sem hora, vazio sem data."""
    return f"{data} {hora}:{minuto}".removesuffix(" :").strip()


def _registro(m):
    """(instante, frase, corpo) da linha do registro. Instante: a data depois da frase (na forma antiga, a do começo do corpo); sem
    ela, a do prefixo `- data:`; sem nenhuma, vazios."""
    corpo, achado = m["corpo"], m
    if m["frase"] == "PERGUNTA" and not m["dia1"] and (antiga := DATA_DO_CORPO.match(corpo)):
        corpo, achado = corpo[antiga.end():], antiga
    s = "1" if achado["dia1"] else "0"
    return (achado[f"dia{s}"] or "", achado[f"hora{s}"] or "", achado[f"min{s}"] or ""), m["frase"], corpo


def _respondida(abertas, instante, corpo, instantes):
    """A pergunta de `abertas` que a decisão fecha, ou None; cada decisão fecha no máximo uma. Citando `pergunta N de HH:MM`, a
    aberta mais recente daquela hora (citação sem aberta não fecha nada); sem citar, a aberta mais recente, se nenhuma outra fala
    do dono caiu entre as duas (decisão sobre outro assunto não fecha pergunta: mostrar a mais é o lado seguro)."""
    if citada := CITACAO.search(corpo):
        return next((p for p in reversed(abertas) if p[0][1:] == citada.groups()), None)
    if abertas and not any(abertas[-1][0] < outro < instante for outro in instantes):
        return abertas[-1]
    return None


def perguntas_do_pedido(nome, texto):
    """As perguntas ao dono (`PERGUNTA AO DONO` e a forma antiga `PERGUNTA:`) do pedido sem `DECISÃO DO DONO` que as feche
    (`_respondida`), em ordem de instante. Decisão sem hora no mesmo dia vale como anterior à pergunta com hora."""
    registro = sorted((_registro(m) + (n,) for n, linha in enumerate(texto.split("\n"), 1) if (m := LINHA_DO_REGISTRO.match(linha))),
                      key=lambda r: (r[0], r[3]))
    instantes, abertas = [r[0] for r in registro], []
    for instante, frase, corpo, _ in registro:
        if frase in ("PERGUNTA AO DONO", "PERGUNTA") and not (frase == "PERGUNTA" and RESPONDIDA_NA_LINHA.search(corpo)):
            abertas.append((instante, corpo))
        elif frase == FRASE_DA_DECISAO and (fechada := _respondida(abertas, instante, corpo, instantes)):
            abertas.remove(fechada)
    return [{"pedido": nome, "hora": _hora(*instante), "texto": corpo, "pergunta": re.sub(r'^.*?→\s*"(.+)"\s*$', r"\1", corpo)}
            for instante, corpo in abertas]


def pendencias_do_quadro(quadro):
    """Os cartões do painel `Aguardando o dono` do KANBAN.md: `ID: cartão`, pedido, `desde` (coluna 6) e a recomendação."""
    abertas, no_painel = [], False
    for linha in quadro.split("\n"):
        if linha.startswith("## "):
            no_painel = _sem_acento(linha[3:]).startswith("aguardando o dono")
            continue
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        if not no_painel or not linha.startswith("|") or len(celulas) < 6 or celulas[0] == "ID" or set(celulas[0]) <= set(":-"):
            continue
        abertas.append({"pedido": re.sub(r"^.*/|\.md$", "", celulas[2]), "hora": _hora(*DATA_DA_CELULA.match(celulas[5]).groups("")),
                        "texto": " · ".join(celulas[1:2] + celulas[6:]), "pergunta": f"{celulas[0]}: {celulas[1]}"})
    return abertas


def cmd_abertas(raiz):
    """Diretriz 29: ([linhas], 0) com as perguntas abertas ao dono de `<raiz>/docs/pedidos/*.md` e do painel `Aguardando o dono`
    de `<raiz>/KANBAN.md`, da de maior peso (irreversível, dinheiro, escopo) para a menor e, no mesmo peso, da mais antiga; sem
    nenhuma, a linha única `SEM_PENDENCIA`. Só leitura; link simbólico não é lido (pasta `docs` ou `docs/pedidos` por link: rc 1);
    arquivo ilegível vira aviso e fica fora da lista."""
    abertas, avisos = [], []
    pasta = Path(raiz) / "docs" / "pedidos"
    if pasta.is_symlink() or pasta.parent.is_symlink():  # A1 da segurança: como `_gravar_novo`, pasta por link não é lida
        return ["abertas: erro: docs/pedidos ou docs é link simbólico; recusado"], 1
    for arq in sorted(pasta.glob("*.md")):
        if arq.is_symlink():
            continue
        try:
            abertas += perguntas_do_pedido(arq.stem, arq.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as erro:
            avisos.append(f"abertas: aviso: {_limpo(arq.name)} ilegível ({type(erro).__name__}); fora da lista")
    quadro = Path(raiz) / "KANBAN.md"
    if quadro.is_file() and not quadro.is_symlink():
        try:
            abertas += pendencias_do_quadro(quadro.read_text(encoding="utf-8", errors="replace"))
        except OSError as erro:
            avisos.append(f"abertas: aviso: KANBAN.md ilegível ({type(erro).__name__}); fora da lista")
    if not abertas:
        return avisos + [SEM_PENDENCIA], 0
    abertas.sort(key=lambda p: (peso(p["texto"])[0], p["hora"], p["pedido"]))  # sem hora conta como a mais antiga
    linhas = [f"aberta: {peso(p['texto'])[1]} | {_limpo(p['pedido'], 60)} | {p['hora'] or '—'} | "
              f"{_limpo(p['pergunta'], LARGURA_DA_PERGUNTA)} | recomendada: {recomendada(p['texto'])}" for p in abertas]
    return avisos + linhas + [f"abertas: total={len(abertas)}"], 0


def executar(a, raiz, ctx):
    """Despacha o subcomando; `ctx` traz do forge-check `pedido` (resolve docs/pedidos/<id>.md ou None), `versao` e `seguro`."""
    if a.cmd == "decisoes":
        return cmd_resposta(raiz, a.pedido or "", a.resposta, ctx)
    return {"pedido": cmd_fala, "recado": cmd_recado, "pausa": cmd_pausa}[a.cmd](raiz, a, ctx)
