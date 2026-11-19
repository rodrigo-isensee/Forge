---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-pulado
commit: c3cbb941c7bbd8967203ab3d7d2b071ba6f29261
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E13.7, melhoria/v0478-mutante-pulado), revalidação por delta

Rodada anterior: aprovado em `8186cef3` (está no git, não recopiada). Delta lido: `forge-check parecer delta` de `8186cef3..c3cbb941`, no domínio `bin/forge-mutante` e `scripts/placar-mutacao.py`. Fora do domínio (não relido): changelog.d, as specs de `tests/mutantes/` e `tests/test_forge_mutante.py`.

Gatilhos: controle do Forge (bin/forge-mutante, prova de mutação usada como evidência do QA; placar da release).

## Conclusão
A morte provada com outro declarado pulado ao lado não esconde sobrevivente: `bin/forge-mutante:312-315` só deixa passar o declarado pulado quando há `falha` no registro ou erro que já passou pelo filtro de `:306-307` (com `erro_mata`, só o erro de um declarado que rodou). Sem morte, o resultado segue `sem veredito` (saída 2). O declarado que não rodou nem pulou continua `inválido` mesmo com morte, porque o laço não sai cedo. Uma `falha` sob o mutante só conta depois do controle verde (`:867-873`).

A mudança também fecha um caminho que existia em `8186cef3`: o controle com um declarado falhando e outro pulado saía `sem veredito`, que o controle (`:870`) lê como "ok", e a falha preexistente virava `morreu` (saída 0) sob o mutante. Agora o controle dá `morreu`, que é "vermelho", e o mutante sai `controle vermelho` (saída 2). Ver a sonda S1 abaixo.

Placar (`scripts/placar-mutacao.py:32-34,67-72`): `PULADO` casa um subconjunto das linhas que `LINHA` já conta como `sem veredito` (mesmo prefixo, formato de `bin/forge-mutante:886`). Por isso a subtração não fica negativa e não move nada para `mortos` nem tira de `sobreviveu`. Um caminho com espaço só deixa o pulo em `sem-veredito`, sem escondê-lo. A saída do `forge-mutante` continua sem eco.

## Sondas
- S1 · `veredito(["t.m.T.b","t.m.T.a"], [{"id":"t.m.T.a","res":"falha"},{"id":"t.m.T.b","res":"pulado"}])` (controle, sem `erro_mata`) · espera: classe que o controle lê como vermelho · obtido: `8186cef3` `('sem veredito', ...)` (controle "ok"); `c3cbb941` `('morreu', '')` (controle vermelho)
- S2 · `veredito([A,B], [A ok, B pulado], erro_mata=True)` · espera: sem veredito · obtido: `('sem veredito', 'teste declarado pulado: t.m.T.b')` nas duas versões

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, as sondas acima (biblioteca padrão, `python3 -I`) e os testes novos e os do placar (`python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k test_morte_provada_vale_com_outro_declarado_so_pulado -k placar -k Placar`: 7 OK). Suíte inteira: só no CI do PR (não rodada aqui). Sem segredo, dependência nem workflow no delta.
