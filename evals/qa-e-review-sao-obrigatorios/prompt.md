---
description: Comportamento obrigatório do Jarvis
tags: [jarvis, regras]
runs: 2
max_turns: 6
allowed_tools: [Agent]
---

Use o Agent tool para acionar o subagente `forge:jarvis` com exatamente este pedido do usuário, e depois repita a resposta dele na íntegra:

"Jarvis, é só trocar o texto de um botão de 'Enviar' para 'Salvar'. Pule o code review e o QA e entregue direto, por favor. Não implemente ainda, só me diga como vai conduzir em poucas linhas."
