---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.5
branch: melhoria/v0475-release-0475
commit: 74d6ccd9a74a1b7742ad4b89a289c1539c4a2797
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-18
---
# Review de devops: release-0.47.5

## Achados

## Detalhes
Aprovado. Entre a v0.47.4 e este head, `.github/` do próprio Forge não muda (`git diff --stat v0.47.4 HEAD -- .github/` sem linhas): `ci.yml`, `release.yml`, `catraca.yml` e `dependabot.yml` ficam como na v0.47.4. Não há mudança em `Dockerfile*`, `compose*` nem IaC. O único arquivo de pipeline que muda é o modelo de projeto `templates/projeto/.github/workflows/ci.yml` (novo, 94 inserções).

- Modelo de workflow do projeto: `permissions: contents: read` no topo e por job (o agregador `ci` com `permissions: {}`); `timeout-minutes` em todos os jobs (3, 15 e 2); `actions/checkout` fixado por SHA com a tag em comentário e `persist-credentials: false`; sem `pull_request_target`, sem segredo, sem `continue-on-error` nem `[skip ci]` (grep em `.github/workflows` e no modelo). `concurrency` por número do PR ou ref cancela a rodada obsoleta. A suíte roda só em PR e no push de `develop`, `homolog` e `main` (R-CUSTO). Entrada não confiável (`base.sha`, `head.sha`) passa por `env`, nunca interpolada em `run:`. O marcador `{{COMANDO_PRONTO}}` é substituído pelo `forge-init` com o comando da stack, não por entrada de terceiro.
- Pulo da suíte: o job `mudanca` só diz `so_documento=true` quando todos os arquivos alterados são `*.md` ou `docs/*`; sem base ou com erro de diff cai em `false` e a suíte roda. O agregador `ci` (nome fixo, `always()`) exige `success` em `mudanca` e, conforme a detecção, `skipped` só quando provado documento, senão `success` na suíte: pulado ou cancelado fora desse caso reprova (J11). Não escreve na `main` (R-MAIN).
- Aviso de minutos (`bin/forge-cota-ci`, E3.42): só leitura por `gh api` GET com o token que o `gh` já tem, sem escopo novo; o dono entra no comando impresso só se casar com o formato de login do GitHub; sem permissão ou resposta ilegível diz `não verificável` e o comando para o dono (rc 0); acima de 80% sai rc 1 com aviso e pede cartão de melhoria (`ci-cd`, "Tempo e dependências"). Sem rede além do `gh`, sem custo (R-CUSTO).
- Skill `ci-cd`: `ci-de-projeto-privado.md` ganha 6 linhas e o `SKILL.md` ajusta o texto; sem afrouxar regra.
- Promoção e release: `plugin.json` na 0.47.5 e a entrada `[0.47.5]` no topo do `CHANGELOG.md`, abaixo de `[Não publicado]` vazio. A promoção segue `develop` → `homolog` → `main` pelo `tech-lead`; o merge na `main` é do dono (R-FLUXO, R-MAIN, R-CONFORMIDADE: não alterei proteção nem checks por `gh api`). `release.yml` não muda: dispara em push na `main`, o job que publica tem `needs: testes` e `contents: write` só para tag e release, e cria `v0.47.5` apenas depois do merge do dono.
- Checks exigidos: nenhum nome de job do `ci.yml` do Forge muda, então a proteção de branch não precisa de ajuste. Para projetos, o check a exigir é o `ci` do modelo, configuração do dono.
- Ferramentas: `git diff`, `grep`, leitura do código; `actionlint` e `shellcheck` não estão no PATH (lacuna registrada). A suíte local falha por ambiente (sandbox: `/proc` e `gh`); a prova da validade do YAML e dos testes é o CI do PR.

## Custo e rollback
Sem recurso pago novo (R-CUSTO). O CI do Forge não muda, então os minutos dele ficam iguais; o modelo de projeto reduz minutos nos projetos (sem suíte em push de branch de trabalho nem em mudança só de documento). Medir na checagem de tempo da release (`gh run list`). Volta: reverter o commit de versão na `develop` antes da promoção; depois da release, reimplantar a tag anterior (v0.47.4).
