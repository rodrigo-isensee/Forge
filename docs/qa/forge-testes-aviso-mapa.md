---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-aviso-mapa
commit: 7d20b39b7f9cc08666be45f5a34e1809cc748c1e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: forge-testes-aviso-mapa (cartão 19)

Escopo: aviso cedo do MAPA em `bin/forge-testes`, leitura por AST (MAPA-TESTES-AVISO-CEDO). Pilha sobre sem-mapa (aec5092). Suíte completa fica com o CI/pre-push (D-5); aqui rodou só tests/test_testes_tocados.py.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| MAPA-TESTES-AVISO-CEDO | CT-01 raiz descartável: teste com `RAIZ / "bin/forge-sugerir"` fora do MAPA | leitura real de bin/ | passou: avisa "lê bin/forge-sugerir, mas o MAPA não leva a test_zzz" |
| MAPA-TESTES-AVISO-CEDO | CT-02 teste que cita "bin/forge-sugerir" em argumento de subprocess.run e em valor de dict | citação, não leitura | passou: nenhum aviso |
| MAPA-TESTES-AVISO-CEDO | CT-03 mesmo CT-01 sobre a base (aec5092) | ausência do aviso antes | passou: base não avisa |
| regressão | CT-04 tests/test_testes_tocados.py | n/a | passou: 92 testes, OK |

## Cenários e resultado real
`python3 -I -m unittest discover -s tests -p test_testes_tocados.py` em 7d20b39: Ran 92 tests, OK. CT-01 a CT-03 rodados num clone descartável no scratchpad (rc 0; o aviso sai em stderr e não bloqueia). Sem mutante declarado neste pedido. Sem teste novo de QA (teto da branch).

Parecer: aprovado sobre 7d20b39.
