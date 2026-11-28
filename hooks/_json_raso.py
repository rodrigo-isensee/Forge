"""Teto de aninhamento comum aos leitores de JSON de controle (JSON-PROFUNDO-PY314).

Medido no 3.12.3: o `json` só recusa o aninhamento acima de um contador fixo em C (entre 9000 e 10000 níveis, que nem
`sys.setrecursionlimit` nem o tamanho da pilha da thread mudam), e o 3.14 nem isso. Quem contava com essa recusa (o estado
dos hooks, a catraca e o `forge-placar`) passa o texto por `fundo_demais` antes do `json.loads` e recusa por conta própria,
com mensagem fixa, igual em toda versão do python.

A catraca (que não carrega código de fora) e o `bin/forge-placar` (script solto) têm cópias; `tests/test_json_raso.py`
prova que as três respondem igual, caractere a caractere, e qualquer uma que mude sozinha deixa a suíte vermelha.
"""

import json

TETO_ANINHAMENTO = 64  # níveis de [ e { aceitos; os JSON do Forge usam até 8 (hooks/hooks.json)


def fundo_demais(texto, teto=TETO_ANINHAMENTO):
    """Aninhamento de [ e { acima do teto, fora das strings. Um passe só sobre os caracteres, sem recursão: custo linear.

    Bytes são decodificados como o `json.loads` os decodifica (mesma detecção de UTF-8, 16 ou 32); o erro de decodificação
    sobe a quem chama, que já recusa o JSON ilegível."""
    if isinstance(texto, (bytes, bytearray)):
        texto = bytes(texto).decode(json.detect_encoding(texto), "surrogatepass")
    nivel = 0
    em_string = escapado = False
    for c in texto:
        if em_string:
            if escapado:
                escapado = False
            elif c == "\\":
                escapado = True
            elif c == '"':
                em_string = False
        elif c == '"':
            em_string = True
        elif c in "[{":
            nivel += 1
            if nivel > teto:
                return True
        elif c in "]}":
            nivel -= 1
    return False
