"""Só para os testes: roda um script Python do Forge como a pessoa no terminal, sem o `claude` que roda a suíte como ancestral.

A guarda `forge_versoes.dentro_do_claude` recusa quando um processo ancestral se chama `claude` (F5-01, R-CONFORMIDADE). A
suíte rodada de dentro do Claude Code (o pre-push de um agente) descende do `claude`, e os testes do caminho feliz, que
simulam a pessoa no terminal, falhavam (TESTES-SEM-CLAUDE-ANCESTRAL). Este lançador troca `_pai_e_nome`, só no processo que
ele roda, por uma leitura que para no processo `--ate <pid>` (o do teste): os ancestrais acima dele não contam, os de baixo
seguem contando (um `claude` entre o teste e o script ainda recusa), e a variável do Claude Code no ambiente também. A troca
passa aos scripts do mesmo `bin/` que o processo chama com `sys.executable` (o `forge atualizar` chama o `forge-voltar-versao`).
No `forge-sempre-atual`, a leitura dos processos vivos (`pids_do_proc`) vê só os descendentes do processo `--ate`: o `forge-fechar`
ou o `claude` de outra parte da suíte, vivo ao mesmo tempo, adiava um escopo do teste (DEFEITO-TESTES-DE-PRAZO-SOB-CARGA).

Não há interruptor em produção: nenhum script do Forge lê este arquivo nem variável nova; a guarda fica como está.

Com `--proc <pasta>` (opcional), o `forge-sempre-atual` lê os processos vivos dessa pasta, que o teste monta (`<pid>/comm` e
`<pid>/cwd`), no lugar do `/proc` da máquina: no sandbox do Bash o `/proc` é de outro namespace de pid e o oráculo adiava tudo
por `duvida:proc`. É só do lançador, que nenhum script do Forge lê; a leitura de `comm`, `cwd` e `cmdline` segue a de produção.

Uso: python3 tests/sem_claude_ancestral.py --ate <pid> [--proc <pasta>] <script> [argumentos...]
"""
import runpy
import subprocess
import sys
from pathlib import Path

ESTE = str(Path(__file__).resolve())


def comando(script, *args, ate, proc=None):
    """A linha de comando que roda `script` pelo lançador, cortando a leitura dos ancestrais no processo `ate`; com `proc`, a
    leitura dos processos vivos é da pasta dada (a árvore que o teste monta), não do `/proc` da máquina."""
    extra = ["--proc", str(proc)] if proc else []
    return [sys.executable, ESTE, "--ate", str(ate), *extra, str(script), *map(str, args)]


def descende_de(pid, ate, pai_e_nome):
    """True se `pid` é `ate` ou descende dele, pela cadeia de pais de `pai_e_nome(pid) -> (pai, nome)`. O processo de outra
    parte da suíte que roda ao mesmo tempo (um `forge-fechar` de verdade, um `claude` falso) não descende do teste."""
    vistos = set()
    while pid > 0 and pid not in vistos:
        if pid == ate:
            return True
        vistos.add(pid)
        pid = pai_e_nome(pid)[0]
    return False


def main():
    if len(sys.argv) < 4 or sys.argv[1] != "--ate":
        sys.exit("uso: sem_claude_ancestral.py --ate <pid> <script> [argumentos...]")
    ate, resto = int(sys.argv[2]), sys.argv[3:]
    proc = None
    if resto[0] == "--proc":
        proc, resto = str(Path(resto[1]).resolve()), resto[2:]
    script = Path(resto[0]).resolve()
    pasta = script.parent
    if (pasta / "forge_versoes.py").is_file():  # script de fora do `bin/` do Forge (o teste da espera do pty) roda como está
        sys.path.insert(0, str(pasta))
        import forge_versoes  # o mesmo módulo que o script importa depois (fica em sys.modules)

        original = forge_versoes._pai_e_nome
        forge_versoes._pai_e_nome = lambda pid: (0, "") if pid == ate else original(pid)
        if script.name == "forge-sempre-atual":  # DEFEITO-TESTES-DE-PRAZO-SOB-CARGA (v0478): só o mundo do teste
            import forge_sempre_atual

            if proc:  # mundo do teste montado na pasta: o /proc da máquina não entra (nem a coerência dele, nem os pids)
                forge_sempre_atual.PROC = proc
                forge_sempre_atual.proc_coerente = lambda: True
            else:
                todos = forge_sempre_atual.pids_do_proc
                forge_sempre_atual.pids_do_proc = lambda: [n for n in todos() if descende_de(int(n), ate, original)]

    class Popen(subprocess.Popen):
        def __init__(self, args, *resto, **nomeados):
            if (isinstance(args, (list, tuple)) and len(args) > 1 and args[0] == sys.executable
                    and Path(str(args[1])).resolve().parent == pasta):
                args = comando(args[1], *args[2:], ate=ate, proc=proc)
            super().__init__(args, *resto, **nomeados)

    subprocess.Popen = Popen
    sys.argv = [str(script), *resto[1:]]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
