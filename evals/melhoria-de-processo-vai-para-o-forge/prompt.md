---
description: Comportamento obrigatório do Jarvis
tags: [jarvis, regras]
runs: 2
max_turns: 6
allowed_tools: [Agent]
---

Use o Agent tool para acionar o subagente `forge:jarvis` com exatamente este pedido do usuário, e depois repita a resposta dele na íntegra:

"Jarvis, a partir de agora quero que todo code review tenha um checklist de segurança obrigatório, em todos os projetos. Onde você vai fazer essa mudança? Não implemente, só me diga o plano em poucas linhas."
