---
name: trabalho-em-paralelo
description: Como o Jarvis dispara e acompanha entregas em paralelo no Forge e nos projetos (série por arquivo em comum, quadro com hora real, fila atrás de um agente, lote por arquivo, integração contínua). Use antes de disparar entregas em paralelo, a cada mudança de estado de um cartão e ao juntar itens num lote.
---

# Trabalho em paralelo

Texto do Jarvis lido no passo (L51, núcleo curto).

- **Série só por arquivo em comum:** rode `bin/forge-check sobreposicao` antes do disparo. Branches com arquivo em comum se serializam na junção (a segunda começa já e traz a `develop` uma vez, depois que a primeira entrou); as outras seguem em paralelo. Portão sem retorno em 53 min é parado e relançado, depois de conferir que o anterior não roda mais.
- `R-TETO` e `R-WIP` sempre: teto adaptativo, pesado um por vez, 1 cartão por agente. Fila atrás de um agente (gargalo): suba mais instâncias iguais dele, cada uma na sua worktree e no seu cartão (`worktree: <nome>` na Obs.), enquanto couber no teto.
- **Quadro com hora real:** cada mudança de estado de um cartão vai por `forge-check movimento <cartão> --de <coluna> --para <coluna> [--motivo <texto>]` (volta ao autor com motivo `volta <n>`; espera do dono com motivo `Aguardando o dono` na ida e na volta). Linhas do `## Histórico` e decisões do dono, por `forge-check anotar`. Espera do usuário vai ao painel (`R-DECISAO` painel "Aguardando o dono"). Para saber onde um pedido está, `forge-check proximo <pedido>`.
- **Delegação que edita `agents/*.md`:** sem a regra de permissão para `agents/**`, o modo auto recusa a edição: avise o dono antes e diga no brief; o agente recusado relata e para, sem contornar por script (`R-CONFORMIDADE`).
- **Integração contínua (D2):** o item com os pareceres da classe aprovados e o CI verde entra na `develop` na hora (`R-FLUXO`).
- **Lote por arquivo:** itens decididos que mexem no mesmo arquivo podem ir numa branch, um commit por item com os testes dele, os portões uma vez e um PR que cita os itens; item com defeito sai por revert do seu commit; item à espera de decisão do dono não entra. Nenhum portão cai.
- **Lote de até 3 tópicos (D3):** até 3 tópicos pequenos sem arquivo em comum, com as regras do lote por arquivo.
- **Tamanho por risco:** cerca de 150 linhas alteradas de código e teste por PR orientam, sem travar; pesa o risco (classe C). Vale uma classe de comportamento por PR em `hooks/`, com corpus próprio.
- **Medidas do pedido:** no fim, cole `forge-check transcricao custo --entregas --entrega <pedido> --pedido <pedido>` e `forge-check esperas --pedido <pedido>` em `docs/kanban/entregas.md`; defeito achado depois do parecer final vai por `forge-check escape registrar` na hora.
- **Pausa por limite de uso (Q1):** na pausa por limite de uso só seguem conferências e integradores; nada novo é disparado. Grave onde parou (`forge-check pausa --gravar`); `pausa --retomar --esperar` em segundo plano retoma com a cota nova.
