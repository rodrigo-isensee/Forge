---
tipo: qa
contrato: 1
pedido: release-0.15.0
branch: melhoria/release-0.15.0
commit: 8b78858404e593e78d7f2e621f759f4b46f28583
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA - fechamento da versão 0.15.0 (D-RELEASE)

Sem UX nem API. Código da release em 8b78858 sobre a develop a5b0261; o HEAD da branch (0c40ad3) só acrescenta o parecer de review. Não altera código nem CHANGELOG.

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1a | Instalação de ponta a ponta com a versão nova | `bash tests/e2e-instalacao.sh` | n/a | rc=0: plugin instalado, 8 agentes, 9 skills, projeto inicializado |
| PQ-1b | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-2 | Suíte completa (`R-TETO`: uptime antes, load 0.46) | `env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests` | n/a | 650 testes, OK |
| PQ-3 | Fragmentos juntados e versão batendo | `python3 bin/forge-changelog conferir-release` | plugin.json 0.15.0 = CHANGELOG `[0.15.0]`; `changelog.d/` sem pendentes | rc=0 |

## Lacunas
O sandbox nega `api.anthropic.com` e `datadoghq.com` (telemetria do `claude`); a validação e o e2e passaram mesmo assim. O `claude plugin validate . --strict` do CI não foi rodado literalmente; `scripts/validar-plugin.sh` o substitui no sandbox.

## Resultado
Nenhum defeito. Aprovado.
