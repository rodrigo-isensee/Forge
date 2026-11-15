---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 88fe9ff40c95a8cae5565c6ea7105117f0a8f4dc
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: v047 (CI-RAPIDO, implementação)

## Achados

## Detalhes
Aprovado. Intervalo `origin/develop...88fe9ff4` (base 067b2a9f), foco em `.github/workflows/ci.yml` (R-REVIEW). Conferi o que a catraca de pipeline exige:

- Permissões: todo job novo tem `permissions: contents: read`; checkout com `persist-credentials: false`; sem `run-id` nem `github-token` no download de artefato (só o run corrente), como pediu A4 do parecer de segurança.
- Ações novas fixadas por SHA com a tag em comentário, as mesmas já usadas no PR (checkout, setup-python, upload e download-artifact). Sem `pull_request_target`, sem `continue-on-error`, sem `[skip ci]`.
- Entrada: só `matrix.parte` (literal) via `env:` ou `${{ }}` em `name`/`path`; nada de ref, título ou branch em `run:` (`R-SEGURANCA`).
- Agregadores `rapida` e `rapida-quatorze` com o nome fixo que `scripts/arvore-testada.py` lê, `if: always()` restrito a push na develop, `needs` da matriz e do teto, e só comparam `needs.*.result` com `success` (matriz com perna pulada, cancelada ou vermelha reprova; A1 atendido). O teto de pulados (`--somar-pulados 5`) roda em job próprio, fora do agregador. O nome das pernas ("suíte (... parte K/5)") não colide com o de prova.
- PR: matriz `[1..5]`, `--parte K/5` e `--somar-pulados 5` coerentes nos dois Pythons; agregadores `bateria` e `bateria (python 3.14)` mantêm o nome (checks exigidos intactos, `R-CONFORMIDADE`: nada a alterar na proteção).
- `timeout-minutes` em todo job novo (15 nas pernas, 5 no teto e no agregador); `retention-days: 1` nos artefatos; `concurrency` do workflow inalterada.
- `scripts/pesos-do-ci.py`: filtro push/develop/`ci.yml`/mesmo repositório/`head_repository`/`success`, unidade no alfabeto `[A-Za-z0-9_.]` e segundos finitos até o teto (A2). Anotações `::notice` sem `checks: write` (S6).
- Verificação: `python3 -m unittest tests.test_pesos_do_ci tests.test_suite_partes` rodou 60 testes, OK. A suíte inteira roda só no CI; cite o CI verde do head no merge.
- Lacunas: `actionlint`, `zizmor` e `gitleaks` ausentes do PATH (não instalo); o módulo `yaml` também falta, então o YAML foi lido por inspeção e pelos testes de matriz de `tests/test_suite_partes.py`. O job de passos do CI roda `actionlint` e `zizmor` no head. Ruleset dos checks exigidos não relido pela API (credencial do `gh` fora do sandbox).
- Observação, sem achado: `pesos-d4.json` sem recalibrar, por desenho do pedido; a recalibração vem depois do primeiro lote de anotações da develop.

## Custo e rollback
Sem custo novo de dinheiro (`R-CUSTO`): runners e artefatos da franquia gratuita, retenção de 1 dia. Minutos: a develop passa de 2 jobs de 13 a 20 min para 10 pernas de 2:30 a 5:00 mais 4 jobs curtos, ou seja, o tempo de relógio cai e os minutos somados ficam na mesma ordem; medir por `gh run list` no checkpoint da release. Rollback: reverter o commit do `ci.yml` (volta ao formato 3 partes e aos jobs únicos da develop); os nomes dos checks exigidos não mudam, então não há ajuste de proteção.
