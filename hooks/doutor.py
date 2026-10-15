#!/usr/bin/env python3
"""Forge: doutor (primeiro uso, F3) - roda as conferências rápidas do `forge doutor` ao abrir a sessão e uma vez por dia.

SessionStart: faz o diagnóstico rápido (local, sem rede, sem `gh`) e grava em `.forge/run/doutor`
`{"data", "problemas", "avisado"}`; nunca escreve no stdout (nele o SessionStart vira contexto do modelo, ADR 0003).
Stop: se a data do cache não é a de hoje, refaz o diagnóstico (uma vez por dia); se há problema ainda não avisado,
imprime só `{"systemMessage": "Forge doutor: ..."}` (uma linha, para o USUÁRIO, nunca `additionalContext`) e marca
como avisado. Também no Stop, uma vez por dia, consulta as releases do Forge (`git ls-remote --tags`, 3 s, só https; cache em
`.forge/run/versao-nova`) e acrescenta à mesma linha o aviso de versão nova. Tudo em ordem: silêncio. Só avisa: o conserto é do comando `forge doutor`, num terminal, com "s".
Erro interno: sai 0 e registra em `erros.log`. Só biblioteca padrão."""
import json
import os
import sys
import time

from _comum import PLUGIN, executar, forge_doutor, gravar_json, ler_json

LIMITE_LINHA = 200


def hoje():
    return os.environ.get("FORGE_HOJE") or time.strftime("%Y-%m-%d")  # FORGE_HOJE: só os testes


LIMITE_GIT = 3  # segundos por comando `git` do diagnóstico (o padrão do comando é 15)
LIMITE_REDE = 3  # segundos da consulta diária às releases do Forge (a única parte que usa a rede, só no Stop)


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


def ler_cache_versao(hook):
    try:
        estado = ler_json(hook.run() / "versao-nova", {})
    except ValueError:
        return {}
    return estado if isinstance(estado, dict) else {}


def aviso_de_versao_nova(hook):
    """Uma vez por dia (cache `.forge/run/versao-nova`): consulta as releases, FORA da trava, e devolve a frase de aviso se saiu
    versão nova e ainda não foi dita hoje; senão None. Sem rede ou consulta desligada: silêncio (e o dia fica marcado)."""
    with hook.trava():
        antigo = ler_cache_versao(hook)
        if antigo.get("data") == hoje():
            texto, avisa = str(antigo.get("texto") or ""), bool(antigo.get("texto")) and not antigo.get("avisado")
            if avisa:
                gravar_json(hook.run() / "versao-nova", {**antigo, "avisado": True})
            return texto if avisa else None
    sys.path.insert(0, str(PLUGIN / "bin"))
    import forge_versoes
    texto = forge_versoes.aviso_de_versao_nova(LIMITE_REDE)
    with hook.trava():  # outra sessão pode ter consultado enquanto esta esperava a rede
        antigo = ler_cache_versao(hook)
        if antigo.get("data") == hoje():
            texto, avisado = str(antigo.get("texto") or ""), bool(antigo.get("avisado"))
        else:
            avisado = False
        avisa = bool(texto) and not avisado
        gravar_json(hook.run() / "versao-nova", {"data": hoje(), "texto": texto, "avisado": avisado or avisa})
    return texto if avisa else None


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
    partes = [linha(mostrar)] if mostrar else []
    nova = aviso_de_versao_nova(hook)
    if nova:
        partes.append(nova)
    if partes:
        print(json.dumps({"systemMessage": " · ".join(partes)}, ensure_ascii=False))


if __name__ == "__main__":
    executar("doutor", principal)
    sys.exit(0)
