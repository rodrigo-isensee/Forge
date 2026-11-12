---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: cddc8915fda2dd271907323e1a2c04beebd2bd28
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.18, conformidade-caminho-git, revalidação por delta da volta 2)

## Escopo lido
Delta lido por `forge-check parecer delta docs/reviews/v046-conformidade-caminho-git.md`: intervalo c0727411..cddc8915 (volta E20.16, commit cddc8915), 23 arquivos no domínio: `hooks/conformidade.py` (a regex `_REV_PARSE` sai; entram `valor_do_rev_parse`, `trocar_rev_parse`, `OPCOES_DO_DIR_DO_GIT` e `CAMINHO_SIMPLES`), `tests/test_hook_git_comum.py` (mínimo 42 → 58), 16 fixtures `gitcomum-v2-*`, as specs `tests/mutantes/v046-conformidade-caminho-git-2.json` (G15, G16) e `-3.json` (G17 a G19), `docs/hooks-fixtures.md` e o fragmento. M14 da branch inteira contra a base 8b5a44d5: 118 linhas de código e teste (`hooks/conformidade.py` 79+5, `tests/test_hook_git_comum.py` 34+0), abaixo da orientação de 150; uma classe de comportamento em `hooks/` com corpus próprio. Instância que não fez a entrega, numa worktree destacada minha no head; rodei só `tests/test_hook_git_comum.py` (R-TETO): 1 teste OK, 58 fixtures (41 recusam, 17 liberam).

## Achados
- A4 (recomendado) hooks/conformidade.py:954 · A4 a A8 da segurança (E20.8, E20.13) seguem nomeados como cartões no Histórico (12:38), sem linha no KANBAN.md; pendente: do Jarvis, não do autor

## Sondas
- S1 · cp x "$(git rev-parse --git-path 'hooks/pre-push')" · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S2 · cp x "$(git rev-parse --git-path \"hooks/pre-push\")" · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S3 · cp x "$(git rev-parse --git-path hooks/pre-push 2>/dev/null)" · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S4 · cp x "$(git rev-parse -q --git-path hooks/pre-push)" · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S5 · cp x "$(git -C . rev-parse --git-path hooks/pre-push)" · espera: rc 2 R-CONFORMIDADE · obtido: rc 2

## Parecer
**Aprovado** no head cddc8915.

A3 (bloqueante da E20.12) resolvido: o corpo de `$(…)` e da crase é lido por palavras (`shlex`, com recaída por palavras sem aspas quando as aspas não fecham), e basta `rev-parse` seguido de `--git-dir`, `--git-common-dir`, `--absolute-git-dir` ou `--git-path <x>`; o argumento do `--git-path` que não é caminho simples vale como o próprio `.git` (falha fechada). S1 a S5 refeitas contra o head como fixtures temporárias na minha worktree, pela máquina do `tests/test_hooks.py`, e apagadas depois: todas rc 2. Além delas, recusam rc 2: `--git-dir;`, `--git-dir|cat`, `--git-dir&&true` colados, `2>&1|head -1`, `$(cd . && git rev-parse --git-dir)`, `$(…)` aninhado no argumento do `--git-path`, `--git-common-dir`, o `$(…)` fechado antes do resto e `$(git rev-parse --show-toplevel)/.git/hooks/pre-push`. Controle: `cp x docs/y.md` e `cp x "$(git rev-parse --show-toplevel)/docs/y.md"` com esperado 2 falham (o hook libera), o que prova que as sondas distinguem.

Leitura: funções pequenas, nomes que dizem o que fazem, comentário do contrato no lugar da regex; `trocar_rev_parse` devolve a substituição intacta quando não é do diretório do git, então `--show-toplevel` e outras seguem livres (fixtures `gitcomum-v2-menos-c-toplevel-libera` e `-menos-c-ler-libera`). Guardas novas com um mutante por linha (G15 :370, G16 :372, G17 :374, G18 :381, G19 :368); cada `de` aparece uma vez na fonte (conferido, AR-12), G14 atualizado para a linha nova (:380). A execução dos mutantes e da cobertura é do QA; cito sem refazer.

A4 · recomendado, não é do autor: registrar no KANBAN.md os cartões A4 a A8 da segurança antes do merge.

Cito e não refaço (`R-SEGURANCA`): a segurança revalida o mesmo delta na E20.19 e o QA na E20.20.
