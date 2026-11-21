### Corrigido
- Hook `conformidade`: o destino com `$(…)`, crase ou variável vale também pelo valor que o hook calcula por inteiro, com o `~` do começo como o do bash; `echo x >> "$(echo ~/.claude)/settings.json"` e `d=~/.claude; echo x >> "$d/settings.json"` passam a recusar (CONFORMIDADE-TIL-EM-SUBSTITUICAO, v0478 E80.1).
