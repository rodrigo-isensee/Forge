---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-filtro-k
commit: 704a60655e092b56eb3d2b7ac5c1745978c90ef7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: forge-testes-filtro-k (cartão 20, `-k`)

Escopo: opção `-k` de `bin/forge-testes` (TESTES-DO-ITEM-FILTRO). Os cartões 15 (sem mapa) e 19 (aviso do MAPA) têm parecer próprio nas branches deles. Suíte completa fica com o CI/pre-push (D-5); aqui rodou tests/test_testes_tocados.py.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| TESTES-DO-ITEM-FILTRO | CT-01 `-k Mapa`; `-k Mapa -k Sem` | 1 e 2 padrões | passou: 23 testes OK |
| TESTES-DO-ITEM-FILTRO | CT-02 `-k zzzz` | nenhum casa | passou: rc 5, NO TESTS RAN |
| TESTES-DO-ITEM-FILTRO | CT-03 `--vermelho -k Mapa` | combinação | passou: recusado, rc 2 |
| regressão | CT-04 tests/test_testes_tocados.py inteiro | n/a | passou: 94 testes, OK |

## Cenários e resultado real
`python3 -I -m unittest discover -s tests -p test_testes_tocados.py` em 704a606: 94 testes, OK. `-k` sem correspondência sai 5 (herdado do unittest), sem mensagem do forge-testes. Sem mutante declarado neste pedido (sem spec em tests/mutantes/).

Parecer: aprovado sobre 704a606.
