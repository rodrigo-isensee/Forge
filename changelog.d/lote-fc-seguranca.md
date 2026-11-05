### Corrigido
- forge-check entrega: a falha do git em qualquer passo do escopo reprova em toda etapa (rc 1, "o git falhou") em vez de virar "nada a conferir"; sem diff lido, o forge-check pr exige todos os portões (FC-ENTREGA-GIT-FALHA-ABERTA)
- forge-check: --pedido com cara de caminho só vale em docs/pedidos/ de uma raiz guardada (absoluto, ~/, .. e link para fora, inclusive o id nu que é link, recusam com rc 2) (FC-PEDIDO-FORA-DAS-RAIZES)
