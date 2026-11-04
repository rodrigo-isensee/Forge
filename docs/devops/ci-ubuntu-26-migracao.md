---
tipo: revisao-devops
contrato: 1
pedido: versao-033
branch: melhoria/ci-ubuntu-26
commit: fd3a3e1536b9b353e1f51e696f04412a5d994f05
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: ci-ubuntu-26-migracao

Segunda rodada do pedido `ci-ubuntu-26` (a primeira, `docs/devops/ci-ubuntu-26.md`, fixou o `ubuntu-24.04`); arquivo novo para não sobrescrever aquele parecer.

## Parecer
Aprovado, sem achado bloqueante. FILA-30 16c, prazo 19/11: os 5 jobs (`ci.yml` 3, `catraca.yml` 1, `release.yml` 1) trocam `ubuntu-24.04` por `ubuntu-26.04`; só a linha `runs-on` mudou. Ficam como estavam: actions fixadas por SHA, `permissions:`, `timeout-minutes`, binários de actionlint e zizmor com SHA256 fixo, e o `release.yml` do #440. Teste novo em `tests/test_ci_local.py` exige `ubuntu-26.04` em todo job (com um job em 24.04 ele falha). `test_ci_local`: 53 testes, OK.
- Hipótese ainda não medida (sem runner 26.04 aqui): o `catraca.yml` usa o `python3` do sistema (sem `setup-python`), que passa de 3.12 para 3.14; a suíte já roda no 3.14 no job `bateria (python 3.14)`, risco baixo. O `shellcheck` do runner passa de 0.9 para 0.11 e pode achar regra nova; o local é 0.9.0 (lacuna). `actionlint` e `zizmor` ausentes do PATH (lacuna; o job `bateria` do PR roda os dois). O primeiro run do PR é a prova.
- recomendado: a branch `melhoria/ci-env-argv0-v2` (sem merge) instala `rust-coreutils` por apt e liga `/usr/lib/cargo/bin/coreutils/env` porque o GNU env do 24.04 recusa `-a`. No 26.04 o `env` do runner pode já ser o do uutils, e pacote ou caminho podem mudar: conferir no primeiro run dela sobre a 26.04 (o passo falha fechado). Não tocada aqui.
- recomendado: fixar `setup-python` no `catraca.yml` se o primeiro run mostrar diferença do 3.14.

## Custo e rollback
Mesmo tipo de runner, sem minuto extra (`R-CUSTO`). Rollback: reverter o commit (volta ao 24.04, até 19/11). Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono, e o push com escopo `workflow` é do dono.
