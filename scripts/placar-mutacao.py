#!/usr/bin/env python3
"""Forge: placar de mutação da release (M-5). Medida, não portão. Só biblioteca padrão.

Uso: scripts/placar-mutacao.py --desde TAG [--versao VERSÃO]
  Amostra: a spec fixa `tests/mutantes/placar.json` mais as specs adicionadas em `tests/mutantes/` desde TAG
  (`--diff-filter=A`: a spec só editada não entra), até 8, em ordem de nome; as demais saem `fora da amostra: <spec>`.
  Nome fora de `tests/mutantes/<nome>.json` (sem `-` no início) ou link simbólico sai `recusada: <spec>`.
  Roda `bin/forge-mutante -- <spec>` uma vez por spec (ele recusa specs de pedidos diferentes juntas) e conta as linhas
  de veredito por padrão fechado, sem ecoar a saída dele. Imprime uma linha por spec e o total:
  `placar: <versão> mortos=<n> sobreviveu=<n> equivalente=<n> invalido=<n> sem-veredito=<n> specs=<n>`.
Saída: 0 sempre que mediu (sobrevivente e spec envelhecida são dado do placar); 2 se TAG não é commit.
Roda dentro da trava da suíte (`R-TETO`, pesado): cada spec é uma rodada do `forge-mutante`.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

AMOSTRA = "tests/mutantes/placar.json"
TETO_DE_SPECS = 8
# R-4: `<id> · <classe> · ...` ou `equivalente: <id> · ...`; o resto da saída do forge-mutante não conta.
LINHA = re.compile(r"^\S+ · (morreu|sobreviveu|equivalente|inválido|sem veredito|controle vermelho) · "
                   r"|^(equivalente): \S+ · ", re.MULTILINE)
CLASSES = {"morreu": "mortos", "sobreviveu": "sobreviveu", "equivalente": "equivalente", "inválido": "invalido",
           "sem veredito": "sem-veredito", "controle vermelho": "sem-veredito"}


def git(raiz, *args):
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True)


def specs_novas(raiz, base):
    """Specs adicionadas desde `base`, sem a amostra fixa (R-2), em ordem de nome: (aceitas, recusadas)."""
    saida = git(raiz, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=A", f"{base}..HEAD", "--",
                "tests/mutantes/", f":!{AMOSTRA}").stdout
    aceitas, recusadas = [], []
    for nome in sorted(saida.split("\0")[:-1]):
        (aceitas if re.fullmatch(r"tests/mutantes/[A-Za-z0-9][A-Za-z0-9._-]*\.json", nome)
         and not os.path.islink(raiz / nome) else recusadas).append(nome)
    return aceitas, recusadas


def contar(saida):
    conta = dict.fromkeys(CLASSES.values(), 0)
    for achado in LINHA.findall(saida):
        conta[CLASSES["".join(achado)]] += 1
    return conta


def main(argv=None):
    p = argparse.ArgumentParser(prog="placar-mutacao.py", description="Placar de mutação da release (não é portão).")
    p.add_argument("--desde", required=True, help="tag da release anterior")
    p.add_argument("--versao", default="próxima", help="versão que o placar mede")
    a = p.parse_args(argv)
    raiz = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").stdout.strip())
    base = git(raiz, "rev-parse", "--verify", "--end-of-options", f"{a.desde}^{{commit}}")
    if a.desde.startswith("-") or base.returncode:  # R-3
        p.error(f"--desde não é commit: {a.desde!r}")
    novas, recusadas = specs_novas(raiz, base.stdout.strip())
    for linha in [f"recusada: {n!r}" for n in recusadas] + [f"fora da amostra: {n}" for n in novas[TETO_DE_SPECS:]]:
        print(linha)
    amostra = [AMOSTRA, *novas[:TETO_DE_SPECS]]
    total = dict.fromkeys(CLASSES.values(), 0)
    for spec in amostra:  # uma rodada por spec, R-1: `--` antes do caminho
        feito = subprocess.run([sys.executable, str(raiz / "bin" / "forge-mutante"), "--", spec], cwd=raiz,
                               capture_output=True, text=True)
        conta = contar(feito.stdout)
        total = {k: total[k] + conta[k] for k in total}
        print(f"spec: {spec} rc={feito.returncode} " + " ".join(f"{k}={v}" for k, v in conta.items()))
    print(f"placar: {a.versao} " + " ".join(f"{k}={v}" for k, v in total.items()) + f" specs={len(amostra)}")
    return 0  # placar, não portão


if __name__ == "__main__":
    sys.exit(main())
