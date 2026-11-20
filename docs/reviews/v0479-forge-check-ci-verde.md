---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: cb1d5ed7d506a409e05807f30b664ae1ee84f1da
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478

## Achados
- A2 (recomendado) bin/forge-check:2122 · A prova só exige os módulos de teste editados no diff (diff sem teste aceita qualquer lista); o cartão pede os módulos tocados do forge-testes, e o #703 (test_selo_e_entrega, test_forge_dono não editados) passaria pela prova. Registrar a troca como decisão (NaoEPortao) no pedido.

## Sondas

## Parecer
Aprovado no head cb1d5ed7 (revalidação do reprovado em 0b2e8d6f). A1 resolvido; A2 segue recomendado (vira cartão depois do merge).

Delta lido: `forge-check parecer delta docs/reviews/v0479-forge-check-ci-verde.md` sobre `0b2e8d6f..cb1d5ed7`; base `origin/develop` 004ce86 → 8a50379 pelo merge 47b14589, fora do escopo. No domínio: `bin/forge-check` (:1578-1592 `adiar_suite` no `pr_da_cli`; :8788 o `pareceres_da_etapa` passa `adiar_suite=True`), `changelog.d/v0479-forge-check-ci-verde.md` (o texto cita o `brief gerar`), `tests/mutantes/v0479-forge-check-ci-verde-5.json` (M25, M26) e `tests/test_forge_check_pr.py` (classe `SuiteNoBriefSemPr`). O resto já foi lido no parecer anterior.

- A1: o `adiar_suite` só adia a prova da suíte (vira aviso no stderr, como no `--previo`); o `checks_do_head` não muda, e os passos 4 e 6 do `forge-fechar` seguem exigindo o CI verde. Os dois chamadores do `pareceres_da_etapa` (:8338 só avisa; :9064 recusa nas ETAPAS_QUE_RECUSAM) ficam cobertos; a etapa `qa` também adia, o que é coerente porque ela também roda antes do PR. O `pr` direto segue reprovando sem PR (teste `test_o_pr_direto_sem_pr_segue_reprovando`).
- Sonda S1 refeita neste head (mesma entrada: review aprovado sem `- suíte:`, gh "no pull requests found"): `pr_da_cli(..., adiar_suite=True)` e `pareceres_da_etapa(..., "pr", ...)` não trazem linha de `docs/reviews` (só as faltas de QA, segurança e conferência da fixture), com o aviso `aviso: docs/reviews/p1.md: suíte:` no stderr; o `pr_da_cli` direto segue com a linha `docs/reviews/p1.md: suíte: ...`. Esperado e obtido batem.
- Mutantes do delta: `bin/forge-mutante --processos 1 tests/mutantes/v0479-forge-check-ci-verde-5.json`: M25 morreu (:1592), M26 morreu (:8788), rc=0.
- Testes: `tests.test_forge_check_pr` neste head, 47 testes, OK, rc=0. Suíte inteira: sem PR, sem CI; não rerrodada (brief). Sem a linha `- suíte:` aqui: o `test_forge.py` do diff não foi rodado inteiro, então este parecer conta só com o CI verde no head (PARECER-SO-COM-CI-VERDE).
