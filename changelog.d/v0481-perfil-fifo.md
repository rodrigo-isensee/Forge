### Corrigido
- conformidade: o texto da recusa lê o `.forge/perfil` sem `git`, sem esperar FIFO (`O_NONBLOCK`) e só se for arquivo regular, e o prazo vencido na escolha do texto cai no texto técnico; um FIFO em `.forge/perfil` já não faz o prazo liberar push na main e `--force` na sessão do Forge (A2 da segurança no #885, v0481 E7.15).
