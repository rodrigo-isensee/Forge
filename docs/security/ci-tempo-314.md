---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/ci-tempo-314
commit: 65f402e7c65349036c36c9c769c77f6a09b0ffff
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v0457

## Achados

## Sondas

## Gatilhos
Controle do Forge: workflow em `.github/workflows/ci.yml` (`R-SEGURANCA`). Custo: `R-CUSTO`. Etapa E23.14 (CI-TEMPO-314), diff d3453407..65f402e7.

## Detalhe dos achados
Diff conferido (3 arquivos, +6/-4): em `.github/workflows/ci.yml` mudam só dois valores de `timeout-minutes`, linha 37 (job `rapida`) e linha 79 (job `rapida-quatorze`), de 20 para 30, e a linha 37 ganha um comentário. Nenhum `on:`, `if:`, `permissions:`, `concurrency:`, `continue-on-error`, passo, nome de job, ação ou segredo foi tocado; as ações seguem fixadas por SHA e o checkout segue com `persist-credentials: false`.
Permissões e segredos: o topo do workflow segue `permissions: contents: read` (linhas 24-25) e os dois jobs não pedem permissão própria nem leem `secrets.*`.
Gatilhos e janela de abuso: os dois jobs só rodam em `push` na `develop` (linhas 34 e 76), isto é, depois do merge de código já revisado; nenhum job disparado por `pull_request` de terceiro muda de teto. Um autor de PR não ganha minutos a mais de runner com esta mudança. `concurrency` com `cancel-in-progress: true` segue limitando a uma execução por ref.
Prova da promoção: os nomes dos jobs não mudam, então `JOBS_DE_PROVA` em `scripts/arvore-testada.py:29` segue casando; job cancelado ou vermelho continua sem prova, e a suíte roda inteira na promoção (falha fechado). O teto maior não cria verde sem suíte: só evita o cancelamento que hoje tira a prova do 3.14.
Custo: o teto só limita o pior caso; o acréscimo máximo é de 10 min por job por push na develop, em runner hospedado, sem serviço pago novo (`R-CUSTO`).
Teste: `tests/test_catraca.py:3322` ancora a lista inteira de tetos na ordem dos jobs (`30, 30, 45, 5, 20, 20, 15, 5, 5, 5, 20, 20, 5`), igual às 13 ocorrências do workflow no head; a classe `Workflows` do arquivo tocado roda 6 testes, OK.
Fragmento `changelog.d/ci-tempo-314.md`: sem dado sensível.
Observação fora de segurança (ao `tech-lead`, não bloqueia): o comentário da linha 37 diz "medido 13-20 min (3.12)", e a medida do autor no pedido é 12,7 a 15,7 min.
PA-7 (`docs/engineering/achados-recorrentes.md`) conferido: nenhum dos AR-1 a AR-12 se aplica a valores numéricos de teto de tempo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As ferramentas de varredura de workflow e de segredos não estão no PATH deste ambiente (lacuna registrada; elas rodam no CI); a mudança é só de valores numéricos e foi revisada por leitura.
