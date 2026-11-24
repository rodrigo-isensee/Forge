---
name: produto-criterios
description: Transforma o pedido de quem não programa em critérios de aceite verificáveis antes do time começar. Use quando o Jarvis ou o ux-designer receber um pedido novo, antes de abrir o cartão e de delegar.
---

# Critérios de aceite do pedido

Dono: o Jarvis, com o `ux-designer` quando há tela. Sem critério verificável, o time não sabe quando acabou e o QA não sabe o que testar.

## Passos
1. **Reescreva o pedido em uma frase:** quem faz o quê e para quê. Se faltar um dos três e a resposta mudar o escopo, é pergunta bloqueante ao dono (`R-DECISAO`); o resto vira suposição registrada.
2. **Liste de 3 a 7 critérios** no formato: Dado um contexto, quando a pessoa faz algo, então vê ou recebe um resultado que se observa. Cada critério tem um número, um texto ou uma tela como prova, nunca "funciona bem" nem "rápido". Cada um ganha um id estável `C-n` (`- C-1 Dado ...` no `## Critério de pronto` do pedido): o id nunca se renumera nem se reaproveita; critério retirado fica com o id e a marca de corte.
3. **Inclua o que não muda e o caso de erro:** uma linha de fora de escopo e uma de entrada inválida ou falha.
4. **Marque como cada critério se verifica:** teste automático, olhar a tela ou conferir um dado. O QA parte desta lista.
5. **Grave no cartão e no pedido** (`docs/pedidos/`) e mostre à pessoa em linguagem simples (skill `explicar-para-o-leigo` se for iniciante). Mudou o critério depois, registre a mudança e avise quem já começou.
6. **Ligue cada critério a uma prova:** o `PQ-n` do brief que o prova leva o campo `cobre: C-n` (`- PQ-1 (cmd): ... · espera: rc=0 · cobre: C-1, C-2`; `R-PROVA`). A tabela pedido × entregue sai de `forge-check criterios <pedido>`, não à mão: o critério conta como entregue só com um `PQ-n` que o cobre num brief selado cuja etapa do `Cobre:` tem `entrega conferida` no `## Histórico`; sem isso, sai "não entregue" (rc 1).

## Teste
Um critério vale se duas pessoas diferentes chegam ao mesmo "passou" ou "não passou". Se não, reescreva.
