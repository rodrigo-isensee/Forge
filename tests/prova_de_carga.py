"""Prova de carga do `test_prazo_do_merge` (DEFEITO-TESTES-DE-PRAZO-SOB-CARGA, v0478): quando a recusa do vigia do
prazo longo vale como carga da máquina, e não como defeito do hook. Fora de `test_hooks.py` para os mutantes declarados
(`tests/mutantes/v0478-testes-prazo*.json`); só os testes importam este módulo."""
import contextlib
import os
import subprocess
import sys

# DEFEITO-TESTES-DE-PRAZO-SOB-CARGA (v0478): o fixture de merge que libera com o git lento (3,5 s) cabe no prazo longo
# (`PRAZO_DO_MERGE_S`, 7,5 s) só se o resto do hook roda em menos de 4 s de relógio; com a máquina em carga acima de 20, a vez na
# CPU passa disso e o vigia recusa sem o hook ter erro. A recusa só vale como carga quando a mensagem e o relógio são os do prazo
# longo (o defeito de cair nos 3 s recusa com "em 3 s", antes dos 7,5), a CPU do hook somada ao `sleep` do git lento cabe no prazo
# com a folga e a disputa pela CPU está provada no mesmo intervalo: um processo irmão que só gasta CPU (`referencia_da_cpu`)
# conseguiu no máximo `PARCELA_DE_DISPUTA` do relógio, e o hook usou na CPU ao menos `APROVEITAMENTO_MINIMO` da parcela da
# referência no tempo fora do sono (quem espera na fila da CPU gasta CPU no ritmo que a fila deixa; quem dorme, trava ou espera
# E/S, não). A S1 do review (3,8 s de sono a mais) reprova: com a máquina livre pela referência perto de 1; em carga, pelo
# aproveitamento (0,08 medido com carga 24, contra 0,7 a 1,5 do hook que só esperou a fila).
FOLGA_DA_CPU_NO_PRAZO_S = 1.0
PARCELA_DE_DISPUTA = 0.5
APROVEITAMENTO_MINIMO = 0.5
# A referência avisa que está pronta, gasta CPU até o SIGTERM e responde com a CPU e o relógio dela desde o aviso.
_REFERENCIA_DA_CPU = """import signal, sys, time
def fim(*_):
    print(time.process_time() - cpu, time.monotonic() - inicio, flush=True)
    sys.exit(0)
signal.signal(signal.SIGTERM, fim)
cpu, inicio = time.process_time(), time.monotonic()
print("pronta", flush=True)
while True:
    pass
"""


@contextlib.contextmanager
def referencia_da_cpu():
    """Um processo irmão que só gasta CPU enquanto o bloco roda; o dicionário entregue ganha, no fim, `parcela`: a fração do
    relógio que ele conseguiu na CPU (perto de 1 com a máquina livre, cai com a disputa; None se a medida falhou)."""
    medida = {"parcela": None}
    p = subprocess.Popen([sys.executable, "-I", "-c", _REFERENCIA_DA_CPU], stdout=subprocess.PIPE, text=True,
                         env={"PATH": os.environ.get("PATH", os.defpath)})
    try:
        p.stdout.readline()
        yield medida
    finally:
        p.terminate()
        saida, _ = p.communicate(timeout=30)
        try:
            cpu, parede = (float(x) for x in saida.split())
        except ValueError:
            cpu, parede = 0.0, 0.0
        if parede > 0:
            medida["parcela"] = cpu / parede


def aproveitamento_da_cpu(parede, cpu, sono, parcela):
    """A CPU do hook no relógio fora do sono, dividida pela parcela da referência (1: o hook usou tudo o que a fila deixou)."""
    acordado = parede - sono
    return cpu / (acordado * parcela) if acordado > 0 and parcela > 0 else 0.0


def carga_explica_a_recusa(r, parede, cpu, sono, prazo, parcela):
    """True se a recusa `r` veio do vigia de `prazo` s (mensagem e relógio), `cpu` + `sono` cabem nele com a folga e a disputa
    pela CPU está provada: a `parcela` da referência mostra a fila e o hook a aproveitou (`aproveitamento_da_cpu`)."""
    if r is None or r.returncode != 2 or f"não decidiu em {prazo:g} s" not in r.stderr:
        return False
    if parede is None or parede < prazo or cpu is None or parcela is None:
        return False
    if cpu + sono > prazo - FOLGA_DA_CPU_NO_PRAZO_S or parcela > PARCELA_DE_DISPUTA:
        return False
    return aproveitamento_da_cpu(parede, cpu, sono, parcela) >= APROVEITAMENTO_MINIMO
