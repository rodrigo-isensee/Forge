# Decisões de arquitetura do Forge

Propósito: índice das ADRs da fábrica. Público: quem mantém o Forge e quem contribui de um projeto. Revisão: 2026-10-12.

Formato: contexto, decisão, alternativas e consequências; estado conforme `docs/padrao-de-documentacao.md` ("Estado das ADRs"). Numeração sequencial, nunca reaproveitada.

## Vigentes
| ADR | Assunto |
|---|---|
| [0001](0001-nucleo-neutro-e-pacotes-de-stack.md) | Núcleo neutro e pacotes de stack em `stacks/<nome>/` |
| [0002](0002-uma-fonte-por-regra.md) | Uma fonte por regra em `docs/regras/`, com IDs |
| [0003](0003-hooks-deterministicos-e-silenciosos.md) | Hooks determinísticos e silenciosos no plugin |
| [0004](0004-contrato-verificavel-entre-agentes.md) | Contrato verificável entre agentes e `forge-check` |
| [0005](0005-migracao-iniciada-pelo-projeto.md) | Migração iniciada pelo projeto e `forge-upgrade` |
| [0006](0006-contribuicao-de-qualquer-projeto.md) | Contribuição de qualquer projeto e versão só na release |
| [0007](0007-verificacao-de-comportamento-sem-custo.md) | Verificação de comportamento sem custo |
| [0008](0008-governanca-de-contribuicoes.md) | Governança de contribuições: portões para todos, catraca e identidade dos agentes |

## Substituídas
Nenhuma.

## Ordem de implementação
0006 (versão no CI, destrava PRs paralelos) → 0002 (regras com ID) → 0004 (contrato e `forge-check`) → 0003 (hooks, que usam os dois) → 0001 (stacks) → 0005 (migração, que leva os projetos ao novo formato) → 0007 → 0008.
