"""Forge: execução capturada como prova (siegard S5, 0.44.2). Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando roda:
- `rodar <slug> -- <cmd> [args] [; <cmd2> args]`: roda cada passo SEM shell (o `;` sozinho separa passos), na raiz, e grava
  `.forge/run/<slug>/run.json` (rc, tempo por passo, argv, head do git) e o log completo de cada passo (`passo-N.log`, stdout e
  stderr juntos). Para no primeiro passo que falha. Slug já usado recusa (rc 2): a prova não se sobrescreve.
- `ler(pasta, argv, head)`: o PQ `cmd` que é `forge-check rodar <slug> -- ...` não roda de novo na conferência; o forge-check lê o
  run.json da pasta e confere argv, head e a espera contra o rc e o log gravados.
"""
import datetime
import json
import os
import re
import shlex
import subprocess
import time
from pathlib import Path

PASTA = Path(".forge") / "run"
SLUG = re.compile(r"[a-z0-9][a-z0-9._-]{0,60}")
SEPARADOR = ";"
TEMPO_PADRAO_S = 1800


def passos_de(argv):
    """Os passos do argv (separados por `;` sozinho); passo vazio é erro (lista vazia)."""
    passos, atual = [], []
    for a in argv:
        if a == SEPARADOR:
            passos.append(atual)
            atual = []
        else:
            atual.append(a)
    passos.append(atual)
    return passos if all(passos) else []


def _head(raiz):
    r = subprocess.run(["git", "-C", str(raiz), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def rodar(raiz, slug, argv, tempo=TEMPO_PADRAO_S):
    """rc do comando gravado (0 se todos os passos passaram); 2 se a entrada é inválida ou o slug já existe."""
    argv = argv[1:] if argv[:1] == ["--"] else argv
    passos = passos_de(argv)
    if not SLUG.fullmatch(slug or "") or not passos:
        print("rodar: uso `forge-check rodar <slug> -- <cmd> [args] [; <cmd2> ...]` (slug: [a-z0-9._-], até 61)")
        return 2
    base = raiz / PASTA
    if base.is_symlink() or base.parent.is_symlink():
        print(f"rodar: {PASTA} é link simbólico; nada rodado")
        return 2
    base.mkdir(parents=True, exist_ok=True)
    pasta = base / slug
    try:
        pasta.mkdir()
    except FileExistsError:
        print(f"rodar: slug {slug!r} já usado ({PASTA / slug}); escolha outro, a prova gravada não se sobrescreve")
        return 2
    inicio = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    registros, rc = [], 0
    for n, passo in enumerate(passos, 1):
        log = pasta / f"passo-{n}.log"
        t0 = time.monotonic()
        with open(log, "wb") as f:
            try:
                r = subprocess.run(passo, cwd=raiz, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=tempo)
                rc_passo = r.returncode
            except subprocess.TimeoutExpired:
                rc_passo = 124
            except OSError as e:
                f.write(f"rodar: não rodou: {e.strerror or e}\n".encode())
                rc_passo = 127
        registros.append({"passo": n, "argv": passo, "rc": rc_passo, "segundos": round(time.monotonic() - t0, 3), "log": log.name})
        if rc_passo != 0:
            rc = rc_passo
            break
    dados = {"slug": slug, "inicio": inicio, "fim": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
             "head": _head(raiz), "argv": argv, "rc": rc, "passos": registros}
    (pasta / "run.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in registros:
        print(f"rodar: passo {r['passo']} rc={r['rc']} {r['segundos']}s log={PASTA / slug / r['log']}")
    print(f"rodar: {PASTA / slug / 'run.json'} rc={rc}")
    return rc


def citado(argv):
    """(slug, argv do run) se o PQ `cmd` é `forge-check rodar <slug> -- ...`; senão None."""
    if len(argv) >= 3 and Path(argv[0]).name == "forge-check" and argv[1] == "rodar":
        resto = argv[3:]
        return argv[2], (resto[1:] if resto[:1] == ["--"] else resto)
    return None


def ler(pasta, slug, argv, head):
    """(rc, saída, motivo) do run gravado em `pasta`; motivo != None quando ele não vale como prova."""
    if not SLUG.fullmatch(slug or ""):
        return None, "", "slug inválido"
    arq = Path(pasta) / PASTA / slug / "run.json"
    if not arq.is_file() or arq.is_symlink():
        return None, "", f"{PASTA / slug / 'run.json'} ausente (rode o PQ antes de pedir a conferência)"
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
    except ValueError:
        return None, "", "run.json ilegível"
    if dados.get("argv") != argv:
        return None, "", "run.json é de outro comando"
    if head and dados.get("head") != head:
        return None, "", "run.json é de outro commit (rode de novo com outro slug)"
    saida = []
    for p in dados.get("passos", []):
        log = arq.parent / str(p.get("log", ""))
        if log.parent != arq.parent or not log.is_file() or log.is_symlink():
            return None, "", "log do passo ausente"
        saida.append(log.read_text(encoding="utf-8", errors="replace"))
    return dados.get("rc"), "".join(saida), None


CRASES = re.compile(r"`([^`]+)`")


def prova_do_pq(resto, pasta, head, script, espera_do_script):
    """(linha, reprova) do PQ `cmd` cujo comando é `forge-check rodar <slug> -- ...`; None se o PQ não cita um run."""
    achado = CRASES.search(resto)
    try:
        run = citado(shlex.split(achado.group(1))) if achado is not None else None
    except ValueError:
        run = None
    if run is None:
        return None
    espera = espera_do_script(script, resto[achado.end():].partition("espera:")[2].strip())
    rc, saida, motivo = ler(pasta, run[0], run[1], head)
    divergiu = motivo or (espera is None and "espera fora do vocabulário") or script.avaliar(espera, saida, rc)
    return (f"run {run[0]}: diverge ({divergiu})", True) if divergiu else (f"run {run[0]}: ok", False)


def executar(a, raiz):
    return rodar(raiz, a.slug, list(a.comando), a.tempo)
