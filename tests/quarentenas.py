"""Teto de pulados da quarentena (v0478 E37.15): conta as quarentenas abertas em tests/ e diz se `teto_pulados` passa
de TETO_PULADOS_ORIGINAL mais elas. Testes em tests/test_catraca.py (TetoDaQuarentena)."""
import ast
import re
from pathlib import Path

# Teto antes da quarentena da S1. O dono autorizou subir `teto_pulados` 1 por quarentena aberta, só enquanto ela durar
# (v0478 E37.15, 19/11); o mesmo PR que tira a quarentena devolve o teto a este valor.
TETO_PULADOS_ORIGINAL = 1
_PRAZO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _motivo_do_skip(chamada, nomes):
    nome = getattr(chamada.func, "attr", getattr(chamada.func, "id", None))
    arg = chamada.args[0] if nome in nomes and chamada.args else None
    return arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else ""


def _e_testcase(classe):
    return any(getattr(base, "attr", getattr(base, "id", None)) == "TestCase" for base in classe.bases)


def _chamadas_vivas(filhos):
    """As chamadas dos nós, sem entrar em função aninhada nem em ramo `if False`/`if 0` óbvio."""
    for no in filhos:
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(no, ast.Call):
            yield no
        if isinstance(no, ast.If) and isinstance(no.test, ast.Constant) and not no.test.value:
            yield from _chamadas_vivas(no.orelse)
        else:
            yield from _chamadas_vivas(ast.iter_child_nodes(no))


def _motivos_vivos(arvore):
    for classe in ast.walk(arvore):
        if not (isinstance(classe, ast.ClassDef) and _e_testcase(classe)):
            continue
        for metodo in classe.body:
            if not (isinstance(metodo, ast.FunctionDef) and metodo.name.startswith("test_")):
                continue
            for deco in metodo.decorator_list:
                yield _motivo_do_skip(deco, {"skip"}) if isinstance(deco, ast.Call) else ""
            for chamada in _chamadas_vivas(metodo.body):
                yield _motivo_do_skip(chamada, {"skipTest"})


def _confere_quarentena(motivo, onde):
    if not (_PRAZO.search(motivo) and "OK do dono" in motivo):
        raise ValueError(f"{onde}: a quarentena pede no motivo o prazo (AAAA-MM-DD) e o 'OK do dono': {motivo!r}")


def quarentenas_abertas(pasta):
    """Os `@unittest.skip` em `test_*` de TestCase e os `skipTest` no corpo de `test_*` cujo motivo começa com 'quarentena',
    nos test_*.py da pasta e subpastas. Skip morto (função nunca chamada, `if False`, classe que não é TestCase) não conta.
    Quarentena sem prazo em data ou sem 'OK do dono' no motivo é recusada (ValueError)."""
    abertas = 0
    for arq in sorted(Path(pasta).rglob("test_*.py")):
        for motivo in _motivos_vivos(ast.parse(arq.read_text(encoding="utf-8"))):
            if motivo.startswith("quarentena"):
                _confere_quarentena(motivo, arq.name)
                abertas += 1
    return abertas


def teto_passa_da_quarentena(teto, abertas):
    return teto > TETO_PULADOS_ORIGINAL + abertas
