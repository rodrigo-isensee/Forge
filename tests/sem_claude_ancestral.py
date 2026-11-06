"""Só para os testes: roda um script Python do Forge como a pessoa no terminal, sem o `claude` que roda a suíte como ancestral.

A guarda `forge_versoes.dentro_do_claude` recusa quando um processo ancestral se chama `claude` (F5-01, R-CONFORMIDADE). A
suíte rodada de dentro do Claude Code (o pre-push de um agente) descende do `claude`, e os testes do caminho feliz, que
simulam a pessoa no terminal, falhavam (TESTES-SEM-CLAUDE-ANCESTRAL). Este lançador troca `_pai_e_nome`, só no processo que
ele roda, por uma leitura que para no processo `--ate <pid>` (o do teste): os ancestrais acima dele não contam, os de baixo
seguem contando (um `claude` entre o teste e o script ainda recusa), e a variável do Claude Code no ambiente também. A troca
passa aos scripts do mesmo `bin/` que o processo chama com `sys.executable` (o `forge atualizar` chama o `forge-voltar-versao`).

Não há interruptor em produção: nenhum script do Forge lê este arquivo nem variável nova; a guarda fica como está.

Uso: python3 tests/sem_claude_ancestral.py --ate <pid> <script> [argumentos...]
"""
import runpy
import subprocess
import sys
from pathlib import Path

ESTE = str(Path(__file__).resolve())


def comando(script, *args, ate):
    """A linha de comando que roda `script` pelo lançador, cortando a leitura dos ancestrais no processo `ate`."""
    return [sys.executable, ESTE, "--ate", str(ate), str(script), *map(str, args)]


def main():
    if len(sys.argv) < 4 or sys.argv[1] != "--ate":
        sys.exit("uso: sem_claude_ancestral.py --ate <pid> <script> [argumentos...]")
    ate, script = int(sys.argv[2]), Path(sys.argv[3]).resolve()
    pasta = script.parent
    if (pasta / "forge_versoes.py").is_file():  # script de fora do `bin/` do Forge (o teste da espera do pty) roda como está
        sys.path.insert(0, str(pasta))
        import forge_versoes  # o mesmo módulo que o script importa depois (fica em sys.modules)

        original = forge_versoes._pai_e_nome
        forge_versoes._pai_e_nome = lambda pid: (0, "") if pid == ate else original(pid)

    class Popen(subprocess.Popen):
        def __init__(self, args, *resto, **nomeados):
            if (isinstance(args, (list, tuple)) and len(args) > 1 and args[0] == sys.executable
                    and Path(str(args[1])).resolve().parent == pasta):
                args = comando(args[1], *args[2:], ate=ate)
            super().__init__(args, *resto, **nomeados)

    subprocess.Popen = Popen
    sys.argv = [str(script), *sys.argv[4:]]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
