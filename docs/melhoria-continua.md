# Melhoria contínua por entrega

Objetivo: a cada entrega o time (arquitetura, UX, back, front, QA, tech lead, Jarvis) gasta menos tokens, entrega mais e erra menos. Métricas são do processo, nunca de agente ou pessoa. Experimentos vão para `docs/kanban/melhorias.md` (próximo ID: M-014).

## a) Mecanismo (fim de cada entrega, 15 min no máximo)
1. **Registro por papel** (Jarvis pede no fechamento do PR; cada papel responde em até 3 linhas no relatório final do subagente): `custou caro` (tokens, tempo, releitura), `deu retrabalho` (o que voltou e por quê), `melhoria proposta` (mudança exata).
2. **Consolidação** (agile-coach): junta as respostas em `docs/retrospectivas/AAAA-MM-DD-<pedido>.md`, agrupa por causa e escolhe **no máximo 3 experimentos**, cada um com dono, métrica, linha de base, critério de sucesso (ex.: "tokens do QA -20% sem subir escapes") e **critério de reversão** (um fato observável que o desfaria, ex.: "escapes sobem 2 entregas seguidas"). Mecanismo novo (hook, regra, ferramenta) traz também "por que o existente não basta", com evidência de execução.
3. **Reavaliação** na entrega seguinte: cada experimento termina em manter, ajustar ou reverter, anotado em `melhorias.md` como leitura (data, medida, veredito) contra o critério de reversão. Uma mudança por vez por parte do processo. Mudança no `CLAUDE.md` do projeto só entra após aprovação do usuário; mudança em agente ou skill nunca é copiada para o projeto: vira PR no Forge.
4. Retrospectiva sem dados não vale: se a métrica não foi coletada, o primeiro experimento é coletá-la.

## b) Métricas (planilha única `docs/kanban/entregas.md`, uma linha por entrega)
| Métrica | Como coletar | Quem |
|---|---|---|
| Tokens por agente por entrega | `forge-check transcricao custo --entregas --entrega <pedido>`, lido das transcrições locais: inclui a sessão principal do Jarvis e as compactações; sem transcrição, `subagent_tokens` do relatório, anotado à mão | Jarvis roda no fim do pedido |
| Retrabalho de delegação | `relancamentos` do mesmo comando: agente relançado com o mesmo tipo e prompt (hash), por pedido | agile-coach |
| Rodadas de review e de QA | contar `docs/reviews/*-rN.md` e `docs/qa/` da entrega | agile-coach |
| Bugs por entrega e onde nasceram | pareceres por severidade; origem = fase (spec, arquitetura, código, teste, UX) | agile-coach |
| Tempo de ciclo | `historico.md` (valores brutos até 20 itens) | agile-coach |
| Falhas de CI por entrega | `gh run list --json conclusion` filtrado pela branch | tech-lead |
| Retrabalho | commits `fix:` na branch após o primeiro review; pais devolvidos | tech-lead |
| Escapes | bugs achados após o parecer do QA | qa-engineer |
| M1: afirmações sem lastro por relatório de subagente | `forge-check transcricao lastro`: sha, PR, push, mescla e "N testes OK" que não aparecem nas saídas de ferramenta do próprio subagente; mescla só tem lastro com prova de merge do PR citado (`state` MERGED, `mergedAt` não nulo ou saída de `gh pr merge`) e "N testes OK" só com `Ran N tests` seguido de `OK`; negação ("não mesclei") não conta como afirmação; saída de `git fetch` não prova push (F1). Limite: o lastro exclui o prompt de delegação (um sha que veio dele e foi citado conta como sem lastro). Linha de base remedida depois da correção do parecer do #120: 113 de 832 afirmações (13,6%), em 274 relatórios, nas transcrições locais do Forge em 2026-10-14 (a primeira medida, frouxa, deu 14,5%). Meta: -80% em 10 entregas | tech-lead |
| M3: respostas do Jarvis com mais de uma decisão ou sem "Recomendo" | `forge-check transcricao decisoes`: grupos de opções A/B/C fora de código e citação; só mede (F1). Linha de base: 0 de 434 respostas (27 com grupo de opções), mesma fonte e data. Fixtures para a fatia 3: lista de passos `A.` `B.` `C.` vira "decisão sem Recomendo" e opções na mesma linha ("A) x; B) y") não são vistas. A heurística só pega opções rotuladas A/B/C; decisões em texto livre ou lista numerada não entram | tech-lead |
