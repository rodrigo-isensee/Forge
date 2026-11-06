---
tipo: revisao-devops
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: 84472bfa6c63406c46a6c86ce6353939a39a53dc
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-06
---
# Review de devops: versao-034 (E2.4, lote B)

## Parecer
Aprovado. Escopo: `git diff d9b26bb..84472bf -- .github` (ci.yml, catraca.yml, release.yml) e `git show --remerge-diff` dos 7 merges. Nenhum merge tem conflito em `.github/` (o remerge-diff é vazio nos 7), então não houve resolução manual nesses arquivos. A ordem dos merges (catraca-ramo antes de catraca-fork) não muda o resultado em `.github/`.

Por item que toca `.github/`:
- catraca-fork: ci.yml:226-227 passa `HEAD_REPO` e `BASE_REPO` por env (não por opção, tests/catraca.py:1198 explica); valor vem de contexto, não de texto livre do PR, sem interpolação em `run:`. Sem permissão nova.
- ci-comentario-rapida: só comentário no cabeçalho do ci.yml; sem efeito de execução.
- ci-env-argv0-v2: passo "env com -a" (apt `rust-coreutils`, link no `RUNNER_TEMP`, `GITHUB_PATH`) em `bateria-python-tres-quatorze` e em `bateria` (ci.yml:56 e 260). Falha fechado, sem `continue-on-error`; `bateria` o condiciona a `steps.gate.outputs.pesada`; `permissions:` não mudam (`contents: read`); sem segredo, sem ação de terceiros nova.
- ci-ubuntu-26: `runs-on` de 24.04 para 26.04 nos 4 jobs do ci.yml, no catraca.yml e no release.yml; nenhum 24.04 restante.
- catraca-ramo-cmd-pr, release-pr-so-parecer, lote-cilista-v2: sem alteração em `.github/`.

Soma: nenhum job novo, nenhuma `permissions:` ampliada, ações fixadas por SHA inalteradas, `concurrency` e `timeout-minutes` intactos, sem escrita na `main` (`R-MAIN`). Os dois passos do env rodam em paralelo (um por job), a ordem barato antes de caro segue.

Achados (todos recomendados, não bloqueiam):
1. ci.yml:56 e 260 · o mesmo bloco de ~20 linhas está duplicado em dois jobs; correção futura num só deixa o outro defasado · extrair para script em `scripts/` ou ação composta local · recomendado.
2. ci.yml:56 e 260 · `apt-get update` e install somam algumas dezenas de segundos por job em cada PR com bateria pesada; medir no primeiro run e registrar no checkpoint da release (`R-CUSTO`: sem custo extra, dentro da franquia) · recomendado.
3. A existência do rótulo `ubuntu-26.04` e do pacote `rust-coreutils` no runner só se prova no primeiro run do CI; o passo falha fechado se faltar · recomendado.

Ferramentas: `shellcheck` presente, não aplicado ao YAML embutido; `actionlint` e `zizmor` ausentes do PATH (lacuna; o job de lint do próprio CI os roda); `docker build` não se aplica.

## Custo e rollback
Sem recurso pago nem runner maior (`R-CUSTO`). Rollback: reverter o merge do lote (runner volta a 24.04, passo do env some); `catraca.py` aceita as duas formas de env. Os pareceres de cada item seguem valendo.
