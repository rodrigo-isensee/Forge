### Corrigido
- Dois testes deixam de depender do ambiente: o `--simular` do preparar-estacao usa um `claude` falso (sem rede para API paga, R-CUSTO) e o caso `../../x.md` do `forge-check brief` roda com `cwd` controlado e alvo plantado, sem ler fora do clone.
- O teste do `--simular` do preparar-estacao fixa `NVM_DIR` no HOME falso (uma sentinela prova que o `nvm.sh` de fora do clone não é carregado) e usa um `dpkg-query` falso.
