### Corrigido
- Hook `conformidade`: a exceção de leitura da F6 (`so_leitura`) recusa a palavra que abre com `*`, `?` ou `[` e a que tem `{`, que o bash expande para um argumento `--pre=...` (R2 de docs/reviews/conformidade-leitura.md, K2-REC).
