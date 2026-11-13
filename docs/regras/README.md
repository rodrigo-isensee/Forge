# Regras da fábrica

Propósito: índice das regras com ID (como cada uma é verificada fica no frontmatter dela). Público: todo o time e quem mantém o Forge.

Decisão: `docs/adr/0002-uma-fonte-por-regra.md`. Agentes, skills e modelos citam o ID com o nome curto; o texto fica só aqui (o teste `AntiDuplicacao` reprova trecho de 12 palavras copiado; exceções em `anti_duplicacao.excecoes` de `tests/config.json`). IDs nunca se reaproveitam. [`R-LIMITES`](R-LIMITES.md) junta `R-MAIN`, `R-VERIFY`, `R-CUSTO`, `R-CONTRIB` e `R-COPIA`: cada um continua sendo o ID citado, e o texto fica num arquivo só.

**Validade e medida (decisão do dono, 2026-11-08):** toda regra traz `Revisar em:` e `Medida:` (o número que a justifica; regra sem número ganha um até 2027-01-07 ou sai, AV5); `forge-check regras` aponta as vencidas. Regra nova só com medida (`R-DECISAO`).

| ID | Regra |
|---|---|
| [`R-MAIN`](R-LIMITES.md#r-main-a-main-é-do-usuário) | A main é do usuário |
| [`R-FLUXO`](R-FLUXO.md) | Branches, integração contínua e promoção |
| `R-WIP` | Um cartão por agente e limites de coluna (a linha abaixo da tabela; só o hook `quadro` a verifica) |
| [`R-TETO`](R-TETO.md) | Teto de recursos da máquina |
| [`R-QA`](R-QA.md) | Portão de QA |
| [`R-REVIEW`](R-REVIEW.md) | Code review em toda entrega, numa passada |
| [`R-DISCOVERY`](R-DISCOVERY.md) | Todo pedido começa com discovery |
| [`R-CUSTO`](R-LIMITES.md#r-custo-nada-que-custe-dinheiro-sem-autorização) | Nada que custe dinheiro sem autorização |
| [`R-NEUTRO`](R-NEUTRO.md) | Neutralidade da fábrica |
| [`R-COPIA`](R-LIMITES.md#r-copia-não-copiar-agentes-e-skills-para-o-projeto) | Não copiar agentes e skills para o projeto |
| [`R-VERIFY`](R-LIMITES.md#r-verify-nunca---no-verify-nem---force) | Nunca `--no-verify` nem `--force` |
| [`R-DECISAO`](R-DECISAO.md) | Decisões do dono uma a uma, com opções e recomendação, sem prazo que decida |
| [`R-CONFORMIDADE`](R-CONFORMIDADE.md) | Controles não se contornam; o que está em vigor é do usuário |
| [`R-CONTRIB`](R-LIMITES.md#r-contrib-contribuição-ao-forge-projeto-abre-pr-nunca-mescla) | Contribuição ao Forge: projeto abre PR, nunca mescla |
| [`R-SEGURANCA`](R-SEGURANCA.md) | Parecer de segurança quando há gatilho |
| [`R-PROVA`](R-PROVA.md) | Afirmação com prova |
| [`R-BRIEF`](R-BRIEF.md) | Brief selado pela ferramenta antes da delegação |

**`R-WIP` (regra só de hook; o `forge-check kanban` e o hook `quadro` barram):** **1 cartão em "Em andamento" por agente.** Instâncias paralelas de um agente usam cada uma o seu `git worktree`, dentro de `R-TETO`, com `worktree: <nome>` na Obs. e nomes distintos; são no máximo o teto de agentes de `R-TETO`. **Gargalo ganha ajuda.** O agente com fila pode ter mais instâncias iguais, cada uma no seu cartão, respeitando o `R-TETO` inteiro: o teto de agentes, as worktrees (uma por instância, com disco livre), as tarefas pesadas uma por vez e os extras só em trabalho leve; sem folga no teto, a fila espera; a instância que implementou um cartão não faz o review do próprio cartão (`R-REVIEW`). Limite mínimo de cada coluna (teto até 3): Empatizar e definir 2 · Idear e prototipar 2 · Pronto para fazer 5 · Em andamento 1 por agente · Code review 2 · QA 2 · Aguardando sua validação 2; com teto maior, cada limite (menos Em andamento) cresce na proporção **teto ÷ 3, arredondado para baixo**; "Bloqueado" e "Aguardando o dono" sem limite próprio, e um cartão só entra em coluna com vaga. Cartão em "Bloqueado" ou em "Aguardando o dono" ocupa vaga na coluna de onde saiu; `origem:` nunca é "Validação do usuário" nem "Aguardando sua validação" (`R-DECISAO`). Exceções do retrabalho: skill `kanban-scrum`, "Bugs e retrabalho". Medida: 10 mensagens de recusa `(R-WIP)` em `bin/forge-check` (`grep -c '(R-WIP)'`); revisar em 2027-01-07.
