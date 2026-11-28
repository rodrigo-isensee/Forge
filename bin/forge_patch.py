"""Forge: módulo do `forge-patch` (ARQUIVO-TRAVADO-APROVA-COM-COMANDO; C1 é só o `preparar`, o `aplicar` vem no C2)."""
import argparse
import datetime
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import pwd
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.append(str(AQUI.parent / "hooks"))  # a política vigente é a do hook ao lado deste módulo, nunca a da cópia
import conformidade

TETO_DA_FICHA = 256 * 1024
GIT = ("git", "-c", "core.fsmonitor=false", "-c", "core.pager=cat", "-c", "diff.external=")
SUMARIO_ACEITO = re.compile(r" (?:create|delete) mode 100(?:644|755) \S+")  # arquivo comum criado ou apagado; o resto recusa
CAMINHO_TORTO = re.compile(r"[\s*?\[\]\\]")


class Recusa(Exception):
    """Conferência que falhou: o `preparar` sai com 1 e não grava nada."""


def casa():
    return Path(pwd.getpwuid(os.getuid()).pw_dir)  # do banco de usuários, nunca de HOME: o ambiente não muda caminho nenhum


def forge_check():
    """O `bin/forge-check` vizinho como módulo: o mesmo `NUNCA_PATCH_DO_DONO` e o resolvedor de pedido do `anotar`."""
    carregador = importlib.machinery.SourceFileLoader("forge_check_patch", str(AQUI / "forge-check"))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
    carregador.exec_module(modulo)
    return modulo


def vigente():
    """Este módulo roda da cópia vigente: o cache de plugins do Claude Code ou o clone do `jarvis-forge`."""
    return any(AQUI.is_relative_to(casa() / r) for r in (".claude/plugins", ".local/share/forge/vigente"))


def raizes():
    """Onde a cópia pode estar: as pastas de cópias do Forge e a raiz de cada sessão registrada na máquina."""
    lista = [casa() / ".forge-contrib" / "wt", Path("/workspaces/.forge-contrib/.forge/wt")]
    try:
        sessoes = json.loads((casa() / ".forge" / "maquina" / "projetos-ativos.json").read_text(encoding="utf-8"))["sessoes"]
        lista += [Path(s["pasta"]) for s in sessoes.values() if isinstance(s.get("pasta"), str)]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        pass
    return [Path(os.path.realpath(r)) for r in lista]


def git(copia, *args, entrada=None):
    r = subprocess.run([*GIT, "-C", str(copia), *args], input=entrada, capture_output=True, check=False)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def conferir_copia(copia):
    """(ramo, head) da cópia: nas raízes, sem link, raiz do repositório, fora da integração e limpa; senão `Recusa`."""
    real = Path(os.path.realpath(copia))
    if real != Path(os.path.abspath(copia)) or not any(real.is_relative_to(r) for r in raizes()):
        raise Recusa(f"cópia fora das raízes conhecidas ou por link: {copia}")
    rc, topo = git(real, "rev-parse", "--show-toplevel")
    if rc != 0 or Path(os.path.realpath(topo.strip())) != real:
        raise Recusa(f"a cópia não é a raiz de uma cópia de trabalho do git: {copia}")
    rc, ramo = git(real, "symbolic-ref", "--short", "-q", "HEAD")
    if rc != 0 or ramo.strip() in {"main", "master", "develop", "homolog"}:  # R-MAIN, R-FLUXO
        raise Recusa(f"ramo protegido ou HEAD solto: '{ramo.strip()}'")
    rc, sujo = git(real, "status", "--porcelain", "--untracked-files=no")
    if rc != 0 or sujo.strip():
        raise Recusa("árvore ou índice com mudança: commite ou descarte antes")
    return ramo.strip(), git(real, "rev-parse", "HEAD")[1].strip()


def conferir_patch(copia, ramo, patch, arquivos, fc):
    """O patch muda só `arquivos`, travados, fora dos que nunca isentam, em arquivo comum e limpo no head; senão `Recusa`."""
    rc, numstat = git(copia, "apply", "--numstat", "-z", "-", entrada=patch)
    registros = [r for r in numstat.split("\0") if r]
    if rc != 0 or not registros or any(not re.fullmatch(r"\d+\t\d+\t[^\t]+", r) for r in registros):
        raise Recusa("patch ilegível ou com binário")
    if sorted(r.split("\t", 2)[2] for r in registros) != sorted(arquivos):
        raise Recusa("os arquivos do patch não são exatamente os de --arquivos")
    rc, sumario = git(copia, "apply", "--summary", "-", entrada=patch)
    if rc != 0 or any(not SUMARIO_ACEITO.fullmatch(linha) for linha in sumario.splitlines()):
        raise Recusa("patch com renomeação, cópia, link, submódulo ou mudança de modo")
    for nome in arquivos:
        if (nome.startswith(fc.NUNCA_PATCH_DO_DONO + ("docs/autorizacoes/", ".forge/autorizacoes/")) or fc.com_controle(nome)
                or CAMINHO_TORTO.search(nome) or any(p in ("", ".", "..") for p in nome.split("/"))):
            raise Recusa(f"caminho que nunca vai por patch do dono: {fc.sem_controle(nome)}")
        barrada = conformidade.escrita_barrada("forge:tech-lead", nome, str(copia), ramo)
        if barrada is None or barrada[3:] in ((conformidade.NAO_CONFERIDA,), (conformidade.NAO_VERIFICAVEL,)):
            raise Recusa(f"arquivo livre ou não conferido pela política: {nome} (arquivo livre segue o caminho normal)")
    if git(copia, "apply", "--check", "-", entrada=patch)[0] != 0:
        raise Recusa("o patch não aplica limpo no head")


def preparar(ident, copia, pedido, motivo, arquivos):
    """Confere tudo e grava a ficha (cabeçalho, linha vazia, patch); devolve a linha do comando do dono."""
    if not re.fullmatch(r"[a-z0-9-]{1,40}", ident):
        raise Recusa("id fora de [a-z0-9-]{1,40}")
    if not vigente():
        raise Recusa(f"este forge-patch não é o da cópia vigente ({AQUI}): o comando do dono rodaria código da cópia")
    fc = forge_check()
    if not motivo.strip() or fc.com_controle(motivo) or fc.pedido_para_anotar(copia, pedido) is None:
        raise Recusa("motivo vazio ou com controle, ou pedido sem docs/pedidos/<id>.md")
    pasta = casa() / ".forge-contrib" / "patches"
    origem = pasta / f"{ident}.patch"
    if not origem.is_file() or origem.is_symlink() or origem.stat().st_size > TETO_DA_FICHA:
        raise Recusa(f"patch ausente, link ou acima de {TETO_DA_FICHA} bytes: {origem}")
    patch = origem.read_bytes()
    ramo, head = conferir_copia(copia)
    conferir_patch(Path(os.path.realpath(copia)), ramo, patch, arquivos, fc)
    agora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    campos = {"Id": ident, "Pedido": pedido, "Copia": os.path.realpath(copia), "Ramo": ramo, "Head": head,
              "Arquivos": " ".join(arquivos), "Motivo": motivo.strip(), "Preparado-em": agora}
    ficha = "".join(f"{k}: {v}\n" for k, v in campos.items()).encode("utf-8") + b"\n" + patch
    if len(ficha) > TETO_DA_FICHA:
        raise Recusa(f"ficha acima de {TETO_DA_FICHA} bytes")
    with open(destino := pasta / f"{ident}.ficha", "xb") as saida:  # ficha que já existe não se sobrescreve (FileExistsError)
        saida.write(ficha)
    return f"python3 -I {AQUI / 'forge-patch'} aplicar {destino} {hashlib.sha256(ficha).hexdigest()}"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="forge-patch", description=__doc__.splitlines()[0])
    p = parser.add_subparsers(dest="acao", required=True).add_parser("preparar", help="confere o patch e grava a ficha")
    p.add_argument("id")
    for opcao, quantos in (("--copia", None), ("--pedido", None), ("--motivo", None), ("--arquivos", "+")):
        p.add_argument(opcao, required=True, nargs=quantos)
    args = parser.parse_args(argv)
    try:
        print(preparar(args.id, args.copia, args.pedido, args.motivo, args.arquivos))
    except (Recusa, FileExistsError) as erro:
        print(f"forge-patch: recusado: {erro}", file=sys.stderr)
        return 1
    return 0
