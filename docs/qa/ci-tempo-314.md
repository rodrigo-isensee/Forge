---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/ci-tempo-314
commit: 65f402e7c65349036c36c9c769c77f6a09b0ffff
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: ci-tempo-314 (E23.15)

Diff d3453407..65f402e7: timeout-minutes de `rapida` (ci.yml:37) e `rapida-quatorze` (ci.yml:79) de 20 para 30, o teste tests/test_catraca.py:3322 e o fragmento de changelog.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Teto 30 nas duas checagens rápidas; os demais jobs inalterados | `Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore` (assertEqual da lista posicional de 13 tetos) | teto de cada job; a ordem ancora `rapida` e `rapida-quatorze` nas duas primeiras posições | passou |
| Mutante: teto de `rapida` volta a 20 (linha 37) | mesmo teste | teto | morreu (FAILED) |
| Mutante: teto de `rapida-quatorze` volta a 20 (linha 79) | mesmo teste | teto | morreu (FAILED) |

## Cenários e resultado real
- `python3 -m unittest tests.test_catraca.Workflows`: 6 testes, OK.
- Mutantes feitos à mão em cópia em `$TMPDIR` (sed na linha 37 e na 79, 30 para 20): os dois falham no teste acima. O workflow não tem lógica de guarda mudada além do número.
- Sem divisão do job: `scripts/arvore-testada.py` usa os nomes dos jobs como prova (JOBS_DE_PROVA), então manter os dois jobs é coerente.
- A medição (3.12 em 12,7 a 15,7 min; 3.14 cancelada nos 20 min) é do autor e não foi reexecutada aqui; o teto 30 só vale se o CI do PR confirmar. A suíte inteira roda no CI do PR (bateria do mesmo sha).
