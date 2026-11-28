#!/usr/bin/env python3
"""Forge: valida o YAML dos workflows antes do envio (VALIDAR-YAML-DO-WORKFLOW). Só biblioteca padrão, sem custo (R-CUSTO).

Uso: validar-yaml-workflow.py [arquivo.yml ...]   (sem argumento: .github/workflows/*.yml e *.yaml deste repositório)
Saída: uma linha `arquivo:linha: defeito` por problema; rc 0 limpo, 1 com defeito, 2 em erro de uso.

Não é um parser YAML completo: confere o subconjunto que o GitHub recusa sem criar jobs (#929, run 45924102244: `: ` sem
aspas num valor simples e o run nasceu sem jobs, parecendo verde). Pega: tabulação na indentação, valor simples com `: ` ou
terminado em `:`, chave repetida no mesmo mapa. Corpo de bloco `|`/`>`, valores entre aspas e coleções `[ ]`/`{ }` não
têm o conteúdo conferido.
"""
import re
import sys
from pathlib import Path

BLOCO = re.compile(r"^[|>][+\-0-9]*$")
PAR = re.compile(r"^([^\s\"'\[{#][^:]*?):(?:\s+(.*))?$")


def validar(texto):
    """Lista de (linha, defeito) do texto de um workflow."""
    erros, mapas, corpo_acima = [], {}, None
    for n, bruta in enumerate(texto.splitlines(), 1):
        resto = bruta.lstrip(" \t")
        indent = len(bruta) - len(resto)
        if not resto or resto.startswith("#"):
            continue
        if corpo_acima is not None:
            if indent > corpo_acima:
                continue
            corpo_acima = None
        if "\t" in bruta[:indent]:
            erros.append((n, "tabulação na indentação (o YAML só aceita espaços)"))
            continue
        col, itens = indent, False
        while resto.startswith("- "):
            itens = True
            col += len(resto) - len(resto[1:].lstrip())
            resto = resto[1:].lstrip()
        resto = re.sub(r"\s+#.*$", "", resto)
        for k in [k for k in mapas if k > col or (itens and k >= col)]:
            del mapas[k]
        par = PAR.match(resto)
        if not par:
            continue
        chave, valor = par.group(1).strip(), (par.group(2) or "").strip()
        if chave in mapas.setdefault(col, set()):
            erros.append((n, f"chave repetida no mesmo mapa: {chave}"))
        mapas[col].add(chave)
        if BLOCO.match(valor):
            corpo_acima = col
        elif valor and valor[0] not in "\"'|>[{&*!%@`" and re.search(r": |:$", valor):
            erros.append((n, f"valor simples com `:` (ponha entre aspas ou use `|`): {valor[:60]}"))
    return erros


def main(argv):
    if argv:
        arquivos = [Path(a) for a in argv]
    else:
        pasta = Path(__file__).resolve().parent.parent / ".github" / "workflows"
        arquivos = sorted([*pasta.glob("*.yml"), *pasta.glob("*.yaml")])
    ruim = 0
    for arq in arquivos:
        try:
            texto = arq.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"{arq}: não li o arquivo: {e}", file=sys.stderr)
            return 2
        for n, msg in validar(texto):
            print(f"{arq}:{n}: {msg}")
            ruim += 1
    return 1 if ruim else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
