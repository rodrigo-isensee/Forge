---
tipo: review
contrato: 1
pedido: workflows-auditoria
branch: melhoria/workflows-auditoria
commit: dd77d49
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: job `workflows` (actionlint e zizmor no CI)

Escopo: job `workflows` em `.github/workflows/ci.yml` e entrada do `CHANGELOG.md`, diff `origin/develop..dd77d49`.

## Verificado na prática
Trecho de download e checksum executado num diretório temporário, com os mesmos valores do job:
- Caso normal: as duas URLs baixam, `sha256sum -c` dá OK para os dois arquivos, a extração funciona e o job inteiro leva menos de 1 s de rede. `actionlint -version` mostra 1.7.12 e `zizmor --version` mostra 1.30.1.
- Caso adulterado (checksum do zizmor com os 4 primeiros dígitos trocados): `sha256sum -c` imprime `FAILED`, sai com código 1 e, por causa do `set -euo pipefail`, o script para antes do `tar`; nada é extraído nem executado.
- `actionlint -color` e `zizmor --offline --no-progress --min-severity medium .github/workflows` rodam sem achados sobre os três workflows atuais.

## Foco do pedido
- Checksum conferido antes de executar: sim, para os dois binários, e falha de verdade (provado acima).
- URLs fixas da release oficial: sim, `rhysd/actionlint` e `zizmorcore/zizmor`, `releases/download/v<versão fixa>`, versões e SHA-256 em `env` no topo do job.
- Código do PR com privilégio: não há. Os arquivos do PR são só dados de entrada das ferramentas; `contents: read`, `persist-credentials: false`, sem `secrets`, sem `pull_request_target`, sem expressão `${{ }}` dentro de `run` (as variáveis passam por `env`).
- Sem token: `zizmor --offline` dispensa `GITHUB_TOKEN`; nenhum segredo usado.
- Custo zero: runner padrão do GitHub, sem chamada de IA.
- Não trava PRs normais: duas baixadas pequenas, execução de segundos, sem dependência de API externa além do download de releases do GitHub.

## Achados
Bloqueia: nenhum.

Recomendado:
1. `ci.yml`, job `workflows`: sem `timeout-minutes`. Uma rede lenta no `curl` seguraria o runner até o limite de 6 h. Sugestão: `timeout-minutes: 5` no job (ou `--max-time 60` e `--retry 3` nos `curl`).
2. `ci.yml`, passo de download: `curl` sem `--retry`; uma falha transitória do GitHub derruba o PR com vermelho falso. Sugestão: `--retry 3 --retry-all-errors`.
3. A saída "2 ignored, 5 suppressed" do zizmor mostra que há achados de baixa severidade ou anotações `zizmor: ignore`; vale confirmar que nenhuma supressão foi acrescentada para passar e registrar o motivo das existentes. Não bloqueia.

Observação: a versão do CHANGELOG já está sob "Não publicado" e declara corretamente a exigência do rótulo `afrouxa-regra`, por mexer em `.github/workflows/`. A remoção do item "job `workflows`" das pendências está coerente.

## Parecer
**Aprovado.** Os itens recomendados podem entrar neste PR ou em seguida.
