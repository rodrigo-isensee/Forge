### Alterado
- forge-mutante aceita várias specs do mesmo pedido na linha de comando (tests/mutantes/<pedido>-<n>.json), cada uma com o teto de 8 mutantes, sem id repetido entre elas; uma spec inválida barra todas antes de rodar (MUTANTE-TETO).

### Corrigido
- forge-mutante aceita id de teste com letra não ASCII (def test_ação): cada parte depois de tests. é um identificador Python (str.isidentifier), e parte que começa por dígito passa a ser recusada (MUTANTE-ID-ASCII).
