---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ci-anotacao
commit: 3487d89164ca7a88c317a071707d168196fa08f3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA · anotação do CI calada pelo import do test_catraca (E137.12, PR #821)

Head 3487d891. Sem suíte local: a bateria inteira é o check-run `bateria` do CI do mesmo sha; aqui, só o módulo tocado, o vermelho antes do verde e o mutante. Diff: `scripts/suite-partes.py` (uma linha: `environ = dict(os.environ) if environ is None else environ`), um teste novo, a spec de mutante e o fragmento de changelog.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CI-ANOTACAO-CALADA (E137.2): módulo que tira `GITHUB_ACTIONS` no import não cala a anotação de tempos (verde) nem a de falha (vermelha) | `Brinquedo5.test_modulo_que_tira_github_actions_no_import_nao_cala_as_anotacoes` | 5 partes: 4 verdes com `::notice title=forge-tempos`, 1 vermelha com `::error title=forge-suite parte` | passou |
| Anotação só no CI e só com parte verde (regra existente) | `Brinquedo5.test_anotacao_de_tempos_so_no_ci_e_so_com_a_parte_verde` | sem CI, parte vermelha | passou (50 testes do módulo OK) |

Execução: `python3 -m unittest tests.test_suite_partes` da raiz, sem -I: `Ran 50 tests in 25.911s ... OK`.

## Vermelho antes do verde (R-QA)
`forge-testes --vermelho 0e59c446 --modulos test_suite_partes`:
```
vermelho: base=0e59c44642a8 head=3487d89164ca módulos=test_suite_partes (restrito por --modulos)
tests.test_suite_partes.Brinquedo5.test_modulo_que_tira_github_actions_no_import_nao_cala_as_anotacoes · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=49; prova (asserção)=1
```
Os 49 restantes já existiam e passam nos dois lados, como esperado. Nenhum teste cai no HEAD.

## Mutantes (R-QA)
Lista conferida contra o diff: uma linha de guarda mudada, um mutante (M1, a cópia do ambiente volta a ser o `os.environ`). `forge-mutante tests/mutantes/v0480-ci-anotacao.json`:
```
forge-mutante: pedido=v0480-ci-anotacao rev=3487d89164ca spec=1afba177c5bb65b1839b1049268a9708fdcc54cceebbc6739230147e5fa8fab5
M1 · morreu · scripts/suite-partes.py:483
```
Saída 0. `forge-mutante --cobertura --base 0e59c446`: sem condição mudada fora da spec, rc 0.

## Observação do CI
No momento da leitura, `bateria (pareceres)` e `catraca` constavam `fail` no run 45293171200/45293171197, o restante pendente; não consegui ler o log (cache do `gh` em sistema somente leitura). A falha de `pareceres` é compatível com a falta deste parecer; a de `catraca` não foi diagnosticada aqui. O parecer cita o check-run `bateria` do sha final como prova da suíte; se `catraca` seguir vermelho no head aprovado, volta ao autor.
