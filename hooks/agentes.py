#!/usr/bin/env python3
"""Forge: teto de agentes e relançamento duplicado (ADR 0003, R-TETO).

PreToolUse (Agent/Task): bloqueia se já há o teto de agentes ativos ou um ativo com o mesmo tipo e descrição;
senão reserva a vaga. SubagentStart confirma a reserva com o agent_id; SubagentStop libera a vaga.
Estado em .forge/run/agentes.json; registros expiram (reserva sem início: 5 min; agente: expiracao_horas).
"""
import time

from _comum import bloquear, executar, gravar_json, ler_json

FERRAMENTAS = {"Agent", "Task"}
EVENTOS = {"PreToolUse", "SubagentStart", "SubagentStop"}
RESERVA_S = 300  # a reserva sem SubagentStart (lançamento negado ou falho) não prende a vaga por horas


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
    teto = hook.config()["teto_agentes"]
    if len(agentes) >= teto:
        bloquear("R-TETO", f"{len(agentes)} agentes ativos, teto {teto} (.forge/config.json: teto_agentes); "
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
