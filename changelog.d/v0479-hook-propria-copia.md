### Adicionado
- Hook `copia` (HOOK-AGENTE-FORA-DA-PROPRIA-COPIA, R-CONFORMIDADE): o agente do time grava e roda git de escrita só na própria cópia (worktree ou clone de `~/.forge-contrib/wt/` da branch da reserva no registro do R-TETO); a raiz da sessão e as outras cópias recusam; controle, temporárias e leitura seguem livres; sem registro da cópia, libera e anota no erros.log.
