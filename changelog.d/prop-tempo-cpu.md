### Corrigido
- Os 4 testes de desempenho dos hooks medem tempo de CPU (processo e filhos) e não o relógio, e os limites subiram para caber no runner do CI (corpus 90 s por trabalhador, lançador 120 s, T 2 s), afrouxando a trava por decisão do dono: o runner carregado do CI deixa de reprovar PRs sem relação com eles (PROP-TEMPO-CPU)
