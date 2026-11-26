---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: 6c709157b28682ed39bab0663bdd8989753e9790
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (melhoria/v0481-voltas-alinhada, #902, E14.88)

Revalidação por delta (H3), `e871982c..6c709157`, lida por `forge-check parecer delta docs/reviews/v0481-voltas-alinhada.md` (revalida: sim). O delta é o merge da `develop` 020e4af7 (98c9dfde) e a correção 6c709157 (2 arquivos, +1 −21).

Merge (98c9dfde), conferido por `git show --remerge-diff`:
- Arquivos tocados pelos dois lados desde a base 34ab6714: `agents/jarvis.md`, `bin/forge-check`, `bin/forge-testes`, `tests/pesos-d4.json`. Conflito de conteúdo só nos dois primeiros.
- `agents/jarvis.md:30-31`: o passo 5 ficou como na `develop` (`--worktree <cópia>`), que só ela mudou; o passo 6 ficou como na branch (`voltas sem teto`), que só ela mudou. Resolução certa.
- `bin/forge-check` em `cmd_entrega_conferir`: as duas linhas novas ficaram (`testes_enfraquecidos_da_volta` da branch e o bloco D2 da `develop`), sem troca de lógica.
- Todo arquivo que só a `develop` mudou entrou idêntico a 020e4af7; todo arquivo que só a branch mudou ficou idêntico a e871982c, fora os três pareceres commitados depois.

Achados da rodada anterior:
- A1 (sanitizador): resolvido. `bin/forge-check:4751` passa `real` e `texto_da_volta` por `sem_controle` (aceita int, `str(texto)`); SaidaSanitizada verde no CI.
- A2 (M23 na spec -3): resolvido. M21 e M23 saíram de `tests/mutantes/v0480-g1-1-uma-volta-3.json`; o `de` dos dois não existe mais na fonte (o teste do M21 também saiu no delta anterior); os 5 restantes (M16, M18..M20, M22) acham âncora única e morrem. ConferirTodas verde no CI.
- A3 (recomendado, `autorizar` sem uso): não mexido; vira cartão depois do merge.

## Verificações
- Testes do diff, à mão no head 6c709157: `python3 -m unittest tests.test_volta_por_delta tests.test_volta_alinhada` · Ran 120 tests, OK.
- Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v0480-g1-1-uma-volta-3.json` · M16, M18, M19, M20, M22 morreram. A linha mudada em 4751 é mensagem, não guarda.
- ci: 6c709157b28682ed39bab0663bdd8989753e9790 verde
- CI do head 6c709157 (run 45806461223): suíte partes 1 a 5 em 3.12 e 3.14, teto de pulados, bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação e árvore já provada verdes. Vermelhos esperados: `bateria (pareceres)` (pareceres do head anterior reprovados), `catraca` (pede o rótulo `afrouxa-regra` pelos testes do teto apagados, o mesmo da rodada anterior; o rótulo é do dono) e `bateria`, que agrega as duas.

## Parecer
Aprovado. O merge entrou igual à `develop` e as duas resoluções de conflito juntam o que cada lado mudou; as duas correções de uma linha fecham A1 e A2 sem mudar lógica. A3 segue como cartão. O merge ainda depende do rótulo `afrouxa-regra` do dono (catraca) e dos pareceres de QA e segurança no head.
