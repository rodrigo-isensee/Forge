### Corrigido

- O hook R-REVIEW (`hooks/parecer.py`) dá à linha com `gh pr merge` o prazo `PRAZO_DO_MERGE_S` (8 s), abaixo do `timeout` de 10 s do hooks.json, em vez dos 3 s que a decisão pelo `forge-check pr` estourava com a máquina carregada; estourado, continua recusando, e não há cache de veredito.
