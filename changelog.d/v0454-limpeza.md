### Alterado

- FILA-31 F2: `git_da_copia`, `resolver` e `montar_copia`, iguais em bin/forge-testes e bin/forge-mutante, vão para bin/forge_apoio_testes.py; cada script passa o próprio `ambiente_da_copia` por `functools.partial` (o do forge-mutante segue tirando o `PYTHONPYCACHEPREFIX`), sem mudar comportamento.
