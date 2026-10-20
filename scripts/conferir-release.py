#!/usr/bin/env python3
"""Release exige versão nova e changelog fechado (mesma checagem para o PR para a main e para a homolog).

Uso: scripts/conferir-release.py --base <sha-da-base> [--so-se-versao-mudou]
Roda na raiz do checkout do PR. Com --so-se-versao-mudou (PR develop -> homolog), a checagem só vale quando a
versão do PR difere da versão da base: promoção sem versão nova (não é release) sai 0 sem conferir nada.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def versao_da_base(base):
    r = subprocess.run(["git", "show", f"{base}:.claude-plugin/plugin.json"], capture_output=True, text=True, cwd=RAIZ)
    try:
        return json.loads(r.stdout)["version"] if r.returncode == 0 else "0.0.0"
    except (ValueError, KeyError):
        return "0.0.0"


def conferir(base, so_se_versao_mudou):
    atual = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    anterior = versao_da_base(base)
    print(f"versão base: {anterior} | versão da release: {atual}")
    if so_se_versao_mudou and atual == anterior:
        print("promoção sem versão nova: não é release, checagem de release não se aplica")
        return
    b, a = (tuple(map(int, v.split("."))) for v in (anterior, atual))
    if a <= b:
        sys.exit(f"Suba a versão em .claude-plugin/plugin.json (base {anterior}, release {atual}).")
    texto = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"^## \[{re.escape(atual)}\]", texto, re.M):
        sys.exit(f"CHANGELOG.md sem a entrada '## [{atual}]'.")
    m = re.search(r"^## \[Não publicado\][^\n]*\n(.*?)(?=^## |\Z)", texto, re.M | re.S)
    if m and any(linha.strip() for linha in m.group(1).splitlines()):
        sys.exit(f"Converta '## [Não publicado]' em '## [{atual}] - data': a seção deve estar vazia na release.")
    r = subprocess.run([sys.executable, str(RAIZ / "bin" / "forge-changelog"), "conferir-release"], cwd=RAIZ)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(prog="conferir-release")
    ap.add_argument("--base", required=True)
    ap.add_argument("--so-se-versao-mudou", action="store_true")
    args = ap.parse_args()
    conferir(args.base, args.so_se_versao_mudou)


if __name__ == "__main__":
    main()
