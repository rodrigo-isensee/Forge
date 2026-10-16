"""Guarda da suíte: o `.git/config` comum do repositório real não pode mudar durante os testes.

Numa worktree, um `git config` sem `--worktree` grava no `.git/config` comum a todas as cópias (foi assim que um
teste ou um agente deixou `user.name` no clone principal). Cada módulo de teste importa `setUpModule` e
`tearDownModule` daqui: comparam o arquivo antes e depois e falham com a diferença."""
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def config_comum(pasta=RAIZ):
    """Caminho do `.git/config` comum (`git rev-parse --git-common-dir`) ou None fora de um repositório."""
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})  # pasta pode ser temporária
    r = subprocess.run(["git", "-C", str(pasta), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True, env=env, timeout=30)
    return Path(r.stdout.strip()) / "config" if r.returncode == 0 and r.stdout.strip() else None


def ler(caminho):
    return caminho.read_text(encoding="utf-8") if caminho and caminho.is_file() else None


_SECAO = re.compile(r"^\s*\[")
_SECAO_BRANCH = re.compile(r'^\s*\[branch[\s."]', re.IGNORECASE)


def sem_branch(texto):
    """O config sem as seções `branch.*`: o git grava o rastreamento de branch (remote, merge) por conta própria quando
    outros agentes criam ou enviam branches em paralelo; isso não é identidade nem configuração alterada."""
    saida, dentro = [], False
    for linha in (texto or "").splitlines(True):
        if _SECAO.match(linha):
            dentro = bool(_SECAO_BRANCH.match(linha))
        if not dentro:
            saida.append(linha)
    return "".join(saida)


def diferenca(antes, depois):
    """Texto da diferença entre os dois conteúdos (ignorando `branch.*`), ou "" se iguais."""
    return "".join(difflib.unified_diff(sem_branch(antes).splitlines(True), sem_branch(depois).splitlines(True),
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
