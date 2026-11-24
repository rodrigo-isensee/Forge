---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-zero-nao-medido
commit: 099850609cd17b04189cdfd49281ae3b8da6d810
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E147.7 (PR #834, nao-medido no lugar de 0; volta de CI E147.6)

Revisão por delta. Head anterior aprovado 2cfb734c; head revisado 09985060. A develop entrou por merge (998e2e45), fora do escopo deste parecer.

## Delta lido
`forge-check parecer delta docs/reviews/v0480-zero-nao-medido.md`: intervalo 2cfb734c..09985060, escopo sem o que veio da base (origin/develop 998e2e4); no domínio só `tests/mutantes/v0457-f6-4-5.json` (M38, `de` e `para`, 2 linhas).

## Achados
- A1 (recomendado) bin/forge-check:63 · a ajuda diz que o metricas sai nao-medido "nas contagens do pedido sem item no Histórico", mas o resumo() vale também para o período sem item (o teste novo confere a linha `periodo`); cite o período na ajuda.

## Parecer
**Aprovado.**

- **M38 testa a mesma guarda:** o `de` novo é a linha 197 atual de `bin/forge_voltas.py` (uma ocorrência só na fonte); o `para` muda só o `construcao is not None` para `not (construcao is not None)`, como antes. O trecho novo `if movimento or linhas else 'nao-medido'` fica igual nos dois lados, então a mutação continua só na guarda declarada. Lista de testes inalterada.
- **Rodado aqui:** `bin/forge-mutante --ids M38 --processos 1 tests/mutantes/v0457-f6-4-5.json`: `M38 · morreu · bin/forge_voltas.py:197`. `bin/forge-mutante --conferir --base 2cfb734`: "conferidas: o trecho de cada spec do diff está no lugar".
- **Observação sem bloqueio:** o rótulo `guarda` do M38 segue com `:144` (a linha real é 197); o `forge-mutante` localiza pelo `de`, não pelo número, e o rótulo já vinha defasado antes desta volta.
- **Suíte inteira:** fica no CI do PR #834; na leitura, suítes pendentes e `catraca`/`bateria (pareceres)` vermelhas por pareceres desatualizados no head novo, o que este arquivo supre em parte. Sem rerrodar.
- **A1** segue recomendado (o delta não tocou `bin/forge-check`); vira cartão depois do merge.
