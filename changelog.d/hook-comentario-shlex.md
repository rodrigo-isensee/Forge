### Corrigido
- Hooks: o '#' só abre comentário no início de palavra, como no bash; colado a uma palavra (`echo a#; git push --force origin main`) não esconde mais o resto da linha das checagens, e a quebra de linha depois de um comentário volta a separar comandos (HOOK-COMENTARIO-SHLEX)
