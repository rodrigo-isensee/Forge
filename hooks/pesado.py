#!/usr/bin/env python3
"""Forge: tarefa pesada uma de cada vez (ADR 0003, R-TETO).

PreToolUse (Bash): se o comando casa com `pesados` de .forge/config.json e outra tarefa pesada está ativa
(trava com o PID da sessão vivo e dentro da expiração), bloqueia; senão pega a trava.
PostToolUse e PostToolUseFailure (Bash) do mesmo comando soltam a trava. Estado em .forge/run/pesado.json.
"""
import os
import time
from pathlib import Path

from _comum import bloquear, executar, gravar_json, ler_json

CASCAS = {"sh", "bash", "dash", "zsh"}


def normalizar(texto):
    return " ".join(texto.split()).lower()


def pid_da_sessao():
    """PID do Claude Code que chamou o hook (pula uma casca intermediária, se houver)."""
    pid = os.getppid()
    try:
        if Path(f"/proc/{pid}/comm").read_text(encoding="utf-8").strip() in CASCAS:
            pid = int(Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return pid


def pid_vivo(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def principal(hook):
    if hook.campo("tool_name") != "Bash":
        return
    comando = hook.campo("tool_input", "command")
    evento = hook.campo("hook_event_name")
    if not isinstance(comando, str) or evento not in ("PreToolUse", "PostToolUse", "PostToolUseFailure"):
        return
    if not hook.projeto(hook.cwd()):
        return
    texto = normalizar(comando)
    if not any(normalizar(p) in texto for p in hook.config()["pesados"]):
        return
    uso = hook.campo("tool_use_id")
    with hook.trava():
        arquivo = hook.run() / "pesado.json"
        trava = ler_json(arquivo, None)
        if evento != "PreToolUse":
            if isinstance(trava, dict) and (not uso or trava.get("tool_use_id") in (uso, None)):
                arquivo.unlink()
            return
        agora = time.time()
        if isinstance(trava, dict) and trava.get("tool_use_id") != uso and pid_vivo(trava.get("pid")) \
                and isinstance(trava.get("desde"), (int, float)) and agora - trava["desde"] < hook.expira_s():
            minutos = int((agora - trava["desde"]) // 60)
            bloquear("R-TETO", f"tarefa pesada em andamento há {minutos} min (`{str(trava.get('comando'))[:50]}`); "
                               "rode uma de cada vez e tente quando ela terminar.")
        gravar_json(arquivo, {"pid": pid_da_sessao(), "comando": " ".join(comando.split())[:120],
                              "desde": agora, "tool_use_id": uso})


if __name__ == "__main__":
    executar("pesado", principal)
