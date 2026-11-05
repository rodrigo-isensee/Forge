# L08-3 - a spec de mutantes lote-l08-e7b.json ficou velha: teste movido (controle vermelho) e mutante M36 equivalente
- Severidade: média
- Responsável sugerido: forge:tech-lead (tests/mutantes/lote-l08-e7b.json)
- Ambiente: melhoria/lote-l08 @ 5ac531f (a spec é a mesma desde 04437d1 e 1d50bea)

## Passos para reproduzir
1. Numa worktree limpa no head: `bin/forge-mutante tests/mutantes/lote-l08-*.json`.
2. Ler o fim da saída.

## Resultado esperado
rc=0, todos os mutantes mortos (PQ-2 do lote).

## Resultado obtido
rc=2: `M36 · controle vermelho · bin/forge-check`. Dois defeitos na mesma spec:
- a linha 13 cita `tests.test_fechar.FecharComOForgeCheckReal.test_com_a_conferida_do_head_fecha`, mas o commit 04437d1 moveu a classe para `tests/test_fechar_forge_check_real.py`; o teste citado não existe e o controle (código sem mutação) cai;
- com o caminho corrigido (spec de conserto numa cópia, só para diagnóstico), M36 `sobreviveu` (bin/forge-check:757): desde o commit 1d50bea o `pr_da_cli` e o `cmd_pr` já derivam a branch pelo sha (`branch_do_sha`), então o mesmo `or branch_do_sha(...)` dentro de `conferencia_do_head` ficou redundante (mutante equivalente) e a guarda real, em `pr_da_cli`, está sem mutante nesta spec. M37, M50, M51 e M52 morrem.

## Evidência
Saída da rodada sobre 5ac531f: 54 mortos, `M36 · controle vermelho`, rc=2. Com o caminho corrigido, na spec do QA: `M36 · sobreviveu · bin/forge-check:757`. Não corrigi: spec é do autor.
