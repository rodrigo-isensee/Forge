---
name: falar-com-o-dono
description: Perguntas do Jarvis ao dono, uma a uma, com recomendação; ordem ampla não confirma (R-DECISAO). Use antes de perguntar ao usuário, no pedido das decisões e diante de ordem ampla (resolva, acabe tudo, pode fazer).
---

# Falar com o dono

Texto do Jarvis (L51).

**Perguntas uma a uma (`R-DECISAO`):** no formato de "Como perguntar" da skill `forge:modo-iniciante` (opções, "Afrouxa o processo?", custo de eficiência em tempo e tokens por opção, recomendação); decisão ruim do dono volta a ele. Sem resposta, fica pendente. Inclua a saída "decidam vocês", que não se oferece nas perguntas que `R-DECISAO` não deixa delegar.

**Pedido das decisões** ("me traga as decisões", "o que precisa de mim"): foco total. Antes da
resposta, só ler as perguntas abertas (`PERGUNTA:` e "precisa de você", numa consulta). Logo a
lista curta por peso e a primeira pergunta completa; cada resposta, ao `forge-check anotar`, e já a
próxima. O time segue no que não depende delas (Q2); entre as perguntas, nenhum aviso (o andamento,
num resumo no fim). Sem pendência: "Não há decisão sua pendente."

**Resposta curta (O4):** formato inteiro em
`${CLAUDE_PLUGIN_ROOT}/skills/falar-com-o-dono/resposta-curta.md`.

**Ordem ampla não confirma:** diante de "resolva", "acabe tudo" ou "pode fazer", faça só o que já está `confirmado` ou `delegado`; o novo ou irreversível volta ao usuário como pergunta, sem passar pelo teste de bloqueante; isso não contradiz o teste de bloqueante, que decide só dúvidas de entendimento.

**Pergunta pendente não segura o tópico (Q2):** o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`; a reversão entra no `## Histórico` como `suposição revertida`; trocadas 2 de 5, volta a esperar. A escolha provisória nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo: essas perguntas seguram o que depende delas (`R-CONFORMIDADE`).

**Ritmo:** `forge ritmo`; regra 12 de `docs/economia-de-tokens.md`.
