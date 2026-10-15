#!/usr/bin/env python3
"""Forge: teto de agentes e relançamento duplicado (ADR 0003, R-TETO).

O teto é adaptativo (load e memória disponível, lidos de /proc; fallback 3) e `teto_agentes` em
.forge/config.json o fixa; `teto_maximo` limita o adaptativo.
PreToolUse (Agent/Task): bloqueia qualquer disparo com load > 6 ou < 2 GB disponíveis (R-TETO);
bloqueia também se já há o teto de agentes ativos ou um ativo com o mesmo tipo e descrição;
senão reserva a vaga. SubagentStart confirma a reserva com o agent_id; SubagentStop libera a vaga.
Estado em .forge/run/agentes.json; registros expiram (reserva sem início: 5 min; agente: expiracao_horas).
"""
import os
import time
from pathlib import Path

from _comum import RESERVA, bloquear, executar, gravar_json, ler_json

FERRAMENTAS = {"Agent", "Task"}
EVENTOS = {"PreToolUse", "SubagentStart", "SubagentStop"}
RESERVA_S = 300  # a reserva sem SubagentStart (lançamento negado ou falho) não prende a vaga por horas


GB_KB = 1024 * 1024


def medir(proc=None):
    """(load de 1 min, GB disponíveis) lidos de /proc; None onde não der (sem /proc, formato inesperado).
    FORGE_PROC aponta para outra raiz (usado nos testes)."""
    proc = Path(proc or os.environ.get("FORGE_PROC") or "/proc")
    try:
        carga = float((proc / "loadavg").read_text(encoding="utf-8").split()[0])
    except (OSError, ValueError, IndexError):
        carga = None
    try:
        linha = next(l for l in (proc / "meminfo").read_text(encoding="utf-8").splitlines()
                     if l.startswith("MemAvailable:"))
        memoria = int(linha.split()[1]) / GB_KB
    except (OSError, ValueError, IndexError, StopIteration):
        memoria = None
    return carga, memoria


def teto_adaptativo(carga, memoria):
    """Faixas da R-TETO: 2 (load > 6 ou < 2 GB), 5 (load < 3 e > 4 GB), 4 (load < 4 e > 3 GB), senão 3.
    Sem medida (None), o piso conservador de 3."""
    if carga is None or memoria is None:
        return RESERVA["teto_agentes"]
    if carga > 6 or memoria < 2:
        return 2
    if carga < 3 and memoria > 4:
        return 5
    if carga < 4 and memoria > 3:
        return 4
    return 3


def carga_alta(carga, memoria):
    """R-TETO: load acima de 6 ou menos de 2 GB disponíveis. Sem medida (None), nunca é carga alta."""
    return carga is not None and memoria is not None and (carga > 6 or memoria < 2)


def calcular_teto(config, proc=None):
    """(teto, explicação para a mensagem). `teto_agentes` fixo sobrepõe o adaptativo."""
    if config.get("teto_agentes"):
        return config["teto_agentes"], "fixo em .forge/config.json: teto_agentes"
    carga, memoria = medir(proc)
    teto = teto_adaptativo(carga, memoria)
    maximo = config.get("teto_maximo")
    limitado = bool(maximo) and teto > maximo
    if limitado:
        teto = maximo
    origem = "adaptativo sem leitura de /proc: padrão 3" if carga is None or memoria is None \
        else f"adaptativo: load {carga:.1f}, {memoria:.1f} GB disponíveis"
    return teto, origem + (f", limitado por teto_maximo {maximo}" if limitado else "")


def vigentes(agentes, agora, expira_s):
    return [a for a in agentes if isinstance(a, dict) and isinstance(a.get("desde"), (int, float))
            and agora - a["desde"] < (expira_s if a.get("id") else min(RESERVA_S, expira_s))]


def lancar(hook, agentes, agora):
    entrada = hook.campo("tool_input") or {}
    tipo = str(entrada.get("subagent_type") or "general-purpose")
    descricao = " ".join(str(entrada.get("description") or "").split())
    for a in agentes:
        if descricao and a.get("tipo") == tipo and a.get("descricao") == descricao:
            bloquear("R-TETO", f"já há um agente {tipo} ativo com a descrição \"{descricao[:60]}\"; "
                               "não relance, espere o resultado dele.")
    carga, memoria = medir()
    if carga_alta(carga, memoria):  # vale para qualquer teto: teto_agentes e teto_maximo não desligam
        bloquear("R-TETO", f"carga alta (load {carga:.1f}, {memoria:.1f} GB disponíveis; limite: load 6 e 2 GB): "
                           "nenhum agente novo, mesmo com poucos ativos; espere a carga baixar.")
    teto, motivo = calcular_teto(hook.config())
    if len(agentes) >= teto:
        bloquear("R-TETO", f"{len(agentes)} agentes ativos, teto {teto} ({motivo}); "
                           "espere um terminar antes de lançar outro.")
    agentes.append({"id": None, "tipo": tipo, "descricao": descricao, "desde": agora})


def iniciar(hook, agentes, agora):
    aid, tipo = hook.campo("agent_id"), str(hook.campo("agent_type") or "")
    if not aid or any(a.get("id") == aid for a in agentes):
        return
    reservas = sorted((a for a in agentes if not a.get("id")), key=lambda a: a["desde"])
    # O tipo informado pode vir com ou sem o prefixo do plugin; na dúvida, a reserva mais antiga.
    par = next((a for a in reservas if str(a.get("tipo")) == tipo), None) \
        or next((a for a in reservas if str(a.get("tipo")).split(":")[-1] == tipo.split(":")[-1]), None) \
        or (reservas[0] if reservas else None)
    if par is None:
        agentes.append({"id": aid, "tipo": tipo, "descricao": "", "desde": agora})
    else:
        par.update(id=aid, desde=agora)


def principal(hook):
    evento = hook.campo("hook_event_name")
    if evento not in EVENTOS or (evento == "PreToolUse" and hook.campo("tool_name") not in FERRAMENTAS):
        return
    if not hook.projeto(hook.cwd()):
        return
    with hook.trava():
        arquivo = hook.run() / "agentes.json"
        agora = time.time()
        estado = ler_json(arquivo, {"agentes": []})
        agentes = vigentes(estado.get("agentes", []), agora, hook.expira_s())
        if evento == "PreToolUse":
            lancar(hook, agentes, agora)
        elif evento == "SubagentStart":
            iniciar(hook, agentes, agora)
        else:
            aid = hook.campo("agent_id")
            agentes = [a for a in agentes if not aid or a.get("id") != aid]
        gravar_json(arquivo, {"agentes": agentes})


if __name__ == "__main__":
    executar("agentes", principal)
