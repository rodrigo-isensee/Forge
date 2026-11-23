# Retrospectiva do pedido melhorias-anti-erro

Tags: nenhuma própria (as entregas saíram nas v0.47.12, v0.47.13, v0.47.14 e v0.47.15, cobertas pelas retros de versão)
Autor: agile-coach, etapa E116.2 do v0478, 2026-11-23. Janela: 2026-11-20T08:40-03:00 (pedido aberto) a 2026-11-23. Marcas de `R-DECISAO`: `medido` (com o comando), `estimado` (com a base), `não medido`.

## 1. Dados do pedido
Pedido de 8 itens, AE1 a AE8, "Pronto quando": a auditoria diária (AE6) dar zero por 3 dias seguidos.

| Dado | Valor | Marca |
|---|---|---|
| PRs mesclados de AE | 10 (#724, #726, #729, #732, #759, #760, #763, #795, #797, #799), de 20/11 18:02 a 22/11 19:39 | medido (`gh pr list --state merged --search "merged:2026-11-13..2026-11-23"`, filtro `AE<n>`/`anti-erro`) |
| Lead time do PR | P50 0,7 h, máximo 6,1 h (n=10) | medido, mesmo comando |
| Itens do escopo com entrega visível no `CHANGELOG.md` | AE1 (desenho e prova da ferramenta), AE2 (desenho do quadro que anda com o PR; implementação não vista), AE3 (desenho), AE4 (`forge-check ordens`, 0.47.14), AE5 (`forge-check retro --pendentes`, 0.47.14), AE6 (desenho), AE7 (`forge-check comparar`, 0.47.14; AE7.2 na 0.47.15), AE8 (guia e conferência da proteção de branch, 0.47.12) | medido (`CHANGELOG.md`) |
| "Pronto quando" (AE6 zero por 3 dias) | não medido | sem registro da auditoria diária da AE6 neste clone; AE6 só tem desenho |
| Lead time do pedido, voltas por classe, escape | não medido | `forge-check retro --pedido melhorias-anti-erro`: `lead=nao-medido p85=nao-medido(n=0) voltas-classe=nao-medido escapes=0 custo=lacuna`; "sem gatilho" |
| Clareza | não medido | sem seção "Registro de clareza" |
| ERRO-JARVIS do período | 25 em v0478 (8+5+12, 0.47.12 a 0.47.14), 5 da classe "afirma sem ler o estado" | medido (as duas formas `ERRO-JARVIS:` e `ERRO-JARVIS HH:MMx:` nas linhas datadas de `docs/pedidos/v0478.md`, por janela de tag; sonda S1 do review a315a372; a classe vem da leitura de cada linha) |

Linha de métricas e resumo do `forge-placar --dias 14` (medido; 09/11 a 23/11): `taxa_forma: atual 0.00% · anterior 68.98%`, `erros_jarvis: atual 3.39% · anterior 14.90%`, `taxa_escape: atual 0.00% · anterior 0.37%`.
`resumo: os erros de forma do time caíram 100%; os defeitos que escaparam caíram 100%`
Ressalva: base atual `vereditos=0`, sem leitura confiável; a queda de erros de forma é falta de dado.

## 2. O que funcionou
- Cada item AE ganhou desenho antes do código, e os PRs de AE tiveram lead de P50 42 min (medido acima, n=10).
- A AE5 já deu o resultado esperado: a cobrança de retro por tag existe e é por ela que esta rodada de seis retros foi gerada (`forge-check retro --pendentes`).
- A AE4 deu o cruzamento de ordens sem cartão (`forge-check ordens`).

## 3. O que atrapalhou
- O "Pronto quando" depende da AE6 (auditoria diária às 8h), que só tem desenho; o pedido não pode ser dado como pronto pelo critério dele, e não há medida de partida.
- O pedido abriu em 20/11 e a primeira retro sai em 23/11: três dias com versão a versão sem retro, que a própria AE5 existe para evitar. A AE5 saiu na 0.47.14 (21/11), depois da 0.47.12 e da 0.47.13.
- A AE2 (quadro que anda com o PR) segue só em desenho na base lida: o cartão ainda nasce e anda à mão (`CHANGELOG.md`: 0.47.12 e 0.47.15 só trazem o desenho da AE2); a classe de ERRO-JARVIS "abre cartão sem ler o histórico" (3 em 21/11) é o custo visto.

## 4. Causa nova (no máximo 1) e a proposta
Sem proposta aberta nova (`docs/kanban/melhorias.md` não existe). Candidata: "pedido com critério de pronto que depende de item não implementado" (AE6). Virou apenas dado e nota para o tech-lead na ordem do backlog; não abro cartão, pois o item AE6 já está no pedido. A causa de erro do Jarvis é a do cartão JARVIS-CONFERE-ESTADO-ANTES (ver retro da 0.47.14).

| Linha `Melhoria vista:` do pedido | Classe | Destino |
|---|---|---|
| nenhuma no `## Histórico` do pedido | não medido | o pedido só tem a linha de abertura |

## 5. Revisão das propostas vencidas
Nenhuma proposta vencida.
