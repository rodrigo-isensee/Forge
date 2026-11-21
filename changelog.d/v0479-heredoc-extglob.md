### Corrigido
- Hook `parecer` (HOOK-HEREDOC-EXTGLOB-E-CAIXA, v0478 E70.1): o corpo de heredoc só vira dado se o alvo de redireção não tem curinga estendido (`bin/@(ls)`, `bin/+(ls)`, `bin/!(cat)`) e não grava, sem caixa, o nome de um programa da chamada (`bin/LS` com `ls`); só aperta; premissa do shell em `docs/hooks.md`.
