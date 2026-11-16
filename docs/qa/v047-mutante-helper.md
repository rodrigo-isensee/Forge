---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-helper
commit: 4d2a9b7d93fa8b929cddf36da9fe4b80a5d84759
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 (E2.112, lote MU1, helper de teste na --base do forge-mutante)

Escopo: `git diff bf475209..4d2a9b7d` (`bin/forge-mutante`, `tests/test_forge_mutante.py`, duas specs de mutantes, fragmento de changelog). Obrigação: `test_*.py` importado por outro teste e `.py` de `tests/mutantes/` contam como apoio de teste e põem todos os mutantes no diff (sondas S5 e S6, `R-QA`). Sem UX nem API: sem acessibilidade e sem E2E.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| S5: `test_*.py` importado por outro teste é apoio | `test_helper_em_test_py_importado_por_outro_teste_poe_todos_no_diff` | helper com nome de teste | passou; cai na base |
| S6: `.py` de `tests/mutantes/` é apoio | `test_py_de_tests_mutantes_poe_todos_no_diff` | `.py` x `.json` na mesma pasta | passou; cai na base |
| Formas de importação; `git grep` com falha não é "nada achado" | `test_test_py_importado_em_qualquer_forma_e_apoio_e_o_grep_que_falha_nao_e_nada_achado` | quatro formas de import, nome com prefixo parecido, entrada vazia, sha inválido | passou; erro na base |
| Spec e teste não importado seguem fora do apoio | `test_teste_e_spec_de_outro_mutante_nao_poem_todos_no_diff` (já existente) | spec `.json` | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_mutante.MutacaoDirigida`: 11 testes, OK, no head mesclado.
- Vermelho (manual, cópia em `$TMPDIR` com `bin/forge-mutante` da base `bf475209` e os testes do head): 2 FAIL e 1 ERROR, os 3 testes novos. `forge-testes --vermelho bf475209…` não deu veredito: estourou o prazo de 550 s na fila `R-TETO` (rc=124, sem veredito, não vale como vermelho); vale a prova manual, e o autor roda o comando.
- Mutantes: `forge-mutante` das duas specs (`--processos 2`), saída 0, todos morreram: MH-M1 a MH-M9 `morreu` (bin/forge-mutante:811 a 830).
- Cobertura: `forge-mutante --cobertura --base bf475209…` rc=0; 5 condições `coberta` (814, 825, 826, 827, 830) e 1 `isenta` (810, condição velha trocada por `apoio(a)`, ramos com MH-M3 a MH-M9). Nenhuma linha de guarda mudada sem mutante.
- Suíte inteira: não rodada localmente; vale o check-run `bateria` do CI do PR, que ainda não existe (sem PR neste pedido).
- Merge: o remoto avançou (`8bd62154`, só o parecer de segurança); trazido por merge, sem rebase.
