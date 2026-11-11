"""Capacidades que o sandbox dos agentes tira (ENVIO-DO-SANDBOX, correção A; pedido v0457, E11).

No sandbox do Bash (bubblewrap), o root não troca o dono de um arquivo para outro usuário (o uid não está mapeado:
o `chown` dá EINVAL) e o /proc montado é o de outro namespace de pid (`/proc/self` não é o pid do processo; `ps`,
grupo de processo e `/proc/<pid>` leem outros processos). O teste que precisa de uma delas chama
`exigir(self, "chown")` ou `exigir(self, "proc")` logo antes de usá-la:
- capacidade presente: segue;
- falta de fato, detectada aqui, e CI vazio ou ausente: pula, com o motivo e a contagem em stderr;
- falta com CI definido: reprova. No CI nada pula, e o `teto_pulados` de tests/config.json não sobe.
Afrouxamento listado no fragmento de changelog da branch (diretriz 3 do dono).
"""
import errno
import functools
import os
import sys
import tempfile
from pathlib import Path

UID_ALHEIO = 65534  # nobody: o mesmo que os testes de dono alheio usam
FALTA_DO_CHOWN = (errno.EINVAL, errno.EPERM)  # uid fora do mapa do namespace, ou sem CAP_CHOWN
pulados = 0


def falta_chown(pasta=None):
    """Motivo se o root não consegue dar um arquivo a outro usuário; None se consegue ou se não é root."""
    if os.geteuid() != 0:
        return None  # quem não é root nem tenta: os testes têm ramo próprio para isso
    with tempfile.TemporaryDirectory(dir=pasta) as tmp:
        alvo = Path(tmp) / "dono"
        alvo.touch()
        try:
            os.chown(alvo, UID_ALHEIO, UID_ALHEIO)
        except OSError as erro:
            if erro.errno not in FALTA_DO_CHOWN:
                raise
            return f"chown para o uid {UID_ALHEIO} falhou ({errno.errorcode[erro.errno]}): uid fora do namespace"
    return None


def falta_proc(proc=Path("/proc"), pid=None):
    """Motivo se o /proc não é o do namespace de pid deste processo; None se é."""
    pid = os.getpid() if pid is None else pid
    try:
        visto = os.readlink(proc / "self")
    except OSError as erro:
        return f"sem {proc}/self ({erro.strerror})"
    if visto != str(pid):
        return f"{proc} de outro namespace de pid ({proc}/self={visto}, pid={pid}): ps, grupo e /proc/<pid> não servem"
    return None


SONDAS = {"chown": falta_chown, "proc": falta_proc}


@functools.lru_cache(maxsize=None)
def falta(capacidade):
    """Motivo da falta da capacidade neste processo (sondada uma vez), ou None."""
    if capacidade not in SONDAS:
        raise ValueError(f"capacidade desconhecida: {capacidade!r} (conheço {sorted(SONDAS)})")
    return SONDAS[capacidade]()


def exigir(teste, capacidade, ambiente=None):
    """Segue com a capacidade; sem ela, pula fora do CI (motivo e contagem em stderr) e reprova com CI definido."""
    motivo = falta(capacidade)
    if motivo is None:
        return
    ambiente = os.environ if ambiente is None else ambiente
    if ambiente.get("CI"):
        teste.fail(f"falta a capacidade {capacidade!r} com CI definido (no CI nada pula): {motivo}")
    global pulados
    pulados += 1
    print(f"sandbox: pulado {pulados} · {teste.id()} · {capacidade}: {motivo}", file=sys.stderr, flush=True)
    teste.skipTest(f"sandbox fora do CI, sem {capacidade}: {motivo}")
