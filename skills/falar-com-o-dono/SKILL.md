---
name: falar-com-o-dono
description: Formato das perguntas do Jarvis ao dono, em lote, com recomendação e prazo, e a regra de que ordem ampla não confirma (R-DECISAO). Use antes de perguntar algo ao usuário e diante de ordem ampla como resolva, acabe tudo ou pode fazer.
---

# Falar com o dono

Texto do Jarvis lido no passo (L51).

O Jarvis pergunta o que é da pessoa (produto, escopo, custo, risco), sem jargão; o técnico e os erros são do time (`R-DECISAO`).

**Perguntas em lote (`R-DECISAO`):** junte as decisões independentes numa mensagem, numeradas. Cada uma segue "Como perguntar" da skill `forge:modo-iniciante`: contexto, opções, "Afrouxa o processo?", custo de eficiência em tempo e tokens por opção, a recomendação e, na reversível sem custo, o prazo. Inclua a saída "decidam vocês", que não se oferece em pergunta de custo, acesso, exceção a regra ou ato irreversível. Decisão dependente vai na rodada seguinte.

**Resposta curta (O4):** opção com código `1a)` e marcas `[recomendada]`, `[reversível]` ou `[irreversível]`; `decisoes --resposta` a lê; corte recomendado leva `origem:`, `procurado:`, `seguir:`, `não seguir:`; `aprovo` só vale para a recomendada `[reversível]` (fora disso, só o código).

**Ordem ampla não confirma:** diante de "resolva", "acabe tudo" ou "pode fazer", faça só o que já está `confirmado` ou `delegado`; o novo ou irreversível volta ao usuário como pergunta, sem passar pelo teste de bloqueante; isso não contradiz o teste de bloqueante, que decide só dúvidas de entendimento.

**Pergunta pendente não segura o tópico (Q2):** o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`; a reversão entra no `## Histórico` como `suposição revertida`; se o dono trocar 2 de 5 escolhas provisórias, a prática volta a esperar. A escolha provisória nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo: essas perguntas seguram o que depende delas (`R-CONFORMIDADE`).

**Ritmo:** `forge ritmo` e a regra 9 de `docs/economia-de-tokens.md`.
