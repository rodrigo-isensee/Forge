---
tipo: revisao-devops
contrato: 1
pedido: release-timeout
branch: melhoria/release-timeout
commit: 5ebbfd0b261a50e2a999e4a4f09779ba918e5479
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-28
---
# Review de devops: release-timeout

## Parecer
Aprovado. Mudança única em `.github/workflows/release.yml:16`: `timeout-minutes` do job `release` de 10 para 20, com comentário do motivo (10m09s medido nos dois cancelamentos da 0.30.4, run 40654086533). Nenhum outro passo, permissão ou ação alterado; `permissions`, SHAs e `persist-credentials: false` intactos. Nenhum teste fixava o valor 10 do release; a suíte completa passou (2162 testes, rc=0).

Ferramentas: `actionlint` ausente do PATH (lacuna registrada; a edição é de uma linha de valor e um comentário). `shellcheck` e `docker build` não se aplicam.

## Achados
- Nenhum bloqueante.
- release.yml:16 · recomendado · a folga de 2x sobre 10m09s é aceitável, mas a suíte da Release cresce; reavaliar no checkpoint de tempo da próxima release (opção b do pedido, fora do escopo).

## Custo e rollback
Sem recurso novo (`R-CUSTO`): runner padrão, e o teto só consome minutos se a execução durar mais, dentro da franquia. Rollback: reverter o commit (volta a 10).
