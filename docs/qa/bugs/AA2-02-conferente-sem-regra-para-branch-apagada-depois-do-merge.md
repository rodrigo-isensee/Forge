# AA2-02 - `conferente.md` não diz como provar `push` quando a branch do PR já foi apagada
- Severidade: baixa
- Responsável sugerido: `forge:tech-lead` (agents/conferente.md)
- Ambiente: melhoria/anti-alucinacao-regras 6a63087; PR #122 (mesclado)

## Passos para reproduzir
1. `git ls-remote origin melhoria/anti-alucinacao-medicao-fix` (branch do PR #122, já mesclado).
2. `git ls-remote origin refs/pull/122/head`.

## Resultado esperado
O roteiro do modo `entrega` dá um comando que prove o push de entrega já mesclada.

## Resultado obtido
O tipo de prova `push` manda `git ls-remote origin <b>` igual ao head local: a saída é vazia (branch apagada), o que pela letra vira `não cumpriu`, um falso negativo. A prova existe em `refs/pull/122/head` (2251ad5, igual ao `headRefOid`). Só afeta conferência feita depois do merge; antes do review a branch existe.

## Evidência
`git ls-remote origin melhoria/anti-alucinacao-medicao-fix` -> (vazio); `git ls-remote origin refs/pull/122/head` -> `2251ad5116dea5e4c7447fbbb8ea056de37adbf9`.
