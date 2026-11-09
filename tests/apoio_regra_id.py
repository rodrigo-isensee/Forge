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
    """Os IDs de regra citados no texto que existem em docs/regras/."""
    return {i for i in ID.findall(texto) if (RAIZ / "docs" / "regras" / f"{i}.md").is_file()}


def linha(rel, ancora):
    """A única linha de `rel` que começa (sem os espaços) pela âncora; AssertionError se não há uma só."""
    achadas = [l for l in ler(rel).splitlines() if l.strip().startswith(ancora)]
    if len(achadas) != 1:
        raise AssertionError(f"{rel}: {len(achadas)} linhas começam por {ancora!r} (precisa de uma)")
    return achadas[0]
