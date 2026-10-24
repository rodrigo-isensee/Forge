---
tipo: qa
contrato: 1
pedido: release-0.30.0
branch: melhoria/release-0.30.0
commit: dcb80ad7df0ef6ff0e361fcc6faa8cb35895c873
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: release-0.30.0

Pedido REL-0300-REV, etapa E3.1. Base `3d73bdc2b1941cae893d50ee2421060d843f16b9`, head `dcb80ad7df0ef6ff0e361fcc6faa8cb35895c873`. Sem especificação de UX nem contrato de API: as obrigações vêm do pedido REL-0300 (escopo E1).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: CHANGELOG junta os 8 fragmentos (#298 a #308) | `bin/forge-changelog release 0.30.0 2026-10-24` sobre a base, em cópia no TMPDIR, e `diff` com o CHANGELOG do commit | todos os 8 fragmentos (8 em `changelog.d/` na base, 8 juntados) | passou: diff vazio |
| E1: fragmentos apagados | `ls changelog.d` na cópia após o release | pasta sem fragmento | passou |
| E1: versão 0.30.0 nos dois manifestos | `cmp` dos dois `plugin.json` gerados contra os do commit; `tests.test_forge -k test_versao_igual_a_do_forge` | manifesto da raiz e `dev/` iguais | passou |
| E1: testes do changelog e da conferência de release | `tests.test_changelog`, `tests.test_conferir_release` | n/a | passou (45 testes, 1 skip) |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | passou (rc=0) |
| Diff só de release | `git diff --name-only` | nenhum arquivo fora de CHANGELOG, `changelog.d/`, dois `plugin.json` | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog tests.test_conferir_release`: `Ran 45 tests ... OK (skipped=1)`. O skip é `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, que só vale em `melhoria/*` e a worktree está em HEAD solto (skip da própria condição do teste, não escondido por mim); o diff não adiciona fragmento.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0.
- Reprodução: `git archive` da base em `$TMPDIR/qa-engineer-release-0.30.0/base`, `bin/forge-changelog release 0.30.0 2026-10-24` gravou `8 fragmento(s) juntado(s) e apagado(s)`; `diff` do CHANGELOG com o do commit vazio; os dois manifestos idênticos byte a byte.
- Conferência da dupla mudança em `dev/.claude-plugin/plugin.json` (fora da lista do brief): coberta pela decisão técnica do Jarvis no pedido, e provada aqui, pois o próprio `release` a grava.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem achado recorrente registrado, nada a conferir.
- Vermelho antes do verde e mutação: não se aplicam (nenhum teste novo, nenhum arquivo de `bin/`, `hooks/` ou `.githooks/` alterado no diff).
- Sandbox: chamadas de rede negadas (api.anthropic.com, datadog) durante a validação do plugin não afetaram o resultado.
