---
name: trabalho-em-paralelo
description: Como o Jarvis dispara, espera e acompanha entregas em paralelo (série por arquivo, quadro com hora real, instância por item, lote). Use ao disparar, esperar, mover cartão ou montar lote.
---

# Trabalho em paralelo

L51: texto do Jarvis lido no passo.

- **Série só por arquivo em comum:** rode `bin/forge-check sobreposicao` antes. Itens com arquivo em comum não andam em paralelo (serializam): vão num lote ou o segundo espera o primeiro entrar e traz a `develop` uma vez. Portão mudo há 53 min: confira que parou e relance.
- `R-TETO` e `R-WIP` sempre: teto adaptativo, pesado um por vez, 1 cartão por agente. Fila atrás de um papel: suba mais instâncias iguais dele, uma por item independente (`worktree: <nome>` na Obs.) até o teto (`ritmo-e-corte.md`).
- **Quadro com hora real:** mova o cartão com `forge-check movimento <cartão> --de <coluna> --para <coluna> [--motivo <texto>]` (motivo `volta <n>` ao autor; `Aguardando o dono` na ida e volta). Linhas do `## Histórico` e decisões do dono, por `forge-check anotar --pedido <p> --tipo <tipo> --literal <fala>`. Espera do usuário: `R-DECISAO` painel "Aguardando o dono". Onde está: `forge-check proximo <pedido>`.
- **Delegação que edita `agents/*.md`:** sem permissão em `agents/**`, o modo auto recusa: avise o dono antes e diga no brief; o recusado relata e para sem contornar (`R-CONFORMIDADE`).
- **Integração contínua (D2):** o PR abre com os pareceres da classe aprovados no head e a entrega conferida; com CI verde, entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`).
- **Correção antes dos portões:** toda, nunca após o último parecer (`recomendado` de review e QA vira cartão: `R-REVIEW`).
- **Lote por arquivo:** itens do mesmo arquivo numa branch e um PR; regras em `ritmo-e-corte.md`.
- **CI pago** (`R-CUSTO`): antes de push ou `gh run rerun`, leia `ritmo-e-corte.md`.
- **Lote de até 3 (D3):** sem arquivo comum; integrar e promover: `docs/fechamento-integrador.md`.
- **H1:** até 150 linhas de código, fora testes e documentação; passa só se cortar mais deixa a suíte vermelha; uma classe de comportamento por PR em `hooks/`, com corpus próprio.
- **Medidas do pedido:** no fim, cole `forge-check transcricao custo --entregas --entrega <pedido> --pedido <pedido>` e `forge-check esperas --pedido <pedido>` em `docs/kanban/entregas.md`; defeito após o parecer final: `forge-check escape registrar` na hora.
- **Anda sozinho:** nunca peça para ser chamado. Espere hora ou estado com `run_in_background` e o prazo no comando, `fim=$((SECONDS+N)); until <condição> || [ $SECONDS -ge $fim ]; do sleep 60; done`, e encha as vagas sem esperar a versão (`R-WIP`); vencido o prazo, confira o estado; subagente segue a skill `esperar-estado`. Pausa por limite de uso (Q1): nada novo é disparado, só conferências e integradores; grave onde parou (`forge-check pausa --gravar`); `pausa --retomar --esperar` retoma na cota nova. Medida: zero pedidos de "me chame" ou "continue".
