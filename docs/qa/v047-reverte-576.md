---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-reverte-576
commit: 988ca87aa95f0b9dea54bdb442f0ee5b5b7f0e0f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 revert do #576 (E2.441)

Código testado: `988ca87a` (revert de `22f1eaa8`, base `befbb464` = `origin/develop`). Revert puro sem especificação de UX nem contrato novo; a obrigação é desfazer o #576 e a catraca de workflows (`R-CONFORMIDADE`) voltar a passar. Sem PR aberto, não há check-run `bateria`; rodei local os módulos que tocam o diff.

## Achados
- A1 (recomendado) docs/engineering/achados-recorrentes.md:23 · o revert devolveu AR-9 a "vezes: 2 · SKILL.md:85"; as ocorrências do #576 (suite-partes) sumiram junto. Se o #576 voltar, recontar; sem ação agora.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Revert toca só os arquivos do #576 | `git show --name-only` de `22f1eaa8` e `HEAD` comparados com `diff` | conjunto idêntico (28 arquivos) | passou |
| 11 arquivos modificados voltam byte a byte ao pré-#576 | `git rev-parse 22f1eaa8^:<f>` = `HEAD:<f>` (ci.yml, suite-partes.py, test_suite_partes.py, test_ci_local.py, test_forge.py, README, stacks, skill ci-cd, protecao-de-branch, economia-de-tokens) | ci.yml e scripts | passou |
| Arquivos criados pelo #576 saem | ausentes em `HEAD` (pesos-do-ci.py, 7 mutantes, 2 testes, pareceres) | n/a | passou |
| Exceção declarada: `achados-recorrentes.md` | diff contra `22f1eaa8` mostra só a linha AR-9 revertida; AR-1/AR-4 de outros PRs preservados | linha única | passou |
| Catraca de workflows volta a passar | `tests.test_catraca` (inclui `ci.yml` e `runs_dos_workflows` no repo real) | classes citadas em `run:` | passou |
| Partes da suíte e CI local coerentes com o ci.yml restaurado | `tests.test_suite_partes`, `tests.test_ci_local`, `tests.test_forge` | ci.yml restaurado | passou |

## Cenários e resultado real
Comando na raiz do clone: `python3 -m unittest tests.test_catraca tests.test_suite_partes tests.test_ci_local tests.test_forge`

```
Ran 1066 tests in 1600.792s
OK
```

Vermelho antes do verde: não se aplica, não há teste novo (o revert restaura testes pré-#576). Mutação: não se aplica, não há linha de guarda nova. Suíte inteira: fica para o CI do PR.

`origin/develop` = `befbb464` = base do brief.
