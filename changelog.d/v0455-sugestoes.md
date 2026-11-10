### Corrigido

- O hook R-REVIEW (`hooks/parecer.py`) dá à linha com `gh pr merge` o prazo `PRAZO_DO_MERGE_S` (8 s), abaixo do `timeout` de 10 s do hooks.json, em vez dos 3 s que a decisão pelo `forge-check pr` estourava com a máquina carregada; estourado, continua recusando, e não há cache de veredito.
- O `forge-check entrega` tira do escopo, em toda etapa, o arquivo cujo conteúdo no head é igual ao da base da branch (`origin/<base>`): depois de um merge da develop (também `--squash`), o parecer de outro lote e o arquivo que já está na base não ficam mais "fora do declarado no brief"; o arquivo que a branch mudou de verdade continua contando.
