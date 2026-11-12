#!/usr/bin/env python3
"""Forge: confere, antes do review, se cada commit da branch se reverte sozinho (M10). Só biblioteca padrão.

Uso: conferir-reversao.py BASE BRANCH
  Para cada commit de BASE..BRANCH (sem os de mescla), numa cópia do repositório em $TMPDIR:
  `git revert --no-commit` sobre a ponta da branch e a suíte afetada escolhida pelo `bin/forge-testes`.
  Antes, pede o plano da ponta com `--listar` (o contrato do `.githooks/pre-push`): só o dirigido e o "nada alterado"
  rodam; o plano que cai na suíte inteira não classifica nada, porque a suíte inteira só roda na trava (R-TETO) e no CI.
  Depois roda a suíte afetada na ponta: se já falha, avisa e não classifica (a falha não seria do commit).
  Imprime uma linha por commit: `<sha7> reverte`, `<sha7> nao-reverte: <motivo>` ou `<sha7> sem-veredito: <motivo>`
  (o `forge-testes` saiu 2: não conseguiu dar veredito, e isso não é falha do commit; ou o plano do revert, pedido
  com o mesmo `--listar` da ponta, cai na suíte inteira: nada roda para esse commit).

É aviso, não portão: sai com 0 sempre que conseguiu conferir (inclusive com `nao-reverte`) e com 2 em erro de
uso ou repositório inválido. Só lê o repositório real: nada é escrito nele nem no `.git` dele.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

FORGE_TESTES = Path(__file__).resolve().parent.parent / "bin" / "forge-testes"
PLANO_DIRIGIDO = "forge-testes: dirigido ("
NADA_ALTERADO = "forge-testes: nada alterado; nada a rodar."
IDENTIDADE = {"GIT_AUTHOR_NAME": "conferir-reversao", "GIT_AUTHOR_EMAIL": "c@c",
              "GIT_COMMITTER_NAME": "conferir-reversao", "GIT_COMMITTER_EMAIL": "c@c"}


# Variáveis de local do git (um hook de commit as define): herdadas, mandariam o git da cópia para o repositório real.
LOCAIS_GIT = ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_OBJECT_DIRECTORY",
              "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR")


def ambiente():
    return {**{k: v for k, v in os.environ.items() if k not in LOCAIS_GIT}, **IDENTIDADE}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=ambiente())


def forge_testes(copia, base, *opcoes):
    return subprocess.run([sys.executable, str(FORGE_TESTES), "--base", base, *opcoes], cwd=copia,
                          capture_output=True, text=True, env=ambiente())


def ponta_dirigida(copia, base):
    """O plano da ponta pela primeira linha do `--listar`; qualquer outra saída ou erro conta como suíte inteira."""
    r = forge_testes(copia, base, "--listar")
    primeira = (r.stdout.splitlines() or [""])[0]
    return r.returncode == 0 and (primeira.startswith(PLANO_DIRIGIDO) or primeira == NADA_ALTERADO)


def suite_afetada(copia, base):
    """O código de saída da suíte afetada: 0 passa, 2 é sem veredito do `forge-testes`, o resto é falha."""
    return forge_testes(copia, base).returncode


def resolver(repo, ref):
    r = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return r.stdout.strip() if r.returncode == 0 else None


def preparar_copia(repo, destino):
    """Clone local sem hardlinks (os objetos novos nascem só na cópia), com todas as refs do original."""
    r = git(repo, "clone", "--quiet", "--no-hardlinks", "--no-checkout", str(repo), str(destino))
    if r.returncode:
        return False
    return git(destino, "fetch", "--quiet", str(repo), "+refs/*:refs/orig/*").returncode == 0


def conferir_commit(copia, base, commit):
    git(copia, "reset", "--hard", "--quiet")
    git(copia, "clean", "-fdxq")
    r = git(copia, "revert", "--no-commit", commit)
    if r.returncode:
        return "nao-reverte: conflito ao reverter"
    if not ponta_dirigida(copia, base=base):  # C-7: plano do revert; base= mantém único o trecho do I9a0-1
        return "sem-veredito: o revert pede a suíte inteira (R-TETO)"
    if (codigo := suite_afetada(copia, base)) == 2:
        return "sem-veredito: o forge-testes saiu 2 sem o commit"
    if codigo:
        return "nao-reverte: a suíte afetada falha sem o commit"
    return "reverte"


def main(argv):
    if len(argv) != 2:
        print("uso: conferir-reversao.py BASE BRANCH", file=sys.stderr)
        return 2
    topo = git(".", "rev-parse", "--show-toplevel")
    if topo.returncode:
        print("conferir-reversao: fora de um repositório git", file=sys.stderr)
        return 2
    repo = Path(topo.stdout.strip())
    base, ponta = resolver(repo, argv[0]), resolver(repo, argv[1])
    if not base or not ponta:
        print("conferir-reversao: base ou branch inexistente", file=sys.stderr)
        return 2
    # Sem mesclas: reverter uma mescla exige `-m` e o conteúdo dela já vem dos commits de cada lado, conferidos à parte.
    lista = git(repo, "rev-list", "--reverse", "--no-merges", f"{base}..{ponta}")
    if lista.returncode:
        print("conferir-reversao: intervalo inválido", file=sys.stderr)
        return 2
    commits = lista.stdout.split()
    if not commits:
        print("conferir-reversao: nenhum commit entre a base e a branch.")
        return 0
    with tempfile.TemporaryDirectory(prefix="conferir-reversao-") as tmp:
        copia = Path(tmp) / "repo"
        if not preparar_copia(repo, copia):
            print("conferir-reversao: não consegui copiar o repositório", file=sys.stderr)
            return 2
        if git(copia, "checkout", "--quiet", "--detach", ponta).returncode:
            print("conferir-reversao: não consegui abrir a ponta da branch", file=sys.stderr)
            return 2
        if not ponta_dirigida(copia, base):
            print("conferir-reversao: a ponta pede a suíte inteira, que só roda na trava (R-TETO) e no CI do PR; "
                  "nada classificado.")
            return 0
        if suite_afetada(copia, base):
            print("conferir-reversao: a suíte afetada já falha na ponta da branch; "
                  "nada classificado (corrija a suíte antes).")
            return 0
        for commit in commits:
            print(f"{commit[:7]} {conferir_commit(copia, base, commit)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
