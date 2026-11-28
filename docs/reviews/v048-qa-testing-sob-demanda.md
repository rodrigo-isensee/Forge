---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-qa-testing-sob-demanda
commit: 87575570ef9ac5b24f09ab56e9f7354dab3a2987
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Code review: modelos, oráculo e saídas do mutante da qa-testing num arquivo lido sob demanda (v048 E5.3)

Escopo: pedido v048, etapa E5.3, PR #958, 1ª rodada completa no head `87575570` (`R-REVIEW`). Li o diff inteiro, `git diff 21aada577952d1c6739e950047ffe8af0cfceeaf 87575570ef9ac5b24f09ab56e9f7354dab3a2987`: 3 arquivos (`skills/qa-testing/SKILL.md` 5+/36-, `skills/qa-testing/referencia.md` novo com 65 linhas, o fragmento `changelog.d/v048-qa-testing-sob-demanda.md`), num commit do autor (`74a8a84c`) e no merge da `develop` (`87575570`, sem mudança própria). QA (E5.5) e segurança (E5.4) correm em paralelo no mesmo head; não os refaço.

## Achados
- A1 (bloqueante) skills/qa-testing/referencia.md:45 · texto movido mudou de palavra e de sentido: o original dizia "lista a condição ... sem mutante declarado ("declarado, não provado"; ...)"; agora diz que essa condição "sai declarado, não provado", e o bin/forge-mutante:715 dá esse rótulo à condição coberta. Restaure o texto literal
- A2 (recomendado) skills/qa-testing/SKILL.md:35 · o ponteiro manda ler a seção do oráculo só "ao escrever o oráculo", mas ela traz também a regra do review do oráculo, e o referencia.md:30 diz "ou ao revisar um"; o portão que revisa não é mandado ler; sugestão: acrescentar "ou ao revisar um" no ponteiro

## Conferência do pedido
- **Nenhuma regra com ID saiu da `SKILL.md`:** extraí os IDs (`[A-Z][A-Z0-9]+(-[A-Z0-9]+)+`) da base e do head; a única diferença é `CT-01`, que é o exemplo da tabela do modelo do plano, agora no `referencia.md`, e não uma regra. `EXT-1`, `R-TETO`, `AR-<n>` e os demais seguem na `SKILL.md`.
- **Invariantes de `tests/config.json`:** os 12 trechos de `skills/qa-testing/SKILL.md` estão todos no head (o de `relatorios/` difere só pelo escape `\\.gitignore` do JSON, igual à base). `tests.test_forge.RegrasInviolaveis` no head: 3 testes `ok`.
- **Texto movido idêntico:** comparei cada linha removida da `SKILL.md` com o `referencia.md`, com espaços normalizados. Os dois modelos (plano e bug), o "Onde e como" e o "Review" do oráculo e a frase do mutante equivalente batem palavra por palavra (mudam só a quebra de linha e o rótulo em negrito). A frase das saídas do `--cobertura` não bate: é o A1. Pelo código (`bin/forge-mutante:715`, `:719`, `:895`), a condição sem mutante sai `sem mutante`; `declarado, não provado` é o sufixo da linha `coberta`. O original era ambíguo (uma lista de rótulos entre parênteses), e a reescrita o tornou falso; a regra do pedido era mover sem mudar palavra.
- **A `SKILL.md` diz quando ler cada seção:** plano ("ao abrir o plano"), oráculo ("ao escrever o oráculo", mas sem o review: A2), bug ("ao abrir o relatório"); o mutante aponta "formato e saídas em `referencia.md`", e o `referencia.md` diz o quando em cada seção.
- **Orçamento do `qa-engineer`:** `medir()` de `tests/test_orcamento_instrucao.py` dá, na base `21aada57`, 21463 caracteres e 41 marcadores, e no head 20068 e 34 (teto 21480 e 45). `tests/test_orcamento_instrucao.py` no head: `Ran 8 tests ... OK`.

## Ferramentas, catraca e custo (ordem do dono 28/11 07:41)
- O diff não toca hook nem `bin/`; toca a `SKILL.md`, que tem invariantes (arquivo protegido). `catraca` e `catraca (conferência)` estão verdes no run `46142076207`, `headSha` `87575570`, `conclusion` `success`.
- Teste de custo (`tests/test_hooks_volta_corpus.py`) no meu computador, com `env -i`: `test_corpus_nos_dois_hooks` deu 6094068 contra o teto 6082580 do interpretador. Não é do diff: nenhum arquivo de `hooks/` ou `.githooks/` lê `qa-testing` nem `referencia.md` (`grep -rln` vazio), e o contador depende do ambiente do interpretador. O mesmo teste roda verde na suíte do CI deste head.
- Mutação: o diff é só de texto (skill, classe C), sem linha de guarda e sem `tests/mutantes/v048*.json` tocado; não há mutante a refazer.
- Teto H1: 0 linhas de código (só `.md` de skill e fragmento). O pedido tem um comportamento só.
- Commit `74a8a84c` em Conventional Commits, em português, com o fragmento de changelog; o merge da `develop` entrou uma vez, antes do pedido de merge (`R-FLUXO`).

## CI
- ci: 87575570ef9ac5b24f09ab56e9f7354dab3a2987 verde (`gh pr checks 958` rc 0; run `46142076201` com `headSha` `87575570`, `success`: suíte 5/5, instalação, passos, verificações longas, python 3.14, teto de pulados, árvore já provada).

## Parecer
Reprovado, por um bloqueante. A1 · `skills/qa-testing/referencia.md:45` · a frase das saídas do `--cobertura` foi reescrita ao mudar de arquivo e agora diz que a condição sem mutante sai "declarado, não provado", o que o `bin/forge-mutante:715` desmente · sugestão: copiar o texto original sem mudar palavra (ou, se o autor quiser corrigir o sentido, que a condição sem mutante sai `sem mutante` e a coberta sai `declarado, não provado`, o que é mudança de texto e precisa ser dita no PR) · bloqueia. A2 é recomendado e vira cartão depois do merge. O resto confere: nenhuma regra nem invariante saiu, o orçamento caiu de 21463 para 20068 e o CI do head está verde.
