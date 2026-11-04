---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/catraca-fork
commit: 838803f4c8da680b589f47f022aebe9c2e81e25b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (catraca-fork)

Parecer aprovado. No CI `BASE_REPO` (`github.repository`) vem sempre preenchido; `head.repo` nulo chega vazio e recusa. A ordem (fork antes de tudo, promoções incluídas) está coberta por teste. O efeito vale só depois do merge, pois a catraca roda da base (documentado no código). Diff com 62 linhas, abaixo do teto da M14 (150). Testes rodados: `test_catraca` e `test_ci_local`.

## Achados
- A1 (recomendado) tests/catraca.py:1108 · Fechado em 838803f: em CI sem BASE_REPO a recusa é fechada e um teste exige os dois envs no ci.yml.

## Revalidação
Delta lido: 5ad6373..838803f (catraca.py, test_catraca.py, docs/devops/catraca-fork.md). Já lido: o restante. A1 resolvido; test_catraca e test_ci_local com rc=0.
