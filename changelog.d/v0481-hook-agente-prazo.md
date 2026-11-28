### Corrigido
- Hook `agentes`: o aviso de brief vencido pergunta ao git em lote (um `rev-list` por ponta e um `cat-file --batch-check`), com as mesmas respostas; com centenas de linhas `conferida` no pedido, o disparo decide em menos de 1 s, sem a recusa do vigia de 8 s (R-TETO) (v0481 E50.1).
