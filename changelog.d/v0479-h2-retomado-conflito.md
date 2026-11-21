### Corrigido
- Hook `agentes` (H2-RETOMADO-CONFLITO, R-TETO): o retomado cujo `SubagentStart` chega depois da reserva curta não grava por cima da branch que outra reserva de escrita viva tomou; a reserva viva vale e o conflito vai ao `erros.log`, que o vigia mostra no Stop.
