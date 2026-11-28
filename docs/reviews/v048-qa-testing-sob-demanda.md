---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-qa-testing-sob-demanda
commit: 2c6b6f8193c1f3c4046cd436bef423193274d079
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Code review: modelos, oráculo e saídas do mutante da qa-testing num arquivo lido sob demanda (v048 E5.6, volta 1)

Escopo: pedido v048, etapa E5.6, PR #958, revalidação DELTA no head `2c6b6f81` (`R-REVIEW`, H3). Delta lido: `forge-check parecer delta docs/reviews/v048-qa-testing-sob-demanda.md`, intervalo `87575570ef9ac5b24f09ab56e9f7354dab3a2987..2c6b6f8193c1f3c4046cd436bef423193274d079`, no domínio só `skills/qa-testing/SKILL.md` e `skills/qa-testing/referencia.md` (+4 -4, commit `2c6b6f81`). Fora do delta nada foi relido. QA (E5.8) e segurança (E5.7) correm em paralelo no mesmo head.

## Delta conferido
- **A1 da 1ª rodada (bloqueante), resolvido:** `skills/qa-testing/referencia.md:45-47` volta ao texto original. Comparei, com espaços normalizados, o trecho a partir de "lista a condição" da `skills/qa-testing/SKILL.md:91` da `develop` (`21aada57`, igual em `origin/develop`) com as três linhas do head: `IGUAL`, palavra por palavra, do "Python mudada sem mutante declarado" ao "rc 1)." final. Os rótulos citados existem no `bin/forge-mutante` (`declarado, não provado` em :715, `isenta · ` em :717, `não coberto: ` em :880, `isenta velha` no rc 1 de :895); a frase volta a ser a da `develop`, sem a reescrita que dava o rótulo da condição coberta à condição sem mutante.
- **A2 da 1ª rodada (recomendado), atendido:** `skills/qa-testing/SKILL.md:35` diz "ao escrever o oráculo ou ao revisar um", o mesmo gatilho de `skills/qa-testing/referencia.md:30`.
- **Testes que o delta alcança:** `tests.test_orcamento_instrucao` e `tests.test_forge.RegrasInviolaveis` no head, com `env -i`: `Ran 11 tests ... OK` (o ponteiro cresceu 15 caracteres; o orçamento segue abaixo do teto).

## Ferramentas, catraca e custo (ordem do dono 28/11 07:41)
- O delta não toca hook nem `bin/`; toca a `SKILL.md`, arquivo com invariantes. `catraca` e `catraca (conferência)` verdes no head (run `46146179674`). O teste de custo roda na suíte do CI deste head, verde.
- Mutação: delta só de texto, sem linha de guarda nem `tests/mutantes/v048*.json`; não há mutante a refazer. Teto H1: 0 linhas de código.
- Commit `2c6b6f81` em Conventional Commits, em português, citando os achados que fecha.

## CI
- ci: 2c6b6f8193c1f3c4046cd436bef423193274d079 verde (`gh pr checks 958`, run `46146179731`: suíte 5/5, teto de pulados, instalação, passos, verificações longas, python 3.14, árvore já provada; fora `bateria (pareceres)` e `bateria`, que esperam os pareceres).

## Parecer
Aprovado. O bloqueante A1 foi resolvido com o texto literal da `develop`, o recomendado A2 foi atendido, e o delta não traz achado novo.
