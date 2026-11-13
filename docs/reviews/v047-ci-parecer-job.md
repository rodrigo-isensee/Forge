---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-parecer-job
commit: 7ba85a056b4eb332362ce5cda7b6efb193b6b017
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v047 (E1.10, code review da E1.4, CI-PARECER-NAO-BARRA-SUITE)

Head revisado 7ba85a05, base a986c292. Diff: 55 linhas que contam (ci.yml 27+/5-, testes 17+/4-), um comportamento só, dentro da orientação M14.

## O que está certo
- O passo de parecer saiu do job `bateria (passos)` e virou o job `pareceres` (nome `bateria (pareceres)`), sem token (`contents: read`), checkout com `persist-credentials: false`, ações no mesmo SHA dos outros jobs, `timeout-minutes: 10`. O corpo do passo é o mesmo de antes (script da base, ADR 0008, seção 3).
- O job não está em `needs` das partes nem de `verificacoes`, e o agregador `bateria` (o check exigido, mesmo nome) o tem em `needs`. Parecer faltando deixa de pular a suíte. Era esse o pedido.
- Fora de PR o job é pulado e o agregador aceita `skipped` só quando o evento não é `pull_request`. Push em homolog/main e `workflow_dispatch` ficam como antes (o passo antigo também só rodava em PR).
- A regra chegou aos projetos em `agents/devops-engineer.md` e no `pronto.md` das stacks node-react e python, com fragmento em `changelog.d/`. Os testes de leitura (`test_ci_local`, `test_catraca.Workflows`) passam no head: 72 testes OK.

## Ferramentas (citadas, sem refazer)
- `bin/forge-mutante --cobertura --base a986c292e4ec78e2ae357bead4bb9ae71f8fd99f` no head: `não coberto: .github/workflows/ci.yml`. Não há `tests/mutantes/v047*.json`.
- CI: a branch ainda não tem PR, então não há CI para citar. Rodei só os testes afetados e as sondas abaixo.

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:674 · Guarda nova do agregador (pareceres success, ou skipped fora de PR) e `if:` do job (:550) sem mutante declarado nem teste do ramo de falha (classe C; --cobertura: não coberto). S1 a S3 sobrevivem: tirar a checagem de pareceres deixa os testes verdes.
- A2 (recomendado) .github/workflows/ci.yml:451 · O gate de commit só de parecer exige `bateria` verde no commit anterior. Com parecer faltando o agregador fica vermelho mesmo com a suíte verde, e o commit do parecer roda a suíte de novo. Avaliar se o gate pode ler os jobs da suíte em vez do agregador.

## Sondas
- S1 · ci.yml:674 sem o trecho de PARECERES (fica só PASSOS..PULADOS), rodando tests.test_ci_local e tests.test_catraca.Workflows · espera: algum teste falha · obtido: Ran 72 tests, OK
- S2 · ci.yml:674 com `[ "$EVENTO" != pull_request ]` trocado por `true` (skipped aceito em PR), mesmos testes · espera: algum teste falha · obtido: Ran 72 tests, OK
- S3 · ci.yml:550 sem `if: github.event_name == 'pull_request'` no job pareceres, mesmos testes · espera: algum teste falha · obtido: Ran 72 tests, OK

## Parecer
Reprovado por A1. O desenho está correto e cumpre o pedido, mas a garantia central ("obrigatório para o merge") está numa guarda de shell que nenhum teste vigia. Com S1, um parecer faltando passaria pelo agregador e o merge abriria, e mesmo assim a suíte segue verde. Sugestão: declarar `tests/mutantes/v047-ci-parecer-job.json` com um mutante por linha de guarda mudada (:550 e :674, e as duas alternativas de :674 em separado) e escrever um teste de comportamento pelo ci-local (`ci.status` ou o runner do agregador) com `pareceres` em `failure`, e em `skipped` com evento `pull_request`, cada um reprovando o agregador. Teste que procura o texto da linha na fonte não conta. A2 não devolve.
