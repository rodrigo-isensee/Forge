---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: 0b2e8d6f8ca3671cdba187ec985a5b15afe65b0b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478

## Achados
- A1 (bloqueante) bin/forge-check:8786 · Sem PR aberto, o `brief gerar` das etapas `pr` e `merge-integracao` (ETAPAS_QUE_RECUSAM, :8778) passa a recusar o brief pelo PARECER-SO-COM-CI-VERDE; o PR só nasce no passo 3 do `forge-fechar` que esse brief manda rodar: o fluxo trava (S1). Adiar ali, como no `--previo`, ou tratar PR ausente.
- A2 (recomendado) bin/forge-check:2122 · A prova só exige os módulos de teste editados no diff (diff sem teste aceita qualquer lista); o cartão pede os módulos tocados do forge-testes, e o #703 (test_selo_e_entrega, test_forge_dono não editados) passaria pela prova. Registrar a troca como decisão (NaoEPortao) no pedido.

## Sondas
- S1 · `pr_da_cli` (a chamada do `pareceres_da_etapa`), review aprovado sem `- suíte:`, gh "no pull requests found" · espera: nada, como o `checks_do_head` sem PR (`[]`) · obtido: `docs/reviews/p1.md: suíte: o parecer aprovado só conta com o CI verde no head ... (PARECER-SO-COM-CI-VERDE, R-REVIEW)`

## Parecer
Reprovado por A1. O desenho da guarda é bom: `checks_ruins` virou a fonte única do `checks_do_head` e do `ci_verde_no_head`, a falha é fechada sem gh ou rede, a catraca (`conferir=False`) não muda e o `--previo` e o passo 1 do fechar só avisam. Os restos da META85 (A2 do passo 5 do Jarvis, A3 com `-I` e ambiente limpo, caminho do `parecer novo` no slug) estão corretos e testados. Falta só não aplicar a guarda onde o PR ainda não pode existir: o `brief gerar` das etapas que abrem o PR.
Tamanho dentro do H1 (cerca de 90 linhas de código líquidas em `bin/forge-check`). Mutantes e cobertura: são do autor (V2), nas specs `tests/mutantes/v0479-forge-check-ci-verde*.json`; não os refiz. Suíte inteira: sem PR, sem CI; não rerrodada (brief). Testes do item rodados neste head: `tests.test_forge_check_pr`, `tests.test_aq5_parecer_novo`, `tests.test_meta85_item_arquivos`, `tests.test_jarvis_nucleo.RevalidaMesmaInstancia`, `tests.test_forge.LerDirigidoDoBrief`: 63 testes, OK, rc=0.
