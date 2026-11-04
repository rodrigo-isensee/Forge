# e23-01 - teste de orçamento falha sob carga pelo prazo de parede do próprio hook
- Severidade: média
- Responsável sugerido: dev da stack (teste ou PRAZO_DA_LINHA_S do hook)
- Ambiente: wt/e23, a97ea35, load average ~6,7

## Passos para reproduzir
1. `python3 -I -m unittest discover -s tests -p test_hooks.py -k muitos_heredocs_recusam`, 5 vezes, máquina carregada.

## Resultado esperado
5 OK; o teste mede CPU e não depende da carga.
## Resultado obtido
Rodadas 1 e 4 falharam (e uma terceira no mutante) na forma `python3 - a{i}`: o hook recusou por "conferir dentro do prazo" (hooks/conformidade.py:729, `PRAZO_DA_LINHA_S = 3.0` em `time.monotonic()`), não por `.github/`. A forma custa 2,0 a 2,2 s de CPU, perto dos 3 s de parede.
## Evidência
/tmp/claude-0/e23-qa/est1.log e est4.log.

## Status
Resolvido em 09e0f13 (o lançador de teste alarga PRAZO_DA_LINHA_S); revalidado em 3 rodadas sob load 7 a 12, sem falha.
