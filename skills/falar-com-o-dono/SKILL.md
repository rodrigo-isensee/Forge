---
name: falar-com-o-dono
description: Formato das perguntas do Jarvis ao dono, uma a uma, com recomendação, e a regra de que ordem ampla não confirma (R-DECISAO). Use antes de perguntar algo ao usuário e diante de ordem ampla como resolva, acabe tudo ou pode fazer.
---

# Falar com o dono

Texto do Jarvis lido no passo (L51).

O Jarvis pergunta o que é da pessoa (produto, escopo, custo, risco), sem jargão; o técnico e os erros são do time (`R-DECISAO`).

**Perguntas uma a uma (`R-DECISAO`):** uma decisão por mensagem, a mais pesada primeiro; a seguinte, depois da resposta. Cada uma segue "Como perguntar" da skill `forge:modo-iniciante`: contexto, opções, "Afrouxa o processo?", custo de eficiência em tempo e tokens por opção e a recomendação. Sem resposta, fica pendente. Inclua a saída "decidam vocês", que não se oferece nas perguntas que `R-DECISAO` não deixa delegar.

**Resposta curta (O4):** opção com código `1a)` e marcas `[recomendada]`, `[reversível]` ou `[irreversível]`; `decisoes --resposta` a lê; corte recomendado leva `origem:`, `procurado:`, `seguir:`, `não seguir:`; `aprovo` só vale para a recomendada `[reversível]` (fora disso, só o código).

**Ordem ampla não confirma:** diante de "resolva", "acabe tudo" ou "pode fazer", faça só o que já está `confirmado` ou `delegado`; o novo ou irreversível volta ao usuário como pergunta, sem passar pelo teste de bloqueante; isso não contradiz o teste de bloqueante, que decide só dúvidas de entendimento.

**Pergunta pendente não segura o tópico (Q2):** o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`; a reversão entra no `## Histórico` como `suposição revertida`; se o dono trocar 2 de 5 escolhas provisórias, a prática volta a esperar. A escolha provisória nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo: essas perguntas seguram o que depende delas (`R-CONFORMIDADE`).

**Ritmo:** `forge ritmo` e a regra 12 de `docs/economia-de-tokens.md`.
