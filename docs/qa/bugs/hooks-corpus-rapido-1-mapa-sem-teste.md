# hooks-corpus-rapido-1 - o mapa do bin/forge-testes que roda os 3 módulos novos não tem teste
- Severidade: média
- Responsável sugerido: tech-lead (autor da entrega)
- Ambiente: melhoria/hooks-corpus-rapido, 978d2d648ec19915cc3ac3b8d140669daa442cc5

## Passos para reproduzir
1. Em cópia descartável do head, tire ` + VOLTA_UNICA` de uma das linhas de `bin/forge-testes` (96, 100, 105 ou 106; uma por vez).
2. `CI=true python3 -m unittest tests.test_testes_tocados tests.test_pre_push_afetados`.

## Resultado esperado
Falha: o filtro dirigido do pre-push deixaria de rodar `test_hooks_volta_*` quando `hooks/*.py`, `stacks/*` ou `.claude-plugin/*` mudam, e `test_hooks` já não os cobre.

## Resultado obtido
`OK` nas quatro linhas (4 mutantes sobreviventes). Nenhum teste afirma que `VOLTA_UNICA` entra no plano; `tests/mutantes/hooks-corpus-rapido.json` não existe.

## Evidência
linha 96: OK; linha 100: OK; linha 105: OK; linha 106: OK (saída de `unittest`, 80+20 testes).
