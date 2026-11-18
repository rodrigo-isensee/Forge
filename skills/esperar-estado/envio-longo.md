# O envio longo: detalhe

Parte da skill `esperar-estado`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres da
`SKILL.md` (diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de arquivo, com ponteiro).

## Caminho literal nas três vezes
O laço do log cita o mesmo caminho literal nas três vezes, sem variável: com `$log`, o caminho que cita `.forge/` ou
outra marca de ação crítica é recusado pela `conformidade`.

## O `bin/forge-fechar` com `--espera` acima de 170 s
Vale a mesma forma do envio longo: lance-o no lugar de `<envio>` e, com `fim=rc=1`, leia no log a linha
`fim: código <n>` (3 é integrado com limpeza pendente).
