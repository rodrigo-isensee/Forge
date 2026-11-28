### Corrigido
- O hook parecer deixa passar o desarme do merge automático (opção --disable-auto do merge de PR), que não mescla nada, sem pedir o forge-check pr verde; valor de outra opção, =false, --admin, --auto, grupo de opções curtas e o que vem depois de -- seguem como merge (HOOK-DISABLE-AUTO, v048 E13.2).
