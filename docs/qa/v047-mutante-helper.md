---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-helper
commit: b3ade362ea6dd0b5a872a52a6d62086635f48f59
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 (E2.112, lote MU1, helper de teste na --base do forge-mutante)

Escopo: `git diff bf475209..4d2a9b7d` (`bin/forge-mutante`, `tests/test_forge_mutante.py`, duas specs de mutantes, fragmento de changelog). Obrigação: `test_*.py` importado por outro teste e `.py` de `tests/mutantes/` contam como apoio de teste e põem todos os mutantes no diff (sondas S5 e S6, `R-QA`). Sem UX nem API: sem acessibilidade e sem E2E.

Revalidação E2.541 (incremental): `forge-check parecer delta` de `4d2a9b7d` a `744e1dbd`, sem o que veio da develop, lista no domínio `bin/forge-mutante`, `tests/test_forge_mutante.py` e as specs `guarda-sem-mutante-7.json` e `v046-mutacao-bench-3.json` (realinhamento de M41, M19 e M20 à fonte, commit `78248550`). O review aprovou que o realinhamento mata as mesmas mutações; aqui se reexecutou o que o delta tocou. Os critérios e a tabela abaixo seguem valendo.

Revalidação E2.619 (incremental, head `f5638d71`): `forge-check parecer delta` de `52f0ce3e` a `f5638d71` lista no domínio só `tests/mutantes/v047-mutante-helper-2.json` (`linha_base` da isenta 810 para 918, A2 da segurança). Nenhum código nem teste mudou.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| S5: `test_*.py` importado por outro teste é apoio | `test_helper_em_test_py_importado_por_outro_teste_poe_todos_no_diff` | helper com nome de teste | passou; cai na base |
| S6: `.py` de `tests/mutantes/` é apoio | `test_py_de_tests_mutantes_poe_todos_no_diff` | `.py` x `.json` na mesma pasta | passou; cai na base |
| Formas de importação; `git grep` com falha não é "nada achado" | `test_test_py_importado_em_qualquer_forma_e_apoio_e_o_grep_que_falha_nao_e_nada_achado` | quatro formas de import, nome com prefixo parecido, entrada vazia, sha inválido | passou; erro na base |
| Spec e teste não importado seguem fora do apoio | `test_teste_e_spec_de_outro_mutante_nao_poem_todos_no_diff` (já existente) | spec `.json` | passou |
| Realinhamento de M41, M19, M20 (delta) | specs `guarda-sem-mutante-7` e `v046-mutacao-bench-3` | `de` único no arquivo do rev | M41, M19 e M20 `morreu` |

## Cenários e resultado real
- Cabeça de 1ª rodada (head `4d2a9b7d`): vermelho manual dos 3 testes novos (2 FAIL, 1 ERROR na base `bf475209`); `forge-testes --vermelho` estourou o prazo na fila `R-TETO` (rc=124, sem veredito). Os testes novos não mudaram no delta; o vermelho vale.
- Head `744e1dbd`: `python3 -m unittest tests.test_forge_mutante` (sem `-I`): 127 testes, OK, 111 s.
- Mutantes das duas specs do pedido (`v047-mutante-helper.json` e `-2.json`, `--processos 2`): saída 0, MH-M1 a MH-M9 `morreu` (bin/forge-mutante:919 a 938).
- Mutantes das specs realinhadas, uma a uma (pedidos diferentes não rodam juntos, rc=2): `guarda-sem-mutante-7` M40 a M47 `morreu`, rc=0; `v046-mutacao-bench-3` M16 a M20 `morreu`, rc=0.
- Suíte inteira: não rodada localmente (ordem do dono de 16/11); vale o check-run `bateria` do CI do PR, que ainda não existe (sem PR neste pedido).
- Merge: `git fetch origin melhoria/v047-mutante-helper` devolveu o mesmo `744e1dbd`; nada a trazer.
- Head `f5638d71` (E2.619): `bin/forge-mutante --cobertura --base 86ac0fcb`, rc=0; a isenta sai `isenta · bin/forge-mutante:918(base)`, e MH-M1, M3, M4, M5 e M9 cobrem as linhas 922 a 938. `python3 -m unittest tests.test_forge_mutante.ConferirTodas` (sem `-I`): 4 testes, OK. Delta sem mutante novo (só metadado da isenta); mutantes e suíte anteriores seguem valendo. Fetch devolveu o mesmo head, nada a trazer.
