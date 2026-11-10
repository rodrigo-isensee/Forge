### Alterado

- FILA-31 F2: `git_da_copia`, `resolver` e `montar_copia`, iguais em bin/forge-testes e bin/forge-mutante, vão para bin/forge_apoio_testes.py; cada script passa o próprio `ambiente_da_copia` por `functools.partial` (o do forge-mutante segue tirando o `PYTHONPYCACHEPREFIX`), sem mudar comportamento.
- Bancada de instrução (S7): o `espera` dos casos aceita alternativas separadas por `|` e compara sem diferenciar maiúsculas e acentos ("Minha recomendação" conta para "recomend").

### Adicionado

- Índice do corpus de fixtures dos hooks (`docs/hooks-fixtures.md`, Fase C): por hook e por prefixo do nome do caso, com a contagem, quantos recusam e liberam, as regras `R-*` esperadas, os cartões e um exemplo do que o grupo prova. Sai de `scripts/indice-fixtures.py` (`--conferir` dá rc 1 se não está em dia), e `tests/test_indice_fixtures.py` confere que está em dia. Nenhuma fixture muda de nome nem de lugar.
- Bancada de instrução (S7): `--saida ARQ` grava em JSON, por versão, caso e rodada, a entrada, a resposta, os tokens, os segundos, o `ok` e o `invalida`, com o resumo por versão, para comparar a qualidade das respostas.
- Bancada de instrução (S7): `--contexto ARQ` (opcional) e a nota fixa "sem ferramentas", iguais nas duas versões; a rodada cuja resposta escreve uma chamada de ferramenta falsa (`<invoke`, `"name": "Bash"`) é `invalida`, sai das médias e é contada por versão.
