#!/usr/bin/env python3
"""Forge: teto de agentes, relançamento duplicado (ADR 0003, R-TETO) e forma da mensagem ao conferente (R-BRIEF).

O teto é adaptativo (nproc, load de 1 min e memória lidos de /proc; fallback 3) e `teto_agentes` em
.forge/config.json o fixa; `teto_maximo` limita o adaptativo.
PreToolUse (Agent/Task): bloqueia qualquer disparo com load >= 0,8 x nproc ou MemAvailable <= max(1 GB, 15% do total) (R-TETO);
bloqueia também se já há o teto de agentes ativos ou um ativo com o mesmo tipo e descrição;
senão reserva a vaga. `FORGE_CARGA_LIVRE=1` no ambiente do processo (só o dono) pula só a trava de carga
(teto e duplicado seguem; o uso fica no erros.log). SubagentStart confirma a reserva com o agent_id; SubagentStop libera a vaga.
Estado em .forge/run/agentes.json; registros expiram (reserva sem início: 5 min; agente: expiracao_horas).
"""
import os
import re
import time
from pathlib import Path

from _comum import RESERVA, bloquear, executar, gravar_json, ler_json

FERRAMENTAS = {"Agent", "Task"}
EVENTOS = {"PreToolUse", "SubagentStart", "SubagentStop"}
RESERVA_S = 300  # a reserva sem SubagentStart (lançamento negado ou falho) não prende a vaga por horas


GB_KB = 1024 * 1024
CARGA_MAX = 0.8  # fração de nproc: o load de 1 min abaixo disso (R-TETO)
PISO_GB = 1.0  # piso de memória disponível; vale o maior entre ele e PISO_FRACAO do total
PISO_FRACAO = 0.15


def nucleos():
    """nproc: os.sched_getaffinity(0) (respeita afinidade e cpuset) quando existir, senão os.cpu_count();
    FORGE_NPROC o substitui (usado nos testes). None se não der."""
    try:
        if hasattr(os, "sched_getaffinity"):
            padrao = len(os.sched_getaffinity(0))
        else:
            padrao = os.cpu_count() or 0
        return int(os.environ.get("FORGE_NPROC") or padrao or 0) or None
    except (ValueError, OSError):
        return None


def medir(proc=None):
    """(load de 1 min, GB disponíveis, GB totais) lidos de /proc; None onde não der (sem /proc, formato inesperado).
    FORGE_PROC aponta para outra raiz (usado nos testes)."""
    proc = Path(proc or os.environ.get("FORGE_PROC") or "/proc")
    try:
        carga = float((proc / "loadavg").read_text(encoding="utf-8").split()[0])
    except (OSError, ValueError, IndexError):
        carga = None
    memoria = total = None
    try:
        linhas = (proc / "meminfo").read_text(encoding="utf-8").splitlines()
        memoria = int(next(l for l in linhas if l.startswith("MemAvailable:")).split()[1]) / GB_KB
        total = int(next(l for l in linhas if l.startswith("MemTotal:")).split()[1]) / GB_KB
    except (OSError, ValueError, IndexError, StopIteration):
        memoria = total = None
    return carga, memoria, total


def carga_alta(carga, memoria, total, nproc):
    """R-TETO: load de 1 min >= 0,8 x nproc ou MemAvailable <= max(1 GB, 15% do total).
    Sem medida (None), nunca é carga alta."""
    if None in (carga, memoria, total, nproc):
        return False
    return carga >= CARGA_MAX * nproc or memoria <= max(PISO_GB, PISO_FRACAO * total)


def teto_adaptativo(carga, memoria, total, nproc):
    """R-TETO: teto absoluto de nproc agentes ao mesmo tempo; a carga alta é outra trava (carga_alta) e
    vale antes dele. Sem medida (None), o padrão de 3, nunca acima de nproc quando ele é conhecido."""
    if None in (carga, memoria, total, nproc):
        padrao = RESERVA["teto_agentes"]
        return min(padrao, nproc) if nproc else padrao
    return nproc


def calcular_teto(config, proc=None):
    """(teto, explicação para a mensagem). `teto_agentes` fixo sobrepõe o adaptativo; `teto_maximo` limita
    os dois (hook e forge-check usam esta função)."""
    maximo = config.get("teto_maximo")
    if config.get("teto_agentes"):
        teto, origem = config["teto_agentes"], "fixo em .forge/config.json: teto_agentes"
    else:
        carga, memoria, total = medir(proc)
        nproc = nucleos()
        teto = teto_adaptativo(carga, memoria, total, nproc)
        origem = f"adaptativo sem leitura de /proc: padrão {teto}" if None in (carga, memoria, total, nproc) \
            else f"adaptativo: load {carga:.1f} de {nproc} núcleos, {memoria:.1f} GB disponíveis"
    limitado = bool(maximo) and teto > maximo
    if limitado:
        teto = maximo
    return teto, origem + (f", limitado por teto_maximo {maximo}" if limitado else "")


def vigentes(agentes, agora, expira_s):
    return [a for a in agentes if isinstance(a, dict) and isinstance(a.get("desde"), (int, float))
            and agora - a["desde"] < (expira_s if a.get("id") else min(RESERVA_S, expira_s))]


CONFERENTE = "forge:conferente"
MODO_DA_MENSAGEM = re.compile(r"modo: (brief|entrega)[ \t]*")
ARQUIVO_DA_MENSAGEM = re.compile(r"^Arquivo:[ \t]*\S*docs/briefs/\S+", re.M)
HASH_DA_MENSAGEM = re.compile(r"^Brief-sha256:[ \t]*[0-9a-f]{64}(?![0-9A-Za-z])", re.M)


def mensagem_sem_forma(prompt):
    """R-BRIEF, só a forma: o que falta no cabeçalho da mensagem ao conferente (primeira linha `modo: brief|entrega`, uma linha
    `Arquivo:` em docs/briefs/ e uma `Brief-sha256:` de 64 hex), ou None. Não lê o arquivo nem recalcula o hash; vários blocos passam."""
    linhas = str(prompt or "").splitlines()
    faltas = []
    if not (linhas and MODO_DA_MENSAGEM.fullmatch(linhas[0])):
        faltas.append("`modo: brief` ou `modo: entrega` na primeira linha")
    if not ARQUIVO_DA_MENSAGEM.search("\n".join(linhas)):
        faltas.append("uma linha `Arquivo:` com o caminho em docs/briefs/")
    if not HASH_DA_MENSAGEM.search("\n".join(linhas)):
        faltas.append("uma linha `Brief-sha256:` com 64 hex")
    return "; ".join(faltas) or None


def lancar(hook, agentes, agora):
    entrada = hook.campo("tool_input") or {}
    tipo = str(entrada.get("subagent_type") or "general-purpose")
    faltas = mensagem_sem_forma(entrada.get("prompt")) if tipo == CONFERENTE else None
    if faltas:
        bloquear("R-BRIEF", "gere a mensagem ao conferente com `forge-check brief mensagem` e envie-a inteira; "
                            f"faltou: {faltas}.")
    for a in agentes:
        if descricao and a.get("tipo") == tipo and a.get("descricao") == descricao:
            bloquear("R-TETO", f"já há um agente {tipo} ativo com a descrição \"{descricao[:60]}\"; "
                               "não relance, espere o resultado dele.")
    carga, memoria, total = medir()
    nproc = nucleos()
    for variavel in ("FORGE_NPROC", "FORGE_PROC"):  # substituem a medida real: ficam registrados
        if os.environ.get(variavel):
            hook.registrar_escape(f"{variavel}={os.environ[variavel]} substitui a medida real do teto de agentes")
    if carga_alta(carga, memoria, total, nproc):  # vale para qualquer teto: teto_agentes e teto_maximo não desligam
        if os.environ.get("FORGE_CARGA_LIVRE") == "1":  # escape só do dono: pula só a trava de carga
            hook.registrar_escape(f"FORGE_CARGA_LIVRE=1 liberou o disparo com carga alta (load {carga:.1f} de {nproc} núcleos, "
                                  f"{memoria:.1f} GB disponíveis)")
        else:
            bloquear("R-TETO", f"carga alta (load {carga:.1f} de {nproc} núcleos, {memoria:.1f} GB disponíveis; limite: load "
                               f"{CARGA_MAX * nproc:.1f} e {max(PISO_GB, PISO_FRACAO * total):.1f} GB): "
                               "nenhum agente novo; espere a carga baixar; só o dono: FORGE_CARGA_LIVRE=1.")
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
