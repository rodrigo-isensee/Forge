#!/usr/bin/env python3
"""Forge: estado da máquina (diretriz 35), fora dos repositórios, em PASTA (0700), gravado só pelos hooks.

MP2: o SessionStart e o Stop de cada sessão anotam a sessão em ATIVOS, com o projeto (nome da pasta da raiz, como no `meta`),
a pasta, o pid da sessão e o batimento (a hora da anotação). A sessão some quando o processo dela acaba ou passa BATIMENTO_S
sem bater: a poda roda a cada anotação, e quem lê as sessões filtra de novo (`vivas`; `forge-status --maquina`).
Formato: {"projetos": [nomes], "sessoes": {session_id: {...}}}; a chave `projetos` é a que o `meta` e o `agentes` leem
(MP1, MP5). Registro ilegível ou fora da forma recomeça vazio na próxima anotação.
MP4: a mesma pasta guarda as vagas e a fila do hook `pesado` (`pesado.json`, `pesado.fila/`), sob a mesma `trava`.
"""
import contextlib
import fcntl
import json
import os
import time
from pathlib import Path

from _comum import executar, expandir_home, gravar_json

PASTA = "~/.forge/maquina"
ATIVOS = "projetos-ativos.json"
BATIMENTO_S = 1800  # meia hora sem turno nenhum: a sessão deixa de contar como ativa
EVENTOS = {"SessionStart", "Stop"}


def caminho_da_pasta():
    """PASTA, ou `FORGE_MAQUINA` do ambiente do processo do hook (os testes; o `export` dos agentes não chega ao hook)."""
    return Path(expandir_home(os.environ.get("FORGE_MAQUINA") or PASTA))


def pasta():
    """A pasta do estado da máquina, criada; em link, levanta (ninguém desvia o estado para outro lugar)."""
    caminho = caminho_da_pasta()
    if caminho.is_symlink():
        raise OSError(f"{caminho} é link")
    caminho.mkdir(mode=0o700, parents=True, exist_ok=True)
    return caminho


@contextlib.contextmanager
def trava():
    """Exclusão mútua entre os hooks de todas as sessões da máquina."""
    with open(pasta() / ".trava", "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def ler(nome):
    """O objeto JSON de `nome` na pasta; {} sem o arquivo, em link, ilegível ou fora da forma."""
    caminho = pasta() / nome
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8")) if not caminho.is_symlink() else {}
    except (OSError, ValueError, RecursionError):
        return {}
    return dados if isinstance(dados, dict) else {}


def gravar(nome, dados):
    gravar_json(pasta() / nome, dados)


def vivas(sessoes, agora, vivo):
    """As sessões que bateram há menos de BATIMENTO_S e cujo processo segue vivo (`vivo(pid, inicio)`)."""
    sessoes = sessoes if isinstance(sessoes, dict) else {}
    return {sid: s for sid, s in sessoes.items() if isinstance(s, dict) and isinstance(s.get("batimento"), (int, float))
            and 0 <= agora - s["batimento"] < BATIMENTO_S and vivo(s.get("pid"), s.get("inicio"))}


def anotar(hook):
    from pesado import inicio_de, pid_da_sessao, pid_vivo  # o `pesado` importa este módulo
    sid, raiz = hook.campo("session_id"), hook.projeto(hook.cwd(), clone_do_forge=True)
    if hook.campo("hook_event_name") not in EVENTOS or not isinstance(sid, str) or not sid or not raiz:
        return
    dono, agora = pid_da_sessao(), time.time()
    with trava():
        sessoes = vivas(ler(ATIVOS).get("sessoes"), agora, pid_vivo)
        sessoes[sid] = {"projeto": Path(raiz).name, "pasta": str(raiz), "pid": dono, "inicio": inicio_de(dono), "batimento": agora}
        nomes = {s["projeto"] for s in sessoes.values() if isinstance(s.get("projeto"), str)}
        gravar(ATIVOS, {"projetos": sorted(nomes), "sessoes": sessoes})


if __name__ == "__main__":
    executar("maquina", anotar)
