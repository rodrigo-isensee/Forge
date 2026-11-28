#!/usr/bin/env python3
"""Forge: estado da máquina (diretriz 35), fora dos repositórios, em PASTA (0700), gravado só pelos hooks.

MP2: o SessionStart e o Stop de cada sessão anotam a sessão em ATIVOS, com o projeto e a pasta da cópia principal
(`identidade`: a sessão numa worktree conta como o projeto dela), o pid da sessão e o batimento (a hora da anotação). A
sessão some quando o processo dela acaba ou passa BATIMENTO_S sem bater: a poda roda a cada anotação, e quem lê as
sessões filtra de novo (`vivas`; `forge-status --maquina`).
Formato: {"projetos": [nomes], "sessoes": {session_id: {...}}}; a chave `projetos` é a que o `meta` e o `agentes` leem
(MP1, MP5). Registro ilegível ou fora da forma recomeça vazio na próxima anotação.
MP4: a mesma pasta guarda as vagas e a fila do hook `pesado` (`pesado.json`, `pesado.fila/`), sob a mesma `trava`.
"""
import contextlib
import fcntl
import json
import os
import stat
import tempfile
import time
from pathlib import Path

from _comum import executar, expandir_home, so_do_usuario

PASTA = "~/.forge/maquina"
ATIVOS = "projetos-ativos.json"
BATIMENTO_S = 1800  # meia hora sem turno nenhum: a sessão deixa de contar como ativa
EVENTOS = {"SessionStart", "Stop"}
TETO_DE_BYTES = 65536  # o registro e as vezes cabem folgados; maior que isso não se lê


def caminho_da_pasta():
    """PASTA, ou `FORGE_MAQUINA` do ambiente do processo do hook (os testes; o `export` dos agentes não chega ao hook)."""
    return Path(expandir_home(os.environ.get("FORGE_MAQUINA") or PASTA))


def pasta():
    """A pasta do estado da máquina, criada; em link, de outro dono ou aberta ao grupo, levanta (segurança A6)."""
    caminho = caminho_da_pasta()
    if caminho.is_symlink():
        raise OSError(f"{caminho} é link")
    caminho.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not so_do_usuario(caminho) or os.stat(caminho).st_mode & 0o077:
        raise OSError(f"{caminho} não é só do usuário (0700)")
    return caminho


@contextlib.contextmanager
def trava():
    """Exclusão mútua entre os hooks de todas as sessões da máquina."""
    with open(pasta() / ".trava", "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def ler(nome):
    """O objeto JSON de `nome` na pasta; {} sem o arquivo, em link, FIFO, acima do teto, ilegível ou fora da forma."""
    try:
        dados = json.loads(ler_regular(pasta() / nome, TETO_DE_BYTES))
    except (OSError, ValueError, RecursionError):
        return {}
    return dados if isinstance(dados, dict) else {}


def ler_regular(caminho, teto):
    """Até `teto` bytes do arquivo regular `caminho`, sem seguir link nem esperar FIFO (segurança A4); acima, levanta."""
    fd = os.open(caminho, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(f"{caminho} não é arquivo regular")
        bruto = f.read(teto + 1)
    if len(bruto) > teto:
        raise OSError(f"{caminho} passa de {teto} bytes")
    return bruto.decode("utf-8")


def gravar(nome, dados):
    """Temporário de nome imprevisível criado com O_EXCL (não segue link plantado; segurança A5) e trocado de uma vez."""
    destino = pasta() / nome
    fd, tmp = tempfile.mkstemp(dir=destino.parent, prefix=f".{nome}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(dados, ensure_ascii=False, indent=1) + "\n")
        os.replace(tmp, destino)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def vivas(sessoes, agora, vivo):
    """As sessões que bateram há menos de BATIMENTO_S e cujo processo segue vivo (`vivo(pid, inicio)`)."""
    sessoes = sessoes if isinstance(sessoes, dict) else {}
    return {sid: s for sid, s in sessoes.items() if isinstance(s, dict) and isinstance(s.get("batimento"), (int, float))
            and 0 <= agora - s["batimento"] < BATIMENTO_S and vivo(s.get("pid"), s.get("inicio"))}


def identidade(hook):
    """(nome, pasta) do projeto do hook, depois do `hook.projeto`: a cópia principal, a mesma no registro (MP2) e no teto
    de agentes (MP3). A sessão numa worktree conta como o projeto dela; a pasta separa projetos de mesmo nome."""
    principal = Path(hook.copia_principal())
    return principal.name, str(principal)


def anotar(hook):
    from pesado import inicio_de, pid_da_sessao, pid_vivo  # o `pesado` importa este módulo
    sid, raiz = hook.campo("session_id"), hook.projeto(hook.cwd(), clone_do_forge=True)
    if hook.campo("hook_event_name") not in EVENTOS or not isinstance(sid, str) or not sid or not raiz:
        return
    dono, agora = pid_da_sessao(), time.time()
    nome, principal = identidade(hook)
    with trava():
        sessoes = vivas(ler(ATIVOS).get("sessoes"), agora, pid_vivo)
        sessoes[sid] = {"projeto": nome, "pasta": principal, "pid": dono, "inicio": inicio_de(dono), "batimento": agora}
        nomes = {s["projeto"] for s in sessoes.values() if isinstance(s.get("projeto"), str)}
        gravar(ATIVOS, {"projetos": sorted(nomes), "sessoes": sessoes})


if __name__ == "__main__":
    executar("maquina", anotar)
