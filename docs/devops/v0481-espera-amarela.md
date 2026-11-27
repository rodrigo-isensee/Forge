---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 517557abcd34a5605bac2c37b3d344acb953ed61
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: v0481 (espera amarela, #948, E47.4)

- ci: 517557abcd34a5605bac2c37b3d344acb953ed61 verde

## Achados
- A1 (recomendado) .github/workflows/ci.yml:1 · actionlint e zizmor ausentes na estação; o parecer não rodou os dois sobre ci.yml e catraca.yml. Instalar por scripts/preparar-estacao.sh.
- A2 (recomendado) .github/workflows/catraca.yml:70 · o agregador `catraca` herda o `contents: read` do topo; declarar `permissions: {}` no job (não usa API) segue o menor privilégio por job.

## Detalhes
Aprovado. Lido o diff de `ci.yml`, `catraca.yml`, `scripts/ci-local` e `tests/catraca.py` contra a base.

- Permissões: `checks: read` entra só nos jobs `pareceres` e `conferencia`, que leem o check-run do próprio head por `gh api`; nada de escrita. No job de pareceres o token fica em `TOKEN_DE_LEITURA` e o script Python roda com `env -u`, então o código do PR/da base não o recebe. `PR_TITULO` entra por `env:` (nunca interpolado em `run:`), usado só em regex pelo script.
- `always()`: o agregador `catraca` novo tem `always()` e exige `conferencia == success`; cancelado, pulado ou vermelho reprova. O `agregador` do ci.yml já tinha `always()` e exige `pareceres == success` em PR; o rc 3 só deixa o job verde com a saída `espera` gravada (rc diferente de 0 e 3 sai com o próprio rc).
- Nomes frente ao ruleset da develop (lido por `gh api rules/branches/develop`): exigidos `bateria`, `bateria (python 3.14)`, `catraca`. Em espera os nomes viram `bateria (espera parecer)` e `catraca (espera rótulo)`; o check exigido com o nome exato não é reportado e fica pendente, então a junção segue barrada. O nome volta ao exato quando a saída some (rc 0). `bateria (python 3.14)` não muda.
- Falha fechada: leitura da API que falha, ou check `bateria`/`catraca` já verde no mesmo head (de outro run), saem com 1, para o verde velho não valer. Os eventos `labeled`/`unlabeled`/`edited` já reexecutam a catraca depois do rótulo.
- `scripts/ci-local`: `pernas` expande o nome do job sem matriz, descartando o sufixo `needs.*`, de modo que o nome reportado é o do check exigido; coberto por `tests/test_ci_local.py`.
- Sem `continue-on-error`, `[skip ci]` ou check desligado; ações fixadas por SHA como antes; nenhum job novo escreve na `main` (`R-MAIN`).
- CI (G3): no `Revisar-sha` todos verdes, e2e e instalação inclusos, salvo `bateria (pareceres)`, `bateria`, `catraca` (esperam o parecer e o rótulo) e `catraca (conferência)`, vermelho só pelo rótulo `afrouxa-regra` ainda ausente (o log lista só violações R-CONFORMIDADE de .github/ e tests/catraca.py, liberáveis pelo rótulo; os dois "confira" não barram). Como o brief prevê, os workflows rodam o script da base, e a espera ainda aparece vermelha neste PR. O rótulo do dono vem depois das revisões; o título já traz `[afrouxa-regra`.
- PQ-3 não é rc 0 enquanto o rótulo e este parecer faltam; a leitura acima é o que vale.

## Custo e rollback
Um job extra de poucos segundos por PR (catraca), repositório público, sem custo de dinheiro (`R-CUSTO`). Rollback: reverter o commit (os dois workflows voltam aos jobs únicos); nada de estado externo.
