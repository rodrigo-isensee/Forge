---
tipo: revisao-devops
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <hash do HEAD revisado>
parecer: aprovado
revisor: forge:devops-engineer
data: AAAA-MM-DD
---
# Review de devops: <pedido>

Copie para `docs/devops/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` são ignorados. Exigido quando a entrega toca `.github/`, `Dockerfile*`, `compose*` ou IaC (`R-REVIEW`).

## Parecer
Aprovado ou reprovado; por achado: arquivo:linha · problema · sugestão · severidade (bloqueia ou recomendado). Registre as ferramentas usadas (`actionlint`, `shellcheck`, `docker build`) e as que faltaram no ambiente.

Bloqueio (`R-REVIEW`): `bloqueante` é só defeito provado, requisito ou segurança com gatilho; o resto é `recomendado` e não devolve. Promover recomendação a bloqueante exige `critério mudou:` com o motivo no achado.

## Custo e rollback
Minutos de CI e recursos novos (`R-CUSTO`); procedimento de volta da mudança.
