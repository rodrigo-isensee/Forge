### Corrigido
- Testes sem manutenção automática do git: ponto único em tests/ambiente_git.py (maintenance.auto, gc.auto, receive.autogc) em todo teste que roda git num repositório temporário, mais um teste que falha se um módulo de tests/ chamar git sem ele; some o erro de tearDown por maintenance.lock em worktree.
