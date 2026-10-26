### Corrigido
- forge-fechar: a leitura da branch remota (passo 2, passo 2b e limpeza) passa por um ajudante único que só aceita a linha do `git ls-remote` com o nome inteiro; outra branch terminada em `/refs/heads/<ref>` não engana mais (LSREMOTE-EXATO)
- forge-fechar: entra na lista do shellcheck do CI e sai limpo (SC2034, SC2015 e SC2086 do passo 2b corrigidos; os pontos de partida viram lista) (SHELLCHECK-FECHAR)
- forge-fechar: a coluna 1 do `git ls-remote` tem de ser sha hexadecimal (40 ou 64); outra coisa é leitura que falhou (LSREMOTE-EXATO, segurança)
