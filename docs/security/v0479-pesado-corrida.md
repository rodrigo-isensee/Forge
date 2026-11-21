---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pesado-corrida
commit: eb2f9b9d51f38bb4c6810ad5c228aaf966bf5f66
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-pesado-corrida (v0478 E89.3)

Escopo: diff `37156f9c..eb2f9b9d` (PESADO-CORRIDA-TRAVA-SOME, E89.1): `bin/forge-pesado:51-62`, o fragmento de changelog, `tests/test_forge_pesado.py` (classe `TravaQueSomeNaLeitura`) e `tests/mutantes/v0478-pesado-corrida.json`. `hooks/pesado.py` e `hooks/_comum.py` não mudam.

## Gatilhos
Gatilhos: controle do Forge (fila de testes pesados do R-TETO, leitura da trava).

## Conclusão

**Classificação: só corrige; não afrouxa nem aperta.** O `forge-pesado` só lê o estado (docstring `bin/forge-pesado:6-8`; nenhuma escrita no arquivo). Antes, o arquivo que sumia entre o `exists` e a leitura (`hooks/_comum.py:2506-2508`) levantava FileNotFoundError e o `esperar` saía 2 (`bin/forge-pesado:117-119`); agora vale como trava ausente, o mesmo resultado que o `exists` falso já dava em `hooks/_comum.py:2506-2507`. O estado aceito como livre não ganha nenhum caso novo: só o resultado da mesma ausência observada um instante depois.

1. **Exclusividade da vez preservada.** Quem concede a vez é o hook: `hooks/pesado.py:394-409` e `:445-450` leem e gravam a trava sob `hook.trava()` e `_maquina.trava()` (flock) e a senha da fila nasce com `O_CREAT|O_EXCL|O_NOFOLLOW` (`hooks/pesado.py:103`) e flock exclusivo (`:105`). Nada disso muda. O `fim=livre` do `forge-pesado` é só aviso: o comando pesado que vier depois passa de novo pelo PreToolUse do hook, que relê a trava sob as travas e entra na fila se ela estiver ocupada. Duas execuções pesadas simultâneas continuam exigindo passar pelo hook, que não foi tocado.
2. **Ilegível e permissão negada não liberam.** O `except` pega só FileNotFoundError (`bin/forge-pesado:56`), subclasse exclusiva de ENOENT; PermissionError, IsADirectoryError e ValueError (JSON quebrado) seguem levantando e saem 2 por `bin/forge-pesado:117-119`. Provado pelo teste `test_trava_que_existe_e_nao_se_le_segue_levantando` (permissão e JSON quebrado) e pela sonda local de diretório no lugar da trava (IsADirectoryError, não libera). O mutante M1 (`except (OSError, ValueError)`) é morto por esse teste e por `test_json_ilegivel_sai_2`; o M2 (relevantar) pelo teste da corrida.
3. **Corrida coberta sem relógio.** `test_trava_que_some_entre_o_exists_e_a_leitura_pega_a_vez` injeta a remoção dentro do `exists` e confere que a remoção ocorreu antes de afirmar `fim=livre`.

Fora do diff, sem efeito no veredito: no Python 3.12 o `Path.exists` de `hooks/_comum.py:2506` já devolve falso em ENOTDIR (pai que vira arquivo), comportamento anterior a esta mudança e também de leitura só.

## Achados

## Sondas

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira não rodada localmente (brief: sem suíte local; vale o CI do PR). Rodado: `python3 -m unittest tests.test_forge_pesado.TravaQueSomeNaLeitura` (2 testes, OK) e a sonda de diretório/ENOTDIR em `ler_trava`. Varredura de segredos não aplicável ao diff (sem configuração nem credencial).
