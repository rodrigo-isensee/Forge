# AA1-01 - mescla verdadeira em JSON com objeto aninhado fica sem lastro
- Severidade: média (infla M1, não esconde afirmação falsa; contorno: ignorar)
- Responsável sugerido: dev do `forge-check` (cartão próprio; achado 1 da re-review)
- Ambiente: melhoria/anti-alucinacao-medicao-fix @ dab099a

## Passos para reproduzir
1. `python3 -I` carregar `bin/forge-check` e chamar `tem_lastro(("mesclado","120"), saida)` com `saida = '[\n {\n "number": 120,\n "author": {"login": "x"},\n "state": "MERGED"\n }\n]'`.
## Resultado esperado
True (prova de merge do PR 120).
## Resultado obtido
False. `merge_provado` usa `\{[^{}]*\}`, que não casa objeto com objeto dentro. Com `{"number": 120, "state": "MERGED"}` plano dá True.
## Evidência
Saída do script: `'PR #120 mesclado.' ... [False, True]` (mesclado, pr).
