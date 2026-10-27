### Corrigido
- Os 4 testes de desempenho dos hooks medem tempo de CPU (processo e filhos) com os mesmos limites, e não o relógio: o runner carregado do CI deixa de reprovar PRs sem relação com eles (PROP-TEMPO-CPU)
