---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: f3258bb890921173e775a174642fdb048f758158
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E6.39, #878, G2.1 `forge-check parecer publicar`), volta por delta

Revalidação por delta da rodada aprovada em 939e4d22 (E6.34; texto no git). Delta lido: `forge-check parecer delta` (intervalo `939e4d22..f3258bb8`, sem o que veio da develop 020e4af7). No domínio ficam `bin/forge-check`, `bin/forge-testes` e `tests/test_hooks.py`.

Gatilhos: controles-do-forge, autorizacao, ci-cd.

Conferência da resolução: `git merge-tree --write-tree 99b48fbe 020e4af7` reproduz o merge (árvore 7e91a91d). Ela difere do f3258bb8 só nos dois arquivos em conflito, `bin/forge-testes` e `docs/hooks-fixtures.md`. O resto, inclusive `bin/forge-check` e `tests/test_hooks.py`, é a união automática do git, sem mão humana: a develop entrou igual e as linhas do item ficaram como foram aprovadas. Contra a develop (`git diff 020e4af7 f3258bb8 -- bin/forge-testes`), mudam só duas linhas, as duas com acréscimo do item. `test_forge_pareceres` entra na tupla `FORGE_CHECK` ao lado do `test_fechar_corte` da develop, e `test_forge_pareceres` fica em `RODAM_OS_HOOKS`. Nenhum módulo sai.

O que aperta, o que é neutro, o que afrouxa:
- Aperta: nada novo. As travas do item seguem as aprovadas em 939e4d22.
- Neutro: `bin/forge-testes` (união das duas tuplas, sem remoção, o que mantém os módulos dos dois lados no mapa de afetados) e `docs/hooks-fixtures.md` (índice gerado, 3596 fixtures, igual ao `ls tests/hooks/*/*.json | wc -l`; `scripts/indice-fixtures.py --conferir` diz "em dia").
- Afrouxa: nada. Nenhuma fixture, asserção, mutante ou módulo da lista de testes saiu.

## Achados anteriores
- A1 da E6.24, A1 do review E6.18 e A1/A2 da E6.16 seguem fechados. O delta não toca `hooks/conformidade.py` nem `bin/forge_pareceres.py` além da união automática com a develop.

## Suíte e CI
Rodei aqui, no f3258bb8, `tests.test_forge_pareceres` e `tests.test_fechar_corte`, os dois módulos da tupla resolvida: 70 testes, OK. Nenhum mutante foi tocado pela resolução.

No run 45806174857 (CI, `headSha` f3258bb8), deram `success` `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, as 10 partes da suíte (3.12 e 3.14), os dois `teto de pulados`, `instalação (python 3.14)` e `árvore já provada na develop`. `bateria (pareceres)` falha: o log diz R-REVIEW com o parecer de review sem o `commit:` deste head, o que estes pareceres resolvem. `bateria` falha só por agregá-la. O run 45806174799 (Catraca) falha com R-CONFORMIDADE porque o item muda `bin/forge-check` e `hooks/conformidade.py`, e só o rótulo `afrouxa-regra` do dono libera. Nenhuma das falhas é de teste.
- ci: f3258bb890921173e775a174642fdb048f758158 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH: a lacuna fica registrada e nada foi instalado (`R-CUSTO`). A revisão foi estática.
