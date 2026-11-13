---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-parecer-job
commit: bd28180e9129015578029dee765abd206960bac1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v047 (E1.10 e E1.19, code review da E1.4, CI-PARECER-NAO-BARRA-SUITE)

Head revisado 7ba85a05 (E1.10), revalidado por delta em bd28180e (E1.19), base a986c292. Diff: 55 linhas que contam (ci.yml 27+/5-, testes 17+/4-), um comportamento só, dentro da orientação M14.

## O que está certo
- O passo de parecer saiu do job `bateria (passos)` e virou o job `pareceres` (nome `bateria (pareceres)`), sem token (`contents: read`), checkout com `persist-credentials: false`, ações no mesmo SHA dos outros jobs, `timeout-minutes: 10`. O corpo do passo é o mesmo de antes (script da base, ADR 0008, seção 3).
- O job não está em `needs` das partes nem de `verificacoes`, e o agregador `bateria` (o check exigido, mesmo nome) o tem em `needs`. Parecer faltando deixa de pular a suíte. Era esse o pedido.
- Fora de PR o job é pulado e o agregador aceita `skipped` só quando o evento não é `pull_request`. Push em homolog/main e `workflow_dispatch` ficam como antes (o passo antigo também só rodava em PR).
- A regra chegou aos projetos em `agents/devops-engineer.md` e no `pronto.md` das stacks node-react e python, com fragmento em `changelog.d/`. Os testes de leitura (`test_ci_local`, `test_catraca.Workflows`) passam no head: 72 testes OK.

## Ferramentas (citadas, sem refazer)
- `bin/forge-mutante --cobertura --base a986c292e4ec78e2ae357bead4bb9ae71f8fd99f` no head: `não coberto: .github/workflows/ci.yml`. Não há `tests/mutantes/v047*.json`.
- CI: a branch ainda não tem PR, então não há CI para citar. Rodei só os testes afetados e as sondas abaixo.

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:674 · Guarda nova do agregador (pareceres success, ou skipped fora de PR) e `if:` do job (:550) sem mutante declarado nem teste do ramo de falha (classe C; --cobertura: não coberto). S1 a S3 sobrevivem: tirar a checagem de pareceres deixa os testes verdes. Resolvido em a453857a (E1.19).
- A2 (recomendado) .github/workflows/ci.yml:451 · O gate de commit só de parecer exige `bateria` verde no commit anterior. Com parecer faltando o agregador fica vermelho mesmo com a suíte verde, e o commit do parecer roda a suíte de novo. Avaliar se o gate pode ler os jobs da suíte em vez do agregador. Segue aberto na E1.19, não devolve.

## Sondas
- S1 · ci.yml:674 sem o trecho de PARECERES (fica só PASSOS..PULADOS), rodando tests.test_ci_local e tests.test_catraca.Workflows · espera: algum teste falha · obtido: Ran 72 tests, OK
- S2 · ci.yml:674 com `[ "$EVENTO" != pull_request ]` trocado por `true` (skipped aceito em PR), mesmos testes · espera: algum teste falha · obtido: Ran 72 tests, OK
- S3 · ci.yml:550 sem `if: github.event_name == 'pull_request'` no job pareceres, mesmos testes · espera: algum teste falha · obtido: Ran 72 tests, OK

## Parecer
Reprovado por A1. O desenho está correto e cumpre o pedido, mas a garantia central ("obrigatório para o merge") está numa guarda de shell que nenhum teste vigia. Com S1, um parecer faltando passaria pelo agregador e o merge abriria, e mesmo assim a suíte segue verde. Sugestão: declarar `tests/mutantes/v047-ci-parecer-job.json` com um mutante por linha de guarda mudada (:550 e :674, e as duas alternativas de :674 em separado) e escrever um teste de comportamento pelo ci-local (`ci.status` ou o runner do agregador) com `pareceres` em `failure`, e em `skipped` com evento `pull_request`, cada um reprovando o agregador. Teste que procura o texto da linha na fonte não conta. A2 não devolve.

## Revalidação (E1.19, delta 7ba85a05..bd28180e)
Delta lido: `forge-check parecer delta docs/reviews/v047-ci-parecer-job.md`, intervalo 7ba85a05..bd28180e; no domínio: `.github/workflows/ci.yml`, `agents/devops-engineer.md`, `changelog.d/v047-ci-parecer-job.md`, `stacks/node-react/pronto.md`, `stacks/python/pronto.md`, `tests/mutantes/v047-ci-parecer-job.json`, `tests/test_catraca.py`, `tests/test_ci_local.py`, `tests/test_suite_partes.py`.
- A1 resolvido: `tests/mutantes/v047-ci-parecer-job.json` declara um mutante por guarda (M1 a M4 nas alternativas de :674, M5 no `if:` de :550, M6 no teto de :552). `bin/forge-mutante tests/mutantes/v047-ci-parecer-job.json` no head bd28180e: M1 a M6 `morreu`. S1, S2 e S3 do review anterior correspondem a M1, M3 e M5 e agora morrem.
- Os testes novos de `tests/test_ci_local.py` executam o `run:` do agregador de verdade (bash -eo pipefail, ambiente limpo com só PATH), em PR e fora dele, com success, failure, skipped, cancelled e vazio, e os demais jobs em failure: teste de comportamento, não leitura de texto. `test_job_pareceres_so_roda_em_pr_e_sem_needs` lê o `if:` e o `needs` pelo parser do ci-local, o que basta para M5.
- `timeout-minutes` 10 → 5 (J9) acompanhado em `tests/test_catraca.py` e no teste do bloco; `tests/test_suite_partes.py` passa a exigir `pareceres` no `needs` do agregador. Texto J11 em `agents/devops-engineer.md` e nos dois `pronto.md` coerente com o código.
- Testes afetados no head (ambiente limpo): `tests.test_ci_local`, `tests.test_catraca.Workflows`, `tests.test_suite_partes.FiacaoDoCI`, Ran 82 tests, OK. Sem PR, sem CI para citar; a suíte inteira fica para o CI do PR.
- Tamanho (M14): o delta soma 41 linhas em `tests/test_ci_local.py` e poucas linhas no resto, dentro da orientação.

## Parecer (E1.19)
Aprovado no head bd28180e. A1 resolvido com mutantes declarados que morrem e teste de comportamento do agregador; nenhum achado novo no delta. A2 segue recomendado.
