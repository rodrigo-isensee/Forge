### Alterado
- Pesos da suíte do CI regravados em segundos reais, sem escala (a escala contornava o teto de 225 s por unidade): `Hooks.test_fixtures` e o T1 de variantes viram 4 fatias cada (mesmos casos, com teste de cobertura da união) e as classes de `test_selo_e_entrega` e `test_hooks` ganham chave própria (v0478 E102.4)
- O teste de cobertura do T1 passa a chamar o mesmo corte (`corpus_da_fatia`) das fatias, e um teste trava as constantes de fatias ao número de métodos `test_fixtures_fatia_*` e `test_t1_fatia_*` (v0478 E102.8)
