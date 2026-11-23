---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-retros
commit: 3b972c81b48b18db009acaed0c0aec984f172039
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · retrospectivas atrasadas (0.47.12 a 0.47.14 e três pedidos), etapa E116.7 (2ª volta)

Revalidação por delta (H3, `R-REVIEW`) do parecer reprovado a315a372 (head 9b2109ef).

## Delta lido
- `forge-check parecer delta docs/reviews/v0480-retros.md`: intervalo `9b2109ef..3b972c81`; no domínio, só as retros 0.47.12, 0.47.13, 0.47.14 e melhorias-anti-erro. Só documentação, sem código, guarda nem mutante.
- Fora do delta nada foi relido; as ferramentas citadas no parecer anterior (`forge-check docs`, `retro --pendentes`, Neutralidade) seguem valendo para o que não mudou.

## Leitura
- A1 resolvido: a contagem passa a incluir as duas formas (`ERRO-JARVIS:` e `ERRO-JARVIS HH:MM[x]:`), sem as citações, e dá 8, 5 e 12, total 25 (S1). Mudaram junto: tabela e seção 3 da 0.47.12 ("Oito"), tabela e seção 3 da 0.47.13 ("Cinco"), tabela, ressalva e "5 de 25" da 0.47.14 e "25 (8+5+12)" na anti-erro. Nenhum 5/1/9 ou 15 sobrou nas quatro.
- As faixas de linha citadas nas retros (1694 a 1950 etc.) já estão 4 linhas atrás, porque a fonte cresce acima do `## Histórico`. A janela pela data da tag dá a mesma contagem, então não é achado.

## Sondas
- S1 · entradas ERRO-JARVIS em `docs/pedidos/v0478.md` por janela da data das tags (v0.47.11 20/11 07:19, v0.47.12 20/11 18:47, v0.47.13 21/11 07:27, v0.47.14 21/11 21:05), sem "no brief)", "ERRO-JARVIS)" e "de novo" · espera: 8, 5, 12 · obtido: 8, 5, 12
