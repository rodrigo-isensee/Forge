---
tipo: revisao-devops
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 03155612d2d56a54686248d5131557075289e4b8
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-26
---
# Review de devops: lote-fechar2

## Parecer
Aprovado. A única mudança em `.github/` é uma linha em `.github/workflows/ci.yml` (passo "shellcheck (scripts e hooks)"): `bin/forge-fechar` entra na lista logo depois de `bin/forge-init`. O passo mantém o nome, a posição (depois de "Testes do Forge", antes da instalação ponta a ponta), o `if: ${{ !cancelled() && steps.gate.outputs.pesada == 'true' }}` e o restante da lista, inalterados. Nenhum outro passo, permissão, gatilho, ação, segredo ou `concurrency` mudou (`git diff` de `.github/`: 1 linha trocada). Ferramentas: `git diff b6eb84f...0315561`, `shellcheck` (lista completa do passo, incluindo `bin/forge-fechar`, no worktree em 0315561: rc=0, sem aviso). Faltou no ambiente: `actionlint` (lacuna registrada; a mudança é só o argumento de um `run:`).

## Achados

## Detalhe dos achados
(nenhum)

## Custo e rollback
Custo: zero (`R-CUSTO`); um arquivo a mais no shellcheck, sem job novo nem runner pago. Nada escreve na `main` (`R-MAIN`); sem `continue-on-error`, `[skip ci]` ou check desligado (`R-VERIFY`). Rollback: reverter o commit. O PR toca `.github/`: a catraca pede o rótulo `afrouxa-regra` do dono; o tech-lead deve avisar (o autor não aplica).
