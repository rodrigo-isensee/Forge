---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: 59add0136ba78ab707d74575f2325327284126e9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (AE2, #875, E10.17), volta por delta

Delta lido: `f45bf805..59add013`. Commit próprio da branch: `3559c9aa` (E10.14), que renumera os ids de `tests/mutantes/v0481-ae2-quadro-anda-5.json` de AE33–AE39 para AE35–AE41 e ajusta o comentário em `tests/test_sobreposicao_quadro.py:499` e o fragmento do changelog. Os dois são fora do domínio. As duas fusões da develop (`c65fb3a9` traz o #898 e `59add013` traz o #885) não têm conflito: o `git show --remerge-diff` sai vazio nas duas. O `bin/forge-fechar`, o `docs/fechamento-integrador.md` e o `hooks/conformidade.*` que o `forge-check parecer delta` mostra vêm da develop, já revisados nos PRs de origem. A diferença do AE2 contra a develop em `bin/`, `skills/` e `hooks/` tem as mesmas 135 linhas `+`/`-` antes (`7e38f842..f45bf805`) e depois (`34ab6714..59add013`). O código não mudou. Classe C.

Gatilhos: controle do Forge que analisa entrada (corpo do PR no fechamento), escrita do KANBAN.md por ferramenta, fechamento depois do merge.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta: nada novo nesta volta.** As guardas do AE2 (`coluna_do_cartao`, movimento do quadro) são as mesmas da rodada aprovada em `f45bf805`.
- **Neutro: a renumeração.** Mudam só os campos `id` e os textos que os citam. `guarda`, `arquivo`, `de` e `para` ficam iguais, e nenhum mutante sai. Os 41 ids das cinco specs agora são únicos, sem repetição (antes AE33 e AE34 se repetiam com a `-4`). Assim a prova dos mutantes fica sem ambiguidade, mas nenhuma guarda muda. As fusões limpas da develop também são neutras aqui: o que elas trazem é dos PRs de origem.
- **Afrouxa: nada.** Nenhuma guarda que barrava deixou de barrar. O rótulo `afrouxa-regra` que a catraca pede por tocar em `bin/forge-check` é do time (ordem de 25/11) e não indica afrouxamento do AE2.

Achados anteriores: nenhum aberto (A5 já resolvido em `f45bf805`).

## Detalhe
Suíte: no head, `python3 -m unittest tests.test_sobreposicao_quadro tests.test_fechar_move_cartao` rodou 97 testes, OK. `bin/forge-mutante tests/mutantes/v0481-ae2-quadro-anda-5.json` em `59add0136ba7` deixou AE35 a AE41 todos mortos. A unicidade dos ids nas cinco specs (AE1 a AE41) foi conferida por script, sem repetição.

O CI do head está verde nas partes que contam: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), verificações longas, bateria (python 3.14), instalação, teto de pulados, árvore provada e `catraca`. Dois checks estão vermelhos só por espera:
- `bateria (pareceres)`: falta o parecer novo desta volta.
- `bateria`: é o agregador.

## Parecer
- ci: 59add0136ba78ab707d74575f2325327284126e9 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: leitura do delta, `git show --remerge-diff`, testes dos módulos tocados, `forge-mutante` da spec tocada e check-runs pelo `gh`. A varredura de segredos não se aplica, porque o delta não traz credencial nem configuração.
