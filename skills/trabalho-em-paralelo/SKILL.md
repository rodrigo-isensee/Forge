---
name: trabalho-em-paralelo
description: Como o Jarvis dispara, espera e acompanha entregas em paralelo (série por arquivo em comum, quadro com hora real, uma instância por item, lote por arquivo, integração contínua). Use antes de disparar entregas, ao esperar hora ou estado, a cada mudança de cartão e ao juntar itens num lote.
---

# Trabalho em paralelo

Texto do Jarvis lido no passo (L51, núcleo curto).

- **Série só por arquivo em comum:** rode `bin/forge-check sobreposicao` antes do disparo. Branches com arquivo em comum se serializam: a segunda começa já e traz a `develop` uma vez, após a primeira entrar; as outras seguem em paralelo. Portão sem retorno em 53 min: pare e relance quando o anterior não rodar mais.
- `R-TETO` e `R-WIP` sempre: teto adaptativo, pesado um por vez, 1 cartão por agente. Fila atrás de um papel (gargalo): suba mais instâncias iguais dele, uma por item independente, cada uma na sua worktree e no seu cartão (`worktree: <nome>` na Obs.), enquanto couber no teto. A volta vai à mesma instância; o portão usa o CI do PR se ele cobre.
- **Quadro com hora real:** cada mudança de estado de cartão vai por `forge-check movimento <cartão> --de <coluna> --para <coluna> [--motivo <texto>]` (motivo `volta <n>` na volta ao autor; `Aguardando o dono` na ida e na volta). Linhas do `## Histórico` e decisões do dono, por `forge-check anotar`. Espera do usuário: painel (`R-DECISAO` painel "Aguardando o dono"). Onde um pedido está: `forge-check proximo <pedido>`.
- **Delegação que edita `agents/*.md`:** sem permissão para `agents/**`, o modo auto recusa: avise o dono antes e diga no brief; o recusado relata e para, sem contornar por script (`R-CONFORMIDADE`).
- **Integração contínua (D2):** item com os pareceres da classe aprovados e CI verde entra na `develop` na hora (`R-FLUXO`).
- **Lote por arquivo:** itens decididos no mesmo arquivo podem ir numa branch, um commit por item com os testes dele, portões uma vez e um PR que cita os itens; item com defeito sai por revert do commit; item à espera do dono não entra. Nenhum portão cai.
- **Lote de até 3 tópicos (D3):** tópicos pequenos sem arquivo em comum, com as regras do lote por arquivo.
- **Tamanho por risco:** 150 linhas alteradas de código e teste por PR orientam; pesa o risco. Vale uma classe de comportamento por PR em `hooks/`, com corpus próprio.
- **Medidas do pedido:** no fim, cole `forge-check transcricao custo --entregas --entrega <pedido> --pedido <pedido>` e `forge-check esperas --pedido <pedido>` em `docs/kanban/entregas.md`; defeito visto após o parecer final: `forge-check escape registrar` na hora.
- **Anda sozinho:** nunca peça para ser chamado. Espere hora ou estado (registro de agente expirar, CI, merge, memória) com `run_in_background` e `until <condição>; do sleep 60; done` com prazo, e encha as vagas. Pausa por limite de uso (Q1): só conferências e integradores, `forge-check pausa --gravar` e `--retomar --esperar`. Medida: zero pedidos de "me chame" ou "continue".
