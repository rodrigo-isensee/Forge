# Retrospectiva do pedido pr-verde-de-primeira

Tags: nenhuma própria (as entregas saíram nas v0.47.12, v0.47.13 e v0.47.14, cobertas pelas retros de versão)
Autor: agile-coach, etapa E116.2 do v0478, 2026-11-23. Janela: 2026-11-20T10:50-03:00 (pedido aberto) a 2026-11-23. Marcas de `R-DECISAO`: `medido` (com o comando), `estimado` (com a base), `não medido`.

## 1. Dados do pedido
Meta do pedido: PR verde na 1.ª execução, de cerca de 57% para 85%. De partida, o Controlador mediu 52 de 121 execuções de PR vermelhas desde 17/11 (43%).

| Dado | Valor | Marca |
|---|---|---|
| Verde na 1.ª execução, total dos 30 dias | 43,42% (66/152); vermelhos: CI 27, Catraca 68; cancelados 21; lacunas 331 | medido (`gh run list --event pull_request --limit 1000 --json ...` e `gh pr list --state all --limit 1000 --json ...` gerados fora, depois `forge-placar ci-primeira --runs ... --pr-lista ... --dias 30`) |
| Verde na 1.ª por dia depois da entrega | 20/11: 46,67% (14/30); 21/11: 44,83% (13/29); 22/11: 62,50% (15/24) | medido (mesma saída); antes, 18/11: 25,00% (4/16); 19/11: 12,50% (2/16) |
| Meta (85%) | não atingida; o melhor dia medido é 62,5% | medido (mesma saída) |
| PRs mesclados de PV | 10 (#725, #727, #730, #733, #738, #739, #741, #744, #746, #749), de 20/11 18:03 a 21/11 04:10; lead P50 0,3 h, máximo 1,9 h (n=10) | medido (`gh pr list --state merged --search "merged:2026-11-13..2026-11-23"`, filtro `PR-VERDE`/`PV-`) |
| Itens do escopo com entrega visível no `CHANGELOG.md` | PV-A (OK do dono preso ao commit, 0.47.12; A2 parcial, 0.47.13), PV-B (`forge-testes --registros`, 0.47.12; `--regerar` e patch do envio, 0.47.13), PV-C (pesos por PR, 0.47.12), PV-D (`forge-testes --versoes`, 0.47.13) | medido (`CHANGELOG.md`) |
| Lead time do pedido, voltas por classe, escape | não medido | `forge-check retro --pedido pr-verde-de-primeira`: `lead=nao-medido p85=nao-medido(n=0) voltas-classe=nao-medido escapes=0 custo=lacuna` |
| Clareza | não medido | sem seção "Registro de clareza" |

Linha de métricas e resumo do `forge-placar --dias 14` (medido; 09/11 a 23/11): `taxa_forma: atual 0.00% · anterior 68.98%`, `pronto_ate_develop: atual 728 min · anterior 175 min`.
`resumo: os erros de forma do time caíram 100%; os defeitos que escaparam caíram 100%`
Ressalva: base atual `vereditos=0`; o `resumo:` do placar não mede o objetivo deste pedido. A medida que vale é o `ci-primeira`, acima.

## 2. O que funcionou
- A medida do próprio objetivo existe (`forge-placar ci-primeira`, PR-VERDE M1) e é reproduzível sem serviço pago, só com `gh` de leitura.
- A tendência após a entrega é de alta no que medimos: de 12,5% (19/11) a 62,5% (22/11).
- As quatro frentes tiveram PR (10 mesclados, P50 de 18 min) e entraram em três versões seguidas.

## 3. O que atrapalhou
- A meta de 85% não foi atingida; o total de 30 dias (43,42%) fica abaixo da partida citada no pedido (57%) porque a janela inclui os dias anteriores à entrega e a base de partida do pedido é de outra conta (121 execuções desde 17/11): os dois números não são comparáveis; `estimado`.
- A Catraca é o maior vermelho: 68 de 95 vermelhos (71%) e 11 a 13 por dia em 20/11 e 21/11, contra 4 em 22/11. O PV-A (OK do dono preso ao commit) estava previsto para esse sintoma e só entrou em parte (A2 parcial na 0.47.13).
- 331 lacunas: a saída do `ci-primeira` marca muita execução sem o workflow exigido no 1.º head; o número verde é um piso incerto, não o valor exato.
- 21 execuções canceladas pelo avanço da develop não contam como verde nem vermelho.

## 4. Causa nova (no máximo 1) e a proposta
Causa nova candidata: a Catraca vermelha na 1.ª execução (68 de 152). Proposta para o tech-lead abrir (não há proposta aberta; `docs/kanban/melhorias.md` não existe): Métrica: `forge-placar ci-primeira`, vermelhos por workflow Catraca por dia (hoje 4 em 22/11, 11 a 13 em 20/11 e 21/11) e verde na 1.ª; meta do pedido 85%; critério de reversão: se o verde na 1.ª cair abaixo de 40% em 7 dias seguidos. Mudança, Início e Revisão ficam para o tech-lead, que desenha o código (R-DECISAO: sem regra nova em texto). Como a causa já está no escopo PV-A, não abro cartão novo: o dado vai ao pedido, e a decisão é do tech-lead.

| Linha `Melhoria vista:` do pedido | Classe | Destino |
|---|---|---|
| nenhuma no `## Histórico` do pedido | não medido | o pedido só tem a linha de abertura |

## 5. Revisão das propostas vencidas
Nenhuma proposta vencida. Próxima leitura sugerida: `forge-placar ci-primeira` com `--ate` em 7 dias, para ver se os 62,5% de 22/11 se sustentam.
