---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-merges
commit: 7bfe5cc8f5d288500c63894a8ff985576d958aa6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E62.20), melhoria/v0479-entrega-merges

Esta é a revalidação do parecer reprovado em 590d1954 (E62.16), agora no head 7bfe5cc8. Pela H3 e pela `R-REVIEW`, li só o delta. Pela `R-REVIEW`, a suíte inteira fica no CI. Ainda não há PR, então também não há CI.

## Delta lido
`forge-check parecer delta` 590d1954..7bfe5cc8 dá nove arquivos no domínio:
- `bin/forge-check`
- `changelog.d/v0479-entrega-merges.md`
- `tests/mutantes/est-030-l1.json`
- `tests/mutantes/revisor-wt-e6a-3.json`
- `tests/mutantes/v0479-entrega-merges.json`
- `tests/mutantes/v0479-entrega-merges-2.json`
- `tests/mutantes/v0479-entrega-merges-3.json`
- `tests/test_forge_check_base_igual.py`
- `tests/test_selo_e_entrega.py`

O autor também fechou os achados A1 a A5 da segurança (`remoto_da_branch` por nome exato, merge-base único e na 1.a linha de pais, arquivo ausente nos dois lados, blob do outro pai). Li esses trechos só onde tocam A1 e A2 deste parecer. O mérito deles fica com a segurança.

## A1 (vindos_da_base redefinida): resolvido
- A função nova passou a se chamar `vindos_do_remoto_da_base` (`bin/forge-check:2859`). A do E7 (`:877`) volta a ser a única desse nome, e os chamadores dela (`:915`, `:3757`) não mudaram.
- Os mutantes D1 a D6 foram realinhados ao nome novo.
- S1 passa (14 testes OK).
- O teste novo `NomeUnicoNoModulo` faz o parse do módulo com `ast`, afirma mais de 300 definições e exige que nenhum nome se repita. Rodei a mesma leitura nos dois heads. Em 590d1954 ela acha 543 nomes com `['vindos_da_base']` repetido. Em 7bfe5cc8, 544 nomes e nenhum repetido. Ou seja, o teste reprova o defeito que motivou este achado e passa na correção. Ele lê a árvore sintática, não o texto de uma guarda, e cobre a classe inteira do defeito.

## A2 (conferido antigo por cima de reprovado novo): resolvido
- `conferido_mais_novo` (`:2520`) aceita, por arquivo, só o conferido que muda o arquivo e de que nenhum outro desses descende.
- Dois conferidos em ramos sem ordem entre si, ou um `merge-base --is-ancestor` que falha, deixam mais de um candidato e o resultado é None. A falha é fechada.
- `vale_pelo_conferido` (`:2531`) exige o mesmo blob no merge, no outro pai e no conferido mais novo.
- S2 agora recusa.
- Os testes `test_parecer_conferido_antigo_restaurado_no_merge_reprova` e `test_o_conferido_mais_novo_vale` fixam o caso. Os mutantes N1 a N8 cobrem uma guarda cada.
- As classes `MergeDeParecerAninhado`, `MergeDaBaseDepoisDoBrief`, `JuncaoLimpa` e `NomeUnicoNoModulo` passam juntas: 41 testes OK.

## Achados
- A3 (recomendado) bin/forge-check:2524 · `conferido_mais_novo` roda `rev-list <q>` da história inteira e um `nomes_do_intervalo` por conferido, a cada arquivo de cada merge. Limite com `^<base_ref>` ou guarde o resultado por `q`.

## Sondas
- S1 · tests.test_forge_check_base_igual no head 7bfe5cc8 (python3 -I, ambiente limpo) · espera: OK · obtido: Ran 14 tests, OK
- S2 · P1 aprovado, P2 reprovado sobre P1, os dois conferidos; merge de P2 resolvido com o blob de P1; merges_nao_conferidos · espera: recusa fora dos pareceres conferidos · obtido: [('escopo: fora (o merge 89c2198 traz "docs/reviews/x.md" fora dos pareceres conferidos)', True)]
