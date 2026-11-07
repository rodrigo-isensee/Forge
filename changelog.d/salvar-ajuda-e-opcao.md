### Corrigido
- `forge salvar -h` e `forge salvar --help` mostram o uso sem salvar nada (também fora de um repositório); mensagem que começa com `-` (como `-m x`, `--amend` ou `--`) é recusada com código 2 e nada é salvo; traço no meio da mensagem segue valendo (SALVAR-AJUDA-E-OPCAO, versao-067).
