---
id: R-WIP
titulo: Um cartão por agente e limites de coluna
verificada_por: revisão (auditoria do quadro pelo agile-coach) e hook `quadro` (forge-check kanban)
---
# R-WIP: Um cartão por agente e limites de coluna

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- **1 cartão em "Em andamento" por agente.** Instâncias paralelas de um agente usam cada uma o seu `git worktree`, dentro de `R-TETO`.
- Limite de cada coluna do `KANBAN.md`: Empatizar e definir 2 · Idear e prototipar 2 · Pronto para fazer 5 · Em andamento 1 por agente · Code review 2 · QA 2 · Aguardando sua validação 2. Entrada, Validação do usuário e Pronto não têm limite.
- Puxar, não empurrar: um cartão só entra numa coluna que tem vaga. Coluna cheia: o time termina ou destrava o que já existe antes de começar algo novo.
- Cartão em "Bloqueado" ocupa vaga na coluna de onde saiu.
- Exceções, ambas do retrabalho (processo na skill `kanban-scrum`, "Bugs e retrabalho"): o cartão pai à espera dos próprios bugs não ocupa vaga, ocupam os cartões de bug; e um autor pode ter até 3 cartões de retrabalho em andamento, atacados por ordem de severidade.
