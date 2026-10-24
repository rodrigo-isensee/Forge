#!/usr/bin/env python3
"""Reexecuta as provas `cmd` de um arquivo de provas da branch (R-PROVA, EST-030-L2).

Uso: reexecutar-provas.py [--raiz DIR] [--tempo S] docs/provas/<pedido>.md...
Lista positiva de linhas: toda linha do arquivo é lida e só passa a vazia, um título (`# ` e `## Provas`, um de cada no
máximo), uma linha `Propósito: ` ou uma prova `- PQ-n (cmd): `<comando>` · espera: <espera>`; qualquer outra linha, arquivo
sem prova, comando fora da lista permitida ou espera ilegível reprova (falha fechada), antes de executar qualquer comando.
Cada prova roda sem shell, em DIR; para na primeira divergência. Sem segredo: ambiente mínimo (PATH e locale).
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
import unicodedata
from pathlib import Path

LINHA = re.compile(r"^- PQ-(\d+) \(cmd\): `([^`]+)` · espera: (.+)$", re.ASCII)  # na linha crua, sem normalizar
TITULO = re.compile(r"^(# \S.*|## Provas)$")  # `# <título>` ou `## Provas`, na linha crua
PROPOSITO = "Propósito: "
MARCA_DE_PROVA = re.compile(r"espera|cmd|pq")  # em texto normalizado: título e Propósito sem cara de prova (mais estrito que "pq+dígito")
MODULO = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+")  # pacote.modulo: o nome de pacote sozinho roda o load_tests dele
ARG = re.compile(r"[A-Za-z0-9_./:=^~@+-]+")  # um argumento sem espaço nem metacaractere de shell
UNITTEST_FLAGS = {"-v", "-q", "-b", "-f"}
SAIDA_PERMITIDA_GIT = {("rev-parse",), ("ls-files",), ("diff", "--numstat"), ("diff", "--name-only")}
FLAGS_GIT = {"--numstat", "--name-only", "--verify", "--short", "--cached", "--show-toplevel", "--"}
TERMO = re.compile(r"rc=0|contém '(.*)'|igual '(.*)'|linhas=(\d+)|linhas>=(\d+)", re.S)


class Falha(Exception):
    pass


def normalizar(texto):
    """Grafia canônica para comparar com a lista: NFKC, sem caracteres de formato (U+200B...) e sem diferença de caixa."""
    return "".join(c for c in unicodedata.normalize("NFKC", texto) if unicodedata.category(c) != "Cf").casefold()


def caminho_fora_da_arvore(arg):
    """Argumento de git que sai da árvore: absoluto, `~` ou com componente `..` (o git cairia em --no-index)."""
    return arg.startswith(("/", "~")) or ".." in arg.split("/")


def comando_permitido(argv):
    """Lista permitida: `python3 -m unittest <pacote.modulo>...` (sem discover) e git de leitura. Devolve o motivo da recusa ou None."""
    if not argv or any(not ARG.fullmatch(a) for a in argv):
        return "argumento fora do alfabeto permitido"
    if argv[:3] == ["python3", "-m", "unittest"]:
        modulos = [a for a in argv[3:] if a not in UNITTEST_FLAGS]
        if not modulos or any(not MODULO.fullmatch(a) or normalizar(a) == "discover" for a in modulos):
            return "unittest exige ao menos um módulo pacote.modulo, com -v/-q/-b/-f e sem discover"
        return None
    if argv[0] == "git" and any(tuple(argv[1:1 + len(p)]) == p for p in SAIDA_PERMITIDA_GIT):
        if any(a.startswith("-") and a not in FLAGS_GIT for a in argv[1:]):
            return "opção de git fora da lista (--output, --no-index e --ext-diff, por exemplo)"
        if any(caminho_fora_da_arvore(a) for a in argv[1:] if not a.startswith("-")):
            return "caminho de git fora da árvore (absoluto, ~ ou ..)"
        return None
    return "comando fora da lista permitida"


def ler_espera(espera):
    """Termos da espera ligados por ` e `; ilegível, que sempre passa ou sem `rc=0` falha fechada (lê todos antes de comparar)."""
    termos = [t.strip() for t in re.split(r" e (?=rc=0|contém |igual |linhas)", espera.strip())]
    for termo in termos:
        m = TERMO.fullmatch(termo)
        if not m:
            raise Falha(f"espera ilegível: {termo!r}")
        if m.group(1) == "" or (m.group(4) is not None and int(m.group(4)) == 0):
            raise Falha(f"espera que sempre passa: {termo!r}")
    if "rc=0" not in termos:
        raise Falha(f"espera sem rc=0 (comando que falha não pode passar): {espera.strip()!r}")
    return termos


def avaliar(espera, saida, rc):
    """Compara `espera` com a saída; devolve o primeiro termo que diverge, ou None."""
    linhas = len(saida.splitlines())
    for termo in ler_espera(espera):
        contem, igual, n, minimo = TERMO.fullmatch(termo).groups()
        if termo == "rc=0":
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
            return termo
    return None


def forma_da_linha(linha, vistas):
    """Classifica a linha crua numa das quatro formas permitidas ou devolve None (reprova). `vistas` conta título e Propósito."""
    if linha == "":
        return "vazia"
    if LINHA.match(linha):
        return "prova"
    forma = "titulo " + linha.split(" ", 1)[0] if TITULO.match(linha) else "proposito" if linha.startswith(PROPOSITO) else None
    if forma is None or forma in vistas or MARCA_DE_PROVA.search(normalizar(linha)):
        return None
    vistas.add(forma)
    return forma


def ler_provas(arquivo, texto, raiz):
    """Lê todas as linhas antes de executar: devolve (número, PQ, comando, argv, espera) de cada prova ou levanta Falha."""
    provas, vistas = [], set()
    for numero, linha in enumerate(texto.splitlines(), 1):
        forma = forma_da_linha(linha, vistas)
        if forma is None:
            raise Falha(f"{arquivo}:{numero}: linha fora do formato do arquivo de provas")
        if forma != "prova":
            continue
        m = LINHA.match(linha)
        pq, comando, espera = f"PQ-{m.group(1)}", m.group(2).strip(), m.group(3)
        try:
            argv = shlex.split(comando)
        except ValueError as erro:
            raise Falha(f"{arquivo}:{numero}: {pq}: comando ilegível ({erro})")
        try:
            ler_espera(espera)
        except Falha as erro:
            raise Falha(f"{arquivo}:{numero}: {pq}: {erro}")
        motivo = comando_permitido(argv)
        if motivo:
            raise Falha(f"{arquivo}:{numero}: {pq}: recusado ({motivo}): {comando}")
        if argv[0] == "git" and not (raiz / ".git").exists():
            raise Falha(f"{arquivo}:{numero}: {pq}: git sem repositório em --raiz (cairia em --no-index): {comando}")
        provas.append((numero, pq, comando, argv, espera))
    if not provas:
        raise Falha(f"{arquivo}: nenhuma prova cmd")
    return provas


def reexecutar(arquivo, raiz, tempo):
    caminho = (raiz / arquivo).resolve()
    if raiz.resolve() not in caminho.parents or caminho.parent.name != "provas" or caminho.parent.parent.name != "docs" or caminho.name == "_modelo.md":
        raise Falha(f"{arquivo}: fora de docs/provas/ ou é o modelo")
    try:
        texto = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as erro:
        raise Falha(f"{arquivo}: não foi possível ler ({erro.__class__.__name__})")
    return executar(arquivo, texto, raiz, tempo)


def executar(arquivo, texto, raiz, tempo):
    """Lê o texto inteiro (`ler_provas`) e só então roda cada prova; imprime `ok <arquivo>:<linha> PQ-n` e devolve quantas."""
    provas = ler_provas(arquivo, texto, raiz)
    ambiente = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
    for numero, pq, comando, argv, espera in provas:
        try:
            r = subprocess.run(argv, cwd=raiz, env=ambiente, capture_output=True, text=True, timeout=tempo, shell=False)
        except subprocess.TimeoutExpired:
            raise Falha(f"{arquivo}:{numero}: {pq}: passou de {tempo}s: {comando}")
        divergiu = avaliar(espera, r.stdout + r.stderr, r.returncode)
        if divergiu:
            raise Falha(f"{arquivo}:{numero}: {pq}: diverge de '{divergiu}' (rc={r.returncode}): {comando}")
        print(f"ok {arquivo}:{numero} {pq}")
    return len(provas)


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
