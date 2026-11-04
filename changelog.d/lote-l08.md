### Corrigido
- forge-check pr --pr <n> confere o PR já mesclado (squash, branch apagada) no head dele (headRefOid do gh, sha40 presente no clone) e escolhe o parecer pelo headRefName; o commit do squash nunca vale como revisado (CONF-MERGE-APOS-SQUASH)
- brief mensagem --entrega e brief gerar --volta propõem o Desde pela base mais recente da própria branch (conferida ou do dono), não pela última do pedido; sem ela, o Base-sha; e o forge-check entrega só aceita o Base-sha como Desde sem conferida da própria branch (CONFERIDA-DESDE-POR-BRANCH)

### Alterado
- QA commita teste e parecer em commits separados, com o commit: do parecer igual ao do teste; o forge-check pr recusa o parecer commitado junto do teste dizendo isso, e o review revalida o delta do teste; o texto de quem revalida diz que o forge-check delta não lista docs/ux/ (QA-TESTE-E-PARECER-SEPARADOS, C-4 do PARECER-UX-LIVRE)
