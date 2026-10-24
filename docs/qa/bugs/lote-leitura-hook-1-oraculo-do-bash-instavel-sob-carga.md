# lote-leitura-hook-1 - oráculo do bash (`rodar_no_bash_do_t9b`) falha de forma esporádica sob carga (ETXTBSY)
- Severidade: média
- Responsável sugerido: forge:tech-lead (código de teste do lote; sem código de produção)
- Ambiente: e8b2af94d1e21a16899980910665d50e20404b2e, bash 5.3.9, Python 3.14.4, 8 CPUs, WSL2

## Passos para reproduzir
1. `cd ~/.forge-contrib/wt/wt-qa-lote-leitura-hook`
2. Quatro cópias ao mesmo tempo: `python3 -m unittest discover -s tests -p test_hooks.py -k test_g1_esta_na_classe -k test_divisao_esta_na_classe` (a máquina com carga ~9).
3. Sozinho, o par passa (5 de 5 seguidas); em paralelo, 3 de 4 cópias falharam; numa 2.ª sonda (4 cópias, `subprocess.run` instrumentado) 3 execuções do bash voltaram rc 126.

## Resultado esperado
O oráculo roda o texto no bash e a sentinela aparece no registro, com ou sem carga.

## Resultado obtido
`AssertionError: ('git', ['push', 'origin', 'SENTINELA:main']) not found in [] : o bash não roda a sentinela em "sudo env --split 'timeout\\_5\\_sh' -ec '…'"` (e o equivalente em `test_g1_esta_na_classe`: `exec b''ash -''lc '…'`). Causa provada: o stderr do bash, descartado pelo teste, é `…/env: /usr/bin/bash: bad interpreter: Text file busy` (ETXTBSY). As threads do `ThreadPoolExecutor` gravam e dão `chmod` nos registradores enquanto outra thread faz `fork`, e o filho herda o descritor de escrita aberto; o `exec` do script recém-gravado falha, nada é registrado e o teste acusa "não roda a sentinela" como se o gerador estivesse errado. O teste não olha o rc nem o stderr. O autor já viu a mesma falha duas vezes hoje no pre-push (histórico do RET-LEITURA-HOOK-E, 13:38).

## Evidência
Logs em `$TMPDIR/qa-engineer-lote-leitura-hook/`: `par-1.log` a `par-4.log` (falhas), `sonda2-1.log` a `sonda2-4.log` (stderr com "Text file busy"), `rep-1.log` a `rep-5.log` (sequencial, todas OK).

## Contorno
Rodar o teste sozinho. Correção sugerida (não feita pelo QA): criar todos os registradores antes de abrir as threads, ou repetir a execução quando o rc for 126 com "Text file busy", ou conferir rc e stderr e falhar com a causa real.

## Estado
Fechado em 1b4b0d8 (caminho 1 do lote): 20 de 20 cópias em paralelo sob carga 14,7 passaram; ver docs/qa/lote-leitura-hook.md.
