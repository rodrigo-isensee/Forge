# QA-AE12-1 - forge-fechar --cartao não move o cartão com o forge-check real
- Severidade: alta
- Responsável sugerido: dev do Forge (bin/forge-fechar, bin/forge_onde.py)
- Ambiente: melhoria/v0479-ae1-movimento-prova, 8bdb976e

## Passos para reproduzir
1. python3 -I -m unittest discover -s tests -p test_fechar_forge_check_real.py

## Resultado esperado
Cartão movido para Pronto com --prova pr:#N; código 0.

## Resultado obtido
FAILED (failures=1): "não movi o cartão", fim: código 3. O PR aberto pelo forge-fechar não cita o cartão, então a prova é recusada (ver review A1 e A2).

## Evidência
Saída do módulo acima; passa na base ed5bfa02.
