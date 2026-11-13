---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.0
branch: melhoria/release-0.47.0-b
commit: 0867f7157f37ca5ea76ef31824cbb159c215086f
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-13
---
# Review de devops: release-0.47.0

## Achados
- A1 (recomendado) .github/workflows/ci.yml:552 · o job `pareceres` repete checkout e setup-python do job `bateria`; custo de poucos segundos por PR, aceitável pelo ganho de paralelismo e sem ação nova

## Detalhes
Aprovado no head 0867f715, contra origin/main. Único arquivo de domínio tocado: `.github/workflows/ci.yml` (PR 542, e CI-CHANGELOG-BASE; os demais PRs 541, 543 e 544 não tocam `.github/`, Dockerfile, compose nem IaC).
- Job novo `pareceres`: `permissions: contents: read`, `timeout-minutes: 5`, ações fixadas por SHA com a tag em comentário (as mesmas já usadas no arquivo; nenhuma ação sem SHA no arquivo), `persist-credentials: false`, sem segredo e sem token. Entradas não confiáveis (head_ref, autor) passam por `env:`, não por interpolação em `run:`. Sem `pull_request_target`, sem `continue-on-error`.
- Agregador `bateria`: `pareceres` entra em `needs`; passa com `success`, ou `skipped` só fora de `pull_request`; em PR o pulo reprova (falha fechada, `R-VERIFY`). O nome do check exigido não muda (`R-CONFORMIDADE`).
- Passo de changelog: base passa a `git rev-parse HEAD^1` (ponta atual da develop), sem interpolar entrada externa.
- Nenhum workflow escreve na `main` nem publica release (`R-MAIN`). Custo: runner padrão do GitHub, job de menos de 1 minuto, paralelo; sem serviço pago (`R-CUSTO`).
- Entrada 0.47.0: versão 0.47.0 em `plugin.json` bate com `## [0.47.0]` do `CHANGELOG.md`; os quatro fragmentos dos PRs 541 a 544 foram apagados e seus textos estão na entrada; `changelog.d/` só com o README; `[Não publicado]` vazio.
- Ferramentas: `actionlint` ausente do PATH (lacuna registrada; leitura manual do diff e `tests.test_ci_local`, 73 testes OK); `shellcheck` presente, não aplicado a blocos inline além da leitura. Sem PR aberto: sem CI do PR para citar; carga ~16 em 12 CPUs, só testes leves.

## Custo e rollback
Sem custo novo de dinheiro; um job leve a mais por PR. Volta: reverter o PR 542 (um arquivo) e reabrir o passo de pareceres dentro do job `bateria`; sem migração nem estado.
