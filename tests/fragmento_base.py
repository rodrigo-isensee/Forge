"""CHANGELOG-FRAGMENTO-BASE: o fragmento da branch de baixo, numa branch empilhada, não conta como novo."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def de_branch_abaixo(nome, raiz=RAIZ):
    """Fragmento `changelog.d/<s>.md` trazido por `melhoria/<s>` (local ou de origin) ancestral do HEAD e que o tem."""
    def ok(*args):
        return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, env=sem_manutencao()).returncode == 0
    caminho = f"changelog.d/{Path(nome).name}"
    for ref in (f"refs/heads/melhoria/{Path(nome).stem}", f"refs/remotes/origin/melhoria/{Path(nome).stem}"):
        if ok("merge-base", "--is-ancestor", ref, "HEAD") and ok("cat-file", "-e", f"{ref}:{caminho}"):
            return True
    return False
