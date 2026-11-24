# G12a-01 - resumo de compactação gravado como fala do dono
- Severidade: alta
- Responsável sugerido: desenvolvedor do Forge (autor do G1.2a)
- Ambiente: melhoria/v0479-sieg-g1-gravar @ 2a0e4620

## Passos para reproduzir
1. Transcrição com um registro `type: user`, `isCompactSummary: true`, `isVisibleInTranscriptOnly: true`, sem `isMeta`, texto "pode mesclar a main 0.47.3" (texto do modelo, não do dono).
2. `forge-check autorizacao gravar --mensagem <uuid> --transcricao <arq> --ato merge-main --alvos versao:0.47.3 --pedido v0478`.

## Resultado esperado
Recusa (ADR 0018 item 4 exclui o que não é digitado pelo dono); nada gravado.

## Resultado obtido
`autorizacao: A-1 gravada · ativa (nenhum) · merge-main · versao:0.47.3`, rc 0; `autorizacao ler` a mostra ativa.

## Evidência
Reprodução local no head 2a0e4620; coincide com o achado A1 do review (`docs/reviews/v0479-sieg-g1-gravar.md`). Linha em `bin/forge_autorizacao.py:291`; a cópia em `hooks/vigia.py:301` tem a mesma falta.
