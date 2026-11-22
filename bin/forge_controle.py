"""Forge: salva a pasta de controle (quadro, pedidos, briefs, retros, pareceres) num commit local (AE3.1, v0478 E108.1).

Desenho em docs/propostas/v0479-melhorias-anti-erro.md (AE3, D3 e D7): `salvar(pasta)` faz o commit só dos caminhos da lista
positiva `CAMINHOS`, com a mensagem fixa `MENSAGEM`, nunca `add -A`, nunca push, nunca `--no-verify` e sem efeito se nada
mudou. Tudo ou nada: um caminho recusado (link, segredo, arquivo grande, tipo estranho) não deixa commit parcial. Hook ativo na
pasta (`core.hooksPath` ou `.git/hooks` sem `.sample`) sai `nao-verificavel`: o commit rodaria código de fora e o módulo
nunca troca nem esvazia o `core.hooksPath` (R-VERIFY). O git roda sem as `GIT_*` herdadas (um hook exporta `GIT_DIR`, que
venceria o `-C`) e sem `-c` de quem chama. Dois `salvar` ao mesmo tempo: o segundo sai `ocupado`. Só biblioteca padrão.
Saída: (estado, detalhe), com estado em salvo, nada, recusado, nao-verificavel, ocupado ou erro.
"""
import fcntl
import os
import re
import stat
import subprocess
from pathlib import Path

MENSAGEM = "chore(controle): salvar a pasta de controle"
CAMINHOS = ("KANBAN.md", "docs/")  # lista positiva: o quadro e a pasta docs/ (pedidos, briefs, retros, pareceres, kanban)
TETO_DE_BYTES = 1_000_000
SEGREDO = re.compile(r"(^|/)\.env(\.[^/]*)?$|\.(pem|key|p12|pfx)$|(^|/)id_(rsa|ed25519|ecdsa|dsa)$")
SEM_MANUTENCAO = ("-c", "maintenance.auto=false", "-c", "gc.auto=0")  # nada de repack em segundo plano depois do commit


def _git(pasta, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(pasta), "--literal-pathspecs", *args], env=env, capture_output=True,
                           timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as erro:
        return 1, str(erro)
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr).decode("utf-8", "replace")


def _hook_ativo(pasta):
    """Motivo se algum hook rodaria no commit (ou se não dá para saber); None se não há hook."""
    if _git(pasta, "config", "--get", "core.hooksPath")[0] == 0:
        return "core.hooksPath configurado"
    cod, saida = _git(pasta, "rev-parse", "--path-format=absolute", "--git-path", "hooks")
    if cod != 0:
        return "pasta de hooks ilegível"
    hooks = Path(saida.strip())
    if hooks.is_dir():
        for arq in hooks.iterdir():
            if not arq.name.endswith(".sample") and arq.is_file() and os.access(arq, os.X_OK):
                return f"hook ativo {arq.name}"
    return None


def _recusa(pasta, nome):
    """Motivo para não salvar `nome` (relativo à pasta), ou None."""
    if not any(nome == c or (c.endswith("/") and nome.startswith(c)) for c in CAMINHOS):
        return "fora da lista"
    if SEGREDO.search(nome):
        return "nome de segredo"
    atual = Path(pasta)
    for parte in Path(nome).parts:
        atual = atual / parte
        try:
            info = os.lstat(atual)
        except FileNotFoundError:
            return None  # apagado: o commit grava a remoção
        if stat.S_ISLNK(info.st_mode):
            return "link"
    if not stat.S_ISREG(info.st_mode):
        return "não é arquivo comum"
    if info.st_size > TETO_DE_BYTES:
        return f"acima de {TETO_DE_BYTES} bytes"
    return None


def _mudados(pasta):
    """Caminhos alterados, apagados ou novos dentro de `CAMINHOS` (None se o git falhar)."""
    cod, saida = _git(pasta, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames", "--", *CAMINHOS)
    if cod != 0:
        return None
    return sorted({item[3:] for item in saida.split("\0") if len(item) > 3})


def salvar(pasta):
    """Commit local dos caminhos de controle mudados em `pasta` (raiz de um repositório git). Nunca faz push."""
    pasta = Path(pasta).resolve()
    cod, raiz = _git(pasta, "rev-parse", "--show-toplevel")
    if cod != 0 or Path(raiz.strip()).resolve() != pasta:
        return "nao-verificavel", "a pasta não é a raiz de um repositório git"
    cod, trava = _git(pasta, "rev-parse", "--path-format=absolute", "--git-path", "forge-controle.lock")
    if cod != 0:
        return "nao-verificavel", "trava ilegível"
    with open(trava.strip(), "a", encoding="utf-8") as arquivo_da_trava:
        try:
            fcntl.flock(arquivo_da_trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return "ocupado", "outro salvar em andamento"
        return _salvar_travado(pasta)


def _salvar_travado(pasta):
    motivo = _hook_ativo(pasta)
    if motivo:
        return "nao-verificavel", motivo
    nomes = _mudados(pasta)
    if nomes is None:
        return "erro", "git status falhou"
    if not nomes:
        return "nada", "nada mudou"
    for nome in nomes:
        motivo = _recusa(pasta, nome)
        if motivo:
            return "recusado", f"{motivo}: {nome}"
    cod, saida = _git(pasta, "add", "--", *nomes)
    if cod != 0:
        return "erro", saida.strip()
    cod, saida = _git(pasta, *SEM_MANUTENCAO, "commit", "-q", "-m", MENSAGEM, "--only", "--", *nomes)
    if cod != 0:
        return "erro", saida.strip()
    return "salvo", _git(pasta, "rev-parse", "HEAD")[1].strip()
