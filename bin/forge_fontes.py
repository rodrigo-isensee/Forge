"""Forge: `forge-check fontes` (FILA-31 F6, 0.45.7 E5.1): compara o commit mais recente de cada fonte do registro local
(~/.forge-contrib/fontes/fontes.json) com o último revisado. Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando `fontes` roda; não usa nada dele (o grupo sem dependência dos outros).
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

URL_FONTE = re.compile(r"https://[A-Za-z0-9.-]+(:[0-9]+)?(/[A-Za-z0-9._~%+/-]*)?")


def _imprimivel(texto):
    """Tira caracteres de controle (o código vem de um registro que os agentes podem gravar)."""
    return "".join(c for c in texto if c.isprintable())


def cmd_fontes():
    """Retorna (linhas, código): 0 consultou, 3 alguma fonte não respondeu (sem rede). Sem registro, ([], 0)."""
    registro = Path.home() / ".forge-contrib/fontes/fontes.json"
    if not registro.is_file():
        return [], 0
    try:
        fontes = json.loads(registro.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["fontes: registro local ilegível"], 1
    if not isinstance(fontes, dict):
        return ["fontes: registro local ilegível"], 1
    novas, recusadas, falhou = [], [], False
    # Sem GIT_* herdado e sem configuração de usuário/sistema (insteadOf, credential.helper): só vale a linha abaixo.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_TERMINAL_PROMPT="0", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    protocolos = [a for p in ("ext", "file", "ssh", "git", "http") for a in ("-c", f"protocol.{p}.allow=never")]
    with tempfile.TemporaryDirectory() as vazia:  # fora de qualquer repositório: um .git gravável no cwd não entra
        for codigo, f in sorted(fontes.items()):
            url, revisado = (f.get("url"), f.get("commit_revisado")) if isinstance(f, dict) else (None, None)
            if not isinstance(url, str) or not url or not isinstance(revisado, str) or not revisado:
                continue
            nome = _imprimivel(str(codigo))
            if not URL_FONTE.fullmatch(url):
                recusadas.append(nome)  # só https://; o registro é gravável pelos agentes e esta consulta roda fora do sandbox
                continue
            try:
                r = subprocess.run(["git", "-c", "protocol.allow=never", *protocolos, "-c", "protocol.https.allow=always",
                                    "ls-remote", "--", url, "HEAD"], capture_output=True, text=True, timeout=15, env=env,
                                   cwd=vazia)
            except (subprocess.TimeoutExpired, OSError):
                falhou = True
                continue
            topo = r.stdout.split()[0] if r.returncode == 0 and r.stdout.strip() else ""
            if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", topo):
                falhou = True
            elif not topo.startswith(revisado):
                novas.append(f"{nome} tem versão nova ({_imprimivel(revisado)[:7]} -> {topo[:7]})")
    linhas = []
    if novas:
        linhas.append("fontes: " + "; ".join(novas) + "; abra o estudo comparativo")
    if recusadas:
        linhas.append("fontes: URL recusada (só https:// é aceito) em: " + ", ".join(recusadas))
    if not linhas and not falhou:
        linhas = ["fontes: sem novidade"]
    return linhas, 3 if falhou else 0
