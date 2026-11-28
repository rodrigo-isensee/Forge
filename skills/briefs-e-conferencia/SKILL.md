---
name: briefs-e-conferencia
description: Brief selado e entrega conferida pela ferramenta (R-BRIEF, R-PROVA), com o conferente opcional para dúvida de conteúdo. Use antes de cada delegação a um agente, ao receber a entrega de um agente e ao montar o brief de volta.
---

# Brief selado e entrega conferida

Texto do Jarvis (L51); a forma é da ferramenta.

## Antes de delegar (`R-BRIEF`)
1. `forge-check brief gerar --pedido <p> --destino forge:<nome> --branch <b> --gravar` monta o brief do pedido e do desenho, com base, `Desde:`, etapa e decisões do dono por referência. Nunca parta de outro brief.
2. Preencha só o que é da tarefa (Objetivo, Ler, Entregar, Pronto quando); até 10.000 caracteres, senão o selo reprova. PQ de teste: a forma de `skills/qa-testing/comandos.md` ('Um módulo de teste'). Leia a skill `checagem-do-brief` para o que a ferramenta não sabe (estado do remoto, credencial, efeito fora da worktree). A worktree de outra sessão é só leitura: crie a sua antes de delegar (senão o brief avisa e oferece `update-branch`). Se não gravável: clone local `git clone -q <repo> ~/.forge-contrib/wt/<nome>-c`, `origin` no GitHub e branch da `origin/develop`.
3. `forge-check brief selar --arquivo <brief> --pedido <p>`: reprovado, corrija o apontado e rode de novo; aprovado, ele grava o selo e imprime o hash.
4. Delegue citando o caminho do brief e o hash do selo. O hook `agentes` recusa brief sem selo ou com hash diferente em todo tipo que escreve (fora conferente e `Explore`). Brief editado pede selo novo. Uma delegação de escrita por branch (Z10); o parecer roda junto.

O `forge:conferente` é opcional: chame-o só com dúvida de conteúdo que a ferramenta não decide, com a mensagem de `forge-check brief mensagem --arquivo <brief> --pedido <p>`.

## Ao receber a entrega (`R-PROVA`)
- `forge-check entrega --pedido <p> --branch <b> --etapa <etapa> --worktree <cópia>`: confere o estado real, roda os PQ que sabe conferir e grava a linha `entrega conferida <sha40>` no `## Histórico`. Nunca escreva essa linha à mão. Opções, D2, PR e rótulo: `conferencia-da-entrega.md` nesta skill.
- Compare a saída com o bloco `Provas:` do relatório; divergência volta ao autor.
- Depois, `forge-check classe` e os portões da classe numa passada, em paralelo, no mesmo head (`R-REVIEW`).

## Brief de volta
Os bloqueantes de review, segurança, QA, o recomendado da segurança e o CI vermelho viram **um** brief de volta. Ele vai ao autor da branch, retomado por `SendMessage` até o merge (H2; comando e detalhe em `autor-ate-o-merge.md` nesta skill), revalidação inclusa. Sem `gh run rerun` à toa (`R-CUSTO`).

## Brief que manda escrever parecer
Avise da receita de `envio-de-parecer.md` nesta skill (achado, ID de regra, envio).
