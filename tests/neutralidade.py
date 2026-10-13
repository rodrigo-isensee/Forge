"""Detector de termos proibidos por hash (ADR 0008): a lista não guarda os nomes em claro.

Cada entrada de `termos_proibidos_hash` em tests/config.json tem `tipo`, `n` (tamanho) e `sha256` da forma normalizada
(minúsculas, sem acento, sem espaços):
- `palavra`: o token inteiro é igual à forma (equivale a `\\bforma\\b`);
- `trecho`: a forma aparece dentro de um token (equivale a uma busca de substring);
- `par`: `n` = [a, b]; os a últimos caracteres de um token mais os b primeiros do token seguinte, separados por
  exatamente um espaço, formam a forma (equivale a `parte1 ?parte2`).
"""
import hashlib
import re
import unicodedata


def normalizar(texto):
    sem_acento = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return sem_acento.lower()


def _hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def termos_achados(texto, entradas):
    """Devolve o conjunto de `sha256` das entradas encontradas em `texto`."""
    norm = normalizar(texto)
    tokens = list(re.finditer(r"\w+", norm))
    esperados = {"palavra": {}, "trecho": {}}
    pares = []
    for e in entradas:
        if e["tipo"] == "par":
            pares.append(e)
        else:
            esperados[e["tipo"]].setdefault(e["n"], set()).add(e["sha256"])
    achados = set()
    for t in tokens:
        w = t.group(0)
        if _hash(w) in esperados["palavra"].get(len(w), ()):
            achados.add(_hash(w))
        for n, hashes in esperados["trecho"].items():
            achados |= {s for s in (_hash(w[i:i + n]) for i in range(len(w) - n + 1)) if s in hashes}
    for par in pares:
        a, b = par["n"]
        for x, y in zip(tokens, tokens[1:]):
            if norm[x.end():y.start()] == " " and _hash(x.group(0)[-a:] + y.group(0)[:b]) == par["sha256"]:
                achados.add(par["sha256"])
    return achados
