# MP5-01 - Mutante M3 sobrevive (guarda S_ISREG sem teste)
- Estado: fechado em 105501f8 (M3 morre)
- Severidade: média
- Responsável sugerido: autor do pedido (hooks/testes)
- Ambiente: melhoria/v0475-mp5 @ e1be408b

## Passos para reproduzir
1. `forge-mutante tests/mutantes/v0475-mp1-mp7.json tests/mutantes/v0475-mp1-mp7-2.json tests/mutantes/v0475-mp1-mp7-3.json --base 88e9c58a6838e9b783cb4e6c5439a8fab26aabe0`

## Resultado esperado
M3 morre (teste `test_ativos_em_link_fifo_grande_ou_com_nomes_demais_nao_mede` cai com `if False:` em hooks/_comum.py:123).

## Resultado obtido
`M3 · sobreviveu · hooks/_comum.py:123`, rc 1. No head 88e9c58a morria; o `except OSError` novo (_comum.py:126) devolve None na leitura de pasta, então o teste passa sem a guarda.

## Evidência
Saída acima. Sugestão: teste com FIFO que tenha escritor e JSON válido de 2 nomes (deve dar None), ou declarar `equivalente` com justificativa que o QA aceite.

## Fechamento
No head 105501f8 o teste `test_ativos_em_fifo_com_escritor_e_json_valido_nao_vale` entrou no M3. `forge-mutante` das 3 specs `v0475-mp1-mp7*.json --base e1be408b`: `M3 · morreu · hooks/_comum.py:123`, M1 a M20 morreram, rc 0.
