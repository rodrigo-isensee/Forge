### Corrigido
- Hook `agentes` (H2-RETOMADO-CONFLITO, R-TETO): o retomado cujo `SubagentStart` chega depois da reserva curta e acha a branch dele tomada por outra reserva de escrita viva registra o conflito no `erros.log`, que o vigia mostra no Stop; ele mantém todas as branches no registro, como antes, e segura a branch quando a outra reserva cai.
