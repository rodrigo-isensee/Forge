---
tipo: revisao-devops
contrato: 1
pedido: release-0.33.0
branch: melhoria/release-0.33.0
commit: c004a70a01459b483322b006a012bac382bb36e6
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-05
---
# Review de devops: release-0.33.0

## Parecer
Aprovado. Na leva contra a main 0.32.0, o único arquivo de `.github/` que muda é `release.yml` (#440). Em `templates/` mudou só `templates/projeto/.githooks/pre-push` (#436), sem Dockerfile, compose ou IaC. Ferramentas: `actionlint` não está no PATH (lacuna); li o diff e o arquivo inteiro à mão.

## Achados
- `.github/workflows/release.yml:26` · `python3 scripts/suite-paralela.py` troca o `unittest discover` em série, como no `ci.yml:36`, `:58` e `:238`; o script existe na árvore · sem defeito · informativo.
- `release.yml:15-16,21-23` · `timeout-minutes` sobe de 20 para 25 (a v0.32.0 estourou 20 min) e entra o `setup-python` com o mesmo SHA do `ci.yml` (v7.1.0, 3.12); `permissions: contents: write` e `persist-credentials: false` seguem · sem defeito · informativo.
- `release.yml:26-28` · a suíte roda antes de "Tag e release", então teste vermelho não publica; o gatilho segue `push` na `main` (`R-MAIN`), sem `continue-on-error`, `[skip ci]` nem check desligado (`R-VERIFY`) · conforme · informativo.
- `ci.yml:12,165-184` · `develop`, `homolog` e `main` rodam a bateria completa no PR, e o PR para a `main` exige versão nova e CHANGELOG fechado; a leva não altera esse arquivo · conforme · informativo.
- `.claude-plugin/plugin.json:3` · versão 0.33.0 bate com `CHANGELOG.md` `## [0.33.0] - 2026-11-05`; `changelog.d/` só tem o README; minor é coerente com a leva (feat e fix compatíveis, E3) · conforme · informativo.
- `release.yml:13-16` · recomendado: se a Release passar de 25 min de novo, medir `gh run list` no checkpoint e abrir cartão em vez de subir o teto de novo · recomendado, não devolve.

## Custo e rollback
Custo: runner `ubuntu-24.04` da franquia gratuita; a suíte paralela reduz os minutos da Release, sem recurso novo nem serviço pago (`R-CUSTO`). Rollback: reverter o #440 por PR (volta ao `unittest` em série e ao teto de 20 min), ou republicar a versão anterior pelo mesmo fluxo. A leva não tem migração de dados. O workflow cria a tag só se ela não existir, então a reexecução é segura.
