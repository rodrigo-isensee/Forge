---
tipo: revisao-devops
contrato: 1
pedido: release-0.46.0
branch: melhoria/release-0.46.0
commit: 2e45133689fbddb381d134637cc1e5c6569e8b75
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-12
---
# Review de devops: release-0.46.0

## Achados
- A1 (recomendado) .github/workflows/ci.yml:567 · o job verificacoes usa `needs.bateria.outputs.pesada != 'false'`: saída vazia roda os passos (falha para o lado seguro), mas só o ci-local exercita esse caso; vale um teste que prove a saída ausente.

## Detalhes
Aprovado. Release 0.46.0: develop em 2e451336 contra main em 4099658f (485 arquivos). Em `.github/` mudou só `workflows/ci.yml` (66 inserções, 24 remoções); `release.yml`, `catraca.yml`, `dependabot.yml` e `templates/projeto/.github` não mudaram.

ci.yml (A18): o job `bateria (passos)` ficou só com os passos baratos e exporta `pesada`; o passo "Nada pula degrau" subiu para logo depois do lint, sem mudar o texto. Novo job `verificacoes` (needs `bateria`) leva Provas, shellcheck e e2e, com checkout `persist-credentials: false`, `permissions: contents: read`, `timeout-minutes: 20`, ações no mesmo SHA já usado nos outros jobs, CLI instalado antes de código da branch (CI-ORDEM-LINT). Partes 3.12 e 3.14 passam a exigir `bateria`: passo barato vermelho pula as partes, e os agregadores (`always()`) reprovam o job pulado, então o check exigido não fica verde por pulo. O agregador "bateria" agora exige `verificacoes`; o do 3.14 depende de `partes-quatorze`, que depende de `bateria`, e cobre o caso. Timeout dos jobs de prova da develop de 20 para 30 min, com medida citada no comentário (13-20 min no 3.12; 3.14 cancelado no teto em 3 runs): dentro da franquia, sem runner maior.

release.yml: inalterado e correto. Dispara em push na `main`; `permissions: {}` no topo; `testes` com `contents: read` e `actions: read`; `release` com `contents: write` só para `gh release create` com tag `vX.Y.Z` lida de `plugin.json`, notas do CHANGELOG, `--target $GITHUB_SHA`, e sai sem erro se a tag já existe. Só roda depois do merge do dono na `main` (R-MAIN). `plugin.json` 0.46.0 e `## [0.46.0] - 2026-11-12` no CHANGELOG batem.

Scripts de CI e instalação: `scripts/suite-paralela.py` (tempo ao vivo em stderr, lista de testes caídos no resumo, sem rede), `scripts/suite-partes.py`, `scripts/conferir-reversao.py`, `scripts/verificar-contribuicao.sh` (regex de caminho pessoal ampliada para `/home` e `/Users`); `bin/` novos sem chamada de rede nem serviço externo. `tests/e2e-instalacao.sh` e a instalação não mudaram.

R-CUSTO: nada novo custa dinheiro; mesmo runner `ubuntu-26.04`, sem cache nem artefato novos, sem serviço externo. Um job a mais roda em paralelo às partes e não soma minutos de forma relevante (e passo barato vermelho agora economiza as partes).

Ferramentas: shellcheck rodou limpo em `scripts/verificar-contribuicao.sh` e `bin/forge`. `actionlint` e `zizmor` não estão no PATH (lacuna; o CI os roda no job `bateria`). Leitura manual do YAML (PyYAML ausente, sem parse automático) e conferência dos `needs`/`outputs`. PA-7 (`docs/engineering/achados-recorrentes.md`) conferido: nada aplicável a workflow nesta leva.

## Custo e rollback
Sem custo novo. Volta: reverter o PR da release na `main` (revert do merge) e republicar a versão anterior; o workflow de volta é o `ci.yml` da v0.45.x, sem migração.
