### Corrigido
- forge-check: a entrega por --pedido só grava a ponta enviada (a branch no origin, lida pelo git ls-remote, igual ao head; branch nunca enviada, ref de rastreio apagada ou forjada e remoto sem resposta não gravam), e o .md em caminho de controle da classe (.github/, hooks/) não isenta de QA, o que fazia o pr dizer "isento de QA" e "sem parecer de QA" juntos (K-345, v0478 E79.1)
