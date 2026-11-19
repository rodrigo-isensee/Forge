---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.9
branch: melhoria/v0478-release-0479
commit: d8794a474246c064546144ff60b7f52435d36d33
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-19
---
# Review de devops: release 0.47.9

## Detalhes
Aprovado. Diff da v0.47.7 até d8794a47 em pipeline, container e IaC: mudam `.github/workflows/ci.yml` (+24 linhas, #682), `.github/workflows/catraca.yml` e `.github/pull_request_template.md` (os dois últimos já na 0.47.8, parecer `docs/devops/v0478-release-0478.md`). Desde a 0.47.8 (829251d9) só o `ci.yml` muda. `release.yml`, `dependabot.yml`, `Dockerfile*`, `compose*` e IaC não mudam. Cada item já entrou na develop com o parecer próprio; o do `ci.yml` é `docs/devops/v0478-testes-prazo.md` (aprovado).

- `ci.yml`: quatro passos iguais (jobs da checagem rápida 3.12 e 3.14 e da suíte, nas duas partes de matriz) que só contam as linhas `PRAZO-CARGA fixture=` do `suite.log` e as escrevem em `$GITHUB_STEP_SUMMARY`. Sem entrada não confiável em `run:` (só `$RUNNER_TEMP` e `$GITHUB_STEP_SUMMARY`); sem segredo, sem ação nova, sem `permissions` novas, `timeout-minutes` e `concurrency` mantidos. `if: !cancelled()` (nos jobs da suíte, mais `provada != 'true'`, igual ao passo vizinho) faz o resumo sair também com a parte vermelha; o passo só conta e não decide o verde: a falha da parte vem do passo da suíte, sem `continue-on-error`, `[skip ci]` nem teste pulado (R-VERIFY). `|| true` cobre só o `grep` sem casamento (rc 1), que não é falha. Custo: nenhum run, runner ou artefato novo (R-CUSTO). Sem escrita na `main` (R-MAIN).
- Junção: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.9, igual ao `CHANGELOG.md`; entrada `## [0.47.9] - 2026-11-19` em português; `changelog.d/` só com `README.md` (sem fragmentos). Os itens juntos (122 arquivos desde a v0.47.7) não tocam container nem IaC. Promoção `develop` → `homolog` → `main` pelo `tech-lead`; a entrada na `main` é do dono (R-FLUXO, R-CONFORMIDADE: nada alterado pela API do GitHub).
- Ferramentas: `git diff`, leitura; `actionlint` e `shellcheck` não estão no PATH (lacuna registrada). A suíte local falha por ambiente (sandbox: `/proc` e `gh`); a prova de YAML e testes é o CI do PR.

## Custo e rollback
Sem recurso pago novo (R-CUSTO). Volta: reverter o commit de versão na develop antes da promoção; depois da release, reimplantar a tag anterior (v0.47.8).
