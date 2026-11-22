---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pesado-corrida
commit: eb2f9b9d51f38bb4c6810ad5c228aaf966bf5f66
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E89.2 (PESADO-CORRIDA-TRAVA-SOME)

## Parecer
Aprovado no head eb2f9b9d (base 37156f9c). Diff: `bin/forge-pesado` +10/-1 (dentro do teto H1), teste, spec de mutantes e fragmento do changelog.

- Escopo: `ler_trava` local converte só `FileNotFoundError` em trava livre; `PermissionError` e `ValueError` (JSON quebrado) seguem até o `except (OSError, ValueError)` do `main`, que sai 2. Faz o pedido, nem mais nem menos; `_comum.ler_trava` (usado pelo hook) não muda.
- Testes: `TravaQueSomeNaLeitura` injeta a corrida no `Path.exists` (determinístico, sem relógio) e afirma que a injeção ocorreu; o ramo de falha (permissão e JSON quebrado) tem teste de comportamento, mais o `test_json_ilegivel_sai_2` já existente.
- Ferramentas (R-REVIEW, sem refazer a suíte): `python3 -m unittest tests.test_forge_pesado tests.test_pesado_fila` com ambiente limpo: 28 testes, OK. `bin/forge-mutante tests/mutantes/v0478-pesado-corrida.json`: M1 morreu, M2 morreu (por erro do teste declarado sob o mutante). `--cobertura --base 37156f9c`: sem condição sem mutante; `--conferir`: trechos no lugar.
- Suíte inteira: fica no CI do PR (R-REVIEW); o test_hooks não lê este script.
