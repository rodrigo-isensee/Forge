#!/usr/bin/env python3
"""Forge: varredura semanal de dívida técnica; só lê e lista os achados, um por linha, com a sugestão de cartão.

Uso: varredura-divida.py [--raiz PASTA] [--base REF] [--dias N] [--lentos N] [--copias PASTA] [--mb N]

Linha: `<tipo> · <alvo> · <medida> · cartão: <sugestão>`, em ordem estável; no fim, `varredura: <n> achado(s)`.
- branch-mesclada e branch-parada: refs/remotes/origin/* (as já buscadas) contidas na base (padrão: origin/develop,
  senão origin/main) ou sem commit há mais de --dias (padrão 30); main, develop, homolog e HEAD ficam fora.
- teste-lento: os --lentos (padrão 3) módulos (chave sem ponto) de maior tempo em tests/pesos-d4.json.
- mutante-velho: o que `bin/forge-mutante --conferir --todas` acha no HEAD (trecho `de` que não está uma vez só no
  `arquivo`, ou a spec que ele recusa).
- regra-sem-teste: docs/regras/R-*.md cujo ID nenhum tests/**/*.py cita.
- copias (só no Forge): uma linha com o total de --copias (padrão ~/.forge-contrib/wt) acima de --mb (padrão 2048) MB;
  o `du` de milhares de cópias leva cerca de um minuto.
O que o repositório não tem (tests/, docs/regras/, remoto) só não gera achado: vale no Forge e num projeto do forge-init.
Só leitura: não busca no remoto (rode `git fetch` antes), não abre cartão, não grava arquivo e não usa rede (R-CUSTO).
Abrir os cartões sozinho é decisão do dono, passo seguinte. Só biblioteca padrão.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

FIXAS = {"HEAD", "main", "develop", "homolog"}
REMOTAS = "refs/remotes/origin/"
FORGE = Path(__file__).resolve().parent.parent


def git(raiz, *args):
    """Linhas da saída do git (nenhuma se ele falha: fora de repositório, ref que não existe)."""
    return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, timeout=120).stdout.splitlines()


def base_padrao(raiz):
    for ref in ("origin/develop", "origin/main"):
        if git(raiz, "rev-parse", "--verify", "-q", ref + "^{commit}"):
            return ref
    return None


def branches(raiz, base, dias, agora):
    mescladas = set(git(raiz, "for-each-ref", "--merged", base, "--format=%(refname)", REMOTAS)) if base else set()
    for linha in git(raiz, "for-each-ref", "--format=%(refname)\t%(committerdate:unix)", REMOTAS):
        ref, data = linha.split("\t")
        nome = ref[len(REMOTAS):]
        if nome in FIXAS or f"origin/{nome}" == base:
            continue
        idade = int((agora - int(data)) // 86400)
        if ref in mescladas:
            yield "branch-mesclada", nome, f"contida na {base}", f"apagar a branch remota {nome}"
        elif idade > dias:
            yield "branch-parada", nome, f"{idade} dias sem commit", f"retomar ou fechar a branch {nome}"


def lentos(raiz, quantos):
    try:
        pesos = json.loads((raiz / "tests" / "pesos-d4.json").read_text(encoding="utf-8"))
        tempos = sorted((-float(s), m) for m, s in pesos.items() if "." not in m)
    except (OSError, ValueError, TypeError, AttributeError):
        return
    for menos, modulo in tempos[:max(quantos, 0)]:
        yield "teste-lento", modulo, f"{-menos:.1f} s", f"acelerar {modulo} ({-menos:.1f} s por rodada)"


def mutantes(raiz):
    """O trecho de cada mutante pelo próprio forge-mutante (`--conferir --todas`, AR-12, no HEAD): a regra fica num lugar.
    O filho roda com `-B`: sem ele, o forge_apoio_testes grava o cache de bytecode em bin/__pycache__/."""
    if not any((raiz / "tests" / "mutantes").glob("*.json")):
        return
    r = subprocess.run([sys.executable, "-B", str(FORGE / "bin" / "forge-mutante"), "--conferir", "--todas"], cwd=raiz,
                       capture_output=True, text=True, timeout=300)
    for linha in r.stdout.splitlines() if r.returncode == 1 else []:
        spec, _, resto = linha.partition(": ")
        ident, _, medida = resto.partition(" · ")
        yield "mutante-velho", f"{spec} {ident}", medida.split(" · ")[0], f"atualizar o trecho do {ident} em {spec}"
    if r.returncode == 2:
        erro = " ".join(r.stderr.split()[-40:])
        yield "mutante-velho", "tests/mutantes", erro, "corrigir a spec que o forge-mutante recusa"


def regras(raiz):
    ids = sorted(p.stem for p in (raiz / "docs" / "regras").glob("R-*.md"))
    testes = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted((raiz / "tests").rglob("*.py")))
    for ident in ids:
        if not re.search(re.escape(ident) + r"(?![\w-])", testes):
            yield "regra-sem-teste", ident, "nenhum teste em tests/ cita o ID", f"teste que cubra {ident}"


def e_o_forge(raiz):
    """Clone do Forge: o manifesto dele e sem `.forge/versao` (marca de projeto), como no forge-check."""
    if (raiz / ".forge" / "versao").is_file():
        return False
    try:
        return json.loads((raiz / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("name") == "forge"
    except (OSError, ValueError, AttributeError):
        return False


def copias(pasta, mb):
    """Uma linha para a pasta inteira (um `du`; as cópias, uma a uma, são pequenas e muitas)."""
    quantas = sum(1 for p in pasta.glob("*") if p.is_dir())
    saida = subprocess.run(["du", "-sk", str(pasta)], capture_output=True, text=True, timeout=600).stdout.split()
    total = int(saida[0]) // 1024 if saida and saida[0].isdigit() else 0
    if total > mb:
        yield "copias", str(pasta), f"{quantas} cópias, {total} MB", "limpar as cópias sem branch aberta (git worktree remove)"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--raiz", type=Path, default=Path.cwd())
    p.add_argument("--base", help="ref da integração (padrão: origin/develop, senão origin/main)")
    p.add_argument("--dias", type=int, default=30)
    p.add_argument("--lentos", type=int, default=3)
    p.add_argument("--copias", type=Path, default=Path.home() / ".forge-contrib" / "wt")
    p.add_argument("--mb", type=int, default=2048)
    a = p.parse_args(argv)
    if not a.raiz.is_dir():
        p.error(f"--raiz {a.raiz}: não é pasta")
    topo = git(a.raiz, "rev-parse", "--show-toplevel")
    raiz = Path(topo[0]) if topo else a.raiz.resolve()
    base = a.base or base_padrao(raiz)
    achados = [*branches(raiz, base, a.dias, time.time()), *lentos(raiz, a.lentos), *mutantes(raiz), *regras(raiz)]
    if e_o_forge(raiz):
        achados += copias(a.copias, a.mb)
    for tipo, alvo, medida, cartao in achados:
        print(f"{tipo} · {alvo} · {medida} · cartão: {cartao}")
    print(f"varredura: {len(achados)} achado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
