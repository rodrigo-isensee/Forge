---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/catraca-fork
commit: 5ad6373f37d21c727a1cf97f1f1c3a1256c62163
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: catraca-fork

## Gatilhos
R-SEGURANCA: CI (ci.yml) e catraca (tests/catraca.py). Fecha o A1 do parecer do catraca-ramo.

## Achados
- A1 (recomendado) tests/catraca.py:1106 · Os dois vazios liberam; em CI (GITHUB_ACTIONS=true) BASE_REPO vazio deveria recusar, para não depender de o ci.yml manter o env.

## Detalhe dos achados
Fork: o passo só roda em `pull_request` (ci.yml:188 e 204). Não há `pull_request_target`; `push` e `workflow_dispatch` pulam o passo, então os vazios não ocorrem ali. Com fork apagado, `head.repo` chega vazio e `github.repository` não, logo difere e recusa (testado). Os dois vazios exigiriam `github.repository` vazio, impossível no GitHub.

Injeção: os valores entram por `env:` e são lidos por `os.environ`, sem interpolação no shell; nomes de repositório só têm letras, dígitos, `.`, `-`, `_` e `/`.

Maiúsculas: os dois valores vêm da mesma API, em grafia canônica; o mesmo repositório compara igual. Divergência de caixa só recusaria (falha fechada), sem abrir caminho.

A1: um PR que remova o env do ci.yml volta aos vazios; o workflow vem do merge do PR, mas o passo roda o script da base. Baixa; correção mínima: recusar se `GITHUB_ACTIONS` e `BASE_REPO` vazio. Dono: software-engineer.

## Riscos aceitos e ferramentas
Nenhum. Rodei só a leitura do diff e os testes do arquivo tocado por inspeção; actionlint e zizmor não foram executados.
