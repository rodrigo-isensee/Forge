### Corrigido
- O mapa do `bin/forge-testes` roda o `test_hook_erro_libera` junto quando o `tests/test_hooks.py` muda: ele reaproveita o lote de `Hooks.executar_em_lote` e faltava em `REAPROVEITAM_O_LOTE`, o que deixava a develop vermelha (E1.204, v047).
