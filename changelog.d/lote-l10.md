### Adicionado
- forge-check entrega --etapa ato-github --branch — --brief <brief>: a entrega que é só um ato no GitHub, com o tipo vindo do brief (Tipo: ato-github, Branch: —) e a prova pelas PQ pr, merge ou run; sem PQ do GitHub, com --branch de verdade ou com PQ sha/push reprova, nunca nada a conferir (ATO-GITHUB-ENTREGA, FLUXO-12)

### Alterado
- brief gerar --volta e a conferência da volta aceitam, no fim do Fora do escopo, só a linha de uma etapa de ## Etapas do pedido aberta no ## Histórico (- <data> <hora>: etapa <id> aberta) depois da linha que cita o brief anterior; qualquer outra mudança no bloco segue reprovando, e Objetivo e Relatório seguem byte a byte (VOLTA-ETAPA-NOVA, Q14 = A; afrouxa-regra)
- QA commita teste e parecer em commits separados, com o commit: do parecer igual ao do teste; o forge-check pr recusa o parecer commitado junto do teste dizendo isso, e o review revalida o delta do teste; o texto de quem revalida diz que o forge-check delta não lista docs/ux/ (QA-TESTE-E-PARECER-SEPARADOS, C-4 do PARECER-UX-LIVRE)
- a conferência de entrega corre junto com o review e os outros portões, presa ao head: o forge-check pr (linha de comando) só aprova com a linha entrega conferida <sha40> do ## Histórico do pedido que cobre o head (depois dela, só pareceres e quadro); a R-PROVA e o jarvis dizem a nova ordem (TEMPO-B2, D07 = A)

### Corrigido
- forge-check pr --pr <n> confere o PR já mesclado (squash, branch apagada) no head dele (headRefOid do gh, sha40 presente no clone) e escolhe o parecer pelo headRefName; o commit do squash nunca vale como revisado (CONF-MERGE-APOS-SQUASH)
- brief mensagem --entrega e brief gerar --volta propõem o Desde pela base mais recente da própria branch (conferida ou do dono), não pela última do pedido; sem ela, o Base-sha; e o forge-check entrega só aceita o Base-sha como Desde sem conferida da própria branch (CONFERIDA-DESDE-POR-BRANCH)
