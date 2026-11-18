### Corrigido
- `bin/forge-mutante`: o mutante cujo teste declarado é pulado (`skipTest`, também num subTest) sai `sem veredito` (saída 2) com os IDs pulados, nunca `sobreviveu`; com pulo e os outros testes verdes, a linha diz "os que rodaram não o mataram", e o equivalente declarado com pulo não se confirma (DEFEITO-MUTANTE-PULADO-SOBREVIVE, v0478 E13.1).
