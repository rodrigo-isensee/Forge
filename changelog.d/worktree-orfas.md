### Corrigido
- forge-fechar, passo 7: a lista do `git worktree prune -v` vai só ao log do fechamento (marca [prune]) e a tela mostra `registro: prune tirou <n> registro(s) de worktree órfã`, para centenas de registros órfãos não enterrarem a linha `limpeza: …`; prune que falha avisa com o código e o caminho do log (WORKTREE-ORFAS, F1).
