---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 0237a1bcdad85dca462d34aa0426a328f6af78c0
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: v047 (CI-RAPIDO, volta no head 0237a1bc)

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

## Revalidação por delta (88fe9ff4..5b632a48)
Aprovado, sem achado. `forge-check parecer delta` aponta um único arquivo no domínio: `scripts/suite-partes.py`, que só perde `esperado_da_parte`, `pesos_por_modulo` e `dividir` (sem chamador em `scripts/`, `.github/` nem `tests/`; o `dividir` que resta é o de `scripts/suite-paralela.py`, outro módulo). O arquivo compila. `.github/`, `Dockerfile*`, `compose*` e IaC não mudam no intervalo: a análise do `ci.yml` acima segue valendo (permissões, SHAs, agregadores, nomes dos checks exigidos). Fora do domínio, conferi por leitura os textos de `skills/ci-cd/SKILL.md` (orçamento de tempo e agregador com `always()` exigindo `success`, coerentes com o `ci.yml`). `python3 -m unittest tests.test_suite_partes tests.test_ci_local`: 115 testes, OK. A suíte inteira roda só no CI; cite o CI verde do head no merge. Lacunas inalteradas: `actionlint`, `zizmor`, `gitleaks` fora do PATH.

## Revalidação por delta (5b632a48..0237a1bc)
Aprovado, sem achado. `forge-check parecer delta`: nenhum arquivo do domínio mudou (`.github/`, `scripts/`, `bin/`, `.githooks/`, `tests/config.json` intactos). Fora do domínio, só textos: `stacks/node-react/pronto.md` (`vitest --shard` por arquivo, sem pesos), `skills/ci-cd/SKILL.md` (sem medida do Forge, neutro, `R-NEUTRO`), docstring de `tests/test_suite_partes.py` (5 partes) e AR-9. Coerentes com o `ci.yml` já revisado. `tests.test_suite_partes tests.test_ci_local`: testes OK. A suíte inteira roda só no CI. Lacunas inalteradas: `actionlint`, `zizmor`, `gitleaks` fora do PATH.

## Custo e rollback
Sem custo novo de dinheiro (`R-CUSTO`): runners e artefatos da franquia gratuita, retenção de 1 dia. Minutos: a develop passa de 2 jobs de 13 a 20 min para 10 pernas de 2:30 a 5:00 mais 4 jobs curtos, ou seja, o tempo de relógio cai e os minutos somados ficam na mesma ordem; medir por `gh run list` no checkpoint da release. Rollback: reverter o commit do `ci.yml` (volta ao formato 3 partes e aos jobs únicos da develop); os nomes dos checks exigidos não mudam, então não há ajuste de proteção.
