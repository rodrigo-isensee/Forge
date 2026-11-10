---
id: R-WIP
titulo: Um cartão por agente e limites de coluna
verificada_por: hook `quadro` (forge-check kanban); auditoria do quadro pelo agile-coach
---
# R-WIP: Um cartão por agente e limites de coluna

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: sem medida (o hook `quadro` barra)

- **1 cartão em "Em andamento" por agente.** Instâncias paralelas de um agente usam cada uma o seu `git worktree`, dentro de `R-TETO`, com `worktree: <nome>` na Obs. e nomes distintos; são no máximo o teto de agentes de `R-TETO` (o `forge-check kanban` barra).
- **Gargalo ganha ajuda.** O agente com fila pode ter mais instâncias iguais, cada uma no seu cartão, respeitando o `R-TETO` inteiro: o teto de agentes, as worktrees (uma por instância, com disco livre), as tarefas pesadas uma por vez e os extras só em trabalho leve; sem folga no teto, a fila espera. A instância que implementou um cartão não faz o review do próprio cartão (`R-REVIEW`).
- Limite mínimo de cada coluna (teto até 3): Empatizar e definir 2 · Idear e prototipar 2 · Pronto para fazer 5 · Em andamento 1 por agente · Code review 2 · QA 2 · Aguardando sua validação 2. Com teto maior, cada limite (menos Em andamento) cresce na proporção **teto ÷ 3, arredondado para baixo**. "Bloqueado" e "Aguardando o dono" sem limite próprio; um cartão só entra em coluna com vaga.
- Cartão em "Bloqueado" ou em "Aguardando o dono" ocupa vaga na coluna de onde saiu; `origem:` nunca é "Validação do usuário" nem "Aguardando sua validação" (`R-DECISAO`).
- Exceções do retrabalho (skill `kanban-scrum`, "Bugs e retrabalho").
