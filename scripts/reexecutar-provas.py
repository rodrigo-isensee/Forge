#!/usr/bin/env python3
"""Reexecuta as provas `cmd` de um arquivo de provas da branch (R-PROVA, EST-030-L2).

Uso: reexecutar-provas.py [--raiz DIR] [--tempo S] docs/provas/<pedido>.md...
Cada linha `- PQ-n (cmd): `<comando>` · espera: <espera>` roda sem shell, em DIR, só se o comando estiver na lista
permitida; comando fora dela, linha fora do formato ou espera ilegível reprova (falha fechada). Para na primeira divergência.
Sem segredo: o comando recebe um ambiente mínimo (PATH e locale).
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

LINHA = re.compile(r"^- PQ-(\d+) \(cmd\): `([^`]+)` · espera: (.+)$")
PARECE_CMD = re.compile(r"PQ-\d+.*\(cmd\)", re.I)  # qualquer linha assim tem de casar LINHA ou reprova
ARG = re.compile(r"[A-Za-z0-9_./:=^~@+-]+")  # um argumento sem espaço nem metacaractere de shell
UNITTEST_FLAGS = {"-v", "-q", "-b", "-f"}
SAIDA_PERMITIDA_GIT = {("rev-parse",), ("ls-files",), ("diff", "--numstat"), ("diff", "--name-only")}
FLAGS_GIT = {"--numstat", "--name-only", "--verify", "--short", "--cached", "--show-toplevel", "--"}
TERMO = re.compile(r"rc=0|contém '(.*)'|igual '(.*)'|linhas=(\d+)|linhas>=(\d+)", re.S)


class Falha(Exception):
    pass


def caminho_fora_da_arvore(arg):
    """Argumento de git que sai da árvore: absoluto, `~` ou com componente `..` (o git cairia em --no-index)."""
    return arg.startswith(("/", "~")) or ".." in arg.split("/")


def comando_permitido(argv):
    """Lista permitida: `python3 -m unittest <módulos>` (sem discover) e git de leitura. Devolve o motivo da recusa ou None."""
    if not argv or any(not ARG.fullmatch(a) for a in argv):
        return "argumento fora do alfabeto permitido"
    if argv[:3] == ["python3", "-m", "unittest"]:
        resto = argv[3:]
        if "discover" in resto or not resto or any(a not in UNITTEST_FLAGS and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", a) for a in resto):
            return "unittest só com módulos e -v/-q/-b/-f (sem discover)"
        return None
    if argv[0] == "git" and any(tuple(argv[1:1 + len(p)]) == p for p in SAIDA_PERMITIDA_GIT):
        if any(a.startswith("-") and a not in FLAGS_GIT for a in argv[1:]):
            return "opção de git fora da lista (--output, --no-index e --ext-diff, por exemplo)"
        if any(caminho_fora_da_arvore(a) for a in argv[1:] if not a.startswith("-")):
            return "caminho de git fora da árvore (absoluto, ~ ou ..)"
        return None
    return "comando fora da lista permitida"


def avaliar(espera, saida, rc):
    """Compara `espera` (termos ligados por ` e `) com a saída; devolve o primeiro termo que diverge, ou None."""
    termos = re.split(r" e (?=rc=0|contém |igual |linhas)", espera.strip())
    for termo in termos:  # lê todos antes de comparar: espera ilegível ou que sempre passa reprova mesmo depois de um termo que diverge
        m = TERMO.fullmatch(termo.strip())
        if not m:
            raise Falha(f"espera ilegível: {termo!r}")
        if m.group(1) == "" or (m.group(4) is not None and int(m.group(4)) == 0):
            raise Falha(f"espera que sempre passa: {termo.strip()!r}")
    for termo in termos:
        contem, igual, n, minimo = TERMO.fullmatch(termo.strip()).groups()
        linhas = len(saida.splitlines())
        if termo.strip() == "rc=0":
            ok = rc == 0
        elif contem is not None:
            ok = contem in saida
        elif igual is not None:
            ok = saida.strip() == igual
        elif n is not None:
            ok = linhas == int(n)
        else:
            ok = linhas >= int(minimo)
        if not ok:
            return termo.strip()
    return None


def reexecutar(arquivo, raiz, tempo):
    caminho = (raiz / arquivo).resolve()
    if raiz.resolve() not in caminho.parents or caminho.parent.name != "provas" or caminho.parent.parent.name != "docs" or caminho.name == "_modelo.md":
        raise Falha(f"{arquivo}: fora de docs/provas/ ou é o modelo")
    n = 0
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        if not PARECE_CMD.search(linha):
            continue
        m = LINHA.match(linha)
        if not m:
            raise Falha(f"{arquivo}:{numero}: linha cmd fora do formato")
        pq, comando, espera = f"PQ-{m.group(1)}", m.group(2).strip(), m.group(3)
        try:
            argv = shlex.split(comando)
        except ValueError as erro:
            raise Falha(f"{arquivo}:{numero}: {pq}: comando ilegível ({erro})")
        motivo = comando_permitido(argv)
        if motivo:
            raise Falha(f"{arquivo}:{numero}: {pq}: recusado ({motivo}): {comando}")
        if argv[0] == "git" and not (raiz / ".git").exists():
            raise Falha(f"{arquivo}:{numero}: {pq}: git sem repositório em --raiz (cairia em --no-index): {comando}")
        ambiente = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            r = subprocess.run(argv, cwd=raiz, env=ambiente, capture_output=True, text=True, timeout=tempo, shell=False)
        except subprocess.TimeoutExpired:
            raise Falha(f"{arquivo}:{numero}: {pq}: passou de {tempo}s: {comando}")
        divergiu = avaliar(espera, r.stdout + r.stderr, r.returncode)
        if divergiu:
            raise Falha(f"{arquivo}:{numero}: {pq}: diverge de '{divergiu}' (rc={r.returncode}): {comando}")
        n += 1
        print(f"ok {arquivo}:{numero} {pq}")
    return n


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("arquivos", nargs="+")
    p.add_argument("--raiz", default=".")
    p.add_argument("--tempo", type=int, default=300)
    a = p.parse_args(argv)
    try:
        total = sum(reexecutar(f, Path(a.raiz), a.tempo) for f in a.arquivos)
    except Falha as erro:
        print(f"reexecutar-provas: {erro}", file=sys.stderr)
        return 1
    print(f"reexecutar-provas: {total} prova(s) cmd conferida(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
