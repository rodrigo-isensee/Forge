---
name: produto-criterios
description: Transforma o pedido de quem não programa em critérios de aceite verificáveis antes do time começar. Use quando o Jarvis ou o ux-designer receber um pedido novo, antes de abrir o cartão e de delegar.
---

# Critérios de aceite do pedido

Dono: o Jarvis, com o `ux-designer` quando há tela. Sem critério verificável, o time não sabe quando acabou e o QA não sabe o que testar.

## Passos
1. **Reescreva o pedido em uma frase:** quem faz o quê e para quê. Se faltar um dos três e a resposta mudar o escopo, é pergunta bloqueante ao dono (`R-DECISAO`); o resto vira suposição registrada.
2. **Liste de 3 a 7 critérios** no formato: Dado um contexto, quando a pessoa faz algo, então vê ou recebe um resultado que se observa. Cada critério tem um número, um texto ou uma tela como prova, nunca "funciona bem" nem "rápido".
3. **Inclua o que não muda e o caso de erro:** uma linha de fora de escopo e uma de entrada inválida ou falha.
4. **Marque como cada critério se verifica:** teste automático, olhar a tela ou conferir um dado. O QA parte desta lista.
5. **Grave no cartão e no pedido** (`docs/pedidos/`) e mostre à pessoa em linguagem simples (skill `explicar-para-o-leigo` se for iniciante). Mudou o critério depois, registre a mudança e avise quem já começou.

## Teste
Um critério vale se duas pessoas diferentes chegam ao mesmo "passou" ou "não passou". Se não, reescreva.
