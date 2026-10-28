---
tipo: qa
contrato: 1
pedido: flaky-teto-lancador
branch: melhoria/flaky-teto-lancador
commit: b4bd24c39821e74ec66c4064a09c1f2499140aeb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: flaky-teto-lancador

Diff conferido contra a base b3791ed: só `tests/test_hooks_volta_lancador.py` (docstring e dois limites) e o fragmento `changelog.d/flaky-teto-lancador.md`; nada em `hooks/`, o revert 62e071a/d2970bd não deixa resto. Escopo do pedido (E1 a E3) intacto. PA-7: sem linha em `docs/engineering/achados-recorrentes.md`; o diff não traz classe repetida. Regra aplicada: PR-VERDE-D3-TEMPO (limite de 2x o p95 de 10 execuções, medido no runner; CPU, não relógio).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: limites a 2x o p95 do runner, nas duas versões de Python | conferência aritmética da medida do run 40756009076 | máximo 24,42 -> 24,5 ms; média 20,76 -> 20,8 ms (maior p95, 3.12) | passou |
| E1: docstring cita data, run e p95 | leitura do diff | n/a | passou |
| E1: o teste continua provando o teto K (K libera, K+1 recusa, custo em CPU) | `test_tempo_do_teto_das_leituras_do_lancador` | K e K+1 (asserções intactas) | passou |
| E1: o limite novo não deixa o runner lento reprovar | sonda com a medida do runner 3.12 (max 12,21 ms, média 10,38 ms) | acima do limite antigo, abaixo do novo | passou |
| E2/E3: sem workflow novo, fragmento do changelog | diff | n/a | passou |

## Cenários e resultado real
- Medida do run 40756009076 (a linha vem do log lido pelo Jarvis, registrada no pedido; o `gh` do QA não leu o log, sem saída): `TETO-LANCADOR p95-max=12.21 p95-media=10.38 python=3.12.15` e `p95-max=5.35 p95-media=4.04 python=3.14.9`. Limites: 2 x 12,21 = 24,42 -> 24,5 ms; 2 x 10,38 = 20,76 -> 20,8 ms, arredondados para cima na primeira casa, a mesma regra nos dois. O 3.14 fica bem abaixo.
- Teste no head: `python3 -m unittest tests.test_hooks_volta_lancador.LancadorDaVoltaUnica.test_tempo_do_teto_das_leituras_do_lancador` -> `Ran 1 test ... OK`.
- Mutante (cópia em `$TMPDIR`, nunca a árvore): limites voltados a 15 ms e 10 ms, com `decidir_na_guarda` devolvendo a medida do runner lento (máximo 12,21 ms, média 10,38 ms): `AssertionError: 0.0104715 not less than 0.01 : o teto K gastou 10.5 ms de CPU por decisão` -> `FAILED (failures=1)`, o mutante morre. O HEAD, com a mesma medida, passa (`OK`). Prova: o limite de 10 ms reprova o runner lento; o novo não.
- Vermelho antes do verde: a mudança não cria teste novo, só reajusta limite de teste existente; a prova de que o limite antigo reprova no runner é o mutante acima (e as falhas #353 e #354 de 10,2 e 10,5 ms registradas no pedido). `forge-testes --vermelho` não se aplica (sem teste novo).
- Suíte completa: não rodada por mim, por instrução do brief (roda uma vez no pre-push; o autor registrou 2182 testes OK).
- Acessibilidade e E2E: não se aplicam (teste de tempo da fábrica).

## Riscos
- Os limites cobrem o p95 de 10 execuções; um runner mais lento que o medido ainda pode reprovar (limite 2x folga a regra do dono, não a elimina).
