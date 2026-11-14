---
name: kanban-metricas
description: Métricas de fluxo e DORA do time, medição do retrabalho, retrospectiva e experimentos de melhoria, do agile-coach. Use ao calcular métricas do time, ao conduzir a retrospectiva e ao registrar experimento; o Jarvis a lê antes de pedir a retrospectiva.
---

# Métricas e retrospectiva do time

Trechos movidos inteiros da skill `kanban-scrum` e do `agile-coach` (diretriz 25: nenhuma regra sai; para caber, mova o detalhe para skill citada).

## Métricas de fluxo do time
- **Lead time:** entrada no Backlog → Pronto. **Cycle time:** entrada em "Em andamento" → Pronto.
- **Vazão:** Pronto por semana. **Idade do WIP:** desde "Em andamento". **Bloqueio:** tempo e motivos.
- **Dois relógios (D-4):** pedido aberto → develop; pronto para fazer → develop (`relogios:`).
- **Retrabalho:** % de cartões que voltaram de Code review, QA ou UX para "Em andamento" (ver "Bugs e retrabalho").
- **Escape:** bugs encontrados depois do parecer do QA.
- Percentis P50/P85 só com 20+ itens; abaixo disso, mostrar os valores individuais. Nunca média sozinha.

## Métricas DORA (sem serviço pago)
Calculadas por período, a partir do git (`git log`, tags de release), dos PRs (`gh pr list --state merged`) e de `docs/kanban/historico.md`:
- **Frequência de entrega:** PRs mesclados na branch de integração (ou releases) por semana.
- **Lead time de mudança:** do primeiro commit da branch até o merge.
- **Taxa de falha:** % das entregas que exigiram correção, reversão ou hotfix (cartões `[bug]` ligados a um pai já em Pronto, `revert`, `fix` urgente).
- **Tempo de recuperação:** da detecção da falha (cartão `[bug]` ou issue) até a correção mesclada.
Mesma regra de amostra das métricas de fluxo. Taxa de falha e tempo de recuperação (estabilidade) pesam tanto quanto frequência e lead time (velocidade): velocidade que sobe com estabilidade em queda não é melhoria.

## Medição do retrabalho
**5. Medição** (a partir de `historico.md`, sempre do processo, nunca de pessoa ou agente)
- Taxa de retrabalho: pais devolvidos / cartões que chegaram ao Code review.
- Voltas por bug: reaberturas por cartão de bug; alvo <= 1, alarme em 3.
- Escape: bugs achados no QA ou depois, que o code review deveria ter pegado, e bugs achados após o parecer do QA.
- Achados por parecer e por severidade, para ver a tendência rodada a rodada. Poucos itens: mostrar os valores brutos.

## Retrospectiva (`docs/retrospectivas/AAAA-MM-DD-<pedido>.md`)
1. Dados do pedido: lead time, cycle time, vazão, retrabalho, bloqueios e as quatro métricas DORA, lendo velocidade e estabilidade juntas.
2. O que funcionou.
3. O que atrapalhou (fatos, não pessoas).
4. **No máximo 1 causa nova**, escolhida por `forge-placar` e `forge-placar propostas` (o checklist: métrica, `Mudança: código:` ou `Mudança: texto:`, critério de reversão, Início e Revisão de 1 a 30 dias; uma proposta aberta por vez), mais a tabela das linhas `MELHORIA:` (`R-DECISAO`), que são só candidatas. O ciclo é do `agile-coach` com o `tech-lead`, sem a pessoa.
5. Revisão das propostas vencidas: `forge-placar comparar --antes <data> --depois <data> --metrica <m>` (rc 0 manter, rc 1 reverter a mudança inteira, rc 3 inconclusivo), com o resultado gravado. `ERRO-JARVIS:` entra como dado, com `Prevenção: eval/trava: <caso>` ou `sem trava possível`. Proibido: regra, lembrete ou checklist em texto sem métrica e prazo; trava sem eval; segunda proposta aberta. À pessoa, só a linha `resumo:` do `forge-placar`.
- Na retrospectiva da 0.42, rode `forge-check provas medida --desde <abertura da 0.41>` e leve o número (conferências de entrega pegas só pelo conferente × as que o CI com a M15 pegaria) ao cartão EST-M2B-REAVALIAR (0.43), como a decisão 9 do dono pede.

## Experimentos de melhoria (`docs/kanban/melhorias.md`)
| ID | Hipótese | Mudança | Métrica | Critério de reversão | Início | Revisão | Resultado |
Uma mudança por vez em cada parte do processo, para saber o que causou o efeito.

## Elementos de Scrum usados
O time trabalha em fluxo contínuo (Kanban), aproveitando de Scrum: **objetivo claro por pedido** (como meta de sprint), **revisão** com o usuário ao fim de cada pedido, **retrospectiva** com ações concretas e **definição de pronto** compartilhada. Não há sprints de duração fixa nem pontos de estória.
