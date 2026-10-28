---
tipo: qa
contrato: 1
pedido: release-timeout
branch: melhoria/release-timeout
commit: 5aacdcdb6cafc7606300a78b7912deb5f70759be
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: release-timeout

Parecer sobre o head 5aacdcdb (diff contra 991cd09: `.github/workflows/release.yml`, `changelog.d/release-timeout.md`, `docs/devops/release-timeout.md`). Pedido de correção sem especificação nova, sem plano antecipado. Não há teste novo nem código de controle (`bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`): vermelho antes do verde e `forge-mutante` não se aplicam.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 / PQ-1: `timeout-minutes: 20` só no job `release` | leitura do YAML (`yaml.safe_load` = 20; 1 ocorrência de `timeout-minutes` em release.yml; jobs `push` e `release`) | n/a | passou |
| Todo job com timeout, sem `paths-ignore` | `tests.test_catraca` (`test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore`, inclui release.yml) | job sem limite | passou |
| Os outros limites seguem (ci.yml 10/15/15, catraca.yml 10) e o prazo da catraca cabe na metade do limite de catraca.yml | `git grep timeout-minutes`; `test_o_prazo_total_cabe_na_metade_do_timeout_do_job` | limite do job catraca | passou |
| A suíte continua rodando antes de publicar (controle intacto) | diff: só o valor e o comentário mudam; `tests.test_ci_local` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_testes_tocados tests.test_ci_local tests.test_catraca`: 394 testes, OK (95,8 s). Nenhum teste fixa o valor 10 do release.
- `forge-check docs`: sem erro.
- Valor 20 só no job `release`: confirmado (única ocorrência em release.yml; os demais workflows não mudaram).
- `actionlint` ausente do PATH: lacuna (mesma do parecer de devops); a edição é um valor e um comentário, e o YAML carrega.
- PA-7: `docs/engineering/achados-recorrentes.md` sem achado registrado (`nenhum ainda`); nada a conferir. Nenhuma classe repetida, sem linha AR nova.
- Não verificável aqui: que 20 min bastam na Release real (medido 10m09s; folga 2x). Só a próxima execução prova; o parecer de devops já registra reavaliar no checkpoint de tempo.
