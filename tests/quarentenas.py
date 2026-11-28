"""Teto de pulados da quarentena (v0478 E37.15): conta as quarentenas abertas em tests/ e diz se `teto_pulados` passa
de TETO_PULADOS_ORIGINAL mais elas. Testes em tests/test_catraca.py (TetoDaQuarentena)."""
import ast
import datetime
import inspect
import re
import sys
import unittest
from pathlib import Path

# Teto antes da quarentena da S1. O dono autorizou subir `teto_pulados` 1 por quarentena aberta, só enquanto ela durar
# (v0478 E37.15, 19/11); o mesmo PR que tira a quarentena devolve o teto a este valor.
TETO_PULADOS_ORIGINAL = 1
_PRAZO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _motivo_do_skip(chamada, nomes):
    nome = getattr(chamada.func, "attr", getattr(chamada.func, "id", None))
    arg = chamada.args[0] if nome in nomes and chamada.args else None
    return arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else ""


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


def _testes(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _testes(item)
        else:
            yield item


def _definicoes(arquivo, lidos):
    """As `def` do arquivo que citam `skipTest`, pela primeira linha do código (a do 1.o decorador); lido uma vez só."""
    if arquivo not in lidos:
        try:
            texto = Path(arquivo).read_text(encoding="utf-8")
            arvore = ast.parse(texto if "skipTest" in texto else "")  # sem skipTest no arquivo, nada a ler
        except (OSError, SyntaxError, ValueError):
            texto, arvore = "", ast.Module(body=[], type_ignores=[])
        linhas = texto.splitlines()
        lidos[arquivo] = {
            min([no.lineno] + [deco.lineno for deco in no.decorator_list]): no for no in ast.walk(arvore)
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
            and "skipTest" in "\n".join(linhas[no.lineno - 1:no.end_lineno])}
    return lidos[arquivo]


def _motivos(teste, lidos):
    """O motivo do pulo que o unittest dá ao teste (classe ou método marcado), ou os `skipTest` vivos no texto do corpo
    do método real (o código que o unittest roda; sem fonte legível, nenhum)."""
    metodo = getattr(teste, teste._testMethodName)
    if getattr(type(teste), "__unittest_skip__", False) or getattr(metodo, "__unittest_skip__", False):
        motivo = getattr(type(teste), "__unittest_skip_why__", "") or getattr(metodo, "__unittest_skip_why__", "")
        yield motivo if isinstance(motivo, str) else ""
        return
    codigo = getattr(inspect.unwrap(metodo), "__code__", None)
    definicao = codigo and _definicoes(codigo.co_filename, lidos).get(codigo.co_firstlineno)
    for chamada in _chamadas_vivas(definicao.body if definicao else []):
        yield _motivo_do_skip(chamada, {"skipTest"})


def _motivos_carregados(pasta):
    """Os motivos de pulo dos testes que `unittest.TestLoader().discover(pasta)` carrega; sys.path e os módulos voltam."""
    caminho, modulos, lidos = list(sys.path), set(sys.modules), {}
    try:
        carregador = unittest.TestLoader()
        testes = list(_testes(carregador.discover(str(pasta), top_level_dir=str(pasta))))
        if carregador.errors:
            raise ValueError(f"{pasta}: o unittest não carregou a pasta, a contagem não vale: {carregador.errors[0][:300]}")
        return [(teste.id(), motivo) for teste in testes for motivo in _motivos(teste, lidos)]
    finally:
        sys.path[:] = caminho
        for nome in set(sys.modules) - modulos:
            del sys.modules[nome]


def _confere_quarentena(motivo, onde, hoje):
    prazo = _PRAZO.search(motivo)
    if not (prazo and "OK do dono" in motivo):
        raise ValueError(f"{onde}: a quarentena pede no motivo o prazo (AAAA-MM-DD) e o 'OK do dono': {motivo!r}")
    if datetime.date.fromisoformat(prazo.group()) < hoje:
        raise ValueError(f"{onde}: quarentena vencida em {prazo.group()}: tire o skip ou peça ao dono um prazo novo")


def quarentenas_abertas(pasta, hoje=None):
    """Os pulos cujo motivo começa com 'quarentena' nos testes que o unittest carrega da pasta (`discover`): o
    `__unittest_skip_why__` da classe ou do método real e os `skipTest` vivos no corpo do método real. Skip que o
    unittest não aplica (função solta, classe fora do carregador, método sombreado) não conta. Quarentena sem prazo em
    data, sem 'OK do dono' no motivo ou com o prazo antes de `hoje` (padrão: a data de hoje) é recusada (ValueError)."""
    hoje = hoje or datetime.date.today()
    abertas = 0
    for onde, motivo in _motivos_carregados(pasta):
        if motivo.startswith("quarentena"):
            _confere_quarentena(motivo, onde, hoje)
            abertas += 1
    return abertas


def teto_passa_da_quarentena(teto, abertas):
    return teto > TETO_PULADOS_ORIGINAL + abertas
