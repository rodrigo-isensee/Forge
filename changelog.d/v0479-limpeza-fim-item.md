### Adicionado
- forge-copia limpar <cópia>: apaga a cópia (clone ou worktree) do item que acabou, com PR mesclado, PR fechado sem merge ou vazio: sim, só limpa, sem stash e com tudo na origem, no Forge e nos projetos; o forge-fechar --limpar sem PR mesclado nem aberto passa as cópias da branch a ele e deixa a branch local e a remota (LIMPEZA-AO-FIM-DO-ITEM, v0478 E68.1)
### Corrigido
- forge-copia limpar: PR de fork com o mesmo nome de branch (isCrossRepository) não conta como fim do item, e a limpeza da cópia é conferida de novo logo antes de apagar, para não perder escrita feita durante a consulta ao gh (A1 e A2 da segurança, v0478 E68.6)
- forge-fechar --limpar: sem prova de fim do item (PR fechado do próprio repositório ou vazio: sim) volta a recusar como antes, com a mesma mensagem e sem apagar nada; só com a prova passa as cópias ao forge-copia limpar (v0478 E68.12)
