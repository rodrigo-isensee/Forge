# v0480 - teste do prazo único é instável sob carga
- Severidade: média
- Responsável sugerido: autor do pedido v0478 (dev de shell/Python do Forge)
- Ambiente: melhoria/v0480-seg-quarentena-fechar @ 3820b484

## Passos para reproduzir
1. Com a máquina carregada, rodar `python3 -I -m unittest discover -s tests -p test_fechar_checks_do_head.py -k test_espera_do_passo_4`, ou `bin/forge-mutante tests/mutantes/v0480-seg-quarentena-fechar.json` várias vezes.

## Resultado esperado
Verde sempre; VU4 `morreu`.

## Resultado obtido
Falha ocasional: o passo 4 esgota `--espera 1` e para antes do passo 6 ("o check exigido catraca não passou ... ausente após 1s"); VU4 sai `controle vermelho` (rc 2) em 2 de 4 rodadas.

## Evidência
Isolado: 1 falha em 6 execuções (load average 19); mutante: 2 de 4 rodadas sem veredito.
