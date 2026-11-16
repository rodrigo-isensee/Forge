# v047-1 - quebra de linha no command neutraliza o hook sem acusar
- Severidade: alta
- Responsável sugerido: dev da stack do Forge (autor da catraca)
- Ambiente: melhoria/v047-catraca-hook-por-script, 66a3a9a4

## Passos para reproduzir
1. Em `tests/`, importe `catraca` e compare `script_do_hook({"command": "python3 x.py"})` com `script_do_hook({"command": "python3 x.py\nexit 0"})`.

## Resultado esperado
Chaves diferentes: o shell lê a quebra de linha como separador e `exit 0` troca a saída do hook (R-CONFORMIDADE: hook neutralizado é hook removido).

## Resultado obtido
Ambas `('command', 'python3', 'x.py', 'padrão')`: `str.split()` descarta a quebra de linha e `CONTROLE_DO_SHELL` (`tests/catraca.py:261`) não a tem. Idem `\r`.

## Evidência
Sonda manual no head 66a3a9a4. Falta caso em `Hooks` e sonda no corpus.

## Resolução
Corrigido em ee91a8f0 (`SO_ASCII_IMPRIMIVEL` em `termos_do_hook`, `tests/catraca.py:293`); coberto por `Hooks.test_command_lido_como_o_claude_code_o_roda` e pelo corpus. Revalidado no delta 66a3a9a4..ee91a8f0.
