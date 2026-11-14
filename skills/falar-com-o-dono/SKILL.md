---
name: falar-com-o-dono
description: Formato das perguntas do Jarvis ao dono, uma a uma, com recomendação, e o pedido de decisões com foco total (R-DECISAO). Use antes de perguntar algo ao usuário, quando ele pede as decisões e diante de ordem ampla.
---

# Falar com o dono

Texto do Jarvis lido no passo (L51).

**Perguntas uma a uma (`R-DECISAO`):** uma decisão por mensagem, a mais pesada primeiro; a seguinte, depois da resposta. Cada uma segue "Como perguntar" da skill `forge:modo-iniciante`: contexto, opções, "Afrouxa o processo?", custo de eficiência em tempo e tokens por opção e a recomendação. Sem resposta, fica pendente. Inclua a saída "decidam vocês", que não se oferece nas perguntas que `R-DECISAO` não deixa delegar.

**Pedido de decisões (diretriz 29):** a "me traga as decisões", "o que precisa de mim" ou "quais as pendências", faça só isso, sem disparo, cartão, registro, conferência nem andamento antes. Leia só as perguntas abertas (`PERGUNTA:` e "precisa de você", nos pedidos e no quadro, numa consulta). Responda já: a lista curta de todas as decisões pendentes, da de maior peso para a menor, e a primeira pergunta completa (contexto simples, opções, recomendação, o que acontece sem decisão). Uma a uma, cada resposta por `forge-check anotar` e a próxima logo. O time não para: o que não depende das respostas segue e é disparado, sem aviso ao dono entre as perguntas (resumo no fim); o que depende de uma decisão espera só ela. Sem pendência: "Não há decisão sua pendente", numa linha.

**Pergunta pendente não segura o tópico (Q2):** o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`; a reversão entra no `## Histórico` como `suposição revertida`; trocadas 2 de 5, volta a esperar. A escolha provisória nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo: essas perguntas seguram o que depende delas (`R-CONFORMIDADE`).

O que é da pessoa, custo e origem, resposta curta, ordem ampla e ritmo: skill `fluxo-do-pedido`.
