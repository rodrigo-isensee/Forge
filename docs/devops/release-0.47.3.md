---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.3
branch: melhoria/v047-release-0473
commit: eb9b4295bd8cafbbd70977f9c9170275b7932982
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-16
---
# Review de devops: release-0.47.3

## Achados

## Detalhes
Aprovado. A mudança (5 arquivos: versão em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`, entrada 0.47.3 no `CHANGELOG.md`, dois fragmentos de `changelog.d/` apagados) não toca `.github/`, `Dockerfile*`, `compose*` nem IaC: `git diff origin/develop HEAD -- .github` sem diferença.

- Promoção: `homolog` e `main` estão na 0.47.1 e não existe tag `v0.47.2`. A promoção develop, homolog e main leva a 0.47.2 e a 0.47.3 juntas; o `CHANGELOG.md` traz as duas entradas, e a versão dos dois manifestos (0.47.3) bate com a entrada mais nova (R-FLUXO, R-MAIN).
- `ci.yml` segue o de 3 partes: matriz `parte: [1, 2, 3]` em `partes-doze` e `partes-quatorze`, nome "suíte (python X, parte K/3)", agregador e parecer em jobs próprios, sem alteração nesta leva.
- Sem `continue-on-error`, `[skip ci]` ou check afrouxado introduzido (R-VERIFY).
- Ferramentas: `git diff`, `grep`; `actionlint` e `shellcheck` não foram necessários, pois nenhum workflow nem script mudou.

## Custo e rollback
Sem minutos nem recurso novos (R-CUSTO). Volta: reverter o commit de versão na `develop` antes da promoção; depois da release, reimplantar a tag anterior (v0.47.1).
