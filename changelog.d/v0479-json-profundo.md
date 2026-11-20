### Corrigido
- Hooks, catraca e forge-placar: teto comum de aninhamento (64 níveis de `[` e `{`, `hooks/_json_raso.py`) antes do `json.loads` no estado dos hooks, nos JSON que a catraca lê e no `--ci` da medida, com falha fechada e mensagem fixa; o python 3.14 aceita o aninhamento fundo que o 3.12 recusava com RecursionError, e o `--ci` fundo deixa de dar traceback (v0478 E44.1).
