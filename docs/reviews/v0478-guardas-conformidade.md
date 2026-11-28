---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: 5118747e8d0299079713107b6fe233d0e264ff56
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E1.28 (revalidação no head 5118747e, troca de nome do campo para a T4)

Escopo lido: só o delta de `forge-check parecer delta` (d67b2f4e..5118747e, sem o que veio da develop): hooks/conformidade.py (5 linhas) e docs/hooks.md (linha do `_maquina`, vinda do merge e3721a1 que o delta conta inteiro). Fora do domínio, nada relido.

## Achados
- A1 (recomendado) tests/test_conformidade_verde.py:463 · segue do head bdbdc257: o pulo sem GNU tar também pula no CI; siga o `tests/apoio_sandbox.py`. Vira cartão.
- A2 (recomendado) hooks/conformidade.py:2292 · H1: o item soma 301 linhas em hooks/ desde a base 4182a6b9 (+2 nesta volta), acima de 150; o PR leva `teto: excedido, <n> linhas, <motivo>`. Vira cartão.

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-conformidade.md`, intervalo d67b2f4e..5118747e, 2 arquivos no domínio.
- hooks/conformidade.py:909, 1155-1156, 1160 e 2386: o campo `comandos` de `Alvos` vira `executados` nos 4 pontos de uso; só nome, sem guarda mudada, logo sem mutante novo. `grep` por `alvos.comandos` e pelo nome antigo em hooks/, bin/ e tests/: nenhum resto (os `comandos` de tests/test_hooks.py, tests/test_forge.py e tests/apoio_volta_unica.py são de outros objetos).
- docs/hooks.md:17: texto do `forge-status --maquina` (MP8), trazido da develop; fora do item.
- A1 e A2: seguem recomendados, sem mudança no código deles.

## Verificação
- T4 e as outras regras da catraca: `python3 -I tests/catraca.py --modo regras --base eca1d21b --head 5118747e`: nenhuma violação de testes no CI (T4); restam só a do skip (o A1, 36 para 37) e a de mudança em hooks/conformidade.py, que pede o rótulo `afrouxa-regra` do dono no PR, como antes.
- `python3 -m unittest tests.test_conformidade_verde`: 43 testes, OK (312,4 s).
- Suíte inteira: não rodada (brief); sem PR, CI do head não citável.

## Parecer
Aprovado. A troca de nome é mecânica e completa, sem mudança de comportamento; a junção com a develop não toca o domínio do item além da linha de docs/hooks.md.
