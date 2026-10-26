### Alterado
- forge-mutante aceita várias specs do mesmo pedido na linha de comando (tests/mutantes/<pedido>-<n>.json), cada uma com o teto de 8 mutantes, sem id repetido entre elas; uma spec inválida barra todas antes de rodar (MUTANTE-TETO).

### Corrigido
- forge-mutante aceita id de teste com letra não ASCII (def test_ação): cada parte depois de tests. é um identificador Python (str.isidentifier), e parte que começa por dígito passa a ser recusada (MUTANTE-ID-ASCII).
- forge-mutante recusa id de teste fora da forma NFKC (letra com acento combinado, largura cheia) e a spec com `testes` que não são texto vira "spec inválida"; mutantes declarados para as guardas novas e para a de "sem executor e sem tests/test_*.py" (MUTANTE-ID-ASCII, MUTANTE-TETO).
