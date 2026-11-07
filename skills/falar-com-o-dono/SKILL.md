---
name: falar-com-o-dono
description: Formato da pergunta do Jarvis ao dono e a regra de que ordem ampla não confirma (R-DECISAO). Use antes de perguntar algo ao usuário e diante de ordem ampla como resolva, acabe tudo ou pode fazer.
---

# Falar com o dono

Texto que saiu do `agents/jarvis.md` (L51, núcleo curto) sem mudar de sentido; o Jarvis o lê no passo indicado, porque como agente principal as skills não vêm pré-carregadas.

Pergunta ao usuário segue o formato da seção "Como perguntar" da skill `forge:modo-iniciante` (contexto, exemplo, opções com o efeito de cada uma, "Afrouxa o processo?" e custo de eficiência em tempo e tokens por opção, com faixa, média e a marca `medido`, `estimado` ou `não medido`, recomendação com a base, quantas faltam e a saída "decidam vocês", que não se oferece em pergunta de custo, acesso, exceção a regra ou ato irreversível: `R-DECISAO`), nos dois perfis. **Ordem ampla não confirma:** diante de "resolva", "acabe tudo" ou "pode fazer", faça apenas o que já está `confirmado` ou `delegado`; o que for novo ou irreversível volta ao usuário como pergunta, sem passar pelo teste de bloqueante (`R-DECISAO`, "Complemento"); isso não contradiz o teste de bloqueante, que decide as dúvidas de entendimento e não os itens novos sob ordem ampla.

**Pergunta pendente não segura o tópico (Q2):** o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`, e a reversão entra no `## Histórico` como `suposição revertida`, contada pelo placar `reversoes_do_pedido`; se o dono trocar 2 de 5 escolhas provisórias, a prática volta a esperar. A escolha provisória nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo: essas perguntas seguram o que depende delas (`R-DECISAO`, `R-CONFORMIDADE`).
