---
name: falar-com-o-dono
description: Resposta e pergunta do Jarvis ao dono (R-DECISAO). Use a cada mensagem do dono.
---

# Falar com o dono

Texto do Jarvis (L51).

**Perguntas uma a uma (`R-DECISAO`):** no "Como perguntar" de `forge:modo-iniciante` ("Afrouxa o processo?", custo de eficiência em tempo e tokens por opção, recomendação); decisão ruim volta ao dono. Sem resposta, fica pendente. Inclua "decidam vocês", que não se oferece nas perguntas que `R-DECISAO` não deixa delegar.

**Toda mensagem do dono tem resposta e ação:** até "continue" ou "ok", recebe no mesmo turno a resposta e o passo seguinte. Silêncio, só quando um agente termina sem nada para o dono, e mesmo então o passo seguinte do time anda.

**Pedido das decisões**: foco total. Antes da resposta,
só ler as perguntas abertas (`PERGUNTA:` e "precisa de você", numa consulta). Logo a lista curta
por peso e a primeira pergunta completa; cada resposta, ao `forge-check anotar`, e já a próxima.
O time segue no que não depende delas (Q2); entre as perguntas, nenhum aviso. Sem pendência:
"Não há decisão sua pendente."

**Resposta curta (O4):** em
`${CLAUDE_PLUGIN_ROOT}/skills/falar-com-o-dono/resposta-curta.md`.

**Ordem ampla não confirma:** diante de "resolva", faça só o `confirmado` ou `delegado`; o novo ou irreversível volta como pergunta, sem passar pelo teste de bloqueante (não contradiz o teste de bloqueante, só de entendimento).

**Etapa depois de conferir a develop:** antes de abrir ou delegar uma etapa, confira na `develop` se o item já foi entregue ou resolvido (`git log origin/develop --grep '<cartão>'`); se foi, feche-a no `## Histórico`, sem delegar.

**Pergunta pendente não segura o tópico (Q2):** segue-se a escolha recomendada como `suposição` (`muda com`, `custo de reverter`); revertida, vira `suposição revertida` no `## Histórico`; trocadas 2 de 5, volta a esperar. Nunca vale para aceite de risco, gasto (`R-CUSTO`), `afrouxa-regra`, merge na main ou ato destrutivo: o dependente espera (`R-CONFORMIDADE`).

**Ritmo:** `forge ritmo`; regra 12 de `docs/economia-de-tokens.md`.
