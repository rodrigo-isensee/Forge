#!/usr/bin/env python3
"""Forge: ambiente (E2.54, ordem do dono) - ao abrir a sessão no container, confere o ambiente e põe as linhas `falta:` no contexto.

SessionStart: roda `preparar-estacao.sh --verificar` (clone do Forge) ou o `preparar-ambiente.sh --verificar` do modelo de
projeto (projeto com `.devcontainer/devcontainer.json`) e imprime só as linhas `falta:`, com o comando exato de cada uma, para o
Jarvis dá-las ao usuário na 1ª mensagem. Exceção declarada à saída muda da ADR 0003: o stdout do SessionStart é o contexto e só
sai quando falta algo; ambiente em ordem, fora de container, erro ou demora: silêncio.
R-SEGURANCA: o script vem do PLUGIN (cópia instalada, que o agente não grava), nunca do work tree que o agente edita; o
`--verificar` só lê. Só biblioteca padrão."""
import os
import subprocess
import sys
from pathlib import Path

from _comum import PLUGIN, e_clone_do_forge, executar, raiz_de_estado

LIMITE_S = 7  # abaixo do timeout de 10 s do hooks.json (o `gh auth status` fala com a rede)


def no_container(raiz):
    persistente = Path(os.environ.get("FORGE_PERSISTENTE") or "/workspaces").resolve()
    return persistente in raiz.resolve().parents


def faltas(raiz):
    """As linhas `falta:` do `--verificar` adequado a `raiz`, ou []."""
    if e_clone_do_forge(raiz):
        comando, env = PLUGIN / "scripts" / "preparar-estacao.sh", {"FORGE_ORIGEM": str(raiz)}
    elif (raiz / ".devcontainer" / "devcontainer.json").is_file():
        comando, env = PLUGIN / "templates" / "projeto" / ".devcontainer" / "preparar-ambiente.sh", {"FORGE_PROJETO": str(raiz)}
    else:
        return []
    if not comando.is_file():
        return []
    try:
        r = subprocess.run(["bash", str(comando), "--verificar"], env={**os.environ, **env}, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=LIMITE_S)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [linha for linha in r.stdout.splitlines() if linha.startswith("falta: ")] if r.returncode == 1 else []


def principal(hook):
    if hook.campo("hook_event_name") != "SessionStart":
        return
    raiz = raiz_de_estado(hook.cwd())
    if raiz is None or not no_container(raiz):
        return
    linhas = faltas(raiz)
    if linhas:
        print("Forge, ambiente do container incompleto. Jarvis: dê ao dono, na 1ª mensagem, o comando exato de cada linha `falta:`.")
        print("\n".join(linhas))


if __name__ == "__main__":
    executar("ambiente", principal)
    sys.exit(0)
