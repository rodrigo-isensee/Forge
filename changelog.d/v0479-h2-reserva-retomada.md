### Corrigido
- Hook `agentes` (H2-RESERVA-DA-RETOMADA-PRAZO, R-TETO): o agente retomado por `SendMessage` cujo `SubagentStart` chega depois dos 5 min da reserva curta reserva de novo as branches dele, e a hora anunciada na recusa de branch ocupada sai do mesmo prazo da expiração (função única `prazo_do_registro`).
