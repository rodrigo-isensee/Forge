### Corrigido
- O `scripts/promover-homolog.py` lê só os checks do evento `pull_request` do PR (`gh pr checks --json`): os do push da `develop`, no mesmo sha, não contam mais como a bateria do PR, e sem check do PR o script não diz "checks verdes" e imprime o merge com `--auto` e `--match-head-commit` (cartão PROMOVER-SEM-AUTO, promoção #371).
