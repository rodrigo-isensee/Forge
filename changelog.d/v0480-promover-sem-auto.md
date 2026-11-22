### Corrigido
- PROMOVER-SEM-AUTO-MERGE: o scripts/promover-homolog.py não imprime mais o merge automático; só com todo check obrigatório (CHECKS_EXIGIDOS do bin/forge-fechar) em pass imprime o merge direto preso ao head, e pendente ou sem check sai com 4, sem comando de merge (decisão do dono: merge automático proibido em qualquer PR).
