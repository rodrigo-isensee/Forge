### Corrigido
- `forge-fechar --limpar`: o clone da branch cujo origin difere só no `.git` ou na barra final é o mesmo repositório e entra na limpeza; o de outro origin fica pendente, com aviso e a leitura `git -C <clone> remote -v`, nunca em silêncio (v0478 E166.1).
