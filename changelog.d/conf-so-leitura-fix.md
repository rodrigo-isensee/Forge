### Corrigido
- O conferente passa a ser só de leitura também na sessão do Forge: `escrita_permitida` do papel em `hooks/conformidade.json` faz o hook avaliá-lo fora de projeto (antes liberava `python3 -m unittest` e redirecionamento), com três fixtures de sessão do Forge.
