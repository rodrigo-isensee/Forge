---
name: trabalho-em-paralelo
description: Como o Jarvis dispara, espera e acompanha entregas em paralelo (série por arquivo, quadro com hora real, instância por item, lote). Use ao disparar, esperar, mover cartão ou montar lote.
---

# Trabalho em paralelo

L51: texto do Jarvis lido no passo.

- **Série só por arquivo em comum:** rode `bin/forge-check sobreposicao` antes do disparo. Itens com arquivo em comum não andam em paralelo: vão juntos (lote por arquivo) ou o segundo espera o primeiro entrar. Portão sem retorno em 53 min: pare e relance, depois de conferir que o anterior parou.
- `R-TETO` e `R-WIP` sempre: teto adaptativo, pesado um por vez, 1 cartão por agente. Fila atrás de um papel: suba mais instâncias iguais dele, uma por item independente, cada uma com worktree e cartão (`worktree: <nome>` na Obs.), no teto.
- **Quadro com hora real:** cada mudança de cartão vai por `forge-check movimento <cartão> --de <coluna> --para <coluna> [--motivo <texto>]` (motivo `volta <n>` ao autor; `Aguardando o dono` na ida e na volta). `## Histórico` e decisões do dono: `forge-check anotar`. Espera do usuário: `R-DECISAO` painel "Aguardando o dono".
- **Delegação que edita `agents/*.md`:** sem permissão para `agents/**`, o auto recusa: avise o dono e diga no brief; o recusado relata e para, sem contornar (`R-CONFORMIDADE`).
- **Integração contínua (D2):** o PR abre com os pareceres aprovados no head; CI verde, entra na `develop` (`R-FLUXO`).
- **Lote por arquivo:** itens decididos no mesmo arquivo podem ir numa branch, um commit por item com seus testes, portões uma vez e um PR que cita os itens; item com defeito sai por revert; o à espera do dono não entra; nenhum portão cai.
- **Lote de até 3 tópicos (D3):** pequenos, sem arquivo em comum, nas regras do lote por arquivo.
- **Tamanho por risco:** 150 linhas alteradas de código e teste por PR orientam; uma classe de comportamento por PR em `hooks/`, com corpus próprio.
- **Medidas do pedido:** no fim, cole `forge-check transcricao custo --entregas --entrega <pedido> --pedido <pedido>` e `forge-check esperas --pedido <pedido>` em `docs/kanban/entregas.md`; defeito visto após o parecer final: `forge-check escape registrar` na hora.
- **Retomada:** liste os briefs selados sem relatório, leia o estado de cada branch (commits e trabalho sem commit no clone) e relance cada agente do ponto em que parou, sem refazer o feito.
- **Anda sozinho:** nunca peça para ser chamado. Espere hora ou estado (agente, CI, merge, memória) com `run_in_background` e o prazo no comando, `fim=$((SECONDS+N)); until <condição> || [ $SECONDS -ge $fim ]; do sleep 60; done`; encha as vagas; vencido o prazo, confira o estado. Vale para o Jarvis; subagente segue a skill `esperar-estado`. Pausa por limite de uso (Q1): nada novo é disparado, só conferências e integradores; grave onde parou (`forge-check pausa --gravar`); `pausa --retomar --esperar` retoma com a cota nova. Medida: zero pedidos de "me chame" ou "continue".
