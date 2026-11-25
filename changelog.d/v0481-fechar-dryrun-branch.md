### Corrigido
- forge-fechar --dry-run sem a branch local (clone separado) cria a branch sem rastreio na origin/<branch> e roda o 1c, e a apaga no fim (o passo real seguinte lê o servidor, não a origin/<branch> velha); sem a origin/<branch>, para com código 1 e manda git fetch (antes, '1c: não rodou' com código 0). O --limpar --dry-run só descreve o passo 7 (v0481 E14.32).
