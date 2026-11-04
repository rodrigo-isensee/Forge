---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/catraca-fork
commit: 838803f4c8da680b589f47f022aebe9c2e81e25b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: catraca-fork

## Gatilhos
R-SEGURANCA: CI (ci.yml) e catraca (tests/catraca.py). Fecha o A1 do parecer do catraca-ramo.

## Achados

## Detalhe dos achados
Fork: o passo só roda em `pull_request` (ci.yml:188 e 204). Não há `pull_request_target`; `push` e `workflow_dispatch` pulam o passo, então os vazios não ocorrem ali. Com fork apagado, `head.repo` chega vazio e `github.repository` não, logo difere e recusa (testado). Os dois vazios exigiriam `github.repository` vazio, impossível no GitHub.

Injeção: os valores entram por `env:` e são lidos por `os.environ`, sem interpolação no shell; nomes de repositório só têm letras, dígitos, `.`, `-`, `_` e `/`.

Maiúsculas: os dois valores vêm da mesma API, em grafia canônica; o mesmo repositório compara igual. Divergência de caixa só recusaria (falha fechada), sem abrir caminho.

A1 (fechado em 838803f): em CI com BASE_REPO vazio a catraca recusa; o teste do caso CI define GITHUB_ACTIONS por patch.dict, então a limpeza da variável na suíte não o mascara, e outro teste exige os dois env no passo e nenhum `${{` no run. Antes: um PR que remova o env do ci.yml volta aos vazios; o workflow vem do merge do PR, mas o passo roda o script da base. Baixa; correção mínima: recusar se `GITHUB_ACTIONS` e `BASE_REPO` vazio. Dono: software-engineer.

## Riscos aceitos e ferramentas
Nenhum. Rodei só a leitura do diff e os testes do arquivo tocado por inspeção; actionlint e zizmor não foram executados.
