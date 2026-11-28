---
tipo: revisao-devops
contrato: 1
pedido: v0478
branch: melhoria/v0478-cobertura-c1
commit: 67ef9dfbfc2d252ed7d82a7bd34269b5801291db
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-18
---
# Review de devops: v0478

## Detalhes
Aprovado, sem achado. Mudança em `.github/workflows/catraca.yml` (diff de `origin/develop...67ef9dfb`) e no comentário de `.github/pull_request_template.md`.

- Injeção por `$GITHUB_ENV` (`catraca.yml:45`): o valor gravado é `$script`, que só pode ser `tests/catraca.py` ou `$RUNNER_TEMP/base/tests/catraca.py`. `RUNNER_TEMP` é do runner e o resto é literal do workflow; `BASE` é um sha de `git rev-parse` e não entra na variável. Título, corpo e nome de branch do PR não chegam a ela, e o corpo continua só em `env: PR_BODY`. Não há quebra de linha nem `VAR=` extra controlável por quem abre o PR. No passo seguinte a variável aparece entre aspas (`"${CATRACA_DA_BASE:-tests/catraca.py}"`), sem reinterpretação.
- Permissões: inalteradas (`contents: read`, `pull-requests: read`, `actions: read`; checkout com `persist-credentials: false`). Não há segredo novo nem `pull_request_target`; o passo de texto só recebe `PR_BODY`. A ação continua fixada por SHA.
- Custo (`R-CUSTO`): nenhum job nem passo novo; o mesmo job `catraca` roda os mesmos passos, no mesmo runner e nos mesmos gatilhos. Só muda qual script executa (o da base). O `concurrency` com cancelamento e o `timeout-minutes: 10` seguem. Zero minuto a mais esperado.
- Promoção: o passo de texto tem `github.base_ref == 'develop'`, então nos PRs `develop` -> `homolog` e `homolog` -> `main` ele é pulado, como antes (o passo de regras roda em todos e grava a variável sem efeito). Nos PRs para a `develop`, `HEAD^1` do merge commit é a base. O `--base` é aceito pelo argparse do script da base e do PR, então uma base antiga ignora o argumento sem erro. Sem `tests/catraca.py` na base (introdução), o fallback usa o do PR, como o passo de regras já fazia.
- O `bin/forge-check` carregado é o ao lado do script (`tests/catraca.py:1704`), portanto o da base quando o script é o da base, coerente com o comentário do passo.
- Observação sem ação: se o passo de regras falhar antes do `echo`, o passo de texto (que roda com `!cancelled()`) cai no `tests/catraca.py` do PR. O check já está vermelho nesse caso, então o PR não passa por essa via; não é achado.
- Template do PR: só comentário HTML, sem efeito de execução.
- Ferramentas: `actionlint` e `shellcheck` não estão no PATH deste ambiente (lacuna registrada); revisão por leitura do diff e do `catraca.py`. Sem suíte local, como pedido.

## Custo e rollback
Sem minuto de CI nem recurso novo. Volta: reverter o commit do `catraca.yml` (a variável some e o passo volta a rodar o `tests/catraca.py` do PR); por ser arquivo de `.github/`, o envio e o rótulo `afrouxa-regra` seguem o fluxo do dono.
