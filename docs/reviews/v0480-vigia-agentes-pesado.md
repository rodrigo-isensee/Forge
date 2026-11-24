---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-agentes-pesado
commit: 995807ff250529e98107c0a1a014653dce85be99
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.43 (PR #859, revalidação por delta no head 995807ff; item E172.3)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `25c60be7..995807ff`, sem o que veio da base). No domínio do review: `docs/hooks-fixtures.md` e `tests/test_hooks.py`. O delta é o merge da `develop` (a6e81a54) e o índice das fixtures regerado; o código de `hooks/` da branch não mudou desde o parecer aprovado em 25c60be7.

## Achados
- A3 (recomendado) hooks/pesado.py:450 · mantido do parecer anterior: alarme de 290 s entre o gravar_a_vez e a saída do hook deixa a trava gravada sem PostToolUse que a solte; vira cartão depois do merge.
- A4 (recomendado) docs/hooks.md:1 · mantido do parecer anterior: a seção do vigia ainda o descreve só no conformidade e no parecer; vira cartão depois do merge.

## Sondas
- S1 · git merge-tree --write-tree 995807ff^1 995807ff^2 · espera: conflito só no índice gerado · obtido: CONFLICT só em docs/hooks-fixtures.md; tests/test_hooks.py auto-merge
- S2 · git diff --stat <árvore do merge-tree> 995807ff · espera: só docs/hooks-fixtures.md · obtido: 1 arquivo, docs/hooks-fixtures.md (2+, 11-)
- S3 · python3 -I scripts/indice-fixtures.py --conferir (env -i, head 995807ff) · espera: em dia · obtido: em dia, rc 0; 3576 fixtures = 3570 da develop + 6 da branch; `pesado` 30 e `parecer` 587

## Parecer
Aprovado. O merge da `develop` não muda o patch da branch: recomputado com `git merge-tree`, a árvore automática é igual ao commit 995807ff em tudo, fora o índice gerado, e o conflito do índice foi resolvido regerando-o (S2, S3), não à mão. O lado da branch em `tests/test_hooks.py` é o mesmo já aprovado em 25c60be7.

Rodado aqui no head 995807ff (env -i): `tests.test_indice_fixtures` (7 OK); `tests.test_hooks.Hooks` com `test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera`, `test_alias_do_gh_com_opcao_antes_do_nome` e `test_graphql_arquivo_que_nao_e_regular_e_ilegivel` (3 OK, o teste da branch e os dois que a develop trouxe no mesmo arquivo).

CI do head 995807ff (run 45462014706), lido na hora do parecer: `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `árvore já provada na develop` e 8 das 10 partes da suíte verdes; `suíte (3.12, parte 1/5)` e `suíte (3.14, parte 4/5)` pendentes; `bateria (pareceres)` e `catraca` vermelhos aguardam os pareceres neste head. O merge segue pelo CI verde completo.
