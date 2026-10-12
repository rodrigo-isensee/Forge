---
name: kanban-scrum
description: Práticas de Kanban e Scrum do time - estrutura do quadro KANBAN.md, formato de cartão, políticas de coluna e WIP, registro de transições, métricas de fluxo, retrospectiva e experimentos de melhoria contínua. Use ao mover cartões, auditar o quadro, calcular métricas do time ou conduzir retrospectivas.
---

# Kanban e Scrum do time

## Quadro (`KANBAN.md`, na raiz)
Visível no GitHub e no editor. Duas partes, separadas pelo **ponto de compromisso**.

**Upstream — descoberta (Design Thinking, conduzido pelo `ux-designer`)**

| Coluna | Entra quando | Limite de WIP |
|---|---|---|
| **Entrada** | Pedido registrado em `docs/pedidos/` | — |
| **Empatizar e definir** | UX e arquiteto começaram o discovery | 2 |
| **Idear e prototipar** | Problema definido e aceito | 2 |
| **Validação do usuário** | Protótipo pronto, aguardando o usuário | — |

▶ **Ponto de compromisso:** protótipo validado pelo usuário. Correções e tarefas técnicas sem interface entram direto em "Pronto para fazer".

**Downstream — entrega**

| Coluna | Entra quando | Limite de WIP |
|---|---|---|
| **Pronto para fazer** | Validado, quebrado em cartões, critério de pronto claro | 5 |
| **Em andamento** | Um agente começou a implementar | 1 por agente |
| **Code review** | Implementação entregue ao `tech-lead` | 2 |
| **QA** | Code review aprovado | 2 |
| **Aguardando sua validação** | QA aprovado, branch enviada, PR pronto para o usuário | 2 |
| **Pronto** | Usuário validou e fez o merge na `main` | — |
| **Bloqueado** | Dependência externa ou decisão pendente (registrar motivo e coluna de origem) | conta no WIP da origem (exceção: cartão pai aguardando bugs, ver "Bugs e retrabalho") |

Políticas:
- Puxar, não empurrar: só entra numa coluna se houver vaga no WIP.
- Terminar antes de começar: com WIP cheio, o time ajuda a destravar o que existe.
- Nenhuma coluna é pulada no downstream: todo cartão passa por Code review e QA.
- Só o usuário move um cartão para "Pronto" (ao fazer o merge).
- Bloqueio: o cartão vai para "Bloqueado" com a coluna de origem anotada e volta para ela.
- Cartão devolvido no code review ou no QA volta para "Em andamento" e conta como retrabalho.

## Formato do cartão
Uma linha de tabela por cartão, em cada coluna:

```markdown
| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |
|---|---|---|---|---|---|---|
| K-012 | Tela de login - fluxo principal | 001 | react-frontend | 2026-10-09 | 2026-10-10 | — |
```

- ID sequencial `K-NNN`, nunca reutilizado.
- Responsável é um agente (ou "usuário" quando depende de você).
- Tamanho: um cartão cabe em até uma fase do pedido; se for maior, quebrar.
- No topo do quadro: data/hora da última atualização e um resumo (WIP por coluna × limite, itens bloqueados, item mais antigo em andamento).

## Histórico (`docs/kanban/historico.md`)
Append-only, uma linha por movimento — é a fonte das métricas:

```markdown
| Data/hora | Cartão | De | Para | Motivo |
|---|---|---|---|---|
| 2026-10-10 14:05 | K-012 | Pronto para fazer | Em andamento | — |
```

## Métricas de fluxo do time
- **Lead time:** entrada no Backlog → Pronto. **Cycle time:** entrada em "Em andamento" → Pronto.
- **Vazão:** cartões em Pronto por semana.
- **Idade do WIP:** tempo desde a entrada em "Em andamento" dos cartões abertos.
- **Tempo bloqueado** e **motivos de bloqueio**.
- **Retrabalho:** % de cartões que voltaram de Code review, QA ou UX para "Em andamento" (ver "Bugs e retrabalho").
- **Escape:** bugs encontrados depois do parecer do QA.
- Percentis P50/P85 só com 20+ itens; abaixo disso, mostrar os valores individuais. Nunca média sozinha.

## Bugs e retrabalho
Todo achado de code review, revisão de UX e bug do QA volta ao autor por este processo (pedido do usuário). O Jarvis cria os cartões no mesmo dia do parecer; o agile-coach audita.

**1. Achado vira cartão**
- ID `K-NNN` normal, título com prefixo `[bug]` (defeito: não cumpre spec, regra ou teste) ou `[ajuste]` (melhoria pedida em revisão, sem defeito). Obs. com: `origem` (code review / QA / UX), `pai` (cartão de origem, ex. K-004), `severidade` (bloqueante, crítico, alto, médio, baixo; a maior do grupo), contagem por severidade e link do parecer (`docs/reviews/...` ou `docs/qa/...`) com os números dos achados. O texto do achado fica no parecer; o cartão não o copia.
- Severidade: bloqueante = fere regra inviolável, ADR ou critério de pronto; crítico = quebra função principal ou acessibilidade essencial; alto = desvio da spec que a próxima fase replicaria; médio = desvio localizado; baixo = polimento. "Recomendado" do code review conta como médio, salvo se o parecer disser que vira bloqueante.

**2. Agrupamento**
Um cartão por (origem, área, faixa de severidade), revisável de uma vez: bloqueantes/críticos de code review num cartão; altos de UX noutro; médios e baixos de UX juntos. Nunca um cartão por achado. Achado novo de severidade maior que a do grupo, ou de outra área, vira cartão próprio. Tamanho máximo: o que o autor entrega e o revisor lê em uma sessão; senão dividir por área.

**3. Fluxo**
- Entra em "Em andamento" com o autor original, sem passar por "Pronto para fazer". Depois: Code review, QA, e revisão de UX se houver interface (nenhuma coluna pulada; o QA roda a suíte completa).
- Conta como retrabalho (métrica: cartão devolvido). O histórico registra `Code review -> Em andamento` no pai e `Entrada -> Em andamento` nos cartões de bug.
- O cartão pai vai para "Bloqueado" (motivo: "aguardando bugs K-xxx", origem Em andamento) até todos os bugs bloqueantes, críticos e altos fecharem; só então volta e segue o fluxo com os bugs. **Exceção de WIP:** o pai aguardando bugs não conta no WIP (senão o mesmo trabalho conta duas vezes); contam os cartões de bug. A idade do pai continua correndo (cycle time não para).
- Bug aprovado em code review e QA fecha junto com o pai: não tem "Pronto" próprio, vai com o pai para "Aguardando sua validação"; o histórico registra "Fechado com K-xxx".

**4. Limites e prioridade**
- Máximo de 3 voltas por bug (rodadas de review/QA que o reabrem). Na 3ª reprovação o Jarvis leva a decisão ao usuário; registrar no cartão "voltas: n".
- Bloqueante, crítico e alto são puxados antes de qualquer trabalho novo ("terminar antes de começar"): nada em "Pronto para fazer" ou "Entrada" é puxado enquanto houver bug dessas severidades aberto.
- Cartões de retrabalho do mesmo autor podem ocupar até a vaga cheia do WIP (3); o agente trabalha em ordem de severidade. É a única exceção a "um cartão em Em andamento por agente".
- Médio e baixo abertos só acompanham uma entrega ao usuário com aprovação explícita dele (portão de QA em `.claude/agents/jarvis.md`), listados no PR como pendências. Bloqueante, crítico e alto nunca seguem abertos.

**5. Medição** (a partir de `historico.md`, sempre do processo, nunca de pessoa ou agente)
- Taxa de retrabalho: pais devolvidos / cartões que chegaram ao Code review.
- Voltas por bug: reaberturas por cartão de bug; alvo <= 1, alarme em 3.
- Escape: bugs achados no QA ou depois, que o code review deveria ter pegado, e bugs achados após o parecer do QA.
- Achados por parecer e por severidade, para ver a tendência rodada a rodada. Poucos itens: mostrar os valores brutos.

**6. A cada rodada de review/QA, o Jarvis**
1. Confere que o parecer tem contagem por severidade e links com número de achado.
2. Cria os cartões de bug/ajuste agrupados, lança o movimento no histórico (hora real) e move o pai para Bloqueado.
3. Encaminha ao autor e puxa os bugs antes de trabalho novo.
4. Ao receber a correção: Code review, QA, UX; só fecha o pai com todos os bloqueantes, críticos e altos fechados.
5. Pede ao agile-coach a auditoria do quadro e inclui as métricas de retrabalho na retrospectiva.

## Retrospectiva (`docs/retrospectivas/AAAA-MM-DD-<pedido>.md`)
1. Dados do pedido: lead time, cycle time, vazão, retrabalho, bloqueios.
2. O que funcionou.
3. O que atrapalhou (fatos, não pessoas).
4. Até 3 ações — cada uma com responsável, mudança exata e como medir.
5. Revisão das ações da retrospectiva anterior: funcionou, não funcionou, abandonar.

## Experimentos de melhoria (`docs/kanban/melhorias.md`)
| ID | Hipótese | Mudança | Métrica | Início | Revisão | Resultado |
Uma mudança por vez em cada parte do processo, para saber o que causou o efeito.

## Elementos de Scrum usados
O time trabalha em fluxo contínuo (Kanban), aproveitando de Scrum: **objetivo claro por pedido** (como meta de sprint), **revisão** com o usuário ao fim de cada pedido, **retrospectiva** com ações concretas e **definição de pronto** compartilhada. Não há sprints de duração fixa nem pontos de estória.
