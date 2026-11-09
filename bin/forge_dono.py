"""Forge: a conversa com o dono e entre sessões, gravada no disco (0.44.1). Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um destes roda:
- `decisoes --pedido P --resposta "1a 2c"` (O4): a resposta curta do dono lida contra a última `PERGUNTA AO DONO` do pedido.
  Opções `1a)`, `1b)`...; `[recomendada]` e `[irreversível]` no texto da opção. Vocabulário fechado: os códigos da pergunta e as
  palavras de PALAVRAS (aprova a recomendada de cada questão sem código). O ambíguo volta como pergunta (rc 1), e a palavra
  solta nunca vale para opção irreversível. Só lê: o Jarvis grava a decisão com `forge-check anotar`.
"""
import datetime
import hashlib
import json
import os
import re
import time
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


def ler_resposta(questoes, resposta):
    """(escolhas {questão: letra}, ambiguidades [texto]). Fora do vocabulário, código que não existe, duas opções para a mesma
    questão, palavra solta sem recomendação única ou sobre opção irreversível: ambiguidade."""
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
        elif "[irreversível]" in questoes[n][recomendadas[0]]:
            ambiguas.append(f"a questão {n} é irreversível: a palavra solta não vale, responda com o código")
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


def executar(a, raiz, ctx):
    """Despacha o subcomando; `ctx` traz do forge-check `pedido` (resolve docs/pedidos/<id>.md ou None), `versao` e `seguro`."""
    return cmd_resposta(raiz, a.pedido or "", a.resposta, ctx)
