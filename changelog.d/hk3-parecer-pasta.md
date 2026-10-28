### Corrigido
- o hook parecer resolve a pasta do git como o git a resolve (cd, -C repetido, ~, variável): o pull --rebase de parecer e o git -C de outra worktree deixam de ser recusados, e o que o hook não resolve (variável desconhecida, pushd, --git-dir, GIT_DIR) é recusado em vez de julgado pelo cwd (HK3-PARECER)
