### Adicionado
- forge-check retomada (BP3 S4): lista os agentes interrompidos pela queda da sessão, com brief e sha256, e a ação da matriz de retomada para cada um; --contar dá só o número (sem rede, até 3 s) para o atalho da S5. Só leitura; a remoção fica com o dono.

### Corrigido
- forge-check retomada (BP3 S4): tipo, id e branch do registro só saem na linha se casam a forma (o resto vira ?, com teto) e o status da worktree usa --no-optional-locks, sem regravar o index.
