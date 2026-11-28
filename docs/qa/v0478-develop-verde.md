---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-develop-verde
commit: 1bd10c54ed4cba5bb1c58f4c7e788276923b08b3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (develop verde, E16.3)

Escopo: o diff `82bb9e57..1bd10c54` tem três arquivos de dado: `tests/pesos-d4.json` (peso 7.4 do `test_indice_forge`), `tests/mutantes/v047-mapa-testes.json` (spec M8 alinhada à linha 302 de `bin/forge-testes`) e o fragmento de changelog. Não há código de produção. Sem suíte local: só os módulos tocados, com TMPDIR; a suíte inteira é do check-run `bateria` do CI.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Todo módulo de teste tem peso medido (`R-TETO`) | `test_pesos_do_ci`, `test_pesos_teto` | módulo sem peso no `pesos-d4.json` | passou (16 e 2 testes) |
| Spec M8 casa com a linha real e o mutante morre | `bin/forge-mutante tests/mutantes/v047-mapa-testes.json` | trecho `de` ausente da fonte | M1 a M8 `morreu` |
| Plano do hook leva o fecho de quem importa | `test_testes_tocados` (inclui `QuemImporta...plano_do_hook...`) | linha nova do plano (`teste_do_indice`) | passou (162 testes) |
| Módulo que ganhou peso segue verde | `test_indice_forge` | n/a | passou (19 testes) |

## Provas
- `python3 -I -m unittest discover -s tests -p test_pesos_do_ci.py`: `Ran 16 tests`, `OK`; `-p test_pesos_teto.py`: `Ran 2 tests`, `OK`.
- `-p test_testes_tocados.py`: `Ran 162 tests`, `OK (skipped=1)`; `-p test_indice_forge.py`: `Ran 19 tests`, `OK`.
- JSON dos dois arquivos de dado carrega (`json-ok`); `bin/forge-testes:302` traz o trecho `de` novo da M8.
- `bin/forge-mutante tests/mutantes/v047-mapa-testes.json`: `spec=b3804672...`, M1 `morreu` (erro), M2 a M8 `morreu`; a M8 aponta `bin/forge-testes:302`. Saída 0.
- Vermelho antes do verde: não se aplica, pois não há teste novo nem regra nova; a correção devolve a spec e o peso ao estado que os testes existentes já exigiam.
- Remoto: `origin/melhoria/v0478-develop-verde` = `1bd10c54`.
