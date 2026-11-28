---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-pulado
commit: c3cbb941c7bbd8967203ab3d7d2b071ba6f29261
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E13.6, melhoria/v0478-mutante-pulado)

Diff revisado: `4182a6b9..8186cef3`, revalidado por delta até `c3cbb941` (bin/forge-mutante +22 linhas de código, dentro do teto H1; testes, spec de mutantes e fragmento do changelog).

## Revalidação (E13.6)
Delta lido: `forge-check parecer delta docs/reviews/v0478-mutante-pulado.md`, intervalo `8186cef3..c3cbb941`, domínio código e testes (bin/forge-mutante, scripts/placar-mutacao.py, tests/test_forge_mutante.py, as duas specs de mutantes, o fragmento do changelog). Os dois achados recomendados da rodada anterior estão resolvidos; nenhum achado novo.

- **A1 resolvido** (`bin/forge-mutante:312-315`). O declarado não rodado e não pulado segue `inválido`; o só pulado sai `sem veredito` apenas sem morte provada (sem falha e sem erro). `erros` não vazio ali já é só erro que mata, porque o erro que não mata devolve `inválido` antes do laço. Teste novo `Veredito.test_morte_provada_vale_com_outro_declarado_so_pulado`: [A, B] e [B, A] com falha dão `morreu`; erro com controle verde dá `morreu` por erro; A verde e B pulado dão `sem veredito`; o terceiro declarado que não rodou segue `inválido` mesmo com morte.
- **A2 resolvido** (`scripts/placar-mutacao.py:32,71-72`). A coluna `sem-veredito-pulado` conta as linhas `<id> · sem veredito · <arquivo>:<linha> · teste declarado pulado: ...` (o formato de `bin/forge-mutante:886`, também com o sufixo "os que rodaram não o mataram") e sai de `sem-veredito`; o `controle vermelho` segue em `sem-veredito`. Docstring do script atualizada; o teste do placar afirma o total e a linha da spec com a coluna nova.
- **Guardas e mutantes.** Linhas de guarda mudadas: 312 e 314 do `forge-mutante`, 32 e 72 do placar; a spec `v0478-mutante-pulado-2.json` declara Q1, Q2 (314), Q4 (312), Q5 (72) e Q6 (32), e a P2 da primeira spec foi reancorada no texto novo. Rodada neste head das duas specs: Q1, Q2, Q4, Q5, Q6 e P1 a P7 mortos, saída 0. Testes do item (`Veredito` e `PlacarDaRelease`, 16 testes): OK. Suíte inteira: fica para o CI do PR no merge.

## Parecer
Aprovado. O defeito (DEFEITO-MUTANTE-PULADO-SOBREVIVE) está corrigido sem esconder sobrevivente:

- **Nenhum sobrevivente escondido.** A única reclassificação é `sobreviveu` (1) para `sem veredito` (2), e só com teste declarado pulado; o agregado é o `max` dos códigos (`bin/forge-mutante:944`), então a rodada nunca chega a 0 por causa do pulo, e a linha diz "os que rodaram não o mataram". A falha por asserção segue `morreu` antes do pulo; o erro sem controle verde segue `inválido`; o erro que mata segue `morreu` (P7). O equivalente declarado com pulo não se confirma (sai 2 antes do ramo do equivalente, P5). O controle com pulo não vira vermelho (P4): o pulo se decide no mutante. O ID do pulo em subTest (`<id> [<desc>]` ou `<id> (<params>)`) começa por `<id> `, como o `pulado_de` espera.
- **Specs antigas iguais.** Das 246 linhas de mutante sobre `bin/forge-mutante` nas specs de `tests/mutantes/`, todo `de` aparece uma vez antes e depois do diff; só o número da linha muda, e a âncora é o texto. As specs que tocam a região mudada (`v0457-mutante-erro` e `v0457-mutante-erro-2`) rodaram neste head: 10 de 10 mortos, saída 0.
- **Guardas e testes.** Sete mutantes declarados, um por guarda nova (`tests/mutantes/v0478-mutante-pulado.json`), cada um com teste de comportamento do ramo; rodada neste head: P1 a P7 mortos, saída 0. A asserção removida (`pulado` sozinho era `inválido`) é a do comportamento corrigido, e o teste novo afirma o contrário.
- **Regras.** `R-REVIEW`; sem shell tocado; docstring do topo atualizada com o novo veredito; fragmento em `changelog.d/`. Suíte: sem PR neste pedido, o CI do PR fica para o merge; rodei só os testes do item (`Veredito` inteiro e o teste novo de `Execucao`, 10 testes, OK).
