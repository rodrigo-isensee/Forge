"""0.44.2 (troca dos testes de frase): o teste de texto confere a âncora (o título ou o começo da linha, que outros textos citam) e
a presença do ID da regra que manda, nunca a frase inteira; o corte de orçamento reescreve a frase sem quebrar o teste. A regra
continua protegida pelos invariantes por ID em tests/config.json."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ID = re.compile(r"\bR-[A-Z]+\b")


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def ids(texto):
    """Os IDs de regra citados no texto que existem em docs/regras/ (arquivo próprio, trecho de R-LIMITES.md ou, como o
    `R-WIP` desde a E1 da 0.45.7, linha sem link na tabela do README: regra só de hook, com o texto no próprio índice)."""
    limites = ler("docs/regras/R-LIMITES.md")
    indice = ler("docs/regras/README.md")
    return {i for i in ID.findall(texto)
            if (RAIZ / "docs" / "regras" / f"{i}.md").is_file() or f"## {i}:" in limites or f"| `{i}` |" in indice}


def linha(rel, ancora):
    """A única linha de `rel` que começa (sem os espaços) pela âncora; AssertionError se não há uma só."""
    achadas = [l for l in ler(rel).splitlines() if l.strip().startswith(ancora)]
    if len(achadas) != 1:
        raise AssertionError(f"{rel}: {len(achadas)} linhas começam por {ancora!r} (precisa de uma)")
    return achadas[0]
