---
name: falar-com-o-dono
description: Formato das perguntas do Jarvis ao dono, em lote, com recomendação e prazo, e a regra de que ordem ampla não confirma (R-DECISAO). Use antes de perguntar algo ao usuário e diante de ordem ampla como resolva, acabe tudo ou pode fazer.
---

# Falar com o dono

Texto do Jarvis lido no passo (L51, núcleo curto).

O Jarvis facilita para quem pode não saber desenvolver: pergunta o que é da pessoa (produto, escopo, custo, risco), com recomendação e sem jargão; o técnico e os erros são do time (`R-DECISAO`).

**Perguntas em lote (`R-DECISAO`):** junte as decisões independentes numa mensagem, numeradas. Cada uma segue "Como perguntar" da skill `forge:modo-iniciante`: contexto, opções, "Afrouxa o processo?", custo de eficiência em tempo e tokens por opção, a recomendação e, na reversível sem custo, o prazo. Inclua a saída "decidam vocês", que não se oferece em pergunta de custo, acesso, exceção a regra ou ato irreversível. Decisão dependente vai na rodada seguinte.

**Resposta curta (O4):** opção com código `1a)` e marcas `[recomendada]`, `[reversível]` ou `[irreversível]`; `forge-check decisoes --pedido <id> --resposta "<fala>"` a lê; a ambígua volta como pergunta; `aprovo` só vale para a recomendada `[reversível]` (fora disso, só o código).

**Ordem ampla não confirma:** diante de "resolva", "acabe tudo" ou "pode fazer", faça só o que já está `confirmado` ou `delegado`; o novo ou irreversível volta ao usuário como pergunta, sem passar pelo teste de bloqueante; isso não contradiz o teste de bloqueante, que decide só dúvidas de entendimento.

**Pergunta pendente não segura o tópico (Q2):** o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`; a reversão entra no `## Histórico` como `suposição revertida`; se o dono trocar 2 de 5 escolhas provisórias, a prática volta a esperar. A escolha provisória nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo: essas perguntas seguram o que depende delas (`R-CONFORMIDADE`).

**Ritmo (0.45.7):** o dono escolhe o ritmo uma vez (`ritmo` em `.forge/config.json`, lido por `forge ritmo`): `econômico` (um agente por vez, modelo mais leve para texto, só os testes afetados), `equilibrado` (o padrão) ou `acelerado` (mais trabalho em paralelo, modelo mais forte). "Pode acelerar" vale `forge ritmo acelerado`. Dentro do ritmo, o Jarvis ajusta sem perguntar agentes, modelo, afetados ou suíte, pelo que se mede sozinho: memória e carga (hook `agentes`), tokens por pedido (`forge-check transcricao custo --pedido <id>`) e tempo por etapa (fatia por portão do `forge-check metricas`). Pergunta uma vez por pedido, com custo e ganho (`R-DECISAO`), só se o pedido passar do limite de tokens, se a máquina não comportar o ritmo ou se houver urgência que o ritmo atrase. A cota semanal não aparece no Claude Code: pergunte ao dono de vez em quando e guarde a resposta com a data em `.forge/onboarding.md`. Nenhum ritmo afrouxa: tarefa pesada segue uma por vez (`R-TETO`).
