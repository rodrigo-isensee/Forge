### Corrigido
- Skill `esperar-estado`: o envio longo de um subagente é lançado em segundo plano gravando num log que termina com `rc=` e esperado em primeiro plano, no mesmo turno, pelo laço de 540 s; o tech-lead e o fechamento-integrador deixam de esperar a notificação do fim, que não chega quando o turno acaba (PN5-ESPERA-ENVIO; P-N5, BG-MORRE-TURNO, BRIEF-ESPERA-SH-C).
