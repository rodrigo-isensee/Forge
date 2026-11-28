# Rastreio do critério à prova (D7)

Apoio da skill `produto-criterios`, passo 4: o id do critério e a prova que o cobre.

## Id estável
Cada critério ganha um id estável `C-n` no `## Critério de pronto` do pedido (`- C-1 Dado ...`). O id nunca se renumera nem se
reaproveita; critério retirado fica com o id e a marca de corte.

## Prova
O `PQ-n` do brief que prova o critério leva o campo `cobre: C-n` (`- PQ-1 (cmd): ... · espera: rc=0 · cobre: C-1, C-2`; `R-PROVA`).

## Tabela pedido × entregue
Sai de `forge-check criterios <pedido>`, não à mão. O critério conta como entregue só com um `PQ-n` que o cobre num brief selado
cujo conteúdo ainda é o do selo (o sha256 do `## Histórico` confere) e cuja etapa do `Cobre:` tem `entrega conferida` no
`## Histórico`. Sem isso, sai "não entregue" (rc 1); brief alterado depois do selo não prova nada.
