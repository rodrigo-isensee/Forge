#!/usr/bin/env python3
"""Forge: índice do corpus de fixtures dos hooks (`tests/hooks/<hook>/<caso>.json`, ADR 0003). Só biblioteca padrão.

Uso: indice-fixtures.py              grava docs/hooks-fixtures.md a partir do corpus
     indice-fixtures.py --conferir   não grava; rc 1 se o arquivo não está em dia (o teste do índice usa o mesmo texto)

O índice agrupa por hook (a pasta) e por prefixo (o nome do caso até o primeiro `-`). Para cada grupo: quantos casos,
quantos recusam (`esperado.codigo` 2) e quantos liberam (0), as regras `R-*` que o `esperado.stderr` cita, os cartões que
abrem a `descricao` e uma descrição de exemplo, a primeira sem termo de stack (`neutralidade_nucleo` de
tests/config.json, ADR 0001: o índice é núcleo). Nenhuma fixture muda de nome nem de lugar: o índice só lê.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CORPUS = Path("tests/hooks")
INDICE = Path("docs/hooks-fixtures.md")
CONFIG = RAIZ / "tests" / "config.json"  # sempre o do repositório do script, mesmo com outra raiz
REGRA = re.compile(r"\bR-[A-Z][A-Z0-9-]*[A-Z0-9]")
CARTAO = re.compile(r"^([A-Z][A-Z0-9]*(?:[.-][A-Z0-9]+)+|[A-Z]{2,}[0-9]*)\b")
MAXIMO_DO_EXEMPLO = 140
MAXIMO_DA_LISTA = 4


def prefixo(nome):
    return nome.split("-", 1)[0]


def celula(texto):
    """Texto numa célula de tabela Markdown: sem quebra de linha e sem `|` solto."""
    return " ".join(str(texto).split()).replace("|", "\\|")


def resumo(contagem):
    """Os mais citados primeiro (empate pela ordem alfabética), até MAXIMO_DA_LISTA, e quantos ficaram de fora."""
    nomes = [n for n, _ in sorted(contagem.items(), key=lambda x: (-x[1], x[0]))]
    texto = ", ".join(f"`{n}`" for n in nomes[:MAXIMO_DA_LISTA])
    return texto + (f" e mais {len(nomes) - MAXIMO_DA_LISTA}" if len(nomes) > MAXIMO_DA_LISTA else "") or "—"


def placar(casos):
    """(recusa, libera): quantos casos esperam o código 2 e quantos o 0."""
    codigos = Counter(f["esperado"].get("codigo") for f in casos)
    return codigos[2], codigos[0]


def ler(raiz):
    """{hook: {prefixo: [fixture]}} do corpus, em ordem de nome."""
    grupos = defaultdict(lambda: defaultdict(list))
    for caminho in sorted((raiz / CORPUS).glob("*/*.json")):
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        grupos[caminho.parent.name][prefixo(caminho.stem)].append(dados)
    return grupos


def termos_de_stack():
    """Os termos de stack que o núcleo não cita (tests/config.json, `neutralidade_nucleo`)."""
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    return [re.compile(t) for t in config["neutralidade_nucleo"]["termos"]]


def exemplo_neutro(casos, termos):
    """A primeira descrição do grupo sem termo de stack, cortada no máximo; "—" se todas citam algum."""
    for f in casos:
        texto = celula(f.get("descricao", ""))
        if not any(t.search(texto) for t in termos):
            return texto[:MAXIMO_DO_EXEMPLO].rstrip() + "…" if len(texto) > MAXIMO_DO_EXEMPLO else texto
    return "—"


def gerar(raiz=RAIZ, termos=None):
    grupos = ler(raiz)
    termos = termos_de_stack() if termos is None else termos
    total = sum(len(f) for por_prefixo in grupos.values() for f in por_prefixo.values())
    linhas = ["# Índice das fixtures dos hooks", "",
              "<!-- Gerado por scripts/indice-fixtures.py; não edite à mão. Rode o script depois de mudar o corpus. -->", "",
              f"O corpus de `tests/hooks/<hook>/<caso>.json` ({total} fixtures) roda em `tests/test_hooks.py` (ADR 0003): "
              "cada caso dá a entrada de uma chamada ao hook e o código e a saída que ele tem de dar. O índice agrupa por "
              "hook e pelo prefixo do nome do caso (até o primeiro `-`); nenhum caso muda de nome nem de lugar. "
              "\"Recusa\" é `esperado.codigo` 2; \"libera\", 0. As regras são as `R-*` do `stderr` esperado; os cartões, "
              "o identificador que abre a `descricao`.", "", "## Por hook", "", "| Hook | Fixtures | Recusa | Libera | Prefixos |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for hook, por_prefixo in sorted(grupos.items()):
        casos = [f for lista in por_prefixo.values() for f in lista]
        recusa, libera = placar(casos)
        linhas.append(f"| `{hook}` | {len(casos)} | {recusa} | {libera} | {len(por_prefixo)} |")
    for hook, por_prefixo in sorted(grupos.items()):
        linhas += ["", f"## `{hook}`", "", "| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |",
                   "| --- | ---: | ---: | ---: | --- | --- | --- |"]
        for nome, casos in sorted(por_prefixo.items(), key=lambda x: (-len(x[1]), x[0])):
            regras, cartoes = Counter(), Counter()
            for f in casos:
                regras.update(set(REGRA.findall(str(f["esperado"].get("stderr", "")))))
                cartoes.update(CARTAO.findall(f.get("descricao", ""))[:1])  # `^` sem re.M: zero ou um
            exemplo = exemplo_neutro(casos, termos)
            recusa, libera = placar(casos)
            linhas.append(f"| `{nome}-*` | {len(casos)} | {recusa} | {libera} | {resumo(regras)} | {resumo(cartoes)} | {exemplo} |")
    return "\n".join(linhas) + "\n"


def main(argv):
    texto = gerar(RAIZ)
    destino = RAIZ / INDICE
    if argv == ["--conferir"]:
        em_dia = destino.is_file() and destino.read_text(encoding="utf-8") == texto
        print(f"{INDICE}: {'em dia' if em_dia else 'desatualizado; rode scripts/indice-fixtures.py'}")
        return 0 if em_dia else 1
    if argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    destino.write_text(texto, encoding="utf-8")
    print(f"{INDICE}: gravado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
