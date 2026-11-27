---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-release-0-47-20
commit: 1e301536467df853dae1e7229952b930078c979d
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: release 0.47.20 (PR #935, main..1e301536)

## Achados
- A1 (recomendado) CHANGELOG.md:1 · o corpo do PR #935 da main não lista as 7 regras afrouxadas (#909, #918, #920, #928, #929, #931, #932) nem traz a saída de `tests/catraca.py --modo rotulados`; o tech-lead edita o corpo antes do merge do dono (R-FLUXO).
- A2 (recomendado) .github/workflows/ci.yml:1 · `actionlint` e `zizmor` ausentes nesta estação; não rodei os dois sobre `ci.yml`, `diario.yml` e `obsoletas.yml` (só `shellcheck` existe). Quem instala é o preparar-estacao.

## Detalhes
- ci: 1e301536467df853dae1e7229952b930078c979d verde

Escopo em `.github/` (main..head): `ci.yml` (reescrito), `diario.yml` (novo, #929) e `obsoletas.yml` (novo, #925). Nada em Dockerfile, compose ou IaC. Os três já passaram pelo parecer de devops de cada PR; aqui a leitura é da leva contra a main.

Checklist do pipeline, lido no diff:
- `permissions: contents: read` no topo dos dois arquivos novos. Escrita só em jobs próprios e mínimos: `issues: write` no job `cartao` do `diario.yml` (só `gh issue create` e `comment`) e `actions: write` no job `obsoletas` (só `gh run cancel`, protegido por `head.repo.full_name == github.repository`, sem fork). No `ci.yml` só entra `actions: read` onde se leem execuções.
- Ações fixadas por SHA com a tag em comentário (as mesmas SHAs do `ci.yml`); `persist-credentials: false` nos checkouts; `timeout-minutes` em todo job novo.
- Sem `pull_request_target`, sem `continue-on-error`, sem `[skip ci]`. Entrada não confiável (`head_ref`, SHAs, título) passa por `env:`, nunca interpolada em `run:`.
- `concurrency`: o `ci.yml` deixa de cancelar em PR (`cancel-in-progress: ${{ github.event_name != 'pull_request' }}`) e o `obsoletas.yml` cancela só run anterior do mesmo ramo, de outro sha e de id menor que o seu, poupando o envio só de parecer. Isso protege a linha `ci` do revisor sem custo extra.
- `R-MAIN`: o `diario.yml` roda na `develop` (`ref: develop`), com `schedule` e `workflow_dispatch`, sem escrever na `main`, sem merge e sem release. Não é check exigido nem entra em agregador.
- `R-CUSTO`: runner `ubuntu-26.04` como o resto do pipeline; o diário corta custo (suíte 3.14, instalação e mutantes saem do PR e rodam uma vez por dia; mutantes em fatia de 30 dias, `timeout` 60). Sem serviço pago nem artefato novo.
- `R-VERIFY`: nenhum check desligado; os pendentes de mutantes ficam fora por catraca que só encolhe, versionada.

As 7 regras afrouxadas (todas mescladas na `develop`, base do PR #935):
- #909 (pesos da suíte), #920 (hook estado), #928 (versão com 20 itens), #929 (F6, exceção de neutralidade no `diario.yml`), #931 (vigia) e #932 (árvore provada no PR) têm o rótulo `afrouxa-regra` e a justificativa no título. Só #929 e #932 tocam `.github/`; a exceção do #929 em `tests/config.json` é por arquivo (`diario.yml`), não global.
- #918 (ato rotulo-pelo-time) traz a marca no título, mas está sem o rótulo no GitHub agora; confira na saída do modo `rotulados` (A1) que a decisão do dono está declarada.

Prova de CI do head (`gh pr checks 935`, depois de esperar as partes 1 e 4 da suíte): verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `cancela runs obsoletos do PR`, `instalação (python 3.14)`, as 5 partes da suíte 3.12, `teto de pulados` e `árvore já provada na develop`. Também verdes `bateria`, `bateria (pareceres)` e `catraca`, que não contam como prova do parecer. Os jobs de push na develop e a cobertura aparecem `skipping`, como previsto. PR `MERGEABLE`.

Versão e `CHANGELOG`: conforme o corpo do PR, a 0.47.20 fecha 23 itens sem fragmento sobrando (`forge-changelog conferir-release` ok); a conferência mecânica é do CI.
