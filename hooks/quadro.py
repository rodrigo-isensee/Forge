#!/usr/bin/env python3
"""Forge: quadro válido após edição (ADR 0003, R-WIP).

PostToolUse (Write/Edit/MultiEdit) do KANBAN.md da raiz do projeto: roda a validação do `forge-check kanban`
e, se houver violação de formato ou de WIP, sai com 2 mostrando a primeira ao agente.
"""
from pathlib import Path

from _comum import bloquear, executar, forge_check, separar_regra

FERRAMENTAS = {"Write", "Edit", "MultiEdit"}


def principal(hook):
    if hook.campo("hook_event_name") != "PostToolUse" or hook.campo("tool_name") not in FERRAMENTAS:
        return
    caminho = hook.campo("tool_input", "file_path")
    if not isinstance(caminho, str) or Path(caminho).name != "KANBAN.md":
        return
    arquivo = Path(caminho) if Path(caminho).is_absolute() else hook.cwd() / caminho
    raiz = hook.projeto(arquivo.parent)
    if not raiz or arquivo.resolve() != (raiz / "KANBAN.md").resolve():
        return
    violacoes = forge_check().cmd_kanban(raiz)
    if violacoes:
        rid, texto = separar_regra(violacoes[0], "R-WIP")
        extra = f" (e mais {len(violacoes) - 1})" if len(violacoes) > 1 else ""
        bloquear(rid, f"{texto}{extra}; corrija o quadro (forge-check kanban).")


if __name__ == "__main__":
    executar("quadro", principal)
