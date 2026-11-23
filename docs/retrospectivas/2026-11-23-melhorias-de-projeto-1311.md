# Retrospectiva do pedido melhorias-de-projeto-1311

Cobre: v0.47.1
Autor: agile-coach, etapa E116.2 do v0478, 2026-11-23. Janela: 2026-11-13T13:07-03:00 (primeiros briefs selados) a 2026-11-14T21:34-03:00 (última linha do `## Histórico`). Marcas de `R-DECISAO`: `medido` (com o comando), `estimado` (com a base), `não medido`.

## 1. Dados do pedido
Retro atrasada: a tag v0.47.1 saiu em 2026-11-15T08:58-03:00 (`git log -1 --format=%cI v0.47.1`). O pedido levou à fábrica 12 melhorias de um projeto que usava a 0.46.0 (itens 1, 2, 3, 9 e 11 na 0.47.1; 5, 6, 7, 8 e 12 na 0.47.2; 4 e 10 no pacote node-react). A tag v0.47.2 não existe neste clone; só a v0.47.1 entra em `Cobre:`.

| Dado | Valor | Marca |
|---|---|---|
| Etapas do pedido | 99 (E1: 61, E2: 27, E3: 11) | medido (`grep -cE "^- E[0-9]+\.[0-9]+ "` em `docs/pedidos/melhorias-de-projeto-1311.md`) |
| PRs mesclados com `mp1311` na branch ou no título | 9 (#533, #534, #536, #539, #544, #551, #554, #555, #563), de 13/11 16:49 a 15/11 09:31 | medido (`gh pr list --state merged --search "merged:2026-11-13..2026-11-23"`, filtro por `mp1311`) |
| Lead time do PR (abertura → merge) | P50 2,4 h, máximo 19,9 h (n=9, valores, sem percentil) | medido, mesmo comando |
| Frequência | 9 PRs em ~1,7 dia | medido |
| Retrabalho | 50 linhas do pedido citam volta ou revisão por delta; contagem de cartões devolvidos não medida | estimado (`grep -ciE "volta (única\|curta)\|por delta"`); `forge-check retro --pedido melhorias-de-projeto-1311`: `lead=nao-medido p85=nao-medido(n=0) voltas-classe=nao-medido escapes=0` |
| PRs vermelhos no CI citados | 24 linhas do pedido citam "vermelh*"; causas: #539 defeito real do forge-fechar (`refs/heads/`), #554 herdado da develop | estimado (`grep -ic vermelh`) |
| ERRO-JARVIS no pedido | 2 (15:27 portões do item 12 não disparados; 17:50 E2.16 já entregue e quase delegada de novo) | medido (`grep -c "ERRO-JARVIS:"`) |
| `Melhoria vista:` com problema | 2 (`forge-check docs` recusa achado resolvido em `## Achados`; PQ do pre-push sem stdin não prova nada) | medido |
| Clareza (perguntas, "não entendi", escopo+/-, devolvidas) | não medido | o pedido não tem a seção "Registro de clareza" |
| DORA: taxa de falha e recuperação | não medido | sem vínculo de `fix` a PR do pedido |

Linha de métricas e resumo do `forge-placar --dias 14` (medido; janela de 09/11 a 23/11, que inclui este pedido): `taxa_reprovacao: atual - · anterior 35.39%`, `voltas_por_item: atual 0.00% · anterior 73.66%`, `taxa_escape: atual 0.00% · anterior 0.37%`.
`resumo: os erros de forma do time caíram 100%; os defeitos que escaparam caíram 100%`
Ressalva: base atual com `vereditos=0`: a queda é falta de dado; na base anterior, 73,66% de voltas por item é o dado real da época deste pedido.

## 2. O que funcionou
- A cada item, conferir na develop se já estava feito (a suposição do pedido, vinda dos ERRO-JARVIS de 13/11) evitou nova entrega duplicada: o brief da E2.16 foi descartado sem disparo (`docs/pedidos/melhorias-de-projeto-1311.md`, 13/11 17:50).
- Defeito real achado por teste, não por opinião: #539 mostrou que o `forge-fechar` devolve `refs/heads/` no nome; o dono decidiu a correção dos testes e do mapa (DECISÃO DO DONO 13/11 19:52).
- Diretriz 23 do dono virou critério mensurável de envio (PQ-1, PQ-2 e, quando muda bin/hooks/scripts/tests, PQ-3).

## 3. O que atrapalhou
- Volume: 99 etapas para 12 itens, boa parte em ciclos de review/segurança/QA por delta (50 linhas citam volta), e 24 menções a CI vermelho.
- Quedas de sessão exigiram etapas de retomada (E1.46 a E1.48) para enviar commits locais.
- A entrega duplicada quase aconteceu (ERRO-JARVIS 17:50), com 31 linhas reescritas em `agents/jarvis.md`.
- O vermelho do #554 vinha da develop, não do item (corrigido em #558): CI vermelho herdado atrasa PR sem culpa do PR; o PR-VERDE-DE-PRIMEIRA nasceu daqui (ver a retro do pedido).

## 4. Causa nova (no máximo 1) e a proposta
Sem proposta aberta nova (`docs/kanban/melhorias.md` não existe). Causa registrada como dado: "entrega já feita quase delegada de novo" é a mesma classe do cartão JARVIS-CONFERE-ESTADO-ANTES (aberto nesta rodada, ver a retro da 0.47.14); não abro segunda causa. O pedido tem 2 ERRO-JARVIS e 2 `Melhoria vista:`, todos candidatos.

| Linha `Melhoria vista:` | Classe | Destino |
|---|---|---|
| `forge-check docs` recusa achado resolvido em `## Achados` | candidata | triagem (a conferir se já existe cartão) |
| PQ do pre-push afetados sem stdin não prova nada | candidata | coberta pela diretriz 23 e pelo `forge-testes --registros` (PR-VERDE B1) |

## 5. Revisão das propostas vencidas
Nenhuma proposta vencida. Pedido de 13/11; o placar de 14 dias não o isola, então não há `forge-placar comparar` a rodar.
