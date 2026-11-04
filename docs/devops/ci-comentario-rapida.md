---
tipo: revisao-devops
contrato: 1
pedido: ci-comentario-rapida
branch: melhoria/ci-comentario-rapida
commit: 8bcc469d7eb32f3a09accc59d242755474d54f57
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: ci-comentario-rapida

## Parecer
Aprovado, sem achado bloqueante. Só o comentário do topo do `ci.yml` muda (nenhuma linha executável): o job `rapida` (push na develop) roda a suíte inteira por `scripts/suite-paralela.py` no Python 3.12, sem os demais passos da bateria (shellcheck, actionlint, zizmor, e2e, 3.14). Teste novo em `tests/test_ci_local.py`: o comentário não diz mais "só a checagem rápida" e cita o script que o job roda. Branch empilhada em `melhoria/ci-ubuntu-26` (mesmo arquivo). `test_ci_local`: 54 testes, OK. `actionlint` e `zizmor` ausentes do PATH (lacuna; rodam no CI do PR).
- recomendado: o nome do job ("checagem rápida (push na develop)") segue como está; renomear mudaria o nome do check, que o dono pode ter exigido.

## Custo e rollback
Sem minuto nem recurso novo (`R-CUSTO`). Rollback: reverter o commit.
