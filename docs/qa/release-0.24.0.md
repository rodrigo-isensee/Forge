---
tipo: qa
contrato: 1
pedido: release-0.24.0
branch: melhoria/release-0.24.0
commit: 765c4ea40c36c052af1c23e2a209049578e2c7db
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: fechamento da release 0.24.0

Ambiente: worktree da branch, conteúdo do commit 765c4ea (o HEAD bc380f0 só acrescenta o parecer de review). Sem rede e sem custo (R-CUSTO). O diff da release é só versão (`plugin.json` e `dev/plugin.json`), entrada do CHANGELOG e remoção de 4 fragmentos; as mudanças de código já passaram por QA nos PRs de origem.

## Critério, teste, resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte completa verde | `python3 -m unittest discover -s tests -q` | n/a | 933 testes, OK (1 skip já existente na base, não adicionado por esta release) |
| Plugin válido | `scripts/validar-plugin.sh` | manifesto raiz e `dev/` | passou, rc 0 |
| Changelog fechado | `bin/forge-changelog conferir-release` | `changelog.d/` sem fragmentos | rc 0 |
| Versão e changelog batem | `bin/forge-changelog conferir --base origin/develop` | 0.23.0 para 0.24.0 | rc 0 |
| Versão maior que homolog e main | `git show origin/homolog:...` e `origin/main:...` | versão igual ou menor | ambas 0.23.0; 0.24.0 é maior |
| Raiz e `dev/` na mesma versão | diff dos dois `plugin.json` | divergência | ambos 0.24.0 |

## Achados
