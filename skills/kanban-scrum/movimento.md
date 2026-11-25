# O movimento no quadro: casos de borda

Detalhe do `forge-check movimento` (resumo em `SKILL.md`, seção "Histórico"). Além de gravar a linha do histórico, ele move a linha do cartão para a seção de destino no `KANBAN.md`:

- Cartão sem linha no quadro nasce na seção de destino.
- Cartão repetido em duas seções sai de todas; a linha achada por último é a que anda.
- Cabeçalho e separador da tabela nunca contam como cartão, nem linha de outra largura ou fora de tabela.
- Quadro com byte UTF-8 inválido não é reescrito.
- Estado sem seção de mesmo nome vai à seção que o estado mapeia (como no `kanban --gerar`); sem ela, a "Bloqueado".
- Se não move, avisa, e o histórico fica gravado.
- O `·` do `--titulo` vira `-`.
