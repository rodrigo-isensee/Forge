---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.0
branch: melhoria/release-0.47.0
commit: 72bb40084ec4b32d979dbbd8ba7379934aa5d055
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-13
---
# Review de devops: release-0.47.0

## Achados
- A1 (recomendado) scripts/verificar-contribuicao.sh · a troca `${texto//\/home\/runner\//@}` apaga todo `/home/runner/` antes da regex de caminho pessoal, então um caminho pessoal literal com esse prefixo passaria; o risco é baixo (o usuário real de um projeto não se chama runner), mas vale um teste que fixe o limite.
- A2 (recomendado) .github/workflows/ci.yml (job `pareceres`) · o comentário diz "promoções ficam fora do job", mas o job roda em todo `pull_request`, inclusive `homolog` e `main`; o comportamento é o mesmo do passo anterior (o script trata a promoção por `--base-ref`), só o texto engana.

## Detalhes
Aprovado. Release 0.47.0: head da branch revisado em 72bb4008 (develop em befd4cca contra main em 5f83b58d; 186 arquivos). Em `.github/` mudou só `workflows/ci.yml` (32 inserções, 8 remoções); `release.yml`, `catraca.yml`, `dependabot.yml` e `templates/projeto/.github` não mudaram. Não há `Dockerfile*`, `compose*` nem IaC no diff. Depois do Revisar-sha a branch recebeu só commits de pareceres (`docs/qa`, `docs/reviews`, `docs/security`), sem código.

ci.yml:
- CI-CHANGELOG-BASE: a base do `conferir` passa a ser `git rev-parse HEAD^1` (ponta atual da develop no merge commit do checkout), sem interpolar entrada do evento em `run:`; remove o `env: BASE` com `base.sha` velho.
- CI-PARECER-NAO-BARRA-SUITE: o passo de pareceres virou o job `pareceres`, com `if: pull_request`, `timeout-minutes: 5`, `permissions: contents: read`, checkout com `persist-credentials: false` e as mesmas ações fixadas por SHA já usadas nos outros jobs (checkout v4.4.0, setup-python v7.1.0). Entradas não confiáveis (`head_ref`, `user.login`) chegam por `env`, nunca interpoladas no script. Roda o `catraca.py` da base, quando existe.
- Agregador `bateria`: `needs` agora inclui `pareceres`, com `always()`. Em PR exige `success`; `skipped` só é aceito quando o evento não é `pull_request`, caso em que o job não existe. Então parecer faltando continua reprovando o check exigido, e pulo em PR não vira verde. Os demais resultados (passos, verificações, partes, pulados) seguem exigidos em `success`.
- Efeito: `pareceres` não está em `needs` das partes nem de `verificacoes`, então a suíte roda inteira com parecer faltando e o autor vê tudo numa rodada.

release.yml: inalterado; só roda em push na `main`, depois do merge do dono (R-MAIN). `plugin.json` 0.47.0 e `## [0.47.0] - 2026-11-13` no CHANGELOG batem.

`scripts/verificar-contribuicao.sh`: duas linhas mudam (ver A1); shellcheck limpo.

R-CUSTO: um job a mais, no mesmo runner `ubuntu-26.04`, sem cache, artefato nem serviço novos; fica dentro da franquia. R-VERIFY: nenhum `continue-on-error`, `[skip ci]` nem check desligado. R-CONFORMIDADE: nada de proteção de branch, ruleset, segredo ou environment alterado; o check exigido continua sendo o agregador "bateria", e o novo job entra por ele.

Ferramentas: shellcheck rodou limpo. `actionlint` e `zizmor` não estão no PATH (lacuna; o CI os roda no job `bateria`). Leitura manual do YAML e conferência de `needs`, `permissions` e SHAs. Sem PR aberto para este head, o CI do PR não foi consultado; a suíte inteira roda só no CI.

## Custo e rollback
Sem custo novo. Volta: reverter o PR da release na `main` (revert do merge) e republicar a versão anterior; o workflow de volta é o `ci.yml` da v0.46.0, sem migração.
