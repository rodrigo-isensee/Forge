"""Forge: o que `bin/forge-testes` e `bin/forge-mutante` têm em comum (FILA-31 F1): a linha de contexto do log (MAQ-A7), com as
outras pesadas vivas. Só biblioteca padrão; importado pelos dois pelo caminho da própria pasta."""
import os
import re
from pathlib import Path

# MAQ-A7: a linha do log ganha a entrada (FORGE_ENTRADA validada), o load, os núcleos e as outras pesadas vivas.
ENTRADA, PESADA = re.compile(r"[a-z-]{1,20}"), re.compile(r"suite-paralela\.py|unittest discover|forge-testes|forge-mutante")


def outras(proc=Path("/proc"), eu=None):
    """Pesadas vivas fora desta e dos ancestrais dela; erro de leitura do /proc dá "?"; a linha lida nunca se guarda."""
    try:
        fora, pid = set(), eu or os.getpid()
        while pid > 1 and pid not in fora:
            fora.add(pid)
            pid = int((proc / str(pid) / "stat").read_text().rsplit(")", 1)[1].split()[1])
        pids = [p for p in os.listdir(proc) if p.isdigit() and int(p) not in fora]
    except (OSError, ValueError, IndexError):
        return "?"
    n = 0
    for p in pids:
        try:  # o processo que termina no meio da leitura não derruba a contagem
            n += bool(PESADA.search((proc / p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")))
        except OSError:
            continue
    return n


def contexto():
    entrada = os.environ.get("FORGE_ENTRADA", "autor")
    try:
        load1 = f"{os.getloadavg()[0]:.2f}"
    except OSError:
        load1 = "?"
    return f" entrada={entrada if ENTRADA.fullmatch(entrada) else '?'} load1={load1} nproc={os.cpu_count()} outras={outras()}"

