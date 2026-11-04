---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/catraca-fork
commit: 5ad6373f37d21c727a1cf97f1f1c3a1256c62163
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (catraca-fork)

Parecer aprovado. No CI `BASE_REPO` (`github.repository`) vem sempre preenchido; `head.repo` nulo chega vazio e recusa. A ordem (fork antes de tudo, promoções incluídas) está coberta por teste. O efeito vale só depois do merge, pois a catraca roda da base (documentado no código). Diff com 62 linhas, abaixo do teto da M14 (150). Testes rodados: `test_catraca` e `test_ci_local`.

## Achados
- A1 (recomendado) tests/catraca.py:1108 · Os dois vazios liberam: passo do CI que perca o env vira falha aberta. Sugestão: teste que exige HEAD_REPO e BASE_REPO no passo de pareceres do ci.yml. Não devolve (R-REVIEW).
