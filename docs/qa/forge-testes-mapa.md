---
tipo: qa
contrato: 1
pedido: forge-testes-mapa
branch: melhoria/forge-testes-mapa
commit: c61752f3e4bc41175476e0a0208408d469e73702
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - mapa FORGE_CHECK do modo dirigido do forge-testes

Links: `docs/pedidos/forge-testes-mapa.md`, `docs/reviews/forge-testes-mapa.md`. Sem UX nem API; sem gatilho de segurança. Offline, só disco local (`R-CUSTO`).

## Resultados
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: mapa lista os 13 módulos que usam o forge-check | sonda A: só `bin/forge-check` alterado, `forge-testes --listar` | mapa completo, inclui `test_erros_no_brief` | passou: 13 módulos planejados |
| E1: teste isolado roda só ele | sonda B: só `tests/test_hooks.py` alterado | mapa não alarga o que não deve | passou: `dirigido (test_hooks)` |
| E1: `MapaDoForgeCheck` falha se módulo sai do mapa | sonda C: `test_pedido_fora` removido do mapa | módulo ausente | passou (falhou como devia): `faltam no mapa FORGE_CHECK` |
| E2: fragmento do changelog | suíte (`test_changelog`) | n/a | passou |
| Suíte inteira | `python3 -m unittest discover -s tests -q` | n/a | 1269 testes, OK (298 s) |
| Plugin | `scripts/validar-plugin.sh` | n/a | Validation passed |

Sondas feitas em clone em `$TMPDIR` (nada gravado na worktree). Vermelho antes do verde: a sonda C é o vermelho do `MapaDoForgeCheck` (9 faltantes no estado anterior, segundo o pedido). Sem mutação (stack Python sem ferramenta no Forge).

Observação (não bloqueante, já no review): o critério CITA é heurística; módulo que alcança o forge-check por caminho que ela não vê escapa do teste.

## Achados
