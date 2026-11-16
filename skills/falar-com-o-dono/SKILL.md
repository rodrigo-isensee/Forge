---
name: falar-com-o-dono
description: Perguntas do Jarvis ao dono, uma a uma e com recomendação; ordem ampla não confirma (R-DECISAO). Use a cada mensagem do dono e antes de perguntar a ele.
---

# Falar com o dono

Texto do Jarvis (L51).

**Perguntas uma a uma (`R-DECISAO`):** de produto, escopo, custo ou risco, sem jargão, uma decisão por mensagem, a mais pesada primeiro. Cada uma segue "Como perguntar" de `forge:modo-iniciante`: contexto, opções, "Afrouxa o processo?", tempo e tokens por opção, origem e recomendação. Sem resposta, fica pendente. Inclua "decidam vocês", que não se oferece nas perguntas que `R-DECISAO` não deixa delegar. Decisão ruim do dono volta a ele. **Resposta curta (O4):** opção `1a)` com `[recomendada]`, `[reversível]` ou `[irreversível]` (`decisoes --resposta`); corte recomendado leva `origem:`, `procurado:`, `seguir:`, `não seguir:`; `aprovo` só vale para a recomendada `[reversível]`.

**Toda mensagem do dono tem resposta e ação:** até "continue" ou "ok", recebe no mesmo turno a resposta e o passo seguinte. Silêncio, só quando um agente termina sem nada para o dono, e mesmo então o passo seguinte do time anda.

**Ordem ampla não confirma:** diante de "resolva" ou "pode fazer", faça só o `confirmado` ou `delegado`; o novo ou irreversível volta como pergunta, sem passar pelo teste de bloqueante (não contradiz o teste de bloqueante, só de entendimento).

**Etapa depois de conferir a develop:** antes de abrir ou delegar uma etapa, confira na `develop` se o item já foi entregue ou resolvido (`git log origin/develop --grep '<cartão>'`); se foi, feche-a com o commit no `## Histórico`, sem delegar.

**Pergunta pendente não segura o tópico (Q2):** segue-se a escolha recomendada como `suposição` (`muda com`, `custo de reverter`); revertida, vira `suposição revertida` no `## Histórico`; trocadas 2 de 5, volta a esperar. Nunca vale para aceite de risco, gasto (`R-CUSTO`), `afrouxa-regra`, merge na main ou ato destrutivo: o que depende delas espera (`R-CONFORMIDADE`).

**Ritmo:** `forge ritmo`; regra 12 de `docs/economia-de-tokens.md`.
