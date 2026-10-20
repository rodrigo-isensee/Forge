### Adicionado
- O pre-push do Forge espera a vez por uma trava (flock) antes de rodar a suíte, para duas suítes não rodarem juntas na máquina (R-TETO); `.githooks/pre-push --status` diz se há suíte rodando.
- A trava do pre-push é aberta uma vez, só do próprio usuário e sem seguir link; no recuo para `$TMPDIR` e `/tmp` fica na subpasta `forge-<uid>` (modo 700); o `--status` só vale com um único argumento (um remoto chamado `--status` não pula a suíte) e o descritor da trava não vai para a suíte.
