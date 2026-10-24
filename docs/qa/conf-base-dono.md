---
tipo: qa
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: bc39b09e5066300e03db024c09f2a3c0c05762b5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: conf-base-dono (revalidação do delta da integração `09e6b3d..0bb2641`)

Código conferido: o de `0bb264163d0d60c5ef8d49cf376755964654a9cf` (o head `bc39b09` só soma o parecer do review). Escopo: só o delta que tocou `bin/forge-testes` e `tests/test_testes_tocados.py`; o QA anterior (`aa7d3d1`) não foi reaberto.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mudança só em `bin/forge-check` seleciona os 21 módulos de `FORGE_CHECK`, entre eles `test_conferencia_base_dono` | `Mapa.test_forge_check_roda_os_modulos_dele` | contagem exata 21 e seis módulos nomeados | passou |
| A lista `FORGE_CHECK` bate com os arquivos que importam ou executam o `forge-check` (sem faltar nem sobrar) | `MapaDoForgeCheck.test_mapa_lista_todo_modulo_que_usa_o_forge_check` | mínimo de 8 módulos; diferença vazia nos dois sentidos | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_testes_tocados tests.test_conferencia_base_dono`: 86 testes, OK.
- Conferência direta pelo `bin/forge-testes` da branch: `FORGE_CHECK` tem 21 entradas, sem repetição, e todas têm `tests/<módulo>.py`; `test_conferencia_base_dono` está na lista.
- Diff do delta: 8 linhas a mais e 5 a menos, só na tupla `FORGE_CHECK` e no teste que a vigia; nenhuma linha de guarda de `bin/forge-check`, `hooks/` ou `.githooks/` mudou, então não há mutante a declarar.
- Sem suíte completa (fica para o pre-push).
