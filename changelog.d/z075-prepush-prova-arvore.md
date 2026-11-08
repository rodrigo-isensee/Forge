### Corrigido
- PREPUSH-PROVA-ARVORE (versao-075, PP-4a, PP-4/C-1): com uma ref só, o `.githooks/pre-push` anota a prova (`.verde` ou `.dirigida`) apenas se a árvore do início e do fim da suíte é a árvore do commit enviado; um HEAD trocado durante a espera na fila deixa de gravar prova de uma árvore que não foi enviada (caso `reldev`). Com mais de uma ref, a regra de antes continua.
