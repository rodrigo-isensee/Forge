---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: 95994eec3b874dff23e39f68a6b4e7181d4205d5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E91.6 (TRILHA-FORGE-CHECK, revalidação)

Escopo: delta a318e97d..95994eec lido por `forge-check parecer delta` (bin/forge-check, changelog.d, specs -2 e -3, test_revisor_wt, test_trilha_forge_check); 14 linhas de código em `bin/forge-check`, dentro do H1.

## Parecer
Aprovado. Os dois recomendados da rodada anterior estão resolvidos e o resto do delta se sustenta.

- A1 anterior (ids repetidos): a spec -2 vai de M7 a M12 e a -3 de M13 a M15. `forge-mutante` com a spec 1 e a -2 juntas aceita (`--ids M7`: "M7 · morreu · bin/forge-check:466"), sem a recusa de id repetido.
- A2 anterior (PQ do K-156): `ultimos_do_historico` recebe a branch nos dois chamadores (`pareceres_conferidos`, `conferidos_fora_da_ref`). `de_outra_branch` só pula o sha ilegível quando a linha cita parecer e nenhum tem o slug da branch; a linha da própria branch, ou sem parecer citado, segue ilegível (falha fechada). O teste cobre os cinco ramos, incluindo a linha mista e o nome vizinho (`x-2`). Medido neste clone, `forge-check pr v0478 --previo --base develop`: com o forge-check de 48839de0 (antes da correção), 34 linhas "o git não lê"; com o de 95994eec, 0. O rc=1 que sobra vem só dos portões desta volta, ainda pendentes (review e segurança desatualizados, QA reprovado).
- Teste do portão (EnvioDoParecer): o `next()` virou `assertEqual(len(linhas), 1)`, então na base o vermelho é uma falha de asserção e não um StopIteration.

Verificação: `PrLeParecerConferido` e `test_trilha_forge_check`: 20 OK. Mutantes da spec -3: M13, M14 e M15 morreram. `forge-mutante --cobertura --base a318e97d`: as duas guardas do diff (linhas 2431 e 2442) estão cobertas; `--conferir`: os trechos estão no lugar. Suíte completa: CI do PR.
