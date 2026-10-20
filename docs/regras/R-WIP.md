---
id: R-WIP
titulo: Um cartão por agente e limites de coluna
verificada_por: revisão (auditoria do quadro pelo agile-coach) e hook `quadro` (forge-check kanban)
---
# R-WIP: Um cartão por agente e limites de coluna

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- **1 cartão em "Em andamento" por agente.** Instâncias paralelas de um agente usam cada uma o seu `git worktree`, dentro de `R-TETO`. A instância extra tem o seu cartão, e a Obs. de cada cartão do agente traz `worktree: <nome>` (o nome da worktree; `principal` para o diretório principal). Com mais de um cartão do mesmo agente, todos trazem o campo, com nomes distintos, e são no máximo o teto de agentes de `R-TETO` (o diretório principal e as worktrees que o teto permite, com disco livre; menos se `teto_maximo` ou `teto_agentes` de `.forge/config.json` for menor). O `forge-check kanban`, que o hook `quadro` roda, barra o quadro sem o campo, com nome repetido ou acima desse número; não se contorna trocando o nome do responsável (`R-CONFORMIDADE`).
- **Gargalo ganha ajuda.** Todo agente que virar gargalo (há fila de cartões esperando por ele) pode ter mais instâncias iguais, cada uma no seu cartão e na sua worktree, sempre respeitando o `R-TETO` inteiro: o teto de agentes, as worktrees (uma por instância, com disco livre), as tarefas pesadas uma por vez e os agentes extras só em trabalho leve. O Jarvis sobe a instância ao ver a fila e a dispensa quando a fila acaba; sem folga no teto, a fila espera (decisão do dono em 2026-10-15). A instância que implementou um cartão não faz o review do próprio cartão (`R-REVIEW`).
- Limite de cada coluna do `KANBAN.md`, **mínimo** (teto de agentes de `R-TETO` até 3): Empatizar e definir 2 · Idear e prototipar 2 · Pronto para fazer 5 · Em andamento 1 por agente · Code review 2 · QA 2 · Aguardando sua validação 2. Com o teto calculado maior, cada limite do `WIP` do cabeçalho de coluna (menos o de Em andamento, que é foco e não capacidade) cresce na proporção **teto ÷ 3, arredondado para baixo** (teto 16: limites ×5; teto 6: ×2); o `forge-check kanban` usa a mesma função do hook `agentes`. Entrada, Validação do usuário e Pronto não têm limite.
- Puxar, não empurrar: um cartão só entra numa coluna que tem vaga. Coluna cheia: o time termina ou destrava o que já existe antes de começar algo novo.
- Cartão em "Bloqueado" ocupa vaga na coluna de onde saiu.
- Exceções, ambas do retrabalho (processo na skill `kanban-scrum`, "Bugs e retrabalho"): o cartão pai à espera dos próprios bugs não ocupa vaga, ocupam os cartões de bug; e um autor pode ter até 3 cartões de retrabalho em andamento, atacados por ordem de severidade.
