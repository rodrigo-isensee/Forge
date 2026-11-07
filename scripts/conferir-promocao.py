#!/usr/bin/env python3
"""Forge DV-3(b): a ponta da homolog e da main é merge commit sem conteúdo próprio (R-FLUXO, ADR 0012). Só biblioteca padrão.

Uso: conferir-promocao.py --ref REF
  Confere o repositório do diretório corrente, nunca o do próprio arquivo (o CI roda a cópia do primeiro pai).
  0 = exatamente 2 pais e árvore igual à do segundo pai; 1 = 1 pai, 3 ou mais pais ou árvore diferente;
  2 = não verificável (ref com `-` inicial ou controle, recusada antes do git; clone raso, saída fora do formato
  ou git com erro). A saída só traz sha7 e contagens, nunca nome de arquivo ou de ref.
"""
import argparse
import re
import subprocess
import sys

PAIS = re.compile(r"[0-9a-f]{40}( [0-9a-f]{40})*")
ARVORE = re.compile(r"[0-9a-f]{40}")
PRAZO = 60  # segundos por chamada ao git


class NaoVerificavel(Exception):
    pass


def git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=PRAZO)
    except (OSError, subprocess.TimeoutExpired) as erro:
        raise NaoVerificavel(f"git {args[0]}: {type(erro).__name__}") from erro
    if r.returncode != 0:
        raise NaoVerificavel(f"git {args[0]} falhou, rc {r.returncode}")
    return r.stdout.strip()


def arvore(sha):
    saida = git("log", "-1", "--format=%T", "--end-of-options", sha)
    if not ARVORE.fullmatch(saida):
        raise NaoVerificavel("git log fora do formato")
    return saida


def conferir(ref):
    linha = git("rev-list", "--parents", "-n1", "--end-of-options", ref)
    if not PAIS.fullmatch(linha):
        raise NaoVerificavel("rev-list fora do formato")
    head, *pais = linha.split(" ")
    if not pais:
        raise NaoVerificavel("sem pai legível, clone raso?")
    if len(pais) == 1:
        return 1, f"{head[:7]} tem 1 pai (squash ou fast-forward; R-FLUXO, ADR 0012)"
    if len(pais) > 2:
        return 1, f"{head[:7]} tem {len(pais)} pais (merge octopus; R-FLUXO, ADR 0012)"
    if arvore(head) == arvore(pais[1]):
        return 0, f"ok {head[:7]} (2 pais, árvore igual a {pais[1][:7]})"
    nomes = git("diff-tree", "-r", "--no-renames", "--name-only", "-z", "--end-of-options", pais[1], head)
    return 1, f"{head[:7]} difere do segundo pai em {nomes.count(chr(0))} arquivos (conteúdo próprio na branch de promoção)"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Confere que a ponta da branch de promoção é merge commit sem conteúdo próprio.")
    parser.add_argument("--ref", required=True)
    ref = parser.parse_args(argv).ref
    try:
        if ref.startswith("-") or not ref.isprintable():
            raise NaoVerificavel("ref inválida")
        rc, texto = conferir(ref)
    except NaoVerificavel as erro:
        rc, texto = 2, f"não verificável ({erro})"
    print(f"promoção: {texto}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
