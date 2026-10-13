"""Guarda da suíte: o `.git/config` comum do repositório real não pode mudar durante os testes.

Numa worktree, um `git config` sem `--worktree` grava no `.git/config` comum a todas as cópias (foi assim que um
teste ou um agente deixou `user.name` no clone principal). Cada módulo de teste importa `setUpModule` e
`tearDownModule` daqui: comparam o arquivo antes e depois e falham com a diferença."""
import difflib
import os
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def config_comum(pasta=RAIZ):
    """Caminho do `.git/config` comum (`git rev-parse --git-common-dir`) ou None fora de um repositório."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", str(pasta), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True, env=env, timeout=30)
    return Path(r.stdout.strip()) / "config" if r.returncode == 0 and r.stdout.strip() else None


def ler(caminho):
    return caminho.read_text(encoding="utf-8") if caminho and caminho.is_file() else None


def diferenca(antes, depois):
    """Texto da diferença entre os dois conteúdos, ou "" se iguais."""
    return "".join(difflib.unified_diff((antes or "").splitlines(True), (depois or "").splitlines(True),
                                        "antes", "depois"))


_estado = {}


def setUpModule():  # noqa: N802 - nome que o unittest procura
    caminho = config_comum()
    _estado[__name__] = (caminho, ler(caminho))


def tearDownModule():  # noqa: N802
    caminho, antes = _estado.pop(__name__, (None, None))
    mudou = diferenca(antes, ler(caminho))
    if mudou:
        raise AssertionError(f"os testes mudaram o .git/config comum do repositório real ({caminho}):\n{mudou}")
