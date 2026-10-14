#!/usr/bin/env python3
"""Forge: doutor (primeiro uso, F3) - roda as conferências rápidas do `forge doutor` ao abrir a sessão e uma vez por dia.

SessionStart: faz o diagnóstico rápido (local, sem rede, sem `gh`) e grava em `.forge/run/doutor`
`{"data", "problemas", "avisado"}`; nunca escreve no stdout (nele o SessionStart vira contexto do modelo, ADR 0003).
Stop: se a data do cache não é a de hoje, refaz o diagnóstico (uma vez por dia); se há problema ainda não avisado,
imprime só `{"systemMessage": "Forge doutor: ..."}` (uma linha, para o USUÁRIO, nunca `additionalContext`) e marca
como avisado. Tudo em ordem: silêncio. Só avisa: o conserto é do comando `forge doutor`, num terminal, com "s".
Erro interno: sai 0 e registra em `erros.log`. Só biblioteca padrão."""
import json
import os
import sys
import time

from _comum import executar, forge_doutor, gravar_json, ler_json

LIMITE_LINHA = 200


def hoje():
    return os.environ.get("FORGE_HOJE") or time.strftime("%Y-%m-%d")  # FORGE_HOJE: só os testes


LIMITE_GIT = 3  # segundos por comando `git` do diagnóstico (o padrão do comando é 15)


def ler_cache(hook):
    try:
        estado = ler_json(hook.run() / "doutor", {})
    except ValueError:
        return {}
    return estado if isinstance(estado, dict) else {}


def examinar(hook, raiz):
    """Diagnostica FORA da trava (o `git` pode demorar); a trava protege só a leitura e a escrita do cache."""
    modulo = forge_doutor()
    modulo.LIMITE_GIT = LIMITE_GIT
    problemas = [p.texto for p in modulo.diagnosticar(raiz, rapido=True)]
    with hook.trava():
        antigo = ler_cache(hook)
        igual = antigo.get("data") == hoje() and antigo.get("problemas") == problemas
        estado = {"data": hoje(), "problemas": problemas, "avisado": bool(igual and antigo.get("avisado"))}
        gravar_json(hook.run() / "doutor", estado)
    return estado


def linha(problemas):
    n = len(problemas)
    primeiro = " ".join(problemas[0].split())
    texto = f"Forge doutor: {n} {'coisa' if n == 1 else 'coisas'} para ver — {primeiro}"
    cauda = " (rode: forge doutor)"
    return texto[: LIMITE_LINHA - len(cauda) - 1] + "…" + cauda if len(texto) + len(cauda) > LIMITE_LINHA else texto + cauda


def principal(hook):
    evento = hook.campo("hook_event_name")
    if evento not in ("SessionStart", "Stop"):
        return
    raiz = hook.projeto(hook.cwd())
    if raiz is None:
        return
    if evento == "SessionStart":  # inclusive resume e compact: reexamina sem reabrir o aviso de hoje
        examinar(hook, raiz)
        return
    with hook.trava():
        estado = ler_cache(hook)
    if estado.get("data") != hoje() or not isinstance(estado.get("problemas"), list):
        estado = examinar(hook, raiz)
    if estado["problemas"] and not estado.get("avisado"):
        with hook.trava():
            estado["avisado"] = True
            gravar_json(hook.run() / "doutor", estado)
        print(json.dumps({"systemMessage": linha([str(p) for p in estado["problemas"]])}, ensure_ascii=False))


if __name__ == "__main__":
    executar("doutor", principal)
    sys.exit(0)
