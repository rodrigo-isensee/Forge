# v047-pos-release-comentario-recuado - linha recuada com # no fim some calada
- Severidade: alta
- Responsável sugerido: devops-engineer
- Ambiente: melhoria/v047-pos-release @ fb7dccb4, bash

## Passos para reproduzir
1. Arquivo de passos com `  padrao: d1 # x` e `  passo: p :: echo x # c` (recuadas) e um passo normal.
2. `ALVO=d1 scripts/pos-release ensaio <arquivo>`

## Resultado esperado
Recusa (valor padrão) ou os dois passos rodam; nunca pular em silêncio.

## Resultado obtido
rc=0, só o passo normal roda, `pos-release: OK · 1 de 1 passos`; o padrao recuado foi ignorado e o alvo padrão passou.

## Evidência
Linha 31 do script: o glob `[[:space:]]*'#'*` trata como comentário toda linha recuada com `#` em qualquer posição. Nenhum teste cobre linha recuada.
