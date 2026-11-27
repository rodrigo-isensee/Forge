#!/usr/bin/env python3
"""Forge: gerador único dos derivados versionados, rodado pelo autor antes do envio (proposta 1 da auditoria dos testes).

Uso: gerar-derivados.py              roda cada gerador que existe no repositório e grava; diz o que mudou
     gerar-derivados.py --conferir   não grava; rc 1 se algum derivado ficaria diferente

Os geradores são os que já existem (lista fechada `GERADORES`), cada um chamado pelo caminho literal com `python3 -I`, a
partir da raiz do repositório deste script e sem `GIT_*` no ambiente (um hook exporta `GIT_DIR`). Gerador ausente é
avisado e pulado. Os testes continuam iguais: o script só tira o esquecimento. Saída 0 = todos rodaram (e, no
`--conferir`, tudo em dia); 1 = gerador vermelho ou, no `--conferir`, derivado desatualizado; 2 = uso errado.
Ficam fora, e o script diz por quê: os pesos da suíte e o mapa de testes (`FORA`). Só biblioteca padrão.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GERADORES = (  # (nome, gerador, derivado)
    ("índice do Forge", "scripts/indice-forge.py", "docs/indice-forge.md"),
    ("índice das fixtures (corpus dos hooks)", "scripts/indice-fixtures.py", "docs/hooks-fixtures.md"),
)
FORA = (
    ("pesos da suíte (tests/pesos-d4.json)", "só a marca de versão os regera (E19.1), pela API do GitHub"),
    ("mapa de testes", "é código, sem gerador; a conferência de registros do envio o confere"),
)


def ambiente():
    """O ambiente do gerador, sem `GIT_*`: o git dele lê o repositório da raiz, não o de um hook que chamou o script."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def conteudo(caminho):
    return caminho.read_bytes() if caminho.is_file() else None


def rodar(gerador, conferir):
    argv = [sys.executable, "-I", gerador] + (["--conferir"] if conferir else [])
    r = subprocess.run(argv, cwd=RAIZ, env=ambiente(), stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main(argv):
    if argv not in ([], ["--conferir"]):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    conferir, codigo = argv == ["--conferir"], 0
    for nome, gerador, derivado in GERADORES:
        if not (RAIZ / gerador).is_file():
            print(f"gerar-derivados: {nome}: ausente ({gerador}), pulado")
            continue
        antes = conteudo(RAIZ / derivado)
        rc, saida = rodar(gerador, conferir)
        if conferir and rc == 1:
            estado, codigo = "desatualizado; rode scripts/gerar-derivados.py", 1
        elif rc != 0:
            estado, codigo = f"gerador vermelho (rc={rc}): {saida[-300:]}", 1
        elif conferir:
            estado = "em dia"
        else:
            estado = "mudou" if conteudo(RAIZ / derivado) != antes else "sem mudança"
        print(f"gerar-derivados: {nome}: {derivado}: {estado}")
    for nome, motivo in FORA:
        print(f"gerar-derivados: fora: {nome}: {motivo}")
    print(f"gerar-derivados: rc={codigo}" + ("" if conferir else "; confira com `git diff` e commite os derivados"))
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
