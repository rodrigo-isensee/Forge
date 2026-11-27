---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: d0f41115599f182b8e57b6b7dcd78f529bdad70f
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: v0481-f6-arvore-envio (#932, F6), 1ª rodada completa

## Detalhes
- ci: d0f41115599f182b8e57b6b7dcd78f529bdad70f verde

Revisor que não é o autor. Diff lido: `.github/workflows/ci.yml` e `scripts/arvore-testada.py` (`--do-pr`).

Pipeline:
- `arvore-envio`: `if` só no push na `develop`; `permissions` mínimas (`contents: read`, `actions: read`, `pull-requests: read`); `timeout-minutes: 5`; ações fixadas por SHA; `persist-credentials: false`; token só no passo da prova, via `env:`, sem interpolar entrada não confiável em `run:`. O código que roda é o da `develop` já mesclada (nada de fork).
- `needs` e `if`: partes e teto de pulados dependem de `arvore-envio` e pulam com `provada == 'true'`; o agregador `rapida` (`always()`) exige `arvore-envio` em success e, com prova, as duas pulados; sem prova, as duas em success. Falha, cancelamento ou prova ausente reprova (falha fechada). O agregador só lê `needs.*.result`, não roda código da branch.
- Falha fechada no script: toda exceção de rede, HTTP ou JSON vira `provada=false` e a suíte roda inteira. A prova exige o run do `ci.yml` de `pull_request` ligado por `head_sha`, `head_branch`, número e lista de PRs do ramo, base `develop`, compare com a `develop` anterior e `bateria` único em success na tentativa mais recente. A remoção do `3.14` de `JOBS_DE_PROVA` é coerente: o job do 3.14 não existe mais e o `ci.yml` e o `release.yml` provam só com 3.12.
- `R-CUSTO`: runner e serviço gratuitos, leituras de API; o job economiza minutos ao pular a suíte. `R-MAIN`: nenhum workflow escreve na `main`. `R-VERIFY`: sem `continue-on-error`, `[skip ci]` ou teste pulado para ficar verde.

CI do `d0f41115` (run 45985000380): suíte (5 partes), passos, verificações longas, instalação e `árvore` verdes; vermelhos só `bateria (pareceres)` e `bateria` (esperam parecer) e `catraca` (espera o rótulo). Os jobs do push ficam pulados no PR, como esperado. O run do head atual `23a8853b` (só pareceres) ainda corria na leitura.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:36 · `actionlint` e `zizmor` ausentes na estação do revisor; não rodei os dois sobre o `ci.yml`. Quem instala é `scripts/preparar-estacao.sh`; o CI os executa.
