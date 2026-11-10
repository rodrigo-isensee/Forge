---
name: explicar-para-o-leigo
description: Traduz PR, parecer ou entrega em "o que mudou para você" para quem não programa. Use no modo iniciante (.forge/perfil) antes de mostrar qualquer resultado técnico à pessoa.
---

# Explicar para o leigo

Faz parte do modo iniciante (skill `modo-iniciante`). A pessoa decide produto, escopo, custo e risco; ela não lê diff.

## Formato (até 6 linhas)
1. **O que mudou para você:** o efeito que ela vê ou sente, em uma frase.
2. **Como conferir:** um passo que ela mesma faz (abrir tal tela, tentar tal ação).
3. **O que não mudou:** se algo que ela espera continua igual.
4. **Risco:** só se existir, com o que acontece se der errado e como volta atrás.
5. **O que preciso de você:** uma decisão com a minha recomendação, ou "nada, só avisando".

## Como traduzir
- Parta do critério de aceite do pedido (`produto-criterios`) e diga se foi cumprido.
- Parecer de review, segurança ou QA: diga o veredito e o que ele protege ("ninguém acessa dados de outra pessoa"), não o nome do achado.
- Troque jargão por o que a coisa faz; se um termo técnico for inevitável, explique-o uma vez entre parênteses.
- Nunca esconda reprovação, falha ou custo: diga o que aconteceu, o efeito e o próximo passo.
