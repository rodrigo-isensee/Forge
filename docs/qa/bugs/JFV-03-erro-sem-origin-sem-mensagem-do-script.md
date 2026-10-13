# JFV-03 - Sem origin no Forge, a falha vem do git sem mensagem do script

- Severidade: baixa (mensagem; a falha em si está correta: rc diferente de zero e nenhuma cópia parcial)
- Status: resolvido (6432242)
- Responsável sugerido: node-backend (script de infraestrutura `scripts/jarvis-forge`)
- Ambiente: branch `melhoria/jarvis-forge-vigente`, commit b51cd3a, Linux (bash), HOME temporário com um repositório git sem remote `origin`

## Passos para reproduzir
1. Criar `$HOME/Forge` como `git init`, sem remote.
2. Rodar `scripts/jarvis-forge --sem-tmux`.

## Resultado esperado
Mensagem do próprio script explicando que o `~/Forge` não tem `origin` (no mesmo estilo de `não consegui criar a cópia vigente`), com código de saída diferente de zero.

## Resultado obtido
Sai com código 2 e a única mensagem é `error: No such remote 'origin'`, vinda do git, sem indicar que é a cópia vigente que falhou. Não cria cópia parcial.

## Evidência
Saída do harness (cenário T9): `rc=2 err=error: No such remote 'origin'`. Causa: `origem="$(git -C "$HOME/Forge" remote get-url origin)"` está fora de um `if`, então o `set -e` encerra o script antes da mensagem própria.

## Resolução
Resolvido e verificado na revalidação do commit 6432242 (2026-10-13): cenário reproduzido com stubs e origin local, sem recorrência.
