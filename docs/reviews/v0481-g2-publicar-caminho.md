---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-publicar-caminho
commit: 0cdf17c362c8ecb59196d5234a7db013ea334e71
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E21.7, #916, G2 publicar confere caminho)

## Achados
- A1 (recomendado) bin/forge-check:3909 · M40 e M42 morrem só por exceção (IndexError em `ultimo[0]`, TypeError em iterar None), não pela recusa: o `not ultimo` e o `or []` protegem contra a quebra. Trocar por `ultimo = (...)[-1:] or [{}]` deixaria a guarda única e o mutante morreria pela mensagem.

## Parecer
Aprovado. Diff contra o merge-base 3c833f3f: 1 commit, cerca de 12 linhas de código em `bin/forge-check` (H1 dentro do teto, um comportamento só), mais testes, specs de mutante e fragmento de changelog.

- Faz o que o E21.6 pede e só aperta: `recusa_do_publicar` calcula o caminho relativo à raiz por `realpath` (arquivo fora da raiz, ou link que sai dela, fica sem caminho e é recusado), casa com `PARECER_A_PUBLICAR.fullmatch`, a mesma regex que o hook `conformidade` usa em `autoria()` (hooks/conformidade.py:4068), e exige que o último registro daquele caminho tenha o sha256 e o papel do tipo. O hook grava `caminho` relativo à raiz da worktree, então a chave confere.
- Efeito colateral aceito: publicar de uma worktree a partir da cópia principal (caminho absoluto de outra worktree) passa a ser recusado; rode-se o comando na worktree do parecer, como o `commit:` já pede.
- Testes: as sondas S1 (fora do projeto e cópia de `docs/reviews/`) e S2 (veredito superado) viraram 3 testes de comportamento com subprocesso; rodados contra o `bin/forge-check` da base, os 3 falham; no head, passam. O falso de autoria em `tests/test_forge_pareceres.py:253` agora grava o caminho exato, não um coringa (checklist 12).
- Mutantes M17, M18, M38 a M42 e M19/M20 (specs `v0481-g2-publicar-caminho.json` e `v0481-g2-1-publicar-3.json`): todos morrem; M40 e M42 por erro (A1).
- Commit: mensagem em Conventional Commits, português, escopo e etapa.

## Provas
- `python3 -m unittest tests.test_conformidade_pareceres tests.test_forge_pareceres`: Ran 44 tests, OK (head 0cdf17c3).
- Mesmo módulo com o `bin/forge-check` de 3c833f3f: FAILED (failures=3), os testes s1 (2) e s2.
- `bin/forge-mutante tests/mutantes/v0481-g2-publicar-caminho.json tests/mutantes/v0481-g2-1-publicar-3.json --processos 1`: M38, M39, M40, M41, M42, M17, M18, M19, M20 morreu.
- CI no 0cdf17c3 (run 45855084791): árvore já provada na develop, bateria (passos), instalação (python 3.14) e bateria (verificações longas) verdes; `bateria (pareceres)` vermelha por falta do parecer (espera este arquivo), e ela cancelou as partes da suíte e o teto de pulados, o que deixou `bateria (python 3.14)` e `bateria` vermelhas (log: "partes: cancelled; pulados: cancelled; instalação: success"). Nenhum vermelho vem do código.
- ci: 0cdf17c362c8ecb59196d5234a7db013ea334e71 verde
