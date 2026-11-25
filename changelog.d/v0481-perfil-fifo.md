### Corrigido
- conformidade: o texto da recusa lê o `.forge/perfil` sem `git`, sem esperar FIFO (`O_NONBLOCK`) e só se for arquivo regular, e o prazo vencido na escolha do texto cai no texto técnico; um FIFO em `.forge/perfil` já não faz o prazo liberar push na main e `--force` na sessão do Forge (A2 da segurança no #885, v0481 E7.15).
- hooks: o `diretorio_comum` lê o `.git`, o `gitdir` e o `commondir` da worktree sem esperar FIFO e só se forem arquivo regular; um FIFO ali já não atrasa a recusa (A1 da segurança no #886, v0481 E7.19).
