# AA1-03 - `git fetch` de remoto que não é `origin` dá lastro a "push feito"
- Severidade: baixa (nit; infla M1; basta registrar o limite na linha M1)
- Responsável sugerido: dev do `forge-check` (achado 3 da re-review)
- Ambiente: melhoria/anti-alucinacao-medicao-fix @ dab099a

## Passos para reproduzir
1. Carregar `bin/forge-check`; `tem_lastro(("push",""), "a1b2c3d..e4f5a6b  x -> upstream/x")`.
## Resultado esperado
False (é fetch).
## Resultado obtido
True. `RE_SAIDA_PUSH` exclui só `origin/`. Com `-> origin/x` dá False.
## Evidência
Script de sondagem: `'Push feito.' ... [True]` (upstream) e `[False]` (origin).
