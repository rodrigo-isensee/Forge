# AA1-02 - "200 OK" (HTTP) conta como afirmação de testes
- Severidade: média (infla M1; contorno: ignorar)
- Responsável sugerido: dev do `forge-check` (achado 2 da re-review)
- Ambiente: melhoria/anti-alucinacao-medicao-fix @ dab099a

## Passos para reproduzir
1. Carregar `bin/forge-check`; `afirmacoes_do_relatorio("Endpoint respondeu 200 OK.")`.
## Resultado esperado
Nenhuma afirmação de testes.
## Resultado obtido
`{('testes', '200')}`, sem lastro. A terceira alternativa de `RE_TESTES` (`\b(\d+)\s+OK\b`) não exige contexto de testes.
## Evidência
`'Endpoint respondeu 200 OK.' {('testes', '200')} [False]`
