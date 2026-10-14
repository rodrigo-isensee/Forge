---
tipo: qa
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <hash do HEAD testado>
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: AAAA-MM-DD
---
# QA: <pedido>

Copie para `docs/qa/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Médio ou baixo abertos com parecer aprovado exigem a linha `aceite_usuario: sim` no frontmatter. Bugs em `docs/qa/bugs/`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 | CT-01 | vazio, máximo ou `n/a` | passou |

## Cenários e resultado real
