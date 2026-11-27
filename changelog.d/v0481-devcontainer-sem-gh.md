### Corrigido
- devcontainer: o postStartCommand roda o preparo da cópia presente em /workspaces/Forge (sem clonar a main com o gh), o preparo cria ~/.config/gh primeiro e sai com rc 1 e uma linha `erro:` se faltar gh, tmux, ~/.config/gh ou o link ~/.forge-contrib; acabou o `; true` que engolia a falha (v0481 E35.1)
