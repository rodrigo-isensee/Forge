"""Teto de pulados da quarentena (v0478 E37.15): conta as quarentenas abertas em tests/ e diz se `teto_pulados` passa
de TETO_PULADOS_ORIGINAL mais elas. Testes em tests/test_catraca.py (TetoDaQuarentena)."""
import ast
from pathlib import Path

# Teto antes da quarentena da S1. O dono autorizou subir `teto_pulados` 1 por quarentena aberta, só enquanto ela durar
# (v0478 E37.15, 19/11); o mesmo PR que tira a quarentena devolve o teto a este valor.
TETO_PULADOS_ORIGINAL = 1
_SKIP_MOTIVO_NO_1O = {"skip", "skipTest"}
_SKIP_MOTIVO_NO_2O = {"skipIf", "skipUnless"}


def _motivo_do_skip(chamada):
    nome = getattr(chamada.func, "attr", getattr(chamada.func, "id", None))
    pos = 0 if nome in _SKIP_MOTIVO_NO_1O else 1 if nome in _SKIP_MOTIVO_NO_2O else None
    arg = chamada.args[pos] if pos is not None and len(chamada.args) > pos else None
    return arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else ""


def quarentenas_abertas(pasta):
    """Os `skip` (decorador ou `skipTest`) cujo motivo começa com 'quarentena', nos test_*.py da pasta e subpastas."""
    return sum(isinstance(no, ast.Call) and _motivo_do_skip(no).startswith("quarentena")
               for arq in sorted(Path(pasta).rglob("test_*.py"))
               for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8"))))


def teto_passa_da_quarentena(teto, abertas):
    return teto > TETO_PULADOS_ORIGINAL + abertas
