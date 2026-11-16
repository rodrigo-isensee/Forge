# v047-legado-jarvis-contagem - contagem do legado de agents/jarvis.md desatualizada
- Severidade: alta (derruba a bateria do CI e impede a entrada na develop)
- Responsável sugerido: tech-lead / autor da E2.315
- Ambiente: melhoria/v047-fala-e-decisoes, 14a29d8f

## Passos para reproduzir
1. `python3 -m unittest tests.test_forge -k nvariante -k Neutral -k Regra`

## Resultado esperado
15 testes OK.

## Resultado obtido
`test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` falha: `agents/jarvis.md: trecho novo em arquivo do legado sem regra e porque`.
`tests/config.json:696` `invariantes_sem_motivo["agents/jarvis.md"]` = 48; o arquivo tem 58 invariantes e 9 com motivo por trecho = 49.

## Evidência
Correção: trocar 48 por 49 em `tests/config.json:696` (o legado não cresce em relação à base: develop tinha 49).
