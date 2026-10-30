### Corrigido
- `forge-mutante`: o mutante declarado equivalente deixa de valer como prova: no `--cobertura`, a condição coberta só por ele sai `só equivalente` e dá rc 1; a spec só de equivalentes sem `testes` sai 2; o equivalente pode trazer `testes`, e o que eles matam é inválido (pedido COBERTURA-EQUIVALENTE, FM1, segundo PR).
