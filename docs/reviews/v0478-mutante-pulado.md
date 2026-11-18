---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-pulado
commit: 8186cef3fc8174d5303ef9c7f9f668135effd1a2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E13.2, melhoria/v0478-mutante-pulado)

Diff revisado: `4182a6b9..8186cef3` (bin/forge-mutante +22 linhas de código, dentro do teto H1; testes, spec de mutantes e fragmento do changelog).

## Achados
- A1 (recomendado) bin/forge-mutante:312 · declarados [A, B] com A morto por falha e B só pulado saem `sem veredito` (saída 2), não `morreu`: o laço dos não rodados decide antes da falha. Não esconde sobrevivente (era `inválido`, também 2), mas descarta a morte provada; mover a falha para antes.
- A2 (recomendado) scripts/placar-mutacao.py:29 · o sobrevivente com teste declarado pulado passa da coluna `sobreviveu` para `sem-veredito` no placar; registrar na próxima medida que a queda de `sobreviveu` pode vir daí, não de teste mais forte.

## Sondas

## Parecer
Aprovado. O defeito (DEFEITO-MUTANTE-PULADO-SOBREVIVE) está corrigido sem esconder sobrevivente:

- **Nenhum sobrevivente escondido.** A única reclassificação é `sobreviveu` (1) para `sem veredito` (2), e só com teste declarado pulado; o agregado é o `max` dos códigos (`bin/forge-mutante:944`), então a rodada nunca chega a 0 por causa do pulo, e a linha diz "os que rodaram não o mataram". A falha por asserção segue `morreu` antes do pulo; o erro sem controle verde segue `inválido`; o erro que mata segue `morreu` (P7). O equivalente declarado com pulo não se confirma (sai 2 antes do ramo do equivalente, P5). O controle com pulo não vira vermelho (P4): o pulo se decide no mutante. O ID do pulo em subTest (`<id> [<desc>]` ou `<id> (<params>)`) começa por `<id> `, como o `pulado_de` espera.
- **Specs antigas iguais.** Das 246 linhas de mutante sobre `bin/forge-mutante` nas specs de `tests/mutantes/`, todo `de` aparece uma vez antes e depois do diff; só o número da linha muda, e a âncora é o texto. As specs que tocam a região mudada (`v0457-mutante-erro` e `v0457-mutante-erro-2`) rodaram neste head: 10 de 10 mortos, saída 0.
- **Guardas e testes.** Sete mutantes declarados, um por guarda nova (`tests/mutantes/v0478-mutante-pulado.json`), cada um com teste de comportamento do ramo; rodada neste head: P1 a P7 mortos, saída 0. A asserção removida (`pulado` sozinho era `inválido`) é a do comportamento corrigido, e o teste novo afirma o contrário.
- **Regras.** `R-REVIEW`; sem shell tocado; docstring do topo atualizada com o novo veredito; fragmento em `changelog.d/`. Suíte: sem PR neste pedido, o CI do PR fica para o merge; rodei só os testes do item (`Veredito` inteiro e o teste novo de `Execucao`, 10 testes, OK).
