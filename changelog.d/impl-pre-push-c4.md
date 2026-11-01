### Corrigido
- pre-push: a trava e a fila ficam em $HOME/.forge-contrib, dentro e fora do sandbox, sem recuo (as provas ficam onde estavam); todo teste que roda o hook usa HOME temporário. As worktrees abertas só usam a trava comum depois de trazer o hook novo.
