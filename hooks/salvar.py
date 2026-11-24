#!/usr/bin/env python3
"""Forge: salvar (D6-SESSAO-NAO-PERDE, parte a; v0481 E11.2) - ao parar, o agente grava e envia o trabalho em andamento.

SubagentStop: o prompt do agente (primeiro registro `user` do `agent_transcript_path`) cita um só brief de escrita
(`de_escrita` e `ler_brief` do `agentes`). Dele saem a `Branch:`, o escopo (`- arquivos:`: caminho exato ou pasta com `/`) e
a cópia citada (em `~/.forge-contrib/wt/` no Forge, `<projeto>/.forge/wt/` no projeto), que precisa estar nessa branch. A
mudança fora de commit dentro do escopo vira um commit WIP só dela (`--only`), enviado por `git push origin <branch>`, sem
`--force` e nunca em branch de integração. Não age com conflito ou operação do git em andamento, nem com cópia ou brief
ambíguo. O git roda fora do sandbox: sem os hooks do git da cópia (o agente escreve o código deles) nem `core.fsmonitor`,
sem as GIT_* herdadas e sem pedir senha; a guarda da branch é a deste arquivo. Resultado em `.forge/run/salvar.log`; nunca
bloqueia nem escreve no stdout; erro interno: silêncio e uma linha no erros.log (o `executar`). Só biblioteca padrão."""
import json
import os
import re
import subprocess
import time

from _comum import INTEGRACAO, contrib, e_clone_do_forge, executar, expandir_home, forge_check
from agentes import caminhos_de_brief, de_escrita, ler_brief

LEITURA_DO_PROMPT = 1024 * 1024  # bytes do início do transcrito do agente
PRAZO_GIT_S = 10
PRAZO_DO_ENVIO_S = 40  # abaixo dos 60 s do hook no hooks.json
GIT_SEGURO = ("-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "--literal-pathspecs")
BRANCH_VALIDA = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,200}")
ESCOPO = re.compile(r"^- arquivos:[ \t]*(.+)$", re.M)
COPIA_CITADA = re.compile(r"(?:~|/)[^\s`'\"(),;]*/wt/[A-Za-z0-9._-]+")
EM_ANDAMENTO = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply")


def git_da_copia(copia, *args, prazo=PRAZO_GIT_S):
    """(código, stdout em bytes) do git na cópia, com GIT_SEGURO, sem as GIT_* herdadas e sem pedir senha."""
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, "GIT_TERMINAL_PROMPT": "0"}
    r = subprocess.run(["git", *GIT_SEGURO, "-C", str(copia), *args], capture_output=True, env=env, timeout=prazo,
                       stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout


def prompt_do_agente(transcrito):
    """O texto do primeiro registro `user` do transcrito do agente (o prompt do disparo), ou ""."""
    try:
        with open(transcrito, "rb") as f:
            linhas = f.read(LEITURA_DO_PROMPT).decode("utf-8", "replace").splitlines()
    except (OSError, TypeError, ValueError):
        return ""
    for linha in linhas:
        try:
            registro = json.loads(linha)
        except (ValueError, RecursionError):
            continue
        if isinstance(registro, dict) and registro.get("type") == "user":
            conteudo = registro.get("message", {}).get("content") if isinstance(registro.get("message"), dict) else None
            if isinstance(conteudo, list):
                conteudo = "\n".join(b.get("text", "") for b in conteudo if isinstance(b, dict) and b.get("type") == "text")
            return conteudo if isinstance(conteudo, str) else ""
    return ""


def brief_do_agente(hook):
    """O texto do único brief de escrita citado no prompt do agente, ou None (nenhum, mais de um, ilegível)."""
    fc, achados = forge_check(), []
    for caminho in dict.fromkeys(caminhos_de_brief(prompt_do_agente(hook.campo("agent_transcript_path")))):
        try:
            dados = ler_brief(hook, expandir_home(caminho))
        except OSError:  # ausente ou ilegível: o brief fica de fora, como no `branches_dos_briefs` do `agentes`
            continue
        if dados is not None and de_escrita(fc, fc.cabecalho_do_brief(texto := dados.decode("utf-8", "replace"))):
            achados.append(texto)
    return achados[0] if len(achados) == 1 else None


def no_escopo(caminho, escopo):
    return any(caminho.startswith(item) if item.endswith("/") else caminho == item for item in escopo)


def plano(hook, raiz, texto):
    """(cópia, branch, escopo) que o brief descreve, ou None se falta ou sobra alguma coisa."""
    fc = forge_check()
    branch = re.search(fc.CABECALHO_DE_BRIEF_CAMPOS["Branch"], fc.cabecalho_do_brief(texto))
    escopo = ESCOPO.search(texto)
    if not branch or not escopo or branch.group(1) in INTEGRACAO or not BRANCH_VALIDA.fullmatch(branch.group(1)):
        return None
    itens = [i.strip().strip("`") for i in escopo.group(1).split(",")]
    base = os.path.realpath(contrib() / "wt" if e_clone_do_forge(raiz) else hook.copia_principal() / ".forge" / "wt")
    copias = {os.path.realpath(expandir_home(c)) for c in COPIA_CITADA.findall(texto)}
    copias = [c for c in copias if os.path.dirname(c) == base and os.path.isdir(c)]
    if len(copias) != 1:
        return None
    rc, atual = git_da_copia(copias[0], "symbolic-ref", "-q", "--short", "HEAD")
    return (copias[0], branch.group(1), itens) if rc == 0 and atual.decode().strip() == branch.group(1) else None


def arquivos_a_salvar(copia, escopo):
    """Os caminhos mudados fora de commit dentro do escopo; [] com conflito ou operação do git em andamento."""
    rc, pasta = git_da_copia(copia, "rev-parse", "--absolute-git-dir")
    if rc or any(os.path.lexists(os.path.join(pasta.decode().strip(), n)) for n in EM_ANDAMENTO):
        return []
    rc, saida = git_da_copia(copia, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
    if rc:
        raise RuntimeError(f"git status saiu com {rc}")
    entradas = [(e[:2].decode(), e[3:].decode("utf-8", "surrogateescape")) for e in saida.split(b"\0") if e]
    if any("U" in xy or xy in ("AA", "DD") for xy, _ in entradas):
        return []
    return [caminho for _, caminho in entradas if no_escopo(caminho, escopo)]


def salvar(copia, branch, arquivos):
    """Commit WIP só de `arquivos` e envio da branch; devolve a linha do salvar.log."""
    for args in (("add", "-A", "--", *arquivos),
                 ("commit", "-q", "--only", "-m", "chore(wip): trabalho em andamento salvo ao parar o agente", "--", *arquivos)):
        rc, _ = git_da_copia(copia, *args)
        if rc:
            raise RuntimeError(f"git {args[0]} saiu com {rc}")
    sha = git_da_copia(copia, "rev-parse", "--short", "HEAD")[1].decode().strip()
    rc, _ = git_da_copia(copia, "push", "origin", f"refs/heads/{branch}:refs/heads/{branch}", prazo=PRAZO_DO_ENVIO_S)
    return f"{branch} {sha} {len(arquivos)} arquivo(s) " + ("enviado" if rc == 0 else f"envio falhou (rc={rc})")


def principal(hook):
    if hook.campo("hook_event_name") != "SubagentStop" or (raiz := hook.projeto(hook.cwd(), clone_do_forge=True)) is None:
        return
    texto = brief_do_agente(hook)
    alvo = plano(hook, raiz, texto) if texto else None
    arquivos = arquivos_a_salvar(alvo[0], alvo[2]) if alvo else []
    if arquivos:
        linha = salvar(alvo[0], alvo[1], arquivos)
        with open(hook.run() / "salvar.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {linha}\n")


if __name__ == "__main__":
    executar("salvar", principal)
