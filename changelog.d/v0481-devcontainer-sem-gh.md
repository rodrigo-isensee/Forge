### Corrigido
- devcontainer: o postStartCommand baixa o script de preparo da main pelo GitHub, sem o gh (clone raso anônimo, URL fixa) e sem rodar nada da cópia de trabalho como root; o preparo cria ~/.config/gh primeiro e sai com rc 1 e uma linha `erro:` se faltar gh, tmux, ~/.config/gh ou o link ~/.forge-contrib; acabou o `; true` que engolia a falha (v0481 E35.1, E35.6)
