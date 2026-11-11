### Corrigido
- MAQ-I9 (fatia 1): o `scripts/conferir-reversao.py` pede o plano com `bin/forge-testes --listar` também depois de cada `git revert --no-commit`, não só na ponta: o commit cujo revert cai na suíte inteira (por exemplo, o que apaga um arquivo sem mapa criado antes na branch) sai `<sha7> sem-veredito: o revert pede a suíte inteira (R-TETO)` e nada roda para ele.
