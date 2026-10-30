---
tipo: review
contrato: 1
pedido: pn3-pr-contra-main
branch: melhoria/pn3-pr-contra-main
commit: 4b3bf3298a5bf02f26327b04bb4e9683a4cc963d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: pn3-pr-contra-main

Revalidação por delta da volta 1 (158998c correção, 4b3bf32 mutantes) sobre o parecer anterior (ccf72bb, reprovado, head 34e3c1b). Teto M14 na branch inteira (`git diff --numstat --no-renames 31257c14...4b3bf32`): 126 linhas de código e teste (`scripts/promover-homolog.py` 31+3, `tests/test_promover_homolog.py` 85+7; a spec em `tests/mutantes/` fica fora), um comportamento; dentro do teto.

## Delta lido
`forge-check delta --parecer docs/reviews/pn3-pr-contra-main.md` (intervalo `34e3c1b..4b3bf32`): `docs/promocao-integrador.md:14`; `scripts/promover-homolog.py:12-13, 41, 156-158, 160-164`; `tests/mutantes/pn3-pr-contra-main.json:9-10, 46-87`; `tests/test_promover_homolog.py:5-6, 14-15, 393-428`. Todo o resto do diff ficou como "já lido" no parecer ccf72bb (ordem antes do `gh`, dry-run, slug, citação da saída, ramo sem versão nova).

## Achados

## Revalidação dos achados anteriores
- A1 (bloqueante, resolvido) · `scripts/promover-homolog.py:156-158`: a parada agora exige rc diferente de 0 e ao menos uma linha de stdout fora de `docs/devops`/`docs/security` (`PARECERES_DA_LEVA`, linha 41), ou stdout vazio. Conferi no `cmd_pr` do `bin/forge-check` que cada linha de stdout é um problema e que a linha de devops e segurança começa por `docs/devops`/`docs/security` (a pasta, no "sem parecer", ou o caminho do parecer); avisos vão para o stderr. Os casos da #352 (0.30.5) e da #343 (0.30.4), cuja saída eram só as linhas `docs/devops: revisao-devops` e `docs/security: revisao-seguranca`, deixam de parar; linha de review ou QA, junto ou sozinha, segue parando. Regressão: `test_devops_e_seguranca_da_leva_nao_param_a_release` (commit em `.github/workflows/ci.yml` na leva, rc 0 e a linha "não conta" impressa). As linhas ignoradas são impressas, não descartadas em silêncio.
- A2 (recomendado, resolvido) · `scripts/promover-homolog.py:160-161`: a mensagem de parada diz `a branch da release é melhoria/<pedido>, R-FLUXO`; `test_queda_sem_veredito_para` afirma `melhoria/release-0.2.0`.
- A1 do QA (ramo `except`, falha fechada): `ContraMainFalha` cobre prazo estourado, `forge-check` ausente e queda sem stdout; o veredito é do QA.
- `docs/promocao-integrador.md` passo 3 e a docstring dizem que devops e segurança não contam e por quê; batem com o código.

## Ferramentas (citadas, não refeitas à mão)
- `python3 -m unittest tests.test_promover_homolog`: `Ran 36 tests ... OK`.
- `bin/forge-mutante tests/mutantes/pn3-pr-contra-main.json` (rev 4b3bf3298a5b): M1 a M8 `morreu`; M7 (filtro trocado por `or`) e M8 (filtro largo, `docs/`) cobrem os dois lados do A1, M5 e M6 a falha fechada.

## Parecer
Aprovado. O delta resolve o A1 e o A2 sem ampliar o escopo; nenhum achado novo. Sem linha AR nesta rodada (decisão técnica 15:28 do T1-CONF-ESCOPO-REV); classe do A1 anterior: guarda com alcance maior que o requisito (falso bloqueio).
