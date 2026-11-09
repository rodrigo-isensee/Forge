"""Forge: a conversa com o dono e entre sessões, gravada no disco (0.44.1). Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um destes roda:
- `decisoes --pedido P --resposta "1a 2c"` (O4): a resposta curta do dono lida contra a última `PERGUNTA AO DONO` do pedido.
  Opções `1a)`, `1b)`...; `[recomendada]` e `[reversível]` ou `[irreversível]` no texto da opção (com ou sem acento, qualquer
  caixa). Vocabulário fechado: os códigos da pergunta e as palavras de PALAVRAS (aprova a recomendada marcada `[reversível]` de
  cada questão sem código). O ambíguo volta como pergunta (rc 1); a palavra solta nunca vale para opção irreversível nem sem marca. Só lê: o Jarvis grava a decisão com `forge-check anotar`.
- `pedido fala --gravar|--ler --pedido P` (S2): as palavras do dono, literais, com sha256, em docs/pedidos/<P>/fala-<stamp>.md;
  gravar não amplia autorização (o registro diz isso) e ler confere o hash de cada fala.
- `recado --para RAIZ --texto T` e `recado --confirmar [ARQ]` (S8): texto entre sessões em <RAIZ>/.forge/recados/, com
  cabeçalho (raiz de destino, versão do plugin, sha256); a sessão de outra raiz ou de outra versão recusa.
- `pausa --gravar --retoma-em H --onde T` e `pausa --retomar [--esperar]` (X1): onde parou na pausa por limite de uso (Q1), em
  .forge/pausa.json, e a retomada quando a cota renova. Não contorna limite nem troca de conta: só espera o horário dado.
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
        for n in sorted(questoes):
            print(f"pergunta: {n}) " + " · ".join(f"{n}{l}) {ctx['seguro'](t)[:120]}" for l, t in questoes[n].items()))
        return 1
    for n in sorted(questoes):
        if n in escolhas:
            print(f"resposta: {n} -> {n}{escolhas[n]}: {ctx['seguro'](questoes[n][escolhas[n]])[:160]}")
        else:
            print(f"resposta: {n} -> sem resposta: segue pendente")
    print(f"decisoes: grave com `forge-check anotar --pedido {pedido} --tipo decisao --literal <a resposta>` (a pergunta de "
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


def executar(a, raiz, ctx):
    """Despacha o subcomando; `ctx` traz do forge-check `pedido` (resolve docs/pedidos/<id>.md ou None), `versao` e `seguro`."""
    if a.cmd == "decisoes":
        return cmd_resposta(raiz, a.pedido or "", a.resposta, ctx)
    return {"pedido": cmd_fala, "recado": cmd_recado, "pausa": cmd_pausa}[a.cmd](raiz, a, ctx)
