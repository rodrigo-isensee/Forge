#!/usr/bin/env python3
"""Forge: coletor de cobertura por linha (piso de cobertura, versao-048 E3). Só biblioteca padrão.

Parte E3a-1a: só o gerador do texto do `sitecustomize.py` que coleta (controles C-3, C-4 e C-6 do modelo de ameaças).
`instalar` e `remover`, com as sondas do interpretador, entram na E3a-1b; até lá, rodar o arquivo sai 1.
"""
import os
import sys

# C-4: no topo só sys, os e atexit; nada vai a stdout nem a stderr; toda falha vira contagem no arquivo de acertos.
CORPO = '''_acertos = {}
_estado = {"ligado": False, "motivo": "", "falhas": 0, "chamadas": 0}


def _linha(code, linha):
    try:
        _estado["chamadas"] += 1
        _acertos.setdefault(code.co_filename, set()).add(linha)
    except BaseException:
        _estado["falhas"] += 1
    return _DISABLE


def _ligar():
    global _DISABLE
    m = getattr(sys, "monitoring", None)
    if m is None:
        _estado["motivo"] = "python sem sys.monitoring"
        return
    try:
        m.use_tool_id(m.COVERAGE_ID, "forge-cobertura")
    except ValueError:
        _estado["motivo"] = "id de ferramenta ocupado"
        return
    _DISABLE = m.DISABLE
    m.register_callback(m.COVERAGE_ID, m.events.LINE, _linha)
    m.set_events(m.COVERAGE_ID, m.events.LINE)
    _estado["ligado"] = True


def _gravar():
    try:
        import json
        import secrets
        raiz = _RAIZ + os.sep
        acertos = {}
        for nome, linhas in list(_acertos.items()):
            real = os.path.realpath(nome)
            if real.startswith(raiz):
                acertos[real[len(raiz):]] = sorted(linhas)
        caminho = os.path.join(_SAIDA, f"{os.getpid()}-{secrets.token_hex(8)}.json")
        fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as arquivo:
            json.dump(dict(_estado, acertos=acertos), arquivo)
    except BaseException:
        pass


try:
    atexit.register(_gravar)
    _ligar()
except BaseException:
    _estado["falhas"] += 1
'''


def texto_do_coletor(saida, raiz):
    """O `sitecustomize.py` que anota as linhas executadas sob `raiz` e grava os acertos em `saida` (C-3)."""
    resolvidos = []
    for caminho in (str(saida), str(raiz)):
        if any(c in caminho for c in "\n\r\0"):
            raise ValueError(f"caminho com quebra de linha ou nulo: {caminho!r}")
        resolvidos.append(os.path.realpath(caminho))
    saida, raiz = resolvidos
    return ("# forge-cobertura\nimport atexit\nimport os\nimport sys\n\n"
            f"_SAIDA = {saida!r}\n_RAIZ = {raiz!r}\n_DISABLE = None\n" + CORPO)


if __name__ == "__main__":
    print("cobertura: sem linha de comando até a E3a-1b", file=sys.stderr)
    sys.exit(1)
