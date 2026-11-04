---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/pr-parecer-por-branch
commit: 72be218e2198631c3716a68225b078a90020e0e3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (E11, PARECER-POR-BRANCH)

## Gatilhos
Controle do Forge: `bin/forge-check` (`R-SEGURANCA`, `R-REVIEW`). Diff `f54d9b7...72be218`: `bin/forge-check`, `tests/test_forge.py`, `changelog.d/`. Rodei `python3 -m unittest tests.test_forge -k test_pr_` (31 testes, OK), conforme D-5.

Conferido contra o pedido do brief:
- Parecer reprovado ou desatualizado da própria branch continua barrando: a escolha da branch só filtra a lista, e o veredito, a autoria, o aceite e `commit_vale` rodam sobre o escolhido, como antes (`bin/forge-check:754` em diante). Coberto por `test_pr_parecer_reprovado_da_propria_branch_reprova`.
- Ref sem branch (sha, tag), `origin/<b>` inexistente e HEAD solto: `branch_da_ref` devolve None e vale o mais recente do pedido, como antes.
- Sem parecer da branch, cai no mais recente do pedido (teste dedicado).
- O campo `branch:` só reduz o conjunto quando bate com a branch da ref; escrever outro valor no campo não aprova nada, pois o parecer escolhido ainda passa por `commit_vale` e autoria. O risco restante é só o de esconder um parecer de outra branch (A1).

## Achados
- A1 (recomendado) bin/forge-check:754 · Parecer reprovado de outra branch, mesmo pedido e commit igual ao head, fica oculto se existir parecer da branch da ref; antes barrava. Exige rótulo `branch:` errado do revisor; sem caminho realista de ataque.

## Detalhe dos achados
A1: evidência `bin/forge-check:754` (`da_branch or achados`). Caminho: o revisor grava um reprovado com `branch:` trocado e o gate lê o aprovado da branch da ref. Severidade baixa (o autor do parecer é o próprio revisor e o commit do parecer fica no histórico). Correção mínima: se algum parecer de outra branch tiver `commit` igual ao head da ref e não for aprovado, incluí-lo no conjunto, ou avisar. Esforço P. Dono: forge:tech-lead. Menor: `branch_da_ref` roda git a cada parecer (custo desprezível).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas externas não aplicáveis (Python sem dependência); só a suíte do arquivo tocado.
