---
name: briefs-e-conferencia
description: Brief selado e entrega conferida pela ferramenta (R-BRIEF, R-PROVA), com o conferente opcional para dúvida de conteúdo. Use antes de cada delegação a um agente, ao receber a entrega de um agente e ao montar o brief de volta.
---

# Brief selado e entrega conferida

Texto do Jarvis (L51). A forma é da ferramenta; não se repete aqui.

## Antes de delegar (`R-BRIEF`)
1. `forge-check brief gerar --pedido <p> --destino forge:<nome> --branch <b> --gravar` monta o brief do pedido e do desenho, com base, `Desde:`, etapa e decisões do dono por referência. Nunca parta de outro brief.
2. Preencha só o que é da tarefa (Objetivo, Ler, Entregar, Pronto quando); até 10.000 caracteres, senão o selo reprova. Skill `checagem-do-brief`: o que a ferramenta não sabe. Worktree de outra sessão é só leitura no sandbox: crie a sua antes de delegar (senão o brief avisa e oferece `update-branch`). Se não gravar, use um clone local: `git clone -q <repo> ~/.forge-contrib/wt/<nome>-c`, `origin` no GitHub, branch da `origin/develop`.
3. `forge-check brief selar --arquivo <brief> --pedido <p>`: reprovado, corrija o que ele aponta e rode de novo; aprovado, ele grava o selo e imprime o hash.
4. Delegue citando o caminho do brief e o hash do selo. O hook `agentes` recusa brief sem selo ou com hash diferente em todo tipo que escreve (fora conferente e `Explore`). Brief editado pede selo novo. Uma delegação de escrita por branch (Z10); o parecer roda junto.

O `forge:conferente` é opcional: chame-o só com uma dúvida de conteúdo que a ferramenta não decide (o Entregar é fiel ao pedido? contradiz uma decisão?), com a mensagem de `forge-check brief mensagem`.

## Ao receber a entrega (`R-PROVA`)
- `forge-check entrega --pedido <p> --branch <b> --etapa <etapa>`: confere o estado real, roda os PQ que sabe conferir e grava a linha `entrega conferida <sha40>` no `## Histórico`. Nunca escreva essa linha à mão; `--sem-gravar` só confere (o PQ do autor), `--so-leitura` sem PQ `cmd` (o conferente).
- Compare a saída com o bloco `Provas:` do relatório; divergência volta ao autor.
- Depois, `forge-check classe` e os portões da classe numa passada, em paralelo, no mesmo head (`R-REVIEW`).

## Brief de volta
Os achados bloqueantes de review, segurança e QA viram **um** brief de volta: `forge-check brief gerar --pedido <p> --volta <brief anterior> --ref <branch> --parecer <arquivo>...`, selado como qualquer outro. Recomendação não entra. A revalidação de cada parecer lê só `forge-check parecer delta <parecer>`.

## Brief que manda escrever parecer
Avise que o achado tem até 300 caracteres e que regra se cita pelo ID, não copiada (o `forge-check docs` e o pre-push barram).
