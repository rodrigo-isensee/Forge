---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-docs-pareceres
commit: 7d32017c69de41a8ef9e8d19cb8943c2fb0755d3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (melhoria/v047-docs-pareceres, E1.274)

## Parecer
Aprovado. O intervalo `origin/develop..7d32017c` (3 commits) entrega o que E1.252 pede: `forge-check docs` recusa no parecer o `pedido:` que não é id de `docs/pedidos/` (local ou na raiz de pedidos) nem `release-X.Y.Z`, e diz quando é o nome da branch, inteiro ou sem prefixo (PARECER-CAMPO-PEDIDO, PARECER-PEDIDO-NOME-DA-BRANCH); `forge-check docs <arquivo>` valida só os dados, todos no modo estrito, e a cópia fora da raiz com o critério da pasta do `tipo:` (FC-DOCS-CAMINHO); a mensagem da linha fora do formato no `## Achados` diz para omitir o bloco; o modelo de review diz o id do pedido e o parecer sem achados.

## Escopo lido
- `bin/forge-check`: `problema_do_pedido`, `documentos_dados`, `cmd_docs`, a mensagem em `achados_do_parecer`, o argumento `arquivos` do subcomando `docs`.
- `tests/test_forge.py` (classe `DocsPareceresPedidoECaminho`), `tests/mutantes/v047-docs-pareceres.json` e `-2.json` (M1 a M13), `templates/projeto/docs/reviews/_modelo.md`, `changelog.d/v047-docs-pareceres.md`.

## Checklist (regras de leitura que alcançam o diff)
- Faz o que o pedido manda, sem mais: sim. O pedido só é conferido no estrito (fora do delta, pareceres antigos passam: M11), e sem `docs/pedidos/` em nenhuma raiz não há o que conferir (M2), o que mantém o CI do Forge, sem a raiz de pedidos, como antes.
- Travessia: o id só procura `docs/pedidos/<id>.md` se casa `[A-Za-z0-9._-]+` (sem barra; M3, sonda `../pedidos/p1` no teste); `arquivo_existe` trata nome longo e NUL. Caminhos impressos passam por `caminho_impresso` (E7).
- Arquivo dado: só `.md` regular e legível; o resto vira violação, nunca exceção (M5, M6, M13). Dentro da raiz vale o caminho real e a pasta errada segue recusada (M7).
- Guardas: uma linha de guarda, um mutante (13, em dois arquivos de até 8). Teste de subprocesso limpa o ambiente e chama Python com `-I`.
- Commits limpos, Conventional Commits em português.

## Verificadores
- Suíte: sem PR ainda (o brief manda não abrir); o CI do PR decide. Vale o PQ do autor (E1.252: 13 mutantes mortos).
- Rodados aqui no 7d32017c: `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho` → `Ran 10 tests ... OK`; `bin/forge-mutante --processos 1 tests/mutantes/v047-docs-pareceres-2.json` → M9, M10, M11, M12, M13 `morreu`.
- Tamanho (M14): `bin/forge-check` 67+11 e `tests/test_forge.py` 104 somam 182 linhas, acima da orientação de 150; um comportamento só (o `docs` e o seu campo `pedido:`), sem `hooks/`.

## Achados
- A1 (recomendado) bin/forge-check:430 · Os avisos de `conferir_criterio` saem com o `rel` virtual (`docs/reviews/<nome>`) e não com o caminho dado, ao contrário das violações reescritas na linha 429; para a cópia fora da raiz, o aviso aponta um arquivo que não existe. Reescrever o prefixo também nos avisos.
- A2 (recomendado) bin/forge-check:412 · 182 linhas de código e teste passam do teto de 150 (M14): o corpo do PR precisa de `teto: excedido, 182 linhas, <motivo>`.
