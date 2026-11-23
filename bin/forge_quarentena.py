"""Forge: a quarentena de teste instável (BP1 Q1, pedido v0478). Só biblioteca padrão; só leitura.

Formato de `tests/quarentena.json`: `{"entradas": [...]}`, uma entrada por teste com `teste`, `classe`, `cartao`, `prova`, `desde`,
`prazo` (AAAA-MM-DD, no máximo `desde` + 7 dias) e `autorizacao` (`A-<n>` do OK do dono). Uma prorrogação, opcional: `prorrogacao`
com `prazo` (no máximo mais 7 dias) e `autorizacao` nova. A data (`hoje`) é sempre argumento: nada aqui lê o relógio.
Falha fechada: arquivo ilegível, link simbólico, acima de `TETO_BYTES`, com chave repetida, aninhado acima do teto de
`hooks/_json_raso.py` (medido aqui, igual no 3.12 e no 3.14) ou qualquer erro de validação vale como "não há entrada ativa", e o
teste roda no portão.
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
try:
    from _json_raso import fundo_demais  # o teto de aninhamento único dos leitores de JSON de controle
finally:
    sys.path.pop(0)

CAMPOS = ("teste", "classe", "cartao", "prova", "desde", "prazo", "autorizacao")
CLASSES = ("relogio", "carga", "ordem", "rede-local", "desconhecida")
TETO_ENTRADAS = 3
PRAZO_DIAS = 7
DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
OK_DO_DONO = re.compile(r"A-[0-9]+")  # só dígito ASCII: \d aceitaria "A-١" (QUARENTENA-DIGITO-ASCII)
TETO_BYTES = 64 * 1024
# id de um teste só: modulo.Classe.metodo (o módulo pode ter pontos), ASCII, o método com o prefixo `test` do unittest.
ID_DE_TESTE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\.test[A-Za-z0-9_]*")


def _sem_chave_repetida(pares):
    objeto = dict(pares)
    if len(objeto) != len(pares):
        raise ValueError("chave repetida no JSON")
    return objeto


def carregar(caminho):
    """Devolve `(entradas, erros)`; arquivo ausente, ilegível, link, grande demais ou fora do formato dá `([], [motivo])`."""
    try:
        with os.fdopen(os.open(Path(caminho), os.O_RDONLY | os.O_NOFOLLOW), "rb") as arq:
            bruto = arq.read(TETO_BYTES + 1)
        if len(bruto) > TETO_BYTES:
            return [], [f"quarentena: arquivo acima de {TETO_BYTES} bytes"]
        texto = bruto.decode("utf-8")
        if fundo_demais(texto):
            return [], ["quarentena ilegível: aninhamento acima do teto"]
        dados = json.loads(texto, object_pairs_hook=_sem_chave_repetida)
        entradas = dados["entradas"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        return [], [f"quarentena ilegível: {e}"]
    if not isinstance(entradas, list) or not all(isinstance(e, dict) for e in entradas):
        return [], ["quarentena: `entradas` não é uma lista de objetos"]
    return entradas, []


def _data(texto):
    if not isinstance(texto, str) or not DATA.fullmatch(texto):
        return None
    try:
        return datetime.date.fromisoformat(texto)
    except ValueError:
        return None


def prazo_efetivo(entrada):
    """A data final da entrada: a da prorrogação, se houver; `None` se não for uma data."""
    pror = entrada.get("prorrogacao")
    return _data(pror.get("prazo") if isinstance(pror, dict) else entrada.get("prazo"))


def _erros_da_entrada(e, hoje):
    nome = e.get("teste", "?")
    erros = [f"{nome}: falta `{c}`" for c in CAMPOS if not e.get(c)]
    if e.get("teste") and not (isinstance(e["teste"], str) and ID_DE_TESTE.fullmatch(e["teste"])):
        erros.append(f"{nome}: `teste` pede o id de um teste só (modulo.Classe.test_metodo)")
    if e.get("classe") and e["classe"] not in CLASSES:
        erros.append(f"{nome}: classe `{e['classe']}` fora de {', '.join(CLASSES)}")
    desde, prazo = _data(e.get("desde")), _data(e.get("prazo"))
    if e.get("desde") and e.get("prazo") and (desde is None or prazo is None):
        erros.append(f"{nome}: `desde` e `prazo` pedem AAAA-MM-DD")
    elif desde and prazo and not desde <= prazo <= desde + datetime.timedelta(days=PRAZO_DIAS):
        erros.append(f"{nome}: prazo fora de {PRAZO_DIAS} dias a partir de `desde`")
    if desde and hoje < desde:
        erros.append(f"{nome}: `desde` no futuro ({desde} depois de {hoje})")
    if e.get("autorizacao") and not OK_DO_DONO.fullmatch(str(e["autorizacao"])):
        erros.append(f"{nome}: `autorizacao` pede A-<n>")
    if "prorrogacao" in e:
        erros += _erros_da_prorrogacao(nome, e, prazo)
    return erros


def _erros_da_prorrogacao(nome, e, prazo):
    pror = e["prorrogacao"]
    if not isinstance(pror, dict):
        return [f"{nome}: `prorrogacao` pede um objeto"]
    novo = _data(pror.get("prazo"))
    if novo is None or prazo is None or not prazo < novo <= prazo + datetime.timedelta(days=PRAZO_DIAS):
        return [f"{nome}: prorrogação fora de {PRAZO_DIAS} dias depois do `prazo`"]
    if not OK_DO_DONO.fullmatch(str(pror.get("autorizacao"))) or pror["autorizacao"] == e.get("autorizacao"):
        return [f"{nome}: prorrogação pede um OK novo do dono (A-<n> diferente)"]
    return []


def validar(entradas, hoje):
    """Lista os erros: campos, formato, prazos, prorrogação única, teste repetido e o teto de entradas ativas."""
    erros = [m for e in entradas for m in _erros_da_entrada(e, hoje)]
    ids = [e.get("teste") for e in entradas]
    erros += [f"{t}: `teste` repetido na quarentena" for i, t in enumerate(ids) if t and t in ids[:i]]
    if sum(1 for e in entradas if (_p := prazo_efetivo(e)) is not None and hoje <= _p) > TETO_ENTRADAS:
        erros.append(f"quarentena: mais de {TETO_ENTRADAS} entradas ativas")
    return erros


def ativas(entradas, hoje):
    """As entradas que valem em `hoje` (até o prazo, inclusive); com qualquer erro, nenhuma (falha fechada)."""
    if validar(entradas, hoje):
        return []
    return [e for e in entradas if hoje <= prazo_efetivo(e)]


def vencidas(entradas, hoje):
    """As entradas válidas cujo prazo passou: voltam sozinhas ao portão."""
    if validar(entradas, hoje):
        return []
    return [e for e in entradas if prazo_efetivo(e) < hoje]
