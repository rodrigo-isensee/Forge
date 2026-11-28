---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: 5c998a57f1f7126a1c0f4427865136ede7829f4f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478

## Achados
- A2 (recomendado) bin/forge-check:2122 · A prova só exige os módulos de teste editados no diff (diff sem teste aceita qualquer lista); o cartão pede os módulos tocados do forge-testes, e o #703 (test_selo_e_entrega, test_forge_dono não editados) passaria pela prova. Registrar a troca como decisão (NaoEPortao) no pedido.

## Sondas

## Parecer
Aprovado no head 5c998a57 (revalidação do aprovado em cb1d5ed7, depois do merge da develop 6bcd0a64 pelo forge-fechar e do commit 5c998a57). A2 segue recomendado (vira cartão depois do merge).

Delta lido: `forge-check parecer delta docs/reviews/v0479-forge-check-ci-verde.md` sobre `cb1d5ed7..5c998a57`; base `origin/develop` 8a50379 → 0f6034e, fora do escopo. No domínio, só `tests/mutantes/lote-l08-escopo.json` (M61) e `tests/mutantes/v0479-forge-check-ci-verde-3.json` (M19, M20): o `de`/`para` passa a citar a assinatura e a linha atuais do `pr_da_cli` com `adiar_suite`; guarda, alvo e testes iguais. O resto já foi lido nos pareceres anteriores.

- Âncoras: `grep -nF` acha cada `de` uma vez em `bin/forge-check` (:1578 para M61; :1592 para M19 e M20).
- Mutantes do delta neste head: `bin/forge-mutante --processos 1 --ids M61 tests/mutantes/lote-l08-escopo.json`: M61 morreu (:1578); `--ids M19,M20 tests/mutantes/v0479-forge-check-ci-verde-3.json`: M19 e M20 morreram (:1592).
- Suíte inteira: não rerrodada (brief); este parecer conta com o CI verde no head (PARECER-SO-COM-CI-VERDE).
