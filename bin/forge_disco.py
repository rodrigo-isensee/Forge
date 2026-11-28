"""Forge: o uso do disco e o limiar único da cópia de trabalho (MP6, v0474 E3.251).

Acima de LIMIAR_DISCO por cento de uso, o `forge-copia` recusa cópia nova e manda limpar; o `forge-placar` mostra a medida.
O número mora só aqui. Só biblioteca padrão.
"""
import os
import shutil

LIMIAR_DISCO = 90  # por cento de uso; acima dele, cópia nova é recusada


def pasta_existente(caminho):
    """O caminho ou o primeiro pai dele que existe (o destino da cópia ainda não existe)."""
    p = os.path.abspath(caminho)
    while not os.path.exists(p) and os.path.dirname(p) != p:
        p = os.path.dirname(p)
    return p


def uso_do_disco(caminho):
    """Porcentagem inteira de uso do disco que guarda o caminho, como o `df` (usado sobre usado mais livre), arredondada para cima."""
    u = shutil.disk_usage(pasta_existente(caminho))
    ocupavel = u.used + u.free
    return 100 if ocupavel <= 0 else -(-u.used * 100 // ocupavel)
