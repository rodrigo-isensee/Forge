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


def diagnosticar(raiz):
    """O diagnóstico em si, FORA da trava (o `git` pode demorar)."""
    modulo = forge_doutor()
    modulo.LIMITE_GIT = LIMITE_GIT
    return [p.texto for p in modulo.diagnosticar(raiz, rapido=True)]


def registrar(hook, problemas, avisar):
    """Sob a trava: relê o cache, decide se avisa e grava, tudo de uma vez (duas sessões não avisam duas vezes).
    Devolve os problemas a mostrar ao usuário, ou None."""
    with hook.trava():
        antigo = ler_cache(hook)
        igual = antigo.get("data") == hoje() and antigo.get("problemas") == problemas
        avisado = bool(igual and antigo.get("avisado"))
        avisa = avisar and bool(problemas) and not avisado
        gravar_json(hook.run() / "doutor", {"data": hoje(), "problemas": problemas, "avisado": avisado or avisa})
    return problemas if avisa else None


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
        registrar(hook, diagnosticar(raiz), avisar=False)
        return
    with hook.trava():  # cache de hoje: decide e marca "avisado" na mesma trava
        estado = ler_cache(hook)
        valido = estado.get("data") == hoje() and isinstance(estado.get("problemas"), list)
        problemas = [str(p) for p in estado["problemas"]] if valido else []
        avisa = valido and bool(problemas) and not estado.get("avisado")
        if avisa:
            estado["avisado"] = True
            gravar_json(hook.run() / "doutor", estado)
    mostrar = problemas if avisa else None
    if not valido:  # primeira vez hoje: diagnostica fora da trava e decide de novo, relendo o cache
        mostrar = registrar(hook, diagnosticar(raiz), avisar=True)
    if mostrar:
        print(json.dumps({"systemMessage": linha(mostrar)}, ensure_ascii=False))


if __name__ == "__main__":
    executar("doutor", principal)
    sys.exit(0)
