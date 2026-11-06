---
tipo: revisao-devops
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: fb390efc8e6e3b27c4a1f18b5a22bfc997231cb3
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

## Revalidação das voltas do CI
Escopo: `git diff 237c130..fb390ef` (a evidência das falhas está em `/tmp/ci-455.log`). Na minha área o delta tem 3 arquivos: `.github/actionlint.yaml` (novo), `.github/workflows/ci.yml` (+8 -2) e o critério do `env_gnu` em `tests/apoio_volta_unica.py`. Não fui autor das voltas. Veredito: aprovado sobre `fb390ef`; os achados 1 a 3 do parecer anterior seguem como recomendações, e o 3 foi provado pelo CI (o rótulo `ubuntu-26.04` existe; o pacote `rust-coreutils` instalou).

- **Label no actionlint (7ec3a35).** O log mostra o job `actionlint` reprovando em 5 `runs-on: ubuntu-26.04` (catraca.yml:20, ci.yml:27, 46 e 98, release.yml:14), regra `runner-label`, porque o 1.7.12 fixado não conhece o rótulo. `.github/actionlint.yaml` declara só `ubuntu-26.04` em `self-hosted-runner.labels`, sem `ignore` nem regra desligada; o resto da checagem do actionlint segue ativo. O passo `actionlint -color` (ci.yml:171-173) não passa `-config-file`, e o actionlint lê `.github/actionlint.yaml` por padrão, então o arquivo vale sem mudar o job. O arquivo diz quando sai (quando a versão fixada trouxer o rótulo). Cabe anotar que o rótulo entra na lista de "self-hosted" só para o linter: o runner continua o hospedado e gratuito (`R-CUSTO`). Não afrouxa `R-VERIFY`: nada de `continue-on-error` nem check desligado. A mudança em `.github/` pede o rótulo `afrouxa-regra` do dono no PR (já previsto para o lote).
- **Pacote e passo novos (83b3e55).** `gnu-coreutils` entra no mesmo `apt-get install` do passo "env com -a" nos dois jobs (ci.yml:64 e 273): sem passo novo, sem job novo, sem ação de terceiros, sem segredo, `permissions:` e `timeout-minutes` intactos. Acrescenta um `apt` pequeno a cada bateria pesada, dentro da franquia gratuita (medir no checkpoint da release, como no achado 2). Pacote do repositório da própria distribuição, sem `curl | sh`.
- **Falha fechada.** O passo novo exige `gnuenv` no PATH (`command -v gnuenv`) e que `gnuenv --s 'echo a  b'` devolva `a b`; qualquer das duas falhas faz `exit 1` sob `set -euo pipefail`, sem `|| true`. O bloco continua duplicado nos dois jobs (agravo do achado 1: agora são ~24 linhas duplicadas; recomendado extrair para script, não bloqueia).
- **Critério do `env_gnu` e a falha do CI.** O CI reprovou `test_divisao_esta_na_classe` (`--split`, runner 26.04) porque o `env` do uutils 0.10.0 recusa as abreviaturas. O novo `env_gnu` procura `env`, `gnuenv` e `genv`, só aceita o que divide toda grafia de `OPCOES_DE_DIVISAO`, e reprova com a grafia recusada e o caminho quando só há env parcial (fb390ef), em vez de pular o teste. É coerente com o CI: o passo do workflow garante o `gnuenv` completo, e sem ele a bateria reprova, não pula (`R-VERIFY`). Programa local, sem rede. O código de teste é do QA e do review de código; aqui só conferi que o contrato com o passo do CI fecha.

Soma do delta: nenhuma `permissions:` ampliada, nenhuma ação nova, `concurrency` intacta, sem escrita na `main` (`R-MAIN`), sem custo (`R-CUSTO`). Ferramentas: `actionlint` e `zizmor` seguem ausentes do PATH (lacuna; o job de lint do CI os roda e a evidência do log é a do run anterior à volta, a nova só se prova no próximo run). Rollback: reverter os 3 commits das voltas devolve o estado julgado em `84472bf`, que já reprovava no CI; reverter só `actionlint.yaml` volta a reprovar o lint.
