"""`gh` falso para os testes que rodam `forge-check brief gerar --branch` (P5): o `gerar` consulta o PR pelo `gh`, e teste não usa rede
(R-CUSTO, testes determinísticos). `com_gh_falso` põe na frente do PATH um `gh` que sai com 1 e a resposta de `gh_falso` (padrão:
sem rede); o `forge-check` trata a falha como `não verificável`."""
import atexit
import os
import shutil
import tempfile
from pathlib import Path

_PASTAS = []


def pasta_com_gh(script="echo 'gh falso: sem rede no teste' >&2\nexit 1\n"):
    """Pasta temporária com um `gh` executável que roda `script` (sh); apagada no fim do processo."""
    pasta = Path(tempfile.mkdtemp(prefix="forge-gh-falso-"))
    _PASTAS.append(pasta)
    gh = pasta / "gh"
    gh.write_text("#!/bin/sh\n" + script, encoding="utf-8")
    gh.chmod(0o755)
    return pasta


def com_gh_falso(env=None, script=None):
    """Cópia de `env` (padrão: o ambiente atual) com o `gh` falso na frente do PATH."""
    env = dict(os.environ if env is None else env)
    pasta = pasta_com_gh(script) if script is not None else pasta_com_gh()
    env["PATH"] = str(pasta) + os.pathsep + env.get("PATH", "")
    return env


atexit.register(lambda: [shutil.rmtree(p, ignore_errors=True) for p in _PASTAS])
