### Adicionado
- forge-check entrega confere o escopo da entrega só pelo intervalo da delegação (--desde a partir da linha conferida <sha40> do Histórico do pedido, que só o Jarvis grava; branch inteira nas etapas pr e merge), forge-check delta e brief --anterior mostram o que mudou entre rodadas, e brief gerar --volta monta o brief de volta dos achados bloqueantes dos pareceres (bloco ## Achados) com Volta-de e sha256, conferido por forge-check brief; o PQ de merge do brief de integração prova por git merge-base --is-ancestor (VV-2)

### Alterado
- Hooks: docs/pedidos/ e docs/briefs/ (e as cópias em ~/.forge-contrib/docs/) passam a ser só do Jarvis; o conferente roda forge-check entrega e delta sem herdar opção que grave arquivo (VV-2)
- forge-check: a lista de arquivos da entrega lê o diff com -z, então nome com acento chega sem aspas aos gatilhos e ao forge-check pr; brief --anterior aceita o brief em ~/.forge-contrib/docs/briefs/ como o --volta; os modelos de parecer de segurança, review e QA trazem o bloco ## Achados no formato lido por máquina (VV-2)
